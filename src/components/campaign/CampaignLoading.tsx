
import React from 'react';
import { Loader2 } from 'lucide-react';

const CampaignLoading: React.FC = () => {
  return (
    <div className="flex justify-center py-24">
      <Loader2 className="h-12 w-12 animate-spin text-primary/70" />
    </div>
  );
};

export default CampaignLoading;
