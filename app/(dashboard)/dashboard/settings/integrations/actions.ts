'use server';

import { redirect } from 'next/navigation';
import crypto from 'crypto';
import { cookies } from 'next/headers';
import { getTeamForUser } from '@/lib/db/queries';
import { db } from '@/lib/db/drizzle';
import { socialPlatformConnections, NewSocialPlatformConnection } from '@/lib/db/schema';
import { and, eq } from 'drizzle-orm';
import { revalidatePath } from 'next/cache';
import { decrypt, encrypt } from '@/lib/security/crypto';
import { fetchXFundingInstrumentId } from '@/lib/automation/platform_apis/x_ads_api';

const META_APP_ID = process.env.META_APP_ID;
const NEXT_PUBLIC_BASE_URL = process.env.NEXT_PUBLIC_BASE_URL;
// Construct redirect URI more safely if NEXT_PUBLIC_BASE_URL might have trailing slash
const META_REDIRECT_URI = `${NEXT_PUBLIC_BASE_URL ? NEXT_PUBLIC_BASE_URL.replace(/\/$/, '') : ''}/api/auth/meta/callback`;

// Define the required scopes for your application
// Example scopes: 'email', 'public_profile', 'ads_management', 'ads_read', 'pages_read_engagement'
// Consult Meta documentation for the exact scopes needed for your job ad posting functionality.
const META_SCOPES = ['ads_management', 'ads_read', 'pages_read_engagement', 'business_management'].join(',');

export async function getMetaOAuthURL(): Promise<{ error?: string; url?: string }> {
  if (!META_APP_ID) {
    console.error('META_APP_ID is not configured in environment variables.');
    return { error: 'Meta integration is not configured on the server.' };
  }
  if (!NEXT_PUBLIC_BASE_URL) {
    console.error('NEXT_PUBLIC_BASE_URL is not configured.');
    return { error: 'Application base URL is not configured.' };
  }

  try {
    // Generate a random state for CSRF protection
    const state = crypto.randomBytes(16).toString('hex');
    // Store the state in a short-lived HttpOnly cookie
    const cookieStore = await cookies();
    cookieStore.set('meta_oauth_state', state, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 60 * 15, // 15 minutes
      path: '/',
      sameSite: 'lax',
    });

    const params = new URLSearchParams({
      client_id: META_APP_ID,
      redirect_uri: META_REDIRECT_URI,
      scope: META_SCOPES,
      response_type: 'code',
      state: state,
    });

    const oauthURL = `https://www.facebook.com/v19.0/dialog/oauth?${params.toString()}`;
    return { url: oauthURL };

  } catch (error) {
    console.error('Error generating Meta OAuth URL:', error);
    return { error: 'Could not initiate Meta authentication.' };
  }
}

// This is the action that the UI button will call.
// It gets the URL and then redirects.
export async function redirectToMetaConnect() {
  const result = await getMetaOAuthURL();
  if (result.url) {
    redirect(result.url);
  } else {
    // Handle error, perhaps by redirecting to an error page or showing a message
    // For now, redirecting back to integrations page with an error query param (not ideal for production)
    console.error('Failed to get Meta OAuth URL:', result.error);
    redirect(`/dashboard/settings/integrations?error=${encodeURIComponent(result.error || 'Unknown error during Meta connect')}`);
  }
}

export type IntegrationActionState = {
  error?: string | null;
  success?: boolean;
  message?: string | null;
  platform?: string; // To identify which platform action was for
};

