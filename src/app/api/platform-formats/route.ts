import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth/auth-options';
import { PrismaClient, Platform } from '@prisma/client';
import { initializePlatformFormats } from '@/lib/creative/platform-formats';

const prisma = new PrismaClient();

// GET /api/platform-formats - Get all platform formats
export async function GET(req: NextRequest) {
  const session = await getServerSession(authOptions);
  
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  try {
    const { searchParams } = new URL(req.url);
    const platform = searchParams.get('platform');
    
    // Initialize formats if none exist yet
    const formatCount = await prisma.platformFormat.count();
    if (formatCount === 0) {
      await initializePlatformFormats();
    }
    
    let formats;
    
    if (platform) {
      formats = await prisma.platformFormat.findMany({
        where: { platform: platform as Platform },
        orderBy: { formatName: 'asc' },
      });
    } else {
      formats = await prisma.platformFormat.findMany({
        orderBy: [{ platform: 'asc' }, { formatName: 'asc' }],
      });
    }
    
    return NextResponse.json(formats);
  } catch (error) {
    console.error('Error fetching platform formats:', error);
    return NextResponse.json(
      { error: 'Failed to fetch platform formats' },
      { status: 500 }
    );
  }
}
