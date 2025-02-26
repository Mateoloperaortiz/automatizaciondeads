'use client';

import React, { useState } from 'react';
import Link from 'next/link';

// Mock default settings for the POC
const defaultSettings = {
  systemName: 'Magneto Ads Booster',
  companyName: 'Your Company',
  defaultLanguage: 'en',
  timeZone: 'America/New_York',
  dateFormat: 'MM/DD/YYYY',
  logoUrl: 'https://placehold.co/200x60?text=Your+Logo',
  primaryColor: '#4f46e5',
  accentColor: '#8b5cf6',
  maxFileUploadSize: 10,
  enableApiAccess: true,
  enableNotifications: true,
  maintenanceMode: false,
};

export default function SystemSettingsPage() {
  const [settings, setSettings] = useState(defaultSettings);
  const [isSaving, setIsSaving] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target as HTMLInputElement;
    
    setSettings({
      ...settings,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    
    // Simulate API call
    setTimeout(() => {
      console.log('Saving settings:', settings);
      setIsSaving(false);
      setShowSuccess(true);
      
      setTimeout(() => {
        setShowSuccess(false);
      }, 3000);
    }, 1000);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">System Settings</h1>
          <Link
            href="/admin"
            className="text-gray-600 hover:text-gray-900"
          >
            ← Back to Admin
          </Link>
        </div>
        
        {showSuccess && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 mb-6 rounded relative">
            <span className="block sm:inline">Settings saved successfully!</span>
          </div>
        )}
        
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold">General Settings</h2>
            <p className="text-gray-500 text-sm">Basic configuration options for your Magneto Ads Booster instance.</p>
          </div>
          
          <form onSubmit={handleSubmit} className="p-6 space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="systemName" className="block text-sm font-medium text-gray-700 mb-1">
                  System Name
                </label>
                <input
                  type="text"
                  id="systemName"
                  name="systemName"
                  value={settings.systemName}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md"
                />
              </div>
              
              <div>
                <label htmlFor="companyName" className="block text-sm font-medium text-gray-700 mb-1">
                  Company Name
                </label>
                <input
                  type="text"
                  id="companyName"
                  name="companyName"
                  value={settings.companyName}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md"
                />
              </div>
              
              <div>
                <label htmlFor="defaultLanguage" className="block text-sm font-medium text-gray-700 mb-1">
                  Default Language
                </label>
                <select
                  id="defaultLanguage"
                  name="defaultLanguage"
                  value={settings.defaultLanguage}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="timeZone" className="block text-sm font-medium text-gray-700 mb-1">
                  Time Zone
                </label>
                <select
                  id="timeZone"
                  name="timeZone"
                  value={settings.timeZone}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md"
                >
                  <option value="America/New_York">Eastern Time (ET)</option>
                  <option value="America/Chicago">Central Time (CT)</option>
                  <option value="America/Denver">Mountain Time (MT)</option>
                  <option value="America/Los_Angeles">Pacific Time (PT)</option>
                  <option value="Europe/London">London (GMT)</option>
                  <option value="Europe/Paris">Paris (CET)</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="dateFormat" className="block text-sm font-medium text-gray-700 mb-1">
                  Date Format
                </label>
                <select
                  id="dateFormat"
                  name="dateFormat"
                  value={settings.dateFormat}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md"
                >
                  <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                  <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                  <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="maxFileUploadSize" className="block text-sm font-medium text-gray-700 mb-1">
                  Max File Upload Size (MB)
                </label>
                <input
                  type="number"
                  id="maxFileUploadSize"
                  name="maxFileUploadSize"
                  value={settings.maxFileUploadSize}
                  onChange={handleChange}
                  min="1"
                  max="50"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md"
                />
              </div>
            </div>
            
            <hr className="my-6" />
            
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Branding</h3>
              
              <div>
                <label htmlFor="logoUrl" className="block text-sm font-medium text-gray-700 mb-1">
                  Logo URL
                </label>
                <input
                  type="text"
                  id="logoUrl"
                  name="logoUrl"
                  value={settings.logoUrl}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md"
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="primaryColor" className="block text-sm font-medium text-gray-700 mb-1">
                    Primary Color
                  </label>
                  <div className="flex">
                    <input
                      type="color"
                      id="primaryColor"
                      name="primaryColor"
                      value={settings.primaryColor}
                      onChange={handleChange}
                      className="h-10 w-10 border border-gray-300 rounded-md mr-2"
                    />
                    <input
                      type="text"
                      value={settings.primaryColor}
                      onChange={handleChange}
                      name="primaryColor"
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-md"
                    />
                  </div>
                </div>
                
                <div>
                  <label htmlFor="accentColor" className="block text-sm font-medium text-gray-700 mb-1">
                    Accent Color
                  </label>
                  <div className="flex">
                    <input
                      type="color"
                      id="accentColor"
                      name="accentColor"
                      value={settings.accentColor}
                      onChange={handleChange}
                      className="h-10 w-10 border border-gray-300 rounded-md mr-2"
                    />
                    <input
                      type="text"
                      value={settings.accentColor}
                      onChange={handleChange}
                      name="accentColor"
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-md"
                    />
                  </div>
                </div>
              </div>
            </div>
            
            <hr className="my-6" />
            
            <div className="space-y-4">
              <h3 className="text-lg font-medium">System Options</h3>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="enableApiAccess"
                  name="enableApiAccess"
                  checked={settings.enableApiAccess}
                  onChange={handleChange}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <label htmlFor="enableApiAccess" className="ml-2 block text-sm text-gray-700">
                  Enable API Access
                </label>
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="enableNotifications"
                  name="enableNotifications"
                  checked={settings.enableNotifications}
                  onChange={handleChange}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <label htmlFor="enableNotifications" className="ml-2 block text-sm text-gray-700">
                  Enable Email Notifications
                </label>
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="maintenanceMode"
                  name="maintenanceMode"
                  checked={settings.maintenanceMode}
                  onChange={handleChange}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <label htmlFor="maintenanceMode" className="ml-2 block text-sm text-gray-700">
                  Enable Maintenance Mode
                </label>
              </div>
            </div>
            
            <div className="pt-6 border-t border-gray-200">
              <button
                type="submit"
                disabled={isSaving}
                className={`bg-indigo-600 text-white py-2 px-6 rounded-md hover:bg-indigo-700 transition ${
                  isSaving ? 'opacity-70 cursor-not-allowed' : ''
                }`}
              >
                {isSaving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
