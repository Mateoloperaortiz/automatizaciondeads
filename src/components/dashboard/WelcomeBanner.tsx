
import React from 'react';
import AnimatedTransition from '@/components/ui/AnimatedTransition';

const WelcomeBanner = () => {
  return (
    <AnimatedTransition type="fade" delay={0}>
      <div className="bg-gradient-to-r from-primary/10 to-primary/5 rounded-lg p-6 mb-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Welcome to AdFlux</h1>
            <p className="text-muted-foreground mt-1">Your job advertising management platform</p>
          </div>
        </div>
      </div>
    </AnimatedTransition>
  );
};

export default WelcomeBanner;
