
import React, { ReactNode } from 'react';
import { Linkedin } from 'lucide-react';
import { MetaIcon, GoogleIcon, TikTokIcon, SnapchatIcon, TwitterIcon } from '@/components/platform/PlatformIcons';

export interface Platform {
  id: string;
  name: string;
  icon: ReactNode;
  color: string;
  description: string;
  isConnected: boolean;
}

// Define the platforms
export const platforms: Platform[] = [
  {
    id: 'meta',
    name: 'Meta',
    icon: <MetaIcon />,
    color: 'bg-blue-500',
    description: 'Connect to Facebook Business Manager to post job ads on Facebook and Instagram',
    isConnected: false,
  },
  {
    id: 'twitter',
    name: 'X (Twitter)',
    icon: <TwitterIcon />,
    color: 'bg-black',
    description: 'Connect to X for Business to post job openings as promoted tweets',
    isConnected: false,
  },
  {
    id: 'linkedin',
    name: 'LinkedIn',
    icon: <div className="flex items-center justify-center w-full h-full"><Linkedin className="w-5 h-5" /></div>,
    color: 'bg-blue-700',
    description: 'Post job openings to LinkedIn and target professional audiences',
    isConnected: false,
  },
  {
    id: 'google',
    name: 'Google Ads',
    icon: <GoogleIcon />,
    color: 'bg-white border border-gray-200',
    description: 'Create job campaigns on Google Ads and the Google Display Network',
    isConnected: false,
  },
  {
    id: 'tiktok',
    name: 'TikTok',
    icon: <TikTokIcon />,
    color: 'bg-pink-500',
    description: 'Target younger candidates with TikTok For Business job ads',
    isConnected: false,
  },
  {
    id: 'snapchat',
    name: 'Snapchat',
    icon: <SnapchatIcon />,
    color: 'bg-yellow-400',
    description: 'Reach Gen Z with Snapchat job ads and hiring campaigns',
    isConnected: false,
  },
];
