'use client'

import React, { useState, useEffect } from 'react';
import { Platform, PlatformFormat } from '@prisma/client';

interface PlatformRequirementsProps {
  platform?: Platform;
}

// Mock platform format data
const mockPlatformFormats = [
  {
    id: 'format-1',
    platform: 'META' as Platform,
    formatName: 'Feed Image',
    width: 1080,
    height: 1080,
    aspectRatio: '1:1',
    maxFileSize: 4000,
    supportedTypes: ['jpg', 'png'],
    textMaxLength: 125,
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    id: 'format-2',
    platform: 'META' as Platform,
    formatName: 'Story Image',
    width: 1080,
    height: 1920,
    aspectRatio: '9:16',
    maxFileSize: 4000,
    supportedTypes: ['jpg', 'png'],
    textMaxLength: 125,
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    id: 'format-3',
    platform: 'GOOGLE' as Platform,
    formatName: 'Display Ad',
    width: 336,
    height: 280,
    aspectRatio: '6:5',
    maxFileSize: 2000,
    supportedTypes: ['jpg', 'png', 'gif'],
    textMaxLength: 90,
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    id: 'format-4',
    platform: 'GOOGLE' as Platform,
    formatName: 'Responsive Ad',
    width: 1200,
    height: 628,
    aspectRatio: '1.91:1',
    maxFileSize: 5000,
    supportedTypes: ['jpg', 'png'],
    textMaxLength: 90,
    createdAt: new Date(),
    updatedAt: new Date(),
  }
];

export default function PlatformRequirements({ platform }: PlatformRequirementsProps) {
  const [formats, setFormats] = useState<PlatformFormat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFormats = async () => {
      try {
        setLoading(true);
        const url = platform
          ? `/api/platform-formats?platform=${platform}`
          : '/api/platform-formats';
        
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error('Failed to fetch platform formats');
        }
        
        const data = await response.json();
        setFormats(data);
      } catch (err) {
        console.error('Error fetching platform formats:', err);
        setError('Using mock platform requirements data');
        
        // Use mock data if API call fails
        if (platform) {
          setFormats(mockPlatformFormats.filter(format => format.platform === platform));
        } else {
          setFormats(mockPlatformFormats);
        }
      } finally {
        setLoading(false);
      }
    };
    
    fetchFormats();
  }, [platform]);
  
  const getPlatformName = (platform: Platform) => {
    const names = {
      META: 'Meta',
      GOOGLE: 'Google Ads',
      TWITTER: 'Twitter',
      TIKTOK: 'TikTok',
      SNAPCHAT: 'Snapchat',
    };
    return names[platform] || platform;
  };
  
  // Group formats by platform
  const formatsByPlatform = formats.reduce((acc, format) => {
    if (!acc[format.platform]) {
      acc[format.platform] = [];
    }
    acc[format.platform].push(format);
    return acc;
  }, {} as Record<Platform, PlatformFormat[]>);
  
  if (loading) {
    return <div className="p-4 text-center">Loading platform requirements...</div>;
  }
  
  if (error) {
    return <div className="p-4 text-red-500">{error}</div>;
  }
  
  if (formats.length === 0) {
    return <div className="p-4 text-center">No platform requirements found.</div>;
  }
  
  return (
    <div className="space-y-6">
      {Object.entries(formatsByPlatform).map(([platformKey, platformFormats]) => (
        <div key={platformKey} className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="bg-gray-50 px-4 py-3 border-b">
            <h3 className="text-lg font-medium">
              {getPlatformName(platformKey as Platform)} Requirements
            </h3>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Format</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dimensions</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Aspect Ratio</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Max Size</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">File Types</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Text Limit</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {platformFormats.map((format) => (
                  <tr key={format.id}>
                    <td className="px-4 py-3 whitespace-nowrap">{format.formatName}</td>
                    <td className="px-4 py-3 whitespace-nowrap">{format.width} x {format.height}</td>
                    <td className="px-4 py-3 whitespace-nowrap">{format.aspectRatio}</td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {format.maxFileSize >= 1024
                        ? `${(format.maxFileSize / 1024).toFixed(1)} MB`
                        : `${format.maxFileSize} KB`}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {format.supportedTypes.join(', ')}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {format.textMaxLength ? `${format.textMaxLength} chars` : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}
