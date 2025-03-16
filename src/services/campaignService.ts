
import { campaignDatabase, simulateNetworkDelay } from './mockDatabase';

// Campaign data types
export interface CampaignMetrics {
  views: number;
  clicks: number;
  applications: number;
}

export interface Campaign {
  id: string;
  title: string;
  platform: string;
  date: string;
  status: string;
  metrics: CampaignMetrics;
}

export interface CampaignsResponse {
  active: Campaign[];
  all: Campaign[];
}

// Campaign data service
export const fetchCampaigns = async (): Promise<CampaignsResponse> => {
  // Simulating network delay
  await simulateNetworkDelay(800);
  
  return {
    active: [
      {
        id: "camp-001",
        title: "Senior Frontend Developer",
        platform: "Meta, LinkedIn, Google",
        date: "Started 3 days ago",
        status: "active",
        metrics: {
          views: 1240,
          clicks: 85,
          applications: 12
        }
      },
      {
        id: "camp-002",
        title: "UX/UI Designer",
        platform: "LinkedIn, Twitter",
        date: "Started 5 days ago",
        status: "active",
        metrics: {
          views: 892,
          clicks: 56,
          applications: 8
        }
      },
      {
        id: "camp-003",
        title: "Product Manager",
        platform: "Meta, LinkedIn",
        date: "Started 1 week ago",
        status: "active",
        metrics: {
          views: 2105,
          clicks: 143,
          applications: 24
        }
      }
    ],
    all: [
      {
        id: "camp-001",
        title: "Senior Frontend Developer",
        platform: "Meta, LinkedIn, Google",
        date: "Started 3 days ago",
        status: "active",
        metrics: {
          views: 1240,
          clicks: 85,
          applications: 12
        }
      },
      {
        id: "camp-002",
        title: "UX/UI Designer",
        platform: "LinkedIn, Twitter",
        date: "Started 5 days ago",
        status: "active",
        metrics: {
          views: 892,
          clicks: 56,
          applications: 8
        }
      },
      {
        id: "camp-003",
        title: "Product Manager",
        platform: "Meta, LinkedIn",
        date: "Started 1 week ago",
        status: "active",
        metrics: {
          views: 2105,
          clicks: 143,
          applications: 24
        }
      },
      {
        id: "camp-004",
        title: "Full Stack Developer",
        platform: "Meta, LinkedIn, Google",
        date: "Ended 2 weeks ago",
        status: "ended",
        metrics: {
          views: 3450,
          clicks: 210,
          applications: 35
        }
      },
      {
        id: "camp-005",
        title: "Data Scientist",
        platform: "LinkedIn, Google",
        date: "Scheduled for tomorrow",
        status: "scheduled",
        metrics: {
          views: 0,
          clicks: 0,
          applications: 0
        }
      },
      {
        id: "camp-006",
        title: "DevOps Engineer",
        platform: "Meta, LinkedIn",
        date: "Draft created 2 days ago",
        status: "draft",
        metrics: {
          views: 0,
          clicks: 0,
          applications: 0
        }
      }
    ]
  };
};

// Campaign details service
export const fetchCampaignDetails = async (id: string) => {
  // Simulate API call delay
  await simulateNetworkDelay(1000);
  
  // Return the campaign from our database if it exists
  return campaignDatabase[id] || null;
};

// Update campaign
export const updateCampaign = async (id: string, updatedData: any) => {
  // Log the update information
  console.log(`Updating campaign ${id} with:`, updatedData);
  
  // Simulate network delay
  await simulateNetworkDelay(800);
  
  // Update our mock database
  if (campaignDatabase[id]) {
    // Handle jobDetails update
    if (updatedData.jobDetails) {
      campaignDatabase[id] = {
        ...campaignDatabase[id],
        // Update the title in the campaign with the title from jobDetails
        title: updatedData.jobDetails.title || campaignDatabase[id].title,
        jobDetails: {
          ...campaignDatabase[id].jobDetails,
          ...updatedData.jobDetails
        }
      };
    }
    
    // Handle platforms update
    if (updatedData.platforms) {
      campaignDatabase[id] = {
        ...campaignDatabase[id],
        platforms: updatedData.platforms,
        platform: updatedData.platforms
          .map((p: string) => p.charAt(0).toUpperCase() + p.slice(1))
          .join(', ')
      };
    }
    
    // Handle audience update
    if (updatedData.audience) {
      campaignDatabase[id] = {
        ...campaignDatabase[id],
        audience: {
          ...campaignDatabase[id].audience,
          ...updatedData.audience
        }
      };
    }
    
    console.log('Campaign updated:', id, campaignDatabase[id]);
  } else {
    // For creating new campaigns (this is a simplified version)
    const newId = `camp-${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`;
    
    // Create new campaign in database
    campaignDatabase[newId] = {
      id: newId,
      title: updatedData.jobDetails?.title || "New Campaign",
      status: "draft",
      platform: updatedData.platforms 
        ? updatedData.platforms
            .map((p: string) => p.charAt(0).toUpperCase() + p.slice(1))
            .join(', ')
        : "",
      createdDate: new Date().toLocaleDateString("en-US", { month: 'short', day: 'numeric', year: 'numeric' }),
      jobDetails: updatedData.jobDetails || {},
      platforms: updatedData.platforms || [],
      audience: updatedData.audience || {}
    };
    
    console.log('New campaign created:', newId, campaignDatabase[newId]);
    id = newId;  // Update the id to return the new one
  }
  
  // Return success response with the ID of the updated/created campaign
  return { success: true, id, ...updatedData };
};
