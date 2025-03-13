import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { SocialPlatform } from './types';
import { createErrorResponse, handleApiError } from './error-handler';

// Opciones de configuración comunes para todas las peticiones
interface RequestOptions {
  timeout?: number;
  retries?: number;
  headers?: Record<string, string>;
  params?: Record<string, any>;
}

// Opciones específicas para cada plataforma
interface PlatformOptions {
  baseUrl: string;
  defaultTimeout: number;
  defaultRetries: number;
  defaultHeaders: Record<string, string>;
  rateLimitConfig?: {
    rateLimit: number; // Máximo de peticiones
    rateLimitWindow: number; // Ventana de tiempo en ms
    rateMonitoring: boolean; // Si se debe monitorear el límite de peticiones
  };
}

// Configuraciones por plataforma
const platformConfigs: Record<SocialPlatform, PlatformOptions> = {
  meta: {
    baseUrl: 'https://graph.facebook.com/v18.0',
    defaultTimeout: 30000,
    defaultRetries: 3,
    defaultHeaders: {
      'Content-Type': 'application/json',
    },
    rateLimitConfig: {
      rateLimit: 200, // 200 peticiones por ventana
      rateLimitWindow: 60 * 60 * 1000, // 1 hora
      rateMonitoring: true,
    },
  },
  
  google: {
    baseUrl: 'https://googleads.googleapis.com/v15',
    defaultTimeout: 60000, // APIs de Google pueden ser más lentas
    defaultRetries: 3,
    defaultHeaders: {
      'Content-Type': 'application/json',
    },
  },
  
  x: {
    baseUrl: 'https://api.twitter.com/2',
    defaultTimeout: 30000,
    defaultRetries: 2,
    defaultHeaders: {
      'Content-Type': 'application/json',
    },
    rateLimitConfig: {
      rateLimit: 450, // 450 peticiones por ventana para la mayoría de endpoints
      rateLimitWindow: 15 * 60 * 1000, // 15 minutos
      rateMonitoring: true,
    },
  },
  
  tiktok: {
    baseUrl: 'https://business-api.tiktok.com/open_api/v1.3',
    defaultTimeout: 30000,
    defaultRetries: 3,
    defaultHeaders: {
      'Content-Type': 'application/json',
    },
    rateLimitConfig: {
      rateLimit: 1000, // 1000 peticiones por día por app
      rateLimitWindow: 24 * 60 * 60 * 1000, // 24 horas
      rateMonitoring: true,
    },
  },
  
  snapchat: {
    baseUrl: 'https://adsapi.snapchat.com/v1',
    defaultTimeout: 30000,
    defaultRetries: 3,
    defaultHeaders: {
      'Content-Type': 'application/json',
    },
  },
};

/**
 * Cliente HTTP para realizar peticiones a APIs de redes sociales
 */
export class ApiClient {
  private axiosInstance: AxiosInstance;
  private platform: SocialPlatform;
  private rateLimitTracker: {
    requestCount: number;
    resetAt: number;
  };
  
