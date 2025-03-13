import { AdCampaign, ApiResponse, SocialMediaApi } from './types';
import { AuthService } from './auth';

/**
 * Clase para manejar la integración con la API de X (Twitter)
 * Documentación: https://developer.twitter.com/en/docs/twitter-ads-api
 */
export class XApi implements SocialMediaApi {
  private apiKey: string;
  private apiSecret: string;
  private accessToken: string;
  private accessTokenSecret?: string;
  private authService: AuthService;
  private baseUrl = 'https://ads-api.twitter.com/12';
  private accountId?: string; // ID de la cuenta de anuncios de X

  constructor(apiKey: string, apiSecret: string, accessToken: string, accessTokenSecret?: string, authService?: AuthService) {
    this.apiKey = apiKey;
    this.apiSecret = apiSecret;
    this.accessToken = accessToken;
    this.accessTokenSecret = accessTokenSecret;
    this.authService = authService || new AuthService();
  }

  /**
   * Inicializa la API con autenticación
   */
  async initialize(accountId?: string): Promise<ApiResponse> {
    try {
      // Autenticar con X (Twitter)
      const authResult = await this.authService.authenticateX({
        clientId: this.apiKey,
        clientSecret: this.apiSecret,
        accessToken: this.accessToken,
        accessTokenSecret: this.accessTokenSecret || ''
      });

      if (!authResult.success) {
        return {
          success: false,
          error: {
            code: 'X_AUTH_ERROR',
            message: authResult.error?.message || 'Error de autenticación con X'
          }
        };
      }

      // Establecer el ID de cuenta si se proporciona
      if (accountId) {
        this.accountId = accountId;
      } else {
        // En una implementación real, se obtendría el ID de la cuenta
        // de anuncios asociada con las credenciales proporcionadas
        this.accountId = `x_account_${Date.now()}`;
      }

      return {
        success: true,
        data: {
          authenticated: true,
          accountId: this.accountId
        }
      };
    } catch (error: any) {
      console.error('Error al inicializar X API:', error);
      return {
        success: false,
        error: {
          code: 'X_INIT_ERROR',
          message: error.message || 'Error al inicializar X API'
        }
      };
    }
  }

  /**
   * Verifica si la API está autenticada
   */
  isAuthenticated(): boolean {
    return this.authService.isAuthenticated('x');
  }

  /**
   * Obtiene el token de acceso actual
   */
  getAccessToken(): string | null {
    return this.authService.getAccessToken('x');
  }

  /**
   * Método para realizar peticiones a la API de X (Twitter)
   */
  private async makeRequest(endpoint: string, method: 'GET' | 'POST' | 'DELETE', data?: any): Promise<any> {
    // Verificar autenticación
    if (!this.isAuthenticated()) {
      throw new Error('X API no está autenticada');
    }

    // Verificar ID de cuenta
    if (!this.accountId && endpoint.includes('{account_id}')) {
      throw new Error('ID de cuenta de X no configurado');
    }

    // Reemplazar placeholder en la URL si existe
    const url = `${this.baseUrl}/${endpoint.replace('{account_id}', this.accountId || '')}`;

    // En una implementación real, se haría la petición HTTP utilizando
    // los encabezados y datos adecuados para la API de Twitter Ads
    // Ejemplo:
    /*
    // X requiere autenticación OAuth 1.0a, que es más compleja que OAuth 2.0
    // Normalmente se usaría una biblioteca como 'oauth-1.0a' para generar
    // los encabezados de autorización
    
    const oauth = OAuth({
      consumer: { key: this.apiKey, secret: this.apiSecret },
      signature_method: 'HMAC-SHA1',
      hash_function(base_string, key) {
        return crypto
          .createHmac('sha1', key)
          .update(base_string)
          .digest('base64');
      },
    });
    
    const token = {
      key: this.accessToken,
      secret: this.accessTokenSecret || '',
    };
    
    const requestData = {
      url,
      method,
    };
    
    const headers = oauth.toHeader(oauth.authorize(requestData, token));
    headers['Content-Type'] = 'application/json';
    
    const response = await fetch(url, {
      method,
      headers,
      body: data ? JSON.stringify(data) : undefined,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`Error en la petición a X API: ${errorData.errors[0].message}`);
    }
    
    return await response.json();
    */

    // Simulación de respuesta
    return { success: true, id: `x_${Date.now()}` };
  }

