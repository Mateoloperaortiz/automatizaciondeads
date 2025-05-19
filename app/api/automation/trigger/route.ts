import { NextRequest, NextResponse } from 'next/server';
import { processScheduledAds } from '@/lib/automation/engine';

// This is the endpoint that Vercel Cron Jobs will call.
// It should be protected by a secret.
export async function GET(request: NextRequest) {
  const vercelCronSecretHeader = request.headers.get('x-vercel-cron-secret');
  const authorizationHeader = request.headers.get('Authorization');
  const configuredSecret = process.env.CRON_JOB_SECRET;

  let authorized = false;

  if (!configuredSecret) {
    console.warn(
      'CRON_JOB_SECRET not set in environment variables. Allowing cron trigger for local development/testing, but THIS IS INSECURE FOR PRODUCTION.'
    );
    authorized = true; // Allow for local dev if no secret is configured server-side
  } else {
    // Check Vercel's native header first
    if (vercelCronSecretHeader && vercelCronSecretHeader === configuredSecret) {
      authorized = true;
      console.log("Authorized via x-vercel-cron-secret header.");
    } 
    // Fallback to Bearer token for local curl testing if Vercel header isn't present or didn't match
    else if (authorizationHeader && authorizationHeader === `Bearer ${configuredSecret}`) {
      console.log("Authorized via Bearer token (local testing).");
      authorized = true;
    } else if (vercelCronSecretHeader && vercelCronSecretHeader !== configuredSecret) {
        // Log if Vercel secret was present but didn't match
        console.warn('Unauthorized: x-vercel-cron-secret did not match configured CRON_JOB_SECRET.');
    } else if (authorizationHeader && authorizationHeader !== `Bearer ${configuredSecret}` ) {
        // Log if Authorization bearer was present but didn't match
        console.warn('Unauthorized: Authorization Bearer token did not match configured CRON_JOB_SECRET.');
    } else if (!vercelCronSecretHeader && !authorizationHeader) {
        // Log if no auth method was provided but a secret is configured
        console.warn('Unauthorized: No secret provided in x-vercel-cron-secret or Authorization header, but CRON_JOB_SECRET is configured.');
    }
  }

  if (!authorized) {
    console.warn('Unauthorized attempt to trigger cron job. Secrets did not match or were not provided correctly when a secret is configured.');
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  console.log('Cron job trigger received. Starting ad processing...');
  try {
    const result = await processScheduledAds();
    console.log('Ad processing finished via cron trigger.', result);
    return NextResponse.json({ success: true, ...result });
  } catch (error) {
    console.error('Error running processScheduledAds via cron trigger:', error);
    return NextResponse.json({ success: false, error: 'Failed to process ads' }, { status: 500 });
  }
} 