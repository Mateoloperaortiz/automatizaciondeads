import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth/auth-options';
import { CreativeAdapter } from '@/lib/creative/creative-adapter';
import { Platform } from '@prisma/client';

const creativeAdapter = new CreativeAdapter();

// POST /api/creatives/[creativeId]/adaptations - Adapt a creative
export async function POST(
  req: NextRequest,
  { params }: { params: { creativeId: string } }
) {
  const session = await getServerSession(authOptions);
  
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  try {
    const { creativeId } = params;
    const data = await req.json();
    
    // We can adapt to a specific format or all formats for a platform
    if (data.platformFormatId) {
      // Adapt to a specific format
      const adaptation = await creativeAdapter.adaptCreative(
        creativeId,
        data.platformFormatId
      );
      
      return NextResponse.json(adaptation);
    } else if (data.platform) {
      // Adapt to all formats for a platform
      const adaptations = await creativeAdapter.adaptCreativeToAllFormats(
        creativeId,
        data.platform as Platform
      );
      
      return NextResponse.json(adaptations);
    } else {
      return NextResponse.json(
        { error: 'Missing platformFormatId or platform' },
        { status: 400 }
      );
    }
  } catch (error) {
    console.error('Error adapting creative:', error);
    return NextResponse.json(
      { error: 'Failed to adapt creative' },
      { status: 500 }
    );
  }
}

// GET /api/creatives/[creativeId]/adaptations - Get adaptations for a creative
export async function GET(
  req: NextRequest,
  { params }: { params: { creativeId: string } }
) {
  const session = await getServerSession(authOptions);
  
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  try {
    const { creativeId } = params;
    
    const adaptations = await creativeAdapter.getAdaptationsForCreative(creativeId);
    
    return NextResponse.json(adaptations);
  } catch (error) {
    console.error('Error fetching adaptations:', error);
    return NextResponse.json(
      { error: 'Failed to fetch adaptations' },
      { status: 500 }
    );
  }
}
