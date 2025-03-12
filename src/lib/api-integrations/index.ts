import { MetaApi } from './meta-api';
import { XApi } from './x-api';
import { GoogleApi } from './google-api';
import { TikTokApi } from './tiktok-api';
import { SnapchatApi } from './snapchat-api';
import { AdCampaign, ApiResponse, SocialMediaApi, SocialPlatform } from './types';

/**
 * Servicio centralizado para gestionar todas las integraciones de API de redes sociales
 */
export class SocialMediaService {
  private metaApi: MetaApi | null = null;
  private xApi: XApi | null = null;
  private googleApi: GoogleApi | null = null;
  private tiktokApi: TikTokApi | null = null;
  private snapchatApi: SnapchatApi | null = null;

  /**
   * Inicializa la API de Meta (Facebook/Instagram)
   */
  initMetaApi(apiKey: string, apiSecret: string, accessToken: string): void {
    this.metaApi = new MetaApi(apiKey, apiSecret, accessToken);
  }

  /**
   * Inicializa la API de X (Twitter)
   */
  initXApi(apiKey: string, apiSecret: string, accessToken: string): void {
    this.xApi = new XApi(apiKey, apiSecret, accessToken);
  }

  /**
   * Inicializa la API de Google Ads
   */
  initGoogleApi(clientId: string, clientSecret: string, refreshToken: string, developerToken: string): void {
    this.googleApi = new GoogleApi(clientId, clientSecret, refreshToken, developerToken);
  }

  /**
   * Inicializa la API de TikTok
   */
  initTikTokApi(accessToken: string, appId: string, appSecret: string): void {
    this.tiktokApi = new TikTokApi(accessToken, appId, appSecret);
  }

  /**
   * Inicializa la API de Snapchat
   */
  initSnapchatApi(accessToken: string, clientId: string, clientSecret: string): void {
    this.snapchatApi = new SnapchatApi(accessToken, clientId, clientSecret);
  }

  /**
   * Obtiene la instancia de API correspondiente a la plataforma especificada
   */
  private getApiForPlatform(platform: SocialPlatform): SocialMediaApi {
    switch (platform) {
      case 'meta':
        if (!this.metaApi) throw new Error('Meta API no inicializada');
        return this.metaApi;
      case 'x':
        if (!this.xApi) throw new Error('X API no inicializada');
        return this.xApi;
      case 'google':
        if (!this.googleApi) throw new Error('Google API no inicializada');
        return this.googleApi;
      case 'tiktok':
        if (!this.tiktokApi) throw new Error('TikTok API no inicializada');
        return this.tiktokApi;
      case 'snapchat':
        if (!this.snapchatApi) throw new Error('Snapchat API no inicializada');
        return this.snapchatApi;
      default:
        throw new Error(`Plataforma no soportada: ${platform}`);
    }
  }

  /**
   * Crea un anuncio en la plataforma especificada
   */
  async createAd(campaign: AdCampaign): Promise<ApiResponse> {
    try {
      const api = this.getApiForPlatform(campaign.platform);
      return await api.createAd(campaign);
    } catch (error: any) {
      console.error(`Error al crear anuncio en ${campaign.platform}:`, error);
      return {
        success: false,
        error: {
          code: 'API_ERROR',
          message: error.message || `Error desconocido al crear anuncio en ${campaign.platform}`
        }
      };
    }
  }

  /**
   * Crea un anuncio en múltiples plataformas simultáneamente
   */
  async createMultiPlatformAd(baseCampaign: Omit<AdCampaign, 'platform'>, platforms: SocialPlatform[]): Promise<Record<SocialPlatform, ApiResponse>> {
    const results: Partial<Record<SocialPlatform, ApiResponse>> = {};

    await Promise.all(
      platforms.map(async (platform) => {
        const campaign = { ...baseCampaign, platform } as AdCampaign;
        results[platform] = await this.createAd(campaign);
      })
    );

    return results as Record<SocialPlatform, ApiResponse>;
  }

  /**
   * Actualiza un anuncio existente en la plataforma especificada
   */
  async updateAd(platform: SocialPlatform, adId: string, campaign: Partial<AdCampaign>): Promise<ApiResponse> {
    try {
      const api = this.getApiForPlatform(platform);
      return await api.updateAd(adId, campaign);
    } catch (error: any) {
      console.error(`Error al actualizar anuncio ${adId} en ${platform}:`, error);
      return {
        success: false,
        error: {
          code: 'API_ERROR',
          message: error.message || `Error desconocido al actualizar anuncio en ${platform}`
        }
      };
    }
  }

  /**
   * Elimina un anuncio de la plataforma especificada
   */
  async deleteAd(platform: SocialPlatform, adId: string): Promise<ApiResponse> {
    try {
      const api = this.getApiForPlatform(platform);
      return await api.deleteAd(adId);
    } catch (error: any) {
      console.error(`Error al eliminar anuncio ${adId} en ${platform}:`, error);
      return {
        success: false,
        error: {
          code: 'API_ERROR',
          message: error.message || `Error desconocido al eliminar anuncio en ${platform}`
        }
      };
    }
  }

  /**
   * Obtiene el estado de un anuncio en la plataforma especificada
   */
  async getAdStatus(platform: SocialPlatform, adId: string): Promise<ApiResponse> {
    try {
      const api = this.getApiForPlatform(platform);
      return await api.getAdStatus(adId);
    } catch (error: any) {
      console.error(`Error al obtener estado del anuncio ${adId} en ${platform}:`, error);
      return {
        success: false,
        error: {
          code: 'API_ERROR',
          message: error.message || `Error desconocido al obtener estado del anuncio en ${platform}`
        }
      };
    }
  }

  /**
   * Obtiene métricas de rendimiento de un anuncio en la plataforma especificada
   */
  async getAdPerformance(platform: SocialPlatform, adId: string, metrics: string[]): Promise<ApiResponse> {
    try {
      const api = this.getApiForPlatform(platform);
      return await api.getAdPerformance(adId, metrics);
    } catch (error: any) {
      console.error(`Error al obtener métricas del anuncio ${adId} en ${platform}:`, error);
      return {
        success: false,
        error: {
          code: 'API_ERROR',
          message: error.message || `Error desconocido al obtener métricas del anuncio en ${platform}`
        }
      };
    }
  }

  /**
   * Obtiene métricas de rendimiento de anuncios en múltiples plataformas
   */
  async getMultiPlatformPerformance(adIds: Record<SocialPlatform, string>, metrics: string[]): Promise<Record<SocialPlatform, ApiResponse>> {
    const results: Partial<Record<SocialPlatform, ApiResponse>> = {};

    await Promise.all(
      Object.entries(adIds).map(async ([platform, adId]) => {
        results[platform as SocialPlatform] = await this.getAdPerformance(platform as SocialPlatform, adId, metrics);
      })
    );

    return results as Record<SocialPlatform, ApiResponse>;
  }
}

// Exportamos todas las clases y tipos para uso externo
export * from './types';
export * from './meta-api';
export * from './x-api';
export * from './google-api';
export * from './tiktok-api';
export * from './snapchat-api';
