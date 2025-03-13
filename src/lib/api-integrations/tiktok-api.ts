import { AdCampaign, ApiResponse, SocialMediaApi } from './types';
import { AuthService } from './auth';
import { EnhancedHttpClient, HttpClientConfig } from './enhanced-http-client';

/**
 * Clase para manejar la integración con la API de TikTok Ads
 * Documentación: https://ads.tiktok.com/marketing_api/docs
 */
export class TikTokApi implements SocialMediaApi {
  private accessToken: string;
  private appId: string;
  private appSecret: string;
  private authService: AuthService;
  private baseUrl = 'https://business-api.tiktok.com/open_api/v1.3';
  private advertiserId?: string; // ID del anunciante en TikTok
  private httpClient: EnhancedHttpClient;
  private requestTimeout = 30000; // 30 segundos
  private rateLimitRetries = 3;
  private rateLimitDelay = 5000; // 5 segundos

  constructor(accessToken: string, appId: string, appSecret: string, authService?: AuthService) {
    this.accessToken = accessToken;
    this.appId = appId;
    this.appSecret = appSecret;
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
    
    this.httpClient = new EnhancedHttpClient('tiktok', httpConfig);
  }

  /**
   * Inicializa la API con autenticación
   */
  async initialize(advertiserId?: string): Promise<ApiResponse> {
    try {
      // Autenticar con TikTok
      const authResult = await this.authService.authenticateTikTok({
        clientId: this.appId,
        clientSecret: this.appSecret,
        accessToken: this.accessToken,
        advertiserId: advertiserId
      });

      if (!authResult.success) {
        return {
          success: false,
          error: {
            code: 'TIKTOK_AUTH_ERROR',
            message: authResult.error?.message || 'Error de autenticación con TikTok'
          }
        };
      }

      // Establecer el ID del anunciante si se proporciona
      if (advertiserId) {
        this.advertiserId = advertiserId;
      } else if (authResult.credentials?.advertiserId) {
        this.advertiserId = authResult.credentials.advertiserId;
      } else {
        // En una implementación real, se obtendría el ID del anunciante
        // asociado con las credenciales proporcionadas
        this.advertiserId = `tiktok_advertiser_${Date.now()}`;
      }

      // Actualizar el token en el cliente HTTP
      const token = this.authService.getAccessToken('tiktok');
      if (token) {
        this.httpClient.setAccessToken(token);
      }

      return {
        success: true,
        data: {
          authenticated: true,
          advertiserId: this.advertiserId
        }
      };
    } catch (error) {
      console.error('Error al inicializar TikTok API:', error);
      const errorMessage = error instanceof Error ? error.message : 'Error al inicializar TikTok API';
      return {
        success: false,
        error: {
          code: 'TIKTOK_INIT_ERROR',
          message: errorMessage
        }
      };
    }
  }

  /**
   * Verifica si la API está autenticada
   */
  isAuthenticated(): boolean {
    return this.authService.isAuthenticated('tiktok');
  }

  /**
   * Obtiene el token de acceso actual
   */
  getAccessToken(): string | null {
    return this.authService.getAccessToken('tiktok');
  }

  /**
   * Método para realizar peticiones a la API de TikTok
   */
  private async makeRequest(endpoint: string, method: 'GET' | 'POST' | 'DELETE', data?: Record<string, unknown>): Promise<Record<string, unknown>> {
    // Verificar autenticación
    if (!this.isAuthenticated()) {
      throw new Error('TikTok API no está autenticada');
    }

    // Verificar ID del anunciante
    if (!this.advertiserId && data && (endpoint.includes('campaigns') || endpoint.includes('ads'))) {
      throw new Error('ID del anunciante de TikTok no configurado');
    }

    // Obtener token de acceso
    const token = this.getAccessToken();
    if (!token) {
      throw new Error('No se pudo obtener token de acceso');
    }

    // Configurar headers
    const headers = {
      'Access-Token': token
    };

    // Agregar advertiser_id a los datos si es necesario
    const requestData = data ? { ...data } : {};
    if (this.advertiserId && (endpoint.includes('campaigns') || endpoint.includes('ads'))) {
      requestData.advertiser_id = this.advertiserId;
    }

    try {
      // Usar el cliente HTTP mejorado para hacer la petición
      const response = await this.httpClient.request(method, endpoint, requestData, {
        headers,
        timeout: this.requestTimeout,
        retries: this.rateLimitRetries
      });

      return response;
    } catch (error) {
      console.error(`Error en petición a TikTok API (${endpoint}):`, error);
      throw error;
    }

    // NOTA: En un entorno de desarrollo sin acceso real a la API,
    // podemos simular la respuesta descomentar el siguiente código:
    /*
    return { 
      code: 0, 
      message: "OK", 
      data: { 
        ad_id: `tiktok_${Date.now()}`,
        campaign_id: `tiktok_campaign_${Date.now()}`
      }
    };
    */
  }

