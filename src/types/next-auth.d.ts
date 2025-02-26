import NextAuth, { DefaultSession } from 'next-auth'
import { JWT } from 'next-auth/jwt'

declare module 'next-auth' {
  /**
   * Extending the built-in session types
   */
  interface Session {
    user: {
      /** The user's id. */
      id: string
      /** The user's role. */
      role: string
    } & DefaultSession['user']
  }

  /**
   * Extending the built-in user types
   */
  interface User {
    /** The user's id. */
    id: string
    /** The user's role. */
    role: string
  }
}

declare module 'next-auth/jwt' {
  /** Extending the built-in JWT types */
  interface JWT {
    /** The user's id. */
    id: string
    /** The user's role. */
    role: string
  }
}
