import { SocialPlatform } from './types';

// Niveles de log
export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
  CRITICAL = 'critical'
}

// Interfaz para entrada de log
export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  platform?: SocialPlatform;
  data?: Record<string, unknown>;
  requestId?: string;
  // Para errores
  error?: {
    code?: string;
    message?: string;
    stack?: string;
  };
}

// Configuración del logger
interface LoggerConfig {
  minLevel: LogLevel;
  enableConsole: boolean;
  enableFileLogs: boolean;
  logFilePath?: string;
  maxLogSize?: number; // en bytes
  enableRemoteLogging?: boolean;
  remoteLoggingEndpoint?: string;
}

// Configuración por defecto
const DEFAULT_CONFIG: LoggerConfig = {
  minLevel: LogLevel.INFO,
  enableConsole: true,
  enableFileLogs: false,
  maxLogSize: 10 * 1024 * 1024, // 10 MB
  enableRemoteLogging: false
};

/**
 * Logger para APIs de redes sociales
 */
export class ApiLogger {
  private config: LoggerConfig;
  private logEntries: LogEntry[] = [];
  private static instance: ApiLogger;
  
  private constructor(config: Partial<LoggerConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }
  
  /**
   * Obtener la instancia del logger (Singleton)
   */
  public static getInstance(config?: Partial<LoggerConfig>): ApiLogger {
    if (!ApiLogger.instance) {
      ApiLogger.instance = new ApiLogger(config);
    }
    
    // Actualizar configuración si se proporciona
    if (config) {
      ApiLogger.instance.updateConfig(config);
    }
    
    return ApiLogger.instance;
  }
  
  /**
   * Actualizar configuración
   */
  public updateConfig(config: Partial<LoggerConfig>): void {
    this.config = { ...this.config, ...config };
  }
  
  /**
   * Crear entrada de log
   */
  private createLogEntry(
    level: LogLevel,
    message: string,
    platform?: SocialPlatform,
    data?: Record<string, unknown>,
    error?: Error | unknown
  ): LogEntry {
    const timestamp = new Date().toISOString();
    
    const entry: LogEntry = {
      timestamp,
      level,
      message,
      platform,
      data
    };
    
    // Agregar datos de error si existen
    if (error instanceof Error) {
      entry.error = {
        message: error.message,
        stack: error.stack
      };
      
      // Si es un error de API, intentar extraer código
      const apiError = error as any;
      if (apiError.code) {
        entry.error.code = apiError.code;
      }
    } else if (error) {
      entry.error = {
        message: String(error)
      };
    }
    
    return entry;
  }
  
  /**
   * Escribir entrada de log
   */
  private logEntry(entry: LogEntry): void {
    // Guardar en memoria
    this.logEntries.push(entry);
    
    // Limitar tamaño de logs en memoria
    if (this.logEntries.length > 1000) {
      this.logEntries = this.logEntries.slice(-1000);
    }
    
    // Escribir en consola si está habilitado
    if (this.config.enableConsole) {
      this.writeToConsole(entry);
    }
    
    // Enviar a endpoint remoto si está habilitado
    if (this.config.enableRemoteLogging && this.config.remoteLoggingEndpoint) {
      this.sendToRemote(entry).catch(() => {
        // Ignorar errores de envío remoto
      });
    }
  }
  
  /**
   * Escribir en consola
   */
  private writeToConsole(entry: LogEntry): void {
    const prefix = `[${entry.timestamp}] [${entry.level.toUpperCase()}]${entry.platform ? ` [${entry.platform}]` : ''}`;
    
    switch (entry.level) {
      case LogLevel.DEBUG:
        console.debug(prefix, entry.message, entry.data || '');
        break;
      case LogLevel.INFO:
        console.info(prefix, entry.message, entry.data || '');
        break;
      case LogLevel.WARN:
        console.warn(prefix, entry.message, entry.data || '');
        break;
      case LogLevel.ERROR:
      case LogLevel.CRITICAL:
        console.error(prefix, entry.message, entry.error || entry.data || '');
        break;
    }
  }
  
