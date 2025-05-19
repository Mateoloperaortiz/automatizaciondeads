'use client';

import { useEffect, useState, useActionState, startTransition } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Loader2, ArrowLeft } from 'lucide-react';
import { finalizeMetaConnectionAction, IntegrationActionState } from '../../actions';
import Cookies from 'js-cookie'; // Using js-cookie for easier client-side cookie access if needed, though server action will read HttpOnly cookie.

interface AdAccount {
  id: string;
  name: string;
}

interface TempConnectionData {
  longLivedAccessToken: string;
  tokenExpiresAt: string | null;
  platformUserId?: string;
  scopes: string | null;
  adAccounts: AdAccount[];
}

const initialFinalizeState: IntegrationActionState = {
  error: null,
  success: false,
  message: null,
  platform: 'meta',
};

export default function SelectMetaAccountPage() {
  const router = useRouter();
  const [tempData, setTempData] = useState<TempConnectionData | null>(null);
  const [selectedAccountId, setSelectedAccountId] = useState<string | undefined>(undefined);
  const [isLoadingPage, setIsLoadingPage] = useState(true);
  const [cookieError, setCookieError] = useState<string | null>(null);

  // Server action state
  const [finalizeState, submitFinalizeAction, isFinalizing] = useActionState<IntegrationActionState, FormData>(
    finalizeMetaConnectionAction,
    initialFinalizeState
  );

  useEffect(() => {
    // HttpOnly cookies cannot be directly read by client-side JS.
    // This component will primarily serve as the UI for a form that posts to a server action.
    // The server action will be responsible for reading the HttpOnly cookie.
    // We can, however, check if a *non*-HttpOnly cookie was set as a flag, or just proceed.
    // For this example, we'll assume the page loads and tries to get data if the user was redirected here.
    // A simple way to pass non-sensitive info like "number of accounts" or a flag could be via query params from the callback.
    // Or, the server action called by this page will handle cookie reading.
    // For now, we'll fetch a client-side readable cookie if one was set (for testing purposes), 
    // but the real logic depends on the server action reading the HttpOnly one.

    // Simulating that the page expects data; if user lands here without a redirect, it should show error.
    // A robust way is to have the server action redirect here with a query param if the cookie was set.
    // For now, just setting isLoadingPage to false to render the form.
    // We will need to fetch the ad accounts to display them for selection.
    // This info should have been passed from the callback.
    // The server action `finalizeMetaConnectionAction` will actually read the HttpOnly cookie.
    // This page needs to display the ad accounts. Let's assume the callback sets a *client-readable* cookie
    // for the list of ad accounts (not ideal for tokens, but okay for names/IDs for selection).
    // OR, better: the server action that redirects here could pass ad account names/IDs as query params or a flash message.

    // **Revised Strategy**: This page will render a form. The form submission to `finalizeMetaConnectionAction`
    // will be where the HttpOnly `meta_temp_connection` cookie is read and processed server-side.
    // The client just needs to know to show this form. For displaying ad accounts, it's tricky without client-side JS reading them.
    // The best approach is for the OAuth callback to redirect to this page with the ad accounts list embedded or fetched via a dedicated (safe) API endpoint.
    // For simplicity in this step, we'll assume the server action will get everything it needs from the HttpOnly cookie.
    // The form will just submit the selected account ID.
    // To display choices: We MUST get the ad account list on the client. The temporary cookie is HttpOnly.
    // Solution: The callback should set a *second*, non-HttpOnly cookie with just the adAccount list (names/IDs).

    const adAccountsCookie = Cookies.get('meta_ad_accounts_list'); // Assume callback sets this separately
    if (adAccountsCookie) {
      try {
        const accounts = JSON.parse(adAccountsCookie);
        setTempData({ adAccounts: accounts } as TempConnectionData); // Only set what's readable
        if (accounts.length > 0) {
          setSelectedAccountId(accounts[0].id);
        }
      } catch (e) {
        setCookieError('Failed to parse ad account information.');
      }
    } else {
      // This means the user might have navigated here directly or cookie expired.
      setCookieError('Ad account selection data not found. Please try connecting Meta again.');
    }
    setIsLoadingPage(false);

  }, []);

  useEffect(() => {
    if (finalizeState.success) {
      alert(finalizeState.message || 'Meta account connected successfully!');
      Cookies.remove('meta_ad_accounts_list'); // Clean up client-side list cookie
      router.push('/dashboard/settings/integrations');
    } else if (finalizeState.error) {
      alert(`Error: ${finalizeState.error}`);
    }
  }, [finalizeState, router]);

  if (isLoadingPage) {
    return <div className="flex justify-center items-center h-64"><Loader2 className="h-8 w-8 animate-spin text-orange-500" /> <p className='ml-2'>Loading...</p></div>;
  }

  if (cookieError || !tempData || tempData.adAccounts.length === 0) {
    return (
      <section className="flex-1 p-4 lg:p-8">
        <div className="flex items-center mb-6">
          <Link href="/dashboard/settings/integrations" className="mr-4 p-2 rounded-full hover:bg-gray-200">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <h1 className="text-lg lg:text-2xl font-medium">Connect Meta Ad Account</h1>
        </div>
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-500">{cookieError || 'No ad accounts available for selection or data is missing.'}</p>
            <p className="mt-2 text-sm">Please try <Link href="/dashboard/settings/integrations" className="underline text-blue-600">connecting your Meta account</Link> again.</p>
          </CardContent>
        </Card>
      </section>
    );
  }

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedAccountId) {
        alert("Please select an ad account.");
        return;
    }
    const formData = new FormData();
    formData.append('selectedAccountId', selectedAccountId);
    startTransition(() => {
        submitFinalizeAction(formData);
    });
  };

  return (
    <section className="flex-1 p-4 lg:p-8">
      <div className="flex items-center mb-6">
         {/* No back arrow here, user should complete or explicitly cancel via integrations page */}
        <h1 className="text-lg lg:text-2xl font-medium">Select Meta Ad Account</h1>
      </div>
      <form onSubmit={handleSubmit} className="max-w-md mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Choose Ad Account</CardTitle>
            <CardDescription>Select the Meta Ad Account you want to use for posting jobs.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <RadioGroup value={selectedAccountId} onValueChange={setSelectedAccountId} name="selectedAccountId">
              {tempData.adAccounts.map((account) => (
                <div key={account.id} className="flex items-center space-x-2 border p-3 rounded-md">
                  <RadioGroupItem value={account.id} id={`acc-${account.id}`} />
                  <Label htmlFor={`acc-${account.id}`} className="flex-1 cursor-pointer">
                    <span className="font-medium">{account.name}</span>
                    <span className="block text-xs text-gray-500">ID: {account.id}</span>
                  </Label>
                </div>
              ))}
            </RadioGroup>
            {finalizeState.error && (
              <p className="text-sm text-red-500">{finalizeState.error}</p>
            )}
            <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white" disabled={isFinalizing || !selectedAccountId}>
              {isFinalizing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Connect this Ad Account
            </Button>
            <Button type="button" variant="outline" className="w-full mt-2" onClick={() => router.push('/dashboard/settings/integrations')} disabled={isFinalizing}>
                Cancel and go back
            </Button>
          </CardContent>
        </Card>
      </form>
    </section>
  );
} 