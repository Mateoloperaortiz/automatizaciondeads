
import React from 'react';
import { ChartContainer, ChartTooltipContent } from '@/components/ui/chart';
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface DetailedChartProps {
  chartData: Array<{ name: string; value?: number; current?: number; previous?: number; [key: string]: any }>;
  chartColor: string;
  chartColors?: {
    current: string;
    previous: string;
  };
  chartType: 'area' | 'bar';
  showComparison?: boolean;
  legendLabels?: {
    current: string;
    previous: string;
  };
}

const DetailedChart: React.FC<DetailedChartProps> = ({
  chartData,
  chartColor,
  chartColors,
  chartType,
  showComparison = false,
  legendLabels = {
    current: "Current Period",
    previous: "Previous Period"
  }
}) => {
  // Use comparison colors if showComparison is true, otherwise use single color config
  const config = showComparison ? {
    current: { label: legendLabels.current, theme: { light: chartColors?.current || "#0080ff", dark: chartColors?.current || "#0080ff" } },
    previous: { label: legendLabels.previous, theme: { light: chartColors?.previous || "#86EFAC", dark: chartColors?.previous || "#86EFAC" } }
  } : {
    data: { label: "Value", theme: { light: chartColor, dark: chartColor } }
  };

  // Custom legend formatter for better readability
  const renderLegend = (props: any) => {
    const { payload } = props;
    
    return (
      <div className="flex justify-center items-center gap-6 pt-4 pb-2">
        {payload.map((entry: any, index: number) => (
          <div key={`item-${index}`} className="flex items-center gap-2">
            <div 
              className="w-4 h-4 rounded-sm" 
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-sm font-medium">
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

  return (
    <ChartContainer config={config} className="w-full h-full py-4">
      {chartType === 'area' ? (
        <AreaChart data={chartData} margin={{ top: 30, right: 30, left: 20, bottom: 30 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={true} horizontal={true} />
          <XAxis 
            dataKey="name"
            tick={{ fontSize: 12 }}
            axisLine={true}
            tickLine={true}
          />
          <YAxis 
            tick={{ fontSize: 12 }}
            axisLine={true}
            tickLine={true}
            tickFormatter={(value) => `${value}`}
          />
          <Tooltip 
            content={({ active, payload, label }) => (
              <ChartTooltipContent 
                active={active}
                payload={payload}
                label={label}
                formatter={(value: any, name: string) => {
                  const displayName = name === 'current' 
                    ? legendLabels.current 
                    : name === 'previous' 
                      ? legendLabels.previous 
                      : "Value";
                  return [`${value}`, displayName];
                }}
              />
            )}
          />
          
          {showComparison ? (
            <>
              <Area 
                type="monotone" 
                dataKey="current" 
                stroke={chartColors?.current || "#0080ff"} 
                fill={`${chartColors?.current || "#0080ff"}20`} 
                strokeWidth={2}
                activeDot={{ r: 6, strokeWidth: 0 }}
              />
              <Area 
                type="monotone" 
                dataKey="previous" 
                stroke={chartColors?.previous || "#86EFAC"} 
                fill={`${chartColors?.previous || "#86EFAC"}20`} 
                strokeWidth={2}
                strokeDasharray="5 5"
                activeDot={{ r: 6, strokeWidth: 0 }}
              />
            </>
          ) : (
            <Area 
              type="monotone" 
              dataKey="value" 
              stroke={chartColor} 
              fill={`${chartColor}20`} 
              strokeWidth={2}
              activeDot={{ r: 6, strokeWidth: 0 }}
            />
          )}
          
          <Legend content={renderLegend} />
        </AreaChart>
      ) : (
        <BarChart data={chartData} margin={{ top: 30, right: 30, left: 20, bottom: 30 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={true} horizontal={true} />
          <XAxis 
            dataKey="name"
            tick={{ fontSize: 12 }}
            axisLine={true}
            tickLine={true}
          />
          <YAxis 
            tick={{ fontSize: 12 }}
            axisLine={true}
            tickLine={true}
            tickFormatter={(value) => `${value}`}
          />
          <Tooltip 
            content={({ active, payload, label }) => (
              <ChartTooltipContent 
                active={active}
                payload={payload}
                label={label}
                formatter={(value: any, name: string) => {
                  const displayName = name === 'current' 
                    ? legendLabels.current 
                    : name === 'previous' 
                      ? legendLabels.previous 
                      : "Value";
                  return [`${value}`, displayName];
                }}
              />
            )}
          />
          
          {showComparison ? (
            <>
              <Bar 
                dataKey="current" 
                fill={chartColors?.current || "#0080ff"} 
                radius={[4, 4, 0, 0]} 
              />
              <Bar 
                dataKey="previous" 
                fill={chartColors?.previous || "#86EFAC"} 
                radius={[4, 4, 0, 0]} 
              />
            </>
          ) : (
            <Bar 
              dataKey="value" 
              fill={chartColor} 
              radius={[4, 4, 0, 0]} 
            />
          )}
          
          <Legend content={renderLegend} />
        </BarChart>
      )}
    </ChartContainer>
  );
};

export default DetailedChart;
