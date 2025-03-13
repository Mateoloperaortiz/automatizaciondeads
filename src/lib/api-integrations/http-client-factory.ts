import { SocialPlatform } from './types';
import { EnhancedHttpClient, HttpClientConfig } from './enhanced-http-client';

// Configuraciones por defecto para cada plataforma
const defaultConfigs: Record<SocialPlatform, HttpClientConfig> = {
  meta: {
    baseUrl: 'https://graph.facebook.com/v18.0',
    timeout: 30000,
    retries: 3
  },
  google: {
    baseUrl: 'https://googleads.googleapis.com/v15',
    timeout: 60000, // Google APIs pueden ser más lentas
    retries: 3
  },
  x: {
    baseUrl: 'https://api.twitter.com/2',
    timeout: 30000,
    retries: 2
  },
  tiktok: {
    baseUrl: 'https://business-api.tiktok.com/open_api/v1.3',
    timeout: 30000,
    retries: 3
  },
  snapchat: {
    baseUrl: 'https://adsapi.snapchat.com/v1',
    timeout: 30000,
    retries: 3
  }
};

// Cache de instancias de clientes por plataforma
const clientInstances = new Map<SocialPlatform, EnhancedHttpClient>();

/**
 * Factory para crear clientes HTTP para diferentes plataformas
 */
export class HttpClientFactory {
  /**
   * Crea o recupera un cliente HTTP para una plataforma específica
   */
  static getClient(
    platform: SocialPlatform, 
    accessToken?: string,
    customConfig?: Partial<HttpClientConfig>
  ): EnhancedHttpClient {
    // Si ya existe una instancia para esta plataforma
    if (clientInstances.has(platform)) {
      const existingClient = clientInstances.get(platform)!;
      
      // Actualizar el token de acceso si es necesario
      if (accessToken) {
        existingClient.setAccessToken(accessToken);
      }
      
      // Actualizar configuración si es necesario
      if (customConfig) {
        existingClient.updateConfig(customConfig);
      }
      
      return existingClient;
    }
    
    // Combinar configuración por defecto con personalizada
    const config: HttpClientConfig = {
      ...defaultConfigs[platform],
      ...customConfig
    };
    
    // Crear nueva instancia
    const newClient = new EnhancedHttpClient(platform, config);
    
    // Establecer token de acceso si se proporciona
    if (accessToken) {
      newClient.setAccessToken(accessToken);
    }
    
    // Guardar en cache
    clientInstances.set(platform, newClient);
    
    return newClient;
  }
  
  /**
   * Elimina una instancia de cliente del cache
   */
  static removeClient(platform: SocialPlatform): void {
    clientInstances.delete(platform);
  }
  
  /**
   * Limpia toda la cache de clientes
   */
  static clearClients(): void {
    clientInstances.clear();
  }
  
  /**
   * Actualiza el token de acceso para una plataforma
   */
  static updateAccessToken(platform: SocialPlatform, accessToken: string): void {
    const client = this.getClient(platform);
    client.setAccessToken(accessToken);
  }
}