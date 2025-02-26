import React from 'react';
import Link from 'next/link';
import { getServerSession } from 'next-auth/next';
import { redirect } from 'next/navigation';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// Mock campaign data for the POC
const mockCampaigns = [
  {
    id: '1',
    name: 'Reclutamiento de Verano',
    status: 'ACTIVE',
    startDate: new Date('2025-05-01'),
    endDate: new Date('2025-08-31'),
    budget: 25000,
    goal: 'Contratar 50 empleados temporales para la temporada de verano',
    targetAudience: 'Estudiantes universitarios y jóvenes profesionales',
    platforms: ['Meta', 'LinkedIn', 'Indeed'],
    progress: 65,
    vacancyCount: 6,
    creativeCount: 12,
  },
  {
    id: '2',
    name: 'Reclutamiento de Desarrolladores Senior',
    status: 'ACTIVE',
    startDate: new Date('2025-02-15'),
    endDate: new Date('2025-04-30'),
    budget: 15000,
    goal: 'Contratar 5 desarrolladores con experiencia',
    targetAudience: 'Desarrolladores senior con 5+ años de experiencia',
    platforms: ['LinkedIn', 'Stack Overflow', 'GitHub'],
    progress: 40,
    vacancyCount: 5,
    creativeCount: 8,
  },
  {
    id: '3',
    name: 'Expansión del Equipo de Marketing',
    status: 'PLANNING',
    startDate: new Date('2025-04-01'),
    endDate: new Date('2025-06-30'),
    budget: 18000,
    goal: 'Construir el departamento de marketing con 8 nuevos roles',
    targetAudience: 'Profesionales de marketing con experiencia diversa',
    platforms: ['LinkedIn', 'Meta', 'Twitter'],
    progress: 15,
    vacancyCount: 8,
    creativeCount: 4,
  },
  {
    id: '4',
    name: 'Soporte al Cliente Remoto',
    status: 'ACTIVE',
    startDate: new Date('2025-01-10'),
    endDate: new Date('2025-03-15'),
    budget: 12000,
    goal: 'Contratar 15 especialistas de soporte al cliente remoto',
    targetAudience: 'Profesionales de servicio al cliente que buscan oportunidades remotas',
    platforms: ['Indeed', 'LinkedIn', 'ZipRecruiter'],
    progress: 80,
    vacancyCount: 15,
    creativeCount: 10,
  },
  {
    id: '5',
    name: 'Reclutamiento de Equipo de Ventas',
    status: 'COMPLETED',
    startDate: new Date('2024-11-01'),
    endDate: new Date('2025-01-31'),
    budget: 20000,
    goal: 'Expandir el equipo de ventas con 10 nuevos representantes',
    targetAudience: 'Profesionales de ventas con experiencia',
    platforms: ['LinkedIn', 'Meta', 'SalesJobs'],
    progress: 100,
    vacancyCount: 10,
    creativeCount: 15,
  },
];

export default async function CampaignsPage() {
  const session = await getServerSession();
  
  if (!session) {
    redirect('/auth/login');
  }
  
  let campaigns = [];
  
  try {
    // In a real app, we would fetch from the database
    // campaigns = await prisma.campaign.findMany({
    //   orderBy: { createdAt: 'desc' },
    // });
    
    // For the POC, use mock data
    campaigns = mockCampaigns;
  } catch (error) {
    console.error('Error fetching campaigns:', error);
    // Fall back to mock data
    campaigns = mockCampaigns;
  }

  // Helper function to get status class
  const getStatusClass = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'bg-green-100 text-green-800';
      case 'PLANNING':
        return 'bg-blue-100 text-blue-800';
      case 'PAUSED':
        return 'bg-yellow-100 text-yellow-800';
      case 'COMPLETED':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Campaigns</h1>
        <Link
          href="/campaigns/new"
          className="bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition"
        >
          Create Campaign
        </Link>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {campaigns.map((campaign) => (
          <Link key={campaign.id} href={`/campaigns/${campaign.id}`}>
            <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition cursor-pointer h-full">
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <h2 className="text-xl font-semibold mb-2">{campaign.name}</h2>
                  <span className={`px-2 py-1 rounded-full text-xs ${getStatusClass(campaign.status)}`}>
                    {campaign.status}
                  </span>
                </div>
                
                <p className="text-gray-600 text-sm mb-4">{campaign.goal}</p>
                
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-500 mb-1">
                    <span>Progress</span>
                    <span>{campaign.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-indigo-600 h-2 rounded-full"
                      style={{ width: `${campaign.progress}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-gray-500 text-xs">Start Date</p>
                    <p className="font-medium">
                      {new Date(campaign.startDate).toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500 text-xs">End Date</p>
                    <p className="font-medium">
                      {new Date(campaign.endDate).toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500 text-xs">Budget</p>
                    <p className="font-medium">${campaign.budget.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-gray-500 text-xs">Platforms</p>
                    <p className="font-medium">{campaign.platforms.length}</p>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <div className="text-center px-3 py-2 bg-gray-100 rounded-md flex-1">
                    <p className="text-sm font-semibold">{campaign.vacancyCount}</p>
                    <p className="text-xs text-gray-500">Vacancies</p>
                  </div>
                  <div className="text-center px-3 py-2 bg-gray-100 rounded-md flex-1">
                    <p className="text-sm font-semibold">{campaign.creativeCount}</p>
                    <p className="text-xs text-gray-500">Creatives</p>
                  </div>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
