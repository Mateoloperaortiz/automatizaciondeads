
import React from 'react';
import { cn } from '@/lib/utils';

interface ProgressConnectorProps {
  isActive: boolean;
}

const ProgressConnector: React.FC<ProgressConnectorProps> = ({ isActive }) => {
  return (
    <div className="flex-1 h-0.5 mx-4">
      <div className={cn(
        "h-full",
        isActive ? "bg-primary" : "bg-muted"
      )} />
    </div>
  );
};

export default ProgressConnector;
