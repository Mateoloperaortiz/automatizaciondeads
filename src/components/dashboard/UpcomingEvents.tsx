
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Button } from '@/components/ui/button';
import { Calendar, Clock, Plus, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import AnimatedTransition from '@/components/ui/AnimatedTransition';
import { useQuery } from '@tanstack/react-query';
import { fetchEvents, Event } from '@/services/eventsService';
import { useToast } from '@/hooks/use-toast';

interface UpcomingEvent {
  title: string;
  time: string;
}

const UpcomingEvents = () => {
  const { toast } = useToast();
  
  const { data: upcomingEvents, isLoading, error } = useQuery({
    queryKey: ['events'],
    queryFn: fetchEvents,
    meta: {
      onError: (error: Error) => {
        toast({
          title: "Error loading events",
          description: "Could not load upcoming events. Please try again.",
          variant: "destructive"
        });
      }
    }
  });

  return (
    <AnimatedTransition type="slide-up" delay={0.3}>
      <Card>
        <div className="bg-secondary px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-medium">Upcoming</h2>
          <Calendar className="h-5 w-5 text-muted-foreground" />
        </div>
        <CardContent className="p-6">
          {isLoading ? (
            <div className="flex justify-center items-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-primary/70" />
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Failed to load events</p>
              <Button 
                variant="outline" 
                size="sm"
                className="mt-2"
                onClick={() => window.location.reload()}
              >
                Retry
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {upcomingEvents && upcomingEvents.map((event: UpcomingEvent, index: number) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary">
                    <Clock className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="font-medium">{event.title}</p>
                    <p className="text-sm text-muted-foreground">{event.time}</p>
                  </div>
                </div>
              ))}
              
              <Separator className="my-2" />
              
              <div className="pt-2">
                <Link to="/create">
                  <Button variant="outline" className="w-full">
                    <Plus className="mr-2 h-4 w-4" /> Add Event
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </AnimatedTransition>
  );
};

export default UpcomingEvents;
