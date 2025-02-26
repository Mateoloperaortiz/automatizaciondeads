'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

const platforms = [
  { id: 'meta', name: 'Meta (Facebook & Instagram)' },
  { id: 'linkedin', name: 'LinkedIn' },
  { id: 'indeed', name: 'Indeed' },
  { id: 'glassdoor', name: 'Glassdoor' },
  { id: 'twitter', name: 'Twitter' },
  { id: 'stackoverflow', name: 'Stack Overflow' },
  { id: 'github', name: 'GitHub Jobs' },
  { id: 'ziprecruiter', name: 'ZipRecruiter' },
];

export default function NewCampaignPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    goal: '',
    description: '',
    targetAudience: '',
    startDate: '',
    endDate: '',
    budget: '',
    selectedPlatforms: [] as string[],
  });
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handlePlatformToggle = (platformId: string) => {
    setFormData((prev) => {
      const isSelected = prev.selectedPlatforms.includes(platformId);
      return {
        ...prev,
        selectedPlatforms: isSelected
          ? prev.selectedPlatforms.filter(id => id !== platformId)
          : [...prev.selectedPlatforms, platformId],
      };
    });
  };

  const nextStep = () => {
    setCurrentStep(currentStep + 1);
  };

  const prevStep = () => {
    setCurrentStep(currentStep - 1);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // In a real app, this would create a campaign in the database
    console.log('Creating new campaign:', formData);
    
    // Simulate API call
    setTimeout(() => {
      // Show success message for the POC
      alert('Campaign created successfully! (This is just a simulation for the POC)');
      
      // Redirect to campaigns page
      router.push('/campaigns');
    }, 1000);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">Create New Campaign</h1>
          <Link
            href="/campaigns"
            className="text-gray-600 hover:text-gray-900"
          >
            ← Back to Campaigns
          </Link>
        </div>
        
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between">
              {[1, 2, 3].map((step) => (
                <div key={step} className="flex items-center">
                  <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
                    currentStep === step
                      ? 'bg-indigo-600 text-white'
                      : currentStep > step
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}>
                    {currentStep > step ? (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      step
                    )}
                  </div>
                  <span className={`ml-2 text-sm ${currentStep === step ? 'font-semibold text-gray-900' : 'text-gray-500'}`}>
                    {step === 1 && 'Campaign Details'}
                    {step === 2 && 'Platform Selection'}
                    {step === 3 && 'Review & Create'}
                  </span>
                  
                  {step < 3 && (
                    <div className="w-10 mx-2 h-0.5 bg-gray-200"></div>
                  )}
                </div>
              ))}
            </div>
          </div>
          
          <form onSubmit={handleSubmit}>
            {currentStep === 1 && (
              <div className="p-6 space-y-6">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                    Campaign Name*
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    required
                    value={formData.name}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md"
                    placeholder="e.g., Summer Hiring Campaign"
                  />
                </div>
                
                <div>
                  <label htmlFor="goal" className="block text-sm font-medium text-gray-700 mb-1">
                    Campaign Goal*
                  </label>
                  <input
                    type="text"
                    id="goal"
                    name="goal"
                    required
                    value={formData.goal}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md"
                    placeholder="e.g., Hire 10 software engineers"
                  />
                </div>
                
                <div>
                  <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    rows={4}
                    value={formData.description}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md"
                    placeholder="Detailed description of the campaign"
                  />
                </div>
                
                <div>
                  <label htmlFor="targetAudience" className="block text-sm font-medium text-gray-700 mb-1">
                    Target Audience
                  </label>
                  <input
                    type="text"
                    id="targetAudience"
                    name="targetAudience"
                    value={formData.targetAudience}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md"
                    placeholder="e.g., Software engineers with 3+ years experience"
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="startDate" className="block text-sm font-medium text-gray-700 mb-1">
                      Start Date*
                    </label>
                    <input
                      type="date"
                      id="startDate"
                      name="startDate"
                      required
                      value={formData.startDate}
                      onChange={handleChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md"
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="endDate" className="block text-sm font-medium text-gray-700 mb-1">
                      End Date*
                    </label>
                    <input
                      type="date"
                      id="endDate"
                      name="endDate"
                      required
                      value={formData.endDate}
                      onChange={handleChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md"
                    />
                  </div>
                </div>
                
                <div>
                  <label htmlFor="budget" className="block text-sm font-medium text-gray-700 mb-1">
                    Budget (USD)*
                  </label>
                  <input
                    type="number"
                    id="budget"
                    name="budget"
                    required
                    value={formData.budget}
                    onChange={handleChange}
                    min="0"
                    step="100"
                    className="w-full px-4 py-2 border border-gray-300 rounded-md"
                    placeholder="e.g., 5000"
                  />
                </div>
              </div>
            )}
            
            {currentStep === 2 && (
              <div className="p-6">
                <h2 className="text-lg font-semibold mb-4">Select Advertising Platforms</h2>
                <p className="text-gray-500 mb-6">Choose the platforms where you want to advertise your vacancies.</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {platforms.map((platform) => (
                    <div 
                      key={platform.id}
                      className={`border rounded-md p-4 cursor-pointer ${
                        formData.selectedPlatforms.includes(platform.id)
                          ? 'border-indigo-500 bg-indigo-50'
                          : 'border-gray-300 hover:bg-gray-50'
                      }`}
                      onClick={() => handlePlatformToggle(platform.id)}
                    >
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          id={`platform-${platform.id}`}
                          checked={formData.selectedPlatforms.includes(platform.id)}
                          onChange={() => {}} // Handled by the div click
                          className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                        />
                        <label htmlFor={`platform-${platform.id}`} className="ml-3 text-gray-700">
                          {platform.name}
                        </label>
                      </div>
                    </div>
                  ))}
                </div>
                
                {formData.selectedPlatforms.length === 0 && (
                  <p className="text-yellow-600 mt-4">
                    Please select at least one platform to continue.
                  </p>
                )}
              </div>
            )}
            
            {currentStep === 3 && (
              <div className="p-6">
                <h2 className="text-lg font-semibold mb-4">Review Campaign Details</h2>
                
                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Campaign Name</p>
                      <p className="font-medium">{formData.name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Budget</p>
                      <p className="font-medium">${formData.budget}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Start Date</p>
                      <p className="font-medium">{formData.startDate}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">End Date</p>
                      <p className="font-medium">{formData.endDate}</p>
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <p className="text-sm text-gray-500">Campaign Goal</p>
                    <p className="font-medium">{formData.goal}</p>
                  </div>
                  
                  {formData.description && (
                    <div className="mt-4">
                      <p className="text-sm text-gray-500">Description</p>
                      <p className="font-medium">{formData.description}</p>
                    </div>
                  )}
                  
                  {formData.targetAudience && (
                    <div className="mt-4">
                      <p className="text-sm text-gray-500">Target Audience</p>
                      <p className="font-medium">{formData.targetAudience}</p>
                    </div>
                  )}
                  
                  <div className="mt-4">
                    <p className="text-sm text-gray-500">Selected Platforms</p>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {formData.selectedPlatforms.map((platformId) => (
                        <span key={platformId} className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded-full text-xs">
                          {platforms.find(p => p.id === platformId)?.name}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                
                <p className="text-gray-500 text-sm mb-6">
                  Please review the information above before creating your campaign. You'll be able to make changes after creation.
                </p>
              </div>
            )}
            
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between">
              {currentStep > 1 ? (
                <button
                  type="button"
                  onClick={prevStep}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Back
                </button>
              ) : (
                <div></div>
              )}
              
              {currentStep < 3 ? (
                <button
                  type="button"
                  onClick={nextStep}
                  disabled={currentStep === 2 && formData.selectedPlatforms.length === 0}
                  className={`px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 ${
                    currentStep === 2 && formData.selectedPlatforms.length === 0
                      ? 'opacity-50 cursor-not-allowed'
                      : ''
                  }`}
                >
                  Continue
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className={`px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 ${
                    isSubmitting ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  {isSubmitting ? 'Creating...' : 'Create Campaign'}
                </button>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