  /**
   * Crea un anuncio en X (Twitter)
   */
  async createAd(campaign: AdCampaign): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Preparar datos para la API de X
      const adData = this.formatCampaignData(campaign);

      // En una implementación real, se crearían múltiples recursos:
      // 1. Campaña (Campaign)
      // 2. Línea de promoción (Line Item)
      // 3. Tweet promovido (Promoted Tweet)
      // 4. Segmentación (Targeting)
      
      // Simulación: Crear campaña
      const campaignResult = await this.makeRequest(`accounts/{account_id}/campaigns`, 'POST', {
        name: adData.name,
        funding_instrument_id: "xyz123", // En la implementación real, se obtendría de la cuenta
        start_time: adData.startTime,
        end_time: adData.endTime,
        daily_budget_amount_local_micro: adData.dailyBudgetAmountMicro,
        entity_status: adData.status
      });
      
      // Simulación: Crear línea de promoción
      const lineItemResult = await this.makeRequest(`accounts/{account_id}/line_items`, 'POST', {
        campaign_id: campaignResult.data.id,
        name: `${adData.name} - Line`,
        product_type: "PROMOTED_TWEETS",
        placements: ["ALL_ON_X"],
        objective: "JOBS",
        bid_amount_local_micro: adData.bidAmountMicro,
        entity_status: adData.status
      });
      
      // Simulación: Crear tweet (la API real requiere un tweet existente o crear uno)
      const tweetId = `tweet_${Date.now()}`;
      
      // Simulación: Asociar tweet a la línea de promoción
      const promotedTweetResult = await this.makeRequest(`accounts/{account_id}/promoted_tweets`, 'POST', {
        line_item_id: lineItemResult.data.id,
        tweet_ids: [tweetId]
      });
      
      // Simulación: Crear segmentación para la línea de promoción
      const targetingResult = await this.makeRequest(`accounts/{account_id}/targeting_criteria`, 'POST', {
        line_item_id: lineItemResult.data.id,
        targeting_criteria: adData.targetingCriteria
      });

