import { ApiErrorDetail, SocialPlatform } from './types';
import { ApiLogger } from './logger';

// Interfaz de configuración para el tracking de errores
interface ErrorTrackingConfig {
  endpoint?: string;
  enabled: boolean;
  sampleRate?: number; // 0-1, porcentaje de errores a enviar
  includeStackTrace?: boolean;
  enableGlobalHandlers?: boolean;
  ignoredErrors?: string[]; // Errores a ignorar
}

// Detalles de un error rastreado
interface TrackedError {
  id: string; // ID único del error
  timestamp: string;
  message: string;
  code?: string;
  platform?: SocialPlatform;
  component?: string; // Componente donde ocurrió el error
  stackTrace?: string;
  tags?: Record<string, string>;
  userAgent?: string;
  url?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Servicio para rastrear errores centralizadamente
 */
export class ErrorTrackingService {
  private static instance: ErrorTrackingService;
  private config: ErrorTrackingConfig;
  private logger: ApiLogger;
  private errorQueue: TrackedError[] = [];
  private flushIntervalId?: NodeJS.Timeout;
  
  private constructor(config: Partial<ErrorTrackingConfig> = {}) {
    // Configuración por defecto
    this.config = {
      enabled: config.enabled !== undefined ? config.enabled : true,
      endpoint: config.endpoint,
      sampleRate: config.sampleRate || 1,
      includeStackTrace: config.includeStackTrace !== undefined ? config.includeStackTrace : true,
      enableGlobalHandlers: config.enableGlobalHandlers !== undefined ? config.enableGlobalHandlers : true,
      ignoredErrors: config.ignoredErrors || [],
    };
    
    this.logger = ApiLogger.getInstance();
    
    // Inicializar rastreo global si está habilitado
    if (this.config.enabled && this.config.enableGlobalHandlers && typeof window !== 'undefined') {
      this.setupGlobalErrorHandlers();
    }
    
    // Configurar intervalo para enviar errores
    if (this.config.enabled && this.config.endpoint && typeof window !== 'undefined') {
      this.flushIntervalId = setInterval(() => {
        this.flush();
      }, 10000); // Cada 10 segundos
    }
  }
  
  /**
   * Obtener instancia del servicio
   */
  public static getInstance(config?: Partial<ErrorTrackingConfig>): ErrorTrackingService {
    if (!ErrorTrackingService.instance) {
      ErrorTrackingService.instance = new ErrorTrackingService(config);
    }
    
    // Actualizar configuración si se proporciona
    if (config) {
      ErrorTrackingService.instance.updateConfig(config);
    }
    
    return ErrorTrackingService.instance;
  }
  
  /**
   * Actualizar configuración del servicio
   */
  public updateConfig(config: Partial<ErrorTrackingConfig>): void {
    const oldEnableGlobalHandlers = this.config.enableGlobalHandlers;
    const oldEnabled = this.config.enabled;
    
    this.config = { ...this.config, ...config };
    
    // Actualizar handlers globales si se cambia la configuración
    if (typeof window !== 'undefined') {
      if (!oldEnableGlobalHandlers && this.config.enableGlobalHandlers && this.config.enabled) {
        this.setupGlobalErrorHandlers();
      } else if (oldEnableGlobalHandlers && !this.config.enableGlobalHandlers) {
        this.teardownGlobalErrorHandlers();
      }
      
      // Actualizar intervalo de flush
      if (this.flushIntervalId) {
        clearInterval(this.flushIntervalId);
      }
      
      if (this.config.enabled && this.config.endpoint) {
        this.flushIntervalId = setInterval(() => {
          this.flush();
        }, 10000);
      }
    }
  }
  
  /**
   * Configura handlers globales para errores no capturados
   */
  private setupGlobalErrorHandlers(): void {
    if (typeof window === 'undefined') return;
    
    // Error global no capturado
    window.addEventListener('error', this.handleGlobalError);
    
    // Promesa rechazada no capturada
    window.addEventListener('unhandledrejection', this.handleUnhandledRejection);
  }
  
  /**
   * Elimina handlers globales
   */
  private teardownGlobalErrorHandlers(): void {
    if (typeof window === 'undefined') return;
    
    window.removeEventListener('error', this.handleGlobalError);
    window.removeEventListener('unhandledrejection', this.handleUnhandledRejection);
  }
  
  /**
   * Handler para errores globales
   */
  private handleGlobalError = (event: ErrorEvent): void => {
    const error = event.error || new Error(event.message);
    
    this.trackError(error, {
      component: event.filename || 'unknown',
      url: window.location.href,
      tags: {
        type: 'global_error',
        source: event.filename || 'unknown',
        line: event.lineno?.toString() || 'unknown',
        column: event.colno?.toString() || 'unknown'
      }
    });
  };
  
  /**
   * Handler para promesas rechazadas no capturadas
   */
  private handleUnhandledRejection = (event: PromiseRejectionEvent): void => {
    const error = event.reason instanceof Error 
      ? event.reason 
      : new Error(String(event.reason));
    
    this.trackError(error, {
      component: 'promise',
      url: window.location.href,
      tags: {
        type: 'unhandled_rejection',
        source: 'promise'
      }
    });
  };
  
