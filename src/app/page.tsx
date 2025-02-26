import { getServerSession } from 'next-auth'
import Link from 'next/link'
import { redirect } from 'next/navigation'

export default async function Home() {
  const session = await getServerSession()
  
  // If user is logged in, redirect to dashboard
  if (session) {
    redirect('/dashboard')
  }
  
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] text-center">
      <h1 className="text-4xl font-bold mb-6">Welcome to Magneto Ads Booster</h1>
      <p className="text-xl text-gray-600 max-w-2xl mb-8">
        Automate your job vacancy ads across multiple social media platforms.
        Connect your accounts, import vacancies, and let Magneto Ads Booster handle the rest.
      </p>
      <div className="flex gap-4">
        <Link href="/auth/login" className="btn-primary">
          Log In
        </Link>
        <Link href="/auth/register" className="btn-outline">
          Register
        </Link>
      </div>
      
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-4xl">
        <div className="card">
          <h2 className="text-xl font-semibold mb-3">Platform Connections</h2>
          <p className="text-gray-600">
            Connect to Meta, Google, X, TikTok, and Snapchat with secure OAuth integration.
          </p>
        </div>
        <div className="card">
          <h2 className="text-xl font-semibold mb-3">ATS Integration</h2>
          <p className="text-gray-600">
            Import vacancies directly from your ATS system with just a few clicks.
          </p>
        </div>
        <div className="card">
          <h2 className="text-xl font-semibold mb-3">User Management</h2>
          <p className="text-gray-600">
            Create and manage user accounts with different roles and permissions.
          </p>
        </div>
      </div>
    </div>
  )
}
