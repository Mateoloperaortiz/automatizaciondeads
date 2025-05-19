import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db/drizzle';
import { jobAds } from '@/lib/db/schema';
import { eq } from 'drizzle-orm';

export async function GET(request: NextRequest) {
  const jobId = 2; // ID of the JobAd we created
  
  try {
    await db.update(jobAds)
      .set({ 
        status: 'scheduled',
        scheduleStart: new Date(Date.now() - 3600000), // 1 hour ago
        updatedAt: new Date() 
      })
      .where(eq(jobAds.id, jobId));
    
    const updatedJob = await db.query.jobAds.findFirst({
      where: eq(jobAds.id, jobId)
    });
    
    return NextResponse.json({ 
      success: true, 
      message: `Successfully updated JobAd ${jobId} status to 'scheduled'`,
      job: updatedJob
    });
  } catch (error) {
    console.error('Error updating JobAd status:', error);
    return NextResponse.json({ 
      success: false, 
      message: 'Error updating JobAd status',
      error: String(error)
    }, { status: 500 });
  }
}
