import { SocialPlatform } from './types';
import { ApiLogger } from './logger';
import { ApiAnalytics } from './analytics';
import { generateRequestId } from './helpers';

// Interfaz para peticiones
export interface RequestContext {
  platform: SocialPlatform;
  method: string;
  endpoint: string;
  requestId: string;
  startTime: number;
  data?: Record<string, unknown>;
  headers?: Record<string, string>;
  retryCount?: number;
}

// Interfaz para respuestas
export interface ResponseContext {
  statusCode: number;
  data: any;
  headers?: Record<string, string>;
  duration: number;
  retryCount?: number;
}

// Interfaz para errores
export interface ErrorContext {
  error: Error | unknown;
  statusCode?: number;
  errorCode?: string;
  errorMessage?: string;
  duration: number;
  retryCount?: number;
}

// Tipo para middleware de peticiones
export type RequestMiddleware = (
  context: RequestContext
) => Promise<RequestContext> | RequestContext;

// Tipo para middleware de respuestas
export type ResponseMiddleware = (
  context: RequestContext,
  responseContext: ResponseContext
) => Promise<ResponseContext> | ResponseContext;

// Tipo para middleware de errores
export type ErrorMiddleware = (
  context: RequestContext,
  errorContext: ErrorContext
) => Promise<ErrorContext | null> | ErrorContext | null; // null significa que el error fue manejado

/**
 * Gestor de middleware para API
 */
export class ApiMiddlewareManager {
  private requestMiddlewares: RequestMiddleware[] = [];
  private responseMiddlewares: ResponseMiddleware[] = [];
  private errorMiddlewares: ErrorMiddleware[] = [];
  private logger: ApiLogger;
  private analytics: ApiAnalytics;
  
  constructor() {
    this.logger = ApiLogger.getInstance();
    this.analytics = ApiAnalytics.getInstance();
    
    // Registrar middleware predeterminado
    this.registerDefaultMiddlewares();
  }
  
  /**
   * Registra middleware para peticiones
   */
  public addRequestMiddleware(middleware: RequestMiddleware): void {
    this.requestMiddlewares.push(middleware);
  }
  
  /**
   * Registra middleware para respuestas
   */
  public addResponseMiddleware(middleware: ResponseMiddleware): void {
    this.responseMiddlewares.push(middleware);
  }
  
  /**
   * Registra middleware para errores
   */
  public addErrorMiddleware(middleware: ErrorMiddleware): void {
    this.errorMiddlewares.push(middleware);
  }
  
  /**
   * Registra middleware predeterminado para logging y analytics
   */
  private registerDefaultMiddlewares(): void {
    // Request logging middleware
    this.addRequestMiddleware(context => {
      this.logger.debug(`API Request: ${context.method} ${context.endpoint}`, context.platform, {
        requestId: context.requestId,
        data: context.data
      });
      
      // Registrar para analytics
      this.analytics.trackApiRequest(
        context.platform,
        context.method,
        context.endpoint,
        context.requestId,
        context.data
      );
      
      return context;
    });
    
    // Response logging middleware
    this.addResponseMiddleware((context, responseContext) => {
      const duration = responseContext.duration;
      
      this.logger.debug(
        `API Response (${duration}ms): ${context.method} ${context.endpoint} - ${responseContext.statusCode}`,
        context.platform,
        {
          requestId: context.requestId,
          statusCode: responseContext.statusCode,
          data: responseContext.data
        }
      );
      
      // Registrar para analytics
      this.analytics.trackApiResponse(
        context.platform,
        context.method,
        context.endpoint,
        responseContext.statusCode,
        context.requestId,
        duration,
        responseContext.data
      );
      
      return responseContext;
    });
    
    // Error logging middleware
    this.addErrorMiddleware((context, errorContext) => {
      const duration = errorContext.duration;
      const errorCode = errorContext.errorCode || 'UNKNOWN_ERROR';
      const errorMessage = errorContext.errorMessage || 'Error desconocido';
      
      this.logger.error(
        `API Error (${duration}ms): ${context.method} ${context.endpoint}`,
        errorContext.error,
        context.platform,
        {
          requestId: context.requestId,
          statusCode: errorContext.statusCode,
          errorCode,
          retryCount: context.retryCount
        }
      );
      
      // Registrar para analytics
      this.analytics.trackApiError(
        context.platform,
        context.method,
        context.endpoint,
        errorContext.statusCode,
        errorCode,
        errorMessage,
        context.requestId,
        duration,
        context.retryCount
      );
      
      return errorContext;
    });
  }
  
  /**
   * Procesa la petición a través de todos los middleware
   */
  public async processRequest(initialContext: Omit<RequestContext, 'requestId' | 'startTime'>): Promise<RequestContext> {
    // Añadir RequestId y startTime
    let context: RequestContext = {
      ...initialContext,
      requestId: generateRequestId(initialContext.platform),
      startTime: Date.now()
    };
    
    // Aplicar middleware de peticiones
    for (const middleware of this.requestMiddlewares) {
      context = await middleware(context);
    }
    
    return context;
  }
  
