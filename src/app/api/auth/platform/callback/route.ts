import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth/next'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

// Platform-specific token exchange configuration
const platformConfig = {
  meta: {
    tokenUrl: 'https://graph.facebook.com/v17.0/oauth/access_token',
    clientId: process.env.META_CLIENT_ID,
    clientSecret: process.env.META_CLIENT_SECRET,
  },
  google: {
    tokenUrl: 'https://oauth2.googleapis.com/token',
    clientId: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  },
  twitter: {
    tokenUrl: 'https://api.twitter.com/2/oauth2/token',
    clientId: process.env.TWITTER_CLIENT_ID,
    clientSecret: process.env.TWITTER_CLIENT_SECRET,
  },
  tiktok: {
    tokenUrl: 'https://open-api.tiktok.com/oauth/access_token/',
    clientId: process.env.TIKTOK_CLIENT_ID,
    clientSecret: process.env.TIKTOK_CLIENT_SECRET,
  },
  snapchat: {
    tokenUrl: 'https://accounts.snapchat.com/login/oauth2/access_token',
    clientId: process.env.SNAPCHAT_CLIENT_ID,
    clientSecret: process.env.SNAPCHAT_CLIENT_SECRET,
  },
}

export async function GET(request: NextRequest) {
  const session = await getServerSession()
  
  if (!session) {
    return NextResponse.redirect(new URL('/auth/login', request.url))
  }
  
  const searchParams = request.nextUrl.searchParams
  const code = searchParams.get('code')
  const platform = searchParams.get('platform')
  const state = searchParams.get('state')
  const error = searchParams.get('error')
  
  // Check for error from OAuth provider
  if (error) {
    return NextResponse.redirect(
      new URL(`/platforms?error=${error}&platform=${platform}`, request.url)
    )
  }
  
  // Validate required parameters
  if (!code || !platform || !state) {
    return NextResponse.redirect(
      new URL('/platforms?error=missing_params', request.url)
    )
  }
  
  // Validate platform
  const config = platformConfig[platform as keyof typeof platformConfig]
  if (!config) {
    return NextResponse.redirect(
      new URL('/platforms?error=unsupported_platform', request.url)
    )
  }
  
  // Validate state parameter to prevent CSRF
  const storedState = request.cookies.get('platform_oauth_state')?.value
  if (state !== storedState) {
    return NextResponse.redirect(
      new URL('/platforms?error=invalid_state', request.url)
    )
  }
  
  // Exchange the authorization code for an access token
  try {
    const redirectUrl = new URL('/api/auth/platform/callback', request.url)
    redirectUrl.searchParams.append('platform', platform)
    
    // In a real implementation, we would make this request to the platform
    // For the POC, we'll simulate a successful token exchange
    /*
    const tokenResponse = await fetch(config.tokenUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        client_id: config.clientId || '',
        client_secret: config.clientSecret || '',
        grant_type: 'authorization_code',
        code,
        redirect_uri: redirectUrl.toString(),
      }),
    })
    
    const tokenData = await tokenResponse.json()
    
    if (!tokenResponse.ok) {
      throw new Error(tokenData.error || 'Failed to exchange token')
    }
    
    // Store the token in the database
    await prisma.platformConnection.upsert({
      where: {
        userId_platform: {
          userId: session.user.id,
          platform: platform.toUpperCase(),
        },
      },
      update: {
        accessToken: tokenData.access_token,
        refreshToken: tokenData.refresh_token || null,
        expiresAt: tokenData.expires_in
          ? new Date(Date.now() + tokenData.expires_in * 1000)
          : null,
      },
      create: {
        userId: session.user.id,
        platform: platform.toUpperCase(),
        accessToken: tokenData.access_token,
        refreshToken: tokenData.refresh_token || null,
        expiresAt: tokenData.expires_in
          ? new Date(Date.now() + tokenData.expires_in * 1000)
          : null,
      },
    })
    */
    
    // Clear the state cookie
    const response = NextResponse.redirect(
      new URL('/platforms?success=true&platform=' + platform, request.url)
    )
    
    response.cookies.set('platform_oauth_state', '', {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 0,
      path: '/',
    })
    
    return response
  } catch (error) {
    console.error('Token exchange error:', error)
    
    return NextResponse.redirect(
      new URL(`/platforms?error=token_exchange&platform=${platform}`, request.url)
    )
  }
}
