'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  SocialPlatform 
} from '@/lib/api-integrations';
import { 
  PlatformPerformance,
  AggregatedPerformance,
  PerformanceByPeriod,
  DemographicData,
  PerformanceMetrics
} from '@/lib/api-integrations/analytics-service';

// Para demo - normalmente obtendríamos datos reales
const DEMO_DATA = {
  platforms: ['meta', 'google', 'x', 'tiktok', 'snapchat'] as SocialPlatform[],
  performanceData: [
    {
      platform: 'meta' as SocialPlatform,
      adId: 'meta-123',
      adName: 'Desarrollador Frontend - Meta',
      metrics: {
        impressions: 25000,
        clicks: 2500,
        ctr: 10,
        conversions: 125,
        costPerClick: 0.45,
        costPerConversion: 9,
        spend: 1125,
        reach: 20000,
        frequency: 1.25
      },
      period: {
        from: '2023-11-01',
        to: '2023-11-30'
      }
    },
    {
      platform: 'google' as SocialPlatform,
      adId: 'google-456',
      adName: 'Desarrollador Frontend - Google',
      metrics: {
        impressions: 15000,
        clicks: 1800,
        ctr: 12,
        conversions: 90,
        costPerClick: 0.55,
        costPerConversion: 11,
        spend: 990,
      },
      period: {
        from: '2023-11-01',
        to: '2023-11-30'
      }
    },
    {
      platform: 'x' as SocialPlatform,
      adId: 'x-789',
      adName: 'Diseñador UX/UI - X',
      metrics: {
        impressions: 8000,
        clicks: 700,
        ctr: 8.75,
        conversions: 32,
        costPerClick: 0.60,
        costPerConversion: 13.1,
        spend: 420,
      },
      period: {
        from: '2023-11-01',
        to: '2023-11-30'
      }
    },
    {
      platform: 'tiktok' as SocialPlatform,
      adId: 'tiktok-101112',
      adName: 'Product Manager - TikTok',
      metrics: {
        impressions: 12000,
        clicks: 1200,
        ctr: 10,
        conversions: 28,
        costPerClick: 0.40,
        costPerConversion: 17.1,
        spend: 480,
        videoViews: 8500
      },
      period: {
        from: '2023-11-01',
        to: '2023-11-30'
      }
    },
    {
      platform: 'snapchat' as SocialPlatform,
      adId: 'snapchat-131415',
      adName: 'Marketing Digital - Snapchat',
      metrics: {
        impressions: 6000,
        clicks: 520,
        ctr: 8.67,
        conversions: 22,
        costPerClick: 0.50,
        costPerConversion: 11.8,
        spend: 260,
      },
      period: {
        from: '2023-11-01',
        to: '2023-11-30'
      }
    },
  ] as PlatformPerformance[],
  performanceByPeriod: [
    { period: '2023-01', impressions: 12000, clicks: 960, conversions: 24, spend: 240 },
    { period: '2023-02', impressions: 16000, clicks: 1400, conversions: 32, spend: 320 },
    { period: '2023-03', impressions: 14000, clicks: 1120, conversions: 28, spend: 280 },
    { period: '2023-04', impressions: 20000, clicks: 1800, conversions: 40, spend: 400 },
    { period: '2023-05', impressions: 18000, clicks: 1620, conversions: 36, spend: 360 },
    { period: '2023-06', impressions: 22000, clicks: 2000, conversions: 44, spend: 440 },
    { period: '2023-07', impressions: 25000, clicks: 2350, conversions: 48, spend: 480 },
    { period: '2023-08', impressions: 27000, clicks: 2700, conversions: 52, spend: 520 },
    { period: '2023-09', impressions: 30000, clicks: 3100, conversions: 56, spend: 560 },
    { period: '2023-10', impressions: 25000, clicks: 2500, conversions: 48, spend: 480 },
    { period: '2023-11', impressions: 28000, clicks: 2800, conversions: 52, spend: 520 },
    { period: '2023-12', impressions: 32000, clicks: 3400, conversions: 60, spend: 600 },
  ] as PerformanceByPeriod[],
  demographicData: {
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
  } as DemographicData
};

// Colores para diferentes plataformas
const platformColors: Record<SocialPlatform, string> = {
  meta: 'bg-blue-500',
  google: 'bg-red-500',
  x: 'bg-slate-800',
  tiktok: 'bg-rose-600',
  snapchat: 'bg-yellow-400'
};

