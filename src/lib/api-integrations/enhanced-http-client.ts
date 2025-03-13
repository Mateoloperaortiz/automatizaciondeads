import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { SocialPlatform } from './types';
import { 
  getMiddlewareManager, 
  RequestContext, 
  ResponseContext,
  rateLimitMiddleware,
  authErrorMiddleware,
  networkErrorRetryMiddleware
} from './middleware';
import { createApiError } from './error-handler';

// Configuración del cliente
export interface HttpClientConfig {
  baseUrl: string;
  timeout?: number;
  retries?: number;
  headers?: Record<string, string>;
  withCredentials?: boolean;
}

/**
 * Cliente HTTP mejorado con sistema de middleware
 */
export class EnhancedHttpClient {
  private axiosInstance: AxiosInstance;
  private platform: SocialPlatform;
  private defaultRetries: number;
  private middlewareManager = getMiddlewareManager();
  
  constructor(platform: SocialPlatform, config: HttpClientConfig) {
    this.platform = platform;
    this.defaultRetries = config.retries || 3;
    
    // Registrar middleware adicional
    this.middlewareManager.addErrorMiddleware(rateLimitMiddleware);
    this.middlewareManager.addErrorMiddleware(authErrorMiddleware);
    this.middlewareManager.addErrorMiddleware(networkErrorRetryMiddleware);
    
    // Configurar axios
    this.axiosInstance = axios.create({
      baseURL: config.baseUrl,
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
        ...config.headers
      },
      withCredentials: config.withCredentials
    });
  }
  
  /**
   * Actualiza el token de acceso para futuras peticiones
   */
  setAccessToken(accessToken: string): void {
    this.axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
  }
  
  /**
   * Realiza una petición HTTP con procesamiento mediante middleware
   */
  async request<T = any>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    endpoint: string,
    data?: Record<string, unknown>,
    options: {
      params?: Record<string, unknown>;
      headers?: Record<string, string>;
      timeout?: number;
      retries?: number;
    } = {}
  ): Promise<T> {
    // Crear contexto de petición inicial
    const initialContext: Omit<RequestContext, 'requestId' | 'startTime'> = {
      platform: this.platform,
      method,
      endpoint,
      data,
      headers: options.headers,
      retryCount: 0
    };
    
    return this.executeRequest<T>(initialContext, options, 0);
  }
  
  /**
   * Ejecuta la petición con reintentos si es necesario
   */
  private async executeRequest<T>(
    contextData: Omit<RequestContext, 'requestId' | 'startTime'>,
    options: {
      params?: Record<string, unknown>;
      headers?: Record<string, string>;
      timeout?: number;
      retries?: number;
    },
    retryCount: number
  ): Promise<T> {
    // Actualizar contador de reintentos
    const context = {
      ...contextData,
      retryCount
    };
    
    try {
      // Procesar petición con middleware
      const processedContext = await this.middlewareManager.processRequest(context);
      
      // Configurar la petición de axios
      const config: AxiosRequestConfig = {
        method: processedContext.method,
        url: processedContext.endpoint,
        params: options.params,
        headers: processedContext.headers,
        timeout: options.timeout
      };
      
      // Añadir datos para métodos que los aceptan
      if (['POST', 'PUT', 'PATCH'].includes(processedContext.method)) {
        config.data = processedContext.data;
      }
      
      // Realizar petición
      const response = await this.axiosInstance.request<T>(config);
      
      // Procesar respuesta con middleware
      const processedResponse = await this.middlewareManager.processResponse(
        processedContext,
        {
          statusCode: response.status,
          data: response.data,
          headers: response.headers as Record<string, string>
        }
      );
      
      return processedResponse.data;
    } catch (error) {
      // Extraer información del error
      const axiosError = error as any;
      const statusCode = axiosError.response?.status;
      const errorData = axiosError.response?.data;
      
      // Crear detalles del error
      const apiError = createApiError(error, this.platform);
      
      // Procesar error con middleware
      const processedError = await this.middlewareManager.processError(
        { ...context, requestId: 'error_' + Date.now(), startTime: Date.now() - 1000 },
        error,
        statusCode,
        apiError.code,
        apiError.message
      );
      
      // Si el error fue manejado y debemos reintentar
      if (processedError === null && retryCount < (options.retries || this.defaultRetries)) {
        // Esperar antes de reintentar (backoff exponencial)
        const delay = Math.pow(2, retryCount) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
        
        // Reintentar la petición
        return this.executeRequest<T>(context, options, retryCount + 1);
      }
      
      // Si no se debe reintentar, lanzar el error
      throw apiError;
    }
  }
  
  /**
   * Método GET
   */
  async get<T = any>(
    endpoint: string,
    params?: Record<string, unknown>,
    options: {
      headers?: Record<string, string>;
      timeout?: number;
      retries?: number;
    } = {}
  ): Promise<T> {
    return this.request<T>('GET', endpoint, undefined, {
      ...options,
      params
    });
  }
  
  /**
   * Método POST
   */
  async post<T = any>(
    endpoint: string,
    data?: Record<string, unknown>,
    options: {
      params?: Record<string, unknown>;
      headers?: Record<string, string>;
      timeout?: number;
      retries?: number;
    } = {}
  ): Promise<T> {
    return this.request<T>('POST', endpoint, data, options);
  }
  
  /**
   * Método PUT
   */
  async put<T = any>(
    endpoint: string,
    data?: Record<string, unknown>,
    options: {
      params?: Record<string, unknown>;
      headers?: Record<string, string>;
      timeout?: number;
      retries?: number;
    } = {}
  ): Promise<T> {
    return this.request<T>('PUT', endpoint, data, options);
  }
  
  /**
   * Método DELETE
   */
  async delete<T = any>(
    endpoint: string,
    options: {
      params?: Record<string, unknown>;
      headers?: Record<string, string>;
      timeout?: number;
      retries?: number;
    } = {}
  ): Promise<T> {
    return this.request<T>('DELETE', endpoint, undefined, options);
  }
  
  /**
   * Método para actualizar la configuración base
   */
  updateConfig(config: Partial<HttpClientConfig>): void {
    if (config.baseUrl) {
      this.axiosInstance.defaults.baseURL = config.baseUrl;
    }
    
    if (config.timeout) {
      this.axiosInstance.defaults.timeout = config.timeout;
    }
    
    if (config.headers) {
      this.axiosInstance.defaults.headers.common = {
        ...this.axiosInstance.defaults.headers.common,
        ...config.headers
      };
    }
    
    if (config.retries !== undefined) {
      this.defaultRetries = config.retries;
    }
  }
}