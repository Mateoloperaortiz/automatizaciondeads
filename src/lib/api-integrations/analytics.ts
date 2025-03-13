import { SocialPlatform } from './types';
import { sanitizeDataForLogging } from './helpers';

// Tipos de eventos
export enum EventType {
  API_REQUEST = 'api_request',
  API_RESPONSE = 'api_response',
  API_ERROR = 'api_error',
  AD_CREATED = 'ad_created',
  AD_UPDATED = 'ad_updated',
  AD_DELETED = 'ad_deleted',
  AUTHENTICATION = 'authentication',
  RATE_LIMIT = 'rate_limit'
}

// Interfaz para datos de evento
export interface EventData {
  eventType: EventType;
  timestamp: string;
  platform: SocialPlatform;
  endpoint?: string;
  method?: string;
  statusCode?: number;
  duration?: number;
  requestId?: string;
  adId?: string;
  campaignId?: string;
  errorCode?: string;
  errorMessage?: string;
  retryAttempt?: number;
  [key: string]: any;
}

// Configuración
type AnalyticsConfig = {
  enabled: boolean;
  endpoint?: string;
  batchSize?: number;
  flushInterval?: number;
  sampleRate?: number; // Entre 0 y 1
  debug?: boolean;
};

/**
 * Clase para el seguimiento de eventos de API
 */
export class ApiAnalytics {
  private static instance: ApiAnalytics;
  private config: AnalyticsConfig;
  private eventQueue: EventData[] = [];
  private flushIntervalId?: NodeJS.Timeout;
  
  private constructor(config: Partial<AnalyticsConfig> = {}) {
    this.config = {
      enabled: config.enabled !== undefined ? config.enabled : true,
      endpoint: config.endpoint,
      batchSize: config.batchSize || 10,
      flushInterval: config.flushInterval || 30000, // 30 segundos
      sampleRate: config.sampleRate || 1, // Por defecto, rastrear todos los eventos
      debug: config.debug || false,
    };
    
    // Configurar intervalo de envío de eventos
    if (this.config.enabled && typeof window !== 'undefined') {
      this.flushIntervalId = setInterval(() => {
        this.flush();
      }, this.config.flushInterval);
    }
  }
  
  /**
   * Obtener instancia única
   */
  public static getInstance(config?: Partial<AnalyticsConfig>): ApiAnalytics {
    if (!ApiAnalytics.instance) {
      ApiAnalytics.instance = new ApiAnalytics(config);
    }
    
    // Actualizar configuración si se proporciona
    if (config) {
      ApiAnalytics.instance.updateConfig(config);
    }
    
    return ApiAnalytics.instance;
  }
  
  /**
   * Actualizar configuración
   */
  public updateConfig(config: Partial<AnalyticsConfig>): void {
    this.config = { ...this.config, ...config };
    
    // Reiniciar intervalo si cambió
    if (this.flushIntervalId) {
      clearInterval(this.flushIntervalId);
      
      if (this.config.enabled && typeof window !== 'undefined') {
        this.flushIntervalId = setInterval(() => {
          this.flush();
        }, this.config.flushInterval);
      }
    }
  }
  
  /**
   * Registrar un evento
   */
  public trackEvent(data: Omit<EventData, 'timestamp'>): void {
    if (!this.config.enabled) return;
    
    // Aplicar muestreo aleatorio
    if (Math.random() > (this.config.sampleRate || 1)) return;
    
    const event: EventData = {
      ...data,
      timestamp: new Date().toISOString(),
    };
    
    // Sanitizar datos sensibles
    const sanitizedEvent = this.sanitizeEvent(event);
    
    // Agregar a la cola
    this.eventQueue.push(sanitizedEvent);
    
    // Debug logging
    if (this.config.debug) {
      console.log('API Analytics Event:', sanitizedEvent);
    }
    
    // Enviar inmediatamente si alcanzamos el tamaño de lote
    if (this.eventQueue.length >= (this.config.batchSize || 10)) {
      this.flush();
    }
  }
  
  /**
   * Sanitizar datos sensibles del evento
   */
  private sanitizeEvent(event: EventData): EventData {
    // No exponer datos sensibles
    return sanitizeDataForLogging(event) as EventData;
  }
  
  /**
   * Enviar eventos acumulados
   */
  public async flush(): Promise<void> {
    if (!this.config.enabled || this.eventQueue.length === 0) return;
    
    // No enviar si no hay endpoint configurado
    if (!this.config.endpoint) {
      // En desarrollo, solo almacenar en localStorage
      if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
        try {
          const existingEvents = JSON.parse(localStorage.getItem('apiAnalyticsEvents') || '[]');
          localStorage.setItem('apiAnalyticsEvents', JSON.stringify([
            ...existingEvents,
            ...this.eventQueue
          ].slice(-100))); // Limitar a 100 eventos
        } catch (e) {
          console.error('Error guardando eventos de analytics en localStorage:', e);
        }
      }
      
      // Limpiar cola
      this.eventQueue = [];
      return;
    }
    
