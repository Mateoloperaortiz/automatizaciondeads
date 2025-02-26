import React from 'react'
import { getServerSession } from 'next-auth/next'
import { redirect } from 'next/navigation'
import Link from 'next/link'

export default async function DashboardPage() {
  const session = await getServerSession()
  
  if (!session) {
    redirect('/auth/login')
  }
  
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <h2 className="text-xl font-semibold mb-3">Platform Connections</h2>
          <p className="text-gray-600 mb-4">
            Connect your social media advertising accounts to start creating campaigns.
          </p>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-500">2 of 5 connected</span>
            <Link href="/platforms" className="btn-primary text-sm">
              Manage
            </Link>
          </div>
          <div className="mt-4 space-y-2">
            <div className="flex items-center justify-between py-2 px-3 bg-green-50 rounded-md">
              <div className="flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                <span>Meta</span>
              </div>
              <span className="text-xs text-green-600">Connected</span>
            </div>
            <div className="flex items-center justify-between py-2 px-3 bg-green-50 rounded-md">
              <div className="flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                <span>Google</span>
              </div>
              <span className="text-xs text-green-600">Connected</span>
            </div>
            <div className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-md">
              <div className="flex items-center">
                <span className="w-2 h-2 bg-gray-300 rounded-full mr-2"></span>
                <span>Twitter</span>
              </div>
              <span className="text-xs text-gray-500">Not connected</span>
            </div>
          </div>
        </div>
        
        <div className="card">
          <h2 className="text-xl font-semibold mb-3">Vacancies</h2>
          <p className="text-gray-600 mb-4">
            Import job vacancies from your ATS system to create ad campaigns.
          </p>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-500">10 vacancies imported</span>
            <Link href="/vacancies" className="btn-primary text-sm">
              View All
            </Link>
          </div>
          <div className="mt-4">
            <Link href="/vacancies/import" className="btn-secondary w-full">
              Import Vacancies
            </Link>
          </div>
        </div>
        
        <div className="card">
          <h2 className="text-xl font-semibold mb-3">Creative Adaptation</h2>
          <p className="text-gray-600 mb-4">
            Automatically adapt your creative assets to match platform requirements.
          </p>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-500">Multi-platform optimization</span>
            <Link href="/creatives" className="btn-primary text-sm">
              Manage
            </Link>
          </div>
          <div className="mt-4 space-y-2">
            <div className="flex justify-between py-2 px-3 bg-blue-50 rounded-md">
              <span>Meta Feed</span>
              <span className="text-xs">1080 × 1080</span>
            </div>
            <div className="flex justify-between py-2 px-3 bg-blue-50 rounded-md">
              <span>Google Display</span>
              <span className="text-xs">336 × 280</span>
            </div>
            <div className="flex justify-between py-2 px-3 bg-blue-50 rounded-md">
              <span>TikTok Feed</span>
              <span className="text-xs">1080 × 1920</span>
            </div>
          </div>
        </div>
        
        <div className="card">
          <h2 className="text-xl font-semibold mb-3">Campaigns</h2>
          <p className="text-gray-600 mb-4">
            Create and manage advertising campaigns for your vacancies.
          </p>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-500">0 active campaigns</span>
            <Link href="/campaigns" className="btn-primary text-sm">
              Manage
            </Link>
          </div>
          <div className="mt-4 flex items-center justify-center h-24 border-2 border-dashed border-gray-300 rounded-md">
            <div className="text-center">
              <p className="text-gray-500">No campaigns yet</p>
              <Link href="/campaigns/create" className="text-primary-600 text-sm font-medium">
                Create your first campaign
              </Link>
            </div>
          </div>
        </div>
      </div>
      
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Quick Start Guide</h2>
        <div className="space-y-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <div className="flex items-center justify-center h-8 w-8 rounded-full bg-primary-100 text-primary-600">
                1
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium">Connect your platforms</h3>
              <p className="text-gray-600">
                Connect your social media advertising accounts to Magneto Ads Booster.
              </p>
              <Link href="/platforms" className="text-primary-600 text-sm font-medium">
                Go to Platform Connections →
              </Link>
            </div>
          </div>
          
          <div className="flex">
            <div className="flex-shrink-0">
              <div className="flex items-center justify-center h-8 w-8 rounded-full bg-primary-100 text-primary-600">
                2
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium">Import vacancies</h3>
              <p className="text-gray-600">
                Import job vacancies from your ATS system.
              </p>
              <Link href="/vacancies/import" className="text-primary-600 text-sm font-medium">
                Import Vacancies →
              </Link>
            </div>
          </div>
          
          <div className="flex">
            <div className="flex-shrink-0">
              <div className="flex items-center justify-center h-8 w-8 rounded-full bg-primary-100 text-primary-600">
                3
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium">Create campaigns</h3>
              <p className="text-gray-600">
                Create advertising campaigns for your vacancies.
              </p>
              <Link href="/campaigns/create" className="text-primary-600 text-sm font-medium">
                Create Campaign →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
