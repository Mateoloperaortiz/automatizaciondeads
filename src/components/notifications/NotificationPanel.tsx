
import React from 'react';
import { format } from 'date-fns';
import { motion } from 'framer-motion';
import { Bell, CheckCheck, Trash2, X } from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Notification, useNotifications } from '@/contexts/NotificationContext';
import { Separator } from '@/components/ui/separator';
import AnimatedTransition from '@/components/ui/AnimatedTransition';

const NotificationType = ({ type }: { type: Notification['type'] }) => {
  const colors = {
    info: 'bg-blue-500',
    success: 'bg-green-500',
    warning: 'bg-amber-500',
    error: 'bg-red-500',
  };

  return <span className={`${colors[type]} h-2 w-2 rounded-full`} />;
};

const NotificationItem = ({ notification }: { notification: Notification }) => {
  const { markAsRead, removeNotification } = useNotifications();

  const handleClick = () => {
    if (!notification.read) {
      markAsRead(notification.id);
    }
  };

  return (
    <AnimatedTransition type="slide-up" duration={0.2}>
      <div 
        className={cn(
          "p-3 relative rounded-md hover:bg-secondary/50 transition-colors",
          !notification.read && "bg-secondary/30"
        )}
      >
        <div className="flex items-start gap-2">
          <NotificationType type={notification.type} />
          <div className="flex-1 min-w-0" onClick={handleClick}>
            {notification.link ? (
              <Link to={notification.link} className="block">
                <h4 className="font-medium text-sm">{notification.title}</h4>
                <p className="text-muted-foreground text-xs line-clamp-2">{notification.message}</p>
              </Link>
            ) : (
              <>
                <h4 className="font-medium text-sm">{notification.title}</h4>
                <p className="text-muted-foreground text-xs line-clamp-2">{notification.message}</p>
              </>
            )}
            <span className="text-xs text-muted-foreground mt-1 block">
              {format(notification.date, 'MMM d, h:mm a')}
            </span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6 text-muted-foreground hover:text-foreground"
            onClick={() => removeNotification(notification.id)}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </AnimatedTransition>
  );
};

const NotificationPanel = () => {
  const { notifications, unreadCount, markAllAsRead, clearAllNotifications } = useNotifications();

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute top-0 right-0 h-2.5 w-2.5 bg-primary rounded-full">
              {unreadCount > 99 ? (
                <span className="absolute -top-1 -right-1 text-[10px] font-semibold text-white">99+</span>
              ) : unreadCount > 9 ? (
                <span className="absolute -top-1 -right-1 text-[10px] font-semibold text-white">{unreadCount}</span>
              ) : null}
            </span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-0 max-h-[70vh] flex flex-col">
        <div className="p-3 border-b flex items-center justify-between sticky top-0 bg-card z-10">
          <h3 className="font-semibold">Notifications</h3>
          <div className="flex gap-1">
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                className="h-8 px-2 text-xs"
                onClick={markAllAsRead}
              >
                <CheckCheck className="h-3.5 w-3.5 mr-1" />
                Mark all read
              </Button>
            )}
            {notifications.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                className="h-8 px-2 text-xs"
                onClick={clearAllNotifications}
              >
                <Trash2 className="h-3.5 w-3.5 mr-1" />
                Clear all
              </Button>
            )}
          </div>
        </div>
        <div className="overflow-y-auto flex-1">
          {notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-6 text-center text-muted-foreground">
              <Bell className="h-8 w-8 mb-2 opacity-50" />
              <p className="text-sm">No notifications yet</p>
            </div>
          ) : (
            <div className="divide-y divide-border">
              {notifications.map((notification) => (
                <NotificationItem key={notification.id} notification={notification} />
              ))}
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
};

export default NotificationPanel;
