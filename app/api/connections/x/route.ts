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

    const xConnection = await db.query.socialPlatformConnections.findFirst({
      where: and(
        eq(socialPlatformConnections.teamId, team.id),
        eq(socialPlatformConnections.platformName, 'x') // Check for 'x' platform
      ),
      // Select only necessary, non-sensitive fields for client display
      columns: {
        id: true,
        platformName: true,
        platformUserId: true, // X User ID
        platformAccountId: true, // X Ad Account ID (will be null initially)
        status: true,
        // Exclude accessToken, refreshToken
      }
    });

    if (!xConnection) {
      return NextResponse.json(null, { status: 200 }); 
    }

    return NextResponse.json(xConnection);

  } catch (error) {
    console.error('Error fetching X connection status:', error);
    return NextResponse.json(
      { error: 'Failed to fetch X connection status' },
      { status: 500 }
    );
  }
} 