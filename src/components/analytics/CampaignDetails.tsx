
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import AnimatedTransition from '@/components/ui/AnimatedTransition';
import { Badge } from '@/components/ui/badge';
import { useIsMobile } from '@/hooks/use-mobile';
import { useNavigate } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

// Campaign data
const campaignPerformance = [
  { id: 'camp-001', name: 'Senior Frontend Developer', views: 45200, clicks: 3240, conversions: 128, ctr: 7.2, cvr: 3.9, status: 'Active' },
  { id: 'camp-002', name: 'UX/UI Designer', views: 32800, clicks: 2180, conversions: 95, ctr: 6.6, cvr: 4.4, status: 'Active' },
  { id: 'camp-003', name: 'Product Manager', views: 78500, clicks: 5740, conversions: 210, ctr: 7.3, cvr: 3.7, status: 'Paused' },
  { id: 'camp-004', name: 'Full Stack Developer', views: 54300, clicks: 3980, conversions: 155, ctr: 7.3, cvr: 3.9, status: 'Active' },
  { id: 'camp-005', name: 'Data Scientist', views: 28700, clicks: 1850, conversions: 82, ctr: 6.4, cvr: 4.4, status: 'Completed' }
];

const CampaignDetails: React.FC = () => {
  const isMobile = useIsMobile();
  const navigate = useNavigate();
  
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
  
  const handleCampaignClick = (campaignId: string) => {
    navigate(`/analytics/campaign/${campaignId}`);
  };
  
  return (
    <AnimatedTransition type="slide-up" delay={0.5}>
      <Card className="hover-lift">
        <CardHeader className="pb-3">
          <CardTitle>Campaign Performance Details</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="performance">
            <TabsList className="mb-4 w-full sm:w-auto">
              <TabsTrigger value="performance" className="flex-1 sm:flex-initial">Performance</TabsTrigger>
              <TabsTrigger value="conversions" className="flex-1 sm:flex-initial">Conversions</TabsTrigger>
            </TabsList>
            
            <TabsContent value="performance">
              <div className="overflow-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Campaign Name</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Views</TableHead>
                      <TableHead className="text-right">Clicks</TableHead>
                      <TableHead className="text-right">CTR (%)</TableHead>
                      <TableHead className="w-[50px]"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {campaignPerformance.map((campaign, index) => (
                      <TableRow 
                        key={index}
                        onClick={() => handleCampaignClick(campaign.id)}
                        className="cursor-pointer hover:bg-muted"
                      >
                        <TableCell className="font-medium">{campaign.name}</TableCell>
                        <TableCell>{getStatusBadge(campaign.status)}</TableCell>
                        <TableCell className="text-right">{campaign.views.toLocaleString()}</TableCell>
                        <TableCell className="text-right">{campaign.clicks.toLocaleString()}</TableCell>
                        <TableCell className="text-right font-medium">{campaign.ctr}%</TableCell>
                        <TableCell>
                          <ChevronRight className="h-4 w-4 text-muted-foreground" />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </TabsContent>
            
            <TabsContent value="conversions">
              <div className="overflow-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Campaign Name</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Conversions</TableHead>
                      <TableHead className="text-right">CVR (%)</TableHead>
                      <TableHead className="text-right">Cost per Conv.</TableHead>
                      <TableHead className="w-[50px]"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {campaignPerformance.map((campaign, index) => (
                      <TableRow 
                        key={index}
                        onClick={() => handleCampaignClick(campaign.id)}
                        className="cursor-pointer hover:bg-muted"
                      >
                        <TableCell className="font-medium">{campaign.name}</TableCell>
                        <TableCell>{getStatusBadge(campaign.status)}</TableCell>
                        <TableCell className="text-right">{campaign.conversions}</TableCell>
                        <TableCell className="text-right font-medium">{campaign.cvr}%</TableCell>
                        <TableCell className="text-right">${Math.round(45 + Math.random() * 30)}</TableCell>
                        <TableCell>
                          <ChevronRight className="h-4 w-4 text-muted-foreground" />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </AnimatedTransition>
  );
};

export default CampaignDetails;
