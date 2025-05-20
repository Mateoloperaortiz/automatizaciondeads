'use server';

import { z } from 'zod';
import { db } from '@/lib/db/drizzle';
import { jobAds, NewJobAd } from '@/lib/db/schema';
import { getSession } from '@/lib/auth/session'; // Assumes getSession can be used in server actions
import { getTeamForUser } from '@/lib/db/queries'; // Use this instead
import { revalidatePath } from 'next/cache';
import { eq, and } from 'drizzle-orm'; // Import eq and and

// Zod schema for form validation
const JobAdFormSchema = z.object({
  title: z.string().min(1, 'Title is required').max(100, 'Title must be 100 characters or less'),
  companyName: z.string().max(100, 'Company name must be 100 characters or less').optional().or(z.literal('')),
  descriptionShort: z.string().min(1, 'Short description is required').max(280, 'Short description must be 280 characters or less'),
  descriptionLong: z.string().optional(),
  targetUrl: z.string().url('Invalid URL format').min(1, 'Target URL is required'),
  creativeAssetUrl: z.string().url('Invalid URL format').optional().or(z.literal('')),
  platformMeta: z.string().optional(), // Checkbox value is 'on' or undefined
  platformX: z.string().optional(),
  platformGoogle: z.string().optional(),
  budgetDaily: z.preprocess(
    (val) => (typeof val === 'string' ? parseFloat(val) : val),
    z.number().min(1, 'Daily budget must be at least $1')
  ),
  scheduleStart: z.string().min(1, 'Schedule start date is required').refine((date) => !isNaN(new Date(date).getTime()), 'Invalid start date'),
  scheduleEnd: z.string().optional().refine((date) => !date || !isNaN(new Date(date).getTime()), 'Invalid end date'),
});

export type CreateJobAdState = {
  message?: string | null;
  error?: string | null;
  fieldErrors?: {
    [key: string]: string[] | undefined;
  };
  success?: boolean;
};

export async function createJobAdAction(
  prevState: CreateJobAdState,
  formData: FormData
): Promise<CreateJobAdState> {
  const session = await getSession();
  if (!session?.user?.id) {
    return { error: 'User not authenticated', success: false };
  }
  const userId = session.user.id;

  // Get current team ID for the user
  const team = await getTeamForUser(); 
  if (!team) {
    return { error: 'User is not associated with any team or team could not be fetched.', success: false };
  }
  const teamId = team.id;
  
  const rawFormData = Object.fromEntries(formData.entries());
  const validatedFields = JobAdFormSchema.safeParse(rawFormData);

  if (!validatedFields.success) {
    console.error('Validation Errors:', validatedFields.error.flatten().fieldErrors);
    return {
      error: 'Invalid form data. Please check the fields.',
      fieldErrors: validatedFields.error.flatten().fieldErrors,
      success: false,
    };
  }

  const data = validatedFields.data;

  // At least one platform must be selected
  if (!data.platformMeta && !data.platformX && !data.platformGoogle) {
    return {
        error: 'Please select at least one target platform.',
        fieldErrors: { platformMeta: ['Select at least one platform'] }, // crude way to highlight
        success: false,
    };
  }

  try {
    const newJobAdData: Omit<NewJobAd, 'id' | 'createdAt' | 'updatedAt' | 'status'> = {
      teamId: teamId,
      title: data.title,
      companyName: data.companyName || null,
      descriptionShort: data.descriptionShort,
      descriptionLong: data.descriptionLong || null,
      targetUrl: data.targetUrl,
      creativeAssetUrl: data.creativeAssetUrl || null,
      platformsMetaEnabled: data.platformMeta === 'on',
      platformsXEnabled: data.platformX === 'on',
      platformsGoogleEnabled: data.platformGoogle === 'on',
      budgetDaily: data.budgetDaily.toString(), // Drizzle decimal expects string or number
      scheduleStart: new Date(data.scheduleStart),
      scheduleEnd: data.scheduleEnd ? new Date(data.scheduleEnd) : null,
      createdByUserId: userId,
      // status will default to 'draft' as per schema
    };

    await db.insert(jobAds).values(newJobAdData as NewJobAd);

  } catch (e) {
    console.error('Database error creating job ad:', e);
    return { error: 'Failed to create job ad. Database error.', success: false };
  }

  revalidatePath('/dashboard/jobs');
  // Redirect to the job ads list page after successful creation
  // However, useActionState doesn't handle redirects directly. 
  // We'll return a success state and the page can handle the redirect or show a message.
  return { message: 'Job ad created successfully!', success: true };
  // For actual redirect, you might do it on the client-side after checking `state.success`
  // or if not using useActionState directly, the action itself can call redirect().
  // Since we will use useActionState, a client-side redirect is better.
}

