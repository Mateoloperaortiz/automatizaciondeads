
import React from 'react';
import { cn } from '@/lib/utils';
import { CheckCircle2 } from 'lucide-react';
import { MetaIcon, GoogleIcon, TwitterIcon, TikTokIcon, SnapchatIcon } from '@/components/platform/PlatformIcons';
import { Linkedin } from 'lucide-react';

interface Platform {
  id: string;
  name: string;
  icon: React.ReactNode;
  color: string;
  disabled?: boolean;
}

const platforms: Platform[] = [
  {
    id: 'meta',
    name: 'Meta',
    icon: <MetaIcon />,
    color: 'bg-blue-500'
  }, 
  {
    id: 'twitter',
    name: 'X (Twitter)',
    icon: <TwitterIcon />,
    color: 'bg-black'
  },
  {
    id: 'google',
    name: 'Google',
    icon: <GoogleIcon />,
    color: 'bg-white border border-gray-200'
  }, 
  {
    id: 'linkedin',
    name: 'LinkedIn',
    icon: <div className="flex items-center justify-center w-full h-full"><Linkedin className="w-5 h-5" /></div>,
    color: 'bg-blue-700'
  }, 
  {
    id: 'tiktok',
    name: 'TikTok',
    icon: <TikTokIcon />,
    color: 'bg-pink-500'
  }, 
  {
    id: 'snapchat',
    name: 'Snapchat',
    icon: <SnapchatIcon />,
    color: 'bg-yellow-400'
  }
];

interface PlatformSelectorProps {
  value: string[];
  onChange: (value: string[]) => void;
}

const PlatformSelector: React.FC<PlatformSelectorProps> = ({
  value,
  onChange
}) => {
  const togglePlatform = (platformId: string) => {
    if (value.includes(platformId)) {
      onChange(value.filter(id => id !== platformId));
    } else {
      onChange([...value, platformId]);
    }
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 animate-fade-in">
      {platforms.map(platform => {
        const isSelected = value.includes(platform.id);

        return (
          <div
            key={platform.id}
            className={cn(
              "relative flex items-center p-4 rounded-lg border-2 transition-all duration-200",
              "cursor-pointer hover:border-primary/50",
              platform.disabled ? "opacity-50 cursor-not-allowed" : "",
              isSelected ? "border-primary bg-primary/5" : "border-border"
            )}
            onClick={() => !platform.disabled && togglePlatform(platform.id)}
          >
            <div
              className={cn(
                "flex items-center justify-center w-10 h-10 rounded-full overflow-hidden text-white mr-3",
                platform.color
              )}
            >
              {platform.icon}
            </div>
            <div>
              <h3 className="font-medium text-sm">{platform.name}</h3>
              <p className="text-xs text-muted-foreground mt-0.5 text-left">
                {platform.disabled
                  ? "Not connected"
                  : isSelected
                    ? "Selected"
                    : "Click to select"}
              </p>
            </div>
            {isSelected && (
              <CheckCircle2 className="w-5 h-5 text-primary absolute top-2 right-2" />
            )}
          </div>
        );
      })}
    </div>
  );
};

export default PlatformSelector;
