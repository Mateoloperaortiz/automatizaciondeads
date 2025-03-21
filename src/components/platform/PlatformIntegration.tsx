import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import { fetchPlatformHealth } from '@/services/platformHealthService';
import { ApiHealthMetrics } from '@/types/platformTypes';
import ConnectionForm from './ConnectionForm';
import ConnectedAccountInfo from './ConnectedAccountInfo';
import ConnectionFooter from './ConnectionFooter';

interface PlatformIntegrationProps {
  platform: {
    id: string;
    name: string;
    icon: React.ReactNode;
    color: string;
    isConnected?: boolean;
    description: string;
  };
}

const PlatformIntegration: React.FC<PlatformIntegrationProps> = ({
  platform
}) => {
  const { toast } = useToast();
  const [expanded, setExpanded] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [connected, setConnected] = useState(platform.isConnected || false);
  const [apiKey, setApiKey] = useState('');
  const [apiHealth, setApiHealth] = useState<ApiHealthMetrics | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(false);

  useEffect(() => {
    if (connected && expanded) {
      fetchApiHealth();
    }
  }, [connected, expanded]);

  const fetchApiHealth = async () => {
    if (!connected) return;
    
    setLoadingHealth(true);
    try {
      const healthData = await fetchPlatformHealth(platform.id);
      setApiHealth(healthData);
    } catch (error) {
      console.error('Error fetching API health metrics:', error);
      toast({
        title: "Error",
        description: `Could not fetch health metrics for ${platform.name}`,
        variant: "destructive"
      });
    } finally {
      setLoadingHealth(false);
    }
  };

  const handleConnect = () => {
    if (!apiKey.trim()) {
      toast({
        title: "Error",
        description: "Please enter a valid API key",
        variant: "destructive"
      });
      return;
    }
    setConnecting(true);

    setTimeout(() => {
      setConnecting(false);
      setConnected(true);
      toast({
        title: "Connection successful",
        description: `Successfully connected to ${platform.name}`
      });
      setApiKey('');
      
      fetchApiHealth();
    }, 1500);
  };

  const handleDisconnect = () => {
    setConnected(false);
    setApiHealth(null);
    toast({
      title: "Disconnected",
      description: `Disconnected from ${platform.name}`
    });
  };

  return (
    <Card className="border border-border/50 overflow-hidden hover-lift">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white overflow-hidden ${platform.color}`}>
              {platform.icon}
            </div>
            <div>
              <CardTitle className="text-lg text-left">
                {platform.name}
                {connected && 
                  <Badge className="ml-2 bg-green-500 text-white" variant="secondary">
                    Connected
                  </Badge>
                }
              </CardTitle>
              <CardDescription className="text-sm mt-0.5">
                {platform.description}
              </CardDescription>
            </div>
          </div>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => setExpanded(!expanded)} 
            className="text-muted-foreground"
          >
            {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
        </div>
      </CardHeader>

      {expanded && (
        <>
          <CardContent className="pb-3 pt-3">
            {!connected ? (
              <ConnectionForm
                platformName={platform.name}
                platformId={platform.id}
                apiKey={apiKey}
                setApiKey={setApiKey}
                onConnect={handleConnect}
                connecting={connecting}
              />
            ) : (
              <ConnectedAccountInfo
                platformName={platform.name}
                apiHealth={apiHealth}
                loadingHealth={loadingHealth}
                expanded={expanded}
                onRefreshHealth={fetchApiHealth}
              />
            )}
          </CardContent>
          
          <CardFooter className="flex justify-between border-t pt-4">
            <ConnectionFooter
              connected={connected}
              platformId={platform.id}
              platformName={platform.name}
              onDisconnect={handleDisconnect}
            />
          </CardFooter>
        </>
      )}
    </Card>
  );
};

export default PlatformIntegration;
