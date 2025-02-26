'use client'

import React, { useState } from 'react';
import { Campaign } from '@prisma/client';

interface CreativeUploaderProps {
  campaignId: string;
  onUploadComplete?: (creative: any) => void;
}

export default function CreativeUploader({ campaignId, onUploadComplete }: CreativeUploaderProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [name, setName] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      // Check if it's an image
      if (!selectedFile.type.startsWith('image/')) {
        setError('Please select an image file');
        return;
      }
      
      setFile(selectedFile);
      setError(null);
      
      // Create a preview URL
      const url = URL.createObjectURL(selectedFile);
      setPreviewUrl(url);
      
      // Set default name from file name if not already set
      if (!name) {
        setName(selectedFile.name.split('.')[0]);
      }
    }
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file to upload');
      return;
    }
    
    setIsUploading(true);
    
    try {
      // In a real implementation, we would upload the file to a storage service
      // For POC, we'll mock the upload and use the preview URL
      
      // Mock some metadata about the image
      const dimensions = await getImageDimensions(file);
      
      const creativeData = {
        name,
        originalUrl: previewUrl,
        mimeType: file.type,
        width: dimensions.width,
        height: dimensions.height,
        fileSize: Math.round(file.size / 1024), // Convert to KB
        campaignId,
      };
      
      // Call the API to create the creative record
      const response = await fetch('/api/creatives', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(creativeData),
      });
      
      if (!response.ok) {
        throw new Error('Failed to create creative');
      }
      
      const creative = await response.json();
      
      // Reset the form
      setName('');
      setFile(null);
      setPreviewUrl(null);
      
      // Notify parent component
      if (onUploadComplete) {
        onUploadComplete(creative);
      }
    } catch (error) {
      console.error('Error uploading creative:', error);
      setError('Failed to upload creative');
    } finally {
      setIsUploading(false);
    }
  };

  // Helper function to get image dimensions
  const getImageDimensions = (file: File): Promise<{ width: number; height: number }> => {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        resolve({ width: img.width, height: img.height });
        URL.revokeObjectURL(img.src);
      };
      img.src = URL.createObjectURL(file);
    });
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Upload Creative</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Creative Name
          </label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            required
          />
        </div>
        
        <div className="mb-4">
          <label htmlFor="file" className="block text-sm font-medium text-gray-700 mb-1">
            Creative File
          </label>
          <input
            type="file"
            id="file"
            accept="image/*"
            onChange={handleFileChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            required
          />
        </div>
        
        {previewUrl && (
          <div className="mb-4">
            <p className="text-sm font-medium text-gray-700 mb-1">Preview</p>
            <div className="border border-gray-300 rounded-md p-2">
              <img
                src={previewUrl}
                alt="Preview"
                className="max-h-40 mx-auto"
              />
            </div>
          </div>
        )}
        
        {error && (
          <div className="mb-4 text-red-500 text-sm">{error}</div>
        )}
        
        <button
          type="submit"
          disabled={isUploading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-300"
        >
          {isUploading ? 'Uploading...' : 'Upload Creative'}
        </button>
      </form>
    </div>
  );
}
