import { NextResponse } from 'next/server';
import { getTeamForUser } from '@/lib/db/queries';
import { db } from '@/lib/db/drizzle';
import { socialPlatformConnections } from '@/lib/db/schema';
import { and, eq } from 'drizzle-orm';

export const dynamic = 'force-dynamic'; // Ensure fresh data on every request

export async function GET() {
  try {
    const team = await getTeamForUser();
    if (!team) {
      return NextResponse.json({ error: 'User not authenticated or no team found.' }, { status: 401 });
    }

    const allConnections = await db.query.socialPlatformConnections.findMany({
      where: eq(socialPlatformConnections.teamId, team.id),
    });

    // Structure the connections by platform name for easy lookup on the client
    const connectionsMap: { [key: string]: typeof socialPlatformConnections.$inferSelect | null } = {
      meta: null,
      x: null,
      google: null,
    };

    allConnections.forEach(conn => {
      if (connectionsMap.hasOwnProperty(conn.platformName)) {
        connectionsMap[conn.platformName] = conn;
      }
    });

    return NextResponse.json(connectionsMap);

  } catch (err: any) {
    console.error('Error fetching connections status:', err);
    return NextResponse.json({ error: 'Failed to fetch connections status.' }, { status: 500 });
  }
} 