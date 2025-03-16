
import React from 'react';
import { ListChecks } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ViewSwitcherProps {
  view: 'list';
  setView: (view: 'list') => void;
}

const ViewSwitcher: React.FC<ViewSwitcherProps> = ({ view, setView }) => {
  return (
    <Button
      variant="outline"
      size="sm"
      className="h-8 gap-1"
      onClick={() => setView('list')}
    >
      <ListChecks className="h-4 w-4" />
      <span className="hidden sm:inline-block">List</span>
    </Button>
  );
};

export default ViewSwitcher;
