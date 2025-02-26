import React from 'react';
import { getServerSession } from 'next-auth/next';
import { redirect } from 'next/navigation';
import Link from 'next/link';
import { PrismaClient, UserRole } from '@prisma/client';

const prisma = new PrismaClient();

// Mock users data for the POC
const mockUsers = [
  {
    id: '1',
    name: 'Admin User',
    email: 'admin@example.com',
    role: 'ADMIN',
    createdAt: new Date('2025-01-15'),
  },
  {
    id: '2',
    name: 'Demo User',
    email: 'user@example.com',
    role: 'CREATOR',
    createdAt: new Date('2025-02-01'),
  },
  {
    id: '3',
    name: 'Marketing Manager',
    email: 'manager@example.com',
    role: 'MANAGER',
    createdAt: new Date('2025-02-10'),
  },
  {
    id: '4',
    name: 'Content Creator',
    email: 'creator@example.com',
    role: 'CREATOR',
    createdAt: new Date('2025-02-15'),
  },
  {
    id: '5',
    name: 'HR Specialist',
    email: 'hr@example.com',
    role: 'CREATOR',
    createdAt: new Date('2025-02-20'),
  },
];

export default async function AdminPage() {
  const session = await getServerSession();
  
  if (!session) {
    redirect('/auth/login');
  }
  
  // Check if user is admin (in a real app, this would verify the role from the session)
  // For the POC, we'll allow access if the email is our hardcoded admin
  if (session.user?.email !== 'admin@example.com') {
    // Not an admin, redirect to dashboard
    redirect('/dashboard');
  }

  let users = [];
  
  try {
    // In a real app, we would fetch users from the database
    // users = await prisma.user.findMany({
    //   orderBy: { createdAt: 'desc' },
    // });
    
    // For the POC, use mock data
    users = mockUsers;
  } catch (error) {
    console.error('Error fetching users:', error);
    // Fall back to mock data
    users = mockUsers;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Admin Dashboard</h1>
        <Link
          href="/admin/users/new"
          className="btn-primary"
        >
          Add New User
        </Link>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">User Management</h2>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td className="px-4 py-3 whitespace-nowrap">{user.name}</td>
                      <td className="px-4 py-3 whitespace-nowrap">{user.email}</td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          user.role === 'ADMIN'
                            ? 'bg-purple-100 text-purple-800'
                            : user.role === 'MANAGER'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        {new Date(user.createdAt).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-center">
                        <div className="flex justify-center space-x-2">
                          <Link
                            href={`/admin/users/${user.id}/edit`}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            Edit
                          </Link>
                          {user.id !== '1' && (
                            <Link
                              href={`/admin/users/${user.id}/delete`}
                              className="text-red-600 hover:text-red-800"
                            >
                              Delete
                            </Link>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Admin Tools</h2>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/admin/settings"
                  className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded"
                >
                  System Settings
                </Link>
              </li>
              <li>
                <Link
                  href="/admin/platforms"
                  className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded"
                >
                  Platform Configuration
                </Link>
              </li>
              <li>
                <Link
                  href="/admin/ats"
                  className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded"
                >
                  ATS Integration
                </Link>
              </li>
              <li>
                <Link
                  href="/admin/logs"
                  className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded"
                >
                  System Logs
                </Link>
              </li>
            </ul>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">System Status</h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Users</span>
                  <span className="font-medium">{users.length}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '60%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Platform Connections</span>
                  <span className="font-medium">2/5</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                  <div className="bg-green-600 h-2 rounded-full" style={{ width: '40%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Active Campaigns</span>
                  <span className="font-medium">3</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                  <div className="bg-purple-600 h-2 rounded-full" style={{ width: '30%' }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