export default function Analytics() {
  const [, setSelectedPeriod] = useState<string>('30');
  const [, setSelectedAd] = useState<string>('all');
  const [timeframeView, setTimeframeView] = useState<'daily' | 'weekly' | 'monthly'>('monthly');
  const [selectedPlatform, setSelectedPlatform] = useState<string>('all');
  
  // En un caso real, estos datos vendrían de la API
  const [performanceData] = useState<PlatformPerformance[]>(DEMO_DATA.performanceData);
  const [aggregatedData, setAggregatedData] = useState<AggregatedPerformance | null>(null);
  const [demographicData] = useState<DemographicData | null>(DEMO_DATA.demographicData);
  const [timeSeriesData] = useState<PerformanceByPeriod[]>(DEMO_DATA.performanceByPeriod);
  
  // Inicializar analytics service (en una implementación real, este sería un servicio real)
  useEffect(() => {
    // Crear un servicio simulado para la demo
    const analyticsService = {
      aggregatePerformance: (data: PlatformPerformance[]) => {
        const aggregated: AggregatedPerformance = {
          totalImpressions: data.reduce((acc, curr) => acc + (curr.metrics.impressions || 0), 0),
          totalClicks: data.reduce((acc, curr) => acc + (curr.metrics.clicks || 0), 0),
          averageCtr: data.reduce((acc, curr) => acc + (curr.metrics.ctr || 0), 0) / data.length,
          totalConversions: data.reduce((acc, curr) => acc + (curr.metrics.conversions || 0), 0),
          averageCostPerClick: data.reduce((acc, curr) => acc + (curr.metrics.costPerClick || 0), 0) / data.length,
          averageCostPerConversion: data.reduce((acc, curr) => acc + (curr.metrics.costPerConversion || 0), 0) / data.length,
          totalSpend: data.reduce((acc, curr) => acc + (curr.metrics.spend || 0), 0),
          platformBreakdown: data.reduce((acc, curr) => {
            acc[curr.platform] = { ...curr.metrics };
            return acc;
          }, {} as Record<SocialPlatform, Partial<PerformanceMetrics>>)
        };
        return aggregated;
      }
    };
    
    // Aplicar filtros de plataforma
    const filteredData = selectedPlatform === 'all' 
      ? performanceData 
      : performanceData.filter(data => data.platform === selectedPlatform);
      
    // Calcular métricas agregadas
    const aggregated = analyticsService.aggregatePerformance(filteredData);
    setAggregatedData(aggregated);
  }, [performanceData, selectedPlatform]);

  // Formats
  const formatNumber = (num: number): string => {
    return num.toLocaleString('es-ES');
  };
  
  const formatCurrency = (num: number): string => {
    return num.toLocaleString('es-ES', { style: 'currency', currency: 'EUR', minimumFractionDigits: 2 });
  };
  
  const formatPercentage = (num: number): string => {
    return `${num.toFixed(2)}%`;
  };

  // Calcular el porcentaje para barras de progreso
  const calculatePercentage = (value: number, max: number): number => {
    return Math.min(100, Math.max(0, (value / max) * 100));
  };
  
  // Clasificar ads por un metric específico
  const getTopPerformingAds = (metric: keyof typeof performanceData[0]['metrics'] = 'conversions'): PlatformPerformance[] => {
    return [...performanceData].sort((a, b) => (b.metrics[metric] || 0) - (a.metrics[metric] || 0)).slice(0, 5);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-primary mb-2">Analíticas Unificadas</h1>
      <p className="text-muted-foreground mb-6">Métricas de rendimiento de anuncios en todas las plataformas</p>
      
      <Tabs defaultValue="overview" className="mb-8">
        <TabsList className="mb-4">
          <TabsTrigger value="overview">Vista General</TabsTrigger>
          <TabsTrigger value="platforms">Por Plataforma</TabsTrigger>
          <TabsTrigger value="campaigns">Por Campaña</TabsTrigger>
          <TabsTrigger value="demographics">Demografía</TabsTrigger>
        </TabsList>
        
        <div className="mb-4 flex justify-end">
          <Select defaultValue="all" onValueChange={setSelectedPlatform}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Filtrar por plataforma" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas las plataformas</SelectItem>
              {DEMO_DATA.platforms.map(platform => (
                <SelectItem key={platform} value={platform}>{
                  platform.charAt(0).toUpperCase() + platform.slice(1)
                }</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <TabsContent value="overview">
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="border-border shadow-md">
              <CardContent className="pt-6">
                <h2 className="text-sm font-medium text-muted-foreground mb-1">Impresiones Totales</h2>
                <p className="text-3xl font-bold text-secondary">
                  {aggregatedData ? formatNumber(aggregatedData.totalImpressions) : '0'}
                </p>
                <div className="flex items-center mt-2">
                  <span className="text-green-500 text-sm font-medium">+12.5%</span>
                  <span className="text-xs text-muted-foreground ml-1">vs mes anterior</span>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-border shadow-md">
              <CardContent className="pt-6">
                <h2 className="text-sm font-medium text-muted-foreground mb-1">Clics</h2>
                <p className="text-3xl font-bold text-secondary">
                  {aggregatedData ? formatNumber(aggregatedData.totalClicks) : '0'}
                </p>
                <div className="flex items-center mt-2">
                  <span className="text-green-500 text-sm font-medium">+8.2%</span>
                  <span className="text-xs text-muted-foreground ml-1">vs mes anterior</span>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-border shadow-md">
              <CardContent className="pt-6">
                <h2 className="text-sm font-medium text-muted-foreground mb-1">Conversiones</h2>
                <p className="text-3xl font-bold text-secondary">
                  {aggregatedData ? formatNumber(aggregatedData.totalConversions) : '0'}
                </p>
                <div className="flex items-center mt-2">
                  <span className="text-green-500 text-sm font-medium">+24.3%</span>
                  <span className="text-xs text-muted-foreground ml-1">vs mes anterior</span>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-border shadow-md">
              <CardContent className="pt-6">
                <h2 className="text-sm font-medium text-muted-foreground mb-1">Gasto Total</h2>
                <p className="text-3xl font-bold text-secondary">
                  {aggregatedData ? formatCurrency(aggregatedData.totalSpend) : '€0.00'}
                </p>
                <div className="flex items-center mt-2">
                  <span className="text-green-500 text-sm font-medium">-5.7%</span>
                  <span className="text-xs text-muted-foreground ml-1">vs mes anterior</span>
                </div>
              </CardContent>
            </Card>
          </div>
          
          {/* Secondary KPIs */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card className="border-border shadow-md">
              <CardContent className="pt-6">
                <h2 className="text-sm font-medium text-muted-foreground mb-1">CTR Promedio</h2>
                <p className="text-3xl font-bold text-secondary">
                  {aggregatedData ? formatPercentage(aggregatedData.averageCtr) : '0%'}
                </p>
                <div className="flex items-center mt-2">
                  <span className="text-green-500 text-sm font-medium">+1.2%</span>
                  <span className="text-xs text-muted-foreground ml-1">vs mes anterior</span>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-border shadow-md">
              <CardContent className="pt-6">
                <h2 className="text-sm font-medium text-muted-foreground mb-1">Costo por Clic</h2>
                <p className="text-3xl font-bold text-secondary">
                  {aggregatedData ? formatCurrency(aggregatedData.averageCostPerClick) : '€0.00'}
                </p>
                <div className="flex items-center mt-2">
                  <span className="text-red-500 text-sm font-medium">+3.5%</span>
                  <span className="text-xs text-muted-foreground ml-1">vs mes anterior</span>
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-border shadow-md">
              <CardContent className="pt-6">
                <h2 className="text-sm font-medium text-muted-foreground mb-1">Costo por Conversión</h2>
                <p className="text-3xl font-bold text-secondary">
                  {aggregatedData ? formatCurrency(aggregatedData.averageCostPerConversion) : '€0.00'}
                </p>
                <div className="flex items-center mt-2">
                  <span className="text-green-500 text-sm font-medium">-8.7%</span>
                  <span className="text-xs text-muted-foreground ml-1">vs mes anterior</span>
                </div>
              </CardContent>
            </Card>
          </div>
          
          {/* Platform Performance Breakdown */}
          <Card className="border-border shadow-md mb-8">
            <CardHeader className="pb-2">
              <div className="flex justify-between items-center">
                <CardTitle className="text-xl font-semibold text-secondary">Rendimiento por Plataforma</CardTitle>
                <Select defaultValue="impressions">
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Seleccionar métrica" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="impressions">Impresiones</SelectItem>
                    <SelectItem value="clicks">Clics</SelectItem>
                    <SelectItem value="conversions">Conversiones</SelectItem>
                    <SelectItem value="spend">Gasto</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {aggregatedData && Object.entries(aggregatedData.platformBreakdown).map(([platform, metrics]) => {
                  const maxImpressions = Object.values(aggregatedData.platformBreakdown)
                    .reduce((max, curr) => Math.max(max, curr.impressions || 0), 0);
                  
                  return (
                    <div key={platform}>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">{platform.charAt(0).toUpperCase() + platform.slice(1)}</span>
                        <span className="text-sm font-medium">{formatNumber(metrics.impressions || 0)} impresiones</span>
                      </div>
                      <div className="w-full bg-secondary/10 rounded-full h-2.5">
                        <div 
                          className={`${platformColors[platform as SocialPlatform]} h-2.5 rounded-full`} 
                          style={{ width: `${calculatePercentage(metrics.impressions || 0, maxImpressions)}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
          
          {/* Trend Chart */}
          <Card className="border-border shadow-md mb-8">
            <CardHeader className="pb-2">
              <div className="flex justify-between items-center">
                <CardTitle className="text-xl font-semibold text-secondary">Tendencia de Conversiones</CardTitle>
                <div className="flex space-x-2">
                  <Button 
                    variant={timeframeView === 'daily' ? 'secondary' : 'outline'} 
                    size="sm"
                    onClick={() => setTimeframeView('daily')}
                  >
                    Diario
                  </Button>
                  <Button 
                    variant={timeframeView === 'weekly' ? 'secondary' : 'outline'} 
                    size="sm"
                    onClick={() => setTimeframeView('weekly')}
                  >
                    Semanal
                  </Button>
                  <Button 
                    variant={timeframeView === 'monthly' ? 'secondary' : 'outline'} 
                    size="sm"
                    onClick={() => setTimeframeView('monthly')}
                  >
                    Mensual
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-end space-x-2">
                {timeSeriesData.map((data, index) => {
                  // Encontrar el máximo valor para normalizar las alturas
                  const maxValue = timeSeriesData.reduce((max, curr) => Math.max(max, curr.conversions), 0);
                  const height = calculatePercentage(data.conversions, maxValue);
                  
                  // Extraer mes o etiqueta del periodo
                  const label = data.period.substring(5, 7);
                  const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
                  const monthLabel = months[parseInt(label) - 1];
                  
                  return (
                    <div key={index} className="flex-1 flex flex-col justify-end">
                      <div 
                        className={`${index === timeSeriesData.length - 1 ? 'bg-secondary' : 'bg-primary'} rounded-t`} 
                        style={{ height: `${height}%` }}
                      ></div>
                      <span className="text-xs text-center mt-1">{monthLabel}</span>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="platforms">
          <div className="grid grid-cols-1 gap-6 mb-8">
            {DEMO_DATA.platforms.map(platform => {
              // Filtrar datos de la plataforma actual
              const platformData = performanceData.filter(data => data.platform === platform);
              if (platformData.length === 0) return null;
              
              const platformMetrics = platformData.reduce((acc, curr) => {
                Object.entries(curr.metrics).forEach(([key, value]) => {
                  if (typeof value === 'number') {
                    acc[key] = (acc[key] || 0) + value;
                  }
                });
                return acc;
              }, {} as Record<string, number>);
              
              return (
                <Card key={platform} className="border-border shadow-md">
                  <CardHeader>
                    <CardTitle className="flex items-center text-xl font-semibold">
                      <div className={`w-4 h-4 rounded-full ${platformColors[platform]} mr-2`}></div>
                      {platform.charAt(0).toUpperCase() + platform.slice(1)}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
                      <div className="space-y-1">
                        <p className="text-sm text-muted-foreground">Impresiones</p>
                        <p className="text-2xl font-bold">{formatNumber(platformMetrics.impressions || 0)}</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-sm text-muted-foreground">Clics</p>
                        <p className="text-2xl font-bold">{formatNumber(platformMetrics.clicks || 0)}</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-sm text-muted-foreground">CTR</p>
                        <p className="text-2xl font-bold">{formatPercentage(platformMetrics.ctr || 0)}</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-sm text-muted-foreground">Conversiones</p>
                        <p className="text-2xl font-bold">{formatNumber(platformMetrics.conversions || 0)}</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-sm text-muted-foreground">Costo por Clic</p>
                        <p className="text-2xl font-bold">{formatCurrency(platformMetrics.costPerClick || 0)}</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-sm text-muted-foreground">Costo por Conversión</p>
                        <p className="text-2xl font-bold">{formatCurrency(platformMetrics.costPerConversion || 0)}</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-sm text-muted-foreground">Gasto Total</p>
                        <p className="text-2xl font-bold">{formatCurrency(platformMetrics.spend || 0)}</p>
                      </div>
                      {platform === 'meta' && (
                        <div className="space-y-1">
                          <p className="text-sm text-muted-foreground">Alcance</p>
                          <p className="text-2xl font-bold">{formatNumber(platformMetrics.reach || 0)}</p>
                        </div>
                      )}
                      {platform === 'tiktok' && (
                        <div className="space-y-1">
                          <p className="text-sm text-muted-foreground">Vistas de Video</p>
                          <p className="text-2xl font-bold">{formatNumber(platformMetrics.videoViews || 0)}</p>
                        </div>
                      )}
                    </div>
                    
                    <div className="mt-6">
                      <h3 className="text-md font-medium mb-3">Anuncios Activos</h3>
                      <div className="space-y-3">
                        {platformData.map(ad => (
                          <div key={ad.adId} className="p-3 border rounded-md">
                            <p className="font-medium text-secondary mb-2">{ad.adName}</p>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                              <div className="flex justify-between">
                                <span className="text-xs text-muted-foreground">Conversiones</span>
                                <span className="text-xs font-medium">{ad.metrics.conversions}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-xs text-muted-foreground">CPC</span>
                                <span className="text-xs font-medium">{formatCurrency(ad.metrics.costPerClick || 0)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-xs text-muted-foreground">Gasto</span>
                                <span className="text-xs font-medium">{formatCurrency(ad.metrics.spend || 0)}</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>
        
        <TabsContent value="campaigns">
          <div className="mb-6">
            <Card className="border-border shadow-md">
              <CardHeader className="pb-2">
                <div className="flex justify-between items-center">
                  <CardTitle className="text-xl font-semibold text-secondary">Rendimiento por Anuncio</CardTitle>
                  <Select defaultValue="30" onValueChange={setSelectedPeriod}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Seleccionar período" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="30">Últimos 30 días</SelectItem>
                      <SelectItem value="60">Últimos 60 días</SelectItem>
                      <SelectItem value="90">Últimos 90 días</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {getTopPerformingAds().map(ad => {
                    const maxConversions = getTopPerformingAds()[0].metrics.conversions || 1;
                    
                    return (
                      <div key={ad.adId}>
                        <div className="flex justify-between mb-1">
                          <div className="flex items-center">
                            <div className={`w-3 h-3 rounded-full ${platformColors[ad.platform]} mr-2`}></div>
                            <span className="text-sm font-medium">{ad.adName}</span>
                          </div>
                          <span className="text-sm font-medium">{ad.metrics.conversions} conversiones</span>
                        </div>
                        <div className="w-full bg-secondary/10 rounded-full h-2.5">
                          <div 
                            className={`${platformColors[ad.platform]} h-2.5 rounded-full`} 
                            style={{ width: `${calculatePercentage(ad.metrics.conversions || 0, maxConversions)}%` }}
                          ></div>
                        </div>
                        <div className="mt-1 grid grid-cols-3 gap-2">
                          <div className="flex justify-between">
                            <span className="text-xs text-muted-foreground">CTR</span>
                            <span className="text-xs">{formatPercentage(ad.metrics.ctr || 0)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-xs text-muted-foreground">CPC</span>
                            <span className="text-xs">{formatCurrency(ad.metrics.costPerClick || 0)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-xs text-muted-foreground">Gasto</span>
                            <span className="text-xs">{formatCurrency(ad.metrics.spend || 0)}</span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <Card className="border-border shadow-md">
              <CardHeader className="pb-2">
                <CardTitle className="text-xl font-semibold text-secondary">Mejores CTR</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {getTopPerformingAds('ctr').map(ad => {
                    const maxCtr = getTopPerformingAds('ctr')[0].metrics.ctr || 1;
                    
                    return (
                      <div key={ad.adId}>
                        <div className="flex justify-between mb-1">
                          <div className="flex items-center">
                            <div className={`w-3 h-3 rounded-full ${platformColors[ad.platform]} mr-2`}></div>
                            <span className="text-sm font-medium">{ad.adName}</span>
                          </div>
                          <span className="text-sm font-medium">{formatPercentage(ad.metrics.ctr || 0)}</span>
                        </div>
                        <div className="w-full bg-secondary/10 rounded-full h-2.5">
                          <div 
                            className={`${platformColors[ad.platform]} h-2.5 rounded-full`} 
                            style={{ width: `${calculatePercentage(ad.metrics.ctr || 0, maxCtr)}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-border shadow-md">
              <CardHeader className="pb-2">
                <CardTitle className="text-xl font-semibold text-secondary">Menor Costo por Conversión</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {getTopPerformingAds('costPerConversion').sort((a, b) => 
                    (a.metrics.costPerConversion || 0) - (b.metrics.costPerConversion || 0)
                  ).slice(0, 5).map(ad => {
                    // Calculate normalized percentage based on max CPA
                    // Note: We could also use the lowest CPA for scaling but not needed now
                    const maxCpa = getTopPerformingAds('costPerConversion')
                      .sort((a, b) => (a.metrics.costPerConversion || 0) - (b.metrics.costPerConversion || 0))[4]
                      .metrics.costPerConversion || 1;
                    const normalizedPercentage = 100 - calculatePercentage(ad.metrics.costPerConversion || 0, maxCpa);
                    
                    return (
                      <div key={ad.adId}>
                        <div className="flex justify-between mb-1">
                          <div className="flex items-center">
                            <div className={`w-3 h-3 rounded-full ${platformColors[ad.platform]} mr-2`}></div>
                            <span className="text-sm font-medium">{ad.adName}</span>
                          </div>
                          <span className="text-sm font-medium">{formatCurrency(ad.metrics.costPerConversion || 0)}</span>
                        </div>
                        <div className="w-full bg-secondary/10 rounded-full h-2.5">
                          <div 
                            className={`${platformColors[ad.platform]} h-2.5 rounded-full`} 
                            style={{ width: `${normalizedPercentage}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        
        <TabsContent value="demographics">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <Card className="border-border shadow-md">
              <CardHeader className="pb-2">
                <div className="flex justify-between items-center">
                  <CardTitle className="text-xl font-semibold text-secondary">Distribución Demográfica</CardTitle>
                  <Select defaultValue="all" onValueChange={setSelectedAd}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Seleccionar anuncio" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todos los anuncios</SelectItem>
                      {performanceData.map(ad => (
                        <SelectItem key={ad.adId} value={ad.adId}>{ad.adName}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </CardHeader>
              <CardContent>
                {demographicData && (
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground mb-3 text-center">Género</h3>
                      <div className="relative pt-1">
                        <div className="flex mb-2 items-center justify-between">
                          <div>
                            <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-primary bg-primary/20">
                              Masculino
                            </span>
                          </div>
                          <div className="text-right">
                            <span className="text-xs font-semibold inline-block text-primary">
                              {demographicData.gender.male}%
                            </span>
                          </div>
                        </div>
                        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-primary/20">
                          <div 
                            style={{ width: `${demographicData.gender.male}%` }} 
                            className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-primary"
                          ></div>
                        </div>
                        
                        <div className="flex mb-2 items-center justify-between">
                          <div>
                            <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-secondary bg-secondary/20">
                              Femenino
                            </span>
                          </div>
                          <div className="text-right">
                            <span className="text-xs font-semibold inline-block text-secondary">
                              {demographicData.gender.female}%
                            </span>
                          </div>
                        </div>
                        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-secondary/20">
                          <div 
                            style={{ width: `${demographicData.gender.female}%` }} 
                            className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-secondary"
                          ></div>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground mb-3 text-center">Edad</h3>
                      <div className="space-y-2">
                        {Object.entries(demographicData.age).map(([ageRange, percentage]) => (
                          <div key={ageRange} className="flex items-center">
                            <span className="text-xs w-12">{ageRange}</span>
                            <div className="flex-1 mx-2 h-2 bg-muted rounded-full">
                              <div 
                                className="h-2 bg-blue-500 rounded-full" 
                                style={{ width: `${percentage}%` }}
                              ></div>
                            </div>
                            <span className="text-xs w-8 text-right">{percentage}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
            
            <Card className="border-border shadow-md">
              <CardHeader className="pb-2">
                <CardTitle className="text-xl font-semibold text-secondary">Distribución Geográfica</CardTitle>
              </CardHeader>
              <CardContent>
                {demographicData && (
                  <div className="space-y-4">
                    <h3 className="text-sm font-medium text-muted-foreground mb-3 text-center">Ubicaciones Principales</h3>
                    {Object.entries(demographicData.locations).map(([location, percentage]) => (
                      <div key={location}>
                        <div className="flex justify-between mb-1">
                          <span className="text-sm font-medium">{location}</span>
                          <span className="text-sm font-medium">{percentage}%</span>
                        </div>
                        <div className="w-full bg-secondary/10 rounded-full h-2.5">
                          <div 
                            className="bg-green-500 h-2.5 rounded-full" 
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
