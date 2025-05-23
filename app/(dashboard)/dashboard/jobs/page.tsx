'use client';

import { Button } from '@/components/ui/button';
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '@/components/ui/table'; // Assuming shadcn/ui table components
import { PlusCircle, Edit3, Trash2, Eye, Loader2, Briefcase, Facebook, Twitter, Youtube, PlayCircle, Zap } from 'lucide-react'; // Added more platform icons and PlayCircle
import Link from 'next/link';
import useSWR from 'swr';
import { JobAd } from '@/lib/db/schema'; 
import { Suspense, useActionState, useEffect, startTransition, Fragment } from 'react'; 
import { deleteJobAdAction, DeleteJobAdState, publishJobAdNowAction, PublishJobAdState, triggerAutomationEngineAction, TriggerEngineState } from './actions';

const fetcher = (url: string) => fetch(url).then((res) => res.json());

// Row component to manage its own actions
function JobAdTableRow({ ad, onAction }: { ad: JobAd, onAction: () => void }) {
  const initialDeleteState: DeleteJobAdState = { jobId: ad.id, success: false, error: null };
  const [deleteState, submitDeleteAction, isDeleting] = useActionState<DeleteJobAdState, FormData>(
    deleteJobAdAction,
    initialDeleteState
  );

  const initialPublishState: PublishJobAdState = { jobAdId: ad.id, success: false, error: null };
  const [publishState, submitPublishAction, isPublishing] = useActionState<PublishJobAdState, FormData>(
      publishJobAdNowAction,
      initialPublishState
  );

  const handleDelete = () => {
    if (window.confirm(`Are you sure you want to delete "${ad.title}"?`)) {
      const formData = new FormData();
      formData.append('jobAdId', ad.id.toString());
      startTransition(() => { submitDeleteAction(formData); });
    }
  };

  const handlePublishNow = () => {
    if (window.confirm(`Schedule "${ad.title}" for immediate processing?`)) {
        const formData = new FormData();
        formData.append('jobAdId', ad.id.toString());
        startTransition(() => { submitPublishAction(formData); });
    }
  };

  useEffect(() => {
    if (deleteState.success || publishState.success) onAction(); // Trigger SWR revalidation via parent
    if (deleteState.error) alert(`Error deleting: ${deleteState.error}`);
    if (publishState.message) alert(publishState.message);
    if (publishState.error) alert(`Error publishing: ${publishState.error}`);
  }, [deleteState, publishState, onAction]);

  const canPublishNow = [
    'draft', 'error_processing', 'segmentation_failed', 
    'post_failed_meta', 'post_failed_x', 'post_failed_google', 'post_failed_all'
  ].includes(ad.status || '');

  // Get segmentation confidence if available
  const segmentationConfidence = ad.audienceConfidence ? parseFloat(ad.audienceConfidence as string) : null;

  return (
    <TableRow className={`${(isDeleting || isPublishing) ? 'opacity-50' : ''}`}>
      <TableCell className="font-medium py-3">{ad.title}</TableCell>
      <TableCell>
        <div className="flex items-center gap-2">
          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${ad.status === 'live' || ad.status === 'partially_live' ? 'bg-green-100 text-green-700' : (ad.status === 'draft' || ad.status === 'scheduled') ? 'bg-yellow-100 text-yellow-700' : ad.status && ad.status.startsWith('post_failed') ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'}`}>
              {ad.status ? ad.status.charAt(0).toUpperCase() + ad.status.slice(1) : 'N/A'}
          </span>
          {segmentationConfidence !== null && (
            <span 
              className={`px-2 py-1 text-xs font-semibold rounded-full ${
                segmentationConfidence < 0.25 
                  ? 'bg-red-100 text-red-700' 
                  : segmentationConfidence < 0.5 
                  ? 'bg-yellow-100 text-yellow-700' 
                  : 'bg-green-100 text-green-700'
              }`}
              title={`Segmentation confidence: ${(segmentationConfidence * 100).toFixed(1)}%`}
            >
              {(segmentationConfidence * 100).toFixed(0)}%
            </span>
          )}
        </div>
      </TableCell>
      <TableCell>
        <div className="flex space-x-1.5">
          {ad.platformsMetaEnabled && <Facebook className="h-4 w-4 text-blue-600" />}
          {ad.platformsXEnabled && <Twitter className="h-4 w-4 text-sky-500" />}
          {ad.platformsGoogleEnabled && <Youtube className="h-4 w-4 text-red-600" />}
        </div>
      </TableCell>
      <TableCell>{ad.budgetDaily ? `$${parseFloat(ad.budgetDaily as string).toFixed(2)}` : 'N/A'}</TableCell>
      <TableCell className="text-xs">
        <div>Starts: {ad.scheduleStart ? new Date(ad.scheduleStart).toLocaleDateString() : 'N/A'}</div>
        <div>Ends: {ad.scheduleEnd ? new Date(ad.scheduleEnd).toLocaleDateString() : 'Open'}</div>
      </TableCell>
      <TableCell className="text-right space-x-1 py-3">
        {canPublishNow && (
            <Button variant="outline" size="icon" onClick={handlePublishNow} disabled={isPublishing} title="Publish Now">
                {isPublishing ? <Loader2 className="h-4 w-4 animate-spin" /> : <PlayCircle className="h-4 w-4 text-green-600" />}
            </Button>
        )}
        <Button variant="outline" size="icon" asChild title="Edit">
          <Link href={`/dashboard/jobs/${ad.id}/edit`}><Edit3 className="h-4 w-4" /></Link>
        </Button>
        <Button variant="destructive" size="icon" onClick={handleDelete} disabled={isDeleting} title="Delete">
          {(isDeleting) ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />} 
        </Button>
      </TableCell>
    </TableRow>
  );
}

function JobAdsTable() {
  const { data: jobAdsData, error, isLoading, mutate } = useSWR<JobAd[]>('/api/jobs', fetcher);
  if (isLoading) return <p className="text-gray-600 text-center py-10">Loading job ads...</p>;
  if (error) return <p className="text-red-500 text-center py-10">Failed to load job ads.</p>;
  if (!jobAdsData || jobAdsData.length === 0) {
    return (
      <div className="p-6 text-center bg-white rounded-lg shadow-md">
        <Briefcase className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 className="text-xl font-medium text-gray-800">No Job Ads Yet</h3>
        <p className="text-gray-500 mt-2 mb-4">
          Get started by creating your first job advertisement.
        </p>
        <Link href="/dashboard/jobs/create" passHref>
          <Button className="bg-orange-500 hover:bg-orange-600 text-white">
            <PlusCircle className="mr-2 h-4 w-4" />
            Create First Job Ad
          </Button>
        </Link>
      </div>
    );
  }
  return (
    <div className="bg-white p-1 rounded-lg shadow-md overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[200px]">Title</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Platforms</TableHead>
            <TableHead>Budget (Daily)</TableHead>
            <TableHead>Schedule</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {jobAdsData.map((ad) => (
            <JobAdTableRow key={ad.id} ad={ad} onAction={mutate} />
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

export default function JobAdsPage() {
  // State for the trigger engine action
  const [engineTriggerState, submitTriggerEngineAction, isEngineTriggerPending] = useActionState<TriggerEngineState, void>(
    triggerAutomationEngineAction,
    { message: null, error: null, success: false, processedCount: 0 } // Initial state
  );

  const handleTriggerEngine = () => {
    if (window.confirm("Manually trigger the ad processing engine now? This will check for all scheduled ads.")) {
        startTransition(() => {
            submitTriggerEngineAction();
        });
    }
  };

  useEffect(() => {
    if (engineTriggerState.success) {
        alert(engineTriggerState.message || `Engine run complete. Processed: ${engineTriggerState.processedCount || 0} ads.`);
        // Optionally, you might want to force SWR to revalidate the jobs list here if statuses changed
        // mutate('/api/jobs'); // If mutate is available in this scope from useSWR
    } else if (engineTriggerState.error) {
        alert(`Error triggering engine: ${engineTriggerState.error}`);
    }
    // Reset message after showing to avoid re-alerting on re-renders if not careful
    // This might be better handled by not setting the message again in the state unless it changes.
  }, [engineTriggerState]);

  return (
    <section className="flex-1 p-4 lg:p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-lg lg:text-2xl font-medium">Job Advertisements</h1>
        <div className="flex space-x-2">
            <Button 
                onClick={handleTriggerEngine} 
                variant="outline"
                disabled={isEngineTriggerPending}
                className="border-blue-500 text-blue-600 hover:bg-blue-50 hover:text-blue-700"
            >
                {isEngineTriggerPending ? 
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : 
                    <Zap className="mr-2 h-4 w-4" />
                }
                Trigger Ad Processor
            </Button>
            <Link href="/dashboard/jobs/create" passHref>
                <Button className="bg-orange-500 hover:bg-orange-600 text-white">
                    <PlusCircle className="mr-2 h-4 w-4" />
                    Create New Job Ad
                </Button>
            </Link>
        </div>
      </div>
      
      {engineTriggerState.message && !engineTriggerState.error && (
          <div className="mb-4 p-3 bg-green-100 text-green-700 rounded-md text-sm">
              {engineTriggerState.message}
          </div>
      )}
      {engineTriggerState.error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md text-sm">
              Error: {engineTriggerState.error}
          </div>
      )}

      <Suspense fallback={<p className="text-gray-600 text-center py-10">Loading job ad list...</p>}> 
        <JobAdsTable />
      </Suspense>
    </section>
  );
} 