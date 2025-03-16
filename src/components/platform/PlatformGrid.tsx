
import React from 'react';
import { Platform } from '@/data/platformsData';
import PlatformIntegration from '@/components/platform/PlatformIntegration';
import EmptyState from '@/components/platform/EmptyState';

interface PlatformGridProps {
  platforms: Platform[];
  view: 'list';
  filterConnected?: boolean;
}

const PlatformGrid: React.FC<PlatformGridProps> = ({ 
  platforms, 
  filterConnected
}) => {
  const filteredPlatforms = filterConnected !== undefined
    ? platforms.filter(platform => platform.isConnected === filterConnected)
    : platforms;
    
  if (filteredPlatforms.length === 0 && filterConnected === true) {
    return <EmptyState />;
  }

  return (
    <div className="space-y-4">
      {filteredPlatforms.map((platform) => (
        <PlatformIntegration 
          key={platform.id} 
          platform={platform} 
        />
      ))}
    </div>
  );
};

export default PlatformGrid;
