
import React from 'react';
import { Globe2 } from 'lucide-react';

const EmptyState: React.FC = () => {
  return (
    <div className="py-12 text-center">
      <Globe2 className="mx-auto h-12 w-12 text-muted-foreground" />
      <h3 className="mt-4 text-lg font-medium">No connected platforms</h3>
      <p className="mt-2 text-muted-foreground">
        Connect to your first platform to start automating job postings
      </p>
    </div>
  );
};

export default EmptyState;
