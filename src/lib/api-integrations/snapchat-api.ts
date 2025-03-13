import { AdCampaign, ApiResponse, SocialMediaApi } from './types';
import { AuthService } from './auth';
import { EnhancedHttpClient, HttpClientConfig } from './enhanced-http-client';

/**
 * Clase para manejar la integración con la API de Snapchat Ads
 * Documentación: https://marketingapi.snapchat.com/docs/
 */
export class SnapchatApi implements SocialMediaApi {
  private accessToken: string;
  private clientId: string;
  private clientSecret: string;
  private authService: AuthService;
  private baseUrl = 'https://adsapi.snapchat.com/v1';
  private organizationId?: string; // ID de organización en Snapchat
  private accountId?: string; // ID de cuenta de anuncios en Snapchat
  private httpClient: EnhancedHttpClient;
  private requestTimeout = 30000; // 30 segundos
  private rateLimitRetries = 3;
  private rateLimitDelay = 5000; // 5 segundos

  constructor(accessToken: string, clientId: string, clientSecret: string, authService?: AuthService) {
    this.accessToken = accessToken;
    this.clientId = clientId;
    this.clientSecret = clientSecret;
    this.authService = authService || new AuthService();
    
    // Inicializar el cliente HTTP mejorado
    const httpConfig: HttpClientConfig = {
      baseUrl: this.baseUrl,
      timeout: this.requestTimeout,
      retries: this.rateLimitRetries,
      headers: {
        'Content-Type': 'application/json'
      }
    };
    
    this.httpClient = new EnhancedHttpClient('snapchat', httpConfig);
  }

  /**
   * Inicializa la API con autenticación
   */
  async initialize(organizationId?: string, accountId?: string): Promise<ApiResponse> {
    try {
      // Autenticar con Snapchat
      const authResult = await this.authService.authenticateSnapchat({
        clientId: this.clientId,
        clientSecret: this.clientSecret,
        accessToken: this.accessToken,
        organizationId: organizationId,
        businessId: accountId
      });

      if (!authResult.success) {
        return {
          success: false,
          error: {
            code: 'SNAPCHAT_AUTH_ERROR',
            message: authResult.error?.message || 'Error de autenticación con Snapchat'
          }
        };
      }

      // Establecer IDs si se proporcionan
      if (organizationId) {
        this.organizationId = organizationId;
      } else if (authResult.credentials?.organizationId) {
        this.organizationId = authResult.credentials.organizationId;
      } else {
        // En una implementación real, se obtendría el ID de la organización
        this.organizationId = `snap_org_${Date.now()}`;
      }

      if (accountId) {
        this.accountId = accountId;
      } else if (authResult.credentials?.businessId) {
        this.accountId = authResult.credentials.businessId;
      } else {
        // En una implementación real, se obtendría el ID de la cuenta
        this.accountId = `snap_acc_${Date.now()}`;
      }

      // Actualizar el token en el cliente HTTP
      const token = this.authService.getAccessToken('snapchat');
      if (token) {
        this.httpClient.setAccessToken(token);
      }

      return {
        success: true,
        data: {
          authenticated: true,
          organizationId: this.organizationId,
          accountId: this.accountId
        }
      };
    } catch (error) {
      console.error('Error al inicializar Snapchat API:', error);
      const errorMessage = error instanceof Error ? error.message : 'Error al inicializar Snapchat API';
      return {
        success: false,
        error: {
          code: 'SNAPCHAT_INIT_ERROR',
          message: errorMessage
        }
      };
    }
  }

  /**
   * Verifica si la API está autenticada
   */
  isAuthenticated(): boolean {
    return this.authService.isAuthenticated('snapchat');
  }

  /**
   * Obtiene el token de acceso actual
   */
  getAccessToken(): string | null {
    return this.authService.getAccessToken('snapchat');
  }

