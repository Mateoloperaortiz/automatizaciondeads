import { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import GoogleProvider from 'next-auth/providers/google'
import FacebookProvider from 'next-auth/providers/facebook'
import { PrismaAdapter } from '@next-auth/prisma-adapter'
import { PrismaClient } from '@prisma/client'
import bcrypt from 'bcryptjs'

const prisma = new PrismaClient()

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        // For the POC, we're using these hardcoded credentials
        // username: admin@example.com
        // password: password
        if (credentials.email === 'admin@example.com' && credentials.password === 'password') {
          return {
            id: '1',
            name: 'Admin User',
            email: 'admin@example.com',
            role: 'ADMIN',
          }
        }

        // Demo user account
        if (credentials.email === 'user@example.com' && credentials.password === 'password') {
          return {
            id: '2',
            name: 'Demo User',
            email: 'user@example.com',
            role: 'CREATOR',
          }
        }

        // In a full implementation, we would query the database
        // For now we'll just return null for any other credentials
        console.log('Invalid login attempt for email:', credentials.email)
        return null
      },
    }),
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || 'mock-client-id',
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || 'mock-client-secret',
    }),
    FacebookProvider({
      clientId: process.env.META_CLIENT_ID || 'mock-client-id',
      clientSecret: process.env.META_CLIENT_SECRET || 'mock-client-secret',
    }),
  ],
  session: {
    strategy: 'jwt',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
        token.role = user.role
      }
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string
        session.user.role = token.role as string
      }
      return session
    },
  },
  pages: {
    signIn: '/auth/login',
    signOut: '/',
    error: '/auth/error',
  },
  secret: process.env.NEXTAUTH_SECRET,
}
