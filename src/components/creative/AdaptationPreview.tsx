import React from 'react';
import { CreativeAdaptation, PlatformFormat, AdaptationStatus, Platform } from '@prisma/client';

interface AdaptationPreviewProps {
  adaptation: CreativeAdaptation & { platformFormat: PlatformFormat };
}

export default function AdaptationPreview({ adaptation }: AdaptationPreviewProps) {
  const { platformFormat, status } = adaptation;
  
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
  
  const getStatusBadgeColor = (status: AdaptationStatus) => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-green-100 text-green-800';
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-800';
      case 'FAILED':
        return 'bg-red-100 text-red-800';
      case 'NEEDS_REVIEW':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  const getStatusLabel = (status: AdaptationStatus) => {
    switch (status) {
      case 'COMPLETED':
        return 'Ready';
      case 'PENDING':
        return 'Processing';
      case 'FAILED':
        return 'Failed';
      case 'NEEDS_REVIEW':
        return 'Needs Review';
      default:
        return status;
    }
  };
  
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <div className="p-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
        <div>
          <span className="font-medium">
            {getPlatformName(platformFormat.platform)} - {platformFormat.formatName}
          </span>
          <p className="text-sm text-gray-500">
            {platformFormat.width} x {platformFormat.height} px
            ({platformFormat.aspectRatio})
          </p>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadgeColor(status)}`}>
          {getStatusLabel(status)}
        </span>
      </div>
      
      <div className="p-4">
        <div className="relative" style={{ 
          paddingBottom: `${(platformFormat.height / platformFormat.width) * 100}%`
        }}>
          <img
            src={adaptation.adaptedUrl}
            alt={`${platformFormat.platform} ${platformFormat.formatName} adaptation`}
            className="absolute inset-0 w-full h-full object-contain border border-gray-200"
          />
        </div>
        
        <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="text-gray-500">Dimensions</span>
            <p>{adaptation.width} x {adaptation.height} px</p>
          </div>
          <div>
            <span className="text-gray-500">File Size</span>
            <p>{adaptation.fileSize} KB</p>
          </div>
        </div>
        
        {status === 'NEEDS_REVIEW' && (
          <div className="mt-3 p-2 bg-orange-50 border border-orange-200 rounded text-sm">
            <p className="font-medium text-orange-800">Adaptation requires review</p>
            <p className="text-orange-700">
              The original image's aspect ratio is significantly different from this format.
              Manual cropping may be needed for optimal results.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
