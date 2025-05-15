import { NextResponse } from 'next/server';
import { db } from '@/lib/db/drizzle';
import { jobAds } from '@/lib/db/schema';
import { getTeamForUser } from '@/lib/db/queries';
import { eq } from 'drizzle-orm';

export async function GET() {
  try {
    const team = await getTeamForUser();

    if (!team) {
      return NextResponse.json(
        { error: 'User not authenticated or not associated with a team' },
        { status: 401 }
      );
    }

    const ads = await db
      .select()
      .from(jobAds)
      .where(eq(jobAds.teamId, team.id))
      .orderBy(jobAds.createdAt); // Or any other order you prefer

    return NextResponse.json(ads);
  } catch (error) {
    console.error('Error fetching job ads:', error);
    return NextResponse.json(
      { error: 'Failed to fetch job ads' },
      { status: 500 }
    );
  }
} 