  /**
   * Procesa la respuesta a través de todos los middleware
   */
  public async processResponse(
    context: RequestContext,
    response: Omit<ResponseContext, 'duration'>
  ): Promise<ResponseContext> {
    const duration = Date.now() - context.startTime;
    
    let responseContext: ResponseContext = {
      ...response,
      duration
    };
    
    // Aplicar middleware de respuestas
    for (const middleware of this.responseMiddlewares) {
      responseContext = await middleware(context, responseContext);
    }
    
    return responseContext;
  }
  
  /**
   * Procesa el error a través de todos los middleware
   */
  public async processError(
    context: RequestContext,
    error: Error | unknown,
    statusCode?: number,
    errorCode?: string,
    errorMessage?: string
  ): Promise<ErrorContext | null> {
    const duration = Date.now() - context.startTime;
    
    let errorContext: ErrorContext = {
      error,
      statusCode,
      errorCode,
      errorMessage: errorMessage || (error instanceof Error ? error.message : String(error)),
      duration
    };
    
    // Aplicar middleware de errores
    for (const middleware of this.errorMiddlewares) {
      const result = await middleware(context, errorContext);
      
      // Si un middleware devuelve null, significa que el error fue manejado
      if (result === null) {
        return null;
      }
      
      errorContext = result;
    }
    
    return errorContext;
  }
}

// Singleton
let middlewareManagerInstance: ApiMiddlewareManager | null = null;

/**
 * Obtiene la instancia única del gestor de middleware
 */
export function getMiddlewareManager(): ApiMiddlewareManager {
  if (!middlewareManagerInstance) {
    middlewareManagerInstance = new ApiMiddlewareManager();
  }
  return middlewareManagerInstance;
}

// Middleware para el manejo de límites de peticiones
export const rateLimitMiddleware: ErrorMiddleware = async (context, errorContext) => {
  // Verificar si es un error de límite de peticiones
  const isRateLimit = 
    errorContext.statusCode === 429 || 
    errorContext.errorCode?.includes('RATE_LIMIT') ||
    errorContext.errorMessage?.toLowerCase().includes('rate limit');
  
  if (isRateLimit) {
    // Registrar el evento de límite de peticiones
    ApiAnalytics.getInstance().trackRateLimit(
      context.platform,
      context.endpoint,
      0, // Valor por defecto si no disponemos del límite
      0, // Valor por defecto si no disponemos del remanente
      new Date(Date.now() + 60 * 1000).toISOString() // Suponemos un minuto por defecto
    );
    
    // Actualizar el mensaje de error para incluir información adicional
    errorContext.errorMessage = `Límite de peticiones alcanzado para ${context.platform}. Por favor, intente más tarde.`;
  }
  
  return errorContext;
};

// Middleware para el manejo de errores de autenticación
export const authErrorMiddleware: ErrorMiddleware = async (context, errorContext) => {
  // Verificar si es un error de autenticación
  const isAuthError = 
    errorContext.statusCode === 401 || 
    errorContext.statusCode === 403 ||
    errorContext.errorCode?.includes('AUTH') ||
    errorContext.errorCode?.includes('TOKEN') ||
    errorContext.errorMessage?.toLowerCase().includes('authen') ||
    errorContext.errorMessage?.toLowerCase().includes('token');
  
  if (isAuthError) {
    // Registrar el evento de autenticación
    ApiAnalytics.getInstance().trackAuthentication(
      context.platform,
      false,
      errorContext.errorMessage
    );
    
    // Actualizar el mensaje de error para incluir información adicional
    errorContext.errorMessage = `Error de autenticación en ${context.platform}. Por favor, vuelva a autenticarse.`;
  }
  
  return errorContext;
};

// Middleware para retry automático en errores de red
export const networkErrorRetryMiddleware: ErrorMiddleware = async (context, errorContext) => {
  // Verificar si es un error de red
  const isNetworkError = 
    errorContext.error instanceof Error && 
    (errorContext.error.message.includes('Network Error') || 
     errorContext.error.message.includes('ECONNREFUSED') ||
     errorContext.error.message.includes('timeout'));
  
  // Verificar si debemos reintentar
  if (isNetworkError && (!context.retryCount || context.retryCount < 3)) {
    // Registrar el intento de reintento
    ApiLogger.getInstance().debug(
      `Reintentando petición (${(context.retryCount || 0) + 1}/3) debido a error de red`,
      context.platform,
      {
        endpoint: context.endpoint,
        method: context.method,
        requestId: context.requestId
      }
    );
    
    // Marcar el error como manejado (devolviendo null)
    // El código que usa este middleware debe implementar la lógica de reintento
    return null;
  }
  
  return errorContext;
};