
import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, BarChart3, LineChart, PieChart, Users } from 'lucide-react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import AnimatedTransition from '@/components/ui/AnimatedTransition';
import { Badge } from '@/components/ui/badge';
import { Table, TableHeader, TableHead, TableRow, TableBody, TableCell } from '@/components/ui/table';
import PerformanceCharts from '@/components/analytics/PerformanceCharts';

// Mock campaign data - in a real app, you would fetch this based on the ID
const campaignData = {
  'camp-001': {
    id: 'camp-001',
    name: 'Senior Frontend Developer',
    status: 'Active',
    startDate: '2023-10-15',
    endDate: '2023-11-15',
    platforms: ['LinkedIn', 'Indeed', 'Glassdoor'],
    metrics: {
      views: 45200,
      clicks: 3240,
      applications: 128,
      ctr: 7.2,
      cvr: 3.9,
      costPerClick: 2.45,
      costPerApplication: 62
    },
    daily: [
      { date: '2023-10-15', views: 1500, clicks: 120, applications: 5 },
      { date: '2023-10-16', views: 1800, clicks: 145, applications: 6 },
      { date: '2023-10-17', views: 2200, clicks: 175, applications: 7 },
      { date: '2023-10-18', views: 2100, clicks: 168, applications: 8 },
      { date: '2023-10-19', views: 2300, clicks: 182, applications: 9 }
    ]
  },
  'camp-002': {
    id: 'camp-002',
    name: 'UX/UI Designer',
    status: 'Active',
    startDate: '2023-09-01',
    endDate: '2023-10-01',
    platforms: ['Behance', 'LinkedIn', 'Dribbble'],
    metrics: {
      views: 32800,
      clicks: 2180,
      applications: 95,
      ctr: 6.6,
      cvr: 4.4,
      costPerClick: 1.95,
      costPerApplication: 45
    },
    daily: [
      { date: '2023-09-01', views: 1100, clicks: 75, applications: 3 },
      { date: '2023-09-02', views: 1300, clicks: 88, applications: 4 },
      { date: '2023-09-03', views: 1500, clicks: 98, applications: 5 },
      { date: '2023-09-04', views: 1450, clicks: 95, applications: 4 },
      { date: '2023-09-05', views: 1600, clicks: 105, applications: 6 }
    ]
  },
  'camp-003': {
    id: 'camp-003',
    name: 'Product Manager',
    status: 'Paused',
    startDate: '2023-08-15',
    endDate: '2023-09-15',
    platforms: ['LinkedIn', 'AngelList', 'ProductHunt'],
    metrics: {
      views: 78500,
      clicks: 5740,
      applications: 210,
      ctr: 7.3,
      cvr: 3.7,
      costPerClick: 2.75,
      costPerApplication: 75
    },
    daily: [
      { date: '2023-08-15', views: 2600, clicks: 195, applications: 7 },
      { date: '2023-08-16', views: 2850, clicks: 210, applications: 8 },
      { date: '2023-08-17', views: 3100, clicks: 225, applications: 8 },
      { date: '2023-08-18', views: 3050, clicks: 220, applications: 9 },
      { date: '2023-08-19', views: 3200, clicks: 235, applications: 10 }
    ]
  },
  'camp-004': {
    id: 'camp-004',
    name: 'Full Stack Developer',
    status: 'Active',
    startDate: '2023-11-01',
    endDate: '2023-12-01',
    platforms: ['GitHub Jobs', 'Stack Overflow', 'LinkedIn'],
    metrics: {
      views: 54300,
      clicks: 3980,
      applications: 155,
      ctr: 7.3,
      cvr: 3.9,
      costPerClick: 2.15,
      costPerApplication: 55
    },
    daily: [
      { date: '2023-11-01', views: 1800, clicks: 135, applications: 5 },
      { date: '2023-11-02', views: 2000, clicks: 150, applications: 6 },
      { date: '2023-11-03', views: 2200, clicks: 165, applications: 7 },
      { date: '2023-11-04', views: 2150, clicks: 160, applications: 6 },
      { date: '2023-11-05', views: 2300, clicks: 170, applications: 7 }
    ]
  },
  'camp-005': {
    id: 'camp-005',
    name: 'Data Scientist',
    status: 'Completed',
    startDate: '2023-07-01',
    endDate: '2023-08-01',
    platforms: ['Kaggle', 'LinkedIn', 'Indeed'],
    metrics: {
      views: 28700,
      clicks: 1850,
      applications: 82,
      ctr: 6.4,
      cvr: 4.4,
      costPerClick: 2.05,
      costPerApplication: 47
    },
    daily: [
      { date: '2023-07-01', views: 950, clicks: 62, applications: 3 },
      { date: '2023-07-02', views: 1050, clicks: 68, applications: 3 },
      { date: '2023-07-03', views: 1150, clicks: 75, applications: 4 },
      { date: '2023-07-04', views: 1100, clicks: 72, applications: 3 },
      { date: '2023-07-05', views: 1200, clicks: 78, applications: 4 }
    ]
  }
};

