
import React from 'react';
import { Button } from '@/components/ui/button';
import { X, ExternalLink } from 'lucide-react';

interface ConnectionFooterProps {
  connected: boolean;
  platformId: string;
  platformName: string;
  onDisconnect: () => void;
}

const ConnectionFooter: React.FC<ConnectionFooterProps> = ({
  connected,
  platformId,
  platformName,
  onDisconnect
}) => {
  if (connected) {
    return (
      <>
        <Button variant="outline" size="sm" className="text-xs" onClick={onDisconnect}>
          <X className="h-3 w-3 mr-1" /> Disconnect
        </Button>
        <Button variant="outline" size="sm" className="text-xs">
          <ExternalLink className="h-3 w-3 mr-1" /> Open Dashboard
        </Button>
      </>
    );
  }
  
  return (
    <a 
      href={`https://${platformId.toLowerCase()}.com/business`} 
      target="_blank" 
      rel="noopener noreferrer" 
      className="text-xs text-primary hover:underline inline-flex items-center"
    >
      Go to {platformName} Business Manager <ExternalLink className="h-3 w-3 ml-1" />
    </a>
  );
};

export default ConnectionFooter;