    try {
      // Copiar eventos actuales y limpiar cola antes de enviar
      // (para evitar perder eventos si falla la solicitud)
      const eventsToSend = [...this.eventQueue];
      this.eventQueue = [];
      
      // Enviar eventos
      const response = await fetch(this.config.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          events: eventsToSend,
          source: 'ads-master',
          timestamp: new Date().toISOString(),
          clientId: this.getClientId()
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Error enviando eventos: ${response.status}`);
      }
      
      if (this.config.debug) {
        console.log(`API Analytics: ${eventsToSend.length} eventos enviados correctamente`);
      }
    } catch (error) {
      console.error('Error enviando eventos de analytics:', error);
      
      // Reintentar más tarde añadiendo de nuevo a la cola
      // Pero limitar el tamaño para evitar consumo excesivo de memoria
      if (this.eventQueue.length + this.eventQueue.length <= 1000) {
        this.eventQueue.unshift(...this.eventQueue);
      }
    }
  }
  
  /**
   * Obtener o generar ID de cliente
   */
  private getClientId(): string {
    if (typeof window === 'undefined') return 'server';
    
    try {
      let clientId = localStorage.getItem('adsMaster_clientId');
      
      if (!clientId) {
        clientId = `client_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
        localStorage.setItem('adsMaster_clientId', clientId);
      }
      
      return clientId;
    } catch (e) {
      return `client_${Date.now()}`;
    }
  }
  
  /**
   * Limpieza al desmontar
   */
  public cleanup(): void {
    if (this.flushIntervalId) {
      clearInterval(this.flushIntervalId);
    }
    
    // Enviar eventos pendientes
    this.flush();
  }
  
  /**
   * Registrar inicio de una petición API
   */
  public trackApiRequest(
    platform: SocialPlatform,
    method: string,
    endpoint: string,
    requestId: string,
    data?: Record<string, any>
  ): void {
    this.trackEvent({
      eventType: EventType.API_REQUEST,
      platform,
      method,
      endpoint,
      requestId,
      requestData: data
    });
  }
  
  /**
   * Registrar respuesta de una petición API
   */
  public trackApiResponse(
    platform: SocialPlatform,
    method: string,
    endpoint: string,
    statusCode: number,
    requestId: string,
    duration: number,
    data?: Record<string, any>
  ): void {
    this.trackEvent({
      eventType: EventType.API_RESPONSE,
      platform,
      method,
      endpoint,
      statusCode,
      requestId,
      duration,
      responseData: data
    });
  }
  
  /**
   * Registrar error de una petición API
   */
  public trackApiError(
    platform: SocialPlatform,
    method: string,
    endpoint: string,
    statusCode: number | undefined,
    errorCode: string,
    errorMessage: string,
    requestId: string,
    duration: number,
    retryAttempt?: number
  ): void {
    this.trackEvent({
      eventType: EventType.API_ERROR,
      platform,
      method,
      endpoint,
      statusCode,
      errorCode,
      errorMessage,
      requestId,
      duration,
      retryAttempt
    });
  }
  
  /**
   * Registrar creación de anuncio
   */
  public trackAdCreated(
    platform: SocialPlatform,
    adId: string,
    campaignId: string,
    adData: Record<string, any>
  ): void {
    this.trackEvent({
      eventType: EventType.AD_CREATED,
      platform,
      adId,
      campaignId,
      adData
    });
  }
  
  /**
   * Registrar actualización de anuncio
   */
  public trackAdUpdated(
    platform: SocialPlatform,
    adId: string,
    campaignId: string,
    updatedFields: string[]
  ): void {
    this.trackEvent({
      eventType: EventType.AD_UPDATED,
      platform,
      adId,
      campaignId,
      updatedFields
    });
  }
  
  /**
   * Registrar eliminación de anuncio
   */
  public trackAdDeleted(
    platform: SocialPlatform,
    adId: string,
    campaignId: string
  ): void {
    this.trackEvent({
      eventType: EventType.AD_DELETED,
      platform,
      adId,
      campaignId
    });
  }
  
  /**
   * Registrar evento de autenticación
   */
  public trackAuthentication(
    platform: SocialPlatform,
    success: boolean,
    errorMessage?: string
  ): void {
    this.trackEvent({
      eventType: EventType.AUTHENTICATION,
      platform,
      success,
      errorMessage
    });
  }
  
  /**
   * Registrar evento de límite de peticiones
   */
  public trackRateLimit(
    platform: SocialPlatform,
    endpoint: string,
    limit: number,
    remaining: number,
    resetAt: string
  ): void {
    this.trackEvent({
      eventType: EventType.RATE_LIMIT,
      platform,
      endpoint,
      limit,
      remaining,
      resetAt
    });
  }
}