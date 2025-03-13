import { AdCampaign, ApiResponse, SocialMediaApi } from './types';
import { AuthService } from './auth';
import axios, { AxiosError } from 'axios';
import { EnhancedHttpClient, HttpClientConfig } from './enhanced-http-client';
import { createApiError, isAuthError, isRateLimitError } from './error-handler';

// Interfaz para datos de error de la API de Meta
interface MetaApiError {
  error: {
    code: number;
    message: string;
    type?: string;
    error_subcode?: number;
    fbtrace_id?: string;
  };
}

// Interfaces para respuestas específicas de la API de Meta
interface MetaApiBaseResponse {
  id?: string;
  success?: boolean;
  data?: unknown[];
  paging?: {
    cursors: {
      before: string;
      after: string;
    };
    next?: string;
  };
}

// Tipo para respuestas de anuncios
type MetaAdResponse = MetaApiBaseResponse & { id: string }

// Interfaces para respuestas específicas de la API de Meta
interface MetaAdAccount {
  id: string;
  name: string;
  account_status: number;
  business?: string;
  currency?: string;
}

interface MetaPage {
  id: string;
  name: string;
  access_token: string;
  category?: string;
}

interface MetaAdInfo {
  id: string;
  name: string;
  adset_id: string;
  campaign_id: string;
  creative?: {
    id: string;
    object_story_spec?: Record<string, unknown>;
  };
  status: string;
  effective_status?: string;
  delivery_info?: {
    status: string;
  };
  issues_info?: unknown;
  adset?: {
    name: string;
    status: string;
    delivery_info?: Record<string, unknown>;
  };
  campaign?: {
    name: string;
    status: string;
  };
}

interface MetaAdInsights {
  data: Array<{
    ad_id: string;
    status: string;
    impressions?: string | number;
    clicks?: string | number;
    ctr?: string | number;
    reach?: string | number;
    frequency?: string | number;
    actions?: Array<{
      action_type: string;
      value: string;
    }>;
    cost_per_action_type?: Array<Record<string, string>>;
    cost_per_inline_link_click?: string | number;
    inline_link_clicks?: string | number;
    inline_post_engagement?: string | number;
    spend?: string | number;
    unique_clicks?: string | number;
    video_p25_watched_actions?: Array<Record<string, string>>;
    [key: string]: unknown;
  }>;
  paging?: {
    cursors: {
      before: string;
      after: string;
    };
    next?: string;
  };
}

/**
 * Clase para manejar la integración con la API de Meta (Facebook/Instagram)
 * Documentación: https://developers.facebook.com/docs/marketing-apis/
 */
export class MetaApi implements SocialMediaApi {
  private apiKey: string;
  private apiSecret: string;
  private accessToken: string;
  private authService: AuthService;
  private baseUrl = 'https://graph.facebook.com/v18.0';
  private accountId?: string; // ID de la cuenta de anuncios de Meta
  private pageId?: string; // ID de la página de Facebook asociada
  private requestTimeout = 30000; // Timeout para peticiones (30 segundos)
  private rateLimitRetries = 3; // Número máximo de reintentos para rate limiting
  private rateLimitDelay = 5000; // Tiempo de espera entre reintentos (5 segundos)
  private httpClient: EnhancedHttpClient;

  constructor(apiKey: string, apiSecret: string, accessToken: string, authService?: AuthService) {
    this.apiKey = apiKey;
    this.apiSecret = apiSecret;
    this.accessToken = accessToken;
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
    
    this.httpClient = new EnhancedHttpClient('meta', httpConfig);
  }

