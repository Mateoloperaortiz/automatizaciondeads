
import React from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import ChartModalHeader from './modal/ChartModalHeader';
import ChartModalContent from './modal/ChartModalContent';

interface ChartModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  chartData: Array<{ name: string; value?: number; current?: number; previous?: number; [key: string]: any }>;
  chartColor?: string;
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

const ChartModal: React.FC<ChartModalProps> = ({
  isOpen,
  onClose,
  title,
  description,
  chartData,
  chartColor = "#0080ff",
  chartColors,
  chartType,
  showComparison = false,
  legendLabels = {
    current: "Current Period",
    previous: "Previous Period"
  }
}) => {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[90vw] max-h-[90vh] overflow-y-auto">
        <ChartModalHeader
          title={title}
          description={description}
          onClose={onClose}
        />
        <ChartModalContent
          chartData={chartData}
          chartColor={chartColor}
          chartColors={chartColors}
          chartType={chartType}
          showComparison={showComparison}
          legendLabels={legendLabels}
        />
      </DialogContent>
    </Dialog>
  );
};

export default ChartModal;
