import React from 'react';
import { getServerSession } from 'next-auth/next';
import { redirect } from 'next/navigation';
import Link from 'next/link';
import { PrismaClient, Platform, Prisma } from '@prisma/client';
import dynamic from 'next/dynamic';

// Dynamic import for client-side components
const CreativeUploader = dynamic(() => import('@/components/creative/CreativeUploader'), { ssr: false });
const PlatformRequirements = dynamic(() => import('@/components/creative/PlatformRequirements'), { ssr: false });

const prisma = new PrismaClient();

interface CampaignCreativesPageProps {
  params: {
    campaignId: string;
  };
}

// Manual type definitions based on Prisma schema
interface Creative {
  id: string;
  name: string;
  originalUrl: string;
  mimeType: string;
  width: number;
  height: number;
  fileSize: number;
  campaignId: string;
  createdAt: Date;
  updatedAt: Date;
}

interface CampaignWithRelations {
  id: string;
  name: string;
  platform: Platform;
  vacancy: {
    title: string;
  };
  creatives: Creative[];
}

// Mock data for when database isn't available
const getMockCampaignData = (campaignId: string): CampaignWithRelations => {
  return {
    id: campaignId,
    name: campaignId === 'campaign-1' ? 'Senior Developer Campaign' : 'UX Designer Campaign',
    platform: campaignId === 'campaign-1' ? 'META' as Platform : 'GOOGLE' as Platform,
    vacancy: {
      title: campaignId === 'campaign-1' ? 'Senior Frontend Developer' : 'UX Designer',
    },
    creatives: campaignId === 'campaign-1' ? [
      {
        id: 'creative-1',
        name: 'Banner Image',
        originalUrl: 'https://via.placeholder.com/1080x1080',
        mimeType: 'image/jpeg',
        width: 1080,
        height: 1080,
        fileSize: 150,
        campaignId: campaignId,
        createdAt: new Date(),
        updatedAt: new Date(),
      }
    ] : [],
  };
};

export default async function CampaignCreativesPage({ params }: CampaignCreativesPageProps) {
  const { campaignId } = params;
  const session = await getServerSession();
  
  if (!session) {
    redirect('/auth/login');
  }
  
  let campaignWithCreatives: CampaignWithRelations;
  
  try {
    // Get campaign details
    const campaign = await prisma.campaign.findUnique({
      where: { id: campaignId },
      include: {
        vacancy: true,
      },
    });
    
    if (!campaign) {
      // For mock campaigns from the creatives page
      if (campaignId === 'campaign-1' || campaignId === 'campaign-2') {
        campaignWithCreatives = getMockCampaignData(campaignId);
      } else {
        redirect('/creatives');
      }
    } else {
      // Fetch creatives separately using raw query to avoid type issues
      const creatives = await prisma.$queryRaw<Creative[]>`
        SELECT id, name, "originalUrl", "mimeType", width, height, "fileSize", "campaignId", "createdAt", "updatedAt"
        FROM "Creative"
        WHERE "campaignId" = ${campaignId}
        ORDER BY "createdAt" DESC
      `;
      
      // Combine the data
      campaignWithCreatives = {
        ...campaign,
        creatives
      };
    }
  } catch (error) {
    console.error('Error fetching campaign:', error);
    // Use mock data since database tables don't exist yet
    campaignWithCreatives = getMockCampaignData(campaignId);
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Link href="/creatives" className="text-blue-600 hover:underline">
          ← Back to Creatives
        </Link>
        
        <h1 className="text-2xl font-bold mt-2">Campaign: {campaignWithCreatives.name}</h1>
        <p className="text-gray-600">
          Vacancy: {campaignWithCreatives.vacancy.title} | Platform: {campaignWithCreatives.platform}
        </p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Upload New Creative</h2>
            <CreativeUploader campaignId={campaignId} />
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Campaign Creatives</h2>
            
            {campaignWithCreatives.creatives.length === 0 ? (
              <div className="text-center py-6">
                <p className="text-gray-500">No creatives uploaded yet</p>
                <p className="text-sm text-gray-400 mt-1">
                  Use the uploader above to add creatives to this campaign
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {campaignWithCreatives.creatives.map((creative) => (
                  <div key={creative.id} className="border border-gray-200 rounded-lg overflow-hidden">
                    <div className="p-3 border-b border-gray-200 bg-gray-50">
                      <h3 className="font-medium">{creative.name}</h3>
                    </div>
                    
                    <div className="p-4">
                      <div className="relative pb-[75%]">
                        <img
                          src={creative.originalUrl}
                          alt={creative.name}
                          className="absolute inset-0 w-full h-full object-contain border border-gray-200"
                        />
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
                          <span className="text-gray-500">Uploaded</span>
                          <p>{new Date(creative.createdAt).toLocaleDateString()}</p>
                        </div>
                      </div>
                      
                      <div className="mt-4 flex justify-end">
                        <Link
                          href={`/creatives/adapt/${creative.id}`}
                          className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                        >
                          Adapt for {campaignWithCreatives.platform}
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6 sticky top-6">
            <h2 className="text-xl font-semibold mb-4">Platform Requirements</h2>
            <p className="text-gray-600 mb-4">
              Requirements for {campaignWithCreatives.platform} platform:
            </p>
            <PlatformRequirements platform={campaignWithCreatives.platform as Platform} />
          </div>
        </div>
      </div>
    </div>
  );
}
