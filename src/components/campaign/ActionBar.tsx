
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Copy, PenTool } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

interface ActionBarProps {
  campaignId?: string;
  campaignTitle?: string;
  isLoading: boolean;
}

const ActionBar: React.FC<ActionBarProps> = ({ campaignId, campaignTitle, isLoading }) => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const goBack = () => {
    navigate(-1);
  };

  const handleDuplicate = () => {
    toast({
      title: "Campaign duplicated",
      description: "The campaign has been duplicated as a draft.",
    });
  };

  const handleEditCampaign = () => {
    navigate(`/campaign/${campaignId}/edit`);
  };

  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center">
        <Button onClick={goBack} variant="ghost" className="mr-2">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        
        {isLoading ? (
          <div className="h-9 w-40 bg-gray-200 animate-pulse rounded"></div>
        ) : (
          <h1 className="text-3xl font-medium tracking-tight ml-2">{campaignTitle}</h1>
        )}
      </div>
      
      <div className="flex gap-2">
        <Button variant="outline" onClick={handleDuplicate}>
          <Copy className="mr-2 h-4 w-4" />
          Duplicate
        </Button>
        
        <Button onClick={handleEditCampaign}>
          <PenTool className="mr-2 h-4 w-4" />
          Edit Campaign
        </Button>
      </div>
    </div>
  );
};

export default ActionBar;
