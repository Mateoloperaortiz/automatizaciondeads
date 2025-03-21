
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Loader2, Sparkles, CheckCircle } from 'lucide-react';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { optimizeJobDescription } from '@/services/optimizationService';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';

interface OptimizationResult {
  optimizedDescription: string;
  suggestions: {
    category: string;
    suggestion: string;
  }[];
  improvements: string[];
}

interface JobDescriptionOptimizerProps {
  currentDescription: string;
  currentRequirements?: string;
  onApplyOptimization: (optimizedDescription: string) => void;
  platformTargets?: string[];
}

const JobDescriptionOptimizer: React.FC<JobDescriptionOptimizerProps> = ({
  currentDescription,
  currentRequirements,
  onApplyOptimization,
  platformTargets = ['linkedin', 'indeed', 'glassdoor']
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
  const [selectedTab, setSelectedTab] = useState('optimized');
  const { toast } = useToast();

  const handleOptimize = async () => {
    setIsLoading(true);
    try {
      const result = await optimizeJobDescription(
        currentDescription,
        currentRequirements || '',
        platformTargets
      );
      setOptimizationResult(result);
      setSelectedTab('optimized');
    } catch (error) {
      console.error('Optimization error:', error);
      toast({
        title: "Optimization failed",
        description: "Could not generate optimization suggestions. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleApply = () => {
    if (optimizationResult) {
      onApplyOptimization(optimizationResult.optimizedDescription);
      setIsOpen(false);
      toast({
        title: "Optimization applied",
        description: "Your job description has been updated with the optimized version."
      });
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button 
          variant="outline" 
          size="sm" 
          className="flex items-center gap-1"
          onClick={() => setIsOpen(true)}
        >
          <Sparkles className="h-3.5 w-3.5 mr-1" />
          Optimize Description
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[750px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Job Description Optimizer</DialogTitle>
          <DialogDescription>
            AI-powered suggestions to improve your job description for better engagement
          </DialogDescription>
        </DialogHeader>

        {!optimizationResult ? (
          <div className="space-y-4 py-4">
            <div className="border rounded-lg p-4 bg-muted/30">
              <h3 className="font-medium mb-2">Target Platforms</h3>
              <div className="flex flex-wrap gap-2">
                {platformTargets.map(platform => (
                  <Badge key={platform} variant="secondary">
                    {platform.charAt(0).toUpperCase() + platform.slice(1)}
                  </Badge>
                ))}
              </div>
            </div>
            
            <div className="border rounded-lg p-4 mb-4">
              <h3 className="font-medium mb-2">Current Description</h3>
              <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                {currentDescription || "No description available"}
              </p>
            </div>
            
            <Button 
              onClick={handleOptimize} 
              disabled={isLoading || !currentDescription}
              className="w-full"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing description...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Generate Optimization Suggestions
                </>
              )}
            </Button>
          </div>
        ) : (
          <div className="space-y-4 py-2">
            <Tabs value={selectedTab} onValueChange={setSelectedTab}>
              <TabsList className="grid w-full grid-cols-3 mb-4">
                <TabsTrigger value="optimized">Optimized Version</TabsTrigger>
                <TabsTrigger value="suggestions">Suggestions</TabsTrigger>
                <TabsTrigger value="improvements">Key Improvements</TabsTrigger>
              </TabsList>
              
              <TabsContent value="optimized" className="space-y-4">
                <div className="border rounded-lg p-4 bg-muted/20">
                  <h3 className="font-medium mb-2 flex items-center">
                    <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                    Optimized Description
                  </h3>
                  <p className="text-sm whitespace-pre-wrap">
                    {optimizationResult.optimizedDescription}
                  </p>
                </div>
              </TabsContent>
              
              <TabsContent value="suggestions" className="space-y-4">
                <div className="border rounded-lg p-4">
                  <h3 className="font-medium mb-3">Personalized Suggestions</h3>
                  <div className="space-y-3">
                    {optimizationResult.suggestions.map((item, index) => (
                      <div key={index} className="pb-2 border-b last:border-0 last:pb-0">
                        <h4 className="text-sm font-medium text-primary">
                          {item.category}
                        </h4>
                        <p className="text-sm mt-1">{item.suggestion}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="improvements" className="space-y-4">
                <div className="border rounded-lg p-4">
                  <h3 className="font-medium mb-3">Key Improvements</h3>
                  <ul className="space-y-2">
                    {optimizationResult.improvements.map((improvement, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm">
                        <span className="text-green-500 flex-shrink-0 mt-0.5">•</span>
                        <span>{improvement}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        )}

        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            Cancel
          </Button>
          {optimizationResult && (
            <Button onClick={handleApply}>
              Apply Optimization
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default JobDescriptionOptimizer;
