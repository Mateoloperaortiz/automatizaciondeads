import { ApiErrorDetail, ApiResponse, SocialPlatform } from './types';
import axios, { AxiosError } from 'axios';

// Types of errors we might encounter in API calls
export enum ErrorType {
  NETWORK = 'NETWORK',
  AUTH = 'AUTH',
  RATE_LIMIT = 'RATE_LIMIT',
  VALIDATION = 'VALIDATION',
  NOT_FOUND = 'NOT_FOUND',
  SERVER = 'SERVER',
  TIMEOUT = 'TIMEOUT',
  UNKNOWN = 'UNKNOWN'
}

// Platform-specific error codes
export interface PlatformErrorMap {
  [key: string]: {
    type: ErrorType;
    message: string;
    retryable: boolean;
  };
}

// Define platform-specific error mappings
const errorMaps: Record<SocialPlatform, PlatformErrorMap> = {
  meta: {
    '1': { type: ErrorType.VALIDATION, message: 'API parámetro inválido', retryable: false },
    '2': { type: ErrorType.SERVER, message: 'Error de servicio', retryable: true },
    '4': { type: ErrorType.RATE_LIMIT, message: 'Límite de peticiones alcanzado', retryable: true },
    '17': { type: ErrorType.RATE_LIMIT, message: 'Límite de peticiones por usuario alcanzado', retryable: true },
    '100': { type: ErrorType.VALIDATION, message: 'Error de sintaxis en la petición', retryable: false },
    '102': { type: ErrorType.VALIDATION, message: 'Formato de sesión inválido', retryable: false },
    '190': { type: ErrorType.AUTH, message: 'Token de acceso inválido o expirado', retryable: false },
    '200': { type: ErrorType.NOT_FOUND, message: 'Recurso no encontrado', retryable: false },
    '294': { type: ErrorType.VALIDATION, message: 'Error en la gestión de la campaña publicitaria', retryable: false },
    '2635': { type: ErrorType.VALIDATION, message: 'Error en la segmentación del anuncio', retryable: false },
    '1487395': { type: ErrorType.VALIDATION, message: 'Límite de gasto diario demasiado bajo', retryable: false },
  },
  
  google: {
    'AUTHENTICATION_ERROR': { type: ErrorType.AUTH, message: 'Error de autenticación', retryable: false },
    'AUTHORIZATION_ERROR': { type: ErrorType.AUTH, message: 'Error de autorización', retryable: false },
    'CUSTOMER_NOT_FOUND': { type: ErrorType.NOT_FOUND, message: 'Cliente no encontrado', retryable: false },
    'INVALID_PAGE_TOKEN': { type: ErrorType.VALIDATION, message: 'Token de página inválido', retryable: false },
    'QUOTA_EXCEEDED': { type: ErrorType.RATE_LIMIT, message: 'Cuota excedida', retryable: true },
    'RESOURCE_EXHAUSTED': { type: ErrorType.RATE_LIMIT, message: 'Recursos agotados', retryable: true },
    'REQUEST_ERROR': { type: ErrorType.NETWORK, message: 'Error en la petición', retryable: true },
    'SERVER_ERROR': { type: ErrorType.SERVER, message: 'Error del servidor', retryable: true },
    'DEADLINE_EXCEEDED': { type: ErrorType.TIMEOUT, message: 'Tiempo de espera agotado', retryable: true },
  },
  
  x: {
    '32': { type: ErrorType.AUTH, message: 'No se pudo autenticar', retryable: false },
    '34': { type: ErrorType.NOT_FOUND, message: 'Recurso no existe', retryable: false },
    '88': { type: ErrorType.RATE_LIMIT, message: 'Límite de peticiones excedido', retryable: true },
    '89': { type: ErrorType.VALIDATION, message: 'Token inválido', retryable: false },
    '130': { type: ErrorType.SERVER, message: 'Capacidad excedida', retryable: true },
    '131': { type: ErrorType.SERVER, message: 'Error interno', retryable: true },
    '135': { type: ErrorType.AUTH, message: 'No autenticado', retryable: false },
    '170': { type: ErrorType.VALIDATION, message: 'Error en la lista de permisos', retryable: false },
    '185': { type: ErrorType.VALIDATION, message: 'Límite de estatus actualizado', retryable: false },
    '187': { type: ErrorType.VALIDATION, message: 'Contenido duplicado', retryable: false },
    '220': { type: ErrorType.VALIDATION, message: 'Credenciales inválidas', retryable: false },
  },
  
  tiktok: {
    '40001': { type: ErrorType.VALIDATION, message: 'Parámetro requerido faltante', retryable: false },
    '40002': { type: ErrorType.VALIDATION, message: 'Parámetro inválido', retryable: false },
    '40003': { type: ErrorType.VALIDATION, message: 'Petición inválida', retryable: false },
    '40100': { type: ErrorType.AUTH, message: 'Token de acceso inválido', retryable: false },
    '40101': { type: ErrorType.AUTH, message: 'Token de acceso expirado', retryable: false },
    '40301': { type: ErrorType.AUTH, message: 'Acceso denegado', retryable: false },
    '40400': { type: ErrorType.NOT_FOUND, message: 'Recurso no encontrado', retryable: false },
    '40900': { type: ErrorType.VALIDATION, message: 'Acción no permitida por política de la plataforma', retryable: false },
    '42900': { type: ErrorType.RATE_LIMIT, message: 'Demasiadas peticiones', retryable: true },
    '50000': { type: ErrorType.SERVER, message: 'Error del servidor', retryable: true },
  },
  
  snapchat: {
    'INVALID_ARGUMENT': { type: ErrorType.VALIDATION, message: 'Argumento inválido', retryable: false },
    'AUTHENTICATION_ERROR': { type: ErrorType.AUTH, message: 'Error de autenticación', retryable: false },
    'AUTHORIZATION_ERROR': { type: ErrorType.AUTH, message: 'Error de autorización', retryable: false },
    'NOT_FOUND': { type: ErrorType.NOT_FOUND, message: 'Recurso no encontrado', retryable: false },
    'RESOURCE_EXHAUSTED': { type: ErrorType.RATE_LIMIT, message: 'Límite de peticiones alcanzado', retryable: true },
    'UNAVAILABLE': { type: ErrorType.SERVER, message: 'Servicio no disponible', retryable: true },
    'DEADLINE_EXCEEDED': { type: ErrorType.TIMEOUT, message: 'Tiempo de espera agotado', retryable: true },
    'INTERNAL': { type: ErrorType.SERVER, message: 'Error interno del servidor', retryable: true },
  }
};

