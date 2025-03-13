import { SocialMediaService } from './index';
import { SocialPlatform } from './types';

export interface PerformanceMetrics {
  impressions: number;
  clicks: number;
  ctr: number;
  conversions: number;
  costPerClick: number;
  costPerConversion: number;
  spend: number;
  reach?: number;
  frequency?: number;
  engagement?: number;
  videoViews?: number;
}

export interface PlatformPerformance {
  platform: SocialPlatform;
  adId: string;
  adName?: string;
  metrics: PerformanceMetrics;
  period: {
    from: string;
    to: string;
  };
}

export interface AggregatedPerformance {
  totalImpressions: number;
  totalClicks: number;
  averageCtr: number;
  totalConversions: number;
  averageCostPerClick: number;
  averageCostPerConversion: number;
  totalSpend: number;
  platformBreakdown: Record<SocialPlatform, Partial<PerformanceMetrics>>;
}

export interface PerformanceByPeriod {
  period: string;
  impressions: number;
  clicks: number;
  conversions: number;
  spend: number;
}

export interface DemographicData {
  gender: {
    male: number;
    female: number;
    other?: number;
  };
  age: {
    '18-24': number;
    '25-34': number;
    '35-44': number;
    '45-54': number;
    '55+': number;
  };
  locations: Record<string, number>;
}

/**
 * Servicio para agregar y procesar datos analíticos de múltiples plataformas
 */
export class AnalyticsService {
  constructor(private socialMediaService: SocialMediaService) {}

  /**
   * Obtiene métricas de rendimiento para un anuncio específico
   */
  async getAdPerformance(platform: SocialPlatform, adId: string): Promise<PlatformPerformance | null> {
    const metrics = [
      'impressions',
      'clicks',
      'ctr',
      'conversions',
      'costPerClick',
      'costPerConversion',
      'spend',
      'reach',
      'frequency',
      'engagement',
      'videoViews'
    ];

    const response = await this.socialMediaService.getAdPerformance(platform, adId, metrics);
    
    if (!response.success || !response.data) {
      console.error(`Error al obtener métricas para ${platform}:`, response.error);
      return null;
    }

    return {
      platform,
      adId,
      adName: response.data.name as string,
      metrics: response.data.metrics as PerformanceMetrics,
      period: response.data.period as { from: string; to: string }
    };
  }

  /**
   * Obtiene métricas de rendimiento para múltiples anuncios en diferentes plataformas
   */
  async getCrossplatformPerformance(
    adIds: Record<SocialPlatform, string>
  ): Promise<PlatformPerformance[]> {
    const metrics = [
      'impressions',
      'clicks',
      'ctr',
      'conversions',
      'costPerClick',
      'costPerConversion',
      'spend',
      'reach',
      'frequency',
      'engagement',
      'videoViews'
    ];

    const responses = await this.socialMediaService.getMultiPlatformPerformance(adIds, metrics);
    const results: PlatformPerformance[] = [];

    for (const [platform, response] of Object.entries(responses)) {
      if (response.success && response.data) {
        results.push({
          platform: platform as SocialPlatform,
          adId: adIds[platform as SocialPlatform],
          adName: response.data.name as string,
          metrics: response.data.metrics as PerformanceMetrics,
          period: response.data.period as { from: string; to: string }
        });
      } else {
        console.error(`Error al obtener métricas para ${platform}:`, response.error);
      }
    }

    return results;
  }