  /**
   * Rastrea un error específico
   */
  public trackError(
    error: Error | ApiErrorDetail | string,
    options: {
      platform?: SocialPlatform;
      component?: string;
      tags?: Record<string, string>;
      metadata?: Record<string, unknown>;
    } = {}
  ): string {
    if (!this.config.enabled) return '';
    
    // Aplicar muestreo aleatorio
    if (Math.random() > (this.config.sampleRate || 1)) return '';
    
    // Generar ID único para el error
    const errorId = `err_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    
    // Formatear error
    let formattedError: TrackedError;
    
    if (typeof error === 'string') {
      formattedError = {
        id: errorId,
        timestamp: new Date().toISOString(),
        message: error,
        platform: options.platform,
        component: options.component,
        tags: options.tags,
        metadata: options.metadata
      };
    } else if (error instanceof Error) {
      formattedError = {
        id: errorId,
        timestamp: new Date().toISOString(),
        message: error.message,
        platform: options.platform,
        component: options.component,
        stackTrace: this.config.includeStackTrace ? error.stack : undefined,
        tags: options.tags,
        metadata: options.metadata
      };
    } else {
      // Es un ApiErrorDetail
      formattedError = {
        id: errorId,
        timestamp: new Date().toISOString(),
        message: error.message,
        code: error.code,
        platform: error.platform || options.platform,
        component: options.component,
        stackTrace: this.config.includeStackTrace ? 
          (error.originalError instanceof Error ? error.originalError.stack : undefined) : 
          undefined,
        tags: {
          ...(error.statusCode ? { statusCode: error.statusCode.toString() } : {}),
          ...(error.retryable ? { retryable: 'true' } : {}),
          ...(error.rateLimited ? { rateLimited: 'true' } : {}),
          ...(error.authError ? { authError: 'true' } : {}),
          ...options.tags
        },
        metadata: {
          ...options.metadata,
          apiErrorDetail: error
        }
      };
    }
    
    // Añadir información del navegador si está disponible
    if (typeof window !== 'undefined') {
      formattedError.userAgent = navigator.userAgent;
      formattedError.url = window.location.href;
    }
    
    // Verificar si es un error a ignorar
    if (this.shouldIgnoreError(formattedError)) {
      return errorId;
    }
    
    // Registrar en el logger local
    this.logger.error(
      `Error tracked: ${formattedError.message}`,
      new Error(formattedError.message),
      formattedError.platform,
      { 
        errorId, 
        component: formattedError.component,
        ...formattedError.tags
      }
    );
    
    // Añadir a la cola para enviar
    this.errorQueue.push(formattedError);
    
    // Enviar inmediatamente si hay endpoint configurado
    if (this.config.endpoint && this.errorQueue.length >= 10) {
      this.flush();
    }
    
    return errorId;
  }
  
  /**
   * Determina si un error debe ser ignorado
   */
  private shouldIgnoreError(error: TrackedError): boolean {
    // Ignorar errores específicos por mensaje
    return this.config.ignoredErrors?.some(pattern => {
      if (pattern.startsWith('/') && pattern.endsWith('/')) {
        // Es una expresión regular
        const regex = new RegExp(pattern.slice(1, -1));
        return regex.test(error.message);
      }
      
      // Es una cadena normal
      return error.message.includes(pattern);
    }) || false;
  }
  
  /**
   * Envía los errores acumulados
   */
  private async flush(): Promise<void> {
    if (!this.config.enabled || !this.config.endpoint || this.errorQueue.length === 0) {
      return;
    }
    
    try {
      // Copiar errores actuales y limpiar cola
      const errorsToSend = [...this.errorQueue];
      this.errorQueue = [];
      
      // Enviar errores
      const response = await fetch(this.config.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          errors: errorsToSend,
          source: 'ads-master',
          timestamp: new Date().toISOString()
        }),
        // Usar keepalive para asegurar que se envíe incluso si la página se cierra
        keepalive: true
      });
      
      if (!response.ok) {
        // Si falla, volver a añadir a la cola
        this.errorQueue.unshift(...errorsToSend);
        console.error(`Error al enviar errores: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      // Si falla, volver a añadir a la cola
      this.errorQueue.unshift(...this.errorQueue);
      console.error('Error al enviar errores:', error);
    }
  }
  
  /**
   * Limpieza al desmontar
   */
  public cleanup(): void {
    if (typeof window !== 'undefined') {
      this.teardownGlobalErrorHandlers();
      
      if (this.flushIntervalId) {
        clearInterval(this.flushIntervalId);
      }
    }
    
    // Enviar errores pendientes
    this.flush();
  }
}

// Exponer la instancia global
export const errorTracking = ErrorTrackingService.getInstance();

// Se puede usar directamente como: 
// import { errorTracking } from '@/lib/api-integrations/error-tracking';
// errorTracking.trackError(error);