const CampaignAnalytics: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  // Get campaign data based on ID
  const campaign = id ? campaignData[id as keyof typeof campaignData] : null;
  
  if (!campaign) {
    return (
      <div className="container max-w-7xl mx-auto py-6 px-4 md:px-6 lg:py-10">
        <Card>
          <CardContent className="flex flex-col items-center justify-center p-6">
            <h2 className="text-xl font-semibold mb-4">Campaign not found</h2>
            <p className="text-muted-foreground mb-6">The campaign you're looking for doesn't exist or has been removed.</p>
            <Button onClick={() => navigate('/analytics')}>
              <ArrowLeft className="mr-2 h-4 w-4" /> Back to Analytics
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      'Active': { variant: 'default', className: 'bg-green-500/20 text-green-600 hover:bg-green-500/30' },
      'Paused': { variant: 'outline', className: 'bg-amber-500/10 text-amber-600 hover:bg-amber-500/20' },
      'Completed': { variant: 'secondary', className: 'bg-blue-500/10 text-blue-600 hover:bg-blue-500/20' }
    };
    
    return (
      <Badge variant={variants[status]?.variant || 'default'} className={variants[status]?.className}>
        {status}
      </Badge>
    );
  };
  
  return (
    <div className="container max-w-7xl mx-auto py-6 px-4 md:px-6 lg:py-10 space-y-6">
      <AnimatedTransition type="fade">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => navigate('/analytics')}>
              <ArrowLeft className="h-4 w-4 mr-1" /> Back
            </Button>
            <h1 className="text-2xl font-bold">Campaign Analysis</h1>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              Export
            </Button>
            <Button variant="outline" size="sm">
              Share
            </Button>
          </div>
        </div>
      </AnimatedTransition>
      
      <AnimatedTransition type="slide-up" delay={0.1}>
        <Card>
          <CardHeader className="pb-3">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between">
              <div>
                <CardTitle>{campaign.name}</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  {campaign.startDate} to {campaign.endDate}
                </p>
              </div>
              <div className="mt-2 md:mt-0">
                {getStatusBadge(campaign.status)}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <Card className="bg-primary/5">
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Views</p>
                      <h3 className="text-2xl font-bold mt-1">{campaign.metrics.views.toLocaleString()}</h3>
                    </div>
                    <div className="p-2 rounded-full bg-primary/10">
                      <Users className="h-5 w-5 text-primary" />
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-primary/5">
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Clicks</p>
                      <h3 className="text-2xl font-bold mt-1">{campaign.metrics.clicks.toLocaleString()}</h3>
                    </div>
                    <div className="p-2 rounded-full bg-primary/10">
                      <BarChart3 className="h-5 w-5 text-primary" />
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-primary/5">
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">CTR</p>
                      <h3 className="text-2xl font-bold mt-1">{campaign.metrics.ctr}%</h3>
                    </div>
                    <div className="p-2 rounded-full bg-primary/10">
                      <LineChart className="h-5 w-5 text-primary" />
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-primary/5">
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Applications</p>
                      <h3 className="text-2xl font-bold mt-1">{campaign.metrics.applications}</h3>
                    </div>
                    <div className="p-2 rounded-full bg-primary/10">
                      <PieChart className="h-5 w-5 text-primary" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            <div>
              <h3 className="text-lg font-medium mb-3">Platforms</h3>
              <div className="flex flex-wrap gap-2 mb-6">
                {campaign.platforms.map((platform, index) => (
                  <Badge key={index} variant="secondary" className="text-sm">
                    {platform}
                  </Badge>
                ))}
              </div>
            </div>
            
            <Separator className="my-6" />
            
            <Tabs defaultValue="performance">
              <TabsList className="mb-4">
                <TabsTrigger value="performance">Performance</TabsTrigger>
                <TabsTrigger value="daily">Daily Trends</TabsTrigger>
                <TabsTrigger value="costs">Costs</TabsTrigger>
              </TabsList>
              
              <TabsContent value="performance">
                <PerformanceCharts />
              </TabsContent>
              
              <TabsContent value="daily">
                <Card>
                  <CardContent className="p-0">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Date</TableHead>
                          <TableHead className="text-right">Views</TableHead>
                          <TableHead className="text-right">Clicks</TableHead>
                          <TableHead className="text-right">Applications</TableHead>
                          <TableHead className="text-right">CTR</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {campaign.daily.map((day, index) => (
                          <TableRow key={index}>
                            <TableCell>{day.date}</TableCell>
                            <TableCell className="text-right">{day.views}</TableCell>
                            <TableCell className="text-right">{day.clicks}</TableCell>
                            <TableCell className="text-right">{day.applications}</TableCell>
                            <TableCell className="text-right">
                              {((day.clicks / day.views) * 100).toFixed(1)}%
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              </TabsContent>
              
              <TabsContent value="costs">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card>
                    <CardContent className="pt-6">
                      <h3 className="text-xl font-bold">
                        ${campaign.metrics.costPerClick.toFixed(2)}
                      </h3>
                      <p className="text-sm text-muted-foreground">Cost per Click</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="pt-6">
                      <h3 className="text-xl font-bold">
                        ${campaign.metrics.costPerApplication.toFixed(2)}
                      </h3>
                      <p className="text-sm text-muted-foreground">Cost per Application</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="pt-6">
                      <h3 className="text-xl font-bold">
                        ${(campaign.metrics.clicks * campaign.metrics.costPerClick).toFixed(2)}
                      </h3>
                      <p className="text-sm text-muted-foreground">Total Spend</p>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </AnimatedTransition>
    </div>
  );
};

export default CampaignAnalytics;