// Type for Update Action State (can be the same as Create for now)
export type UpdateJobAdState = CreateJobAdState & { jobId?: number };

// Action for updating a job ad
export async function updateJobAdAction(
  prevState: UpdateJobAdState,
  formData: FormData
): Promise<UpdateJobAdState> {
  const session = await getSession();
  if (!session?.user?.id) {
    return { ...prevState, error: 'User not authenticated', success: false };
  }
  const userId = session.user.id; // For ownership/permission checks if needed later

  const jobIdString = formData.get('jobId');
  if (!jobIdString || typeof jobIdString !== 'string') {
    return { ...prevState, error: 'Job ID is missing or invalid.', success: false };
  }
  const jobId = parseInt(jobIdString, 10);
  if (isNaN(jobId)) {
    return { ...prevState, error: 'Invalid Job ID format.', success: false };
  }

  const team = await getTeamForUser();
  if (!team) {
    return { ...prevState, error: 'User is not associated with any team or team could not be fetched.', success: false };
  }
  const teamId = team.id;

  const rawFormData = Object.fromEntries(formData.entries());
  const validatedFields = JobAdFormSchema.safeParse(rawFormData);

  if (!validatedFields.success) {
    return {
      ...prevState,
      jobId,
      error: 'Invalid form data. Please check the fields.',
      fieldErrors: validatedFields.error.flatten().fieldErrors,
      success: false,
    };
  }

  const data = validatedFields.data;

  if (!data.platformMeta && !data.platformX && !data.platformGoogle) {
    return {
      ...prevState,
      jobId,
      error: 'Please select at least one target platform.',
      fieldErrors: { platformMeta: ['Select at least one platform'] },
      success: false,
    };
  }

  try {
    // Verify the job ad belongs to the user's team before updating
    const existingAd = await db.query.jobAds.findFirst({
      where: and(eq(jobAds.id, jobId), eq(jobAds.teamId, teamId)),
    });

    if (!existingAd) {
      return { ...prevState, jobId, error: 'Job ad not found or you do not have permission to edit it.', success: false };
    }

    const updatedJobAdData = {
      // teamId and createdByUserId are not updated
      title: data.title,
      companyName: data.companyName || null,
      descriptionShort: data.descriptionShort,
      descriptionLong: data.descriptionLong || null,
      targetUrl: data.targetUrl,
      creativeAssetUrl: data.creativeAssetUrl || null,
      platformsMetaEnabled: data.platformMeta === 'on',
      platformsXEnabled: data.platformX === 'on',
      platformsGoogleEnabled: data.platformGoogle === 'on',
      budgetDaily: data.budgetDaily.toString(),
      scheduleStart: new Date(data.scheduleStart),
      scheduleEnd: data.scheduleEnd ? new Date(data.scheduleEnd) : null,
      // status might be updatable through a different action/flow, not directly here unless intended
      // For now, not updating status via this general edit form.
      updatedAt: new Date(), // Drizzle schema handles this with $onUpdate, but explicit is fine
    };

    await db.update(jobAds).set(updatedJobAdData).where(eq(jobAds.id, jobId));

  } catch (e) {
    console.error('Database error updating job ad:', e);
    return { ...prevState, jobId, error: 'Failed to update job ad. Database error.', success: false };
  }

  revalidatePath('/dashboard/jobs');
  revalidatePath(`/dashboard/jobs/${jobId}/edit`); // Revalidate the edit page itself
  return { ...prevState, jobId, message: 'Job ad updated successfully!', success: true, fieldErrors: {} };
}

// Type for Delete Action State
export type DeleteJobAdState = {
  error?: string | null;
  success?: boolean;
  jobId?: number; // To know which item was processed if needed
};

