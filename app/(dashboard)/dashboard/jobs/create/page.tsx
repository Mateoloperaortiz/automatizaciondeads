'use client';

import { useEffect } from 'react'; // Added for potential redirect
import { useActionState } from 'react'; // React 19
import { useRouter } from 'next/navigation'; // For client-side redirect
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import Link from 'next/link';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { createJobAdAction, CreateJobAdState } from './actions';

const initialState: CreateJobAdState = {
  message: null,
  error: null,
  fieldErrors: {},
  success: false,
};

export default function CreateJobAdPage() {
  const router = useRouter();
  const [state, formAction, pending] = useActionState<CreateJobAdState, FormData>(
    createJobAdAction,
    initialState
  );

  useEffect(() => {
    if (state.success && state.message) {
      // Optionally, show a toast notification with state.message
      alert(state.message); // Simple alert for now
      router.push('/dashboard/jobs'); // Redirect to the job ads list
    }
  }, [state.success, state.message, router]);

  // Removed handleSubmit, form now directly uses formAction

  return (
    <section className="flex-1 p-4 lg:p-8">
      <div className="flex items-center mb-6">
        <Link href="/dashboard/jobs" className="mr-4 p-2 rounded-full hover:bg-gray-200">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <h1 className="text-lg lg:text-2xl font-medium">Create New Job Advertisement</h1>
      </div>

      {/* Use formAction from useActionState */}
      <form action={formAction} className="space-y-8 max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-md">
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
          />
          {state.fieldErrors?.title && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.title.join(', ')}</p>}
          <p className="text-xs text-gray-500 mt-1">Max 100 characters. Displayed as headline.</p>
        </div>

        {/* Company Name (New) */}
        <div>
          <Label htmlFor="companyName" className="block text-sm font-medium text-gray-700 mb-1">Company Name (Optional)</Label>
          <Input
            id="companyName"
            name="companyName"
            type="text"
            maxLength={100}
            placeholder="e.g., Acme Innovations Inc."
            className="w-full"
          />
          {state.fieldErrors?.companyName && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.companyName.join(', ')}</p>}
          <p className="text-xs text-gray-500 mt-1">Used in ad copy if needed (e.g., by Google Ad translator).</p>
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
          />
          {state.fieldErrors?.targetUrl && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.targetUrl.join(', ')}</p>}
           <p className="text-xs text-gray-500 mt-1">Landing page for applicants (must be HTTPS).</p>
        </div>

        {/* Creative Asset URL (Optional) */}
        <div>
          <Label htmlFor="creativeAssetUrl" className="block text-sm font-medium text-gray-700 mb-1">Creative Asset URL (Optional Image/Video)</Label>
          <Input
            id="creativeAssetUrl"
            name="creativeAssetUrl"
            type="url"
            placeholder="https://yourcdn.com/path/to/image-or-video.jpg_or.mp4"
            className="w-full"
          />
          {state.fieldErrors?.creativeAssetUrl && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.creativeAssetUrl.join(', ')}</p>}
          <p className="text-xs text-gray-500 mt-1">URL for one image or video. Used by platform integrations.</p>
        </div>

        {/* Video Thumbnail URL (New - Conditional) */}
        <div>
          <Label htmlFor="videoThumbnailUrl" className="block text-sm font-medium text-gray-700 mb-1">Video Thumbnail URL (Optional - if Creative Asset is a video)</Label>
          <Input
            id="videoThumbnailUrl"
            name="videoThumbnailUrl"
            type="url"
            placeholder="https://yourcdn.com/path/to/video-thumbnail.jpg"
            className="w-full"
          />
          {state.fieldErrors?.videoThumbnailUrl && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.videoThumbnailUrl.join(', ')}</p>}
          <p className="text-xs text-gray-500 mt-1">Required by some platforms (like Meta) if creative asset is a video and auto-thumbnail isn't used.</p>
        </div>

        {/* Target Platforms */}
        <div>
          <Label className="block text-sm font-medium text-gray-700 mb-2">Target Platforms</Label>
          <div className="space-y-2">
            <div className="flex items-center">
              <Checkbox id="platformMeta" name="platformMeta" />
              <Label htmlFor="platformMeta" className="ml-2 text-sm font-medium text-gray-700">Meta (Facebook/Instagram)</Label>
            </div>
            <div className="flex items-center">
              <Checkbox id="platformX" name="platformX" />
              <Label htmlFor="platformX" className="ml-2 text-sm font-medium text-gray-700">X (formerly Twitter)</Label>
            </div>
            <div className="flex items-center">
              <Checkbox id="platformGoogle" name="platformGoogle" />
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
          />
          {state.fieldErrors?.scheduleEnd && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.scheduleEnd.join(', ')}</p>}
          <p className="text-xs text-gray-500 mt-1">Leave empty for an open-ended campaign.</p>
        </div>
        
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
            disabled={pending}
          >
            {pending ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Saving...</> : 'Save as Draft'}
          </Button>
        </div>
      </form>
    </section>
  );
} 