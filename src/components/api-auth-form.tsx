import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SocialPlatform } from '@/lib/api-integrations/types';

interface ApiCredentials {
  platform: SocialPlatform;
  [key: string]: string | SocialPlatform;
}

interface ApiAuthFormProps {
  onSaveCredentials: (credentials: ApiCredentials) => void;
}

export function ApiAuthForm({ onSaveCredentials }: ApiAuthFormProps) {
  const [activePlatform, setActivePlatform] = useState<SocialPlatform>('meta');
  
  // Credenciales para Meta (Facebook/Instagram)
  const [metaCredentials, setMetaCredentials] = useState({
    clientId: '',
    clientSecret: '',
    accessToken: '',
  });
  
  // Credenciales para X (Twitter)
  const [xCredentials, setXCredentials] = useState({
    apiKey: '',
    apiSecret: '',
    accessToken: '',
    accessTokenSecret: '',
  });
  
  // Credenciales para Google
  const [googleCredentials, setGoogleCredentials] = useState({
    clientId: '',
    clientSecret: '',
    refreshToken: '',
    developerToken: '',
    managerId: '',
  });
  
  // Credenciales para TikTok
  const [tiktokCredentials, setTiktokCredentials] = useState({
    accessToken: '',
    appId: '',
    appSecret: '',
    advertiserId: '',
  });
  
  // Credenciales para Snapchat
  const [snapchatCredentials, setSnapchatCredentials] = useState({
    accessToken: '',
    clientId: '',
    clientSecret: '',
    organizationId: '',
  });

  // Gestionar cambios en los campos de Meta
  const handleMetaChange = (field: string, value: string) => {
    setMetaCredentials((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  // Gestionar cambios en los campos de X
  const handleXChange = (field: string, value: string) => {
    setXCredentials((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  // Gestionar cambios en los campos de Google
  const handleGoogleChange = (field: string, value: string) => {
    setGoogleCredentials((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  // Gestionar cambios en los campos de TikTok
  const handleTikTokChange = (field: string, value: string) => {
    setTiktokCredentials((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  // Gestionar cambios en los campos de Snapchat
  const handleSnapchatChange = (field: string, value: string) => {
    setSnapchatCredentials((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  // Guardar credenciales para la plataforma activa
  const handleSaveCredentials = () => {
    let credentials: ApiCredentials;
    
    switch (activePlatform) {
      case 'meta':
        credentials = {
          platform: 'meta',
          ...metaCredentials,
        };
        break;
      case 'x':
        credentials = {
          platform: 'x',
          ...xCredentials,
        };
        break;
      case 'google':
        credentials = {
          platform: 'google',
          ...googleCredentials,
        };
        break;
      case 'tiktok':
        credentials = {
          platform: 'tiktok',
          ...tiktokCredentials,
        };
        break;
      case 'snapchat':
        credentials = {
          platform: 'snapchat',
          ...snapchatCredentials,
        };
        break;
      default:
        return;
    }
    
    onSaveCredentials(credentials);
  };

  return (
    <Card className="w-full border-border shadow-md">
      <CardHeader>
        <CardTitle className="text-xl font-semibold text-secondary">Configuración de APIs</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="meta" onValueChange={(value) => setActivePlatform(value as SocialPlatform)}>
          <TabsList className="grid w-full grid-cols-5 mb-6">
            <TabsTrigger value="meta">Meta</TabsTrigger>
            <TabsTrigger value="x">X</TabsTrigger>
            <TabsTrigger value="google">Google</TabsTrigger>
            <TabsTrigger value="tiktok">TikTok</TabsTrigger>
            <TabsTrigger value="snapchat">Snapchat</TabsTrigger>
          </TabsList>
          
          {/* Formulario para Meta */}
          <TabsContent value="meta">
            <div className="space-y-6">
              <div className="p-4 bg-secondary/5 rounded-lg border border-secondary/20 mb-4">
                <h3 className="text-md font-semibold text-secondary mb-2">Instrucciones</h3>
                <ol className="text-sm space-y-1 list-decimal pl-4">
                  <li>Crea una aplicación en el <a href="https://developers.facebook.com/" className="text-primary underline" target="_blank" rel="noreferrer">Portal para Desarrolladores de Meta</a></li>
                  <li>Configura los permisos para Ads API</li>
                  <li>Genera un token de acceso para la cuenta de anuncios</li>
                </ol>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="meta-client-id">ID de la Aplicación</Label>
                  <Input 
                    id="meta-client-id"
                    value={metaCredentials.clientId}
                    onChange={(e) => handleMetaChange('clientId', e.target.value)}
                    placeholder="Ej. 123456789012345"
                    className="focus-visible:ring-primary"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="meta-client-secret">Secreto de la Aplicación</Label>
                  <Input 
                    id="meta-client-secret"
                    type="password"
                    value={metaCredentials.clientSecret}
                    onChange={(e) => handleMetaChange('clientSecret', e.target.value)}
                    placeholder="Secreto de la aplicación"
                    className="focus-visible:ring-primary"
                  />
                </div>
                
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="meta-access-token">Token de Acceso</Label>
                  <Input 
                    id="meta-access-token"
                    value={metaCredentials.accessToken}
                    onChange={(e) => handleMetaChange('accessToken', e.target.value)}
                    placeholder="Token de acceso de la cuenta de anuncios"
                    className="focus-visible:ring-primary"
                  />
                </div>
              </div>
            </div>
          </TabsContent>
          
          {/* Formulario para X */}
          <TabsContent value="x">
            <div className="space-y-6">
              <div className="p-4 bg-secondary/5 rounded-lg border border-secondary/20 mb-4">
                <h3 className="text-md font-semibold text-secondary mb-2">Instrucciones</h3>
                <ol className="text-sm space-y-1 list-decimal pl-4">
                  <li>Crea una aplicación en el <a href="https://developer.twitter.com/" className="text-primary underline" target="_blank" rel="noreferrer">Portal para Desarrolladores de X</a></li>
                  <li>Obtén las credenciales de OAuth 1.0a</li>
                  <li>Configura los permisos para la API de Anuncios</li>
                </ol>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="x-api-key">API Key</Label>
                  <Input 
                    id="x-api-key"
                    value={xCredentials.apiKey}
                    onChange={(e) => handleXChange('apiKey', e.target.value)}
                    placeholder="API Key de X"
                    className="focus-visible:ring-primary"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="x-api-secret">API Secret</Label>
                  <Input 
                    id="x-api-secret"
                    type="password"
                    value={xCredentials.apiSecret}
                    onChange={(e) => handleXChange('apiSecret', e.target.value)}
                    placeholder="API Secret de X"
                    className="focus-visible:ring-primary"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="x-access-token">Access Token</Label>
                  <Input 
                    id="x-access-token"
                    value={xCredentials.accessToken}
                    onChange={(e) => handleXChange('accessToken', e.target.value)}
                    placeholder="Access Token de X"
                    className="focus-visible:ring-primary"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="x-access-token-secret">Access Token Secret</Label>
                  <Input 
                    id="x-access-token-secret"
                    type="password"
                    value={xCredentials.accessTokenSecret}
                    onChange={(e) => handleXChange('accessTokenSecret', e.target.value)}
                    placeholder="Access Token Secret de X"
                    className="focus-visible:ring-primary"
                  />
                </div>
              </div>
            </div>
          </TabsContent>
          
          {/* Formulario para Google */}
          <TabsContent value="google">
            <div className="space-y-6">
              <div className="p-4 bg-secondary/5 rounded-lg border border-secondary/20 mb-4">
                <h3 className="text-md font-semibold text-secondary mb-2">Instrucciones</h3>
                <ol className="text-sm space-y-1 list-decimal pl-4">
                  <li>Configura un proyecto en la <a href="https://console.cloud.google.com/" className="text-primary underline" target="_blank" rel="noreferrer">Google Cloud Console</a></li>
                  <li>Habilita la API de Google Ads</li>
                  <li>Crea credenciales OAuth 2.0</li>
                  <li>Genera un refresh token siguiendo el flujo de autorización</li>
                </ol>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="google-client-id">Client ID</Label>
                  <Input 
                    id="google-client-id"
                    value={googleCredentials.clientId}
                    onChange={(e) => handleGoogleChange('clientId', e.target.value)}
                    placeholder="Client ID de OAuth 2.0"
                    className="focus-visible:ring-primary"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="google-client-secret">Client Secret</Label>
                  <Input 
                    id="google-client-secret"
                    type="password"
                    value={googleCredentials.clientSecret}
                    onChange={(e) => handleGoogleChange('clientSecret', e.target.value)}
                    placeholder="Client Secret de OAuth 2.0"
                    className="focus-visible:ring-primary"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="google-refresh-token">Refresh Token</Label>
                  <Input 
                    id="google-refresh-token"
                    value={googleCredentials.refreshToken}
                    onChange={(e) => handleGoogleChange('refreshToken', e.target.value)}
                    placeholder="Refresh Token de OAuth 2.0"
                    className="focus-visible:ring-primary"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="google-developer-token">Developer Token</Label>
                  <Input 
                    id="google-developer-token"
                    type="password"
                    value={googleCredentials.developerToken}
                    onChange={(e) => handleGoogleChange('developerToken', e.target.value)}
                    placeholder="Developer Token de Google Ads"
                    className="focus-visible:ring-primary"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="google-manager-id">ID de Cuenta de Manager</Label>
                  <Input 
                    id="google-manager-id"
                    value={googleCredentials.managerId}
                    onChange={(e) => handleGoogleChange('managerId', e.target.value)}
                    placeholder="ID de la cuenta de Google Ads (opcional)"
                    className="focus-visible:ring-primary"
                  />
                </div>
              </div>
            </div>
          </TabsContent>
          
          {/* Formulario para TikTok */}
          <TabsContent value="tiktok">
            <div className="space-y-6">
              <div className="p-4 bg-secondary/5 rounded-lg border border-secondary/20 mb-4">
                <h3 className="text-md font-semibold text-secondary mb-2">Instrucciones</h3>
                <ol className="text-sm space-y-1 list-decimal pl-4">
                  <li>Regístrate en el <a href="https://ads.tiktok.com/marketing_api/" className="text-primary underline" target="_blank" rel="noreferrer">Portal para Desarrolladores de TikTok</a></li>
                  <li>Crea una aplicación con acceso a la API de Marketing</li>
                  <li>Obtén el token de acceso para tu cuenta de anuncios</li>
                </ol>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="tiktok-app-id">App ID</Label>
                  <Input 
                    id="tiktok-app-id"
                    value={tiktokCredentials.appId}
                    onChange={(e) => handleTikTokChange('appId', e.target.value)}
                    placeholder="App ID de TikTok"
                    className="focus-visible:ring-primary"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="tiktok-app-secret">App Secret</Label>
                  <Input 
                    id="tiktok-app-secret"
                    type="password"
                    value={tiktokCredentials.appSecret}
                    onChange={(e) => handleTikTokChange('appSecret', e.target.value)}
                    placeholder="App Secret de TikTok"
                    className="focus-visible:ring-primary"
                  />
                </div>
                
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="tiktok-access-token">Access Token</Label>
                  <Input 
                    id="tiktok-access-token"
                    value={tiktokCredentials.accessToken}
                    onChange={(e) => handleTikTokChange('accessToken', e.target.value)}
                    placeholder="Access Token de TikTok"
                    className="focus-visible:ring-primary"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="tiktok-advertiser-id">ID de Anunciante</Label>
                  <Input 
                    id="tiktok-advertiser-id"
                    value={tiktokCredentials.advertiserId}
                    onChange={(e) => handleTikTokChange('advertiserId', e.target.value)}
                    placeholder="ID de anunciante (opcional)"
                    className="focus-visible:ring-primary"
                  />
                </div>
              </div>
            </div>
          </TabsContent>
          
          {/* Formulario para Snapchat */}
          <TabsContent value="snapchat">
            <div className="space-y-6">
              <div className="p-4 bg-secondary/5 rounded-lg border border-secondary/20 mb-4">
                <h3 className="text-md font-semibold text-secondary mb-2">Instrucciones</h3>
                <ol className="text-sm space-y-1 list-decimal pl-4">
                  <li>Accede al <a href="https://businesshelp.snapchat.com/s/topic/0TO2o000000Gs4QGAS/marketing-api" className="text-primary underline" target="_blank" rel="noreferrer">Portal de Marketing API de Snapchat</a></li>
                  <li>Crea una aplicación con acceso a la API de Marketing</li>
                  <li>Obtén las credenciales OAuth para tu organización</li>
                </ol>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="snapchat-client-id">Client ID</Label>
                  <Input 
                    id="snapchat-client-id"
                    value={snapchatCredentials.clientId}
                    onChange={(e) => handleSnapchatChange('clientId', e.target.value)}
                    placeholder="Client ID de Snapchat"
                    className="focus-visible:ring-primary"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="snapchat-client-secret">Client Secret</Label>
                  <Input 
                    id="snapchat-client-secret"
                    type="password"
                    value={snapchatCredentials.clientSecret}
                    onChange={(e) => handleSnapchatChange('clientSecret', e.target.value)}
                    placeholder="Client Secret de Snapchat"
                    className="focus-visible:ring-primary"
                  />
                </div>
                
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="snapchat-access-token">Access Token</Label>
                  <Input 
                    id="snapchat-access-token"
                    value={snapchatCredentials.accessToken}
                    onChange={(e) => handleSnapchatChange('accessToken', e.target.value)}
                    placeholder="Access Token de Snapchat"
                    className="focus-visible:ring-primary"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="snapchat-organization-id">ID de Organización</Label>
                  <Input 
                    id="snapchat-organization-id"
                    value={snapchatCredentials.organizationId}
                    onChange={(e) => handleSnapchatChange('organizationId', e.target.value)}
                    placeholder="ID de la organización"
                    className="focus-visible:ring-primary"
                  />
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
      <CardFooter className="flex justify-end">
        <Button onClick={handleSaveCredentials} className="bg-primary text-white hover:bg-primary/90">
          Guardar Credenciales
        </Button>
      </CardFooter>
    </Card>
  );
}