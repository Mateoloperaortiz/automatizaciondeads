
import React, { useState } from 'react';
import { format, subDays, subMonths } from 'date-fns';
import { Calendar as CalendarIcon, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { cn } from '@/lib/utils';

interface DateRangeFilterProps {
  onRangeChange: (startDate: Date, endDate: Date, label: string) => void;
}

const presetRanges = [
  { label: 'Last 7 days', value: '7days' },
  { label: 'Last 30 days', value: '30days' },
  { label: 'Last 3 months', value: '3months' },
  { label: 'Last 6 months', value: '6months' },
  { label: 'Year to date', value: 'ytd' },
  { label: 'Custom range', value: 'custom' },
];

const DateRangeFilter: React.FC<DateRangeFilterProps> = ({ onRangeChange }) => {
  const today = new Date();
  const [selectedRange, setSelectedRange] = useState('30days');
  const [dateRange, setDateRange] = useState<[Date | undefined, Date | undefined]>([
    subDays(today, 30),
    today,
  ]);
  const [isCustomRange, setIsCustomRange] = useState(false);

  const handleRangeChange = (value: string) => {
    setSelectedRange(value);
    setIsCustomRange(value === 'custom');
    
    let startDate: Date;
    let endDate = today;
    let label = '';

    switch (value) {
      case '7days':
        startDate = subDays(today, 7);
        label = 'Last 7 days';
        break;
      case '30days':
        startDate = subDays(today, 30);
        label = 'Last 30 days';
        break;
      case '3months':
        startDate = subMonths(today, 3);
        label = 'Last 3 months';
        break;
      case '6months':
        startDate = subMonths(today, 6);
        label = 'Last 6 months';
        break;
      case 'ytd':
        startDate = new Date(today.getFullYear(), 0, 1);
        label = 'Year to date';
        break;
      case 'custom':
        if (dateRange[0] && dateRange[1]) {
          startDate = dateRange[0];
          endDate = dateRange[1];
          label = `${format(startDate, 'MMM d, yyyy')} - ${format(endDate, 'MMM d, yyyy')}`;
        } else {
          startDate = subDays(today, 30);
          label = 'Custom range';
        }
        break;
      default:
        startDate = subDays(today, 30);
        label = 'Last 30 days';
    }

    if (value !== 'custom' || (dateRange[0] && dateRange[1])) {
      setDateRange([startDate, endDate]);
      onRangeChange(startDate, endDate, label);
    }
  };

  const handleCustomDateChange = (dates: [Date | undefined, Date | undefined]) => {
    setDateRange(dates);
    if (dates[0] && dates[1]) {
      onRangeChange(
        dates[0], 
        dates[1], 
        `${format(dates[0], 'MMM d, yyyy')} - ${format(dates[1], 'MMM d, yyyy')}`
      );
    }
  };

  return (
    <div className="flex flex-col sm:flex-row sm:items-center gap-3">
      <div className="flex-1 sm:max-w-xs">
        <Select value={selectedRange} onValueChange={handleRangeChange}>
          <SelectTrigger>
            <SelectValue placeholder="Select time range" />
          </SelectTrigger>
          <SelectContent>
            {presetRanges.map((range) => (
              <SelectItem key={range.value} value={range.value}>
                {range.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      
      {isCustomRange && (
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              className={cn(
                "justify-start w-full sm:w-auto text-left font-normal",
                !dateRange && "text-muted-foreground"
              )}
            >
              <CalendarIcon className="mr-2 h-4 w-4" />
              {dateRange[0] && dateRange[1] ? (
                <>
                  {format(dateRange[0], 'MMM d, yyyy')} - {format(dateRange[1], 'MMM d, yyyy')}
                </>
              ) : (
                <span>Pick a date range</span>
              )}
              <ChevronDown className="ml-auto h-4 w-4 opacity-50" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="start">
            <Calendar
              mode="range"
              selected={dateRange as any}
              onSelect={handleCustomDateChange as any}
              numberOfMonths={2}
              initialFocus
              className={cn("p-3 pointer-events-auto")}
            />
          </PopoverContent>
        </Popover>
      )}
    </div>
  );
};

export default DateRangeFilter;
