// Update job status using Drizzle ORM
import { db } from '../lib/db/drizzle.js';
import { jobAds } from '../lib/db/schema.js';
import { eq } from 'drizzle-orm';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { config } from 'dotenv';
import { join } from 'path';

// Setup proper path resolution for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables from .env file
config({ path: join(__dirname, '..', '.env') });

async function updateJobStatus() {
  const jobId = 2; // ID of the JobAd we created
  
  try {
    // Update the job ad with ID 2
    await db.update(jobAds)
      .set({ 
        status: 'scheduled',
        scheduleStart: new Date(Date.now() - 3600000), // 1 hour ago
        updatedAt: new Date(),
        platformsMetaEnabled: true
      })
      .where(eq(jobAds.id, jobId));
    
    console.log(`Successfully updated JobAd ${jobId} status to 'scheduled'`);
    
    // Verify the update
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