  constructor(platform: SocialPlatform, accessToken?: string, customConfig?: Partial<PlatformOptions>) {
    this.platform = platform;
    
    // Combinar configuración predeterminada con personalizada
    const config = {
      ...platformConfigs[platform],
      ...customConfig,
    };
    
    // Crear instancia de Axios con configuración predeterminada
    this.axiosInstance = axios.create({
      baseURL: config.baseUrl,
      timeout: config.defaultTimeout,
      headers: {
        ...config.defaultHeaders,
        ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}),
      },
    });
    
    // Inicializar rastreador de límite de peticiones
    this.rateLimitTracker = {
      requestCount: 0,
      resetAt: Date.now() + (config.rateLimitConfig?.rateLimitWindow || 3600000),
    };
    
    // Interceptor para extraer información de límite de peticiones
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => {
        this.processRateLimitHeaders(response);
        return response;
      },
      (error) => {
        if (error.response) {
          this.processRateLimitHeaders(error.response);
        }
        return Promise.reject(error);
      }
    );
  }
  
  /**
   * Actualiza el token de acceso para futuras peticiones
   */
  setAccessToken(accessToken: string): void {
    this.axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
  }
  
  /**
   * Procesa encabezados relacionados con límite de peticiones
   */
  private processRateLimitHeaders(response: AxiosResponse): void {
    const config = platformConfigs[this.platform].rateLimitConfig;
    if (!config || !config.rateMonitoring) return;
    
    // Extraer información de límite de peticiones según la plataforma
    let remaining: number | undefined;
    let resetAt: number | undefined;
    
    switch (this.platform) {
      case 'meta':
        // Meta usa X-Business-Use-Case-Usage y X-App-Usage
        const appUsage = response.headers['x-app-usage'];
        if (appUsage) {
          try {
            const usage = JSON.parse(appUsage);
            remaining = config.rateLimit - Math.floor(usage.call_count);
          } catch (e) {
            // Error al parsear, ignorar
          }
        }
        break;
        
      case 'x':
        // X (Twitter) usa X-Rate-Limit-Remaining y X-Rate-Limit-Reset
        const remainingHeader = response.headers['x-rate-limit-remaining'];
        const resetHeader = response.headers['x-rate-limit-reset'];
        
        if (remainingHeader) {
          remaining = parseInt(remainingHeader);
        }
        
        if (resetHeader) {
          resetAt = parseInt(resetHeader) * 1000; // Convertir a milisegundos
        }
        break;
        
      case 'tiktok':
        // TikTok usa X-RateLimit-Remaining y X-RateLimit-Reset
        const tiktokRemaining = response.headers['x-ratelimit-remaining'];
        const tiktokReset = response.headers['x-ratelimit-reset'];
        
        if (tiktokRemaining) {
          remaining = parseInt(tiktokRemaining);
        }
        
        if (tiktokReset) {
          resetAt = parseInt(tiktokReset) * 1000; // Convertir a milisegundos
        }
        break;
        
      // Agregar más plataformas según sea necesario
    }
    
    // Actualizar rastreador de límite de peticiones
    if (remaining !== undefined) {
      this.rateLimitTracker.requestCount = config.rateLimit - remaining;
    } else {
      this.rateLimitTracker.requestCount++;
    }
    
    if (resetAt !== undefined) {
      this.rateLimitTracker.resetAt = resetAt;
    }
  }
  
  /**
   * Verifica si estamos cerca del límite de peticiones
   */
  isRateLimitNearExhaustion(): boolean {
    const config = platformConfigs[this.platform].rateLimitConfig;
    if (!config || !config.rateMonitoring) return false;
    
    // Resetear el contador si ya pasó el tiempo de reseteo
    if (Date.now() > this.rateLimitTracker.resetAt) {
      this.rateLimitTracker.requestCount = 0;
      this.rateLimitTracker.resetAt = Date.now() + config.rateLimitWindow;
      return false;
    }
    
    // Considerar "cerca de agotamiento" si hemos usado más del 90% de las peticiones permitidas
    return this.rateLimitTracker.requestCount >= config.rateLimit * 0.9;
  }
  
  /**
   * Realizar petición GET
   */
  async get<T>(
    endpoint: string, 
    options: RequestOptions = {}
  ): Promise<T> {
    try {
      // Configurar la petición
      const config: AxiosRequestConfig = {
        timeout: options.timeout || platformConfigs[this.platform].defaultTimeout,
        headers: options.headers,
        params: options.params,
      };
      
      // Realizar la petición
      const response = await this.axiosInstance.get<T>(endpoint, config);
      return response.data;
    } catch (error) {
      // Usar el error handler centralizado
      const errorResponse = await handleApiError(
        error, 
        this.platform, 
        () => this.get<T>(endpoint, options),
        options.retries || platformConfigs[this.platform].defaultRetries
      );
      
      // Convertir la respuesta de error a una excepción tipada
      throw errorResponse.error;
    }
  }
  
  /**
   * Realizar petición POST
   */
  async post<T>(
    endpoint: string, 
    data?: any, 
    options: RequestOptions = {}
  ): Promise<T> {
    try {
      // Configurar la petición
      const config: AxiosRequestConfig = {
        timeout: options.timeout || platformConfigs[this.platform].defaultTimeout,
        headers: options.headers,
        params: options.params,
      };
      
      // Realizar la petición
      const response = await this.axiosInstance.post<T>(endpoint, data, config);
      return response.data;
    } catch (error) {
      // Usar el error handler centralizado
      const errorResponse = await handleApiError(
        error, 
        this.platform, 
        () => this.post<T>(endpoint, data, options),
        options.retries || platformConfigs[this.platform].defaultRetries
      );
      
      // Convertir la respuesta de error a una excepción tipada
      throw errorResponse.error;
    }
  }
  
  /**
   * Realizar petición PUT
   */
  async put<T>(
    endpoint: string, 
    data?: any, 
    options: RequestOptions = {}
  ): Promise<T> {
    try {
      // Configurar la petición
      const config: AxiosRequestConfig = {
        timeout: options.timeout || platformConfigs[this.platform].defaultTimeout,
        headers: options.headers,
        params: options.params,
      };
      
      // Realizar la petición
      const response = await this.axiosInstance.put<T>(endpoint, data, config);
      return response.data;
    } catch (error) {
      // Usar el error handler centralizado
      const errorResponse = await handleApiError(
        error, 
        this.platform, 
        () => this.put<T>(endpoint, data, options),
        options.retries || platformConfigs[this.platform].defaultRetries
      );
      
      // Convertir la respuesta de error a una excepción tipada
      throw errorResponse.error;
    }
  }
  
  /**
   * Realizar petición DELETE
   */
  async delete<T>(
    endpoint: string, 
    options: RequestOptions = {}
  ): Promise<T> {
    try {
      // Configurar la petición
      const config: AxiosRequestConfig = {
        timeout: options.timeout || platformConfigs[this.platform].defaultTimeout,
        headers: options.headers,
        params: options.params,
      };
      
      // Realizar la petición
      const response = await this.axiosInstance.delete<T>(endpoint, config);
      return response.data;
    } catch (error) {
      // Usar el error handler centralizado
      const errorResponse = await handleApiError(
        error, 
        this.platform, 
        () => this.delete<T>(endpoint, options),
        options.retries || platformConfigs[this.platform].defaultRetries
      );
      
      // Convertir la respuesta de error a una excepción tipada
      throw errorResponse.error;
    }
  }
  
  /**
   * Realizar petición con manejo estándar de respuesta
   */
  async request<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    endpoint: string,
    data?: any,
    options: RequestOptions = {}
  ): Promise<T> {
    switch (method) {
      case 'GET':
        return this.get<T>(endpoint, options);
      case 'POST':
        return this.post<T>(endpoint, data, options);
      case 'PUT':
        return this.put<T>(endpoint, data, options);
      case 'DELETE':
        return this.delete<T>(endpoint, options);
      default:
        throw new Error(`Método HTTP no soportado: ${method}`);
    }
  }
}