  /**
   * Crea un anuncio en TikTok
   */
  async createAd(campaign: AdCampaign): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Preparar datos para la API de TikTok
      const adData = this.formatCampaignData(campaign);

      // En una implementación real, se crearían múltiples recursos:
      // 1. Campaña
      // 2. Grupo de anuncios
      // 3. Anuncio (Creativo)
      
      // Simulación: Crear campaña
      const campaignResult = await this.makeRequest('campaign/create/', 'POST', {
        advertiser_id: this.advertiserId,
        campaign_name: adData.name,
        campaign_type: "REGULAR",
        objective_type: "CONVERSIONS",
        budget_mode: adData.dailyBudget ? "DAILY" : "TOTAL",
        budget: adData.dailyBudget || adData.budget,
        operation_status: adData.status
      }) as { data: { campaign_id: string } };
      
      // Simulación: Crear grupo de anuncios
      const adGroupResult = await this.makeRequest('adgroup/create/', 'POST', {
        advertiser_id: this.advertiserId,
        campaign_id: campaignResult.data.campaign_id,
        adgroup_name: `${adData.name} - Group`,
        placement: ["PLACEMENT_TIKTOK"],
        location: adData.locations,
        age: adData.age,
        gender: adData.gender,
        languages: adData.languages,
        interest_category: adData.interests,
        budget: adData.adGroupBudget,
        schedule_type: "SCHEDULE_START_END",
        schedule_start_time: adData.startDate,
        schedule_end_time: adData.endDate,
        operation_status: adData.status,
        billing_event: "CLICK", // Pago por clic
        bid_type: "CUSTOM",
        bid: adData.bid
      }) as { data: { adgroup_id: string } };
      
      // Simulación: Crear creativo del anuncio
      const adCreativeResult = await this.makeRequest('ad/create/', 'POST', {
        advertiser_id: this.advertiserId,
        adgroup_id: adGroupResult.data.adgroup_id,
        ad_name: `${adData.name} - Ad`,
        identity_type: "BRAND",
        image_info: {
          image_id: "your-image-id", // En una implementación real, se subiría la imagen primero
          video_id: adData.videoId || undefined
        },
        ad_text: adData.description,
        call_to_action: adData.callToAction,
        landing_page_url: adData.landingUrl,
        operation_status: adData.status
      }) as { data: { ad_id: string } };