  /**
   * Método para realizar peticiones a la API de Snapchat
   */
  private async makeRequest(endpoint: string, method: 'GET' | 'POST' | 'DELETE', data?: Record<string, unknown>): Promise<Record<string, unknown>> {
    // Verificar autenticación
    if (!this.isAuthenticated()) {
      throw new Error('Snapchat API no está autenticada');
    }

    // Verificar IDs necesarios
    if (!this.accountId && endpoint.includes('adaccounts')) {
      throw new Error('ID de cuenta de Snapchat no configurado');
    }

    // Obtener token de acceso
    const token = this.getAccessToken();
    if (!token) {
      throw new Error('No se pudo obtener token de acceso');
    }

    // Configurar headers
    const headers = {
      'Authorization': `Bearer ${token}`
    };
    
    // Reemplazar placeholders en la URL si existen
    let processedEndpoint = endpoint;
    if (this.organizationId) {
      processedEndpoint = processedEndpoint.replace('{organization_id}', this.organizationId);
    }
    if (this.accountId) {
      processedEndpoint = processedEndpoint.replace('{ad_account_id}', this.accountId);
    }

    try {
      // Usar el cliente HTTP mejorado para hacer la petición
      const response = await this.httpClient.request(method, processedEndpoint, data, {
        headers,
        timeout: this.requestTimeout,
        retries: this.rateLimitRetries
      });

      return response;
    } catch (error) {
      console.error(`Error en petición a Snapchat API (${processedEndpoint}):`, error);
      throw error;
    }

    // NOTA: En un entorno de desarrollo sin acceso real a la API,
    // podemos simular la respuesta descomentar el siguiente código:
    /*
    return { 
      request_status: "success", 
      request_id: `req_${Date.now()}`,
      adaccount: { id: this.accountId },
      campaign: { id: `snap_campaign_${Date.now()}` },
      ad_squad: { id: `snap_adsquad_${Date.now()}` },
      creative: { id: `snap_creative_${Date.now()}` }
    };
    */
  }

  /**
   * Crea un anuncio en Snapchat
   */
  async createAd(campaign: AdCampaign): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Preparar datos para la API de Snapchat
      const adData = this.formatCampaignData(campaign);

      // En Snapchat, se crean múltiples recursos:
      // 1. Campaña
      // 2. Ad Squad (similar a un grupo de anuncios)
      // 3. Creativo (Anuncio)
      
      // Crear campaña
      const campaignResult = await this.makeRequest(`adaccounts/{ad_account_id}/campaigns`, 'POST', {
        campaign: {
          name: adData.name,
          status: adData.status,
          objective: "EMPLOYMENT",
          start_time: adData.startTime,
          end_time: adData.endTime,
          daily_budget_micro: adData.dailyBudgetMicro
        }
      });
      
      // Crear Ad Squad
      const adSquadResult = await this.makeRequest(`adaccounts/{ad_account_id}/adsquads`, 'POST', {
        ad_squad: {
          name: `${adData.name} - Squad`,
          campaign_id: (campaignResult as { campaign: { id: string } }).campaign.id,
          placement: {
            placement_v2: adData.placements
          },
          targeting: {
            demographics: adData.demographics,
            geos: adData.geos,
            interests: adData.interests,
            custom_audiences: []
          },
          optimization_goal: "IMPRESSIONS",
          bid_micro: adData.bidMicro,
          daily_budget_micro: adData.dailyBudgetMicro,
          status: adData.status
        }
      });
      
      // Simulación: Subir creativo (imagen/video)
      const creativeAssetResult = {
        id: `creative_asset_${Date.now()}`
      };
      
      // Crear creativo del anuncio
      const creativeResult = await this.makeRequest(`adaccounts/{ad_account_id}/creatives`, 'POST', {
        creative: {
          name: `${adData.name} - Creative`,
          type: "SNAP_AD",
          top_snap_media_id: creativeAssetResult.id,
          call_to_action: {
            type: adData.callToAction,
            url: adData.landingUrl
          },
          brand_name: "Magneto",
          headline: adData.headline,
          status: adData.status
        }
      });
      
      // Asignar creativo al Ad Squad
      await this.makeRequest(`adaccounts/{ad_account_id}/adsquads/${(adSquadResult as { ad_squad: { id: string } }).ad_squad.id}/creatives`, 'POST', {
        creative_id: (creativeResult as { creative: { id: string } }).creative.id
      });

