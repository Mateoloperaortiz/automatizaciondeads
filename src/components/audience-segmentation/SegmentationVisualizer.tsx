'use client';

import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist';
import { AudienceSegment } from '@/lib/audience-segmentation/types';

interface SegmentationVisualizerProps {
  segments: AudienceSegment[];
  title?: string;
  width?: number;
  height?: number;
}

/**
 * Component to visualize audience segmentation results
 */
export const SegmentationVisualizer: React.FC<SegmentationVisualizerProps> = ({
  segments,
  title = 'Audience Segmentation Visualization',
  width = 800,
  height = 500,
}) => {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartRef.current || segments.length === 0) return;

    // Collect visualization data from all segments
    const plotData: Plotly.Data[] = [];
    const layout: Partial<Plotly.Layout> = {
      title: title,
      showlegend: true,
      width: width,
      height: height,
      hovermode: 'closest',
      xaxis: {
        title: 'Feature 1',
      },
      yaxis: {
        title: 'Feature 2',
      },
      margin: { l: 50, r: 50, b: 50, t: 50, pad: 4 },
    };

    // Process each segment's visualization data
    segments.forEach((segment) => {
      if (!segment.visualizationData) return;
      
      // If segment has traces, add them to the plot
      const segmentData = segment.visualizationData as Record<string, unknown>;
      if (segmentData.traces && Array.isArray(segmentData.traces)) {
        // Add segment name to each trace
        const traces = segmentData.traces.map((trace: Record<string, unknown>) => ({
          ...trace,
          name: `${segment.name} - ${(trace.name as string) || 'Group'}`,
        }));
        
        plotData.push(...traces as Plotly.Data[]);
      }
    });

    // Create the plot
    if (plotData.length > 0) {
      Plotly.newPlot(chartRef.current, plotData, layout);
    } else {
      // If no visualization data, show a message
      Plotly.newPlot(
        chartRef.current, 
        [{
          type: 'scatter',
          mode: 'text',
          text: ['No visualization data available'],
          textposition: 'middle center',
          textfont: {
            size: 16,
            color: '#666'
          },
          x: [0],
          y: [0]
        }], 
        {
          ...layout,
          xaxis: { ...layout.xaxis, showticklabels: false, zeroline: false },
          yaxis: { ...layout.yaxis, showticklabels: false, zeroline: false }
        }
      );
    }

    // Cleanup
    const currentChartRef = chartRef.current;
    return () => {
      if (currentChartRef) {
        Plotly.purge(currentChartRef);
      }
    };
  }, [segments, title, width, height]);

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <div ref={chartRef} className="w-full" />
      <div className="mt-4 text-sm text-gray-500">
        <p>Total Segments: {segments.length}</p>
        <p>Total Users: {segments.reduce((sum, segment) => sum + segment.size, 0)}</p>
      </div>
    </div>
  );
};

export default SegmentationVisualizer;
