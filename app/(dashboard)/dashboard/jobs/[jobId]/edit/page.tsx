'use client';

import { useEffect, useState } from 'react';
import { useActionState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import useSWR from 'swr';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import Link from 'next/link';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { updateJobAdAction, UpdateJobAdState, testSegmentationAction, TestSegmentationState } from '../../actions';
import { JobAd } from '@/lib/db/schema';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { startTransition } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';

// Add type definitions for segmentation data
interface AudiencePrimitive {
  category: string;
  value: string;
  confidence?: number;
}

interface MappedTargeting {
  industries?: string[];
  skillKeywords?: string[];
  seniority?: string[];
  locations?: string[];
}

const fetcher = (url: string) => fetch(url).then((res) => res.json());

// Helper to format Date to yyyy-MM-ddTHH:mm required by datetime-local
const formatDateForInput = (date: Date | string | null): string => {
  if (!date) return '';
  const d = new Date(date);
  // Adjust for timezone offset to display local time correctly in input
  const timezoneOffset = d.getTimezoneOffset() * 60000; //offset in milliseconds
  const localDate = new Date(d.getTime() - timezoneOffset);
  return localDate.toISOString().slice(0, 16);
};

// Define a more specific type for form default values
interface JobAdFormDefaults {
    title?: string;
    companyName?: string | null;
    descriptionShort?: string;
    descriptionLong?: string | null;
    targetUrl?: string;
    creativeAssetUrl?: string | null;
    platformMeta?: boolean;
    platformX?: boolean;
    platformGoogle?: boolean;
    budgetDaily?: string | number | null; // Input type number can take string or number
    scheduleStart?: string; // Input type datetime-local needs string
    scheduleEnd?: string;   // Input type datetime-local needs string
    // Add any other fields from JobAd that are part of the form
}

const initialUpdateState: UpdateJobAdState = { 
  message: null,
  error: null,
  fieldErrors: {},
  success: false,
};

export default function EditJobAdPage() {
  const router = useRouter();
  const params = useParams();
  const jobId = params.jobId as string; // Assuming jobId is always a string from params

  const { data: jobAdData, error: fetchError, isLoading: isFetching } = useSWR<JobAd>(
    jobId ? `/api/jobs/${jobId}` : null, // Conditional fetching
    fetcher
  );

  const [state, formAction, pending] = useActionState<UpdateJobAdState, FormData>(
    updateJobAdAction,
    { ...initialUpdateState, jobId: parseInt(jobId,10) } // Pass jobId to initial state if needed by action
  );
  
  // State for test segmentation
  const [testSegmentationState, submitTestSegmentation, isTestingSegmentation] = useActionState<TestSegmentationState, FormData>(
    testSegmentationAction,
    { message: null, error: null, success: false }
  );
  const [showSegmentationModal, setShowSegmentationModal] = useState(false);
  
  // Use the new JobAdFormDefaults type here
  const [defaultValues, setDefaultValues] = useState<JobAdFormDefaults>({});

  useEffect(() => {
    if (jobAdData) {
      setDefaultValues({
        ...(jobAdData as any), 
        title: jobAdData.title || '',
        companyName: jobAdData.companyName,
        descriptionShort: jobAdData.descriptionShort || '',
        descriptionLong: jobAdData.descriptionLong,
        targetUrl: jobAdData.targetUrl || '',
        creativeAssetUrl: jobAdData.creativeAssetUrl,
        platformMeta: jobAdData.platformsMetaEnabled,
        platformX: jobAdData.platformsXEnabled,
        platformGoogle: jobAdData.platformsGoogleEnabled,
        budgetDaily: jobAdData.budgetDaily ? jobAdData.budgetDaily.toString() : '', // Ensure string for input
        scheduleStart: formatDateForInput(jobAdData.scheduleStart),
        scheduleEnd: formatDateForInput(jobAdData.scheduleEnd),
      });
    }
  }, [jobAdData]);

  useEffect(() => {
    if (state.success && state.message) {
      alert(state.message); // Simple alert for now
      router.push('/dashboard/jobs'); // Redirect to the job ads list
    }
  }, [state.success, state.message, router]);

  const handleTestSegmentation = () => {
    const formData = new FormData();
    formData.append('jobAdId', jobId);
    startTransition(() => {
      submitTestSegmentation(formData);
    });
    setShowSegmentationModal(true);
  };

  useEffect(() => {
    if (testSegmentationState.success && testSegmentationState.segmentationData) {
      // Data loaded successfully, modal is already open
    } else if (testSegmentationState.error && showSegmentationModal) {
      // Keep modal open to show error
    }
  }, [testSegmentationState, showSegmentationModal]);

  if (isFetching) return <div className="flex justify-center items-center h-64"><Loader2 className="h-8 w-8 animate-spin text-orange-500" /> <p className='ml-2'>Loading job ad details...</p></div>;
  if (fetchError) return <p className="text-red-500 text-center p-8">Failed to load job ad details. Please try again.</p>;
  if (!jobAdData && !isFetching) return <p className="text-red-500 text-center p-8">Job ad not found.</p>;

  return (
    <section className="flex-1 p-4 lg:p-8">
      <div className="flex items-center mb-6">
        <Link href="/dashboard/jobs" className="mr-4 p-2 rounded-full hover:bg-gray-200">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <h1 className="text-lg lg:text-2xl font-medium">Edit Job Advertisement</h1>
      </div>

      <form action={formAction} className="space-y-8 max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-md">
        <input type="hidden" name="jobId" value={jobId} />
        
        {/* Title */}
        <div>
          <Label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">Title</Label>
          <Input
            id="title"
            name="title"
            type="text"
            maxLength={100}
            required
            placeholder="e.g., Senior Software Engineer"
            className="w-full"
            defaultValue={defaultValues.title || ''}
          />
          {state.fieldErrors?.title && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.title.join(', ')}</p>}
          <p className="text-xs text-gray-500 mt-1">Max 100 characters. Displayed as headline.</p>
        </div>

        {/* Company Name */}
        <div>
          <Label htmlFor="companyName" className="block text-sm font-medium text-gray-700 mb-1">Company Name (Optional)</Label>
          <Input
            id="companyName"
            name="companyName"
            type="text"
            maxLength={100}
            placeholder="e.g., AdFlux Inc."
            className="w-full"
            defaultValue={defaultValues.companyName || ''}
          />
          {state.fieldErrors?.companyName && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.companyName.join(', ')}</p>}
        </div>

        {/* Description Short */}
        <div>
          <Label htmlFor="descriptionShort" className="block text-sm font-medium text-gray-700 mb-1">Short Description</Label>
          <Textarea
            id="descriptionShort"
            name="descriptionShort"
            maxLength={280}
            required
            placeholder="Brief summary for quick views (e.g., tweet, Google headline)"
            className="w-full min-h-[80px]"
            defaultValue={defaultValues.descriptionShort || ''}
          />
          {state.fieldErrors?.descriptionShort && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.descriptionShort.join(', ')}</p>}
          <p className="text-xs text-gray-500 mt-1">Max 280 characters. Universal body copy.</p>
        </div>

        {/* Description Long (Optional) */}
        <div>
          <Label htmlFor="descriptionLong" className="block text-sm font-medium text-gray-700 mb-1">Long Description (Optional)</Label>
          <Textarea
            id="descriptionLong"
            name="descriptionLong"
            placeholder="Detailed description for platforms that allow richer text."
            className="w-full min-h-[120px]"
            defaultValue={defaultValues.descriptionLong || ''}
          />
          {state.fieldErrors?.descriptionLong && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.descriptionLong.join(', ')}</p>}
           <p className="text-xs text-gray-500 mt-1">Optional. Defaults to short description if empty.</p>
        </div>

        {/* Target URL */}
        <div>
          <Label htmlFor="targetUrl" className="block text-sm font-medium text-gray-700 mb-1">Target URL</Label>
          <Input
            id="targetUrl"
            name="targetUrl"
            type="url"
            required
            placeholder="https://yourcompany.com/careers/job-id"
            className="w-full"
            defaultValue={defaultValues.targetUrl || ''}
          />
          {state.fieldErrors?.targetUrl && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.targetUrl.join(', ')}</p>}
           <p className="text-xs text-gray-500 mt-1">Landing page for applicants (must be HTTPS).</p>
        </div>

        {/* Creative Asset URL (Optional Image) */}
        <div>
          <Label htmlFor="creativeAssetUrl">Creative Asset URL (Optional Image)</Label>
          <Input id="creativeAssetUrl" name="creativeAssetUrl" type="url" defaultValue={defaultValues.creativeAssetUrl || ''} />
          {state.fieldErrors?.creativeAssetUrl && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.creativeAssetUrl.join(', ')}</p>}
           <p className="text-xs text-gray-500 mt-1">URL for one image. Used by platform integrations.</p>
        </div>

        {/* Target Platforms */}
        <div>
          <Label className="block text-sm font-medium text-gray-700 mb-2">Target Platforms</Label>
          <div className="space-y-2">
            <div className="flex items-center">
              <Checkbox id="platformMeta" name="platformMeta" defaultChecked={defaultValues.platformMeta} />
              <Label htmlFor="platformMeta" className="ml-2 text-sm font-medium text-gray-700">Meta (Facebook/Instagram)</Label>
            </div>
            <div className="flex items-center">
              <Checkbox id="platformX" name="platformX" defaultChecked={defaultValues.platformX} />
              <Label htmlFor="platformX" className="ml-2 text-sm font-medium text-gray-700">X (formerly Twitter)</Label>
            </div>
            <div className="flex items-center">
              <Checkbox id="platformGoogle" name="platformGoogle" defaultChecked={defaultValues.platformGoogle} />
              <Label htmlFor="platformGoogle" className="ml-2 text-sm font-medium text-gray-700">Google Ads</Label>
            </div>
          </div>
          {state.fieldErrors?.platformMeta && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.platformMeta.join(', ')}</p>} 
           <p className="text-xs text-gray-500 mt-1">Select at least one platform.</p>
        </div>

        {/* Budget Daily */}
        <div>
          <Label htmlFor="budgetDaily" className="block text-sm font-medium text-gray-700 mb-1">Daily Budget ($)</Label>
          <Input
            id="budgetDaily"
            name="budgetDaily"
            type="number"
            min="1"
            step="0.01"
            required
            placeholder="e.g., 10.00"
            className="w-full"
            defaultValue={defaultValues.budgetDaily?.toString() || ''} // Convert number to string for input
          />
          {state.fieldErrors?.budgetDaily && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.budgetDaily.join(', ')}</p>}
          <p className="text-xs text-gray-500 mt-1">Minimum $1. In your local currency (assumed USD for placeholder).</p>
        </div>

        {/* Schedule Start */}
        <div>
          <Label htmlFor="scheduleStart" className="block text-sm font-medium text-gray-700 mb-1">Schedule Start</Label>
          <Input
            id="scheduleStart"
            name="scheduleStart"
            type="datetime-local"
            required
            className="w-full"
            defaultValue={defaultValues.scheduleStart || ''}
          />
          {state.fieldErrors?.scheduleStart && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.scheduleStart.join(', ')}</p>}
        </div>

        {/* Schedule End (Optional) */}
        <div>
          <Label htmlFor="scheduleEnd" className="block text-sm font-medium text-gray-700 mb-1">Schedule End (Optional)</Label>
          <Input
            id="scheduleEnd"
            name="scheduleEnd"
            type="datetime-local"
            className="w-full"
            defaultValue={defaultValues.scheduleEnd || ''}
          />
          {state.fieldErrors?.scheduleEnd && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.scheduleEnd.join(', ')}</p>}
          <p className="text-xs text-gray-500 mt-1">Leave empty for an open-ended campaign.</p>
        </div>

        {/* Test Segmentation Button */}
        <div className="border-t border-gray-200 pt-6">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Test Audience Segmentation</h3>
          <p className="text-xs text-gray-500 mb-3">
            Preview how your job ad will be segmented and targeted without publishing it.
          </p>
          <Button
            type="button"
            variant="outline"
            className="w-full sm:w-auto"
            onClick={handleTestSegmentation}
            disabled={isTestingSegmentation}
          >
            {isTestingSegmentation ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Testing...
              </>
            ) : (
              'Test Segmentation'
            )}
          </Button>
        </div>

        {/* Audience Segmentation Preview (if available) */}
        {jobAdData && (jobAdData.status !== 'draft') && (
          <div className="border-t border-gray-200 pt-6">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Audience Targeting & Segmentation</h3>
            <div className="bg-gray-50 rounded-lg p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Segmentation Status:</span>
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                  jobAdData.status === 'segmentation_failed' 
                    ? 'bg-red-100 text-red-700' 
                    : jobAdData.segmentationProcessedAt
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-700'
                }`}>
                  {jobAdData.status === 'segmentation_failed' 
                    ? 'Failed' 
                    : jobAdData.segmentationProcessedAt
                    ? 'Completed'
                    : 'Pending'}
                </span>
              </div>
              
              {jobAdData.audienceClusterId && (
                <div>
                  <span className="text-sm text-gray-600">Assigned Cluster:</span>
                  <span className="ml-2 text-sm font-medium">
                    {jobAdData.audienceClusterProfileName || `Cluster ${jobAdData.audienceClusterId}`}
                  </span>
                </div>
              )}
              
              {jobAdData.audienceConfidence !== undefined && jobAdData.audienceConfidence !== null && (
                <div>
                  <span className="text-sm text-gray-600">Confidence Score:</span>
                  <span className={`ml-2 text-sm font-medium ${
                    parseFloat(jobAdData.audienceConfidence as string) < 0.25 
                      ? 'text-red-600' 
                      : parseFloat(jobAdData.audienceConfidence as string) < 0.5 
                      ? 'text-yellow-600' 
                      : 'text-green-600'
                  }`}>
                    {(parseFloat(jobAdData.audienceConfidence as string) * 100).toFixed(1)}%
                  </span>
                  {parseFloat(jobAdData.audienceConfidence as string) < 0.25 && (
                    <span className="ml-2 text-xs text-red-600">(Using broad targeting)</span>
                  )}
                </div>
              )}
              
              {jobAdData.derivedAudiencePrimitives && Array.isArray(jobAdData.derivedAudiencePrimitives) && (jobAdData.derivedAudiencePrimitives as AudiencePrimitive[]).length > 0 ? (
                <div className="mt-3 border-t border-gray-200 pt-3">
                  <p className="text-sm text-gray-600 mb-2">Derived Audience Segments:</p>
                  <div className="space-y-2">
                    {/* Group primitives by category */}
                    {(() => {
                      const primitives = jobAdData.derivedAudiencePrimitives as AudiencePrimitive[];
                      const grouped = primitives.reduce<Record<string, string[]>>((acc, primitive) => {
                        const category = primitive.category || 'other';
                        if (!acc[category]) acc[category] = [];
                        acc[category].push(primitive.value);
                        return acc;
                      }, {});
                      
                      return Object.entries(grouped).map(([category, values]) => (
                        <div key={category} className="text-xs">
                          <strong className="capitalize">{category.replace('_', ' ')}:</strong>
                          <span className="ml-1">{values.join(', ')}</span>
                        </div>
                      ));
                    })()}
                  </div>
                </div>
              ) : null}
              
              {jobAdData.mappedTargeting && Object.keys(jobAdData.mappedTargeting as any).length > 0 ? (
                <div className="mt-3 border-t border-gray-200 pt-3">
                  <p className="text-sm text-gray-600 mb-2">Platform Targeting:</p>
                  <div className="space-y-1 text-xs">
                    {(() => {
                      const targeting = jobAdData.mappedTargeting as MappedTargeting;
                      return (
                        <>
                          {targeting.industries && targeting.industries.length > 0 && (
                            <p><strong>Industries:</strong> {targeting.industries.join(', ')}</p>
                          )}
                          {targeting.skillKeywords && targeting.skillKeywords.length > 0 && (
                            <p><strong>Skills:</strong> {targeting.skillKeywords.join(', ')}</p>
                          )}
                          {targeting.seniority && targeting.seniority.length > 0 && (
                            <p><strong>Seniority:</strong> {targeting.seniority.join(', ')}</p>
                          )}
                          {targeting.locations && targeting.locations.length > 0 && (
                            <p><strong>Locations:</strong> {targeting.locations.join(', ')}</p>
                          )}
                        </>
                      );
                    })()}
                  </div>
                </div>
              ) : null}
              
              {jobAdData.segmentationProcessedAt && (
                <p className="text-xs text-gray-500 mt-3">
                  Last processed: {new Date(jobAdData.segmentationProcessedAt).toLocaleString()}
                </p>
              )}
              
              {!jobAdData.segmentationProcessedAt && jobAdData.status !== 'segmentation_failed' && (
                <p className="text-xs text-gray-500 mt-3">
                  Audience targeting will be automatically determined when the ad is processed for publishing.
                </p>
              )}
            </div>
          </div>
        )}
        
        {state.error && !state.fieldErrors && <p className="text-sm text-red-500 mt-4 text-center">{state.error}</p>}
        {state.success && state.message && !state.error && <p className="text-sm text-green-500 mt-4 text-center">{state.message}</p>} 

        <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 mt-8">
          <Link href="/dashboard/jobs" passHref>
            <Button type="button" variant="outline" disabled={pending}>
              Cancel
            </Button>
          </Link>
          <Button 
            type="submit" 
            className="bg-orange-500 hover:bg-orange-600 text-white min-w-[120px]"
            disabled={pending || isFetching}
          >
            {pending ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Saving...</> : 'Save Changes'}
          </Button>
        </div>
      </form>

      {/* Test Segmentation Modal */}
      <Dialog open={showSegmentationModal} onOpenChange={setShowSegmentationModal}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Test Segmentation Results</DialogTitle>
            <DialogDescription>
              Preview how your job ad will be segmented and targeted across different platforms.
            </DialogDescription>
          </DialogHeader>
          
          {isTestingSegmentation && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-orange-500" />
              <span className="ml-2">Analyzing your job ad...</span>
            </div>
          )}
          
          {testSegmentationState.error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-700">{testSegmentationState.error}</p>
            </div>
          )}
          
          {testSegmentationState.success && testSegmentationState.segmentationData && (
            <div className="space-y-6">
              {/* Cluster Assignment */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Audience Cluster</h3>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-sm">
                    <strong>Assigned to:</strong> {testSegmentationState.segmentationData.audienceClusterProfileName || `Cluster ${testSegmentationState.segmentationData.audienceClusterId}`}
                  </p>
                  {testSegmentationState.segmentationData.audienceConfidence !== undefined && (
                    <p className="text-sm mt-1">
                      <strong>Confidence:</strong>
                      <span className={`ml-2 ${
                        testSegmentationState.segmentationData.audienceConfidence < 0.25 
                          ? 'text-red-600' 
                          : testSegmentationState.segmentationData.audienceConfidence < 0.5 
                          ? 'text-yellow-600' 
                          : 'text-green-600'
                      }`}>
                        {(testSegmentationState.segmentationData.audienceConfidence * 100).toFixed(1)}%
                      </span>
                      {testSegmentationState.segmentationData.audienceConfidence < 0.25 && (
                        <span className="ml-2 text-xs text-red-600">(Will use broad targeting)</span>
                      )}
                    </p>
                  )}
                </div>
              </div>

              {/* Derived Audience Primitives */}
              {testSegmentationState.segmentationData.derivedAudiencePrimitives && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Derived Audience Segments</h3>
                  <div className="bg-gray-50 rounded-lg p-3 space-y-2">
                    {(() => {
                      const primitives = testSegmentationState.segmentationData.derivedAudiencePrimitives as AudiencePrimitive[];
                      const grouped = primitives.reduce<Record<string, string[]>>((acc, primitive) => {
                        const category = primitive.category || 'other';
                        if (!acc[category]) acc[category] = [];
                        acc[category].push(primitive.value);
                        return acc;
                      }, {});
                      
                      return Object.entries(grouped).map(([category, values]) => (
                        <div key={category} className="text-sm">
                          <strong className="capitalize">{category.replace('_', ' ')}:</strong>
                          <span className="ml-1">{values.join(', ')}</span>
                        </div>
                      ));
                    })()}
                  </div>
                </div>
              )}

              {/* Platform Targeting */}
              {testSegmentationState.segmentationData.mappedTargeting && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Platform-Specific Targeting</h3>
                  <div className="bg-gray-50 rounded-lg p-3 space-y-1">
                    {(() => {
                      const targeting = testSegmentationState.segmentationData.mappedTargeting as MappedTargeting;
                      return (
                        <>
                          {targeting.industries && targeting.industries.length > 0 && (
                            <p className="text-sm"><strong>Industries:</strong> {targeting.industries.join(', ')}</p>
                          )}
                          {targeting.skillKeywords && targeting.skillKeywords.length > 0 && (
                            <p className="text-sm"><strong>Skills:</strong> {targeting.skillKeywords.join(', ')}</p>
                          )}
                          {targeting.seniority && targeting.seniority.length > 0 && (
                            <p className="text-sm"><strong>Seniority:</strong> {targeting.seniority.join(', ')}</p>
                          )}
                          {targeting.locations && targeting.locations.length > 0 && (
                            <p className="text-sm"><strong>Locations:</strong> {targeting.locations.join(', ')}</p>
                          )}
                        </>
                      );
                    })()}
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </section>
  );
} 