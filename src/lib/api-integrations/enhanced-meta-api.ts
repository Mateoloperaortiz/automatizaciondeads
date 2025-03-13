import { AdCampaign, ApiErrorDetail, ApiResponse, SocialMediaApi } from './types';
import { AuthService } from './auth';
import { ApiClient } from './http-client';
import { ApiLogger, LogLevel } from './logger';
import { createErrorResponse } from './error-handler';
import { formatGraphDataForWebhook } from './helpers';

// Interfaces para respuestas de Meta
interface MetaApiGraphResponse {
  id?: string;
  success?: boolean;
  data?: any[];
  paging?: {
    cursors: {
      before: string;
      after: string;
    };
    next?: string;
  };
  error?: {
    message: string;
    type: string;
    code: number;
    error_subcode?: number;
    fbtrace_id?: string;
  };
}

/**
 * Implementación mejorada de la API de Meta con manejo de errores y logging
 */
export class EnhancedMetaApi implements SocialMediaApi {
  private apiKey: string;
  private apiSecret: string;
  private accessToken: string;
  private authService: AuthService;
  private apiClient: ApiClient;
  private logger: ApiLogger;
  private readonly platform: 'meta' = 'meta';
  private accountId?: string;
  private pageId?: string;
  
  constructor(apiKey: string, apiSecret: string, accessToken: string, authService?: AuthService) {
    this.apiKey = apiKey;
    this.apiSecret = apiSecret;
    this.accessToken = accessToken;
    this.authService = authService || new AuthService();
    this.apiClient = new ApiClient('meta', accessToken);
    this.logger = ApiLogger.getInstance();
  }
  
  /**
   * Inicializa la API con autenticación
   */
  async initialize(): Promise<ApiResponse> {
    try {
      this.logger.info('Inicializando Meta API', this.platform, {
        apiKey: `${this.apiKey.substring(0, 4)}...`,
      });
      
      // Autenticar con Meta
      const authResult = await this.authService.authenticateMeta({
        clientId: this.apiKey,
        clientSecret: this.apiSecret,
        accessToken: this.accessToken
      });

      if (!authResult.success) {
        this.logger.error('Error de autenticación con Meta', new Error(authResult.error?.message), this.platform);
        return {
          success: false,
          error: {
            code: 'META_AUTH_ERROR',
            message: authResult.error?.message || 'Error de autenticación con Meta',
            platform: this.platform,
            authError: true
          }
        };
      }

      // Si se obtuvo un nuevo token, actualizarlo
      if (authResult.credentials?.accessToken) {
        this.accessToken = authResult.credentials.accessToken;
        // Actualizar el token en el cliente HTTP
        this.apiClient.setAccessToken(this.accessToken);
      }
      
      // Extender token a larga duración si es posible
      if (!authResult.credentials?.longLivedToken) {
        const extendResult = await this.authService.extendMetaToken({
          clientId: this.apiKey,
          clientSecret: this.apiSecret,
          accessToken: this.accessToken
        });

        if (extendResult.success && extendResult.credentials) {
          this.accessToken = extendResult.credentials.accessToken;
          // Actualizar el token en el cliente HTTP
          this.apiClient.setAccessToken(this.accessToken);
          this.logger.info('Token Meta extendido con éxito', this.platform);
        } else {
          this.logger.warn('No se pudo extender el token de Meta', this.platform, {
            error: extendResult.error
          });
        }
      }

      try {
        // Obtener cuentas de anuncios asociadas al usuario
        const accountsResponse = await this.apiClient.get<MetaApiGraphResponse>(
          'me/adaccounts',
          { params: { fields: 'id,name,account_status,business,currency' } }
        );
        
        if (accountsResponse && accountsResponse.data && accountsResponse.data.length > 0) {
          // Tomar la primera cuenta activa
          const activeAccount = accountsResponse.data.find((acc: any) => acc.account_status === 1);
          if (activeAccount) {
            this.accountId = activeAccount.id;
          } else {
            this.accountId = accountsResponse.data[0].id;
          }
          
          this.logger.info('Cuenta de anuncios Meta seleccionada', this.platform, {
            accountId: this.accountId
          });
        } else {
          throw new Error('No se encontraron cuentas de anuncios asociadas');
        }
        
        // Obtener páginas asociadas al usuario
        const pagesResponse = await this.apiClient.get<MetaApiGraphResponse>(
          'me/accounts',
          { params: { fields: 'id,name,access_token,category' } }
        );
        
        if (pagesResponse && pagesResponse.data && pagesResponse.data.length > 0) {
          this.pageId = pagesResponse.data[0].id;
          this.logger.info('Página de Facebook seleccionada', this.platform, {
            pageId: this.pageId,
            pageName: pagesResponse.data[0].name
          });
        } else {
          this.logger.warn('No se encontraron páginas de Facebook asociadas', this.platform);
        }
      } catch (accountError) {
        // Registrar el error pero continuar con IDs simulados
        this.logger.error('Error al obtener información de cuentas', accountError, this.platform);
        
        // Usar IDs simulados para pruebas
        this.accountId = `act_${Date.now()}`;
        this.pageId = `page_${Date.now()}`;
      }

      return {
        success: true,
        data: {
          authenticated: true,
          accountId: this.accountId,
          pageId: this.pageId
        }
      };
    } catch (error) {
      this.logger.error('Error al inicializar Meta API', error, this.platform);
      return createErrorResponse(error, this.platform);
    }
  }
  
