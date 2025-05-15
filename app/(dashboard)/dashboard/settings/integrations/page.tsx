'use client';

import { useState, useEffect, useActionState, startTransition } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Facebook, Loader2 } from 'lucide-react';
import useSWR from 'swr';
import { SocialPlatformConnection } from '@/lib/db/schema';
import { redirectToMetaConnect, disconnectMetaAction, IntegrationActionState, connectXPlatformAction, redirectToGoogleConnect } from './actions';
import { useSearchParams } from 'next/navigation';

// Placeholder X Icon (replace with a proper one if available, e.g., from lucide-react or custom SVG)
const XIcon = () => (
    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
    </svg>
);

const GoogleIcon = () => (
    <svg className="h-6 w-6 text-red-500" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/><path fill="none" d="M1 1h22v22H1z"/>
    </svg>
);

const fetcher = (url: string) => fetch(url).then((res) => res.json());

const initialIntegrationState: IntegrationActionState = {
    error: null,
    success: false,
    message: null,
    platform: '' 
};

export default function IntegrationsPage() {
  const searchParams = useSearchParams();
  const oauthErrorMeta = searchParams.get('error'); // Kept for Meta backward compatibility if needed
  const oauthErrorX = searchParams.get('error_x');
  const oauthErrorGoogle = searchParams.get('error_google'); // Added for Google
  const oauthSuccess = searchParams.get('success'); 

  // Meta Connection State
  const { data: metaConnection, error: fetchMetaError, isLoading: isLoadingMeta, mutate: mutateMeta } = 
    useSWR<SocialPlatformConnection | null>('/api/connections/meta', fetcher);
  const [isConnectingMeta, setIsConnectingMeta] = useState(false);
  const [disconnectMetaState, submitDisconnectMetaAction, isDisconnectingMeta] = useActionState<IntegrationActionState, void>(
    disconnectMetaAction,
    { ...initialIntegrationState, platform: 'meta' }
  );

  // X (Twitter) Connection State
  const { data: xConnection, error: fetchXError, isLoading: isLoadingX, mutate: mutateX } = 
    useSWR<SocialPlatformConnection | null>('/api/connections/x', fetcher); // New SWR hook for X
  const [connectXState, submitConnectXAction, isConnectingX] = useActionState<IntegrationActionState, void>(
    connectXPlatformAction, // Use the new action
    { ...initialIntegrationState, platform: 'x' }
  );
  // Placeholder for X disconnect action state if/when implemented
  // const [disconnectXState, submitDisconnectXAction, isDisconnectingX] = useActionState(...);

  // Google State (New)
  const { data: googleConnection, error: fetchGoogleError, isLoading: isLoadingGoogle, mutate: mutateGoogle } = 
    useSWR<SocialPlatformConnection | null>('/api/connections/google', fetcher);
  const [isConnectingGoogle, setIsConnectingGoogle] = useState(false);

  const handleConnectMeta = async () => {
    setIsConnectingMeta(true);
    try { await redirectToMetaConnect(); } catch (e) { console.error(e); setIsConnectingMeta(false); }
  };

  const handleDisconnectMeta = () => {
    if (window.confirm('Are you sure you want to disconnect your Meta account?')) {
        startTransition(() => { submitDisconnectMetaAction(); });
    }
  };

  const handleConnectX = () => {
    startTransition(() => {
        submitConnectXAction(); // This is now useActionState's submit function
    });
  };

  // Placeholder for X disconnect handler
  const handleDisconnectX = async () => {
    alert('X disconnect logic not yet implemented.');
    // TODO: Implement disconnectXAction and use useActionState for it
    // mutateX(); // To re-fetch X connection status
  };

  const handleConnectGoogle = async () => {
    setIsConnectingGoogle(true);
    try { await redirectToGoogleConnect(); } catch (e) { console.error(e); setIsConnectingGoogle(false); }
  };

  const handleDisconnectGoogle = async () => {
    alert('Google disconnect logic not yet implemented.');
  };

  useEffect(() => {
    if (disconnectMetaState.success) {
      alert(disconnectMetaState.message || 'Meta account disconnected.');
      mutateMeta();
    } else if (disconnectMetaState.error) {
      alert(`Error disconnecting Meta: ${disconnectMetaState.error}`);
    }
  }, [disconnectMetaState, mutateMeta]);
  
  useEffect(() => {
    if (connectXState.success) {
      alert(connectXState.message || 'X Ads platform enabled successfully.');
      mutateX();
    } else if (connectXState.error && connectXState.platform === 'x') {
      alert(`Error enabling X Ads: ${connectXState.error}`);
    }
  }, [connectXState, mutateX]);

  useEffect(() => {
    if (oauthSuccess === 'meta_connected' || oauthSuccess === 'x_connected' || oauthSuccess === 'google_connected') {
      alert(`Account for ${oauthSuccess.split('_')[0].toUpperCase()} connected successfully!`);
      if (oauthSuccess === 'meta_connected') mutateMeta();
      if (oauthSuccess === 'x_connected') mutateX();
      if (oauthSuccess === 'google_connected') mutateGoogle();
      // router.replace('/dashboard/settings/integrations', undefined, { shallow: true }); // Clean URL
    }
  }, [oauthSuccess, mutateMeta, mutateX, mutateGoogle]);

  // Meta UI Content
  let metaStatusContent;
  if (isLoadingMeta) {
    metaStatusContent = <p className="text-sm text-gray-500">Loading Meta status...</p>;
  } else if (fetchMetaError) {
    metaStatusContent = <p className="text-sm text-red-500">Failed to load Meta status.</p>;
  } else if (metaConnection) {
    metaStatusContent = (
      <div className="space-y-2">
        <p className="text-sm text-green-600 font-medium">Connected (Ad Account: {metaConnection.platformAccountId || 'N/A'})</p>
        {disconnectMetaState.error && disconnectMetaState.platform === 'meta' && <p className="text-xs text-red-500">Error: {disconnectMetaState.error}</p>}
        <Button variant="outline" onClick={handleDisconnectMeta} disabled={isDisconnectingMeta} className="w-full sm:w-auto">
          {isDisconnectingMeta ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null} Disconnect Meta
        </Button>
      </div>
    );
  } else {
    metaStatusContent = (
      <div className="flex flex-col items-start space-y-2">
        {oauthErrorMeta && <p className="text-sm text-red-500">Connection failed: {oauthErrorMeta}</p>}
        {disconnectMetaState.error && disconnectMetaState.platform === 'meta' && <p className="text-xs text-red-500">Error: {disconnectMetaState.error}</p>} 
        <Button onClick={handleConnectMeta} disabled={isConnectingMeta} className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white">
          {isConnectingMeta ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Facebook className="mr-2 h-4 w-4" />} Connect to Meta
        </Button>
      </div>
    );
  }

  // X (Twitter) UI Content
  let xStatusContent;
  if (isLoadingX) {
    xStatusContent = <p className="text-sm text-gray-500">Loading X status...</p>;
  } else if (fetchXError) {
    xStatusContent = <p className="text-sm text-red-500">Failed to load X status.</p>;
  } else if (xConnection) {
    xStatusContent = (
      <div className="space-y-2">
        <p className="text-sm text-green-600 font-medium">
          X Ads Enabled (Ad Account: {xConnection.platformAccountId || 'N/A'}, Funding ID: {xConnection.fundingInstrumentId || 'N/A'})
        </p>
        {connectXState.error && connectXState.platform === 'x' && <p className="text-xs text-red-500">Setup Error: {connectXState.error}</p>} 
        <Button variant="outline" onClick={handleDisconnectX} className="w-full sm:w-auto">Disconnect X (Placeholder)</Button>
      </div>
    );
  } else {
    xStatusContent = (
      <div className="flex flex-col items-start space-y-2">
        {oauthErrorX && <p className="text-sm text-red-500">X Connection failed: {oauthErrorX}</p>}
        {connectXState.error && connectXState.platform === 'x' && <p className="text-xs text-red-500">Error: {connectXState.error}</p>}
        <Button onClick={handleConnectX} disabled={isConnectingX} className="w-full sm:w-auto bg-black hover:bg-gray-800 text-white">
          {isConnectingX ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <XIcon />}<span className="ml-2">Enable X Ads</span>
        </Button>
      </div>
    );
  }

  // Google Ads UI Content (New)
  let googleStatusContent;
  if (isLoadingGoogle) {
    googleStatusContent = <p className="text-sm text-gray-500">Loading Google Ads status...</p>;
  } else if (fetchGoogleError) {
    googleStatusContent = <p className="text-sm text-red-500">Failed to load Google Ads status.</p>;
  } else if (googleConnection) {
    googleStatusContent = (
      <div className="space-y-2">
        <p className="text-sm text-green-600 font-medium">Connected (User ID: {googleConnection.platformUserId || 'N/A'})</p>
        {/* Placeholder for disconnect error display */}
        <Button variant="outline" onClick={handleDisconnectGoogle} /*disabled={isDisconnectingGoogle}*/ className="w-full sm:w-auto">
          {/* {isDisconnectingGoogle ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null} */} Disconnect Google (Placeholder)
        </Button>
      </div>
    );
  } else {
    googleStatusContent = (
      <div className="flex flex-col items-start space-y-2">
        {oauthErrorGoogle && <p className="text-sm text-red-500">Google Connection failed: {oauthErrorGoogle}</p>}
        {/* Placeholder for disconnect error display */} 
        <Button onClick={handleConnectGoogle} disabled={isConnectingGoogle} className="w-full sm:w-auto bg-red-600 hover:bg-red-700 text-white">
          {isConnectingGoogle ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <GoogleIcon />}<span className="ml-2">Connect to Google</span>
        </Button>
      </div>
    );
  }

  return (
    <section className="flex-1 p-4 lg:p-8">
      <h1 className="text-lg lg:text-2xl font-medium mb-6">Platform Integrations</h1>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Meta Card (as before, using metaStatusContent) */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-lg font-semibold">Meta (Facebook/Instagram)</CardTitle>
            <Facebook className="h-6 w-6 text-blue-600" />
          </CardHeader>
          <CardContent>
            <CardDescription className="mb-4 text-sm">
              Connect your Meta Ads account to automate ad posting on Facebook and Instagram.
            </CardDescription>
            {metaStatusContent}
          </CardContent>
        </Card>

        {/* X (Twitter) Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-lg font-semibold">X (formerly Twitter)</CardTitle>
            <XIcon />
          </CardHeader>
          <CardContent>
            <CardDescription className="mb-4 text-sm">
              Connect your X Ads account for automated ad campaigns on X.
            </CardDescription>
            {xStatusContent} 
          </CardContent>
        </Card>

        {/* Google Ads Card (Placeholder as before) */}
        <Card className="opacity-50"> 
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-lg font-semibold">Google Ads</CardTitle>
            <GoogleIcon />
          </CardHeader>
          <CardContent>
            <CardDescription className="mb-4 text-sm">
              Connect Google Ads account to manage and automate campaigns across Google's network.
            </CardDescription>
            {googleStatusContent}
          </CardContent>
        </Card>
      </div>
    </section>
  );
} 