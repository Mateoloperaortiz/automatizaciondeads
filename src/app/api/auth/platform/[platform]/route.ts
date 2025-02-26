import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth/next'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

// Platform-specific configuration
const platformConfig = {
  meta: {
    authUrl: 'https://www.facebook.com/v17.0/dialog/oauth',
    tokenUrl: 'https://graph.facebook.com/v17.0/oauth/access_token',
    scopes: ['ads_management', 'ads_read', 'business_management'],
    clientId: process.env.META_CLIENT_ID,
    clientSecret: process.env.META_CLIENT_SECRET,
  },
  google: {
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    tokenUrl: 'https://oauth2.googleapis.com/token',
    scopes: ['https://www.googleapis.com/auth/adwords'],
    clientId: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  },
  twitter: {
    authUrl: 'https://twitter.com/i/oauth2/authorize',
    tokenUrl: 'https://api.twitter.com/2/oauth2/token',
    scopes: ['tweet.read', 'users.read', 'offline.access'],
    clientId: process.env.TWITTER_CLIENT_ID,
    clientSecret: process.env.TWITTER_CLIENT_SECRET,
  },
  tiktok: {
    authUrl: 'https://www.tiktok.com/v2/auth/authorize/',
    tokenUrl: 'https://open-api.tiktok.com/oauth/access_token/',
    scopes: ['user.info.basic', 'video.list', 'video.upload'],
    clientId: process.env.TIKTOK_CLIENT_ID,
    clientSecret: process.env.TIKTOK_CLIENT_SECRET,
  },
  snapchat: {
    authUrl: 'https://accounts.snapchat.com/login/oauth2/authorize',
    tokenUrl: 'https://accounts.snapchat.com/login/oauth2/access_token',
    scopes: ['snapchat-marketing-api'],
    clientId: process.env.SNAPCHAT_CLIENT_ID,
    clientSecret: process.env.SNAPCHAT_CLIENT_SECRET,
  },
}

export async function GET(request: NextRequest, { params }: { params: { platform: string } }) {
  const session = await getServerSession()
  
  if (!session) {
    return NextResponse.redirect(new URL('/auth/login', request.url))
  }
  
  const { platform } = params
  const config = platformConfig[platform as keyof typeof platformConfig]
  
  if (!config) {
    return NextResponse.json({ error: 'Platform not supported' }, { status: 400 })
  }
  
  // Generate a state parameter to prevent CSRF
  const state = Math.random().toString(36).substring(2, 15)
  
  // In a real application, you'd store this state in a database or session
  // For the POC, we'll use a cookie
  const redirectUrl = new URL('/api/auth/platform/callback', request.url)
  redirectUrl.searchParams.append('platform', platform)
  
  const authUrl = new URL(config.authUrl)
  authUrl.searchParams.append('client_id', config.clientId || '')
  authUrl.searchParams.append('redirect_uri', redirectUrl.toString())
  authUrl.searchParams.append('scope', config.scopes.join(' '))
  authUrl.searchParams.append('response_type', 'code')
  authUrl.searchParams.append('state', state)
  
  const response = NextResponse.redirect(authUrl)
  
  // Set a cookie with the state parameter
  response.cookies.set('platform_oauth_state', state, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    maxAge: 60 * 10, // 10 minutes
    path: '/',
  })
  
  return response
}
