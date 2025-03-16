
import React from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { useChartContext } from './ChartProvider';

interface BarChartComponentProps {
  data: Array<{
    name: string;
    value?: number;
    current?: number;
    previous?: number;
    [key: string]: any;
  }>;
  color: string;
  colors?: {
    current: string;
    previous: string;
  };
  showGrid: boolean;
  height: number;
  showLegend: boolean;
  isComparison: boolean;
  legendLabels: {
    current: string;
    previous: string;
  };
  renderLegend: (props: any) => JSX.Element;
}

export const BarChartComponent: React.FC<BarChartComponentProps> = ({
  data,
  color,
  colors,
  showGrid,
  height,
  showLegend,
  isComparison,
  legendLabels,
  renderLegend
}) => {
  const { isExpanded } = useChartContext();
  const showComparison = isComparison && colors;

  return (
    <ResponsiveContainer width="100%" height={isExpanded ? "100%" : height}>
      <BarChart 
        data={data} 
        margin={{
          top: 10,
          right: 0,
          left: 0,
          bottom: showLegend ? 20 : 0
        }}
      >
        {showGrid && (
          <CartesianGrid 
            strokeDasharray="3 3" 
            vertical={false} 
            stroke="#f0f0f0" 
          />
        )}
        <XAxis 
          dataKey="name" 
          axisLine={false} 
          tickLine={false} 
          tick={{
            fontSize: 10,
            fill: '#999'
          }} 
          dy={10} 
        />
        <YAxis 
          hide={!showGrid} 
          axisLine={false} 
          tickLine={false} 
          tick={{
            fontSize: 10,
            fill: '#999'
          }} 
        />
        <Tooltip 
          contentStyle={{
            borderRadius: '8px',
            border: 'none',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
            fontSize: '12px',
            padding: '8px 12px'
          }} 
        />
        
        {showComparison ? (
          <>
            <Bar 
              dataKey="current" 
              name={legendLabels.current}
              fill={colors?.current} 
              radius={[4, 4, 0, 0]}
            />
            <Bar 
              dataKey="previous" 
              name={legendLabels.previous}
              fill={colors?.previous} 
              radius={[4, 4, 0, 0]}
            />
          </>
        ) : (
          <Bar 
            dataKey="value" 
            name="Value"
            fill={color} 
            radius={[4, 4, 0, 0]} 
          />
        )}
        
        {showLegend && (
          <Legend content={renderLegend} />
        )}
      </BarChart>
    </ResponsiveContainer>
  );
};
