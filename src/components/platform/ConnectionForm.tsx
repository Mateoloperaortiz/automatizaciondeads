
import React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Copy, RefreshCw } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

interface ConnectionFormProps {
  platformName: string;
  platformId: string;
  apiKey: string;
  setApiKey: (value: string) => void;
  onConnect: () => void;
  connecting: boolean;
}

const ConnectionForm: React.FC<ConnectionFormProps> = ({
  platformName,
  platformId,
  apiKey,
  setApiKey,
  onConnect,
  connecting
}) => {
  const { toast } = useToast();
  const redirectUrl = `https://adflux-app.com/api/callback/${platformId.toLowerCase()}`;

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied",
      description: "API redirect URL copied to clipboard"
    });
  };

  return (
    <div className="space-y-4">
      <div className="text-sm">
        <p className="mb-4">
          Connect your {platformName} account to automate job ad publishing. You'll need to create an API key in your {platformName} advertising account.
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
          <Input 
            type="text" 
            placeholder={`Enter your ${platformName} API Key`} 
            value={apiKey} 
            onChange={e => setApiKey(e.target.value)} 
            className="flex-1" 
          />
          <Button onClick={onConnect} disabled={connecting}>
            {connecting ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Connecting
              </>
            ) : "Connect"}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ConnectionForm;
