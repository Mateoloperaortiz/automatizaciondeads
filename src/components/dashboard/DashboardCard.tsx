
import React, { ReactNode, useState } from 'react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import ChartModal from './ChartModal';

interface DashboardCardProps {
  title: string;
  description?: string;
  className?: string;
  icon?: ReactNode;
  footer?: ReactNode;
  children: ReactNode;
  accentColor?: string;
  headerClassName?: string; // Added this prop
}

const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  description,
  className,
  icon,
  footer,
  children,
  accentColor,
  headerClassName
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Determine if the card contains a chart by checking for MetricsChart component
  const isChart = React.Children.toArray(children).some(
    child => React.isValidElement(child) && 
    (child.type as any)?.name === 'MetricsChart'
  );

  // Extract data and props from MetricsChart component
  const chartChild = React.Children.toArray(children).find(
    child => React.isValidElement(child) && (child.type as any)?.name === 'MetricsChart'
  ) as React.ReactElement | undefined;

  const chartData = chartChild?.props?.data || [];
  const chartColor = chartChild?.props?.color || "#0080ff";
  const chartType = chartChild?.props?.chartType || 'area';

  const handleCardClick = () => {
    if (isChart) {
      setIsModalOpen(true);
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  return (
    <>
      <Card 
        className={cn(
          'overflow-hidden transition-all duration-200 hover-lift', 
          'border-border/40 subtle-shadow',
          isChart ? 'cursor-pointer' : '',
          className
        )}
        onClick={isChart ? handleCardClick : undefined}
        style={accentColor ? {
          borderTop: `4px solid ${accentColor}`,
          boxShadow: `0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)`
        } : undefined}
      >
        <CardHeader className={cn("pb-2", headerClassName)}>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="text-lg font-medium tracking-tight">{title}</CardTitle>
              {description && (
                <CardDescription className="mt-1 text-sm text-muted-foreground">
                  {description}
                </CardDescription>
              )}
            </div>
            {icon && (
              <div 
                className="text-muted-foreground/70 p-2 rounded-full" 
                style={accentColor ? { 
                  backgroundColor: `${accentColor}15`,
                  color: accentColor
                } : undefined}
              >
                {icon}
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>{children}</CardContent>
        {footer && <CardFooter className="pt-0">{footer}</CardFooter>}
      </Card>

      {isChart && (
        <ChartModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          title={title}
          description={description}
          chartData={chartData}
          chartColor={chartColor}
          chartColors={chartChild?.props?.colors}
          chartType={chartType}
          showComparison={chartChild?.props?.isComparison}
          legendLabels={chartChild?.props?.legendLabels}
        />
      )}
    </>
  );
};

export default DashboardCard;
