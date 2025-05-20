import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { db } from '@/lib/db/drizzle';
import {
  socialPlatformConnections,
  NewSocialPlatformConnection,
} from '@/lib/db/schema';
import { getTeamForUser } from '@/lib/db/queries';
import { encrypt } from '@/lib/security/crypto'; // For encrypting tokens
import { and, eq } from 'drizzle-orm';

const META_APP_ID = process.env.META_APP_ID;
const META_APP_SECRET = process.env.META_APP_SECRET;
const NEXT_PUBLIC_BASE_URL = process.env.NEXT_PUBLIC_BASE_URL;
const META_REDIRECT_URI_PATH = '/api/auth/meta/callback';
const META_API_VERSION = 'v19.0'; // Define and use a consistent API version

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const code = searchParams.get('code');
  const state = searchParams.get('state');
  const error = searchParams.get('error');
  const errorDescription = searchParams.get('error_description');

  const cookieStore = await cookies();
  const storedState = cookieStore.get('meta_oauth_state')?.value;
  // Clear the state cookie once used
  cookieStore.delete('meta_oauth_state');

  const integrationsPageUrl = '/dashboard/settings/integrations';
  const selectAccountPageUrl = '/dashboard/settings/integrations/meta/select-account';

  if (error) {
    console.error('Meta OAuth Error:', error, errorDescription);
    return NextResponse.redirect(
      `${NEXT_PUBLIC_BASE_URL}${integrationsPageUrl}?error=${encodeURIComponent(errorDescription || error)}`
    );
  }

  if (!state || state !== storedState) {
    console.error('Meta OAuth State mismatch. Possible CSRF attempt.');
    return NextResponse.redirect(
      `${NEXT_PUBLIC_BASE_URL}${integrationsPageUrl}?error=Invalid state. CSRF protection.`
    );
  }

  if (!code) {
    return NextResponse.redirect(
      `${NEXT_PUBLIC_BASE_URL}${integrationsPageUrl}?error=Authorization code not found.`
    );
  }

  if (!META_APP_ID || !META_APP_SECRET) {
    console.error('Meta app credentials not configured on server.');
     return NextResponse.redirect(
      `${NEXT_PUBLIC_BASE_URL}${integrationsPageUrl}?error=Meta integration not configured.`
    );
  }
  
  // Construct the full redirect URI for the token exchange
  const fullMetaRedirectUri = `${NEXT_PUBLIC_BASE_URL ? NEXT_PUBLIC_BASE_URL.replace(/\/$/, '') : ''}${META_REDIRECT_URI_PATH}`;

  try {
    // 1. Exchange code for access token
    const tokenResponse = await fetch(
      `https://graph.facebook.com/${META_API_VERSION}/oauth/access_token?client_id=${META_APP_ID}&redirect_uri=${encodeURIComponent(fullMetaRedirectUri)}&client_secret=${META_APP_SECRET}&code=${code}`
    );
    const tokenData = await tokenResponse.json();

    if (tokenData.error || !tokenData.access_token) {
      console.error('Meta Token Exchange Error:', tokenData.error);
      return NextResponse.redirect(
        `${NEXT_PUBLIC_BASE_URL}${integrationsPageUrl}?error=${encodeURIComponent(tokenData.error?.message || 'Failed to get access token.')}`
      );
    }
    const accessToken = tokenData.access_token;
    let longLivedAccessToken = accessToken;
    let longLivedExpiresIn = tokenData.expires_in;

    // Exchange for long-lived token (as before)
    const longLivedTokenResponse = await fetch(
      `https://graph.facebook.com/${META_API_VERSION}/oauth/access_token?` +
        `grant_type=fb_exchange_token&` +
        `client_id=${META_APP_ID}&` +
        `client_secret=${META_APP_SECRET}&` +
        `fb_exchange_token=${accessToken}`
    );

    if (longLivedTokenResponse.ok) {
      const longLivedTokenData = await longLivedTokenResponse.json();
      if (longLivedTokenData.access_token) {
        longLivedAccessToken = longLivedTokenData.access_token;
        longLivedExpiresIn = longLivedTokenData.expires_in; // Typically ~60 days (in seconds)
        console.log('Successfully exchanged for a long-lived Meta token.');
      } else {
        // Log error but proceed with the short-lived token if exchange fails for some reason
        console.warn('Could not exchange for a long-lived Meta token, proceeding with short-lived:', longLivedTokenData.error);
      }
    } else {
      const errorData = await longLivedTokenResponse.json();
      console.warn('Failed to exchange for long-lived Meta token, API error:', errorData.error?.message, 'Proceeding with short-lived token.');
    }

    // 2. Get user ID and Ad Account ID
    let platformUserId: string | undefined = undefined;
    let platformAccountId: string | undefined = undefined;
    let platformUserName: string | undefined = undefined; // Optional
    let adAccountsData: any = { data: [] }; // Initialize to prevent error if fetch fails before this

    try {
      const userProfileResponse = await fetch(`https://graph.facebook.com/${META_API_VERSION}/me?fields=id,name&access_token=${longLivedAccessToken}`);
      if (!userProfileResponse.ok) {
        const errorData = await userProfileResponse.json();
        console.error('Meta /me Error:', errorData.error);
        throw new Error(errorData.error?.message || 'Failed to fetch user profile from Meta.');
      }
      const userProfile = await userProfileResponse.json();
      platformUserId = userProfile.id;
      platformUserName = userProfile.name;

      const adAccountsResponse = await fetch(`https://graph.facebook.com/${META_API_VERSION}/me/adaccounts?fields=account_id,name&access_token=${longLivedAccessToken}`);
      if (!adAccountsResponse.ok) {
        const errorData = await adAccountsResponse.json();
        console.error('Meta /me/adaccounts Error:', errorData.error);
        throw new Error(errorData.error?.message || 'Failed to fetch ad accounts from Meta.');
      }
      adAccountsData = await adAccountsResponse.json();
      if (adAccountsData.data && adAccountsData.data.length > 0) {
        // For MVP, pick the first ad account. 
        // In a real app, you might let the user choose or have specific logic.
        platformAccountId = adAccountsData.data[0].account_id;
        console.log(`Meta Connection: User ${platformUserName} (${platformUserId}), Ad Account ID: ${platformAccountId}`);
      } else {
        // No ad accounts found, this might be an issue depending on requirements
        console.warn('No ad accounts found for this Meta user or error fetching them.');
        // You could redirect with an error or proceed without an ad account ID if that's acceptable
        // For now, we will proceed, platformAccountId will be null.
        // NEW: If no ad accounts, redirect with an error message
        return NextResponse.redirect(
          `${NEXT_PUBLIC_BASE_URL}${integrationsPageUrl}?error=${encodeURIComponent('No Meta Ad Accounts found for your profile.')}`
        );
      }
    } catch (apiError: any) {
      console.error('Error fetching Meta user/ad account details:', apiError);
      return NextResponse.redirect(
        `${NEXT_PUBLIC_BASE_URL}${integrationsPageUrl}?error=${encodeURIComponent(apiError.message || 'Failed to fetch details from Meta.')}`
      );
    }

    const team = await getTeamForUser();
    if (!team) {
      return NextResponse.redirect(
        `${NEXT_PUBLIC_BASE_URL}${integrationsPageUrl}?error=User session invalid or no team found.`
      );
    }

    // Instead of saving directly, store data in a temporary cookie and redirect to selection page
    const temporaryConnectionData = {
        longLivedAccessToken,
        tokenExpiresAt: longLivedExpiresIn ? new Date(Date.now() + longLivedExpiresIn * 1000).toISOString() : null,
        platformUserId,
        scopes: searchParams.get('granted_scopes') || null,
        adAccounts: adAccountsData.data.map((acc: {account_id: string, name: string}) => ({ id: acc.account_id, name: acc.name }))
    };

    cookieStore.set('meta_temp_connection', JSON.stringify(temporaryConnectionData), {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        maxAge: 60 * 15, // 15 minutes to complete selection
        path: '/', // Accessible by the select account page & its action
        sameSite: 'lax',
    });

    // Set a separate, client-readable cookie for just the ad accounts list for the selection UI
    const adAccountsListForClient = temporaryConnectionData.adAccounts;
    cookieStore.set('meta_ad_accounts_list', JSON.stringify(adAccountsListForClient), {
        httpOnly: false, // Client-readable
        secure: process.env.NODE_ENV === 'production',
        maxAge: 60 * 15, // Same expiry
        path: '/',
        sameSite: 'lax',
    });

    return NextResponse.redirect(`${NEXT_PUBLIC_BASE_URL}${selectAccountPageUrl}`);

  } catch (err: any) {
    console.error('Meta OAuth Callback Error:', err);
    return NextResponse.redirect(
      `${NEXT_PUBLIC_BASE_URL}${integrationsPageUrl}?error=${encodeURIComponent(err.message || 'An unexpected error occurred during Meta connection.')}`
    );
  }
} 