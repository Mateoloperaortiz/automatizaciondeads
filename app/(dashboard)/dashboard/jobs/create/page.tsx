'use client';

import { useEffect, useState } from 'react';
import { useActionState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import Link from 'next/link';
import { ArrowLeft, Loader2, Info } from 'lucide-react';
import { createJobAdAction, CreateJobAdState } from '../actions';
import useSWR from 'swr';
import { SocialPlatformConnection } from '@/lib/db/schema';

const fetcher = (url: string) => fetch(url).then(res => res.json());

const STEPS = [
  { id: 1, title: 'Core Details' },
  { id: 2, title: 'Links & Media' },
  { id: 3, title: 'Campaign Settings' },
];

const initialState: CreateJobAdState = {
  message: null,
  error: null,
  fieldErrors: {},
  success: false,
};

export default function CreateJobAdPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [state, formAction, pending] = useActionState<CreateJobAdState, FormData>(createJobAdAction, initialState);

  const { data: connections, error: connectionsError } = useSWR<{ [key: string]: SocialPlatformConnection | null }>(
    '/api/connections', 
    fetcher
  );

  const isMetaConnected = !!connections?.meta;
  const isXConnected = !!connections?.x;
  const isGoogleConnected = !!connections?.google;

  useEffect(() => {
    if (state.success && state.message) {
      alert(state.message);
      router.push('/dashboard/jobs');
    } else if (!state.success && state.error && currentStep > 1) {
        // If there's a server-side validation error after the first step,
        // try to determine which step the error belongs to.
        // This is a simplification. A more robust solution might involve
        // mapping error fields to steps.
        const fieldErrors = Object.keys(state.fieldErrors || {});
        if (fieldErrors.some(field => ['title', 'descriptionShort', 'descriptionLong', 'companyName'].includes(field))) {
            setCurrentStep(1);
        } else if (fieldErrors.some(field => ['targetUrl', 'creativeAssetUrl'].includes(field))) {
            setCurrentStep(2);
        } else {
            setCurrentStep(3);
        }
    }
  }, [state, router]);
  
  const nextStep = () => {
    if (currentStep < STEPS.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };
  
  // Set default start time once on the client
  const [defaultScheduleStart, setDefaultScheduleStart] = useState('');
  useEffect(() => {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset()); // Adjust for local timezone
    setDefaultScheduleStart(now.toISOString().slice(0, 16));
  }, []);

  return (
    <section className="flex-1 p-4 lg:p-8">
      <div className="flex items-center mb-6">
        <Link href="/dashboard/jobs" className="mr-4 p-2 rounded-full hover:bg-gray-200">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <h1 className="text-lg lg:text-2xl font-medium">Create New Job Advertisement</h1>
      </div>

      <div className="max-w-4xl mx-auto">
        {/* Progress Indicator */}
        <div className="mb-8 flex justify-between items-center">
          {STEPS.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                  currentStep >= step.id ? 'bg-orange-500 text-white' : 'bg-gray-200 text-gray-600'
                }`}
              >
                {step.id}
              </div>
              <p className={`ml-3 font-medium ${currentStep >= step.id ? 'text-gray-900' : 'text-gray-500'}`}>
                {step.title}
              </p>
              {index < STEPS.length - 1 && (
                <div className="flex-1 h-px bg-gray-300 mx-4 w-16 sm:w-24 md:w-32"></div>
              )}
            </div>
          ))}
        </div>

        <form action={formAction} className="bg-white p-8 rounded-lg shadow-md border border-gray-200">
          <div className="space-y-8">
            <div style={{ display: currentStep === 1 ? 'block' : 'none' }}>
              <Card>
                <CardHeader>
                  <CardTitle>Step 1: Core Details</CardTitle>
                  <CardDescription>Enter the main information for your job ad.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                   <div>
                      <Label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">Title</Label>
                      <Input id="title" name="title" type="text" maxLength={100} required placeholder="e.g., Senior Software Engineer" className="w-full" />
                      {state.fieldErrors?.title && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.title.join(', ')}</p>}
                    </div>
                    <div>
                      <Label htmlFor="companyName" className="block text-sm font-medium text-gray-700 mb-1">Company Name (Optional)</Label>
                      <Input id="companyName" name="companyName" type="text" maxLength={100} placeholder="e.g., AdFlux Inc." className="w-full" />
                      {state.fieldErrors?.companyName && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.companyName.join(', ')}</p>}
                    </div>
                    <div>
                      <Label htmlFor="descriptionShort" className="block text-sm font-medium text-gray-700 mb-1">Short Description</Label>
                      <Textarea id="descriptionShort" name="descriptionShort" maxLength={280} required placeholder="Brief summary for quick views..." className="w-full min-h-[80px]" />
                      {state.fieldErrors?.descriptionShort && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.descriptionShort.join(', ')}</p>}
                    </div>
                    <div>
                      <Label htmlFor="descriptionLong" className="block text-sm font-medium text-gray-700 mb-1">Long Description (Optional)</Label>
                      <Textarea id="descriptionLong" name="descriptionLong" placeholder="Detailed description for platforms that allow richer text." className="w-full min-h-[120px]" />
                      {state.fieldErrors?.descriptionLong && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.descriptionLong.join(', ')}</p>}
                    </div>
                </CardContent>
              </Card>
            </div>

            <div style={{ display: currentStep === 2 ? 'block' : 'none' }}>
              <Card>
                <CardHeader>
                  <CardTitle>Step 2: Links & Media</CardTitle>
                  <CardDescription>Provide URLs for your application page and any visual assets.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div>
                        <Label htmlFor="targetUrl" className="block text-sm font-medium text-gray-700 mb-1">Target URL</Label>
                        <Input id="targetUrl" name="targetUrl" type="url" required placeholder="https://yourcompany.com/careers/job-id" className="w-full" />
                        {state.fieldErrors?.targetUrl && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.targetUrl.join(', ')}</p>}
                    </div>
                    <div>
                        <Label htmlFor="creativeAssetUrl" className="block text-sm font-medium text-gray-700 mb-1">Creative Asset URL (Optional Image)</Label>
                        <Input id="creativeAssetUrl" name="creativeAssetUrl" type="url" placeholder="https://yourcdn.com/path/to/image.jpg" className="w-full" />
                        {state.fieldErrors?.creativeAssetUrl && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.creativeAssetUrl.join(', ')}</p>}
                    </div>
                </CardContent>
              </Card>
            </div>

            <div style={{ display: currentStep === 3 ? 'block' : 'none' }}>
              <Card>
                <CardHeader>
                  <CardTitle>Step 3: Campaign Settings</CardTitle>
                  <CardDescription>Configure where and how your ad will be published.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <Label className="block text-sm font-medium text-gray-700 mb-2">Target Platforms</Label>
                     <div className="space-y-3">
                        <PlatformCheckbox id="platformMeta" name="platformMeta" label="Meta (Facebook/Instagram)" isConnected={isMetaConnected} />
                        <PlatformCheckbox id="platformX" name="platformX" label="X (formerly Twitter)" isConnected={isXConnected} />
                        <PlatformCheckbox id="platformGoogle" name="platformGoogle" label="Google Ads" isConnected={isGoogleConnected} />
                     </div>
                     {state.fieldErrors?.platformMeta && <p className="text-xs text-red-500 mt-2">{state.fieldErrors.platformMeta.join(', ')}</p>}
                  </div>
                   <div>
                      <Label htmlFor="budgetDaily" className="block text-sm font-medium text-gray-700 mb-1">Daily Budget ($)</Label>
                      <Input id="budgetDaily" name="budgetDaily" type="number" min="1" step="0.01" required placeholder="e.g., 10.00" className="w-full" />
                      {state.fieldErrors?.budgetDaily && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.budgetDaily.join(', ')}</p>}
                   </div>
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <Label htmlFor="scheduleStart" className="block text-sm font-medium text-gray-700 mb-1">Schedule Start</Label>
                        <Input id="scheduleStart" name="scheduleStart" type="datetime-local" required defaultValue={defaultScheduleStart} className="w-full" />
                        {state.fieldErrors?.scheduleStart && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.scheduleStart.join(', ')}</p>}
                    </div>
                    <div>
                        <Label htmlFor="scheduleEnd" className="block text-sm font-medium text-gray-700 mb-1">Schedule End (Optional)</Label>
                        <Input id="scheduleEnd" name="scheduleEnd" type="datetime-local" className="w-full" />
                        {state.fieldErrors?.scheduleEnd && <p className="text-xs text-red-500 mt-1">{state.fieldErrors.scheduleEnd.join(', ')}</p>}
                    </div>
                   </div>
                </CardContent>
              </Card>
            </div>
          </div>
          
          {state.error && !state.fieldErrors && <p className="text-sm text-red-500 mt-4 text-center">{state.error}</p>}
          <div className="flex justify-between items-center pt-6 mt-6 border-t">
            <Button type="button" variant="outline" onClick={prevStep} disabled={currentStep === 1 || pending}>
              Back
            </Button>

            {currentStep < STEPS.length ? (
              <Button type="button" onClick={nextStep} className="bg-orange-500 hover:bg-orange-600 text-white">
                Next
              </Button>
            ) : (
              <Button type="submit" className="bg-orange-500 hover:bg-orange-600 text-white min-w-[120px]" disabled={pending}>
                {pending ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Saving...</> : 'Save as Draft'}
              </Button>
            )}
          </div>
        </form>
      </div>
    </section>
  );
}

const PlatformCheckbox = ({ id, name, label, isConnected }: { id: string; name: string; label: string; isConnected?: boolean }) => {
    return (
      <div className="flex items-start">
        <Checkbox id={id} name={name} disabled={!isConnected} className="mt-1" />
        <div className="ml-3 text-sm">
          <Label htmlFor={id} className={!isConnected ? 'text-gray-400 cursor-not-allowed' : 'text-gray-700'}>
            {label}
          </Label>
          {!isConnected && (
            <p className="text-xs text-gray-500">
              Connection not found. <Link href="/dashboard/settings/integrations" className="text-blue-600 underline">Connect now</Link>.
            </p>
          )}
        </div>
      </div>
    );
}; 