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
import { PlusCircle, Edit3, Trash2, Eye, Loader2, Briefcase, Facebook, Twitter, Youtube } from 'lucide-react'; // Added more platform icons
import Link from 'next/link';
import useSWR from 'swr';
import { JobAd } from '@/lib/db/schema'; 
import { Suspense, useActionState, useEffect, startTransition, Fragment } from 'react'; 
import { deleteJobAdAction, DeleteJobAdState } from './actions';

const fetcher = (url: string) => fetch(url).then((res) => res.json());

// Combined JobAdsList and Item logic into one for table structure
function JobAdsTable() {
  const { data: jobAdsData, error, isLoading } = useSWR<JobAd[]>('/api/jobs', fetcher);

  // Initial state for delete action (can be generic as it's per row)
  const initialDeleteState: DeleteJobAdState = { success: false, error: null };
  const [deleteState, deleteAction, isDeleting] = useActionState<DeleteJobAdState, FormData>(
    deleteJobAdAction,
    initialDeleteState
  );

  const handleDelete = (ad: JobAd) => {
    if (window.confirm(`Are you sure you want to delete the ad "${ad.title}"? This action cannot be undone.`)) {
      const formData = new FormData();
      formData.append('jobId', ad.id.toString());
      startTransition(() => {
         deleteAction(formData);
      });
    }
  };

  useEffect(() => {
    if (deleteState.success && deleteState.jobId) {
      alert(`Job ad (ID: ${deleteState.jobId}) deleted successfully.`);
      // SWR will revalidate due to revalidatePath in action
    }
    if (deleteState.error && deleteState.jobId) {
      alert(`Error deleting ad (ID: ${deleteState.jobId}): ${deleteState.error}`);
    }
  }, [deleteState]);

  if (isLoading) return <p className="text-gray-600 text-center py-10">Loading job ads...</p>;
  if (error) return <p className="text-red-500 text-center py-10">Failed to load job ads. Please try again.</p>;
  
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
            <TableRow key={ad.id} className={`${deleteState.jobId === ad.id && isDeleting ? 'opacity-50' : ''}`}>
              <TableCell className="font-medium py-3">{ad.title}</TableCell>
              <TableCell>
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${ad.status === 'live' ? 'bg-green-100 text-green-700' : ad.status === 'draft' ? 'bg-yellow-100 text-yellow-700' : ad.status === 'paused' ? 'bg-gray-100 text-gray-600' : ad.status === 'archived' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>
                  {ad.status ? ad.status.charAt(0).toUpperCase() + ad.status.slice(1) : 'N/A'}
                </span>
              </TableCell>
              <TableCell>
                <div className="flex space-x-1.5">
                  {ad.platformsMetaEnabled && <Facebook className="h-4 w-4 text-blue-600" title="Meta" />}
                  {ad.platformsXEnabled && <Twitter className="h-4 w-4 text-sky-500" title="X" />}
                  {ad.platformsGoogleEnabled && <Youtube className="h-4 w-4 text-red-600" title="Google" />}
                </div>
              </TableCell>
              <TableCell>
                {ad.budgetDaily ? `$${parseFloat(ad.budgetDaily as string).toFixed(2)}` : 'N/A'}
              </TableCell>
              <TableCell className="text-xs">
                <div>Starts: {ad.scheduleStart ? new Date(ad.scheduleStart).toLocaleDateString() : 'N/A'}</div>
                <div>Ends: {ad.scheduleEnd ? new Date(ad.scheduleEnd).toLocaleDateString() : 'Open'}</div>
              </TableCell>
              <TableCell className="text-right space-x-1 py-3">
                <Button variant="outline" size="icon_sm" asChild title="Edit">
                  <Link href={`/dashboard/jobs/${ad.id}/edit`}>
                    <Edit3 className="h-4 w-4" />
                  </Link>
                </Button>
                <Button variant="outline" size="icon_sm" className="text-blue-600 border-blue-300 hover:bg-blue-50" title="View Details">
                   <Eye className="h-4 w-4" />
                </Button>
                <Button 
                  variant="destructive" 
                  size="icon_sm" 
                  onClick={() => handleDelete(ad)} 
                  disabled={isDeleting && deleteState.jobId === ad.id}
                  title="Delete"
                >
                  {(isDeleting && deleteState.jobId === ad.id) ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />} 
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

export default function JobAdsPage() {
  return (
    <section className="flex-1 p-4 lg:p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-lg lg:text-2xl font-medium">Job Advertisements</h1>
        <Link href="/dashboard/jobs/create" passHref>
          <Button className="bg-orange-500 hover:bg-orange-600 text-white">
            <PlusCircle className="mr-2 h-4 w-4" />
            Create New Job Ad
          </Button>
        </Link>
      </div>
      
      <Suspense fallback={<p className="text-gray-600 text-center py-10">Loading job ad list...</p>}> 
        <JobAdsTable />
      </Suspense>
    </section>
  );
} 