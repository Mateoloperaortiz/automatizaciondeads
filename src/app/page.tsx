'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function Home() {
  // Using defaultValue in the Tabs component instead
  const [activeTab] = useState('overview');

  // Simulated data that would normally come from API
  const metricsData = {
    totalCampaigns: 26,
    activeCampaigns: 12,
    totalApplications: 248,
    costPerApplication: 12.40,
    conversionRate: 3.2,
    campaignPerformance: {
      facebook: { impressions: 25000, clicks: 2800, applications: 82 },
      linkedin: { impressions: 18000, clicks: 3200, applications: 92 },
      instagram: { impressions: 12000, clicks: 1500, applications: 45 },
      google: { impressions: 10000, clicks: 1200, applications: 29 }
    },
    recentCampaigns: [
      { id: 1, title: 'Desarrollador Frontend', platform: 'LinkedIn, Facebook', status: 'active', applications: 45 },
      { id: 2, title: 'Diseñador UX/UI', platform: 'Instagram, LinkedIn', status: 'active', applications: 32 },
      { id: 3, title: 'Desarrollador Backend', platform: 'LinkedIn', status: 'pending', applications: 0 }
    ]
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      {/* Hero Section */}
      <section className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-primary to-secondary opacity-90"></div>
        <div className="container mx-auto px-4 py-20 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl font-bold text-white mb-6">
              Automatización de <span className="text-white drop-shadow-md">Anuncios</span> para Reclutamiento
            </h1>
            <p className="text-xl text-white/90 mb-10">
              Crea, gestiona y optimiza anuncios de empleo en múltiples plataformas desde un único lugar
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" asChild className="bg-white text-primary hover:bg-white/90">
                <Link href="/create">Crear Anuncio</Link>
              </Button>
              <Button size="lg" variant="outline" asChild className="bg-transparent text-white border-white hover:bg-white/10">
                <Link href="/dashboard">Ver Dashboard</Link>
              </Button>
            </div>
          </div>
        </div>
        
        {/* Stat cards floating over the hero section */}
        <div className="container mx-auto px-4 relative -mb-16 z-20">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-white border-none shadow-lg">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="bg-primary/10 p-3 rounded-lg">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                      <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Campañas Totales</p>
                    <h4 className="text-2xl font-bold">{metricsData.totalCampaigns}</h4>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white border-none shadow-lg">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="bg-green-100 p-3 rounded-lg">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-green-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                      <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Campañas Activas</p>
                    <h4 className="text-2xl font-bold">{metricsData.activeCampaigns}</h4>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white border-none shadow-lg">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="bg-blue-100 p-3 rounded-lg">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                      <circle cx="9" cy="7" r="4"></circle>
                      <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                      <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Aplicaciones</p>
                    <h4 className="text-2xl font-bold">{metricsData.totalApplications}</h4>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white border-none shadow-lg">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="bg-yellow-100 p-3 rounded-lg">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-yellow-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10"></circle>
                      <line x1="12" y1="8" x2="12" y2="12"></line>
                      <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Costo por Aplicación</p>
                    <h4 className="text-2xl font-bold">${metricsData.costPerApplication.toFixed(2)}</h4>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="container mx-auto px-4 py-20 mt-6">
        <Tabs defaultValue="overview" className="w-full">
          <div className="flex justify-between items-center mb-6">
            <TabsList className="grid w-full max-w-md grid-cols-3">
              <TabsTrigger value="overview">General</TabsTrigger>
              <TabsTrigger value="campaigns">Campañas</TabsTrigger>
              <TabsTrigger value="platforms">Plataformas</TabsTrigger>
            </TabsList>
            <Button asChild>
              <Link href="/create">Nueva Campaña</Link>
            </Button>
          </div>

          <TabsContent value="overview">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Overview metrics */}
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle>Rendimiento General</CardTitle>
                  <CardDescription>Métricas clave de todas las plataformas</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-80 relative">
                    {/* Simple chart visualization */}
                    <div className="absolute inset-0 flex items-end justify-between gap-2 p-2">
                      <div className="flex flex-col items-center w-1/4">
                        <div className="bg-primary h-40 w-full rounded-t-lg"></div>
                        <span className="text-xs mt-2">Facebook</span>
                      </div>
                      <div className="flex flex-col items-center w-1/4">
                        <div className="bg-blue-500 h-60 w-full rounded-t-lg"></div>
                        <span className="text-xs mt-2">LinkedIn</span>
                      </div>
                      <div className="flex flex-col items-center w-1/4">
                        <div className="bg-pink-500 h-32 w-full rounded-t-lg"></div>
                        <span className="text-xs mt-2">Instagram</span>
                      </div>
                      <div className="flex flex-col items-center w-1/4">
                        <div className="bg-red-500 h-24 w-full rounded-t-lg"></div>
                        <span className="text-xs mt-2">Google</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="border-t px-6 py-4">
                  <p className="text-sm text-muted-foreground">
                    LinkedIn genera más aplicaciones con una tasa de conversión del {metricsData.conversionRate}%
                  </p>
                </CardFooter>
              </Card>

              {/* Performance insights */}
              <Card>
                <CardHeader>
                  <CardTitle>Insights de Rendimiento</CardTitle>
                  <CardDescription>Análisis automático de resultados</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="bg-green-50 p-4 rounded-lg border border-green-100">
                      <div className="flex items-start gap-3">
                        <div className="bg-green-100 p-2 rounded-full">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-green-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"></path>
                            <path d="m9 12 2 2 4-4"></path>
                          </svg>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-green-800">LinkedIn supera otras plataformas</h4>
                          <p className="text-xs text-green-700">28% más aplicaciones que Facebook</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-100">
                      <div className="flex items-start gap-3">
                        <div className="bg-yellow-100 p-2 rounded-full">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-yellow-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                            <line x1="12" y1="9" x2="12" y2="13"></line>
                            <line x1="12" y1="17" x2="12.01" y2="17"></line>
                          </svg>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-yellow-800">Optimización de presupuesto</h4>
                          <p className="text-xs text-yellow-700">Reasignar 20% del presupuesto de Google a LinkedIn</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                      <div className="flex items-start gap-3">
                        <div className="bg-blue-100 p-2 rounded-full">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 16 14"></polyline>
                          </svg>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-blue-800">Mejor hora para publicar</h4>
                          <p className="text-xs text-blue-700">Martes y Jueves entre 10am y 2pm</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="border-t px-6 py-4">
                  <Button variant="outline" size="sm" className="w-full" asChild>
                    <Link href="/analytics">Ver análisis completo</Link>
                  </Button>
                </CardFooter>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="campaigns">
            <Card>
              <CardHeader>
                <CardTitle>Campañas Recientes</CardTitle>
                <CardDescription>Últimas campañas creadas en la plataforma</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="text-xs uppercase bg-slate-50">
                      <tr>
                        <th className="px-6 py-3">Título</th>
                        <th className="px-6 py-3">Plataforma</th>
                        <th className="px-6 py-3">Estado</th>
                        <th className="px-6 py-3">Aplicaciones</th>
                        <th className="px-6 py-3 text-right">Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {metricsData.recentCampaigns.map(campaign => (
                        <tr key={campaign.id} className="border-b">
                          <td className="px-6 py-4 font-medium">{campaign.title}</td>
                          <td className="px-6 py-4">{campaign.platform}</td>
                          <td className="px-6 py-4">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              campaign.status === 'active' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {campaign.status === 'active' ? 'Activo' : 'Pendiente'}
                            </span>
                          </td>
                          <td className="px-6 py-4">{campaign.applications}</td>
                          <td className="px-6 py-4 text-right">
                            <Button variant="link" size="sm">
                              Ver detalles
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
              <CardFooter className="border-t px-6 py-4 flex justify-between">
                <p className="text-sm text-muted-foreground">
                  Mostrando {metricsData.recentCampaigns.length} de {metricsData.totalCampaigns} campañas
                </p>
                <Button variant="outline" size="sm" asChild>
                  <Link href="/dashboard">Ver todas</Link>
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>

          <TabsContent value="platforms">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Platform metrics */}
              <Card>
                <CardHeader>
                  <CardTitle>Rendimiento por Plataforma</CardTitle>
                  <CardDescription>Comparativa de métricas clave</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">LinkedIn</span>
                        <span className="text-sm font-medium">{metricsData.campaignPerformance.linkedin.applications} aplicaciones</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2.5">
                        <div className="bg-blue-500 h-2.5 rounded-full" style={{ width: '78%' }}></div>
                      </div>
                    </div>
                    
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">Facebook</span>
                        <span className="text-sm font-medium">{metricsData.campaignPerformance.facebook.applications} aplicaciones</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2.5">
                        <div className="bg-primary h-2.5 rounded-full" style={{ width: '62%' }}></div>
                      </div>
                    </div>
                    
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">Instagram</span>
                        <span className="text-sm font-medium">{metricsData.campaignPerformance.instagram.applications} aplicaciones</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2.5">
                        <div className="bg-pink-500 h-2.5 rounded-full" style={{ width: '45%' }}></div>
                      </div>
                    </div>
                    
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">Google</span>
                        <span className="text-sm font-medium">{metricsData.campaignPerformance.google.applications} aplicaciones</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2.5">
                        <div className="bg-red-500 h-2.5 rounded-full" style={{ width: '32%' }}></div>
                      </div>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="border-t px-6 py-4">
                  <Button variant="outline" size="sm" className="w-full" asChild>
                    <Link href="/analytics">Análisis detallado</Link>
                  </Button>
                </CardFooter>
              </Card>

              {/* Cost efficiency */}
              <Card>
                <CardHeader>
                  <CardTitle>Eficiencia de Costo</CardTitle>
                  <CardDescription>Costo por aplicación por plataforma</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div className="flex items-center">
                      <div className="w-1/4">
                        <span className="text-sm font-medium">LinkedIn</span>
                      </div>
                      <div className="w-2/4 px-2">
                        <div className="w-full bg-slate-100 rounded-full h-2.5">
                          <div className="bg-blue-500 h-2.5 rounded-full" style={{ width: '40%' }}></div>
                        </div>
                      </div>
                      <div className="w-1/4 text-right">
                        <span className="text-sm font-medium">$8.25</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center">
                      <div className="w-1/4">
                        <span className="text-sm font-medium">Facebook</span>
                      </div>
                      <div className="w-2/4 px-2">
                        <div className="w-full bg-slate-100 rounded-full h-2.5">
                          <div className="bg-primary h-2.5 rounded-full" style={{ width: '65%' }}></div>
                        </div>
                      </div>
                      <div className="w-1/4 text-right">
                        <span className="text-sm font-medium">$13.40</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center">
                      <div className="w-1/4">
                        <span className="text-sm font-medium">Instagram</span>
                      </div>
                      <div className="w-2/4 px-2">
                        <div className="w-full bg-slate-100 rounded-full h-2.5">
                          <div className="bg-pink-500 h-2.5 rounded-full" style={{ width: '58%' }}></div>
                        </div>
                      </div>
                      <div className="w-1/4 text-right">
                        <span className="text-sm font-medium">$11.95</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center">
                      <div className="w-1/4">
                        <span className="text-sm font-medium">Google</span>
                      </div>
                      <div className="w-2/4 px-2">
                        <div className="w-full bg-slate-100 rounded-full h-2.5">
                          <div className="bg-red-500 h-2.5 rounded-full" style={{ width: '90%' }}></div>
                        </div>
                      </div>
                      <div className="w-1/4 text-right">
                        <span className="text-sm font-medium">$18.60</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="border-t px-6 py-4">
                  <div className="w-full flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 bg-blue-500 rounded-full"></div>
                      <span className="text-xs text-muted-foreground">LinkedIn es la plataforma más eficiente</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 bg-red-500 rounded-full"></div>
                      <span className="text-xs text-muted-foreground">Google es la menos eficiente</span>
                    </div>
                  </div>
                </CardFooter>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16 bg-white">
        <div className="max-w-4xl mx-auto text-center mb-12">
          <h2 className="text-3xl font-bold text-secondary mb-4">Características Principales</h2>
          <p className="text-lg text-muted-foreground">
            AdsMaster simplifica tu estrategia de reclutamiento con herramientas potentes e intuitivas
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="flex flex-col items-center text-center">
            <div className="bg-primary/10 p-4 rounded-lg mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Creación Unificada</h3>
            <p className="text-muted-foreground">
              Crea anuncios para múltiples plataformas desde una única interfaz, ahorrando tiempo y esfuerzo.
            </p>
          </div>

          <div className="flex flex-col items-center text-center">
            <div className="bg-blue-100 p-4 rounded-lg mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Analíticas Avanzadas</h3>
            <p className="text-muted-foreground">
              Obtén insights detallados y compara el rendimiento entre plataformas para optimizar tus campañas.
            </p>
          </div>

          <div className="flex flex-col items-center text-center">
            <div className="bg-green-100 p-4 rounded-lg mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-green-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Segmentación Precisa</h3>
            <p className="text-muted-foreground">
              Dirige tus anuncios a las audiencias adecuadas con perfiles detallados para cada plataforma.
            </p>
          </div>
        </div>

        <div className="flex justify-center mt-12">
          <Button size="lg" asChild>
            <Link href="/create">Comenzar ahora</Link>
          </Button>
        </div>
      </section>

      {/* Testimonial Section */}
      <section className="bg-secondary py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <svg className="h-10 w-10 text-white/50 mx-auto mb-4" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
              <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
            </svg>
            <blockquote className="text-xl text-white mb-6">
              AdsMaster ha reducido nuestro tiempo de creación de anuncios en un 65% y ha mejorado las métricas de costo por aplicación en un 22%. Una herramienta esencial para cualquier equipo de reclutamiento.
            </blockquote>
            <div className="flex items-center justify-center">
              <div className="w-12 h-12 bg-white rounded-full mr-4"></div>
              <div className="text-left">
                <p className="text-white font-semibold">María González</p>
                <p className="text-white/70 text-sm">Directora de Recursos Humanos, TechCorp</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold mb-4">Comienza a optimizar tu reclutamiento hoy</h2>
          <p className="text-lg text-muted-foreground mb-8">
            Prueba AdsMaster y descubre cómo puedes reducir costos y mejorar los resultados de tus campañas de reclutamiento.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" asChild>
              <Link href="/create">Crear tu primera campaña</Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/dashboard">Explorar el dashboard</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-6 md:mb-0">
              <h3 className="text-2xl font-bold">
                Ads<span className="text-primary">Master</span>
              </h3>
              <p className="text-white/70 mt-2 max-w-md">
                La plataforma de automatización de anuncios que simplifica el reclutamiento 
                en las principales redes sociales y motores de búsqueda.
              </p>
            </div>
            <div>
              <p className="text-white/70 text-sm">
                &copy; {new Date().getFullYear()} AdsMaster. Powered by <a href="https://www.magneto365.com" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Magneto365</a>
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