export async function disconnectMetaAction(
  prevState: IntegrationActionState
): Promise<IntegrationActionState> {
  const team = await getTeamForUser();
  if (!team) {
    return { error: 'User not authenticated or no team found.', platform: 'meta' };
  }

  try {
    // 1. Find the existing connection to get the token and platformUserId
    const connection = await db.query.socialPlatformConnections.findFirst({
      where: and(
        eq(socialPlatformConnections.teamId, team.id),
        eq(socialPlatformConnections.platformName, 'meta')
      ),
    });

    if (!connection) {
      return { error: 'No active Meta connection found to disconnect.', platform: 'meta' };
    }

    // 2. Attempt to revoke permissions on Meta's side
    if (connection.accessToken && connection.platformUserId) {
      try {
        const decryptedAccessToken = decrypt(connection.accessToken);
        const revokeResponse = await fetch(
          `https://graph.facebook.com/${connection.platformUserId}/permissions`,
          {
            method: 'DELETE',
            headers: {
              Authorization: `Bearer ${decryptedAccessToken}`,
            },
          }
        );
        const revokeData = await revokeResponse.json();
        if (revokeResponse.ok && revokeData.success) {
          console.log('Successfully revoked Meta app permissions.');
        } else {
          console.warn('Failed to revoke Meta app permissions or already revoked:', revokeData.error?.message || revokeData);
        }
      } catch (revokeErr: any) {
        console.warn('Error during Meta permission revocation API call:', revokeErr.message);
        // Continue to delete from our DB even if revocation fails
      }
    }

    // 3. Delete the connection from our database
    const result = await db
      .delete(socialPlatformConnections)
      .where(eq(socialPlatformConnections.id, connection.id)) // Delete by specific connection ID
      .returning({ id: socialPlatformConnections.id });

    if (result.length === 0) {
      // This case should ideally not be reached if `connection` was found
      return { error: 'Failed to delete the connection from the database.', platform: 'meta' };
    }

    revalidatePath('/dashboard/settings/integrations');
    revalidatePath('/api/connections/meta'); 

    return { success: true, message: 'Meta account disconnected successfully.', platform: 'meta' };

  } catch (err: any) {
    console.error('Error disconnecting Meta account:', err);
    return { error: err.message || 'Failed to disconnect Meta account.', platform: 'meta' };
  }
}

export async function finalizeMetaConnectionAction(
  prevState: IntegrationActionState,
  formData: FormData
): Promise<IntegrationActionState> {
  const selectedAccountId = formData.get('selectedAccountId') as string;
  if (!selectedAccountId) {
    return { error: 'No ad account was selected.', platform: 'meta' };
  }

  const cookieStore = await cookies();
  const tempCookie = cookieStore.get('meta_temp_connection')?.value;
  cookieStore.delete('meta_temp_connection');
  cookieStore.delete('meta_ad_accounts_list');

  if (!tempCookie) {
    return { error: 'Connection session expired or data missing. Please try again.', platform: 'meta' };
  }

  let tempData;
  try {
    tempData = JSON.parse(tempCookie);
  } catch (e) {
    return { error: 'Failed to parse connection data. Please try again.', platform: 'meta' };
  }

  const { 
    longLivedAccessToken,
    tokenExpiresAt,
    platformUserId,
    scopes 
  } = tempData;

  if (!longLivedAccessToken) {
    return { error: 'Access token missing from session. Please try again.', platform: 'meta' };
  }

  const team = await getTeamForUser();
  if (!team) {
    return { error: 'User not authenticated or no team found.', platform: 'meta' };
  }

  try {
    const encryptedAccessToken = encrypt(longLivedAccessToken);
    
    const connectionData: NewSocialPlatformConnection = {
      teamId: team.id,
      platformName: 'meta',
      accessToken: encryptedAccessToken,
      tokenExpiresAt: tokenExpiresAt ? new Date(tokenExpiresAt) : null,
      scopes: scopes || null,
      platformUserId: platformUserId || null, 
      platformAccountId: selectedAccountId,
      status: 'active',
    };

    await db.insert(socialPlatformConnections)
      .values(connectionData)
      .onConflictDoUpdate({
        target: [socialPlatformConnections.teamId, socialPlatformConnections.platformName],
        set: {
          accessToken: encryptedAccessToken,
          tokenExpiresAt: connectionData.tokenExpiresAt,
          scopes: connectionData.scopes,
          platformUserId: connectionData.platformUserId,
          platformAccountId: selectedAccountId, // Ensure this is updated
          status: 'active',
          updatedAt: new Date(),
        }
      });
    
    revalidatePath('/dashboard/settings/integrations');
    revalidatePath('/api/connections/meta');

    return { success: true, message: 'Meta account connected successfully with selected ad account.', platform: 'meta' };

  } catch (err: any) {
    console.error('Error finalizing Meta connection:', err);
    return { error: err.message || 'Failed to finalize Meta connection.', platform: 'meta' };
  }
}