  /**
   * Enviar a endpoint remoto
   */
  private async sendToRemote(entry: LogEntry): Promise<void> {
    if (!this.config.remoteLoggingEndpoint) return;
    
    try {
      const response = await fetch(this.config.remoteLoggingEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(entry)
      });
      
      if (!response.ok) {
        console.error('Error al enviar log a endpoint remoto:', response.statusText);
      }
    } catch (error) {
      console.error('Error al enviar log a endpoint remoto:', error);
    }
  }
  
  /**
   * Log de nivel debug
   */
  public debug(message: string, platform?: SocialPlatform, data?: Record<string, unknown>): void {
    if (this.config.minLevel > LogLevel.DEBUG) return;
    const entry = this.createLogEntry(LogLevel.DEBUG, message, platform, data);
    this.logEntry(entry);
  }
  
  /**
   * Log de nivel info
   */
  public info(message: string, platform?: SocialPlatform, data?: Record<string, unknown>): void {
    if (this.config.minLevel > LogLevel.INFO) return;
    const entry = this.createLogEntry(LogLevel.INFO, message, platform, data);
    this.logEntry(entry);
  }
  
  /**
   * Log de nivel warn
   */
  public warn(message: string, platform?: SocialPlatform, data?: Record<string, unknown>): void {
    if (this.config.minLevel > LogLevel.WARN) return;
    const entry = this.createLogEntry(LogLevel.WARN, message, platform, data);
    this.logEntry(entry);
  }
  
  /**
   * Log de nivel error
   */
  public error(message: string, error?: Error | unknown, platform?: SocialPlatform, data?: Record<string, unknown>): void {
    if (this.config.minLevel > LogLevel.ERROR) return;
    const entry = this.createLogEntry(LogLevel.ERROR, message, platform, data, error);
    this.logEntry(entry);
  }
  
  /**
   * Log de nivel crítico
   */
  public critical(message: string, error?: Error | unknown, platform?: SocialPlatform, data?: Record<string, unknown>): void {
    if (this.config.minLevel > LogLevel.CRITICAL) return;
    const entry = this.createLogEntry(LogLevel.CRITICAL, message, platform, data, error);
    this.logEntry(entry);
  }
  
  /**
   * Log para solicitudes API
   */
  public logApiRequest(
    platform: SocialPlatform,
    method: string,
    endpoint: string,
    requestData?: Record<string, unknown>
  ): string {
    // Generar ID único para la solicitud para seguimiento
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    this.info(
      `API Request: ${method} ${endpoint}`,
      platform,
      {
        method,
        endpoint,
        requestId,
        data: requestData
      }
    );
    
    return requestId;
  }
  
  /**
   * Log para respuestas API
   */
  public logApiResponse(
    platform: SocialPlatform,
    method: string,
    endpoint: string,
    statusCode: number,
    responseData: Record<string, unknown>,
    requestId?: string,
    durationMs?: number
  ): void {
    this.info(
      `API Response: ${method} ${endpoint} - ${statusCode}`,
      platform,
      {
        method,
        endpoint,
        statusCode,
        requestId,
        durationMs,
        data: responseData
      }
    );
  }
  
  /**
   * Log para errores API
   */
  public logApiError(
    platform: SocialPlatform,
    method: string,
    endpoint: string,
    error: Error | unknown,
    requestId?: string,
    durationMs?: number
  ): void {
    this.error(
      `API Error: ${method} ${endpoint}`,
      error,
      platform,
      {
        method,
        endpoint,
        requestId,
        durationMs
      }
    );
  }
  
  /**
   * Obtener todas las entradas de log
   */
  public getLogs(): LogEntry[] {
    return [...this.logEntries];
  }
  
  /**
   * Filtrar logs por nivel
   */
  public getLogsByLevel(level: LogLevel): LogEntry[] {
    return this.logEntries.filter(entry => entry.level === level);
  }
  
  /**
   * Filtrar logs por plataforma
   */
  public getLogsByPlatform(platform: SocialPlatform): LogEntry[] {
    return this.logEntries.filter(entry => entry.platform === platform);
  }
  
  /**
   * Limpiar logs
   */
  public clearLogs(): void {
    this.logEntries = [];
  }
}