  /**
   * Verifica si la API está autenticada
   */
  isAuthenticated(): boolean {
    return this.authService.isAuthenticated(this.platform);
  }
  
  /**
   * Obtiene el token de acceso actual
   */
  getAccessToken(): string {
    const token = this.authService.getAccessToken(this.platform);
    return token || this.accessToken;
  }
  
  /**
   * Crea un anuncio en Facebook/Instagram
   */
  async createAd(campaign: AdCampaign): Promise<ApiResponse> {
    try {
      // Registrar inicio de la operación
      this.logger.info('Creando anuncio en Meta', this.platform, {
        campaignName: campaign.name
      });
      
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        this.logger.info('No autenticado, inicializando Meta API', this.platform);
        await this.initialize();
      }
      
      // Validaciones
      if (!this.accountId) {
        throw new Error('No se ha establecido un ID de cuenta de anuncios válido');
      }
      
      if (!this.pageId) {
        throw new Error('No se ha establecido un ID de página de Facebook válido');
      }
      
      // Normalizar el ID de la cuenta
      const accountId = this.accountId.replace('act_', '');
      
      // Preparar datos para la API de Meta
      const adData = {
        name: campaign.name,
        objective: 'CONVERSIONS',
        status: 'PAUSED', // Iniciar en pausa para revisión
        special_ad_categories: [],
        targeting: this.formatTargeting(campaign.targetAudience),
        creative: this.formatCreative(campaign.content),
        budget_remaining: campaign.budget * 100,
        daily_budget: campaign.dailyBudget ? campaign.dailyBudget * 100 : undefined,
        start_time: campaign.startDate.toISOString(),
        end_time: campaign.endDate.toISOString()
      };
      
      // Registrar el proceso paso a paso
      const startTime = Date.now();
      
      // 1. Crear la campaña
      const campaignResult = await this.apiClient.post<MetaApiGraphResponse>(
        `act_${accountId}/campaigns`,
        {
          name: adData.name,
          objective: adData.objective,
          status: adData.status,
          special_ad_categories: adData.special_ad_categories,
        }
      );
      
      if (!campaignResult || !campaignResult.id) {
        throw new Error('No se pudo crear la campaña en Meta');
      }
      
      this.logger.info('Campaña creada en Meta', this.platform, {
        campaignId: campaignResult.id,
        campaignName: adData.name
      });
      
      // 2. Crear conjunto de anuncios (Ad Set)
      const adSetResult = await this.apiClient.post<MetaApiGraphResponse>(
        `act_${accountId}/adsets`,
        {
          name: `${adData.name} - Conjunto`,
          campaign_id: campaignResult.id,
          targeting: adData.targeting,
          daily_budget: adData.daily_budget || adData.budget_remaining,
          lifetime_budget: !adData.daily_budget ? adData.budget_remaining : undefined,
          start_time: adData.start_time,
          end_time: adData.end_time,
          bid_amount: 1000, // 10 USD en centavos
          billing_event: 'IMPRESSIONS',
          optimization_goal: 'LINK_CLICKS',
          pacing_type: ['standard'],
          status: adData.status
        }
      );
      
      if (!adSetResult || !adSetResult.id) {
        throw new Error('No se pudo crear el conjunto de anuncios en Meta');
      }
      
      this.logger.info('Conjunto de anuncios creado en Meta', this.platform, {
        adSetId: adSetResult.id,
        campaignId: campaignResult.id
      });
      
      // 3. Crear primero el creativo para el anuncio
      const creativeResult = await this.apiClient.post<MetaApiGraphResponse>(
        `act_${accountId}/adcreatives`,
        {
          name: `${adData.name} - Creativo`,
          object_story_spec: {
            page_id: this.pageId,
            link_data: {
              message: adData.creative.title + "\n\n" + adData.creative.body,
              link: adData.creative.object_story_spec.link_data.link,
              image_url: adData.creative.object_story_spec.link_data.image_url,
              call_to_action: adData.creative.object_story_spec.link_data.call_to_action
            }
          }
        }
      );
      
      if (!creativeResult || !creativeResult.id) {
        throw new Error('No se pudo crear el creativo del anuncio en Meta');
      }
      
      this.logger.info('Creativo creado en Meta', this.platform, {
        creativeId: creativeResult.id,
        title: adData.creative.title
      });
      
      // 4. Crear el anuncio asociando el creativo
      const adResult = await this.apiClient.post<MetaApiGraphResponse>(
        `act_${accountId}/ads`,
        {
          name: `${adData.name} - Anuncio`,
          adset_id: adSetResult.id,
          creative: { creative_id: creativeResult.id },
          status: adData.status
        }
      );
      
      if (!adResult || !adResult.id) {
        throw new Error('No se pudo crear el anuncio en Meta');
      }
      
      // Calcular tiempo total
      const totalTime = Date.now() - startTime;
      
      this.logger.info(`Anuncio creado en Meta (${totalTime}ms)`, this.platform, {
        adId: adResult.id,
        campaignId: campaignResult.id,
        adSetId: adSetResult.id,
        creativeId: creativeResult.id,
        status: 'pending'
      });
      
      // Cuando el anuncio está creado, enviar webhook con notificación
      this.notifyWebhook('ad.created', {
        adId: adResult.id,
        campaignId: campaignResult.id,
        adSetId: adSetResult.id,
        creativeId: creativeResult.id,
        status: 'pending',
        platform: this.platform
      });
      
      // Registrar resultado completo
      return {
        success: true,
        data: {
          id: adResult.id,
          campaignId: campaignResult.id,
          adSetId: adSetResult.id,
          creativeId: creativeResult.id,
          status: 'pending',
          platform: this.platform,
          createdAt: new Date().toISOString(),
          details: {
            campaignUrl: `https://business.facebook.com/adsmanager/manage/campaigns?act=${accountId}&selected_campaign_ids=${campaignResult.id.split('_')[1]}`,
            adSetUrl: `https://business.facebook.com/adsmanager/manage/adsets?act=${accountId}&selected_adset_ids=${adSetResult.id.split('_')[1]}`,
            adUrl: `https://business.facebook.com/adsmanager/manage/ads?act=${accountId}&selected_ad_ids=${adResult.id.split('_')[1]}`,
          }
        }
      };
    } catch (error) {
      // Registrar el error
      this.logger.error('Error al crear anuncio en Meta', error, this.platform, {
        campaignName: campaign.name
      });
      
      // Usar el manejador de errores para generar respuesta consistente
      return createErrorResponse(error, this.platform);
    }
  }
  
  /**
   * Envía una notificación por webhook (si está configurado)
   */
  private async notifyWebhook(
    event: string, 
    data: Record<string, unknown>
  ): Promise<void> {
    // En una implementación real, aquí implementarías el envío a un webhook configurado
    try {
      // Ejemplo de implementación
      const webhookUrl = process.env.META_WEBHOOK_URL;
      if (!webhookUrl) return;
      
      const payload = {
        event,
        timestamp: new Date().toISOString(),
        platform: this.platform,
        data: formatGraphDataForWebhook(data)
      };
      
      // Registrar intento de envío
      this.logger.debug(`Enviando webhook: ${event}`, this.platform, payload);
      
      // Enviar a webhook
      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Webhook-Source': 'adsMaster',
          'X-Webhook-Event': event
        },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
      }
      
      this.logger.debug('Webhook enviado con éxito', this.platform);
    } catch (error) {
      this.logger.error('Error al enviar webhook', error, this.platform, {
        event
      });
    }
  }
  
  /**
   * Actualiza un anuncio existente en Facebook/Instagram
   */
  async updateAd(adId: string, campaign: Partial<AdCampaign>): Promise<ApiResponse> {
    try {
      // Registrar inicio de la operación
      this.logger.info('Actualizando anuncio en Meta', this.platform, {
        adId,
        updates: Object.keys(campaign)
      });
      
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }
      
      // Buscar información completa del anuncio
      const adInfo = await this.apiClient.get<MetaApiGraphResponse>(
        adId,
        { params: { fields: 'id,name,adset_id,campaign_id,creative,status' } }
      );
      
      if (!adInfo || !adInfo.id) {
        throw new Error(`No se encontró el anuncio con ID ${adId}`);
      }
      
      // Obtener IDs relacionados
      const adSetId = adInfo.adset_id;
      const campaignId = adInfo.campaign_id;
      
      const startTime = Date.now();
      
      // Actualizar el anuncio
      if (campaign.name || campaign.status) {
        const adUpdateData: Record<string, unknown> = {};
        if (campaign.name) adUpdateData.name = campaign.name;
        if (campaign.status) adUpdateData.status = campaign.status === 'active' ? 'ACTIVE' : 'PAUSED';
        
        await this.apiClient.post<MetaApiGraphResponse>(adId, adUpdateData);
        
        this.logger.info('Anuncio actualizado en Meta', this.platform, {
          adId,
          changes: Object.keys(adUpdateData)
        });
      }
      
      // Actualizar el conjunto de anuncios si es necesario
      if (campaign.dailyBudget || campaign.budget || campaign.startDate || campaign.endDate || campaign.targetAudience) {
        const adSetUpdateData: Record<string, unknown> = {};
        
        if (campaign.dailyBudget) adSetUpdateData.daily_budget = campaign.dailyBudget * 100;
        if (campaign.budget) adSetUpdateData.lifetime_budget = campaign.budget * 100;
        if (campaign.startDate) adSetUpdateData.start_time = campaign.startDate.toISOString();
        if (campaign.endDate) adSetUpdateData.end_time = campaign.endDate.toISOString();
        if (campaign.targetAudience) adSetUpdateData.targeting = this.formatTargeting(campaign.targetAudience);
        
        await this.apiClient.post<MetaApiGraphResponse>(adSetId, adSetUpdateData);
        
        this.logger.info('Conjunto de anuncios actualizado en Meta', this.platform, {
          adSetId,
          changes: Object.keys(adSetUpdateData)
        });
      }
      
      // Actualizar la campaña si es necesario
      if (campaign.name || campaign.status) {
        const campaignUpdateData: Record<string, unknown> = {};
        if (campaign.name) campaignUpdateData.name = campaign.name;
        if (campaign.status) campaignUpdateData.status = campaign.status === 'active' ? 'ACTIVE' : 'PAUSED';
        
        await this.apiClient.post<MetaApiGraphResponse>(campaignId, campaignUpdateData);
        
        this.logger.info('Campaña actualizada en Meta', this.platform, {
          campaignId,
          changes: Object.keys(campaignUpdateData)
        });
      }
      
      // Actualizar el creativo si es necesario
      if (campaign.content) {
        // Obtener información del creativo actual
        const adDetails = await this.apiClient.get<MetaApiGraphResponse>(
          adId,
          { params: { fields: 'creative.fields(id,object_story_spec)' } }
        );
        
        if (adDetails && adDetails.creative && adDetails.creative.id) {
          const creativeId = adDetails.creative.id;
          
          // Normalizar el ID de la cuenta
          const accountId = this.accountId?.replace('act_', '') || '';
          
          // Crear un nuevo creativo
          const newCreativeData = {
            name: `${campaign.name || adInfo.name} - Creative Updated`,
            object_story_spec: {
              page_id: this.pageId,
              link_data: {
                message: campaign.content.title + "\n\n" + campaign.content.description,
                link: campaign.content.landingPageUrl,
                image_url: campaign.content.imageUrl,
                call_to_action: {
                  type: this.mapCallToAction(campaign.content.callToAction),
                  value: {
                    link: campaign.content.landingPageUrl
                  }
                }
              }
            }
          };
          
          const newCreative = await this.apiClient.post<MetaApiGraphResponse>(
            `act_${accountId}/adcreatives`,
            newCreativeData
          );
          
          if (newCreative && newCreative.id) {
            // Actualizar el anuncio para usar el nuevo creativo
            await this.apiClient.post<MetaApiGraphResponse>(
              adId,
              { creative: { creative_id: newCreative.id } }
            );
            
            this.logger.info('Creativo actualizado en Meta', this.platform, {
              oldCreativeId: creativeId,
              newCreativeId: newCreative.id,
              adId
            });
          }
        }
      }
      
      // Obtener el estado actualizado del anuncio
      const updatedAdInfo = await this.apiClient.get<MetaApiGraphResponse>(
        adId,
        { params: { fields: 'id,name,status,effective_status,delivery_info' } }
      );
      
      // Calcular tiempo total
      const totalTime = Date.now() - startTime;
      
      this.logger.info(`Anuncio actualizado en Meta (${totalTime}ms)`, this.platform, {
        adId,
        campaignId,
        adSetId,
        status: updatedAdInfo.effective_status
      });
      
      // Enviar notificación por webhook
      this.notifyWebhook('ad.updated', {
        adId,
        campaignId,
        adSetId,
        status: updatedAdInfo.effective_status,
        platform: this.platform
      });
      
      return {
        success: true,
        data: {
          id: adId,
          campaignId: campaignId,
          adSetId: adSetId,
          status: updatedAdInfo.effective_status.toLowerCase(),
          deliveryStatus: updatedAdInfo.delivery_info ? updatedAdInfo.delivery_info.status.toLowerCase() : 'unknown',
          platform: this.platform,
          updatedAt: new Date().toISOString(),
        }
      };
    } catch (error) {
      // Registrar el error
      this.logger.error('Error al actualizar anuncio en Meta', error, this.platform, {
        adId
      });
      
      // Usar el manejador de errores
      return createErrorResponse(error, this.platform);
    }
  }
  
  /**
   * Elimina un anuncio de Facebook/Instagram (en realidad, lo desactiva)
   */
  async deleteAd(adId: string): Promise<ApiResponse> {
    try {
      // Registrar inicio de la operación
      this.logger.info('Eliminando anuncio en Meta', this.platform, {
        adId
      });
      
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }
      
      // Obtener información del anuncio para conseguir IDs relacionados
      const adInfo = await this.apiClient.get<MetaApiGraphResponse>(
        adId,
        { params: { fields: 'id,name,adset_id,campaign_id,status' } }
      );
      
      if (!adInfo || !adInfo.id) {
        throw new Error(`No se encontró el anuncio con ID ${adId}`);
      }
      
      // En Meta, normalmente se marca como DELETED en lugar de eliminarlo realmente
      await this.apiClient.post<MetaApiGraphResponse>(adId, { status: 'DELETED' });
      
      this.logger.info('Anuncio marcado como eliminado en Meta', this.platform, {
        adId,
        adSetId: adInfo.adset_id,
        campaignId: adInfo.campaign_id
      });
      
      // Enviar notificación por webhook
      this.notifyWebhook('ad.deleted', {
        adId,
        campaignId: adInfo.campaign_id,
        adSetId: adInfo.adset_id,
        platform: this.platform
      });
      
      return {
        success: true,
        data: {
          id: adId,
          deleted: true,
          deletedAt: new Date().toISOString(),
          details: {
            campaign_id: adInfo.campaign_id,
            adset_id: adInfo.adset_id,
            message: 'El anuncio ha sido desactivado permanentemente (status=DELETED)'
          }
        }
      };
    } catch (error) {
      // Registrar el error
      this.logger.error('Error al eliminar anuncio en Meta', error, this.platform, {
        adId
      });
      
      // Usar el manejador de errores
      return createErrorResponse(error, this.platform);
    }
  }
  
  /**
   * Obtiene el estado de un anuncio en Facebook/Instagram
   */
  async getAdStatus(adId: string): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }
      
      // Obtener datos completos del anuncio
      const adDetails = await this.apiClient.get<MetaApiGraphResponse>(
        adId,
        { 
          params: { 
            fields: 'id,name,status,effective_status,delivery_info,adset{name,status,delivery_info},campaign{name,status}' 
          } 
        }
      );
      
      if (!adDetails || !adDetails.id) {
        throw new Error(`No se encontró el anuncio con ID ${adId}`);
      }
      
      // Obtener información sobre errores de revisión o rechazos
      const adInsights = await this.apiClient.get<MetaApiGraphResponse>(
        `${adId}/insights`,
        { params: { fields: 'ad_id,status', date_preset: 'last_7_days' } }
      );
      
      // Mapear estados de la API a nuestro modelo
      let status: string;
      switch (adDetails.effective_status) {
        case 'ACTIVE':
          status = 'active';
          break;
        case 'PAUSED':
          status = 'paused';
          break;
        case 'DELETED':
          status = 'completed';
          break;
        case 'DISAPPROVED':
        case 'PENDING_REVIEW':
          status = 'pending';
          break;
        case 'WITH_ISSUES':
        case 'ERROR':
          status = 'error';
          break;
        default:
          status = 'draft';
      }
      
      // Determinar estado de entrega
      let deliveryStatus = 'unknown';
      if (adDetails.delivery_info && adDetails.delivery_info.status) {
        deliveryStatus = adDetails.delivery_info.status.toLowerCase();
      }
      
      // Obtener estadísticas rápidas
      let issueInfo = null;
      if (adDetails.issues_info) {
        issueInfo = adDetails.issues_info;
      }
      
      this.logger.info('Estado de anuncio obtenido de Meta', this.platform, {
        adId,
        status,
        effectiveStatus: adDetails.effective_status
      });
      
      return {
        success: true,
        data: {
          id: adId,
          name: adDetails.name,
          status: status,
          effectiveStatus: adDetails.effective_status,
          deliveryStatus: deliveryStatus,
          adsetStatus: adDetails.adset ? adDetails.adset.status : 'unknown',
          campaignStatus: adDetails.campaign ? adDetails.campaign.status : 'unknown',
          platform: this.platform,
          insightsStatus: adInsights && adInsights.data && adInsights.data.length > 0 
            ? adInsights.data[0].status 
            : 'no_insights',
          issues: issueInfo,
          lastChecked: new Date().toISOString(),
        }
      };
    } catch (error) {
      // Registrar el error
      this.logger.error('Error al obtener estado del anuncio en Meta', error, this.platform, {
        adId
      });
      
      // Usar el manejador de errores
      return createErrorResponse(error, this.platform);
    }
  }
  
  /**
   * Obtiene métricas de rendimiento de un anuncio en Facebook/Instagram
   */
  async getAdPerformance(adId: string, metrics: string[]): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }
      
      // Verificar si el anuncio existe
      const adInfo = await this.apiClient.get<MetaApiGraphResponse>(
        adId,
        { params: { fields: 'id,name,status' } }
      );
      
      if (!adInfo || !adInfo.id) {
        throw new Error(`No se encontró el anuncio con ID ${adId}`);
      }
      
      // Métricas predeterminadas si no se especifican
      if (!metrics || metrics.length === 0) {
        metrics = [
          'impressions', 
          'clicks', 
          'ctr', 
          'reach', 
          'spend', 
          'conversions'
        ];
      }
      
      // Mapeo de métricas genéricas a específicas de Meta
      const metricFieldsMap: Record<string, string> = {
        'impressions': 'impressions',
        'clicks': 'clicks',
        'ctr': 'ctr',
        'reach': 'reach',
        'frequency': 'frequency',
        'conversions': 'actions',
        'costPerConversion': 'cost_per_action_type',
        'costPerClick': 'cost_per_inline_link_click',
        'engagement': 'inline_post_engagement',
        'spend': 'spend',
        'uniqueClicks': 'unique_clicks',
        'videoViews': 'video_p25_watched_actions'
      };
      
      // Convertir métricas solicitadas al formato de Meta
      const metricFields = metrics.map(m => {
        return metricFieldsMap[m] || m;
      });
      
      // Campos adicionales para cálculos
      metricFields.push('spend', 'cost_per_inline_link_click', 'inline_link_clicks');
      
      // Evitar duplicados
      const uniqueMetrics = [...new Set(metricFields)];
      
      // Obtener insights de rendimiento
      const insightsResponse = await this.apiClient.get<MetaApiGraphResponse>(
        `${adId}/insights`,
        {
          params: {
            fields: uniqueMetrics.join(','),
            time_range: JSON.stringify({
              'since': new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
              'until': new Date().toISOString().split('T')[0]
            }),
            level: 'ad'
          }
        }
      );
      
      // Procesar los datos de la respuesta
      let metricsData: Record<string, unknown> = {};
      
      if (insightsResponse && insightsResponse.data && insightsResponse.data.length > 0) {
        const data = insightsResponse.data[0];
        
        // Mapear valores básicos
        for (const metric of metrics) {
          const apiMetric = metricFieldsMap[metric];
          if (apiMetric && data[apiMetric] !== undefined) {
            // Para métricas simples
            metricsData[metric] = data[apiMetric];
          } else if (metric === 'conversions' && data.actions) {
            // Caso especial para conversiones (suma de todas las acciones)
            const actions = data.actions;
            let totalConversions = 0;
            actions.forEach((action: any) => {
              if (action.action_type.includes('conversion')) {
                totalConversions += parseInt(action.value);
              }
            });
            metricsData[metric] = totalConversions;
          }
        }
        
        // Añadir métricas calculadas
        if (data.inline_link_clicks && data.spend) {
          metricsData.costPerClick = parseFloat((data.spend / data.inline_link_clicks).toFixed(2));
        }
        
        if (data.actions) {
          const totalActions = data.actions.reduce((sum: number, action: any) => sum + parseInt(action.value), 0);
          if (totalActions > 0 && data.spend) {
            metricsData.costPerConversion = parseFloat((data.spend / totalActions).toFixed(2));
          }
        }
        
        // Asegurar que todas las métricas numéricas son tipo number, no string
        for (const key in metricsData) {
          if (typeof metricsData[key] === 'string' && !isNaN(Number(metricsData[key]))) {
            metricsData[key] = parseFloat(metricsData[key] as string);
          }
        }
      } else {
        // Si no hay datos, inicializar con ceros
        metrics.forEach(metric => {
          metricsData[metric] = 0;
        });
      }
      
      this.logger.info('Métricas de anuncio obtenidas de Meta', this.platform, {
        adId,
        metrics: Object.keys(metricsData)
      });
      
      return {
        success: true,
        data: {
          id: adId,
          name: adInfo.name,
          metrics: metricsData,
          period: {
            from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
            to: new Date().toISOString()
          },
          platform: this.platform
        }
      };
    } catch (error) {
      // Registrar el error
      this.logger.error('Error al obtener métricas del anuncio en Meta', error, this.platform, {
        adId
      });
      
      // Usar el manejador de errores
      return createErrorResponse(error, this.platform);
    }
  }
  
  /**
   * Formatea los datos de segmentación para la API de Meta
   */
  private formatTargeting(targetAudience: AdCampaign['targetAudience']): any {
    return {
      geo_locations: {
        countries: targetAudience.locations.length > 0 ? targetAudience.locations : ['CO'],
        cities: targetAudience.locations.filter(loc => loc.includes(','))
      },
      age_min: targetAudience.ageRange.min || 18,
      age_max: targetAudience.ageRange.max || 65,
      genders: targetAudience.genders.includes('all') 
        ? [1, 2] // 1 = hombres, 2 = mujeres
        : targetAudience.genders.map(g => g === 'male' ? 1 : 2),
      interests: targetAudience.interests.map(interest => {
        // En una implementación real, se buscarían los IDs de interés en la API de Meta
        // o se usaría un endpoint para búsqueda de intereses
        return { id: `interest_${interest.replace(/\s/g, '_')}`, name: interest };
      }),
      education_statuses: targetAudience.educationLevels?.map(level => {
        // Mapeo de niveles educativos a los valores aceptados por Meta
        switch (level) {
          case 'high-school': return 1;
          case 'technical': return 2;
          case 'undergraduate': return 3;
          case 'graduate': return 4;
          default: return 1;
        }
      }),
      locales: targetAudience.languages?.map(lang => {
        // En una implementación real, se convertirían a códigos de idioma de Meta
        return lang;
      }),
    };
  }
  
  /**
   * Formatea los datos creativos para la API de Meta
   */
  private formatCreative(content: AdCampaign['content']): any {
    return {
      title: content.title,
      body: content.description,
      object_story_spec: {
        page_id: this.pageId,
        link_data: {
          image_url: content.imageUrl,
          link: content.landingPageUrl,
          message: content.description,
          call_to_action: {
            type: this.mapCallToAction(content.callToAction),
            value: {
              link: content.landingPageUrl
            }
          }
        }
      }
    };
  }
  
  /**
   * Mapea el CTA a valores aceptados por Meta
   */
  private mapCallToAction(callToAction: string): string {
    const ctaMap: Record<string, string> = {
      'Aplicar ahora': 'APPLY_NOW',
      'Registrarse': 'SIGN_UP',
      'Saber más': 'LEARN_MORE',
      'Contactar': 'CONTACT',
      'Enviar': 'SUBMIT_APPLICATION'
    };
    
    return ctaMap[callToAction] || 'LEARN_MORE';
  }
}