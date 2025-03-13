'use client';

import React, { useState, useEffect } from 'react';
import { AudienceSegmentationService } from '@/lib/audience-segmentation/segmentation-service';
import { SegmentationVisualizer } from '@/components/audience-segmentation/SegmentationVisualizer';
import { AudienceSegment, SegmentationOptions, UserProfile } from '@/lib/audience-segmentation/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';

// Servicio de segmentación
const segmentationService = new AudienceSegmentationService();

// Datos de ejemplo para pruebas
const mockUsers: UserProfile[] = Array.from({ length: 100 }, (_, i) => ({
  id: `user-${i}`,
  demographics: {
    age: 20 + Math.floor(Math.random() * 40),
    gender: ['male', 'female', 'other'][Math.floor(Math.random() * 3)] as 'male' | 'female' | 'other',
    location: ['Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Bilbao'][Math.floor(Math.random() * 5)],
    income: 20000 + Math.floor(Math.random() * 80000),
    educationLevel: ['high_school', 'bachelors', 'masters', 'phd'][Math.floor(Math.random() * 4)],
    jobTitle: ['student', 'professional', 'unemployed', 'retired'][Math.floor(Math.random() * 4)],
  },
  behavior: {
    interests: Array.from(
      { length: 1 + Math.floor(Math.random() * 4) },
      () => ['technology', 'sports', 'music', 'travel', 'food', 'fashion', 'health', 'education'][Math.floor(Math.random() * 8)]
    ),
    recentSearches: Array.from(
      { length: Math.floor(Math.random() * 3) },
      () => ['jobs', 'vacancies', 'career', 'position', 'work'][Math.floor(Math.random() * 5)]
    ),
    clickedCategories: Array.from(
      { length: Math.floor(Math.random() * 3) },
      () => ['tech', 'finance', 'healthcare', 'education', 'retail'][Math.floor(Math.random() * 5)]
    ),
    purchaseHistory: Array.from(
      { length: Math.floor(Math.random() * 3) },
      () => `product-${Math.floor(Math.random() * 20)}`
    ),
    timeSpentOnCategories: {
      tech: Math.random() * 100,
      finance: Math.random() * 100,
      healthcare: Math.random() * 100
    }
  },
  engagement: {
    clickRate: Math.random(),
    conversionRate: Math.random() * 0.2,
    timeOnSite: Math.floor(Math.random() * 3600),
    pageViewsPerSession: Math.floor(Math.random() * 10),
    returnRate: Math.random(),
    socialInteractions: Math.floor(Math.random() * 100)
  }
}));

