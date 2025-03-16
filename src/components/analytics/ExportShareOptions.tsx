
import React, { useState } from 'react';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle 
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Share, Download, Copy, Mail, FileText, BarChart } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';

interface ExportShareOptionsProps {
  className?: string;
  dateRange: {
    startDate: Date;
    endDate: Date;
    label: string;
  };
}

const ExportShareOptions: React.FC<ExportShareOptionsProps> = ({ className, dateRange }) => {
  const { toast } = useToast();
  const [shareDialogOpen, setShareDialogOpen] = useState(false);
  const [email, setEmail] = useState('');
  
  const exportAsPDF = () => {
    toast({
      title: "Exporting PDF",
      description: `Analytics for ${dateRange.label} being exported as PDF`,
    });
    // In a real app, this would generate and download a PDF
  };
  
  const exportAsCSV = () => {
    toast({
      title: "Exporting CSV",
      description: `Analytics data for ${dateRange.label} being exported as CSV`,
    });
    // In a real app, this would generate and download a CSV file
  };
  
  const copyShareLink = () => {
    // Create a shareable link with date range parameters
    const baseUrl = window.location.origin + window.location.pathname;
    const shareUrl = `${baseUrl}?start=${dateRange.startDate.toISOString()}&end=${dateRange.endDate.toISOString()}`;
    
    navigator.clipboard.writeText(shareUrl).then(() => {
      toast({
        title: "Link Copied",
        description: "Shareable link copied to clipboard",
      });
    });
  };
  
  const sendEmailReport = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Email validation
    if (!email || !email.includes('@')) {
      toast({
        title: "Invalid Email",
        description: "Please enter a valid email address",
        variant: "destructive",
      });
      return;
    }
    
    toast({
      title: "Report Sent",
      description: `Analytics report for ${dateRange.label} has been sent to ${email}`,
    });
    
    setShareDialogOpen(false);
    setEmail('');
  };
  
  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" className={className}>
            <Share className="mr-2 h-4 w-4" />
            Export / Share
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56 bg-background border border-border">
          <DropdownMenuLabel>Export Options</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={exportAsPDF}>
            <FileText className="mr-2 h-4 w-4" />
            Export as PDF
          </DropdownMenuItem>
          <DropdownMenuItem onClick={exportAsCSV}>
            <BarChart className="mr-2 h-4 w-4" />
            Export as CSV
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuLabel>Share Options</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={copyShareLink}>
            <Copy className="mr-2 h-4 w-4" />
            Copy Share Link
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setShareDialogOpen(true)}>
            <Mail className="mr-2 h-4 w-4" />
            Email Report
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      
      <Dialog open={shareDialogOpen} onOpenChange={setShareDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Share Analytics Report</DialogTitle>
            <DialogDescription>
              Send an analytics report for {dateRange.label} via email.
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={sendEmailReport} className="space-y-4 py-4">
            <div className="flex flex-col space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Recipient Email
              </label>
              <Input 
                id="email"
                type="email" 
                placeholder="colleague@company.com" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                className="col-span-3"
              />
            </div>
            
            <DialogFooter className="sm:justify-start">
              <Button type="submit" className="mt-2">
                Send Report
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ExportShareOptions;