      return {
        success: true,
        data: {
          id: lineItemResult.id,
          campaignId: campaignResult.id,
          tweetId: tweetId,
          status: 'pending',
          platform: 'x',
          createdAt: new Date().toISOString(),
        }
      };
    } catch (error: any) {
      console.error('Error al crear anuncio en X:', error);
      return {
        success: false,
        error: {
          code: 'X_API_ERROR',
          message: error.message || 'Error desconocido al crear anuncio en X'
        }
      };
    }
  }

  /**
   * Formatea los datos de la campaña para la API de X
   */
  private formatCampaignData(campaign: AdCampaign): any {
    // Convertir presupuesto a micros (X también maneja importes en millonésimas)
    const dailyBudgetAmountMicro = campaign.dailyBudget
      ? Math.round(campaign.dailyBudget * 1000000)
      : Math.round((campaign.budget / 30) * 1000000); // Estimación si solo hay presupuesto total
    
    // Estimación de puja por clic (en micros)
    const bidAmountMicro = 500000; // $0.50 por clic, por defecto
    
    // Formatear criterios de segmentación
    const targetingCriteria = [];
    
    // Segmentación por ubicación
    if (campaign.targetAudience.locations.length > 0) {
      targetingCriteria.push({
        targeting_type: "LOCATION",
        targeting_value: campaign.targetAudience.locations.map(loc => ({
          name: loc,
          // En una implementación real, se buscarían los IDs de locación
          id: `loc_${loc.replace(/\s/g, '_').toLowerCase()}`
        }))
      });
    }
    
    // Segmentación por género
    if (!campaign.targetAudience.genders.includes('all')) {
      targetingCriteria.push({
        targeting_type: "GENDER",
        targeting_value: campaign.targetAudience.genders.map(g => 
          g === 'male' ? "1" : "2" // 1 = hombres, 2 = mujeres en la API de X
        )
      });
    }
    
    // Segmentación por edad
    targetingCriteria.push({
      targeting_type: "AGE",
      targeting_value: this.formatAgeRanges(
        campaign.targetAudience.ageRange.min,
        campaign.targetAudience.ageRange.max
      )
    });
    
    // Segmentación por intereses
    if (campaign.targetAudience.interests.length > 0) {
      targetingCriteria.push({
        targeting_type: "INTEREST",
        targeting_value: campaign.targetAudience.interests.map(interest => ({
          name: interest,
          // En una implementación real, se buscarían los IDs de interés
          id: `interest_${interest.replace(/\s/g, '_').toLowerCase()}`
        }))
      });
    }
    
    // Segmentación por palabras clave (basadas en intereses)
    if (campaign.targetAudience.interests.length > 0) {
      targetingCriteria.push({
        targeting_type: "KEYWORD",
        targeting_value: campaign.targetAudience.interests
      });
    }
    
    return {
      name: campaign.name,
      status: this.mapStatus(campaign.status),
      startTime: campaign.startDate.toISOString(),
      endTime: campaign.endDate.toISOString(),
      dailyBudgetAmountMicro,
      bidAmountMicro,
      creativeText: campaign.content.description,
      callToAction: this.mapCallToAction(campaign.content.callToAction),
      imageUrl: campaign.content.imageUrl,
      landingUrl: campaign.content.landingPageUrl,
      targetingCriteria
    };
  }
  
  /**
   * Mapea el estado de la campaña al formato de X
   */
  private mapStatus(status: string): string {
    const statusMap: Record<string, string> = {
      'draft': 'DRAFT',
      'pending': 'PAUSED',
      'active': 'ACTIVE',
      'paused': 'PAUSED',
      'completed': 'ARCHIVED',
      'error': 'PAUSED'
    };
    
    return statusMap[status] || 'PAUSED';
  }
  
  /**
   * Formatea los rangos de edad para la API de X
   */
  private formatAgeRanges(min: number, max: number): string[] {
    const ageRanges = [];
    
    if (min <= 24 && max >= 13) ageRanges.push("AGE_13_TO_24");
    if (min <= 34 && max >= 25) ageRanges.push("AGE_25_TO_34");
    if (min <= 49 && max >= 35) ageRanges.push("AGE_35_TO_49");
    if (min <= 64 && max >= 50) ageRanges.push("AGE_50_TO_64");
    if (max >= 65) ageRanges.push("AGE_OVER_65");
    
    // Si no hay rangos seleccionados, agregar todos
    if (ageRanges.length === 0) {
      return ["AGE_13_TO_24", "AGE_25_TO_34", "AGE_35_TO_49", "AGE_50_TO_64", "AGE_OVER_65"];
    }
    
    return ageRanges;
  }
  
  /**
   * Mapea el CTA a valores aceptados por X
   */
  private mapCallToAction(callToAction: string): string {
    const ctaMap: Record<string, string> = {
      'Aplicar ahora': 'APPLY_NOW',
      'Registrarse': 'SIGN_UP',
      'Saber más': 'LEARN_MORE',
      'Contactar': 'CONTACT_US',
      'Enviar': 'APPLY'
    };
    
    return ctaMap[callToAction] || 'LEARN_MORE';
  }

  /**
   * Actualiza un anuncio existente en X (Twitter)
   */
  async updateAd(adId: string, campaign: Partial<AdCampaign>): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Preparar datos para actualizar
      const updateData: any = {};
      
      if (campaign.name) updateData.name = campaign.name;
      if (campaign.status) updateData.entity_status = this.mapStatus(campaign.status);
      if (campaign.budget) {
        // Actualizar presupuesto diario
        updateData.daily_budget_amount_local_micro = Math.round((campaign.budget / 30) * 1000000);
      }
      if (campaign.dailyBudget) {
        updateData.daily_budget_amount_local_micro = Math.round(campaign.dailyBudget * 1000000);
      }
      if (campaign.startDate) updateData.start_time = campaign.startDate.toISOString();
      if (campaign.endDate) updateData.end_time = campaign.endDate.toISOString();
      
      // Simulación: Actualizar línea de promoción
      const result = await this.makeRequest(`accounts/{account_id}/line_items/${adId}`, 'POST', updateData);

      return {
        success: true,
        data: {
          id: adId,
          status: 'active',
          updatedAt: new Date().toISOString(),
        }
      };
    } catch (error: any) {
      console.error(`Error al actualizar anuncio ${adId} en X:`, error);
      return {
        success: false,
        error: {
          code: 'X_API_ERROR',
          message: error.message || 'Error desconocido al actualizar anuncio en X'
        }
      };
    }
  }

  /**
   * Elimina un anuncio de X (Twitter)
   */
  async deleteAd(adId: string): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Simulación: Cambiar estado a DELETED (en X, los recursos se marcan como DELETED)
      const result = await this.makeRequest(`accounts/{account_id}/line_items/${adId}`, 'POST', {
        entity_status: "DELETED"
      });

      return {
        success: true,
        data: {
          id: adId,
          deleted: true,
          deletedAt: new Date().toISOString(),
        }
      };
    } catch (error: any) {
      console.error(`Error al eliminar anuncio ${adId} en X:`, error);
      return {
        success: false,
        error: {
          code: 'X_API_ERROR',
          message: error.message || 'Error desconocido al eliminar anuncio en X'
        }
      };
    }
  }

  /**
   * Obtiene el estado de un anuncio en X (Twitter)
   */
  async getAdStatus(adId: string): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Simulación: Obtener estado del anuncio
      const result = await this.makeRequest(`accounts/{account_id}/line_items/${adId}`, 'GET');

      return {
        success: true,
        data: {
          id: adId,
          status: 'active',
          approvalStatus: 'APPROVED',
          platform: 'x',
          lastChecked: new Date().toISOString(),
        }
      };
    } catch (error: any) {
      console.error(`Error al obtener estado del anuncio ${adId} en X:`, error);
      return {
        success: false,
        error: {
          code: 'X_API_ERROR',
          message: error.message || 'Error desconocido al obtener estado del anuncio en X'
        }
      };
    }
  }

  /**
   * Obtiene métricas de rendimiento de un anuncio en X (Twitter)
   */
  async getAdPerformance(adId: string, metrics: string[]): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Convertir métricas al formato de X
      const xMetrics = metrics.map(m => this.mapMetricToXFormat(m)).join(',');
      
      // Calcular rango de fechas (últimos 7 días)
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 7);
      
      // Simulación: Obtener métricas del anuncio
      const result = await this.makeRequest(
        `accounts/{account_id}/stats?entity=LINE_ITEM&entity_ids=${adId}&metric_groups=${xMetrics}&start_time=${startDate.toISOString()}&end_time=${endDate.toISOString()}&granularity=TOTAL`,
        'GET'
      );

      return {
        success: true,
        data: {
          id: adId,
          metrics: {
            impressions: 8200,
            clicks: 245,
            ctr: 0.0299,
            conversions: 18,
            costPerClick: 0.38,
            costPerConversion: 5.18,
            spend: 93.10
          },
          period: {
            from: startDate.toISOString(),
            to: endDate.toISOString()
          }
        }
      };
    } catch (error: any) {
      console.error(`Error al obtener métricas del anuncio ${adId} en X:`, error);
      return {
        success: false,
        error: {
          code: 'X_API_ERROR',
          message: error.message || 'Error desconocido al obtener métricas del anuncio en X'
        }
      };
    }
  }
  
  /**
   * Mapea métricas generales a formato de X
   */
  private mapMetricToXFormat(metric: string): string {
    const metricMap: Record<string, string> = {
      'impressions': 'ENGAGEMENT',
      'clicks': 'ENGAGEMENT',
      'ctr': 'ENGAGEMENT',
      'conversions': 'CONVERSION',
      'costPerClick': 'BILLING',
      'costPerConversion': 'BILLING',
      'spend': 'BILLING'
    };
    
    return metricMap[metric] || 'ENGAGEMENT';
  }
}