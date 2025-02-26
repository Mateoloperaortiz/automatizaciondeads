import React from 'react'
import { getServerSession } from 'next-auth/next'
import { redirect } from 'next/navigation'
import Link from 'next/link'

export default async function PlatformsPage() {
  const session = await getServerSession()
  
  if (!session) {
    redirect('/auth/login')
  }
  
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Platform Connections</h1>
      </div>
      
      <p className="text-gray-600 mb-8">
        Connect your social media advertising accounts to Magneto Ads Booster to create and manage campaigns.
        Your credentials are securely stored and you can revoke access at any time.
      </p>
      
      <div className="space-y-6">
        {/* Meta (Facebook & Instagram) */}
        <div className="card">
          <div className="flex justify-between items-start">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 text-xl font-bold">f</span>
              </div>
              <div className="ml-4">
                <h2 className="text-xl font-semibold">Meta</h2>
                <p className="text-gray-600">Facebook & Instagram Ads</p>
              </div>
            </div>
            <div className="flex items-center">
              <span className="text-green-600 mr-3">Connected</span>
              <Link href="/platforms/meta/revoke" className="btn-outline text-sm">
                Disconnect
              </Link>
            </div>
          </div>
          
          <div className="mt-4 border-t pt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Connected Accounts</h3>
            <div className="bg-gray-50 rounded-md p-3">
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-medium">Magneto Recruitment</p>
                  <p className="text-sm text-gray-600">Business Account ID: 1234567890</p>
                </div>
                <span className="text-xs text-gray-500">Connected on Feb 25, 2025</span>
              </div>
            </div>
          </div>
          
          <div className="mt-4 border-t pt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Permissions</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>✓ Read and write ads</li>
              <li>✓ Read and write ad accounts</li>
              <li>✓ Read and write campaigns</li>
            </ul>
          </div>
        </div>
        
        {/* Google Ads */}
        <div className="card">
          <div className="flex justify-between items-start">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <span className="text-red-600 text-xl font-bold">G</span>
              </div>
              <div className="ml-4">
                <h2 className="text-xl font-semibold">Google</h2>
                <p className="text-gray-600">Google Ads</p>
              </div>
            </div>
            <div className="flex items-center">
              <span className="text-green-600 mr-3">Connected</span>
              <Link href="/platforms/google/revoke" className="btn-outline text-sm">
                Disconnect
              </Link>
            </div>
          </div>
          
          <div className="mt-4 border-t pt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Connected Accounts</h3>
            <div className="bg-gray-50 rounded-md p-3">
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-medium">Magneto Recruitment</p>
                  <p className="text-sm text-gray-600">Customer ID: 987-654-3210</p>
                </div>
                <span className="text-xs text-gray-500">Connected on Feb 25, 2025</span>
              </div>
            </div>
          </div>
          
          <div className="mt-4 border-t pt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Permissions</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>✓ View and manage your Google Ads campaigns</li>
              <li>✓ View and manage your Google Ads account</li>
            </ul>
          </div>
        </div>
        
        {/* X (Twitter) */}
        <div className="card">
          <div className="flex justify-between items-start">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                <span className="text-black text-xl font-bold">X</span>
              </div>
              <div className="ml-4">
                <h2 className="text-xl font-semibold">X</h2>
                <p className="text-gray-600">Twitter Ads</p>
              </div>
            </div>
            <Link href="/api/auth/platform/twitter" className="btn-primary text-sm">
              Connect
            </Link>
          </div>
          
          <div className="mt-4 border-t pt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Required Permissions</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• View and manage your Twitter Ads campaigns</li>
              <li>• Create and manage Twitter Ads</li>
              <li>• Access your Twitter profile information</li>
            </ul>
          </div>
        </div>
        
        {/* TikTok */}
        <div className="card">
          <div className="flex justify-between items-start">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-black rounded-full flex items-center justify-center">
                <span className="text-white text-xl">TT</span>
              </div>
              <div className="ml-4">
                <h2 className="text-xl font-semibold">TikTok</h2>
                <p className="text-gray-600">TikTok For Business</p>
              </div>
            </div>
            <Link href="/api/auth/platform/tiktok" className="btn-primary text-sm">
              Connect
            </Link>
          </div>
          
          <div className="mt-4 border-t pt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Required Permissions</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Access to your TikTok ad accounts</li>
              <li>• Create and manage ads on TikTok</li>
              <li>• View reports and analytics</li>
            </ul>
          </div>
        </div>
        
        {/* Snapchat */}
        <div className="card">
          <div className="flex justify-between items-start">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
                <span className="text-yellow-600 text-xl">👻</span>
              </div>
              <div className="ml-4">
                <h2 className="text-xl font-semibold">Snapchat</h2>
                <p className="text-gray-600">Snapchat Ads Manager</p>
              </div>
            </div>
            <Link href="/api/auth/platform/snapchat" className="btn-primary text-sm">
              Connect
            </Link>
          </div>
          
          <div className="mt-4 border-t pt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Required Permissions</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Access to your Snapchat ad accounts</li>
              <li>• Create and manage ads on Snapchat</li>
              <li>• View campaign reports</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
