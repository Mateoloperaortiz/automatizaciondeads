
import React from 'react';

interface ChartLegendComponentProps {
  payload: any[];
  legendLabels: {
    current: string;
    previous: string;
  };
}

export const ChartLegendComponent: React.FC<ChartLegendComponentProps> = ({
  payload,
  legendLabels
}) => {
  return (
    <div className="flex justify-center items-center gap-4 pt-2 text-xs">
      {payload.map((entry: any, index: number) => (
        <div key={`item-${index}`} className="flex items-center gap-1.5">
          <div 
            className="w-3 h-3 rounded-sm" 
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-foreground">
            {entry.value === 'value' 
              ? 'Value' 
              : entry.value === 'current' 
                ? legendLabels.current 
                : legendLabels.previous}
          </span>
        </div>
      ))}
    </div>
  );
};
