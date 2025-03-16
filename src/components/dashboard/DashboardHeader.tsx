
import React from 'react';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';

const DashboardHeader: React.FC = () => {
  return (
    <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
      <div>
        <h1 className="text-3xl font-medium tracking-tight text-left">Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Overview of your job advertising campaigns
        </p>
      </div>
      <div className="mt-4 md:mt-0 flex space-x-3">
        <Link to="/platforms">
          <Button variant="outline">
            Manage Platforms
          </Button>
        </Link>
        <Link to="/create-campaign">
          <Button>
            Create New Campaign
          </Button>
        </Link>
      </div>
    </div>
  );
};

export default DashboardHeader;
