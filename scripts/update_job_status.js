import { db } from '../lib/db/drizzle';
import { jobAds } from '../lib/db/schema';
import { eq } from 'drizzle-orm';

async function updateJobStatus() {
  const jobId = 2; // ID of the JobAd we created
  
  try {
    await db.update(jobAds)
      .set({ 
        status: 'scheduled',
        scheduleStart: new Date(Date.now() - 3600000), // 1 hour ago
        updatedAt: new Date() 
      })
      .where(eq(jobAds.id, jobId));
    
    console.log(`Successfully updated JobAd ${jobId} status to 'scheduled'`);
    
    const updatedJob = await db.query.jobAds.findFirst({
      where: eq(jobAds.id, jobId)
    });
    
    console.log('Updated JobAd:', updatedJob);
    
    process.exit(0);
  } catch (error) {
    console.error('Error updating JobAd status:', error);
    process.exit(1);
  }
}

updateJobStatus();
