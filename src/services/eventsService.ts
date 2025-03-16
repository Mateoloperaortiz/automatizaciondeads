
import { simulateNetworkDelay } from './mockDatabase';

export interface Event {
  title: string;
  time: string;
}

// Events data service
export const fetchEvents = async (): Promise<Event[]> => {
  await simulateNetworkDelay(600);
  
  return [
    { title: 'Campaign Launch: Frontend Developer', time: '10:00 AM Today' },
    { title: 'LinkedIn Campaign Ending', time: 'Tomorrow' },
    { title: 'Weekly Performance Review', time: 'Friday, 2:00 PM' },
  ];
};
