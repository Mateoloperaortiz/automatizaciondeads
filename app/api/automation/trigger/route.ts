import { NextResponse } from 'next/server';
import { processScheduledAds } from '@/lib/automation/engine';

// This is the endpoint that Vercel Cron Jobs will call.
// It should be protected by a secret.
export async function GET(request: Request) {
  // Secure this endpoint: Vercel Cron Jobs can send a secret in the Authorization header.
  // Example: Bearer YOUR_CRON_SECRET
  // You would store YOUR_CRON_SECRET in your environment variables.
  const authorization = request.headers.get('Authorization');
  const cronSecret = process.env.CRON_JOB_SECRET;

  if (!cronSecret) {
    console.error('CRON_JOB_SECRET is not set. Endpoint is not secure.');
    // In production, you might want to return 500 or not run if secret isn't set.
    // For now, we'll proceed but log a critical warning.
  }

  if (cronSecret && authorization !== `Bearer ${cronSecret}`) {
    console.warn('Unauthorized attempt to trigger cron job.');
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