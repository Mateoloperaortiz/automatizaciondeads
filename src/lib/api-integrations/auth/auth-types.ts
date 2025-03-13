/**
 * Tipos para autenticación en diferentes plataformas de redes sociales
 */

// Estado de autenticación para cualquier plataforma
export interface AuthState {
  isAuthenticated: boolean;
  expiresAt?: number; // Timestamp de expiración del token
  lastRefreshed?: number; // Timestamp de último refresco
}

// Credenciales básicas para todas las plataformas
export interface BaseCredentials {
  clientId: string;
  clientSecret: string;
}

// Credenciales específicas para Meta (Facebook/Instagram)
export interface MetaCredentials extends BaseCredentials {
  accessToken: string;
  longLivedToken?: string;
}

// Credenciales específicas para X (Twitter)
export interface XCredentials extends BaseCredentials {
  accessToken: string;
  accessTokenSecret: string;
}

// Credenciales específicas para Google
export interface GoogleCredentials extends BaseCredentials {
  refreshToken: string;
  accessToken?: string;
  developerToken: string;
  managerId?: string; // ID de la cuenta de Google Ads
}

// Credenciales específicas para TikTok
export interface TikTokCredentials extends BaseCredentials {
  accessToken: string;
  advertiserId?: string;
}

// Credenciales específicas para Snapchat
export interface SnapchatCredentials extends BaseCredentials {
  accessToken: string;
  organizationId?: string;
  businessId?: string;
}

// Opciones para el manejo de tokens
export interface TokenOptions {
  autoRefresh?: boolean;
  refreshThreshold?: number; // En segundos, cuánto tiempo antes de la expiración se debe refrescar
  maxRetries?: number;
}

// Respuesta de la autenticación
export interface AuthResponse {
  success: boolean;
  authState?: AuthState;
  credentials?: any;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

// Tipo de almacenamiento para credenciales
export enum StorageType {
  MEMORY = 'memory',
  LOCAL_STORAGE = 'localStorage',
  SESSION_STORAGE = 'sessionStorage',
  SECURE_STORAGE = 'secureStorage' // Para implementaciones más seguras
}

// Opciones para inicializar el servicio de autenticación
export interface AuthServiceOptions {
  storageType?: StorageType;
  tokenOptions?: TokenOptions;
  secureStorageKey?: string; // Clave para encriptar/desencriptar credenciales en almacenamiento seguro
}