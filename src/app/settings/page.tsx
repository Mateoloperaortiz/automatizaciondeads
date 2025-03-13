"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ApiAuthForm } from '@/components/api-auth-form';
import { SocialMediaService } from '@/lib/api-integrations';
import { AuthService, StorageType } from '@/lib/api-integrations/auth';
import { SocialPlatform } from '@/lib/api-integrations/types';
import { Button } from '@/components/ui/button';

interface ApiCredentialsState {
  [key: string]: {
    isConfigured: boolean;
    lastUpdated?: Date;
    isAuthenticated?: boolean;
  };
}

export default function SettingsPage() {
  const [socialMediaService] = useState(new SocialMediaService());
  const [authService] = useState(new AuthService({ 
    storageType: StorageType.LOCAL_STORAGE,
    tokenOptions: {
      autoRefresh: true,
      refreshThreshold: 300
    }
  }));
  
  const [apiStatus, setApiStatus] = useState<ApiCredentialsState>({
    meta: { isConfigured: false },
    x: { isConfigured: false },
    google: { isConfigured: false },
    tiktok: { isConfigured: false },
    snapchat: { isConfigured: false }
  });
  
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Cargar estado de autenticación al iniciar
  useEffect(() => {
    const checkAuthStatus = () => {
      const newStatus = { ...apiStatus };
      
      // Verificar estado de cada plataforma
      (['meta', 'x', 'google', 'tiktok', 'snapchat'] as SocialPlatform[]).forEach(platform => {
        const isAuthenticated = authService.isAuthenticated(platform);
        
        // Actualizar estado
        newStatus[platform] = {
          isConfigured: newStatus[platform].isConfigured || isAuthenticated,
          isAuthenticated,
          lastUpdated: isAuthenticated ? new Date() : undefined
        };
      });
      
      setApiStatus(newStatus);
    };
    
    // Comprobar estado inicial
    checkAuthStatus();
    
    // Configurar verificación periódica
    const intervalId = setInterval(checkAuthStatus, 60000); // Cada minuto
    
    return () => clearInterval(intervalId);
  }, [authService]);

  // Función para guardar credenciales
  const handleSaveCredentials = async (credentials: any) => {
    try {
      setSaveSuccess(null);
      setSaveError(null);
      
      const platform = credentials.platform as SocialPlatform;
      let authResult;
      
      // Inicializar la API correspondiente según la plataforma
      switch (platform) {
        case 'meta':
          socialMediaService.initMetaApi(
            credentials.clientId,
            credentials.clientSecret,
            credentials.accessToken
          );
          authResult = await authService.authenticateMeta({
            clientId: credentials.clientId,
            clientSecret: credentials.clientSecret,
            accessToken: credentials.accessToken
          });
          break;
          
        case 'x':
          socialMediaService.initXApi(
            credentials.apiKey,
            credentials.apiSecret,
            credentials.accessToken
          );
          authResult = await authService.authenticateX({
            clientId: credentials.apiKey,
            clientSecret: credentials.apiSecret,
            accessToken: credentials.accessToken,
            accessTokenSecret: credentials.accessTokenSecret
          });
          break;
          
        case 'google':
          socialMediaService.initGoogleApi(
            credentials.clientId,
            credentials.clientSecret,
            credentials.refreshToken,
            credentials.developerToken
          );
          authResult = await authService.authenticateGoogle({
            clientId: credentials.clientId,
            clientSecret: credentials.clientSecret,
            refreshToken: credentials.refreshToken,
            developerToken: credentials.developerToken,
            managerId: credentials.managerId
          });
          break;
          
        case 'tiktok':
          socialMediaService.initTikTokApi(
            credentials.accessToken,
            credentials.appId,
            credentials.appSecret
          );
          authResult = await authService.authenticateTikTok({
            clientId: credentials.appId,
            clientSecret: credentials.appSecret,
            accessToken: credentials.accessToken,
            advertiserId: credentials.advertiserId
          });
          break;
          
        case 'snapchat':
          socialMediaService.initSnapchatApi(
            credentials.accessToken,
            credentials.clientId,
            credentials.clientSecret
          );
          authResult = await authService.authenticateSnapchat({
            clientId: credentials.clientId,
            clientSecret: credentials.clientSecret,
            accessToken: credentials.accessToken,
            organizationId: credentials.organizationId
          });
          break;
          
        default:
          throw new Error(`Plataforma no soportada: ${platform}`);
      }
      
      // Actualizar estado según resultado de autenticación
      if (authResult.success) {
        setApiStatus(prev => ({
          ...prev,
          [platform]: {
            isConfigured: true,
            isAuthenticated: true,
            lastUpdated: new Date()
          }
        }));
        
        setSaveSuccess(`Credenciales de ${getPlatformName(platform)} guardadas correctamente`);
      } else {
        throw new Error(authResult.error?.message || `Error al autenticar con ${platform}`);
      }
    } catch (error: any) {
      console.error('Error al guardar credenciales:', error);
      setSaveError(`Error: ${error.message}`);
      
      // Actualizar estado como no autenticado
      setApiStatus(prev => ({
        ...prev,
        [credentials.platform]: {
          ...prev[credentials.platform],
          isAuthenticated: false,
          lastUpdated: new Date()
        }
      }));
    }
  };

  // Función para cerrar sesión de una plataforma
  const handleLogout = (platform: SocialPlatform) => {
    authService.logout(platform);
    
    setApiStatus(prev => ({
      ...prev,
      [platform]: {
        isConfigured: false,
        isAuthenticated: false,
        lastUpdated: new Date()
      }
    }));
    
    setSaveSuccess(`Sesión de ${getPlatformName(platform)} cerrada correctamente`);
  };

  // Obtener nombre legible de la plataforma
  const getPlatformName = (platform: SocialPlatform): string => {
    const names: Record<SocialPlatform, string> = {
      meta: 'Meta (Facebook/Instagram)',
      x: 'X (Twitter)',
      google: 'Google',
      tiktok: 'TikTok',
      snapchat: 'Snapchat'
    };
    
    return names[platform] || platform;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-primary mb-8">Configuración</h1>
      
      {/* Mensajes de estado */}
      {saveSuccess && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6 flex justify-between items-center">
          <span>{saveSuccess}</span>
          <button onClick={() => setSaveSuccess(null)} className="text-green-700">×</button>
        </div>
      )}
      
      {saveError && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6 flex justify-between items-center">
          <span>{saveError}</span>
          <button onClick={() => setSaveError(null)} className="text-red-700">×</button>
        </div>
      )}
      
      {/* Tarjeta de estado de APIs */}
      <Card className="mb-8 border-border shadow-md">
        <CardHeader>
          <CardTitle className="text-xl font-semibold text-secondary">Estado de Conexión de APIs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(apiStatus).map(([platform, status]) => (
              <div key={platform} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <span className="font-medium">{getPlatformName(platform as SocialPlatform)}</span>
                  <div className="text-sm text-muted-foreground">
                    {status.isAuthenticated 
                      ? <span className="text-green-600">Conectado</span>
                      : status.isConfigured 
                        ? <span className="text-amber-600">Configurado, no autenticado</span>
                        : <span className="text-gray-500">No configurado</span>
                    }
                    {status.lastUpdated && (
                      <span className="ml-2 text-xs">
                        (Actualizado: {status.lastUpdated.toLocaleString()})
                      </span>
                    )}
                  </div>
                </div>
                
                {status.isAuthenticated && (
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleLogout(platform as SocialPlatform)} 
                    className="text-red-600 border-red-200 hover:bg-red-50"
                  >
                    Desconectar
                  </Button>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      
      {/* Formulario de autenticación de APIs */}
      <ApiAuthForm onSaveCredentials={handleSaveCredentials} />
    </div>
  );
}