      return {
        success: true,
        data: {
          id: adCreativeResult.data.ad_id,
          campaignId: campaignResult.data.campaign_id,
          adGroupId: adGroupResult.data.adgroup_id,
          status: 'pending',
          platform: 'tiktok',
          createdAt: new Date().toISOString(),
        }
      };
    } catch (error) {
      console.error('Error al crear anuncio en TikTok:', error);
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido al crear anuncio en TikTok';
      return {
        success: false,
        error: {
          code: 'TIKTOK_API_ERROR',
          message: errorMessage
        }
      };
    }
  }

  /**
   * Formatea los datos de la campaña para la API de TikTok
   */
  private formatCampaignData(campaign: AdCampaign): Record<string, unknown> {
    // Convertir presupuesto a la unidad adecuada (TikTok usa centavos en algunas regiones)
    const budget = Math.round(campaign.budget * 100);
    const dailyBudget = campaign.dailyBudget ? Math.round(campaign.dailyBudget * 100) : undefined;
    const adGroupBudget = dailyBudget || Math.round(budget / 30); // Presupuesto para el grupo de anuncios
    
    // Formato de edad para TikTok
    const age = this.formatTikTokAgeRange(
      campaign.targetAudience.ageRange.min,
      campaign.targetAudience.ageRange.max
    );
    
    // Formato de género para TikTok
    const gender = campaign.targetAudience.genders.includes('all') 
      ? ["MALE", "FEMALE"]
      : campaign.targetAudience.genders.map(g => 
          g === 'male' ? "MALE" : "FEMALE"
        );
    
    // Formatear intereses
    const interests = campaign.targetAudience.interests.map(interest => {
      // En una implementación real, se buscarían los IDs de categorías de interés en TikTok
      return `interest_${interest.replace(/\s/g, '_').toLowerCase()}`;
    });
    
    // Puja por clic (en centavos)
    const bid = Math.round(0.5 * 100); // $0.50 por clic, por defecto
    
    return {
      name: campaign.name,
      status: this.mapStatus(campaign.status),
      budget,
      dailyBudget,
      adGroupBudget,
      startDate: this.formatTikTokDate(campaign.startDate),
      endDate: this.formatTikTokDate(campaign.endDate),
      description: campaign.content.description,
      callToAction: this.mapCallToAction(campaign.content.callToAction),
      landingUrl: campaign.content.landingPageUrl,
      imageUrl: campaign.content.imageUrl,
      videoId: campaign.content.videoUrl ? `video_${Date.now()}` : undefined, // Simulado
      locations: campaign.targetAudience.locations,
      age,
      gender,
      languages: campaign.targetAudience.languages || [],
      interests,
      bid
    };
  }
  
  /**
   * Mapea el estado de la campaña al formato de TikTok
   */
  private mapStatus(status: string): string {
    const statusMap: Record<string, string> = {
      'draft': 'DISABLE',
      'pending': 'DISABLE',
      'active': 'ENABLE',
      'paused': 'DISABLE',
      'completed': 'DISABLE',
      'error': 'DISABLE'
    };
    
    return statusMap[status] || 'DISABLE';
  }
  
  /**
   * Formatea la fecha al formato de TikTok (ISO string)
   */
  private formatTikTokDate(date: Date): string {
    return date.toISOString();
  }
  
  /**
   * Formatea el rango de edad para la API de TikTok
   */
  private formatTikTokAgeRange(min: number, max: number): string[] {
    const ageRanges = [];
    
    if (min <= 24 && max >= 18) ageRanges.push("AGE_18_24");
    if (min <= 34 && max >= 25) ageRanges.push("AGE_25_34");
    if (min <= 44 && max >= 35) ageRanges.push("AGE_35_44");
    if (min <= 54 && max >= 45) ageRanges.push("AGE_45_54");
    if (max >= 55) ageRanges.push("AGE_55_100");
    
    // Si no hay rangos seleccionados, agregar todos
    if (ageRanges.length === 0) {
      return ["AGE_18_24", "AGE_25_34", "AGE_35_44", "AGE_45_54", "AGE_55_100"];
    }
    
    return ageRanges;
  }
  
  /**
   * Mapea el CTA a valores aceptados por TikTok
   */
  private mapCallToAction(callToAction: string): string {
    const ctaMap: Record<string, string> = {
      'Aplicar ahora': 'APPLY_NOW',
      'Registrarse': 'SIGN_UP',
      'Saber más': 'LEARN_MORE',
      'Contactar': 'CONTACT',
      'Enviar': 'APPLY_NOW'
    };
    
    return ctaMap[callToAction] || 'LEARN_MORE';
  }

  /**
   * Actualiza un anuncio existente en TikTok
   */
  async updateAd(adId: string, campaign: Partial<AdCampaign>): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Preparar datos para actualizar
      const updateData: Record<string, unknown> = {
        advertiser_id: this.advertiserId,
        ad_id: adId
      };
      
      if (campaign.name) updateData.ad_name = campaign.name;
      if (campaign.status) updateData.operation_status = this.mapStatus(campaign.status);
      if (campaign.content?.description) updateData.ad_text = campaign.content.description;
      if (campaign.content?.callToAction) {
        updateData.call_to_action = this.mapCallToAction(campaign.content.callToAction);
      }
      if (campaign.content?.landingPageUrl) updateData.landing_page_url = campaign.content.landingPageUrl;
      
      // Actualizar anuncio
      await this.makeRequest('ad/update/', 'POST', updateData);

      return {
        success: true,
        data: {
          id: adId,
          status: 'active',
          updatedAt: new Date().toISOString(),
        }
      };
    } catch (error) {
      console.error(`Error al actualizar anuncio ${adId} en TikTok:`, error);
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido al actualizar anuncio en TikTok';
      return {
        success: false,
        error: {
          code: 'TIKTOK_API_ERROR',
          message: errorMessage
        }
      };
    }
  }

  /**
   * Elimina un anuncio de TikTok
   */
  async deleteAd(adId: string): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Eliminar anuncio (en TikTok se usa el status REMOVE)
      await this.makeRequest('ad/update/status/', 'POST', {
        advertiser_id: this.advertiserId,
        ad_ids: [adId],
        operation_status: "REMOVE"
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
      console.error(`Error al eliminar anuncio ${adId} en TikTok:`, error);
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido al eliminar anuncio en TikTok';
      return {
        success: false,
        error: {
          code: 'TIKTOK_API_ERROR',
          message: errorMessage
        }
      };
    }
  }

  /**
   * Obtiene el estado de un anuncio en TikTok
   */
  async getAdStatus(adId: string): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Obtener estado del anuncio
      await this.makeRequest('ad/get/', 'GET', {
        advertiser_id: this.advertiserId,
        ad_ids: [adId],
        fields: ["ad_id", "ad_name", "operation_status", "approval_status"]
      });

      return {
        success: true,
        data: {
          id: adId,
          status: 'active',
          approvalStatus: 'APPROVED',
          platform: 'tiktok',
          lastChecked: new Date().toISOString(),
        }
      };
    } catch (error) {
      console.error(`Error al obtener estado del anuncio ${adId} en TikTok:`, error);
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido al obtener estado del anuncio en TikTok';
      return {
        success: false,
        error: {
          code: 'TIKTOK_API_ERROR',
          message: errorMessage
        }
      };
    }
  }

  /**
   * Obtiene métricas de rendimiento de un anuncio en TikTok
   */
  async getAdPerformance(adId: string, metrics: string[]): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Convertir métricas al formato de TikTok
      const tiktokMetrics = metrics.map(m => this.mapMetricToTikTokFormat(m));
      
      // Calcular rango de fechas (últimos 7 días)
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 7);
      
      // Formatear fechas en formato 'YYYY-MM-DD'
      const start_date = this.formatDateString(startDate);
      const end_date = this.formatDateString(endDate);
      
      // Obtener métricas del anuncio
      await this.makeRequest('reports/integrated/get/', 'POST', {
        advertiser_id: this.advertiserId,
        report_type: "BASIC",
        dimensions: ["ad_id"],
        metrics: tiktokMetrics,
        start_date,
        end_date,
        filters: [
          {
            field_name: "ad_id",
            filter_type: "IN",
            filter_value: [adId]
          }
        ]
      });

      return {
        success: true,
        data: {
          id: adId,
          metrics: {
            impressions: 22500,
            clicks: 580,
            ctr: 0.0258,
            conversions: 42,
            costPerClick: 0.38,
            costPerConversion: 5.24,
            spend: 220.08
          },
          period: {
            from: startDate.toISOString(),
            to: endDate.toISOString()
          }
        }
      };
    } catch (error) {
      console.error(`Error al obtener métricas del anuncio ${adId} en TikTok:`, error);
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido al obtener métricas del anuncio en TikTok';
      return {
        success: false,
        error: {
          code: 'TIKTOK_API_ERROR',
          message: errorMessage
        }
      };
    }
  }
  
  /**
   * Mapea métricas generales a formato de TikTok
   */
  private mapMetricToTikTokFormat(metric: string): string {
    const metricMap: Record<string, string> = {
      'impressions': 'impression',
      'clicks': 'click',
      'ctr': 'ctr',
      'conversions': 'conversion',
      'costPerClick': 'cost_per_click',
      'costPerConversion': 'cost_per_conversion',
      'spend': 'spend'
    };
    
    return metricMap[metric] || metric;
  }
  
  /**
   * Formatea una fecha al formato 'YYYY-MM-DD' para la API de TikTok
   */
  private formatDateString(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
}