/**
 * Determina si el error es un problema de red
 */
export function isNetworkError(error: unknown): boolean {
  return axios.isAxiosError(error) && error.message === 'Network Error';
}

/**
 * Determina si el error es causado por límite de peticiones
 */
export function isRateLimitError(
  error: unknown, 
  platform: SocialPlatform, 
  statusCode?: number, 
  errorCode?: string
): boolean {
  if (statusCode === 429) {
    return true;
  }
  
  if (errorCode && errorMaps[platform][errorCode]) {
    return errorMaps[platform][errorCode].type === ErrorType.RATE_LIMIT;
  }
  
  // Casos especiales por plataforma
  if (platform === 'meta' && axios.isAxiosError(error)) {
    const axiosError = error as AxiosError;
    const errorData = axiosError.response?.data as any;
    return (errorData?.error?.code === 4 || errorData?.error?.code === 17);
  }
  
  return false;
}

/**
 * Determina si el error es un problema de autenticación
 */
export function isAuthError(
  error: unknown, 
  platform: SocialPlatform, 
  statusCode?: number, 
  errorCode?: string
): boolean {
  if (statusCode === 401 || statusCode === 403) {
    return true;
  }
  
  if (errorCode && errorMaps[platform][errorCode]) {
    return errorMaps[platform][errorCode].type === ErrorType.AUTH;
  }
  
  // Casos especiales por plataforma
  if (platform === 'meta' && axios.isAxiosError(error)) {
    const axiosError = error as AxiosError;
    const errorData = axiosError.response?.data as any;
    return errorData?.error?.code === 190;
  }
  
  return false;
}

/**
 * Determina si el error permite reintentar
 */
export function isRetryableError(
  error: unknown, 
  platform: SocialPlatform, 
  statusCode?: number, 
  errorCode?: string
): boolean {
  // Errores de red casi siempre son reintentables
  if (isNetworkError(error)) {
    return true;
  }
  
  // Errores de límite de peticiones son reintentables
  if (isRateLimitError(error, platform, statusCode, errorCode)) {
    return true;
  }
  
  // Errores de servidor son generalmente reintentables
  if (statusCode && statusCode >= 500 && statusCode < 600) {
    return true;
  }
  
  // Consultar el mapeo específico de la plataforma
  if (errorCode && errorMaps[platform][errorCode]) {
    return errorMaps[platform][errorCode].retryable;
  }
  
  return false;
}

/**
 * Extrae información de un error de Axios
 */
export function extractAxiosErrorInfo(error: AxiosError, platform: SocialPlatform): {
  statusCode?: number;
  errorCode?: string;
  errorMessage?: string;
} {
  const statusCode = error.response?.status;
  let errorCode: string | undefined;
  let errorMessage: string | undefined;
  
  if (error.response?.data) {
    const data = error.response.data as any;
    
    switch (platform) {
      case 'meta':
        errorCode = data.error?.code?.toString();
        errorMessage = data.error?.message;
        break;
        
      case 'google':
        errorCode = data.error?.status || data.error?.code;
        errorMessage = data.error?.message;
        break;
        
      case 'x':
        errorCode = data.errors?.[0]?.code?.toString();
        errorMessage = data.errors?.[0]?.message;
        break;
        
      case 'tiktok':
        errorCode = data.code?.toString();
        errorMessage = data.message;
        break;
        
      case 'snapchat':
        errorCode = data.error?.code;
        errorMessage = data.error?.message;
        break;
    }
  }
  
  return { statusCode, errorCode, errorMessage };
}

