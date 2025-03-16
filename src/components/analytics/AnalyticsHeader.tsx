
import React from 'react';
import AnimatedTransition from '@/components/ui/AnimatedTransition';
import { useIsMobile } from '@/hooks/use-mobile';
import { BarChart3 } from 'lucide-react';

interface AnalyticsHeaderProps {
  title: string;
  description: string;
}

const AnalyticsHeader: React.FC<AnalyticsHeaderProps> = ({ title, description }) => {
  const isMobile = useIsMobile();
  
  return (
    <AnimatedTransition type="fade" delay={0}>
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 md:mb-8">
        <div className="flex items-center">
          <div className="mr-3 bg-primary/10 p-2 rounded-md hidden sm:flex">
            <BarChart3 className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight">{title}</h1>
            <div className="text-muted-foreground mt-1 text-sm">
              <span>{description}</span>
            </div>
          </div>
        </div>
      </div>
    </AnimatedTransition>
  );
};

export default AnalyticsHeader;
