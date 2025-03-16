
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Clock, Plus, TrendingUp, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import AnimatedTransition from '@/components/ui/AnimatedTransition';

interface QuickActionItem {
  title: string;
  description: string;
  icon: React.ReactNode;
  path: string;
  color: string;
}

const QuickActions = () => {
  // Sample data for quick actions
  const quickActions: QuickActionItem[] = [
    { 
      title: 'Create Campaign', 
      description: 'Set up a new job advertisement campaign', 
      icon: <Plus className="w-5 h-5" />, 
      path: '/create-campaign',
      color: 'bg-blue-500'
    },
    { 
      title: 'View Analytics', 
      description: 'Check performance of your campaigns', 
      icon: <TrendingUp className="w-5 h-5" />, 
      path: '/analytics',
      color: 'bg-purple-500'
    },
    { 
      title: 'Manage Platforms', 
      description: 'Configure platform integrations', 
      icon: <Users className="w-5 h-5" />, 
      path: '/platforms',
      color: 'bg-green-500'
    }
  ];

  return (
    <AnimatedTransition type="slide-up" delay={0.1}>
      <div className="mb-8">
        <h2 className="text-xl font-medium mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {quickActions.map((action, index) => (
            <Link to={action.path} key={index}>
              <Card className="hover:shadow-md transition-shadow duration-200 overflow-hidden">
                <div className={`h-1 ${action.color}`}></div>
                <CardContent className="p-6">
                  <div className="flex items-start">
                    <div className={`${action.color} text-white p-2 rounded-md mr-4`}>
                      {action.icon}
                    </div>
                    <div>
                      <h3 className="font-medium">
                        {action.title}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {action.description}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </AnimatedTransition>
  );
};

export default QuickActions;
