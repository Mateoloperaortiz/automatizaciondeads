
import React from 'react';
import { PieChart } from 'lucide-react';
import DashboardCard from '@/components/dashboard/DashboardCard';
import { Progress } from '@/components/ui/progress';
import AnimatedTransition from '@/components/ui/AnimatedTransition';
import { Badge } from '@/components/ui/badge';

// Platform distribution data
const impressionsByPlatform = [
  { name: 'LinkedIn', value: 450000, color: '#0077B5', bgColor: '#0077B520' },
  { name: 'Meta', value: 980000, color: '#1877F2', bgColor: '#1877F220' },
  { name: 'Google', value: 1250000, color: '#4285F4', bgColor: '#4285F420' },
  { name: 'Twitter', value: 320000, color: '#1DA1F2', bgColor: '#1DA1F220' },
  { name: 'Snapchat', value: 180000, color: '#FFFC00', bgColor: '#FFFC0030' }
];

const PlatformDistribution: React.FC = () => {
  const totalImpressions = impressionsByPlatform.reduce((sum, platform) => sum + platform.value, 0);
  
  return (
    <AnimatedTransition type="slide-up" delay={0.4}>
      <div>
        <DashboardCard 
          title="Impressions by Platform" 
          description="Distribution of impressions across platforms" 
          icon={<PieChart className="h-5 w-5" />}
          className="hover-lift"
          accentColor="#7E69AB"
        >
          <div className="space-y-4">
            {impressionsByPlatform.map((platform, index) => {
              const percentage = Math.round((platform.value / totalImpressions) * 100);
              return (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: platform.color }} 
                      />
                      <span className="text-sm font-medium">{platform.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge 
                        variant="outline" 
                        className="font-normal text-xs"
                        style={{ 
                          backgroundColor: platform.bgColor,
                          color: platform.color,
                          borderColor: platform.color
                        }}
                      >
                        {percentage}%
                      </Badge>
                      <span className="text-xs text-muted-foreground">{platform.value.toLocaleString()}</span>
                    </div>
                  </div>
                  <Progress 
                    value={percentage} 
                    className="h-2" 
                    style={{ 
                      '--progress-background': platform.bgColor,
                      '--progress-foreground': platform.color
                    } as React.CSSProperties} 
                  />
                </div>
              );
            })}
          </div>
        </DashboardCard>
      </div>
    </AnimatedTransition>
  );
};

export default PlatformDistribution;
