
import React from 'react';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';
import { DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';

interface ChartModalHeaderProps {
  title: string;
  description?: string;
  onClose: () => void;
}

const ChartModalHeader: React.FC<ChartModalHeaderProps> = ({
  title,
  description,
  onClose
}) => {
  return (
    <DialogHeader>
      <Button
        variant="ghost"
        size="icon"
        className="absolute right-4 top-4 z-10"
        onClick={onClose}
        aria-label="Close"
      >
        <X className="h-4 w-4" />
      </Button>
      <div className="flex justify-between items-center">
        <div>
          <DialogTitle>{title}</DialogTitle>
          {description && (
            <DialogDescription>{description}</DialogDescription>
          )}
        </div>
      </div>
    </DialogHeader>
  );
};

export default ChartModalHeader;
