import React from 'react';
import { getServerSession } from 'next-auth/next';
import { redirect } from 'next/navigation';

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getServerSession();
  
  if (!session) {
    redirect('/auth/login');
  }
  
  // For the POC, we only allow the hardcoded admin user to access admin pages
  if (session.user?.email !== 'admin@example.com') {
    redirect('/dashboard');
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gradient-to-r from-purple-800 to-indigo-900 text-white py-4 px-6 shadow-md">
        <div className="container mx-auto">
          <h1 className="text-xl font-bold">Magneto Ads Booster Admin</h1>
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
}