/**
 * Crea un objeto ApiErrorDetail a partir de errores
 */
export function createApiError(
  error: unknown, 
  platform: SocialPlatform,
  defaultCode = 'UNKNOWN_ERROR',
  defaultMessage = 'Error desconocido en la petición a la API'
): ApiErrorDetail {
  // Error genérico para iniciar
  const apiError: ApiErrorDetail = {
    code: defaultCode,
    message: defaultMessage,
    platform,
    retryable: false,
    rateLimited: false,
    authError: false,
    originalError: error
  };
  
  // Si es un error de red
  if (isNetworkError(error)) {
    apiError.code = 'NETWORK_ERROR';
    apiError.message = 'Error de conexión con la API. Verifique su conexión a internet.';
    apiError.retryable = true;
    return apiError;
  }
  
  // Si es un error de Axios
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError;
    const { statusCode, errorCode, errorMessage } = extractAxiosErrorInfo(axiosError, platform);
    
    apiError.statusCode = statusCode;
    
    // Asignar código y mensaje específicos de la plataforma si están disponibles
    if (errorCode) {
      apiError.code = `${platform.toUpperCase()}_${errorCode}`;
      
      // Obtener información del mapeo de errores
      if (errorMaps[platform][errorCode]) {
        const errorInfo = errorMaps[platform][errorCode];
        apiError.message = errorMessage || errorInfo.message;
        apiError.retryable = errorInfo.retryable;
        apiError.rateLimited = errorInfo.type === ErrorType.RATE_LIMIT;
        apiError.authError = errorInfo.type === ErrorType.AUTH;
      } else {
        apiError.message = errorMessage || `Error ${errorCode} en la API de ${platform}`;
      }
    } else {
      // Error basado en código HTTP
      if (statusCode) {
        switch (true) {
          case statusCode === 401:
            apiError.code = `${platform.toUpperCase()}_AUTH_ERROR`;
            apiError.message = 'Error de autenticación. Credenciales inválidas o expiradas.';
            apiError.authError = true;
            apiError.recommendedAction = 'Intente reconectar su cuenta.';
            break;
            
          case statusCode === 403:
            apiError.code = `${platform.toUpperCase()}_FORBIDDEN`;
            apiError.message = 'Acceso denegado. No tiene permisos para esta operación.';
            apiError.authError = true;
            apiError.recommendedAction = 'Verifique los permisos de su cuenta.';
            break;
            
          case statusCode === 404:
            apiError.code = `${platform.toUpperCase()}_NOT_FOUND`;
            apiError.message = 'Recurso no encontrado.';
            break;
            
          case statusCode === 429:
            apiError.code = `${platform.toUpperCase()}_RATE_LIMIT`;
            apiError.message = 'Ha excedido el límite de peticiones. Intente más tarde.';
            apiError.rateLimited = true;
            apiError.retryable = true;
            apiError.recommendedAction = 'Espere antes de intentar nuevamente.';
            break;
            
          case statusCode >= 500:
            apiError.code = `${platform.toUpperCase()}_SERVER_ERROR`;
            apiError.message = 'Error del servidor. Intente más tarde.';
            apiError.retryable = true;
            break;
        }
      }
    }
  } else if (error instanceof Error) {
    apiError.message = error.message;
  }
  
  return apiError;
}

/**
 * Crea una respuesta de error estándar
 */
export function createErrorResponse(error: unknown, platform: SocialPlatform): ApiResponse {
  const apiError = createApiError(error, platform);
  
  return {
    success: false,
    error: apiError
  };
}

/**
 * Maneja errores de API de forma centralizada
 */
export async function handleApiError(
  error: unknown, 
  platform: SocialPlatform,
  retryCallback?: () => Promise<any>,
  maxRetries = 3,
  currentRetry = 0
): Promise<ApiResponse> {
  const apiError = createApiError(error, platform);
  
  // Si el error es reintentable y tenemos una función de reintento
  if (apiError.retryable && retryCallback && currentRetry < maxRetries) {
    // Calcular tiempo de espera basado en backoff exponencial
    const retryDelay = apiError.rateLimited
      ? 5000 * Math.pow(2, currentRetry) // Retraso más largo para límite de peticiones
      : 1000 * Math.pow(2, currentRetry); // Retraso estándar para otros errores reintentables
    
    console.log(`Reintentando petición (${currentRetry + 1}/${maxRetries}) en ${retryDelay/1000} segundos...`);
    
    // Esperar antes de reintentar
    await new Promise(resolve => setTimeout(resolve, retryDelay));
    
    try {
      // Reintentar operación
      return await retryCallback();
    } catch (retryError) {
      // Gestionar error de reintento recursivamente
      return handleApiError(retryError, platform, retryCallback, maxRetries, currentRetry + 1);
    }
  }
  
  // Si no podemos reintentar, devolver respuesta de error
  return {
    success: false,
    error: apiError
  };
}