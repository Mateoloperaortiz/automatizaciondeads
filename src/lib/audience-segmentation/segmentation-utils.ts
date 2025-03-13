import { UserProfile } from './types';

/**
 * Utility functions for audience segmentation
 */
export class SegmentationUtils {
  /**
   * Converts user profiles to feature vectors for clustering algorithms
   * @param users List of user profiles
   * @param features List of features to include in the vectors
   * @returns Array of feature vectors and feature names
   */
  static convertUsersToFeatureVectors(
    users: UserProfile[],
    features?: string[]
  ): { vectors: number[][]; featureNames: string[]; userIndices: string[] } {
    // Define default features if not provided
    const defaultFeatures = [
      'demographics.age',
      'demographics.gender',
      'demographics.location',
      'behavior.interests',
      'engagement.clickRate',
      'engagement.conversionRate',
      'engagement.timeOnSite'
    ];

    const featuresToUse = features || defaultFeatures;
    const vectors: number[][] = [];
    const userIndices: string[] = [];
    
    // Process each user
    users.forEach(user => {
      const vector: number[] = [];
      
      // Extract features for each user
      featuresToUse.forEach(feature => {
        const [category, subFeature] = feature.split('.');
        
        if (category === 'demographics') {
          if (subFeature === 'age') {
            vector.push(user.demographics.age || 30); // Default age if not provided
          } else if (subFeature === 'gender') {
            // Convert gender to numeric value
            const genderValue = user.demographics.gender === 'male' ? 0 :
                               user.demographics.gender === 'female' ? 1 : 2;
            vector.push(genderValue);
          } else if (subFeature === 'location') {
            // Use a hash of the location string as a numeric feature
            vector.push(user.demographics.location ? this.hashString(user.demographics.location) % 100 : 0);
          }
        } else if (category === 'behavior') {
          if (subFeature === 'interests') {
            // Use the number of interests as a feature
            vector.push(user.behavior.interests.length);
          }
        } else if (category === 'engagement') {
          if (subFeature === 'clickRate') {
            vector.push(user.engagement.clickRate || 0);
          } else if (subFeature === 'conversionRate') {
            vector.push(user.engagement.conversionRate || 0);
          } else if (subFeature === 'timeOnSite') {
            vector.push(user.engagement.timeOnSite || 0);
          }
        }
      });
      
      vectors.push(vector);
      userIndices.push(user.id);
    });
    
    // Normalize the vectors
    const normalizedVectors = this.normalizeVectors(vectors);
    
    return {
      vectors: normalizedVectors,
      featureNames: featuresToUse,
      userIndices
    };
  }
  
  /**
   * Normalize feature vectors to have values between 0 and 1
   * @param vectors Array of feature vectors
   * @returns Normalized vectors
   */
  static normalizeVectors(vectors: number[][]): number[][] {
    if (vectors.length === 0) return [];
    
    const numFeatures = vectors[0].length;
    const mins: number[] = new Array(numFeatures).fill(Number.MAX_VALUE);
    const maxs: number[] = new Array(numFeatures).fill(Number.MIN_VALUE);
    
    // Find min and max values for each feature
    vectors.forEach(vector => {
      for (let i = 0; i < numFeatures; i++) {
        mins[i] = Math.min(mins[i], vector[i]);
        maxs[i] = Math.max(maxs[i], vector[i]);
      }
    });
    
    // Normalize each vector
    return vectors.map(vector => {
      return vector.map((value, i) => {
        // If max and min are the same, return 0.5 to avoid division by zero
        if (maxs[i] === mins[i]) return 0.5;
        return (value - mins[i]) / (maxs[i] - mins[i]);
      });
    });
  }
  
  /**
   * Simple hash function for strings
   * @param str String to hash
   * @returns Hash value
   */
  static hashString(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
  }
  
  /**
   * Calculate Euclidean distance between two vectors
   * @param a First vector
   * @param b Second vector
   * @returns Distance
   */
  static euclideanDistance(a: number[], b: number[]): number {
    if (a.length !== b.length) {
      throw new Error('Vectors must have the same length');
    }
    
    let sum = 0;
    for (let i = 0; i < a.length; i++) {
      sum += Math.pow(a[i] - b[i], 2);
    }
    
    return Math.sqrt(sum);
  }
  
  /**
   * Generate a visualization configuration for the segmentation results
   * @param vectors Feature vectors
   * @param clusters Cluster assignments
   * @param featureNames Names of the features
   * @returns Plotly configuration object
   */
  static generateVisualizationConfig(
    vectors: number[][],
    clusters: number[],
    featureNames: string[]
  ): Record<string, unknown> {
    // For simplicity, we'll use the first two features for 2D visualization
    // In a real implementation, you might want to use PCA or t-SNE for dimensionality reduction
    
    // Prepare data for each cluster
    const uniqueClusters = Array.from(new Set(clusters));
    const traces = uniqueClusters.map(cluster => {
      const clusterPoints = vectors.filter((_, i) => clusters[i] === cluster);
      
      return {
        x: clusterPoints.map(p => p[0]),
        y: clusterPoints.map(p => p.length > 1 ? p[1] : 0),
        mode: 'markers',
        type: 'scatter',
        name: `Cluster ${cluster}`,
        marker: {
          size: 10
        }
      };
    });
    
    // Configuration for the plot
    return {
      data: traces,
      layout: {
        title: 'Audience Segmentation Visualization',
        xaxis: {
          title: featureNames.length > 0 ? featureNames[0] : 'Feature 1'
        },
        yaxis: {
          title: featureNames.length > 1 ? featureNames[1] : 'Feature 2'
        },
        hovermode: 'closest'
      }
    };
  }
}
