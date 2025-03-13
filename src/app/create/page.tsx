"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Label } from '@/components/ui/label';
import { AudienceSegment, SegmentationOptions } from '@/lib/audience-segmentation/types';

export default function CreateAd() {
  const [activeTab, setActiveTab] = useState('info');
  const [selectedPlatforms, setSelectedPlatforms] = useState({
    meta: true,
    x: true,
    google: true,
    tiktok: false,
    snapchat: false
  });
  const [previewPlatform, setPreviewPlatform] = useState('meta');
  const [audienceSegmentation, setAudienceSegmentation] = useState({
    method: 'kmeans',
    ageRange: { min: 18, max: 65 },
    gender: 'all',
    locations: [],
    interests: [],
    behaviors: [],
    educationLevels: [],
    industries: [],
    languages: [],
    deviceTypes: ['mobile', 'desktop', 'tablet'],
    customSegments: []
  });
  
  // Función para manejar cambios en la selección de plataformas
  const handlePlatformChange = (platform: string, checked: boolean) => {
    setSelectedPlatforms(prev => ({
      ...prev,
      [platform]: checked
    }));
  };
  
  // Función para manejar cambios en la segmentación de audiencia
  const handleSegmentationChange = (key: string, value: any) => {
    setAudienceSegmentation(prev => ({
      ...prev,
      [key]: value
    }));
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-primary mb-6">Crear Anuncio</h1>
      
      <Tabs defaultValue="info" onValueChange={setActiveTab} className="mb-8">
        <TabsList className="grid w-full grid-cols-4 mb-6">
          <TabsTrigger value="info">Información</TabsTrigger>
          <TabsTrigger value="platforms">Plataformas</TabsTrigger>
          <TabsTrigger value="audience">Audiencia</TabsTrigger>
          <TabsTrigger value="preview">Vista Previa</TabsTrigger>
        </TabsList>
        
        <TabsContent value="info">
          <Card className="mb-8 border-border shadow-md">
            <CardHeader>
              <CardTitle className="text-xl font-semibold text-secondary">Información del Puesto</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="mb-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="job-title">Título del Puesto</Label>
                    <Input 
                      id="job-title"
                      placeholder="Ej. Desarrollador Frontend"
                      className="focus-visible:ring-primary"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="department">Departamento</Label>
                    <Select>
                      <SelectTrigger id="department" className="focus-visible:ring-primary">
                        <SelectValue placeholder="Selecciona un departamento" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="tech">Tecnología</SelectItem>
                        <SelectItem value="marketing">Marketing</SelectItem>
                        <SelectItem value="sales">Ventas</SelectItem>
                        <SelectItem value="hr">Recursos Humanos</SelectItem>
                        <SelectItem value="finance">Finanzas</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="location">Ubicación</Label>
                    <Input 
                      id="location"
                      placeholder="Ej. Medellín, Colombia"
                      className="focus-visible:ring-primary"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="contract-type">Tipo de Contrato</Label>
                    <Select>
                      <SelectTrigger id="contract-type" className="focus-visible:ring-primary">
                        <SelectValue placeholder="Selecciona un tipo de contrato" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="full-time">Tiempo Completo</SelectItem>
                        <SelectItem value="part-time">Medio Tiempo</SelectItem>
                        <SelectItem value="project">Contrato por Proyecto</SelectItem>
                        <SelectItem value="freelance">Freelance</SelectItem>
                        <SelectItem value="internship">Prácticas</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="md:col-span-2 space-y-2">
                    <Label htmlFor="description">Descripción del Puesto</Label>
                    <Textarea 
                      id="description"
                      rows={4}
                      placeholder="Describe las responsabilidades y requisitos del puesto..."
                      className="focus-visible:ring-primary"
                    />
                  </div>
                </div>
              </div>
              
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-secondary mb-4">Requisitos</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="experience">Experiencia Mínima</Label>
                    <Select>
                      <SelectTrigger id="experience" className="focus-visible:ring-primary">
                        <SelectValue placeholder="Selecciona experiencia requerida" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">Sin experiencia</SelectItem>
                        <SelectItem value="1">1 año</SelectItem>
                        <SelectItem value="2">2 años</SelectItem>
                        <SelectItem value="3-5">3-5 años</SelectItem>
                        <SelectItem value="5+">5+ años</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="education">Nivel Educativo</Label>
                    <Select>
                      <SelectTrigger id="education" className="focus-visible:ring-primary">
                        <SelectValue placeholder="Selecciona nivel educativo" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="high-school">Bachillerato</SelectItem>
                        <SelectItem value="technical">Técnico</SelectItem>
                        <SelectItem value="technology">Tecnólogo</SelectItem>
                        <SelectItem value="undergraduate">Pregrado</SelectItem>
                        <SelectItem value="graduate">Postgrado</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="md:col-span-2 space-y-2">
                    <Label htmlFor="skills">Habilidades Requeridas</Label>
                    <Input 
                      id="skills"
                      placeholder="Ej. React, TypeScript, Diseño UI/UX (separadas por comas)"
                      className="focus-visible:ring-primary"
                    />
                  </div>
                </div>
              </div>
              
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-secondary mb-4">Configuración del Anuncio</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="budget">Presupuesto</Label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <span className="text-muted-foreground">$</span>
                      </div>
                      <Input 
                        id="budget"
                        type="number" 
                        className="pl-7 focus-visible:ring-primary"
                        placeholder="100"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="duration">Duración de la Campaña</Label>
                    <Select>
                      <SelectTrigger id="duration" className="focus-visible:ring-primary">
                        <SelectValue placeholder="Selecciona duración" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="7">7 días</SelectItem>
                        <SelectItem value="14">14 días</SelectItem>
                        <SelectItem value="30">30 días</SelectItem>
                        <SelectItem value="60">60 días</SelectItem>
                        <SelectItem value="90">90 días</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end space-x-3 border-t pt-6">
              <Button variant="outline" className="border-secondary text-secondary hover:bg-secondary/10">Guardar Borrador</Button>
              <Button onClick={() => setActiveTab('platforms')} className="bg-primary text-white hover:bg-primary/90">Siguiente: Plataformas</Button>
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="audience">
          <Card className="mb-8 border-border shadow-md">
            <CardHeader>
              <CardTitle className="text-xl font-semibold text-secondary">Segmentación de Audiencia</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="mb-6">
                <p className="text-sm text-muted-foreground mb-4">Define tu audiencia objetivo para maximizar la efectividad de tu anuncio.</p>
                
                <div className="space-y-6">
                  <div>
                    <h3 className="text-md font-semibold text-secondary mb-3">Método de Segmentación</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="flex items-center space-x-3 rounded-lg border p-4">
                        <input
                          type="radio"
                          id="method-kmeans"
                          name="segmentation-method"
                          className="h-4 w-4 text-primary"
                          checked={audienceSegmentation.method === 'kmeans'}
                          onChange={() => handleSegmentationChange('method', 'kmeans')}
                        />
                        <div className="flex-1 space-y-1">
                          <Label htmlFor="method-kmeans" className="font-medium">K-means</Label>
                          <p className="text-xs text-muted-foreground">Agrupación por similitud de características.</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3 rounded-lg border p-4">
                        <input
                          type="radio"
                          id="method-hierarchical"
                          name="segmentation-method"
                          className="h-4 w-4 text-primary"
                          checked={audienceSegmentation.method === 'hierarchical'}
                          onChange={() => handleSegmentationChange('method', 'hierarchical')}
                        />
                        <div className="flex-1 space-y-1">
                          <Label htmlFor="method-hierarchical" className="font-medium">Jerárquico</Label>
                          <p className="text-xs text-muted-foreground">Segmentación por niveles de similitud.</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3 rounded-lg border p-4">
                        <input
                          type="radio"
                          id="method-dbscan"
                          name="segmentation-method"
                          className="h-4 w-4 text-primary"
                          checked={audienceSegmentation.method === 'dbscan'}
                          onChange={() => handleSegmentationChange('method', 'dbscan')}
                        />
                        <div className="flex-1 space-y-1">
                          <Label htmlFor="method-dbscan" className="font-medium">DBSCAN</Label>
                          <p className="text-xs text-muted-foreground">Identifica grupos de alta densidad.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-md font-semibold text-secondary mb-3">Demografía</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label>Rango de Edad</Label>
                        <div className="flex items-center space-x-4">
                          <div className="flex-1">
                            <Label htmlFor="age-min" className="text-xs text-muted-foreground mb-1">Mínimo</Label>
                            <Input 
                              id="age-min"
                              type="number" 
                              min="18"
                              max="100"
                              value={audienceSegmentation.ageRange.min}
                              onChange={(e) => handleSegmentationChange('ageRange', {
                                ...audienceSegmentation.ageRange,
                                min: parseInt(e.target.value)
                              })}
                              className="focus-visible:ring-primary"
                            />
                          </div>
                          <div className="flex-1">
                            <Label htmlFor="age-max" className="text-xs text-muted-foreground mb-1">Máximo</Label>
                            <Input 
                              id="age-max"
                              type="number" 
                              min="18"
                              max="100"
                              value={audienceSegmentation.ageRange.max}
                              onChange={(e) => handleSegmentationChange('ageRange', {
                                ...audienceSegmentation.ageRange,
                                max: parseInt(e.target.value)
                              })}
                              className="focus-visible:ring-primary"
                            />
                          </div>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Género</Label>
                        <Select 
                          value={audienceSegmentation.gender}
                          onValueChange={(value) => handleSegmentationChange('gender', value)}
                        >
                          <SelectTrigger className="focus-visible:ring-primary">
                            <SelectValue placeholder="Selecciona género" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="all">Todos</SelectItem>
                            <SelectItem value="male">Masculino</SelectItem>
                            <SelectItem value="female">Femenino</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="space-y-2 md:col-span-2">
                        <Label htmlFor="locations">Ubicaciones</Label>
                        <Input 
                          id="locations"
                          placeholder="Ej. Medellín, Bogotá, Cali (separadas por comas)"
                          className="focus-visible:ring-primary"
                        />
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-md font-semibold text-secondary mb-3">Intereses y Comportamientos</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2 md:col-span-2">
                        <Label htmlFor="interests">Intereses</Label>
                        <Input 
                          id="interests"
                          placeholder="Ej. Desarrollo web, Diseño UX, Marketing digital (separados por comas)"
                          className="focus-visible:ring-primary"
                        />
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-md font-semibold text-secondary mb-3">Segmentación Avanzada</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label>Nivel Educativo</Label>
                        <Select>
                          <SelectTrigger className="focus-visible:ring-primary">
                            <SelectValue placeholder="Selecciona nivel educativo" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="any">Cualquiera</SelectItem>
                            <SelectItem value="high-school">Bachillerato</SelectItem>
                            <SelectItem value="technical">Técnico/Tecnólogo</SelectItem>
                            <SelectItem value="undergraduate">Pregrado</SelectItem>
                            <SelectItem value="graduate">Postgrado</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Industria</Label>
                        <Select>
                          <SelectTrigger className="focus-visible:ring-primary">
                            <SelectValue placeholder="Selecciona industria" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="any">Cualquiera</SelectItem>
                            <SelectItem value="tech">Tecnología</SelectItem>
                            <SelectItem value="finance">Finanzas</SelectItem>
                            <SelectItem value="healthcare">Salud</SelectItem>
                            <SelectItem value="education">Educación</SelectItem>
                            <SelectItem value="retail">Comercio</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Dispositivos</Label>
                        <div className="flex flex-wrap gap-2 pt-2">
                          <div className="flex items-center space-x-2">
                            <Checkbox 
                              id="device-mobile"
                              checked={audienceSegmentation.deviceTypes.includes('mobile')}
                            />
                            <Label htmlFor="device-mobile" className="text-sm">Móvil</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Checkbox 
                              id="device-desktop"
                              checked={audienceSegmentation.deviceTypes.includes('desktop')}
                            />
                            <Label htmlFor="device-desktop" className="text-sm">Escritorio</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Checkbox 
                              id="device-tablet"
                              checked={audienceSegmentation.deviceTypes.includes('tablet')}
                            />
                            <Label htmlFor="device-tablet" className="text-sm">Tablet</Label>
                          </div>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Idiomas</Label>
                        <Select>
                          <SelectTrigger className="focus-visible:ring-primary">
                            <SelectValue placeholder="Selecciona idioma" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="es">Español</SelectItem>
                            <SelectItem value="en">Inglés</SelectItem>
                            <SelectItem value="fr">Francés</SelectItem>
                            <SelectItem value="pt">Portugués</SelectItem>
                            <SelectItem value="other">Otro</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-between space-x-3 border-t pt-6">
              <Button variant="outline" onClick={() => setActiveTab('platforms')} className="border-secondary text-secondary hover:bg-secondary/10">Anterior: Plataformas</Button>
              <Button onClick={() => setActiveTab('preview')} className="bg-primary text-white hover:bg-primary/90">Siguiente: Vista Previa</Button>
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="platforms">
          <Card className="mb-8 border-border shadow-md">
            <CardHeader>
              <CardTitle className="text-xl font-semibold text-secondary">Selección de Plataformas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="mb-6">
                <p className="text-sm text-muted-foreground mb-4">Selecciona las plataformas donde deseas publicar tu anuncio. Puedes elegir varias opciones.</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center space-x-3 rounded-lg border p-4">
                    <Checkbox 
                      id="platform-meta"
                      checked={selectedPlatforms.meta}
                      onCheckedChange={(checked) => handlePlatformChange('meta', checked as boolean)}
                    />
                    <div className="flex-1 space-y-1">
                      <Label htmlFor="platform-meta" className="font-medium">Meta (Facebook/Instagram)</Label>
                      <p className="text-xs text-muted-foreground">Ideal para reclutamiento en general, con amplio alcance demográfico.</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3 rounded-lg border p-4">
                    <Checkbox 
                      id="platform-x"
                      checked={selectedPlatforms.x}
                      onCheckedChange={(checked) => handlePlatformChange('x', checked as boolean)}
                    />
                    <div className="flex-1 space-y-1">
                      <Label htmlFor="platform-x" className="font-medium">X (Twitter)</Label>
                      <p className="text-xs text-muted-foreground">Efectivo para roles en tecnología, marketing y comunicaciones.</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3 rounded-lg border p-4">
                    <Checkbox 
                      id="platform-google"
                      checked={selectedPlatforms.google}
                      onCheckedChange={(checked) => handlePlatformChange('google', checked as boolean)}
                    />
                    <div className="flex-1 space-y-1">
                      <Label htmlFor="platform-google" className="font-medium">Google</Label>
                      <p className="text-xs text-muted-foreground">Excelente para búsquedas específicas de empleo y amplio alcance.</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3 rounded-lg border p-4">
                    <Checkbox 
                      id="platform-tiktok"
                      checked={selectedPlatforms.tiktok}
                      onCheckedChange={(checked) => handlePlatformChange('tiktok', checked as boolean)}
                    />
                    <div className="flex-1 space-y-1">
                      <Label htmlFor="platform-tiktok" className="font-medium">TikTok</Label>
                      <p className="text-xs text-muted-foreground">Ideal para atraer talento joven y roles creativos.</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3 rounded-lg border p-4">
                    <Checkbox 
                      id="platform-snapchat"
                      checked={selectedPlatforms.snapchat}
                      onCheckedChange={(checked) => handlePlatformChange('snapchat', checked as boolean)}
                    />
                    <div className="flex-1 space-y-1">
                      <Label htmlFor="platform-snapchat" className="font-medium">Snapchat</Label>
                      <p className="text-xs text-muted-foreground">Enfocado en audiencias jóvenes y roles de primera experiencia.</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 p-4 bg-secondary/5 rounded-lg border border-secondary/20">
                <h3 className="text-lg font-semibold text-secondary mb-2">Recomendaciones de Plataforma</h3>
                <ul className="text-sm list-disc pl-5 space-y-2">
                  <li><span className="font-medium">Meta:</span> Mejor para roles de nivel medio y senior con amplio alcance demográfico.</li>
                  <li><span className="font-medium">X:</span> Ideal para roles técnicos y de tecnología, con buena segmentación profesional.</li>
                  <li><span className="font-medium">Google:</span> Excelente para candidatos que buscan activamente empleo.</li>
                  <li><span className="font-medium">TikTok:</span> Perfecto para atraer talento joven y creativo, especialmente en marketing.</li>
                  <li><span className="font-medium">Snapchat:</span> Orientado a roles de nivel inicial y audiencias más jóvenes.</li>
                </ul>
              </div>
            </CardContent>
            <CardFooter className="flex justify-between space-x-3 border-t pt-6">
              <Button variant="outline" onClick={() => setActiveTab('info')} className="border-secondary text-secondary hover:bg-secondary/10">Anterior: Información</Button>
              <Button onClick={() => setActiveTab('audience')} className="bg-primary text-white hover:bg-primary/90">Siguiente: Audiencia</Button>
            </CardFooter>
          </Card>
        </TabsContent>
        <TabsContent value="preview">
          <Card className="mb-8 border-border shadow-md">
            <CardHeader>
              <CardTitle className="text-xl font-semibold text-secondary">Vista Previa del Anuncio</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="mb-6">
                <p className="text-sm text-muted-foreground mb-4">Visualiza cómo se verá tu anuncio en cada plataforma seleccionada.</p>
                
                <div className="flex flex-wrap gap-2 mb-6">
                  <Button 
                    variant={previewPlatform === 'meta' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setPreviewPlatform('meta')}
                    disabled={!selectedPlatforms.meta}
                    className={previewPlatform === 'meta' ? 'bg-primary text-white' : ''}
                  >
                    Meta
                  </Button>
                  <Button 
                    variant={previewPlatform === 'x' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setPreviewPlatform('x')}
                    disabled={!selectedPlatforms.x}
                    className={previewPlatform === 'x' ? 'bg-primary text-white' : ''}
                  >
                    X
                  </Button>
                  <Button 
                    variant={previewPlatform === 'google' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setPreviewPlatform('google')}
                    disabled={!selectedPlatforms.google}
                    className={previewPlatform === 'google' ? 'bg-primary text-white' : ''}
                  >
                    Google
                  </Button>
                  <Button 
                    variant={previewPlatform === 'tiktok' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setPreviewPlatform('tiktok')}
                    disabled={!selectedPlatforms.tiktok}
                    className={previewPlatform === 'tiktok' ? 'bg-primary text-white' : ''}
                  >
                    TikTok
                  </Button>
                  <Button 
                    variant={previewPlatform === 'snapchat' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setPreviewPlatform('snapchat')}
                    disabled={!selectedPlatforms.snapchat}
                    className={previewPlatform === 'snapchat' ? 'bg-primary text-white' : ''}
                  >
                    Snapchat
                  </Button>
                </div>
                
                {/* Contenedor de vista previa */}
                <div className="border rounded-lg overflow-hidden">
                  {/* Barra de navegación simulada */}
                  <div className="bg-gray-100 p-2 border-b flex items-center">
                    {previewPlatform === 'meta' && (
                      <div className="flex items-center">
                        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold">f</div>
                        <span className="ml-2 text-sm font-medium">Facebook</span>
                      </div>
                    )}
                    {previewPlatform === 'x' && (
                      <div className="flex items-center">
                        <div className="w-8 h-8 rounded-full bg-black flex items-center justify-center text-white font-bold">X</div>
                        <span className="ml-2 text-sm font-medium">X</span>
                      </div>
                    )}
                    {previewPlatform === 'google' && (
                      <div className="flex items-center">
                        <div className="flex">
                          <span className="text-blue-600 font-bold">G</span>
                          <span className="text-red-500 font-bold">o</span>
                          <span className="text-yellow-500 font-bold">o</span>
                          <span className="text-blue-600 font-bold">g</span>
                          <span className="text-green-500 font-bold">l</span>
                          <span className="text-red-500 font-bold">e</span>
                        </div>
                        <span className="ml-2 text-sm font-medium">Jobs</span>
                      </div>
                    )}
                    {previewPlatform === 'tiktok' && (
                      <div className="flex items-center">
                        <div className="w-8 h-8 rounded-full bg-black flex items-center justify-center text-white">
                          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M8.5 3C8.5 2.44772 8.05228 2 7.5 2C6.94772 2 6.5 2.44772 6.5 3H8.5ZM9.53553 3.96447C9.92606 3.57394 9.92606 2.94036 9.53553 2.54984C9.14501 2.15931 8.51142 2.15931 8.1209 2.54984L9.53553 3.96447ZM6.5 3V9.5H8.5V3H6.5ZM6.5 9.5C6.5 10.8807 7.61929 12 9 12V10C8.72386 10 8.5 9.77614 8.5 9.5H6.5ZM9 12C10.3807 12 11.5 10.8807 11.5 9.5H9.5C9.5 9.77614 9.27614 10 9 10V12ZM11.5 9.5V6.5H9.5V9.5H11.5ZM11.5 6.5C11.5 5.11929 10.3807 4 9 4V6C9.27614 6 9.5 6.22386 9.5 6.5H11.5ZM8.1209 2.54984L7.1209 3.54984L8.53553 4.96447L9.53553 3.96447L8.1209 2.54984Z" fill="white"/>
                          </svg>
                        </div>
                        <span className="ml-2 text-sm font-medium">TikTok</span>
                      </div>
                    )}
                    {previewPlatform === 'snapchat' && (
                      <div className="flex items-center">
                        <div className="w-8 h-8 rounded-full bg-yellow-400 flex items-center justify-center">
                          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M8 2C9.65685 2 11 3.34315 11 5V6C11 6.55228 11.4477 7 12 7C12.5523 7 13 6.55228 13 6V5C13 2.23858 10.7614 0 8 0C5.23858 0 3 2.23858 3 5V6C3 6.55228 3.44772 7 4 7C4.55228 7 5 6.55228 5 6V5C5 3.34315 6.34315 2 8 2Z" fill="white"/>
                          </svg>
                        </div>
                        <span className="ml-2 text-sm font-medium">Snapchat</span>
                      </div>
                    )}
                  </div>
                  
                  {/* Contenido de la vista previa */}
                  <div className="p-4">
                    {/* Cabecera del anuncio */}
                    <div className="flex items-start mb-3">
                      <div className="w-10 h-10 rounded-full bg-gray-200 flex-shrink-0"></div>
                      <div className="ml-3">
                        <p className="font-medium">Tu Empresa</p>
                        <p className="text-xs text-gray-500">Anuncio patrocinado</p>
                      </div>
                    </div>
                    
                    {/* Contenido del anuncio */}
                    <div>
                      <h3 className="font-bold text-lg mb-2">Oferta de Empleo: Desarrollador Frontend</h3>
                      <p className="text-sm mb-3">Buscamos un talentoso Desarrollador Frontend para unirse a nuestro equipo en Medellín. Ofrecemos excelentes beneficios y oportunidades de crecimiento.</p>
                      
                      <div className="bg-gray-100 p-3 rounded-md mb-3">
                        <div className="flex items-center mb-2">
                          <svg className="w-5 h-5 text-gray-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                          </svg>
                          <span className="text-sm">Medellín, Colombia</span>
                        </div>
                        <div className="flex items-center mb-2">
                          <svg className="w-5 h-5 text-gray-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                          </svg>
                          <span className="text-sm">Tiempo Completo</span>
                        </div>
                        <div className="flex items-center">
                          <svg className="w-5 h-5 text-gray-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                          </svg>
                          <span className="text-sm">Publicado hace 2 días</span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Botón de llamada a la acción */}
                    <div className="mt-4">
                      <Button className="w-full bg-primary text-white hover:bg-primary/90">
                        {previewPlatform === 'meta' && "Aplicar ahora"}
                        {previewPlatform === 'x' && "Aplicar"}
                        {previewPlatform === 'google' && "Ver oferta de empleo"}
                        {previewPlatform === 'tiktok' && "Desliza hacia arriba"}
                        {previewPlatform === 'snapchat' && "Desliza hacia arriba"}
                      </Button>
                    </div>
                    
                    {/* Estadísticas simuladas */}
                    <div className="mt-4 flex text-xs text-gray-500 justify-between">
                      <span>Alcance estimado: 15.000 - 25.000 personas</span>
                      <span>CPA estimado: $2.50 - $4.00</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 p-4 bg-secondary/5 rounded-lg border border-secondary/20">
                <h3 className="text-lg font-semibold text-secondary mb-2">Recomendaciones de Optimización</h3>
                <ul className="text-sm list-disc pl-5 space-y-2">
                  <li>Añade una imagen de alta calidad relacionada con el puesto para aumentar la tasa de clics.</li>
                  <li>Incluye palabras clave específicas del sector para mejorar la visibilidad.</li>
                  <li>Destaca los beneficios y la cultura de la empresa para atraer a candidatos de calidad.</li>
                  <li>Considera segmentar por habilidades específicas para llegar a candidatos más cualificados.</li>
                </ul>
              </div>
            </CardContent>
            <CardFooter className="flex justify-between space-x-3 border-t pt-6">
              <Button variant="outline" onClick={() => setActiveTab('audience')} className="border-secondary text-secondary hover:bg-secondary/10">Anterior: Audiencia</Button>
              <Button className="bg-primary text-white hover:bg-primary/90">Publicar Anuncio</Button>
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
