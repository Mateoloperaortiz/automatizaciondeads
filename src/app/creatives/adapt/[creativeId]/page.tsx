import React from 'react';
import { getServerSession } from 'next-auth/next';
import { redirect } from 'next/navigation';
import Link from 'next/link';
import { PrismaClient, Platform, AdaptationStatus } from '@prisma/client';
import dynamic from 'next/dynamic';

// Dynamic import for client-side components
const AdaptationPreview = dynamic(() => import('@/components/creative/AdaptationPreview'), { ssr: false });

const prisma = new PrismaClient();

interface CreativeAdaptPageProps {
  params: {
    creativeId: string;
  };
}

export default async function CreativeAdaptPage({ params }: CreativeAdaptPageProps) {
  const { creativeId } = params;
  const session = await getServerSession();
  
  if (!session) {
    redirect('/auth/login');
  }
  
  // Get creative details with campaign
  const creative = await prisma.creative.findUnique({
    where: { id: creativeId },
    include: {
      campaign: true,
      adaptations: {
        include: {
          platformFormat: true,
        },
        orderBy: { createdAt: 'desc' },
      },
    },
  });
  
  if (!creative) {
    redirect('/creatives');
  }
  
  // Get platform formats for this platform
  const platformFormats = await prisma.platformFormat.findMany({
    where: { platform: creative.campaign.platform as Platform },
    orderBy: { formatName: 'asc' },
  });
  
  // For the POC, if there are no adaptations yet, we'll create them on page load
  if (creative.adaptations.length === 0 && platformFormats.length > 0) {
    // This would normally be done via API call, but for simplicity in the POC,
    // we'll do it directly here
    for (const format of platformFormats) {
      const aspectRatioDiff = Math.abs(
        creative.width / creative.height - format.width / format.height
      );
      
      let status: AdaptationStatus;
      if (aspectRatioDiff < 0.01) {
        status = AdaptationStatus.COMPLETED;
      } else if (aspectRatioDiff > 0.2) {
        status = AdaptationStatus.NEEDS_REVIEW;
      } else {
        status = AdaptationStatus.COMPLETED;
      }
      
      // Calculate new dimensions
      let newWidth: number;
      let newHeight: number;
      
      const targetAspectRatio = format.width / format.height;
      
      if (creative.width / creative.height > targetAspectRatio) {
        // Creative is wider, needs cropping on sides
        newWidth = format.width;
        newHeight = Math.round(newWidth / targetAspectRatio);
      } else {
        // Creative is taller, needs padding on sides
        newHeight = format.height;
        newWidth = Math.round(newHeight * targetAspectRatio);
      }
      
      // Calculate new file size (rough estimate)
      const newFileSize = Math.round(
        (creative.fileSize * newWidth * newHeight) / (creative.width * creative.height)
      );
      
      // Generate a mock URL for the adapted image
      const adaptedUrl = `${creative.originalUrl.split('.')[0]}_${format.formatName.toLowerCase().replace(/\s+/g, '_')}_${newWidth}x${newHeight}.${
        creative.originalUrl.split('.')[1]
      }`;
      
      await prisma.creativeAdaptation.create({
        data: {
          adaptedUrl,
          width: newWidth,
          height: newHeight,
          fileSize: newFileSize,
          status,
          creativeId: creative.id,
          platformFormatId: format.id,
        },
      });
    }
    
    // Refresh creative with newly created adaptations
    const refreshedCreative = await prisma.creative.findUnique({
      where: { id: creativeId },
      include: {
        campaign: true,
        adaptations: {
          include: {
            platformFormat: true,
          },
          orderBy: { createdAt: 'desc' },
        },
      },
    });
    
    if (refreshedCreative) {
      creative.adaptations = refreshedCreative.adaptations;
    }
  }
  
  // Group adaptations by status for the UI
  const adaptationsByStatus = {
    completed: creative.adaptations.filter(a => a.status === AdaptationStatus.COMPLETED),
    needsReview: creative.adaptations.filter(a => a.status === AdaptationStatus.NEEDS_REVIEW),
    pending: creative.adaptations.filter(a => a.status === AdaptationStatus.PENDING),
    failed: creative.adaptations.filter(a => a.status === AdaptationStatus.FAILED),
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Link href={`/creatives/campaign/${creative.campaignId}`} className="text-blue-600 hover:underline">
          ← Back to Campaign
        </Link>
        
        <h1 className="text-2xl font-bold mt-2">Adapt Creative: {creative.name}</h1>
        <p className="text-gray-600">
          Platform: {creative.campaign.platform} | Original Size: {creative.width} x {creative.height}
        </p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6 sticky top-6">
            <h2 className="text-xl font-semibold mb-4">Original Creative</h2>
            
            <div className="mb-4">
              <div className="relative pb-[100%]">
                <img
                  src={creative.originalUrl}
                  alt={creative.name}
                  className="absolute inset-0 w-full h-full object-contain border border-gray-200"
                />
              </div>
            </div>
            
            <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-500">Dimensions</span>
                <p>{creative.width} x {creative.height} px</p>
              </div>
              <div>
                <span className="text-gray-500">Size</span>
                <p>{creative.fileSize} KB</p>
              </div>
              <div>
                <span className="text-gray-500">Type</span>
                <p>{creative.mimeType.split('/')[1].toUpperCase()}</p>
              </div>
              <div>
                <span className="text-gray-500">Aspect Ratio</span>
                <p>{(creative.width / creative.height).toFixed(2)}</p>
              </div>
            </div>
            
            <div className="mt-6">
              <h3 className="font-medium mb-2">Adaptation Summary</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Ready:</span>
                  <span className="font-medium text-green-600">{adaptationsByStatus.completed.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Needs Review:</span>
                  <span className="font-medium text-orange-600">{adaptationsByStatus.needsReview.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Processing:</span>
                  <span className="font-medium text-blue-600">{adaptationsByStatus.pending.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Failed:</span>
                  <span className="font-medium text-red-600">{adaptationsByStatus.failed.length}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="lg:col-span-2">
          {adaptationsByStatus.needsReview.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-semibold mb-2 text-orange-700">Needs Review</h2>
              <p className="text-gray-600 mb-4">
                These adaptations require manual review due to significant aspect ratio differences.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {adaptationsByStatus.needsReview.map((adaptation) => (
                  <AdaptationPreview key={adaptation.id} adaptation={adaptation} />
                ))}
              </div>
            </div>
          )}
          
          {adaptationsByStatus.completed.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-semibold mb-2 text-green-700">Ready to Use</h2>
              <p className="text-gray-600 mb-4">
                These adaptations are ready to be used in your campaign.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {adaptationsByStatus.completed.map((adaptation) => (
                  <AdaptationPreview key={adaptation.id} adaptation={adaptation} />
                ))}
              </div>
            </div>
          )}
          
          {adaptationsByStatus.pending.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-semibold mb-2 text-blue-700">Processing</h2>
              <p className="text-gray-600 mb-4">
                These adaptations are currently being processed.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {adaptationsByStatus.pending.map((adaptation) => (
                  <AdaptationPreview key={adaptation.id} adaptation={adaptation} />
                ))}
              </div>
            </div>
          )}
          
          {adaptationsByStatus.failed.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-2 text-red-700">Failed</h2>
              <p className="text-gray-600 mb-4">
                These adaptations failed to process. Please try again or upload a different creative.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {adaptationsByStatus.failed.map((adaptation) => (
                  <AdaptationPreview key={adaptation.id} adaptation={adaptation} />
                ))}
              </div>
            </div>
          )}
          
          {creative.adaptations.length === 0 && (
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <h2 className="text-xl font-semibold mb-4">No Adaptations Available</h2>
              <p className="text-gray-600 mb-4">
                There are no adaptations available for this creative yet.
              </p>
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                onClick={() => window.location.reload()}
              >
                Generate Adaptations
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
