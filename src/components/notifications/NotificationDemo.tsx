
import React from 'react';
import { Button } from '@/components/ui/button';
import { useNotifications } from '@/contexts/NotificationContext';
import { 
  AlertCircle, 
  CheckCircle2, 
  Info, 
  BellRing
} from 'lucide-react';

const NotificationDemo = () => {
  const { addNotification } = useNotifications();

  const addInfoNotification = () => {
    addNotification({
      title: 'New Feature Available',
      message: 'Check out our new analytics dashboard with enhanced metrics',
      type: 'info',
    });
  };

  const addSuccessNotification = () => {
    addNotification({
      title: 'Campaign Created',
      message: 'Your campaign "Summer Sale 2023" has been successfully created',
      type: 'success',
      link: '/analytics',
    });
  };

  const addWarningNotification = () => {
    addNotification({
      title: 'Budget Alert',
      message: 'Your campaign "Black Friday" is approaching the budget limit',
      type: 'warning',
    });
  };

  const addErrorNotification = () => {
    addNotification({
      title: 'Upload Failed',
      message: 'There was an error uploading your image. Please try again.',
      type: 'error',
    });
  };

  return (
    <div className="bg-white dark:bg-black p-4 rounded-lg shadow-sm border">
      <div className="flex items-center mb-4">
        <BellRing className="h-5 w-5 mr-2 text-primary" />
        <h3 className="font-medium">Try the Notification System</h3>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <Button 
          variant="outline" 
          size="sm" 
          className="gap-1.5"
          onClick={addInfoNotification}
        >
          <Info className="h-3.5 w-3.5" />
          Info
        </Button>
        <Button 
          variant="outline" 
          size="sm" 
          className="gap-1.5"
          onClick={addSuccessNotification}
        >
          <CheckCircle2 className="h-3.5 w-3.5" />
          Success
        </Button>
        <Button 
          variant="outline" 
          size="sm" 
          className="gap-1.5"
          onClick={addWarningNotification}
        >
          <AlertCircle className="h-3.5 w-3.5 text-amber-500" />
          Warning
        </Button>
        <Button 
          variant="outline" 
          size="sm" 
          className="gap-1.5"
          onClick={addErrorNotification}
        >
          <AlertCircle className="h-3.5 w-3.5 text-red-500" />
          Error
        </Button>
      </div>
    </div>
  );
};

export default NotificationDemo;
