import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/use-toast';
import { ChevronDown, ChevronUp, Check, X, Copy, ExternalLink, RefreshCw } from 'lucide-react';

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

    // Simulate API connection
    setTimeout(() => {
      setConnecting(false);
      setConnected(true);
      toast({
        title: "Connection successful",
        description: `Successfully connected to ${platform.name}`
      });
      setApiKey('');
    }, 1500);
  };

  const handleDisconnect = () => {
    setConnected(false);
    toast({
      title: "Disconnected",
      description: `Disconnected from ${platform.name}`
    });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied",
      description: "API redirect URL copied to clipboard"
    });
  };

  const redirectUrl = `https://adflux-app.com/api/callback/${platform.id.toLowerCase()}`;

  return <Card className="border border-border/50 overflow-hidden hover-lift">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white overflow-hidden ${platform.color}`}>
              {platform.icon}
            </div>
            <div>
              <CardTitle className="text-lg text-left">
                {platform.name}
                {connected && <Badge className="ml-2 bg-green-500 text-white" variant="secondary">
                    Connected
                  </Badge>}
              </CardTitle>
              <CardDescription className="text-sm mt-0.5">
                {platform.description}
              </CardDescription>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={() => setExpanded(!expanded)} className="text-muted-foreground">
            {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
        </div>
      </CardHeader>

      {expanded && <>
          <CardContent className="pb-3 pt-3">
            {!connected ? <div className="space-y-4">
                <div className="text-sm">
                  <p className="mb-4">
                    Connect your {platform.name} account to automate job ad publishing. You'll need to create an API key in your {platform.name} advertising account.
                  </p>
                  
                  <div className="bg-muted p-3 rounded-md mb-4">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-xs font-medium">API Redirect URL</span>
                      <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => copyToClipboard(redirectUrl)}>
                        <Copy className="h-3 w-3" />
                      </Button>
                    </div>
                    <code className="text-xs">{redirectUrl}</code>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Input type="text" placeholder={`Enter your ${platform.name} API Key`} value={apiKey} onChange={e => setApiKey(e.target.value)} className="flex-1" />
                    <Button onClick={handleConnect} disabled={connecting}>
                      {connecting ? <>
                          <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                          Connecting
                        </> : "Connect"}
                    </Button>
                  </div>
                </div>
              </div> : <div className="space-y-4">
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-3">
                  <div className="flex items-start">
                    <Check className="h-5 w-5 text-green-500 mr-2 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-medium">Successfully connected</h4>
                      <p className="text-xs text-muted-foreground mt-1">
                        Your {platform.name} account is now connected and ready to post job ads.
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="flex flex-col space-y-2">
                  <div className="flex justify-between items-center text-sm">
                    <span>Account status</span>
                    <Badge variant="outline" className="bg-green-500/10 text-green-600 border-green-200">
                      Active
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span>Connection type</span>
                    <span className="text-muted-foreground">API Key</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span>Last synced</span>
                    <span className="text-muted-foreground">Just now</span>
                  </div>
                </div>
              </div>}
          </CardContent>
          
          <CardFooter className="flex justify-between border-t pt-4">
            {connected ? <>
                <Button variant="outline" size="sm" className="text-xs" onClick={handleDisconnect}>
                  <X className="h-3 w-3 mr-1" /> Disconnect
                </Button>
                <Button variant="outline" size="sm" className="text-xs">
                  <ExternalLink className="h-3 w-3 mr-1" /> Open Dashboard
                </Button>
              </> : <a href={`https://${platform.id.toLowerCase()}.com/business`} target="_blank" rel="noopener noreferrer" className="text-xs text-primary hover:underline inline-flex items-center">
                Go to {platform.name} Business Manager <ExternalLink className="h-3 w-3 ml-1" />
              </a>}
          </CardFooter>
        </>}
    </Card>;
};

export default PlatformIntegration;
