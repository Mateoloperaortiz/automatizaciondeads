
import React from 'react';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface EditCampaignHeaderProps {
  campaignId: string;
}

const EditCampaignHeader: React.FC<EditCampaignHeaderProps> = ({ campaignId }) => {
  const navigate = useNavigate();

  const goBack = () => {
    navigate(`/campaign/${campaignId}`);
  };

  return (
    <div className="flex items-center">
      <Button onClick={goBack} variant="ghost" className="mr-2">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back
      </Button>
      <h1 className="text-3xl font-medium tracking-tight">Edit Campaign</h1>
    </div>
  );
};

export default EditCampaignHeader;
