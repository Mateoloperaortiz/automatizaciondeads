import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth/auth-options';
import { PrismaClient } from '@prisma/client';
import { CreativeAdapter } from '@/lib/creative/creative-adapter';

const prisma = new PrismaClient();
const creativeAdapter = new CreativeAdapter();

// POST /api/creatives - Create a new creative
export async function POST(req: NextRequest) {
  const session = await getServerSession(authOptions);
  
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  try {
    const data = await req.json();
    
    // Basic validation
    if (!data.name || !data.originalUrl || !data.campaignId) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }
    
    // In a real implementation, we would upload the file to a storage service
    // and get the metadata (width, height, etc.) from the uploaded file
    // For POC purposes, we'll use the mock data provided
    
    const creative = await creativeAdapter.createCreative({
      name: data.name,
      originalUrl: data.originalUrl,
      mimeType: data.mimeType || 'image/jpeg',
      width: data.width || 1200,
      height: data.height || 800,
      fileSize: data.fileSize || 500, // 500KB
      campaignId: data.campaignId,
    });
    
    return NextResponse.json(creative);
  } catch (error) {
    console.error('Error creating creative:', error);
    return NextResponse.json(
      { error: 'Failed to create creative' },
      { status: 500 }
    );
  }
}

// GET /api/creatives - Get all creatives
export async function GET(req: NextRequest) {
  const session = await getServerSession(authOptions);
  
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  try {
    const { searchParams } = new URL(req.url);
    const campaignId = searchParams.get('campaignId');
    
    let creatives;
    
    if (campaignId) {
      creatives = await prisma.creative.findMany({
        where: { campaignId },
        orderBy: { createdAt: 'desc' },
      });
    } else {
      creatives = await prisma.creative.findMany({
        orderBy: { createdAt: 'desc' },
      });
    }
    
    return NextResponse.json(creatives);
  } catch (error) {
    console.error('Error fetching creatives:', error);
    return NextResponse.json(
      { error: 'Failed to fetch creatives' },
      { status: 500 }
    );
  }
}
