
import React from 'react';
import { Link } from 'react-router-dom';
import { platforms } from '@/data/platformsData';

const Footer: React.FC = () => {
  return (
    <footer className="py-8 px-6 border-t border-border mt-auto bg-background">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Logo and description */}
          <div className="flex flex-col items-center md:items-start">
            <div className="flex items-center space-x-2 mb-4">
              <div className="rounded-lg bg-primary p-1">
                <div className="w-4 h-4 bg-white rounded-sm flex items-center justify-center">
                  <div className="w-2 h-2 bg-primary rounded-[1px]"></div>
                </div>
              </div>
              <span className="font-semibold text-base">AdFlux</span>
            </div>
            <p className="text-sm text-muted-foreground max-w-xs text-center md:text-left">
              Streamline your job ad creation and publishing across multiple platforms with our powerful automation tools.
            </p>
          </div>
          
          {/* Quick Links */}
          <div className="flex flex-col items-center md:items-start">
            <h3 className="font-medium mb-4 text-sm">Quick Links</h3>
            <ul className="space-y-2 text-center md:text-left">
              <li>
                <Link to="/" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link to="/create" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Create Campaign
                </Link>
              </li>
              <li>
                <Link to="/platforms" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Platform Integrations
                </Link>
              </li>
              <li>
                <Link to="/analytics" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Analytics & Reports
                </Link>
              </li>
            </ul>
          </div>
          
          {/* Supported Platforms */}
          <div className="flex flex-col items-center md:items-start">
            <h3 className="font-medium mb-4 text-sm">Supported Platforms</h3>
            <div className="grid grid-cols-3 gap-3">
              {platforms.map((platform) => (
                <div 
                  key={platform.id}
                  className={`w-8 h-8 rounded-full ${platform.color} flex items-center justify-center`}
                  title={platform.name}
                >
                  {React.cloneElement(platform.icon as React.ReactElement, {
                    className: 'w-4 h-4',
                  })}
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* Footer bottom */}
        <div className="border-t border-border mt-8 pt-6 flex flex-col md:flex-row justify-between items-center text-center md:text-left">
          <p className="text-xs text-muted-foreground">
            © {new Date().getFullYear()} AdFlux. All rights reserved.
          </p>
          <div className="flex space-x-4 mt-4 md:mt-0">
            <a href="#" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
              Privacy Policy
            </a>
            <a href="#" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
              Terms of Service
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
