import { NextResponse } from 'next/server';
import { db } from '@/lib/db/drizzle';
import { socialPlatformConnections } from '@/lib/db/schema';
import { getTeamForUser } from '@/lib/db/queries';
import { eq, and } from 'drizzle-orm';

export async function GET() {
  try {
    const team = await getTeamForUser();
    if (!team) {
      return NextResponse.json(
        { error: 'User not authenticated or not associated with a team' },
        { status: 401 }
      );
    }

    const googleConnection = await db.query.socialPlatformConnections.findFirst({
      where: and(
        eq(socialPlatformConnections.teamId, team.id),
        eq(socialPlatformConnections.platformName, 'google') // Check for 'google' platform
      ),
      columns: {
        id: true,
        platformName: true,
        platformUserId: true, // Google User ID (sub)
        platformAccountId: true, // Google Ads Customer ID (will be null initially or set after user selection)
        status: true,
      }
    });

    if (!googleConnection) {
      return NextResponse.json(null, { status: 200 }); 
    }

    return NextResponse.json(googleConnection);

  } catch (error) {
    console.error('Error fetching Google connection status:', error);
    return NextResponse.json(
      { error: 'Failed to fetch Google connection status' },
      { status: 500 }
    );
  }
} 