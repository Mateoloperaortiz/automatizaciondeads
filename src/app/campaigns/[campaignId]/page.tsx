import React from 'react';
import Link from 'next/link';
import { getServerSession } from 'next-auth/next';
import { redirect } from 'next/navigation';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// Mock campaign data for the POC
const mockCampaigns = {
  '1': {
    id: '1',
    name: 'Reclutamiento de Verano',
    status: 'ACTIVE',
    startDate: new Date('2025-05-01'),
    endDate: new Date('2025-08-31'),
    budget: 25000,
    goal: 'Contratar 50 empleados temporales para la temporada de verano',
    description: 'Esta campaña busca reclutar personal temporal para nuestras tiendas en todo el país. Necesitamos llenar puestos rápidamente ya que se acerca la temporada de verano, con un enfoque en roles de servicio al cliente, posiciones de almacén y conductores de entrega.',
    targetAudience: 'Estudiantes universitarios y jóvenes profesionales',
    platforms: ['Meta', 'LinkedIn', 'Indeed'],
    progress: 65,
    createdAt: new Date('2025-01-15'),
    updatedAt: new Date('2025-02-20'),
    createdBy: 'Juan Pérez',
    vacancies: [
      { id: '101', title: 'Vendedor', location: 'Bogotá, Colombia', department: 'Ventas', applications: 28 },
      { id: '102', title: 'Asociado de Almacén', location: 'Medellín, Colombia', department: 'Operaciones', applications: 42 },
      { id: '103', title: 'Representante de Servicio al Cliente', location: 'Remoto (Colombia)', department: 'Soporte', applications: 56 },
      { id: '104', title: 'Conductor de Entregas', location: 'Cali, Colombia', department: 'Logística', applications: 31 },
      { id: '105', title: 'Gerente de Tienda', location: 'Barranquilla, Colombia', department: 'Ventas', applications: 15 },
      { id: '106', title: 'Merchandiser', location: 'Cartagena, Colombia', department: 'Ventas', applications: 19 },
    ],
    metrics: {
      totalImpressions: 128500,
      totalClicks: 8640,
      totalApplications: 191,
      averageCPC: 1.85,
      averageCPA: 24.50,
      conversionRate: 2.21,
    },
    platforms_detail: [
      { name: 'Meta', status: 'Connected', impressions: 65200, clicks: 4320, applications: 95, spend: 8120 },
      { name: 'LinkedIn', status: 'Connected', impressions: 42800, clicks: 3120, applications: 68, spend: 9850 },
      { name: 'Indeed', status: 'Connected', impressions: 20500, clicks: 1200, applications: 28, spend: 3120 },
    ]
  },
  '2': {
    id: '2',
    name: 'Reclutamiento de Desarrolladores Senior',
    status: 'ACTIVE',
    startDate: new Date('2025-02-15'),
    endDate: new Date('2025-04-30'),
    budget: 15000,
    goal: 'Contratar 5 desarrolladores senior',
    description: 'Estamos expandiendo nuestro equipo de ingeniería y buscamos desarrolladores senior con experiencia en nuestra pila tecnológica. Estos roles son fundamentales para nuestro próximo lanzamiento de producto y requieren candidatos con fuertes habilidades de resolución de problemas y potencial de liderazgo.',
    targetAudience: 'Desarrolladores senior con 5+ años de experiencia',
    platforms: ['LinkedIn', 'Stack Overflow', 'GitHub'],
    progress: 40,
    createdAt: new Date('2025-01-30'),
    updatedAt: new Date('2025-02-10'),
    createdBy: 'María Rodríguez',
    vacancies: [
      { id: '201', title: 'Desarrollador Frontend Senior', location: 'Bogotá, Colombia', department: 'Ingeniería', applications: 18 },
      { id: '202', title: 'Desarrollador Backend Senior', location: 'Bogotá, Colombia', department: 'Ingeniería', applications: 15 },
      { id: '203', title: 'Ingeniero DevOps', location: 'Remoto (Colombia)', department: 'Infraestructura', applications: 12 },
      { id: '204', title: 'Desarrollador Móvil', location: 'Medellín, Colombia', department: 'Ingeniería', applications: 9 },
      { id: '205', title: 'Ingeniero de QA y Automatización', location: 'Cali, Colombia', department: 'Control de Calidad', applications: 14 },
    ],
    metrics: {
      totalImpressions: 85200,
      totalClicks: 3840,
      totalApplications: 68,
      averageCPC: 2.95,
      averageCPA: 89.70,
      conversionRate: 1.77,
    },
    platforms_detail: [
      { name: 'LinkedIn', status: 'Connected', impressions: 48600, clicks: 2180, applications: 38, spend: 6420 },
      { name: 'Stack Overflow', status: 'Connected', impressions: 26500, clicks: 1250, applications: 22, spend: 4980 },
      { name: 'GitHub', status: 'Connected', impressions: 10100, clicks: 410, applications: 8, spend: 1680 },
    ]
  },
};

