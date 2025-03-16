
import React from 'react';
import { RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';

interface RefreshButtonProps {
  isRefreshing: boolean;
  setIsRefreshing: (isRefreshing: boolean) => void;
}

const RefreshButton: React.FC<RefreshButtonProps> = ({ isRefreshing, setIsRefreshing }) => {
  const { toast } = useToast();

  const handleRefresh = () => {
    setIsRefreshing(true);
    // Simulate refresh API call
    setTimeout(() => {
      setIsRefreshing(false);
      toast({
        title: "Platforms refreshed",
        description: "All platform connections have been refreshed",
      });
    }, 1500);
  };

  return (
    <Button 
      variant="outline" 
      size="sm" 
      onClick={handleRefresh}
      disabled={isRefreshing}
    >
      <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
      Refresh
    </Button>
  );
};

export default RefreshButton;