  /**
   * Inicializa la API con autenticación
   */
  async initialize(): Promise<ApiResponse> {
    try {
      // Autenticar con Meta
      const authResult = await this.authService.authenticateMeta({
        clientId: this.apiKey,
        clientSecret: this.apiSecret,
        accessToken: this.accessToken
      });

      if (!authResult.success) {
        return {
          success: false,
          error: {
            code: 'META_AUTH_ERROR',
            message: authResult.error?.message || 'Error de autenticación con Meta'
          }
        };
      }

      // Extender token a larga duración si es posible
      const extendResult = await this.authService.extendMetaToken({
        clientId: this.apiKey,
        clientSecret: this.apiSecret,
        accessToken: this.accessToken
      });

      if (extendResult.success && extendResult.credentials) {
        this.accessToken = extendResult.credentials.accessToken;
        
        // Actualizar el token en el cliente HTTP
        this.httpClient.setAccessToken(this.accessToken);
      }

      // Obtener información de la cuenta de anuncios
      try {
        // Obtener cuentas de anuncios asociadas al usuario
        const accountsResponse = await this.makeRequest(
          'me/adaccounts',
          'GET',
          { fields: 'id,name,account_status,business,currency' }
        ) as { data: MetaAdAccount[] };
        
        if (accountsResponse && accountsResponse.data && accountsResponse.data.length > 0) {
          // Tomar la primera cuenta activa
          const activeAccount = accountsResponse.data.find((acc) => acc.account_status === 1);
          if (activeAccount) {
            this.accountId = activeAccount.id;
          } else {
            this.accountId = accountsResponse.data[0].id;
          }
        } else {
          throw new Error('No se encontraron cuentas de anuncios asociadas');
        }
        
        // Obtener páginas asociadas al usuario
        const pagesResponse = await this.makeRequest(
          'me/accounts',
          'GET',
          { fields: 'id,name,access_token,category' }
        ) as { data: MetaPage[] };
        
        if (pagesResponse && pagesResponse.data && pagesResponse.data.length > 0) {
          this.pageId = pagesResponse.data[0].id;
        } else {
          console.warn('No se encontraron páginas de Facebook asociadas al usuario');
        }
        
      } catch (accountError: unknown) {
        console.warn('Error al obtener información de cuentas:', accountError instanceof Error ? accountError.message : 'Error desconocido');
        // Si falla, usar IDs simulados para pruebas
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
    } catch (error: unknown) {
      console.error('Error al inicializar Meta API:', error);
      return {
        success: false,
        error: {
          code: 'META_INIT_ERROR',
          message: error instanceof Error ? error.message : 'Error al inicializar Meta API'
        }
      };
    }
  }

  /**
   * Verifica si la API está autenticada
   */
  isAuthenticated(): boolean {
    return this.authService.isAuthenticated('meta');
  }

  /**
   * Obtiene el token de acceso actual
   */
  getAccessToken(): string {
    const token = this.authService.getAccessToken('meta');
    return token || this.accessToken;
  }

  /**
   * Método para realizar peticiones a la API de Graph usando el cliente HTTP mejorado
   * Incluye manejo de rate limiting, reintentos y errores
   */
  private async makeRequest(
    endpoint: string, 
    method: 'GET' | 'POST' | 'DELETE', 
    data?: Record<string, unknown>
  ): Promise<unknown> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
        if (!this.isAuthenticated()) {
          throw new Error('Meta API no está autenticada');
        }
      }

      // Formatear la URL si es una URL completa
      if (endpoint.startsWith('http')) {
        // Si es una URL completa, usar directamente
        return this.makeExternalRequest(endpoint, method, data);
      }
      
      // Obtener token de acceso actualizado
      const accessToken = this.getAccessToken();
      
      // Preparar los datos según el método
      let requestData: Record<string, unknown> = {};
      let params: Record<string, unknown> | undefined;
      
      if (method === 'GET') {
        params = { ...data, access_token: accessToken };
      } else {
        requestData = { ...data, access_token: accessToken };
      }
      