export default function SegmentationPage() {
  const [algorithm, setAlgorithm] = useState<'kmeans' | 'hierarchical' | 'dbscan'>('kmeans');
  const [segments, setSegments] = useState<AudienceSegment[]>([]);
  const [options, setOptions] = useState<SegmentationOptions>({
    method: 'kmeans',
    numberOfClusters: 3,
    features: ['age', 'income', 'interests', 'socialInteractions'],
    epsilon: 0.5,
    minPoints: 3,
  });
  const [isLoading, setIsLoading] = useState(false);

  // Ejecutar segmentación
  const runSegmentation = async () => {
    setIsLoading(true);
    try {
      // Actualizar opciones según el algoritmo seleccionado
      const updatedOptions: SegmentationOptions = {
        ...options,
        method: algorithm,
      };
      
      // Ejecutar segmentación
      const result = segmentationService.segmentAudience(mockUsers, updatedOptions);
      setSegments(result.segments);
    } catch (error) {
      console.error('Error al realizar la segmentación:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Actualizar opciones cuando cambia el algoritmo
  useEffect(() => {
    setOptions(prev => ({
      ...prev,
      method: algorithm,
    }));
  }, [algorithm]);

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">Audience Segmentation</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle>Algorithm Selection</CardTitle>
            <CardDescription>Choose the segmentation algorithm</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="algorithm">Algorithm</Label>
                <Select
                  value={algorithm}
                  onValueChange={(value: string) => setAlgorithm(value as 'kmeans' | 'hierarchical' | 'dbscan')}
                >
                  <SelectTrigger id="algorithm">
                    <SelectValue placeholder="Select algorithm" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="kmeans">K-Means</SelectItem>
                    <SelectItem value="hierarchical">Hierarchical Clustering</SelectItem>
                    <SelectItem value="dbscan">DBSCAN</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              {algorithm === 'kmeans' || algorithm === 'hierarchical' ? (
                <div className="space-y-2">
                  <Label htmlFor="clusters">Number of Clusters: {options.numberOfClusters}</Label>
                  <Slider
                    id="clusters"
                    min={2}
                    max={10}
                    step={1}
                    value={[options.numberOfClusters || 3]}
                    onValueChange={(value: number[]) => setOptions({ ...options, numberOfClusters: value[0] })}
                  />
                </div>
              ) : (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="epsilon">Epsilon (Distance): {options.epsilon}</Label>
                    <Slider
                      id="epsilon"
                      min={0.1}
                      max={2}
                      step={0.1}
                      value={[options.epsilon || 0.5]}
                      onValueChange={(value: number[]) => setOptions({ ...options, epsilon: value[0] })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="minPoints">Minimum Points: {options.minPoints}</Label>
                    <Slider
                      id="minPoints"
                      min={2}
                      max={10}
                      step={1}
                      value={[options.minPoints || 3]}
                      onValueChange={(value: number[]) => setOptions({ ...options, minPoints: value[0] })}
                    />
                  </div>
                </>
              )}
              
              <Button 
                onClick={runSegmentation} 
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? 'Processing...' : 'Run Segmentation'}
              </Button>
            </div>
          </CardContent>
        </Card>
        
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Features Selection</CardTitle>
            <CardDescription>Select the features to use for segmentation</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="feature-demographics">Demographics</Label>
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="age"
                      checked={options.features?.includes('age')}
                      onChange={(e) => {
                        const features = options.features || [];
                        if (e.target.checked) {
                          setOptions({ ...options, features: [...features, 'age'] });
                        } else {
                          setOptions({ ...options, features: features.filter(f => f !== 'age') });
                        }
                      }}
                    />
                    <Label htmlFor="age">Age</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="income"
                      checked={options.features?.includes('income')}
                      onChange={(e) => {
                        const features = options.features || [];
                        if (e.target.checked) {
                          setOptions({ ...options, features: [...features, 'income'] });
                        } else {
                          setOptions({ ...options, features: features.filter(f => f !== 'income') });
                        }
                      }}
                    />
                    <Label htmlFor="income">Income</Label>
                  </div>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="feature-behavior">Behavior</Label>
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="interests"
                      checked={options.features?.includes('interests')}
                      onChange={(e) => {
                        const features = options.features || [];
                        if (e.target.checked) {
                          setOptions({ ...options, features: [...features, 'interests'] });
                        } else {
                          setOptions({ ...options, features: features.filter(f => f !== 'interests') });
                        }
                      }}
                    />
                    <Label htmlFor="interests">Interests</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="clickRate"
                      checked={options.features?.includes('clickRate')}
                      onChange={(e) => {
                        const features = options.features || [];
                        if (e.target.checked) {
                          setOptions({ ...options, features: [...features, 'clickRate'] });
                        } else {
                          setOptions({ ...options, features: features.filter(f => f !== 'clickRate') });
                        }
                      }}
                    />
                    <Label htmlFor="clickRate">Click Rate</Label>
                  </div>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="feature-engagement">Engagement</Label>
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="socialInteractions"
                      checked={options.features?.includes('socialInteractions')}
                      onChange={(e) => {
                        const features = options.features || [];
                        if (e.target.checked) {
                          setOptions({ ...options, features: [...features, 'socialInteractions'] });
                        } else {
                          setOptions({ ...options, features: features.filter(f => f !== 'socialInteractions') });
                        }
                      }}
                    />
                    <Label htmlFor="socialInteractions">Social Interactions</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="conversionRate"
                      checked={options.features?.includes('conversionRate')}
                      onChange={(e) => {
                        const features = options.features || [];
                        if (e.target.checked) {
                          setOptions({ ...options, features: [...features, 'conversionRate'] });
                        } else {
                          setOptions({ ...options, features: features.filter(f => f !== 'conversionRate') });
                        }
                      }}
                    />
                    <Label htmlFor="conversionRate">Conversion Rate</Label>
                  </div>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="feature-other">Other</Label>
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="location"
                      checked={options.features?.includes('location')}
                      onChange={(e) => {
                        const features = options.features || [];
                        if (e.target.checked) {
                          setOptions({ ...options, features: [...features, 'location'] });
                        } else {
                          setOptions({ ...options, features: features.filter(f => f !== 'location') });
                        }
                      }}
                    />
                    <Label htmlFor="location">Location</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="gender"
                      checked={options.features?.includes('gender')}
                      onChange={(e) => {
                        const features = options.features || [];
                        if (e.target.checked) {
                          setOptions({ ...options, features: [...features, 'gender'] });
                        } else {
                          setOptions({ ...options, features: features.filter(f => f !== 'gender') });
                        }
                      }}
                    />
                    <Label htmlFor="gender">Gender</Label>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {segments.length > 0 ? (
        <div className="space-y-8">
          <Card>
            <CardHeader>
              <CardTitle>Segmentation Results</CardTitle>
              <CardDescription>
                {algorithm === 'kmeans' && 'K-Means clustering results'}
                {algorithm === 'hierarchical' && 'Hierarchical clustering results'}
                {algorithm === 'dbscan' && 'DBSCAN clustering results'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <SegmentationVisualizer 
                segments={segments} 
                title={`${algorithm.toUpperCase()} Segmentation Results`}
                width={800}
                height={500}
              />
            </CardContent>
          </Card>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {segments.map((segment) => (
              <Card key={segment.id}>
                <CardHeader>
                  <CardTitle>{segment.name}</CardTitle>
                  <CardDescription>Size: {segment.size} users</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium">Dominant Demographics</h4>
                      <ul className="list-disc list-inside text-sm">
                        {segment.characteristics.dominantDemographics.age && (
                          <li>Age: ~{segment.characteristics.dominantDemographics.age}</li>
                        )}
                        {segment.characteristics.dominantDemographics.gender && (
                          <li>Gender: {segment.characteristics.dominantDemographics.gender}</li>
                        )}
                        {segment.characteristics.dominantDemographics.location && (
                          <li>Location: {segment.characteristics.dominantDemographics.location}</li>
                        )}
                      </ul>
                    </div>
                    
                    <div>
                      <h4 className="font-medium">Interests</h4>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {segment.characteristics.dominantInterests.map((interest) => (
                          <span key={interest} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                            {interest}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="font-medium">Engagement:</span> {segment.characteristics.engagementLevel}
                      </div>
                      <div>
                        <span className="font-medium">Conversion:</span> {segment.characteristics.conversionPotential}
                      </div>
                    </div>
                    
                    {segment.characteristics.bestTimeToTarget && (
                      <div>
                        <h4 className="font-medium">Best Time to Target</h4>
                        <div className="text-sm">
                          <div>Days: {segment.characteristics.bestTimeToTarget.days.join(', ')}</div>
                          <div>Hours: {segment.characteristics.bestTimeToTarget.hours.join(', ')}</div>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      ) : (
        <Card className="bg-gray-50">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <p className="text-gray-500 mb-4">No segmentation results yet</p>
            <p className="text-sm text-gray-400 max-w-md text-center">
              Select an algorithm and features, then click &quot;Run Segmentation&quot; to see the results.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
