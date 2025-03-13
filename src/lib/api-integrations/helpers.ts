import { SocialPlatform } from './types';

/**
 * Formatea datos para ser enviados por webhook
 */
export function formatGraphDataForWebhook(data: Record<string, unknown>): Record<string, unknown> {
  // Eliminar cualquier información sensible
  const sanitizedData = { ...data };
  
  // Asegurarse de que no se envíen credenciales
  delete sanitizedData.apiKey;
  delete sanitizedData.apiSecret;
  delete sanitizedData.accessToken;
  delete sanitizedData.credentials;
  
  return sanitizedData;
}

/**
 * Genera un ID único para solicitudes
 */
export function generateRequestId(platform: SocialPlatform): string {
  return `${platform}_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Sanitiza datos para logging (elimina información sensible)
 */
export function sanitizeDataForLogging(data: Record<string, unknown>): Record<string, unknown> {
  const result = { ...data };
  
  // Lista de claves sensibles a sanitizar
  const sensitiveKeys = [
    'apiKey', 'apiSecret', 'accessToken', 'refreshToken', 'credentials',
    'clientId', 'clientSecret', 'token', 'password', 'key', 'secret'
  ];
  
  // Buscar y sanitizar claves sensibles en el primer nivel
  Object.keys(result).forEach(key => {
    if (sensitiveKeys.includes(key.toLowerCase())) {
      const value = result[key] as string;
      
      // Si la propiedad existe y es una cadena
      if (value && typeof value === 'string') {
        // Mostrar solo los primeros 4 caracteres
        result[key] = value.substring(0, 4) + '...' + value.substring(value.length - 4);
      } else {
        result[key] = '[REDACTED]';
      }
    }
    
    // Si es un objeto anidado, sanitizar recursivamente
    if (result[key] && typeof result[key] === 'object' && !Array.isArray(result[key])) {
      result[key] = sanitizeDataForLogging(result[key] as Record<string, unknown>);
    }
  });
  
  return result;
}

/**
 * Valida si un error de API es causado por autenticación
 */
export function isAuthenticationError(statusCode?: number, errorCode?: string): boolean {
  return statusCode === 401 || statusCode === 403 || 
         errorCode === '190' || // Meta
         errorCode === '32' || // X
         errorCode === '40100' || errorCode === '40101'; // TikTok
}

/**
 * Formatea errores para respuestas consistentes
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  return 'Error desconocido';
}

/**
 * Filtra parámetros de consulta vacíos o nulos
 */
export function filterEmptyParams(params: Record<string, any>): Record<string, any> {
  return Object.entries(params)
    .filter(([_, value]) => value !== null && value !== undefined && value !== '')
    .reduce((obj, [key, value]) => ({
      ...obj,
      [key]: value
    }), {});
}

/**
 * Normaliza nombres de campos (camelCase a snake_case)
 */
export function toSnakeCase(str: string): string {
  return str.replace(/([A-Z])/g, (g) => `_${g[0].toLowerCase()}`);
}

/**
 * Convierte objeto de camelCase a snake_case
 */
export function convertToSnakeCase(obj: Record<string, any>): Record<string, any> {
  const result: Record<string, any> = {};
  
  Object.entries(obj).forEach(([key, value]) => {
    // Convertir la clave
    const newKey = toSnakeCase(key);
    
    // Procesar recursivamente objetos anidados
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      result[newKey] = convertToSnakeCase(value);
    } else {
      result[newKey] = value;
    }
  });
  
  return result;
}

/**
 * Normaliza nombres de campos (snake_case a camelCase)
 */
export function toCamelCase(str: string): string {
  return str.replace(/_([a-z])/g, (g) => g[1].toUpperCase());
}

/**
 * Convierte objeto de snake_case a camelCase
 */
export function convertToCamelCase(obj: Record<string, any>): Record<string, any> {
  const result: Record<string, any> = {};
  
  Object.entries(obj).forEach(([key, value]) => {
    // Convertir la clave
    const newKey = toCamelCase(key);
    
    // Procesar recursivamente objetos anidados
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      result[newKey] = convertToCamelCase(value);
    } else if (Array.isArray(value)) {
      // Si es un array de objetos, procesar cada objeto
      if (value.length > 0 && typeof value[0] === 'object') {
        result[newKey] = value.map(item => 
          typeof item === 'object' ? convertToCamelCase(item) : item
        );
      } else {
        result[newKey] = value;
      }
    } else {
      result[newKey] = value;
    }
  });
  
  return result;
}