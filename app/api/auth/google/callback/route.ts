import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { db } from '@/lib/db/drizzle';
import {
  socialPlatformConnections,
  NewSocialPlatformConnection,
} from '@/lib/db/schema';
import { getTeamForUser } from '@/lib/db/queries';
import { encrypt } from '@/lib/security/crypto';
import { eq, and } from 'drizzle-orm';

const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID;
const GOOGLE_CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET;
const NEXT_PUBLIC_BASE_URL = process.env.NEXT_PUBLIC_BASE_URL;
const GOOGLE_REDIRECT_URI_PATH = '/api/auth/google/callback';
const GOOGLE_TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token';
const GOOGLE_ADS_CUSTOMER_ID_FOR_APP = process.env.GOOGLE_CUSTOMER_ID_FOR_AUTOMATION;

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const code = searchParams.get('code');
  const state = searchParams.get('state');
  const error = searchParams.get('error');
  const errorDescription = searchParams.get('error_description'); // Google might use this

  // @ts-ignore : Linter issue with Next.js Server Action cookies
  const cookieStore = cookies();
  const storedState = cookieStore.get('google_oauth_state')?.value;
  cookieStore.delete('google_oauth_state');

  const integrationsPageUrl = '/dashboard/settings/integrations';
  const baseRedirectUrl = `${NEXT_PUBLIC_BASE_URL || ''}${integrationsPageUrl}`;

  if (error) {
    console.error('Google OAuth Error:', error, errorDescription);
    return NextResponse.redirect(`${baseRedirectUrl}?error_google=${encodeURIComponent(errorDescription || error)}`);
  }

  if (!state || state !== storedState) {
    console.error('Google OAuth State mismatch. Possible CSRF attempt.');
    return NextResponse.redirect(`${baseRedirectUrl}?error_google=Invalid%20state`);
  }

  if (!code) {
    return NextResponse.redirect(`${baseRedirectUrl}?error_google=Authorization%20code%20not%20found`);
  }

  if (!GOOGLE_CLIENT_ID || !GOOGLE_CLIENT_SECRET) {
    console.error('Google client credentials not configured.');
    return NextResponse.redirect(`${baseRedirectUrl}?error_google=Google%20integration%20misconfigured`);
  }

  if (!GOOGLE_ADS_CUSTOMER_ID_FOR_APP) {
    console.error('GOOGLE_CUSTOMER_ID_FOR_AUTOMATION is not set in .env for the app to use.');
    return NextResponse.redirect(`${baseRedirectUrl}?error_google=Target%20Google%20Ads%20account%20misconfigured`);
  }

  try {
    const tokenRequestBody = new URLSearchParams({
      code: code,
      client_id: GOOGLE_CLIENT_ID,
      client_secret: GOOGLE_CLIENT_SECRET,
      redirect_uri: `${NEXT_PUBLIC_BASE_URL?.replace(/\/$/, '')}${GOOGLE_REDIRECT_URI_PATH}`,
      grant_type: 'authorization_code',
    });

    const tokenResponse = await fetch(GOOGLE_TOKEN_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: tokenRequestBody.toString(),
    });

    const tokenData = await tokenResponse.json();

    if (!tokenResponse.ok || tokenData.error) {
      console.error('Google Token Exchange Error:', tokenData.error_description || tokenData.error || tokenData);
      const errorMessage = tokenData.error_description || tokenData.error || 'Failed to get access token from Google.';
      return NextResponse.redirect(`${baseRedirectUrl}?error_google=${encodeURIComponent(errorMessage)}`);
    }

    const accessToken = tokenData.access_token;
    const refreshToken = tokenData.refresh_token; // Should be present if access_type=offline was used
    const expiresIn = tokenData.expires_in; // in seconds
    const scopes = tokenData.scope; // Space-separated string of granted scopes

    // For Google Ads API, you don't directly get a user ID from /me that's relevant for Ads.
    // The crucial identifiers are the Developer Token (from .env) and the Customer ID (CID) of the Ads account.
    // The Customer ID might be known beforehand or selected by the user after OAuth.
    // For now, we will store the tokens. The CID will be needed when making Ads API calls.
    // We can add a placeholder for platformUserId if Google returns one via /userinfo endpoint, if needed.
    let platformUserId: string | undefined; 
    // Optionally, call Google's /oauth2/v3/userinfo endpoint with the accessToken to get user info like email/sub (Google User ID)
    // const userInfoResponse = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', { headers: { Authorization: `Bearer ${accessToken}`}});
    // if(userInfoResponse.ok) { const userInfo = await userInfoResponse.json(); platformUserId = userInfo.sub; }

    const team = await getTeamForUser();
    if (!team) {
      return NextResponse.redirect(`${baseRedirectUrl}?error_google=User%20session%20invalid%20or%20no%20team`);
    }

    const encryptedAccessToken = encrypt(accessToken);
    const encryptedRefreshToken = refreshToken ? encrypt(refreshToken) : undefined;

    const connectionData: NewSocialPlatformConnection = {
      teamId: team.id,
      platformName: 'google',
      accessToken: encryptedAccessToken,
      refreshToken: encryptedRefreshToken,
      tokenExpiresAt: expiresIn ? new Date(Date.now() + expiresIn * 1000) : null,
      scopes: scopes || null,
      platformUserId: platformUserId, // Will be Google User ID (sub) if fetched
      platformAccountId: GOOGLE_ADS_CUSTOMER_ID_FOR_APP.replace(/-/g, ''),
      status: 'active',
    };

    await db.insert(socialPlatformConnections)
      .values(connectionData)
      .onConflictDoUpdate({
        target: [socialPlatformConnections.teamId, socialPlatformConnections.platformName],
        set: { 
            accessToken: encryptedAccessToken,
            refreshToken: encryptedRefreshToken,
            tokenExpiresAt: connectionData.tokenExpiresAt,
            scopes: connectionData.scopes,
            platformUserId: platformUserId,
            platformAccountId: GOOGLE_ADS_CUSTOMER_ID_FOR_APP.replace(/-/g, ''),
            status: 'active',
            updatedAt: new Date() 
        }, 
      });

    return NextResponse.redirect(`${baseRedirectUrl}?success=google_connected`);

  } catch (err: any) {
    console.error('Google OAuth Callback Error:', err);
    return NextResponse.redirect(`${baseRedirectUrl}?error_google=${encodeURIComponent(err.message || 'Unexpected Google callback error')}`);
  }
} 