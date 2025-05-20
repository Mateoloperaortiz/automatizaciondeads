import { NextResponse } from 'next/server';
import { db } from '@/lib/db/drizzle';
import { jobAds } from '@/lib/db/schema';
import { getTeamForUser } from '@/lib/db/queries';
import { eq, and } from 'drizzle-orm';

export async function GET(
  request: Request, // Standard Request object for context
  { params }: { params: { jobId: string } }
) {
  try {
    const team = await getTeamForUser();
    if (!team) {
      return NextResponse.json(
        { error: 'User not authenticated or not associated with a team' },
        { status: 401 }
      );
    }

    const jobIdParam = await params.jobId;
    const jobId = parseInt(jobIdParam, 10);
    if (isNaN(jobId)) {
      return NextResponse.json({ error: 'Invalid Job ID' }, { status: 400 });
    }

    const ad = await db.query.jobAds.findFirst({
      where: and(eq(jobAds.id, jobId), eq(jobAds.teamId, team.id)),
    });

    if (!ad) {
      return NextResponse.json({ error: 'Job ad not found or access denied' }, { status: 404 });
    }

    return NextResponse.json(ad);
  } catch (error) {
    console.error('Error fetching job ad:', error);
    return NextResponse.json(
      { error: 'Failed to fetch job ad' },
      { status: 500 }
    );
  }
}                  