// --- X (Twitter) Simplified Connection Action ---
// This action now assumes the app uses its own pre-configured X credentials (consumer + user access tokens from .env)
// to operate on a specific X Ads Account ID (also from .env or configured per team).
// It will primarily fetch and store the funding_instrument_id for that account.

export async function connectXPlatformAction(
    prevState: IntegrationActionState
): Promise<IntegrationActionState> {
    const team = await getTeamForUser();
    if (!team) {
        return { error: 'User not authenticated or no team found.', platform: 'x' };
    }

    const xAdsAccountId = process.env.X_ADS_ACCOUNT_ID;
    const xUserAccessToken = process.env.X_USER_ACCESS_TOKEN; // Your app's user token
    const xUserTokenSecret = process.env.X_USER_ACCESS_TOKEN_SECRET; // Your app's user token secret

    if (!xAdsAccountId) {
        return { error: 'X Ads Account ID not configured in server environment.', platform: 'x' };
    }
    if (!xUserAccessToken || !xUserTokenSecret) {
        return { error: 'X User Access Token/Secret for the app not configured.', platform: 'x' };
    }

    let fundingInstrumentId: string | null = null;
    try {
        console.log(`Fetching funding instrument ID for X Ads Account: ${xAdsAccountId}`);
        fundingInstrumentId = await fetchXFundingInstrumentId(xAdsAccountId, xUserAccessToken, xUserTokenSecret);
        if (!fundingInstrumentId) {
            return { error: 'Could not fetch X Ads funding instrument ID. Please check account setup.', platform: 'x' };
        }
        console.log(`Fetched X Funding Instrument ID: ${fundingInstrumentId}`);
    } catch (e: any) {
        console.error("Error fetching X funding instrument ID:", e);
        return { error: e.message || 'Failed to fetch X funding instrument ID.', platform: 'x' };
    }

    try {
        // We still store a connection record, but accessToken and tokenSecret might be "app_managed"
        // or we can store placeholder/app-level identifiers if needed for consistency.
        // Or, simply store the platformAccountId and fundingInstrumentId.
        // For this simplified flow, accessToken will be a placeholder as actual tokens are from .env for API calls.
        const connectionData: NewSocialPlatformConnection = {
            teamId: team.id,
            platformName: 'x',
            platformAccountId: xAdsAccountId, // The pre-configured Ad Account ID
            fundingInstrumentId: fundingInstrumentId,
            accessToken: encrypt('app_managed_x_token'), // Placeholder, real token is from .env
            // tokenSecret: encrypt('app_managed_x_secret'), // Placeholder
            status: 'active',
            // platformUserId can be fetched if your app's user token has user context
        };

        await db.insert(socialPlatformConnections)
            .values(connectionData)
            .onConflictDoUpdate({
                target: [socialPlatformConnections.teamId, socialPlatformConnections.platformName],
                set: { 
                    platformAccountId: xAdsAccountId,
                    fundingInstrumentId: fundingInstrumentId, 
                    accessToken: encrypt('app_managed_x_token'),
                    // tokenSecret: encrypt('app_managed_x_secret'),
                    status: 'active', 
                    updatedAt: new Date() 
                },
            });
        
        revalidatePath('/dashboard/settings/integrations');
        revalidatePath('/api/connections/x');
        return { success: true, message: 'X Ads platform enabled and funding instrument verified.', platform: 'x' };

    } catch (err: any) {
        console.error('Error enabling X Ads platform:', err);
        return { error: err.message || 'Failed to enable X Ads platform.', platform: 'x' };
    }
}

