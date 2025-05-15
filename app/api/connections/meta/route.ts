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

    const metaConnection = await db.query.socialPlatformConnections.findFirst({
      where: and(
        eq(socialPlatformConnections.teamId, team.id),
        eq(socialPlatformConnections.platformName, 'meta')
      ),
      // Optionally, exclude sensitive fields like accessToken if not needed by client
      // columns: {
      //   accessToken: false,
      //   refreshToken: false 
      // }
    });

    if (!metaConnection) {
      // Return null or an empty object if no connection, SWR will handle it
      return NextResponse.json(null, { status: 200 }); 
    }

    // Important: Do not send raw tokens to the client unless absolutely necessary and secured.
    // For status display, platformAccountId is usually enough.
    // Create a DTO (Data Transfer Object) if more specific data is needed.
    const connectionStatus = {
        id: metaConnection.id,
        platformName: metaConnection.platformName,
        platformAccountId: metaConnection.platformAccountId,
        status: metaConnection.status,
        // Add any other safe-to-display fields
    };

    return NextResponse.json(connectionStatus);

  } catch (error) {
    console.error('Error fetching Meta connection status:', error);
    return NextResponse.json(
      { error: 'Failed to fetch Meta connection status' },
      { status: 500 }
    );
  }
} 