  /**
   * Agrega las métricas de rendimiento de varias plataformas
   */
  aggregatePerformance(platformData: PlatformPerformance[]): AggregatedPerformance {
    // Inicializar objeto de agregación
    const aggregated: AggregatedPerformance = {
      totalImpressions: 0,
      totalClicks: 0,
      averageCtr: 0,
      totalConversions: 0,
      averageCostPerClick: 0,
      averageCostPerConversion: 0,
      totalSpend: 0,
      platformBreakdown: {} as Record<SocialPlatform, Partial<PerformanceMetrics>>
    };

    if (platformData.length === 0) return aggregated;

    // Calcular totales
    let validCtrCount = 0;
    let validCpcCount = 0;
    let validCpaCount = 0;

    platformData.forEach(data => {
      const { platform, metrics } = data;
      
      // Agregar a los totales
      aggregated.totalImpressions += metrics.impressions || 0;
      aggregated.totalClicks += metrics.clicks || 0;
      aggregated.totalConversions += metrics.conversions || 0;
      aggregated.totalSpend += metrics.spend || 0;
      
      // Para promedios, solo contar valores válidos
      if (metrics.ctr) {
        aggregated.averageCtr += metrics.ctr;
        validCtrCount++;
      }
      
      if (metrics.costPerClick) {
        aggregated.averageCostPerClick += metrics.costPerClick;
        validCpcCount++;
      }
      
      if (metrics.costPerConversion) {
        aggregated.averageCostPerConversion += metrics.costPerConversion;
        validCpaCount++;
      }
      
      // Agregar al desglose por plataforma
      if (!aggregated.platformBreakdown[platform]) {
        aggregated.platformBreakdown[platform] = {};
      }
      
      aggregated.platformBreakdown[platform] = {
        impressions: metrics.impressions || 0,
        clicks: metrics.clicks || 0,
        ctr: metrics.ctr || 0,
        conversions: metrics.conversions || 0,
        costPerClick: metrics.costPerClick || 0,
        costPerConversion: metrics.costPerConversion || 0,
        spend: metrics.spend || 0
      };
    });
    
    // Calcular promedios
    if (validCtrCount > 0) aggregated.averageCtr /= validCtrCount;
    if (validCpcCount > 0) aggregated.averageCostPerClick /= validCpcCount;
    if (validCpaCount > 0) aggregated.averageCostPerConversion /= validCpaCount;
    
    return aggregated;
  }

  /**
   * Procesa datos de rendimiento para visualización en gráficos de series temporales
   * Agrupa los datos por período (día, semana, mes)
   */
  getPerformanceByPeriod(
    platformData: PlatformPerformance[], 
    // groupBy param can be implemented for a more complete solution
  ): PerformanceByPeriod[] {
    const periodsMap = new Map<string, PerformanceByPeriod>();
    
    platformData.forEach(data => {
      const { metrics, period } = data;
      
      // Simplificado para el ejemplo, normalmente habría lógica para procesar
      // rangos de fechas y agruparlos correctamente según groupBy
      const periodKey = period.from.substring(0, 7); // YYYY-MM para agrupación mensual
      
      if (!periodsMap.has(periodKey)) {
        periodsMap.set(periodKey, {
          period: periodKey,
          impressions: 0,
          clicks: 0,
          conversions: 0,
          spend: 0
        });
      }
      
      const existingPeriod = periodsMap.get(periodKey)!;
      existingPeriod.impressions += metrics.impressions || 0;
      existingPeriod.clicks += metrics.clicks || 0;
      existingPeriod.conversions += metrics.conversions || 0;
      existingPeriod.spend += metrics.spend || 0;
    });
    
    return Array.from(periodsMap.values());
  }

  /**
   * Obtiene los mejores anuncios según una métrica específica
   */
  getTopPerformingAds(
    platformData: PlatformPerformance[],
    metric: keyof PerformanceMetrics,
    limit: number = 5,
    sortOrder: 'asc' | 'desc' = 'desc'
  ): PlatformPerformance[] {
    return [...platformData].sort((a, b) => {
      const aValue = a.metrics[metric] || 0;
      const bValue = b.metrics[metric] || 0;
      return sortOrder === 'desc' ? bValue - aValue : aValue - bValue;
    }).slice(0, limit);
  }

  /**
   * Simula la obtención de datos demográficos (esta funcionalidad dependería de
   * los datos disponibles en cada plataforma - implementación real requeriría APIs específicas)
   */
  // Platform parameter used for logging, adId will be used in a real implementation
  async getDemographicData(platform: SocialPlatform): Promise<DemographicData | null> {
    try {
      // Esta es una simulación, la implementación real requeriría llamadas API específicas
      // a cada plataforma para obtener datos demográficos
      return {
        gender: {
          male: 58,
          female: 42
        },
        age: {
          '18-24': 15,
          '25-34': 42, 
          '35-44': 28,
          '45-54': 10,
          '55+': 5
        },
        locations: {
          'Madrid': 35,
          'Barcelona': 28,
          'Valencia': 12,
          'Sevilla': 10,
          'Otras': 15
        }
      };
    } catch (error) {
      console.error(`Error al obtener datos demográficos para ${platform}:`, error);
      return null;
    }
  }
}