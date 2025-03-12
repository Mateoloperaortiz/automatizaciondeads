import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';

export default function Analytics() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-primary mb-6">Analíticas</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="border-border shadow-md">
          <CardContent className="pt-6">
            <h2 className="text-sm font-medium text-muted-foreground mb-1">Impresiones Totales</h2>
            <p className="text-3xl font-bold text-secondary">45,782</p>
            <div className="flex items-center mt-2">
              <span className="text-green-500 text-sm font-medium">+12.5%</span>
              <span className="text-xs text-muted-foreground ml-1">vs mes anterior</span>
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border shadow-md">
          <CardContent className="pt-6">
            <h2 className="text-sm font-medium text-muted-foreground mb-1">Clics</h2>
            <p className="text-3xl font-bold text-secondary">5,347</p>
            <div className="flex items-center mt-2">
              <span className="text-green-500 text-sm font-medium">+8.2%</span>
              <span className="text-xs text-muted-foreground ml-1">vs mes anterior</span>
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border shadow-md">
          <CardContent className="pt-6">
            <h2 className="text-sm font-medium text-muted-foreground mb-1">Aplicaciones</h2>
            <p className="text-3xl font-bold text-secondary">248</p>
            <div className="flex items-center mt-2">
              <span className="text-green-500 text-sm font-medium">+24.3%</span>
              <span className="text-xs text-muted-foreground ml-1">vs mes anterior</span>
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border shadow-md">
          <CardContent className="pt-6">
            <h2 className="text-sm font-medium text-muted-foreground mb-1">Costo por Aplicación</h2>
            <p className="text-3xl font-bold text-secondary">$12.40</p>
            <div className="flex items-center mt-2">
              <span className="text-green-500 text-sm font-medium">-18.7%</span>
              <span className="text-xs text-muted-foreground ml-1">vs mes anterior</span>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card className="border-border shadow-md">
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-xl font-semibold text-secondary">Rendimiento por Anuncio</CardTitle>
              <Select defaultValue="30">
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
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium">Desarrollador Frontend</span>
                  <span className="text-sm font-medium">45 aplicaciones</span>
                </div>
                <div className="w-full bg-secondary/10 rounded-full h-2.5">
                  <div className="bg-primary h-2.5 rounded-full" style={{ width: '85%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium">Diseñador UX/UI</span>
                  <span className="text-sm font-medium">32 aplicaciones</span>
                </div>
                <div className="w-full bg-secondary/10 rounded-full h-2.5">
                  <div className="bg-secondary h-2.5 rounded-full" style={{ width: '65%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium">Product Manager</span>
                  <span className="text-sm font-medium">28 aplicaciones</span>
                </div>
                <div className="w-full bg-secondary/10 rounded-full h-2.5">
                  <div className="bg-blue-500 h-2.5 rounded-full" style={{ width: '55%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium">Marketing Digital</span>
                  <span className="text-sm font-medium">22 aplicaciones</span>
                </div>
                <div className="w-full bg-secondary/10 rounded-full h-2.5">
                  <div className="bg-green-500 h-2.5 rounded-full" style={{ width: '45%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium">Analista de Datos</span>
                  <span className="text-sm font-medium">18 aplicaciones</span>
                </div>
                <div className="w-full bg-secondary/10 rounded-full h-2.5">
                  <div className="bg-yellow-500 h-2.5 rounded-full" style={{ width: '35%' }}></div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border shadow-md">
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-xl font-semibold text-secondary">Distribución Demográfica</CardTitle>
              <Select defaultValue="all">
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Seleccionar anuncio" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los anuncios</SelectItem>
                  <SelectItem value="dev">Desarrollador Frontend</SelectItem>
                  <SelectItem value="design">Diseñador UX/UI</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardHeader>
          <CardContent>
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
                        58%
                      </span>
                    </div>
                  </div>
                  <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-primary/20">
                    <div style={{ width: "58%" }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-primary"></div>
                  </div>
                  
                  <div className="flex mb-2 items-center justify-between">
                    <div>
                      <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-secondary bg-secondary/20">
                        Femenino
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-semibold inline-block text-secondary">
                        42%
                      </span>
                    </div>
                  </div>
                  <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-secondary/20">
                    <div style={{ width: "42%" }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-secondary"></div>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-muted-foreground mb-3 text-center">Edad</h3>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <span className="text-xs w-12">18-24</span>
                    <div className="flex-1 mx-2 h-2 bg-muted rounded-full">
                      <div className="h-2 bg-blue-500 rounded-full" style={{ width: '15%' }}></div>
                    </div>
                    <span className="text-xs w-8 text-right">15%</span>
                  </div>
                  
                  <div className="flex items-center">
                    <span className="text-xs w-12">25-34</span>
                    <div className="flex-1 mx-2 h-2 bg-muted rounded-full">
                      <div className="h-2 bg-blue-500 rounded-full" style={{ width: '42%' }}></div>
                    </div>
                    <span className="text-xs w-8 text-right">42%</span>
                  </div>
                  
                  <div className="flex items-center">
                    <span className="text-xs w-12">35-44</span>
                    <div className="flex-1 mx-2 h-2 bg-muted rounded-full">
                      <div className="h-2 bg-blue-500 rounded-full" style={{ width: '28%' }}></div>
                    </div>
                    <span className="text-xs w-8 text-right">28%</span>
                  </div>
                  
                  <div className="flex items-center">
                    <span className="text-xs w-12">45-54</span>
                    <div className="flex-1 mx-2 h-2 bg-muted rounded-full">
                      <div className="h-2 bg-blue-500 rounded-full" style={{ width: '10%' }}></div>
                    </div>
                    <span className="text-xs w-8 text-right">10%</span>
                  </div>
                  
                  <div className="flex items-center">
                    <span className="text-xs w-12">55+</span>
                    <div className="flex-1 mx-2 h-2 bg-muted rounded-full">
                      <div className="h-2 bg-blue-500 rounded-full" style={{ width: '5%' }}></div>
                    </div>
                    <span className="text-xs w-8 text-right">5%</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <Card className="border-border shadow-md mb-8">
        <CardHeader className="pb-2">
          <div className="flex justify-between items-center">
            <CardTitle className="text-xl font-semibold text-secondary">Tendencia de Aplicaciones</CardTitle>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm">Diario</Button>
              <Button variant="outline" size="sm">Semanal</Button>
              <Button variant="secondary" size="sm">Mensual</Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-end space-x-2">
            <div className="flex-1 flex flex-col justify-end">
              <div className="h-24 bg-primary rounded-t"></div>
              <span className="text-xs text-center mt-1">Ene</span>
            </div>
            <div className="flex-1 flex flex-col justify-end">
              <div className="h-32 bg-primary rounded-t"></div>
              <span className="text-xs text-center mt-1">Feb</span>
            </div>
            <div className="flex-1 flex flex-col justify-end">
              <div className="h-28 bg-primary rounded-t"></div>
              <span className="text-xs text-center mt-1">Mar</span>
            </div>
            <div className="flex-1 flex flex-col justify-end">
              <div className="h-40 bg-primary rounded-t"></div>
              <span className="text-xs text-center mt-1">Abr</span>
            </div>
            <div className="flex-1 flex flex-col justify-end">
              <div className="h-36 bg-primary rounded-t"></div>
              <span className="text-xs text-center mt-1">May</span>
            </div>
            <div className="flex-1 flex flex-col justify-end">
              <div className="h-44 bg-primary rounded-t"></div>
              <span className="text-xs text-center mt-1">Jun</span>
            </div>
            <div className="flex-1 flex flex-col justify-end">
              <div className="h-48 bg-primary rounded-t"></div>
              <span className="text-xs text-center mt-1">Jul</span>
            </div>
            <div className="flex-1 flex flex-col justify-end">
              <div className="h-52 bg-primary rounded-t"></div>
              <span className="text-xs text-center mt-1">Ago</span>
            </div>
            <div className="flex-1 flex flex-col justify-end">
              <div className="h-56 bg-primary rounded-t"></div>
              <span className="text-xs text-center mt-1">Sep</span>
            </div>
            <div className="flex-1 flex flex-col justify-end">
              <div className="h-48 bg-primary rounded-t"></div>
              <span className="text-xs text-center mt-1">Oct</span>
            </div>
            <div className="flex-1 flex flex-col justify-end">
              <div className="h-52 bg-primary rounded-t"></div>
              <span className="text-xs text-center mt-1">Nov</span>
            </div>
            <div className="flex-1 flex flex-col justify-end">
              <div className="h-60 bg-secondary rounded-t"></div>
              <span className="text-xs text-center mt-1">Dic</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
