import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Label } from '@/components/ui/label';

export default function CreateAd() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-primary mb-6">Crear Anuncio</h1>
      
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
          
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-secondary mb-4">Plataformas</h3>
            <p className="text-sm text-muted-foreground mb-3">Selecciona al menos 3 plataformas para publicar tu anuncio</p>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              <div className="flex items-center space-x-2">
                <Checkbox id="meta" defaultChecked />
                <Label htmlFor="meta" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Meta (Facebook/Instagram)</Label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox id="x" defaultChecked />
                <Label htmlFor="x" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">X (Twitter)</Label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox id="google" defaultChecked />
                <Label htmlFor="google" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Google Ads</Label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox id="tiktok" />
                <Label htmlFor="tiktok" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">TikTok</Label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox id="snapchat" />
                <Label htmlFor="snapchat" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Snapchat</Label>
              </div>
            </div>
          </div>
        
        </CardContent>
        <CardFooter className="flex justify-end space-x-3 border-t pt-6">
          <Button variant="outline" className="border-secondary text-secondary hover:bg-secondary/10">Guardar Borrador</Button>
          <Button variant="secondary" className="bg-secondary text-white hover:bg-secondary/90">Vista Previa</Button>
          <Button className="bg-primary text-white hover:bg-primary/90">Publicar Anuncio</Button>
        </CardFooter>
      </Card>
    </div>
  );
}
