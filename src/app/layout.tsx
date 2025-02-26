import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { getServerSession } from 'next-auth'
import SessionProvider from '@/components/SessionProvider'
import Navbar from '@/components/Navbar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Magneto Ads Booster - Magneto Ads Automation',
  description: 'Automate your job vacancy ads across multiple social media platforms',
}

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const session = await getServerSession()
  
  return (
    <html lang="en">
      <body className={inter.className}>
        <SessionProvider session={session}>
          <div className="min-h-screen flex flex-col">
            <Navbar />
            <main className="flex-grow container mx-auto px-4 py-8">
              {children}
            </main>
            <footer className="bg-gray-100 py-6">
              <div className="container mx-auto px-4 text-center text-gray-500 text-sm">
                &copy; {new Date().getFullYear()} Magneto Ads Booster. All rights reserved.
              </div>
            </footer>
          </div>
        </SessionProvider>
      </body>
    </html>
  )
}
