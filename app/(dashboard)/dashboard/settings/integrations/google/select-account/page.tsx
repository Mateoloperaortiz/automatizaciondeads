'use client';

import { useEffect, useState, useActionState, startTransition } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Loader2, ArrowLeft } from 'lucide-react';
import {
  finalizeGoogleConnectionAction,
  IntegrationActionState,
} from '../../actions';
import Cookies from 'js-cookie';

interface AdAccount {
  id: string; // e.g., "customers/1234567890"
  name: string; // Descriptive name if available
}

const initialFinalizeState: IntegrationActionState = {
  error: null,
  success: false,
  message: null,
  platform: 'google',
};

export default function SelectGoogleAccountPage() {
  const router = useRouter();
  const [adAccounts, setAdAccounts] = useState<AdAccount[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState<string | undefined>(
    undefined
  );
  const [isLoadingPage, setIsLoadingPage] = useState(true);
  const [cookieError, setCookieError] = useState<string | null>(null);

  const [finalizeState, submitFinalizeAction, isFinalizing] =
    useActionState<IntegrationActionState, FormData>(
      finalizeGoogleConnectionAction,
      initialFinalizeState
    );

  useEffect(() => {
    const adAccountsCookie = Cookies.get('google_ad_accounts_list');
    if (adAccountsCookie) {
      try {
        const accounts = JSON.parse(adAccountsCookie);
        setAdAccounts(accounts);
        if (accounts.length > 0) {
          setSelectedAccountId(accounts[0].id);
        }
      } catch (e) {
        setCookieError('Failed to parse ad account information.');
      }
    } else {
      setCookieError(
        'Ad account selection data not found. Please try connecting Google again.'
      );
    }
    setIsLoadingPage(false);
  }, []);

  useEffect(() => {
    if (finalizeState.success) {
      alert(finalizeState.message || 'Google Ads account connected successfully!');
      Cookies.remove('google_ad_accounts_list');
      router.push('/dashboard/settings/integrations');
    } else if (finalizeState.error) {
      alert(`Error: ${finalizeState.error}`);
    }
  }, [finalizeState, router]);

  if (isLoadingPage) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-orange-500" />{' '}
        <p className="ml-2">Loading Google Ads Accounts...</p>
      </div>
    );
  }

  if (cookieError || adAccounts.length === 0) {
    return (
      <section className="flex-1 p-4 lg:p-8">
        <div className="flex items-center mb-6">
          <Link
            href="/dashboard/settings/integrations"
            className="mr-4 p-2 rounded-full hover:bg-gray-200"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <h1 className="text-lg lg:text-2xl font-medium">
            Connect Google Ads Account
          </h1>
        </div>
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-500">
              {cookieError ||
                'No ad accounts available for selection or data is missing.'}
            </p>
            <p className="mt-2 text-sm">
              Please try{' '}
              <Link
                href="/dashboard/settings/integrations"
                className="underline text-blue-600"
              >
                connecting your Google account
              </Link>{' '}
              again.
            </p>
          </CardContent>
        </Card>
      </section>
    );
  }

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedAccountId) {
      alert('Please select an ad account.');
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
        <h1 className="text-lg lg:text-2xl font-medium">
          Select Google Ads Account
        </h1>
      </div>
      <form onSubmit={handleSubmit} className="max-w-md mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Choose Ad Account</CardTitle>
            <CardDescription>
              Select the Google Ads Account you want to use for posting jobs.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <RadioGroup
              value={selectedAccountId}
              onValueChange={setSelectedAccountId}
              name="selectedAccountId"
            >
              {adAccounts.map((account) => (
                <div
                  key={account.id}
                  className="flex items-center space-x-2 border p-3 rounded-md"
                >
                  <RadioGroupItem value={account.id} id={`acc-${account.id}`} />
                  <Label
                    htmlFor={`acc-${account.id}`}
                    className="flex-1 cursor-pointer"
                  >
                    <span className="font-medium">{account.name}</span>
                    <span className="block text-xs text-gray-500">
                      ID: {account.id}
                    </span>
                  </Label>
                </div>
              ))}
            </RadioGroup>
            {finalizeState.error && (
              <p className="text-sm text-red-500">{finalizeState.error}</p>
            )}
            <Button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              disabled={isFinalizing || !selectedAccountId}
            >
              {isFinalizing ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : null}
              Connect this Ad Account
            </Button>
            <Button
              type="button"
              variant="outline"
              className="w-full mt-2"
              onClick={() => router.push('/dashboard/settings/integrations')}
              disabled={isFinalizing}
            >
              Cancel and go back
            </Button>
          </CardContent>
        </Card>
      </form>
    </section>
  );
} 