// Action for deleting a job ad
export async function deleteJobAdAction(
  prevState: DeleteJobAdState,
  formData: FormData // Or just pass jobId directly if preferred
): Promise<DeleteJobAdState> {
  const session = await getSession();
  if (!session?.user?.id) {
    return { ...prevState, error: 'User not authenticated', success: false };
  }

  const jobIdString = formData.get('jobId');
  if (!jobIdString || typeof jobIdString !== 'string') {
    return { ...prevState, error: 'Job ID is missing or invalid for deletion.', success: false };
  }
  const jobId = parseInt(jobIdString, 10);
  if (isNaN(jobId)) {
    return { ...prevState, error: 'Invalid Job ID format for deletion.', success: false };
  }

  const team = await getTeamForUser();
  if (!team) {
    return { ...prevState, jobId, error: 'User is not associated with any team.', success: false };
  }
  const teamId = team.id;

  try {
    // Verify the job ad belongs to the user's team before deleting
    const existingAd = await db.query.jobAds.findFirst({
      where: and(eq(jobAds.id, jobId), eq(jobAds.teamId, teamId)),
      columns: { id: true }, // Only need to confirm existence and ownership
    });

    if (!existingAd) {
      return { ...prevState, jobId, error: 'Job ad not found or you do not have permission to delete it.', success: false };
    }

    await db.delete(jobAds).where(eq(jobAds.id, jobId));

  } catch (e) {
    console.error('Database error deleting job ad:', e);
    return { ...prevState, jobId, error: 'Failed to delete job ad. Database error.', success: false };
  }

  revalidatePath('/dashboard/jobs');
  // No need to revalidate edit page for a deleted item
  return { ...prevState, jobId, success: true }; // Can add a success message if needed
}

export type PublishJobAdState = {
    error?: string | null;
    success?: boolean;
    message?: string | null;
    jobAdId?: number;
};

export async function publishJobAdNowAction(
    prevState: PublishJobAdState,
    formData: FormData // formData will contain jobAdId
): Promise<PublishJobAdState> {
    const jobAdIdString = formData.get('jobAdId');
    if (!jobAdIdString || typeof jobAdIdString !== 'string') {
        return { error: 'Job Ad ID is missing or invalid.' };
    }
    const jobAdId = parseInt(jobAdIdString, 10);
    if (isNaN(jobAdId)) {
        return { error: 'Invalid Job Ad ID format.' };
    }

    const team = await getTeamForUser(); // For permission check
    if (!team) {
        return { error: 'User not authenticated or no team found.', jobAdId };
    }

    try {
        const adToPublish = await db.query.jobAds.findFirst({
            where: and(eq(jobAds.id, jobAdId), eq(jobAds.teamId, team.id))
        });

        if (!adToPublish) {
            return { error: 'Job Ad not found or you do not have permission.', jobAdId };
        }

        // Only allow publishing if it's in a draft or perhaps a failed state, not already live/processing/scheduled with future date
        // More complex status transition logic could be added here.
        if (adToPublish.status === 'draft' || adToPublish.status === 'error_processing' || adToPublish.status === 'segmentation_failed' || adToPublish.status === 'post_failed_meta' || adToPublish.status === 'post_failed_x' || adToPublish.status === 'post_failed_google' || adToPublish.status === 'post_failed_all') {
            await db.update(jobAds).set({
                status: 'scheduled',
                scheduleStart: new Date(), // Set scheduleStart to now to make it eligible immediately
                updatedAt: new Date()
            }).where(eq(jobAds.id, jobAdId));
            
            revalidatePath('/dashboard/jobs');
            // Note: This action itself doesn't trigger the AutomationEngine directly.
            // The AutomationEngine (via cron or manual trigger) will pick it up.
            return { success: true, message: `Job Ad #${jobAdId} has been scheduled for immediate processing.`, jobAdId };
        } else {
            return { error: `Job Ad #${jobAdId} is already ${adToPublish.status} and cannot be published now.`, jobAdId };
        }

    } catch (err: any) {
        console.error('Error in publishJobAdNowAction:', err);
        return { error: err.message || 'Failed to schedule job ad for publishing.', jobAdId };
    }
}

export type TriggerEngineState = {
    error?: string | null;
    success?: boolean;
    message?: string | null;
    processedCount?: number;
};

export async function triggerAutomationEngineAction(
    prevState: TriggerEngineState
): Promise<TriggerEngineState> {
    console.log("Attempting to trigger automation engine manually...");

    const triggerUrl = `${process.env.NEXT_PUBLIC_BASE_URL}/api/automation/trigger`;
    const cronSecret = process.env.CRON_JOB_SECRET;

    if (!cronSecret) {
        return { error: "CRON_JOB_SECRET is not configured. Cannot trigger engine securely." };
    }

    try {
        const response = await fetch(triggerUrl, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${cronSecret}`,
            },
            cache: 'no-store', // Ensure it hits the endpoint fresh
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error(`Error triggering automation engine: ${response.status}`, errorText);
            return { error: `Failed to trigger engine: ${response.status} ${errorText}` };
        }

        const result = await response.json();
        console.log("Automation engine triggered successfully via action:", result);
        return { 
            success: result.success,
            message: result.message || 'Automation engine run complete.',
            processedCount: result.processedCount,
            error: result.error
        };

    } catch (err: any) {
        console.error('Error in triggerAutomationEngineAction:', err);
        return { error: err.message || 'Failed to trigger automation engine.' };
    }
} 