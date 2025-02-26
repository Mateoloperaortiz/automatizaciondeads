import React from 'react';
import { getServerSession } from 'next-auth/next';
import { redirect } from 'next/navigation';
import Link from 'next/link';
import { PrismaClient, Platform, CampaignStatus } from '@prisma/client';
import PlatformRequirements from '@/components/creative/PlatformRequirements';

const prisma = new PrismaClient();

// Mock data for when database isn't available
const mockCampaigns = [
  {
    id: 'campaign-1',
    name: 'Senior Developer Campaign',
    platform: 'META' as Platform,
    status: 'ACTIVE' as CampaignStatus,
    vacancy: {
      title: 'Senior Frontend Developer',
    },
    creatives: [{ id: 'creative-1' }, { id: 'creative-2' }],
  },
  {
    id: 'campaign-2',
    name: 'UX Designer Campaign',
    platform: 'GOOGLE' as Platform,
    status: 'DRAFT' as CampaignStatus,
    vacancy: {
      title: 'UX Designer',
    },
    creatives: [],
  },
];

export default async function CreativesPage() {
  const session = await getServerSession();
  
  if (!session) {
    redirect('/auth/login');
  }
  
  let campaigns = [];
  
  try {
    // Get all campaigns
    campaigns = await prisma.campaign.findMany({
      orderBy: { createdAt: 'desc' },
      include: {
        vacancy: true,
        creatives: {
          select: {
            id: true,
          },
        },
      },
    });
  } catch (error) {
    console.error('Error fetching campaigns:', error);
    // Use mock data since database tables don't exist yet
    campaigns = mockCampaigns;
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Creative Management</h1>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Campaigns</h2>
            
            {campaigns.length === 0 ? (
              <div className="text-center py-6">
                <p className="text-gray-500">No campaigns found</p>
                <Link
                  href="/campaigns/new"
                  className="mt-2 inline-block text-blue-600 hover:underline"
                >
                  Create a campaign
                </Link>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Campaign</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Platform</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vacancy</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Creatives</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {campaigns.map((campaign) => (
                      <tr key={campaign.id}>
                        <td className="px-4 py-3 whitespace-nowrap">{campaign.name}</td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          {campaign.platform}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          {campaign.vacancy.title}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          {campaign.creatives.length}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            campaign.status === 'ACTIVE'
                              ? 'bg-green-100 text-green-800'
                              : campaign.status === 'DRAFT'
                              ? 'bg-gray-100 text-gray-800'
                              : campaign.status === 'FAILED'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-blue-100 text-blue-800'
                          }`}>
                            {campaign.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-center">
                          <Link
                            href={`/creatives/campaign/${campaign.id}`}
                            className="text-blue-600 hover:text-blue-800 mx-1"
                          >
                            Manage Creatives
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
        
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Platform Requirements</h2>
            <p className="text-gray-600 mb-4">
              Each platform has specific requirements for ad creatives. Make sure your
              creatives meet these requirements to ensure optimal performance.
            </p>
            <PlatformRequirements />
          </div>
        </div>
      </div>
    </div>
  );
}