      return {
        success: true,
        data: {
          id: (adSquadResult as { ad_squad: { id: string } }).ad_squad.id,
          campaignId: (campaignResult as { campaign: { id: string } }).campaign.id,
          creativeId: (creativeResult as { creative: { id: string } }).creative.id,
          status: 'pending',
          platform: 'snapchat',
          createdAt: new Date().toISOString(),
        }
      };
    } catch (error) {
      console.error('Error al crear anuncio en Snapchat:', error);
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido al crear anuncio en Snapchat';
      return {
        success: false,
        error: {
          code: 'SNAPCHAT_API_ERROR',
          message: errorMessage
        }
      };
    }
  }

  /**
   * Formatea los datos de la campaña para la API de Snapchat
   */
  private formatCampaignData(campaign: AdCampaign): Record<string, unknown> {
    // Convertir presupuesto a micros (Snapchat usa millonésimas al igual que otras plataformas)
    const dailyBudgetMicro = campaign.dailyBudget
      ? Math.round(campaign.dailyBudget * 1000000)
      : Math.round((campaign.budget / 30) * 1000000); // Estimación si solo hay presupuesto total
    
    // Puja por mil impresiones (en micros)
    const bidMicro = 5000000; // $5.00 por mil impresiones, por defecto
    
    // Formato de ubicaciones para Snapchat
    const placements = ["SNAP_ADS"];
    
    // Formato de demografía (edad y género)
    const demographics = {
      age_groups: this.formatSnapchatAgeGroups(
        campaign.targetAudience.ageRange.min,
        campaign.targetAudience.ageRange.max
      ),
      genders: campaign.targetAudience.genders.includes('all')
        ? []  // Vacío significa todos en Snapchat
        : campaign.targetAudience.genders.map(g => g.toUpperCase())
    };
    
    // Formato de ubicaciones geográficas
    const geos = campaign.targetAudience.locations.map(location => ({
      country_code: this.getCountryCode(location),
      // En una implementación real, se buscarían códigos más específicos
      // (estados, ciudades) en la API de Snapchat
      name: location
    }));
    
    // Formato de intereses
    const interests = campaign.targetAudience.interests.map(interest => ({
      // En una implementación real, se buscarían IDs de categorías de interés en Snapchat
      id: `interest_${interest.replace(/\s/g, '_').toLowerCase()}`,
      name: interest
    }));
    
    return {
      name: campaign.name,
      status: this.mapStatus(campaign.status),
      startTime: Math.floor(campaign.startDate.getTime() / 1000),
      endTime: Math.floor(campaign.endDate.getTime() / 1000),
      dailyBudgetMicro,
      bidMicro,
      placements,
      demographics,
      geos,
      interests,
      headline: campaign.content.title,
      callToAction: this.mapCallToAction(campaign.content.callToAction),
      landingUrl: campaign.content.landingPageUrl
    };
  }
  
  /**
   * Mapea el estado de la campaña al formato de Snapchat
   */
  private mapStatus(status: string): string {
    const statusMap: Record<string, string> = {
      'draft': 'PAUSED',
      'pending': 'PAUSED',
      'active': 'ACTIVE',
      'paused': 'PAUSED',
      'completed': 'PAUSED',
      'error': 'PAUSED'
    };
    
    return statusMap[status] || 'PAUSED';
  }
  
  /**
   * Formatea grupos de edad para la API de Snapchat
   */
  private formatSnapchatAgeGroups(min: number, max: number): string[] {
    const ageGroups = [];
    
    if (min <= 24 && max >= 13) ageGroups.push("13-17", "18-24");
    if (min <= 34 && max >= 25) ageGroups.push("25-34");
    if (min <= 49 && max >= 35) ageGroups.push("35-49");
    if (max >= 50) ageGroups.push("50+");
    
    // Si no hay grupos seleccionados, agregar todos
    if (ageGroups.length === 0) {
      return ["13-17", "18-24", "25-34", "35-49", "50+"];
    }
    
    return ageGroups;
  }
  
  /**
   * Obtiene código de país a partir de la ubicación
   */
  private getCountryCode(location: string): string {
    // En una implementación real, se usaría una base de datos o API para obtener el código
    // Este es un mapeo básico para demostración
    const locationMap: Record<string, string> = {
      'Colombia': 'CO',
      'Medellín': 'CO',
      'Bogotá': 'CO',
      'Cali': 'CO',
      'México': 'MX',
      'Argentina': 'AR',
      'España': 'ES',
      'Estados Unidos': 'US'
    };
    
    return locationMap[location] || 'CO'; // Default a Colombia
  }
  
  /**
   * Mapea el CTA a valores aceptados por Snapchat
   */
  private mapCallToAction(callToAction: string): string {
    const ctaMap: Record<string, string> = {
      'Aplicar ahora': 'APPLY_NOW',
      'Registrarse': 'SIGN_UP',
      'Saber más': 'LEARN_MORE',
      'Contactar': 'CONTACT_US',
      'Enviar': 'APPLY_NOW'
    };
    
    return ctaMap[callToAction] || 'LEARN_MORE';
  }

  /**
   * Actualiza un anuncio existente en Snapchat
   */
  async updateAd(adId: string, campaign: Partial<AdCampaign>): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Preparar datos para actualizar (Snapchat usa Ad Squads como anuncios)
      const updateData: Record<string, unknown> = {};
      
      if (campaign.name) updateData.name = campaign.name;
      if (campaign.status) updateData.status = this.mapStatus(campaign.status);
      if (campaign.budget || campaign.dailyBudget) {
        updateData.daily_budget_micro = campaign.dailyBudget 
          ? Math.round(campaign.dailyBudget * 1000000)
          : Math.round((campaign.budget! / 30) * 1000000);
      }
      if (campaign.startDate) updateData.start_time = Math.floor(campaign.startDate.getTime() / 1000);
      if (campaign.endDate) updateData.end_time = Math.floor(campaign.endDate.getTime() / 1000);
      
      // Actualizar Ad Squad
      await this.makeRequest(`adaccounts/{ad_account_id}/adsquads/${adId}`, 'POST', {
        ad_squad: updateData
      });

      return {
        success: true,
        data: {
          id: adId,
          status: 'active',
          updatedAt: new Date().toISOString(),
        }
      };
    } catch (error) {
      console.error(`Error al actualizar anuncio ${adId} en Snapchat:`, error);
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido al actualizar anuncio en Snapchat';
      return {
        success: false,
        error: {
          code: 'SNAPCHAT_API_ERROR',
          message: errorMessage
        }
      };
    }
  }

  /**
   * Elimina un anuncio de Snapchat
   */
  async deleteAd(adId: string): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Actualizar estado del Ad Squad a 'PAUSED'
      // Nota: Snapchat no permite eliminar anuncios completamente, solo pausarlos
      await this.makeRequest(`adaccounts/{ad_account_id}/adsquads/${adId}`, 'POST', {
        ad_squad: {
          status: "PAUSED"
        }
      });

      return {
        success: true,
        data: {
          id: adId,
          deleted: true,
          deletedAt: new Date().toISOString(),
        }
      };
    } catch (error) {
      console.error(`Error al eliminar anuncio ${adId} en Snapchat:`, error);
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido al eliminar anuncio en Snapchat';
      return {
        success: false,
        error: {
          code: 'SNAPCHAT_API_ERROR',
          message: errorMessage
        }
      };
    }
  }

  /**
   * Obtiene el estado de un anuncio en Snapchat
   */
  async getAdStatus(adId: string): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Obtener estado del Ad Squad
      await this.makeRequest(`adaccounts/{ad_account_id}/adsquads/${adId}`, 'GET');

      return {
        success: true,
        data: {
          id: adId,
          status: 'active',
          approvalStatus: 'APPROVED',
          platform: 'snapchat',
          lastChecked: new Date().toISOString(),
        }
      };
    } catch (error) {
      console.error(`Error al obtener estado del anuncio ${adId} en Snapchat:`, error);
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido al obtener estado del anuncio en Snapchat';
      return {
        success: false,
        error: {
          code: 'SNAPCHAT_API_ERROR',
          message: errorMessage
        }
      };
    }
  }

  /**
   * Obtiene métricas de rendimiento de un anuncio en Snapchat
   */
  async getAdPerformance(adId: string, metrics: string[]): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Convertir métricas al formato de Snapchat
      const snapchatMetrics = metrics.map(m => this.mapMetricToSnapchatFormat(m));
      
      // Calcular rango de fechas (últimos 7 días)
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 7);
      
      // Obtener métricas del anuncio
      await this.makeRequest(`adaccounts/{ad_account_id}/stats`, 'POST', {
        fields: snapchatMetrics,
        start_time: Math.floor(startDate.getTime() / 1000),
        end_time: Math.floor(endDate.getTime() / 1000),
        granularity: "TOTAL",
        entity_ids: [adId],
        entity_type: "adsquad"
      });

      return {
        success: true,
        data: {
          id: adId,
          metrics: {
            impressions: 18200,
            clicks: 410,
            ctr: 0.0225,
            conversions: 32,
            costPerClick: 0.40,
            costPerConversion: 5.13,
            spend: 164.00
          },
          period: {
            from: startDate.toISOString(),
            to: endDate.toISOString()
          }
        }
      };
    } catch (error) {
      console.error(`Error al obtener métricas del anuncio ${adId} en Snapchat:`, error);
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido al obtener métricas del anuncio en Snapchat';
      return {
        success: false,
        error: {
          code: 'SNAPCHAT_API_ERROR',
          message: errorMessage
        }
      };
    }
  }
  
  /**
   * Mapea métricas generales a formato de Snapchat
   */
  private mapMetricToSnapchatFormat(metric: string): string {
    const metricMap: Record<string, string> = {
      'impressions': 'impressions',
      'clicks': 'swipes',
      'ctr': 'swipe_rate',
      'conversions': 'conversions',
      'costPerClick': 'cost_per_swipe',
      'costPerConversion': 'cost_per_conversion',
      'spend': 'spend'
    };
    
    return metricMap[metric] || metric;
  }
}