export default async function CampaignDetailPage({
  params
}: {
  params: { campaignId: string }
}) {
  const { campaignId } = params;
  const session = await getServerSession();
  
  if (!session) {
    redirect('/auth/login');
  }
  
  let campaign = null;
  
  try {
    // In a real app, we would fetch from the database
    // campaign = await prisma.campaign.findUnique({
    //   where: { id: campaignId },
    //   include: {
    //     vacancies: true,
    //     platformConnections: true,
    //     // etc.
    //   }
    // });
    
    // For the POC, use mock data
    campaign = mockCampaigns[campaignId];
    
    if (!campaign) {
      // If campaign ID doesn't exist in our mock data
      redirect('/campaigns');
    }
  } catch (error) {
    console.error('Error fetching campaign:', error);
    
    // Fall back to mock data
    campaign = mockCampaigns[campaignId];
    
    if (!campaign) {
      // If campaign ID doesn't exist in our mock data
      redirect('/campaigns');
    }
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
      <div className="flex items-center mb-6">
        <Link
          href="/campaigns"
          className="text-gray-600 hover:text-gray-900 mr-4"
        >
          ← Back to Campaigns
        </Link>
        <h1 className="text-2xl font-bold">{campaign.name}</h1>
        <span className={`ml-4 px-3 py-1 rounded-full text-sm ${getStatusClass(campaign.status)}`}>
          {campaign.status}
        </span>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-xl font-semibold mb-2">Campaign Overview</h2>
                <p className="text-gray-600">{campaign.goal}</p>
              </div>
              <div className="flex space-x-2">
                <Link
                  href={`/campaigns/${campaign.id}/edit`}
                  className="px-3 py-1 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-50 transition"
                >
                  Edit
                </Link>
                <Link
                  href={`/campaigns/${campaign.id}/metrics`}
                  className="px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition"
                >
                  View Metrics
                </Link>
              </div>
            </div>
            
            <div className="mb-6">
              <div className="flex justify-between text-sm mb-1">
                <span>Campaign Progress</span>
                <span>{campaign.progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  className="bg-indigo-600 h-2.5 rounded-full"
                  style={{ width: `${campaign.progress}%` }}
                ></div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="p-3 bg-gray-50 rounded-md">
                <p className="text-xs text-gray-500">Start Date</p>
                <p className="font-medium">{new Date(campaign.startDate).toLocaleDateString()}</p>
              </div>
              <div className="p-3 bg-gray-50 rounded-md">
                <p className="text-xs text-gray-500">End Date</p>
                <p className="font-medium">{new Date(campaign.endDate).toLocaleDateString()}</p>
              </div>
              <div className="p-3 bg-gray-50 rounded-md">
                <p className="text-xs text-gray-500">Budget</p>
                <p className="font-medium">${campaign.budget.toLocaleString()}</p>
              </div>
              <div className="p-3 bg-gray-50 rounded-md">
                <p className="text-xs text-gray-500">Connected Platforms</p>
                <p className="font-medium">{campaign.platforms.length}</p>
              </div>
            </div>
            
            <div className="mb-6">
              <h3 className="text-lg font-medium mb-2">Campaign Description</h3>
              <p className="text-gray-600">{campaign.description}</p>
            </div>
            
            <div className="mb-6">
              <h3 className="text-lg font-medium mb-2">Target Audience</h3>
              <p className="text-gray-600">{campaign.targetAudience}</p>
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium">Platform Performance</h3>
                <Link
                  href={`/campaigns/${campaign.id}/platforms`}
                  className="text-sm text-indigo-600 hover:text-indigo-800"
                >
                  View All
                </Link>
              </div>
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Platform</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Impressions</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Clicks</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Applications</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Spend</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {campaign.platforms_detail.map((platform) => (
                      <tr key={platform.name}>
                        <td className="px-4 py-3 whitespace-nowrap font-medium">{platform.name}</td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <span className="px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                            {platform.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right whitespace-nowrap">{platform.impressions.toLocaleString()}</td>
                        <td className="px-4 py-3 text-right whitespace-nowrap">{platform.clicks.toLocaleString()}</td>
                        <td className="px-4 py-3 text-right whitespace-nowrap">{platform.applications}</td>
                        <td className="px-4 py-3 text-right whitespace-nowrap">${platform.spend.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
        
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium">Vacancies</h3>
              <Link
                href={`/campaigns/${campaign.id}/vacancies`}
                className="text-sm text-indigo-600 hover:text-indigo-800"
              >
                View All
              </Link>
            </div>
            
            <div className="space-y-3">
              {campaign.vacancies.slice(0, 5).map((vacancy) => (
                <Link key={vacancy.id} href={`/vacancies/${vacancy.id}`}>
                  <div className="p-3 rounded-md hover:bg-gray-50 transition">
                    <div className="flex justify-between">
                      <h4 className="font-medium text-gray-900">{vacancy.title}</h4>
                      <span className="text-sm text-indigo-600">{vacancy.applications}</span>
                    </div>
                    <div className="flex space-x-2 text-xs text-gray-500 mt-1">
                      <span>{vacancy.location}</span>
                      <span>•</span>
                      <span>{vacancy.department}</span>
                    </div>
                  </div>
                </Link>
              ))}
              
              {campaign.vacancies.length > 5 && (
                <div className="text-center mt-2">
                  <Link
                    href={`/campaigns/${campaign.id}/vacancies`}
                    className="text-sm text-indigo-600 hover:text-indigo-800"
                  >
                    +{campaign.vacancies.length - 5} more vacancies
                  </Link>
                </div>
              )}
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="text-lg font-medium mb-4">Campaign Metrics</h3>
            
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Impressions</span>
                  <span>{campaign.metrics.totalImpressions.toLocaleString()}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: '75%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Clicks</span>
                  <span>{campaign.metrics.totalClicks.toLocaleString()}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div className="bg-green-500 h-1.5 rounded-full" style={{ width: '60%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Applications</span>
                  <span>{campaign.metrics.totalApplications}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: '45%' }}></div>
                </div>
              </div>
              
              <div className="pt-4 border-t border-gray-200">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">Avg. CPC</p>
                    <p className="font-medium">${campaign.metrics.averageCPC.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Avg. CPA</p>
                    <p className="font-medium">${campaign.metrics.averageCPA.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Conversion Rate</p>
                    <p className="font-medium">{campaign.metrics.conversionRate.toFixed(2)}%</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Total Cost</p>
                    <p className="font-medium">
                      ${campaign.platforms_detail.reduce((sum, p) => sum + p.spend, 0).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-medium mb-4">Campaign Details</h3>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Created</span>
                <span>{new Date(campaign.createdAt).toLocaleDateString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Last Updated</span>
                <span>{new Date(campaign.updatedAt).toLocaleDateString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Created By</span>
                <span>{campaign.createdBy}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Campaign ID</span>
                <span className="font-mono">{campaign.id}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