      // Usar el cliente HTTP mejorado para hacer la petición
      return await this.httpClient.request(method, endpoint, requestData, {
        params,
        timeout: this.requestTimeout,
        retries: this.rateLimitRetries,
        headers: {
          'Content-Type': 'application/json'
        }
      });
    } catch (error) {
      // Manejar errores específicos de la API de Meta
      if (error instanceof AxiosError) {
        const axiosError = error;
        
        // Extraer información del error
        const errorData = axiosError.response?.data as MetaApiError;
        
        // Formatear mensaje de error
        const errorMessage = errorData?.error?.message || axiosError.message;
        const errorCode = errorData?.error?.code || 'UNKNOWN_ERROR';
        throw new Error(`Error ${errorCode} en la petición a Meta API: ${errorMessage}`);
      }
      
      // Error no relacionado con axios
      throw error;
    }
  }
  
  /**
   * Método para realizar peticiones a URLs externas
   */
  private async makeExternalRequest(
    url: string, 
    method: 'GET' | 'POST' | 'DELETE', 
    data?: Record<string, unknown>
  ): Promise<unknown> {
    try {
      // Obtener token de acceso actualizado
      const accessToken = this.getAccessToken();
      
      // Preparar los datos según el método
      let requestData: Record<string, unknown> = {};
      let params: Record<string, unknown> | undefined;
      
      if (method === 'GET') {
        params = { ...data, access_token: accessToken };
      } else {
        requestData = { ...data, access_token: accessToken };
      }
      
      // Usar axios directamente para URLs externas
      const response = await axios({
        method,
        url,
        data: method !== 'GET' ? requestData : undefined,
        params: method === 'GET' ? params : undefined,
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: this.requestTimeout
      });
      
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        // Manejar errores específicos
        if (isAuthError(error, 'meta')) {
          throw new Error('Error de autenticación en petición externa');
        }
        if (isRateLimitError(error, 'meta')) {
          throw new Error('Límite de tasa excedido en petición externa');
        }
        
        // Otros errores de axios
        throw createApiError(error, 'meta');
      }
      
      // Errores no relacionados con axios
      throw error;
    }
  }

  /**
   * Crea un anuncio en Facebook/Instagram
   */
  async createAd(campaign: AdCampaign): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Validar que tenemos un ID de cuenta válido
      if (!this.accountId) {
        throw new Error('No se ha establecido un ID de cuenta de anuncios válido');
      }

      // Validar que tenemos un ID de página válido para el creativo
      if (!this.pageId) {
        throw new Error('No se ha establecido un ID de página de Facebook válido');
      }

      // Normalizar el ID de la cuenta (quitar 'act_' si está presente)
      const accountId = this.accountId.replace('act_', '');

      // Preparar datos para la API de Meta
      const adData = {
        name: campaign.name,
        objective: 'CONVERSIONS',
        status: 'PAUSED', // Iniciar en pausa para revisión
        special_ad_categories: [],
        // Datos adicionales según API de Meta
        targeting: this.formatTargeting(campaign.targetAudience),
        creative: this.formatCreative(campaign.content),
        budget_remaining: campaign.budget * 100, // Convertir a centavos (Meta usa unidades menores)
        daily_budget: campaign.dailyBudget ? campaign.dailyBudget * 100 : undefined, // Convertir a centavos
        start_time: campaign.startDate.toISOString(),
        end_time: campaign.endDate.toISOString()
      };

      // 1. Crear la campaña
      const campaignResult = await this.makeRequest(`act_${accountId}/campaigns`, 'POST', {
        name: adData.name,
        objective: adData.objective,
        status: adData.status,
        special_ad_categories: adData.special_ad_categories,
      }) as { id: string };
      
      if (!campaignResult || !campaignResult.id) {
        throw new Error('No se pudo crear la campaña en Meta');
      }
      
      // 2. Crear conjunto de anuncios (Ad Set)
      const adSetResult = await this.makeRequest(`act_${accountId}/adsets`, 'POST', {
        name: `${adData.name} - Conjunto`,
        campaign_id: campaignResult.id,
        targeting: adData.targeting,
        daily_budget: adData.daily_budget || adData.budget_remaining,
        lifetime_budget: !adData.daily_budget ? adData.budget_remaining : undefined,
        start_time: adData.start_time,
        end_time: adData.end_time,
        bid_amount: 1000, // 10 USD en centavos, licitación máxima
        billing_event: 'IMPRESSIONS',
        optimization_goal: 'LINK_CLICKS',
        pacing_type: ['standard'],
        status: adData.status
      }) as { id: string };
      
      if (!adSetResult || !adSetResult.id) {
        throw new Error('No se pudo crear el conjunto de anuncios en Meta');
      }
      
      // 3. Crear primero el creativo para el anuncio
      const creativeResult = await this.makeRequest(`act_${accountId}/adcreatives`, 'POST', {
        name: `${adData.name} - Creativo`,
        object_story_spec: {
          page_id: this.pageId,
          link_data: {
            message: adData.creative.title + "\n\n" + adData.creative.body,
            link: (adData.creative as { object_story_spec?: { link_data?: { link?: string } } })?.object_story_spec?.link_data?.link || '',
            image_url: (adData.creative as { object_story_spec?: { link_data?: { image_url?: string } } })?.object_story_spec?.link_data?.image_url || '',
            call_to_action: (adData.creative as { object_story_spec?: { link_data?: { call_to_action?: Record<string, unknown> } } })?.object_story_spec?.link_data?.call_to_action || {}
          }
        }
      }) as MetaAdResponse;
      
      if (!creativeResult?.id) {
        throw new Error('No se pudo crear el creativo del anuncio en Meta');
      }
      
      // 4. Crear el anuncio asociando el creativo
      const adResult = await this.makeRequest(`act_${accountId}/ads`, 'POST', {
        name: `${adData.name} - Anuncio`,
        adset_id: adSetResult.id,
        creative: { creative_id: creativeResult.id },
        status: adData.status
      }) as MetaAdResponse;
      
      if (!adResult?.id) {
        throw new Error('No se pudo crear el anuncio en Meta');
      }

      // Registrar resultado completo con IDs de los recursos creados
      return {
        success: true,
        data: {
          id: adResult.id,
          campaignId: campaignResult.id,
          adSetId: adSetResult.id,
          creativeId: creativeResult.id,
          status: 'pending', // El anuncio está en pausa, pendiente de revisión
          platform: 'meta',
          createdAt: new Date().toISOString(),
          // Incluir información adicional útil
          details: {
            // Agregar enlaces a los recursos creados (útil para panel de administración)
            campaignUrl: `https://business.facebook.com/adsmanager/manage/campaigns?act=${accountId}&selected_campaign_ids=${campaignResult.id.split('_')[1]}`,
            adSetUrl: `https://business.facebook.com/adsmanager/manage/adsets?act=${accountId}&selected_adset_ids=${adSetResult.id.split('_')[1]}`,
            adUrl: `https://business.facebook.com/adsmanager/manage/ads?act=${accountId}&selected_ad_ids=${adResult.id.split('_')[1]}`,
          }
        }
      };
    } catch (error) {
      const typedError = error as Error;
      console.error('Error al crear anuncio en Meta:', typedError);
      
      // Manejar errores específicos de la API de Meta
      if (typedError.message && typedError.message.includes('Error ')) {
        const errorMatch = typedError.message.match(/Error (\d+)/);
        const errorCode = errorMatch ? errorMatch[1] : 'META_API_ERROR';
        
        // Mapear códigos de error comunes a mensajes más amigables
        const errorMessages: Record<string, string> = {
          '100': 'Error de sintaxis en la petición a Meta API',
          '190': 'Token de acceso inválido o expirado',
          '200': 'No se encontró el recurso solicitado',
          '294': 'Error en la gestión de la campaña publicitaria',
          '2635': 'Error en la segmentación del anuncio, verifique los parámetros',
          '1487395': 'Límite de gasto diario demasiado bajo',
          // Agregar más códigos de error según la documentación de Meta
        };
        
        return {
          success: false,
          error: {
            code: `META_ERROR_${errorCode}`,
            message: errorMessages[errorCode] || typedError.message
          }
        };
      }
      
      return {
        success: false,
        error: {
          code: 'META_API_ERROR',
          message: typedError.message || 'Error desconocido al crear anuncio en Meta'
        }
      };
    }
  }

  /**
   * Formatea los datos de segmentación para la API de Meta
   */
  private formatTargeting(targetAudience: AdCampaign['targetAudience']): Record<string, unknown> {
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
      // Otras opciones de segmentación soportadas por Meta
    };
  }

  /**
   * Formatea los datos creativos para la API de Meta
   */
  private formatCreative(content: AdCampaign['content']): Record<string, unknown> {
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

  /**
   * Actualiza un anuncio existente en Facebook/Instagram
   */
  async updateAd(adId: string, campaign: Partial<AdCampaign>): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Buscar información completa del anuncio
      const adInfo = await this.makeRequest(
        adId, 
        'GET', 
        { fields: 'id,name,adset_id,campaign_id,creative,status' }
      ) as MetaAdInfo;

      if (!adInfo || !adInfo.id) {
        throw new Error(`No se encontró el anuncio con ID ${adId}`);
      }

      // Obtener IDs relacionados
      const adSetId = adInfo.adset_id;
      const campaignId = adInfo.campaign_id;
      
      // Actualizar el anuncio
      if (campaign.name || campaign.status) {
        const adUpdateData: Record<string, unknown> = {};
        if (campaign.name) adUpdateData.name = campaign.name;
        if (campaign.status) adUpdateData.status = campaign.status === 'active' ? 'ACTIVE' : 'PAUSED';
        
        await this.makeRequest(adId, 'POST', adUpdateData);
      }
      
      // Actualizar el conjunto de anuncios si es necesario
      if (campaign.dailyBudget || campaign.budget || campaign.startDate || campaign.endDate || campaign.targetAudience) {
        const adSetUpdateData: Record<string, unknown> = {};
        
        if (campaign.dailyBudget) adSetUpdateData.daily_budget = campaign.dailyBudget * 100; // Convertir a centavos
        if (campaign.budget) adSetUpdateData.lifetime_budget = campaign.budget * 100; // Convertir a centavos
        if (campaign.startDate) adSetUpdateData.start_time = campaign.startDate.toISOString();
        if (campaign.endDate) adSetUpdateData.end_time = campaign.endDate.toISOString();
        if (campaign.targetAudience) adSetUpdateData.targeting = this.formatTargeting(campaign.targetAudience);
        
        await this.makeRequest(adSetId, 'POST', adSetUpdateData);
      }
      
      // Actualizar la campaña si es necesario
      if (campaign.name || campaign.status) {
        const campaignUpdateData: Record<string, unknown> = {};
        if (campaign.name) campaignUpdateData.name = campaign.name;
        if (campaign.status) campaignUpdateData.status = campaign.status === 'active' ? 'ACTIVE' : 'PAUSED';
        
        await this.makeRequest(campaignId, 'POST', campaignUpdateData);
      }
      
      // Actualizar el creativo si es necesario
      if (campaign.content) {
        // Obtener información del creativo actual
        const adDetails = await this.makeRequest(
          adId,
          'GET',
          { fields: 'creative.fields(id,object_story_spec)' }
        ) as MetaAdInfo;
        
        if (adDetails && adDetails.creative && adDetails.creative.id) {
          // Usamos el ID del creativo para crear uno nuevo basado en él
          
          // Crear un nuevo creativo con los cambios
          const newCreativeData = {
            name: `${campaign.name || adInfo.name} - Creative Updated`,
            object_story_spec: {
              page_id: this.pageId,
              link_data: {
                message: (campaign.content?.title || '') + "\n\n" + (campaign.content?.description || ''),
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
          
          // Crear nuevo creativo
          const newCreative = await this.makeRequest(
            `act_${this.accountId ? this.accountId.replace('act_', '') : ''}/adcreatives`,
            'POST',
            newCreativeData
          ) as MetaAdResponse;
          
          if (newCreative?.id) {
            // Actualizar el anuncio para usar el nuevo creativo
            await this.makeRequest(
              adId,
              'POST',
              { creative: { creative_id: newCreative.id } }
            );
          }
        }
      }

      // Obtener el estado actualizado del anuncio
      const updatedAdInfo = await this.makeRequest(
        adId,
        'GET',
        { fields: 'id,name,status,effective_status,delivery_info' }
      ) as MetaAdInfo;

      return {
        success: true,
        data: {
          id: adId,
          campaignId: campaignId,
          adSetId: adSetId,
          status: updatedAdInfo.effective_status ? updatedAdInfo.effective_status.toLowerCase() : 'unknown',
          deliveryStatus: updatedAdInfo.delivery_info ? updatedAdInfo.delivery_info.status.toLowerCase() : 'unknown',
          platform: 'meta',
          updatedAt: new Date().toISOString(),
        }
      };
    } catch (error) {
      const typedError = error as Error;
      console.error(`Error al actualizar anuncio ${adId} en Meta:`, typedError);
      
      // Manejar errores específicos de la API de Meta
      if (typedError.message && typedError.message.includes('Error ')) {
        const errorMatch = typedError.message.match(/Error (\d+)/);
        const errorCode = errorMatch ? errorMatch[1] : 'META_API_ERROR';
        
        // Mapear códigos de error comunes a mensajes más amigables
        const errorMessages: Record<string, string> = {
          '100': 'Error de sintaxis en la petición a Meta API',
          '190': 'Token de acceso inválido o expirado',
          '200': 'No se encontró el anuncio solicitado',
          '294': 'Error en la gestión de la campaña publicitaria',
          // Agregar más códigos de error según documentación
        };
        
        return {
          success: false,
          error: {
            code: `META_ERROR_${errorCode}`,
            message: errorMessages[errorCode] || typedError.message
          }
        };
      }
      
      return {
        success: false,
        error: {
          code: 'META_API_ERROR',
          message: typedError.message || 'Error desconocido al actualizar anuncio en Meta'
        }
      };
    }
  }

  /**
   * Elimina un anuncio de Facebook/Instagram
   * Nota: En Meta, "eliminar" un anuncio realmente lo desactiva permanentemente,
   * pero sigue siendo visible en el historial de la cuenta
   */
  async deleteAd(adId: string): Promise<ApiResponse> {
    try {
      // Verificar autenticación
      if (!this.isAuthenticated()) {
        await this.initialize();
      }

      // Obtener información del anuncio para conseguir IDs relacionados
      const adInfo = await this.makeRequest(
        adId, 
        'GET', 
        { fields: 'id,name,adset_id,campaign_id,status' }
      ) as MetaAdInfo;

      if (!adInfo || !adInfo.id) {
        throw new Error(`No se encontró el anuncio con ID ${adId}`);
      }

      // En Meta, normalmente se desactiva el anuncio en lugar de eliminarlo
      // Para una "eliminación" completa, desactivamos todos los niveles
      
      // 1. Desactivar el anuncio
      await this.makeRequest(adId, 'POST', { status: 'DELETED' });
      
      // 2. Opcional: También se puede desactivar el conjunto de anuncios
      // Si se desea un borrado más completo, descomentar:
      /*
      if (adInfo.adset_id) {
        await this.makeRequest(adInfo.adset_id, 'POST', { status: 'DELETED' });
      }
      
      // 3. Opcional: También se puede desactivar la campaña
      if (adInfo.campaign_id) {
        await this.makeRequest(adInfo.campaign_id, 'POST', { status: 'DELETED' });
      }
      */

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
      const typedError = error as Error;
      console.error(`Error al eliminar anuncio ${adId} en Meta:`, typedError);
      
      // Manejar errores específicos
      if (typedError.message && typedError.message.includes('Error ')) {
        const errorMatch = typedError.message.match(/Error (\d+)/);
        const errorCode = errorMatch ? errorMatch[1] : 'META_API_ERROR';
        
        const errorMessages: Record<string, string> = {
          '100': 'Error de sintaxis en la petición a Meta API',
          '190': 'Token de acceso inválido o expirado',
          '200': 'No se encontró el anuncio solicitado',
          '294': 'Error en la gestión de la campaña publicitaria',
        };
        
        return {
          success: false,
          error: {
            code: `META_ERROR_${errorCode}`,
            message: errorMessages[errorCode] || typedError.message
          }
        };
      }
      
      return {
        success: false,
        error: {
          code: 'META_API_ERROR',
          message: typedError.message || 'Error desconocido al eliminar anuncio en Meta'
        }
      };
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
      const adDetails = await this.makeRequest(
        adId, 
        'GET',
        { fields: 'id,name,status,effective_status,delivery_info,adset{name,status,delivery_info},campaign{name,status}' }
      ) as MetaAdInfo;

      if (!adDetails || !adDetails.id) {
        throw new Error(`No se encontró el anuncio con ID ${adId}`);
      }

      // Obtener información sobre errores de revisión o rechazos
      const adInsights = await this.makeRequest(
        `${adId}/insights`,
        'GET',
        { fields: 'ad_id,status', date_preset: 'last_7_days' }
      ) as MetaAdInsights;

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
          platform: 'meta',
          insightsStatus: adInsights && adInsights.data && adInsights.data.length > 0 
            ? adInsights.data[0].status 
            : 'no_insights',
          issues: issueInfo,
          lastChecked: new Date().toISOString(),
        }
      };
    } catch (error) {
      const typedError = error as Error;
      console.error(`Error al obtener estado del anuncio ${adId} en Meta:`, typedError);
      
      // Manejar errores específicos
      if (typedError.message && typedError.message.includes('Error ')) {
        const errorMatch = typedError.message.match(/Error (\d+)/);
        const errorCode = errorMatch ? errorMatch[1] : 'META_API_ERROR';
        
        const errorMessages: Record<string, string> = {
          '100': 'Error de sintaxis en la petición a Meta API',
          '190': 'Token de acceso inválido o expirado',
          '200': 'No se encontró el anuncio solicitado',
        };
        
        return {
          success: false,
          error: {
            code: `META_ERROR_${errorCode}`,
            message: errorMessages[errorCode] || typedError.message
          }
        };
      }
      
      return {
        success: false,
        error: {
          code: 'META_API_ERROR',
          message: typedError.message || 'Error desconocido al obtener estado del anuncio en Meta'
        }
      };
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
      const adInfo = await this.makeRequest(
        adId,
        'GET',
        { fields: 'id,name,status' }
      ) as MetaAdInfo;

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

      // Evitar duplicados usando un objeto para rastrear métricas únicas
      const uniqueMetricsObj: Record<string, boolean> = {};
      metricFields.forEach(metric => uniqueMetricsObj[metric] = true);
      const uniqueMetrics = Object.keys(uniqueMetricsObj);

      // Obtener insights de rendimiento
      const insightsResponse = await this.makeRequest(
        `${adId}/insights`,
        'GET',
        {
          fields: uniqueMetrics.join(','),
          time_range: JSON.stringify({
            'since': new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            'until': new Date().toISOString().split('T')[0]
          }),
          level: 'ad'
        }
      ) as MetaAdInsights;

      // Procesar los datos de la respuesta
      const metricsData: Record<string, unknown> = {};
      
      if (insightsResponse && insightsResponse.data && insightsResponse.data.length > 0) {
        const data = insightsResponse.data[0];
        
        // Mapear valores básicos
        for (const metric of metrics) {
          const apiMetric = metricFieldsMap[metric];
          if (apiMetric && data[apiMetric] !== undefined) {
            // Para métricas simples
            metricsData[metric] = data[apiMetric];
          } else if (metric === 'conversions' && data.actions && Array.isArray(data.actions)) {
            // Caso especial para conversiones (suma de todas las acciones)
            const actions = data.actions;
            let totalConversions = 0;
            actions.forEach((action: { action_type: string; value: string }) => {
              if (action.action_type && action.action_type.includes('conversion')) {
                totalConversions += parseInt(action.value, 10);
              }
            });
            metricsData[metric] = totalConversions;
          }
        }
        
        // Añadir métricas calculadas
        if (typeof data.inline_link_clicks === 'number' && typeof data.spend === 'number' && data.inline_link_clicks > 0) {
          metricsData.costPerClick = parseFloat((data.spend / data.inline_link_clicks).toFixed(2));
        } else if (typeof data.inline_link_clicks === 'string' && typeof data.spend === 'string') {
          const clicks = parseFloat(data.inline_link_clicks);
          const spend = parseFloat(data.spend);
          if (!isNaN(clicks) && !isNaN(spend) && clicks > 0) {
            metricsData.costPerClick = parseFloat((spend / clicks).toFixed(2));
          }
        }
        
        if (data.actions && Array.isArray(data.actions)) {
          const totalActions = data.actions.reduce((sum: number, action: { value: string }) => {
            if (action && action.value) {
              return sum + parseInt(action.value, 10);
            }
            return sum;
          }, 0);
          
          if (totalActions > 0) {
            if (typeof data.spend === 'number') {
              metricsData.costPerConversion = parseFloat((data.spend / totalActions).toFixed(2));
            } else if (typeof data.spend === 'string') {
              const spend = parseFloat(data.spend);
              if (!isNaN(spend)) {
                metricsData.costPerConversion = parseFloat((spend / totalActions).toFixed(2));
              }
            }
          }
        }
        
        // Asegurar que todas las métricas numéricas son tipo number, no string
        for (const key in metricsData) {
          if (metricsData.hasOwnProperty(key)) {
            const value = metricsData[key];
            if (typeof value === 'string' && !isNaN(Number(value))) {
              metricsData[key] = parseFloat(value as string);
            }
          }
        }
      } else {
        // Si no hay datos, inicializar con ceros
        metrics.forEach(metric => {
          metricsData[metric] = 0;
        });
      }

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
          platform: 'meta'
        }
      };
    } catch (error) {
      const typedError = error as Error;
      console.error(`Error al obtener métricas del anuncio ${adId} en Meta:`, typedError);
      
      // Manejar errores específicos
      if (typedError.message && typedError.message.includes('Error ')) {
        const errorMatch = typedError.message.match(/Error (\d+)/);
        const errorCode = errorMatch ? errorMatch[1] : 'META_API_ERROR';
        
        const errorMessages: Record<string, string> = {
          '100': 'Error de sintaxis en la petición a Meta API',
          '190': 'Token de acceso inválido o expirado',
          '200': 'No se encontró el anuncio solicitado',
          '274': 'No se encontraron datos para las métricas solicitadas',
        };
        
        return {
          success: false,
          error: {
            code: `META_ERROR_${errorCode}`,
            message: errorMessages[errorCode] || typedError.message
          }
        };
      }
      
      return {
        success: false,
        error: {
          code: 'META_API_ERROR',
          message: typedError.message || 'Error desconocido al obtener métricas del anuncio en Meta'
        }
      };
    }
  }
}