export async function disconnectXPlatformAction(
  prevState: IntegrationActionState
): Promise<IntegrationActionState> {
  const team = await getTeamForUser();
  if (!team) {
    return { error: 'User not authenticated or no team found.', platform: 'x' };
  }

  try {
    // 1. Find the existing connection
    const connection = await db.query.socialPlatformConnections.findFirst({
      where: and(
        eq(socialPlatformConnections.teamId, team.id),
        eq(socialPlatformConnections.platformName, 'x')
      ),
    });

    if (!connection) {
      return { error: 'No active X connection found to disconnect.', platform: 'x' };
    }

    // 2. For X, since we use app-level tokens (from .env) for API calls via connectXPlatformAction,
    //    a user-specific token revocation on X's side isn't applicable in the same way as Meta.
    //    The "disconnection" primarily means removing the configuration from our database.
    //    If there were a specific X API endpoint to de-authorize an app for a specific ads account
    //    that was linked via an app-level token, that could be called here.
    //    However, the current setup implies the app itself has permissions, and we're just
    //    disabling its use for this team by removing the DB record.

    // 3. Delete the connection from our database
    const result = await db
      .delete(socialPlatformConnections)
      .where(eq(socialPlatformConnections.id, connection.id)) // Delete by specific connection ID
      .returning({ id: socialPlatformConnections.id });

    if (result.length === 0) {
      return { error: 'Failed to delete the X connection from the database.', platform: 'x' };
    }

    revalidatePath('/dashboard/settings/integrations');
    revalidatePath('/api/connections/x'); 

    return { success: true, message: 'X Ads platform disconnected successfully.', platform: 'x' };

  } catch (err: any) {
    console.error('Error disconnecting X Ads platform:', err);
    return { error: err.message || 'Failed to disconnect X Ads platform.', platform: 'x' };
  }
}

// --- Google Ads OAuth 2.0 Actions ---
const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID;
// const GOOGLE_CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET; // Needed for token exchange
const GOOGLE_REDIRECT_URI_PATH = '/api/auth/google/callback';
// Scope for Google Ads API
const GOOGLE_ADS_SCOPE = 'https://www.googleapis.com/auth/adwords';

export async function redirectToGoogleConnect() {
    if (!GOOGLE_CLIENT_ID) {
        console.error('GOOGLE_CLIENT_ID is not configured.');
        redirect(`/dashboard/settings/integrations?error_google=${encodeURIComponent('Google config error')}`);
        return;
    }
    const NEXT_PUBLIC_BASE_URL = process.env.NEXT_PUBLIC_BASE_URL;
    if (!NEXT_PUBLIC_BASE_URL) {
        console.error('NEXT_PUBLIC_BASE_URL is not configured.');
        redirect(`/dashboard/settings/integrations?error_google=${encodeURIComponent('Base URL config error')}`);
        return;
    }
    const redirectUri = `${NEXT_PUBLIC_BASE_URL.replace(/\/$/, '')}${GOOGLE_REDIRECT_URI_PATH}`;
    const state = crypto.randomBytes(16).toString('hex');

    const cookieStore = await cookies();
    cookieStore.set('google_oauth_state', state, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        maxAge: 60 * 15, // 15 minutes
        path: '/',
        sameSite: 'lax',
    });

    const params = new URLSearchParams({
        client_id: GOOGLE_CLIENT_ID,
        redirect_uri: redirectUri,
        response_type: 'code',
        scope: GOOGLE_ADS_SCOPE,
        state: state,
        access_type: 'offline', // Request refresh token
        prompt: 'consent',       // Ensure user sees consent screen for offline access
    });

    const oauthURL = `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
    redirect(oauthURL);
}
