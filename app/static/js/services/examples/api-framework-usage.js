/**
 * MagnetoCursor - API Framework Usage Examples
 * 
 * This file demonstrates how to use the API Framework client library
 * for interacting with different social media platform APIs.
 */

import { 
  APIRequest, 
  APIResponse, 
  MetaAPIClient, 
  TwitterAPIClient, 
  GoogleAPIClient,
  APIFrameworkCampaignManager
} from '../api-framework.js';

import { ENDPOINTS } from '../api-config.js';

/**
 * Example 1: Setting up platform clients
 * 
 * This example shows how to initialize platform-specific API clients
 * with the necessary credentials.
 */
async function setupApiClients() {
  // Meta (Facebook & Instagram) credentials
  const metaCredentials = {
    META_APP_ID: 'your-app-id',
    META_APP_SECRET: 'your-app-secret',
    META_ACCESS_TOKEN: 'your-access-token'
  };
  
  // Twitter credentials
  const twitterCredentials = {
    X_API_KEY: 'your-api-key',
    X_API_SECRET: 'your-api-secret',
    X_ACCESS_TOKEN: 'your-access-token',
    X_ACCESS_TOKEN_SECRET: 'your-access-token-secret'
  };
  
  // Google credentials
  const googleCredentials = {
    GOOGLE_CLIENT_ID: 'your-client-id',
    GOOGLE_CLIENT_SECRET: 'your-client-secret',
    GOOGLE_REFRESH_TOKEN: 'your-refresh-token'
  };
  
  // Create API clients
  const metaClient = new MetaAPIClient(metaCredentials);
  const twitterClient = new TwitterAPIClient(twitterCredentials);
  const googleClient = new GoogleAPIClient(googleCredentials);
  
  // Initialize all clients
  await Promise.all([
    metaClient.initialize(),
    twitterClient.initialize(),
    googleClient.initialize()
  ]);
  
  console.log('All API clients initialized successfully');
  
  return {
    metaClient,
    twitterClient,
    googleClient
  };
}

/**
 * Example 2: Creating and executing a Meta campaign
 * 
 * This example shows how to create a campaign on Meta platforms
 * using the API Framework client.
 */
async function createMetaCampaign(metaClient) {
  try {
    // Step 1: Create a campaign
    const campaignRequest = metaClient.createCampaignRequest(
      'Summer Promotion Campaign',
      'REACH',
      'PAUSED',
      ['EMPLOYMENT'] // Special ad category for job ads
    );
    
    const campaignResponse = await metaClient.executeRequest(campaignRequest);
    
    if (!campaignResponse.success) {
      console.error('Failed to create campaign:', campaignResponse.error);
      return;
    }
    
    const campaignId = campaignResponse.data.campaign_id;
    console.log('Campaign created with ID:', campaignId);
    
    // Step 2: Create an ad set with targeting
    const targeting = {
      age_min: 22,
      age_max: 45,
      genders: [1, 2], // Both men and women
      geo_locations: {
        countries: ['US'],
        cities: [
          { key: '2421215', name: 'San Francisco, California', radius: 50, radius_unit: 'mile' }
        ]
      },
      interests: [
        { id: '6003139266461', name: 'Job hunting' },
        { id: '6002714895372', name: 'Career development' }
      ]
    };
    
    const adSetRequest = metaClient.createAdSetRequest(
      campaignId,
      'Software Engineers in San Francisco',
      targeting,
      2000, // $20.00 daily budget
      600,  // $6.00 bid amount
      'IMPRESSIONS',
      'PAUSED'
    );
    
    const adSetResponse = await metaClient.executeRequest(adSetRequest);
    
    if (!adSetResponse.success) {
      console.error('Failed to create ad set:', adSetResponse.error);
      return;
    }
    
    const adSetId = adSetResponse.data.ad_set_id;
    console.log('Ad set created with ID:', adSetId);
    
    // Step 3: Get campaign statistics (example of a cacheable request)
    const statsRequest = metaClient.getCampaignStatsRequest(campaignId);
    const statsResponse = await metaClient.executeRequest(statsRequest);
    
    if (statsResponse.success) {
      console.log('Campaign statistics:', statsResponse.data);
      console.log('Response timing (ms):', statsResponse.timing);
    }
    
    return {
      campaignId,
      adSetId,
      stats: statsResponse.data
    };
  } catch (error) {
    console.error('Error in Meta campaign creation:', error);
  }
}

/**
 * Example 3: Creating and publishing a tweet with Twitter API
 * 
 * This example shows how to create and publish a tweet on Twitter
 * using the API Framework client.
 */
async function publishTweet(twitterClient, jobTitle, jobLink) {
  try {
    // Create tweet text
    const tweetText = `We're hiring! Check out our latest ${jobTitle} position and apply now: ${jobLink} #JobAlert #Hiring #TechJobs`;
    
    // Create tweet request
    const tweetRequest = twitterClient.postTweetRequest(tweetText);
    
    // Execute the request
    const tweetResponse = await twitterClient.executeRequest(tweetRequest);
    
    if (!tweetResponse.success) {
      console.error('Failed to post tweet:', tweetResponse.error);
      return null;
    }
    
    console.log('Tweet posted successfully:', tweetResponse.data.tweet_id);
    return tweetResponse.data.tweet_id;
  } catch (error) {
    console.error('Error publishing tweet:', error);
    return null;
  }
}

/**
 * Example 4: Creating Google Ads campaign with targeting
 * 
 * This example shows how to create a Google Ads campaign with
 * location and demographic targeting.
 */
async function createGoogleCampaign(googleClient, jobTitle, jobDescription) {
  try {
    // Step 1: Create the campaign
    const campaignRequest = googleClient.createCampaignRequest(
      `${jobTitle} - Google Recruitment Campaign`,
      5000, // $50 daily budget
      'PAUSED'
    );
    
    const campaignResponse = await googleClient.executeRequest(campaignRequest);
    
    if (!campaignResponse.success) {
      console.error('Failed to create Google campaign:', campaignResponse.error);
      return null;
    }
    
    const campaignId = campaignResponse.data.campaign_id;
    console.log('Google campaign created with ID:', campaignId);
    
    // Step 2: Create an ad group
    const adGroupRequest = googleClient.createAdGroupRequest(
      campaignId,
      `${jobTitle} - Main Ad Group`,
      'PAUSED'
    );
    
    const adGroupResponse = await googleClient.executeRequest(adGroupRequest);
    
    if (!adGroupResponse.success) {
      console.error('Failed to create ad group:', adGroupResponse.error);
      return null;
    }
    
    const adGroupId = adGroupResponse.data.ad_group_id;
    console.log('Ad group created with ID:', adGroupId);
    
    // Step 3: Create location targeting (e.g., San Francisco, New York, Seattle)
    const locationRequest = googleClient.createLocationTargetingRequest(
      campaignId,
      ['San Francisco, CA', 'New York, NY', 'Seattle, WA']
    );
    
    await googleClient.executeRequest(locationRequest);
    
    // Step 4: Create demographic targeting (e.g., working professionals 25-54)
    const demographicRequest = googleClient.createDemographicTargetingRequest(
      adGroupId,
      {
        age_ranges: ['25-34', '35-44', '45-54'],
        genders: ['MALE', 'FEMALE'],
        parental_status: ['PARENT', 'NOT_A_PARENT']
      }
    );
    
    await googleClient.executeRequest(demographicRequest);
    
    // Step 5: Create responsive search ad
    const adRequest = googleClient.createResponsiveSearchAdRequest(
      adGroupId,
      [
        `Hiring: ${jobTitle}`,
        `${jobTitle} - Apply Now`,
        `Career Opportunity: ${jobTitle}`
      ],
      [
        `${jobDescription.substring(0, 80)}...`,
        'Join our team and work on exciting projects!',
        'Competitive salary and benefits package'
      ],
      'https://careers.example.com/jobs',
      'PAUSED'
    );
    
    const adResponse = await googleClient.executeRequest(adRequest);
    
    if (!adResponse.success) {
      console.error('Failed to create ad:', adResponse.error);
    } else {
      console.log('Responsive search ad created with ID:', adResponse.data.ad_id);
    }
    
    return {
      campaignId,
      adGroupId,
      adId: adResponse.success ? adResponse.data.ad_id : null
    };
  } catch (error) {
    console.error('Error creating Google campaign:', error);
    return null;
  }
}

/**
 * Example 5: Using the unified Campaign Manager
 * 
 * This example shows how to use the unified Campaign Manager to
 * create campaigns across multiple platforms.
 */
async function createCrossplatformCampaign() {
  try {
    // Set up API clients
    const { metaClient, twitterClient, googleClient } = await setupApiClients();
    
    // Create campaign manager
    const campaignManager = new APIFrameworkCampaignManager({
      metaClient,
      twitterClient,
      googleClient
    });
    
    // Create campaigns across platforms
    const jobOpeningId = 12345;
    const platforms = ['meta', 'twitter', 'google'];
    const segmentId = 789;
    const budget = 3000; // $30.00 per platform
    const status = 'PAUSED';
    const adContent = 'Join our team as a Software Engineer and work on cutting-edge technology!';
    
    // Execute the cross-platform campaign creation
    const result = await campaignManager.createCampaign(
      jobOpeningId,
      platforms,
      segmentId,
      budget,
      status,
      adContent
    );
    
    console.log('Cross-platform campaign creation results:', result);
    
    // Check results for each platform
    for (const platform of platforms) {
      const platformResult = result.platforms[platform];
      if (platformResult.success) {
        console.log(`✅ ${platform.toUpperCase()} campaign created successfully:`, platformResult);
      } else {
        console.error(`❌ ${platform.toUpperCase()} campaign creation failed:`, platformResult.error);
      }
    }
    
    // Get metrics from all platforms
    const metrics = campaignManager.getMetrics();
    console.log('Platform metrics:', metrics);
    
    return result;
  } catch (error) {
    console.error('Error in cross-platform campaign creation:', error);
    return null;
  }
}

/**
 * Example 6: Handling API errors and retrying
 * 
 * This example shows how to handle API errors and implement retry logic.
 */
async function handleApiErrors(client, request, maxRetries = 3) {
  let retries = 0;
  let lastError = null;
  
  while (retries < maxRetries) {
    try {
      const response = await client.executeRequest(request);
      
      if (response.success) {
        return response;
      }
      
      // If rate limited, wait and retry
      if (response.statusCode === 429) {
        const retryAfter = response.headers['retry-after'] || 5;
        console.log(`Rate limited. Retrying after ${retryAfter} seconds...`);
        await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
        retries++;
        continue;
      }
      
      // For other errors, return the error response
      return response;
    } catch (error) {
      lastError = error;
      
      // Network errors may be transient, so retry
      if (error.message === 'Failed to fetch') {
        console.log(`Network error (attempt ${retries + 1}/${maxRetries}). Retrying...`);
        await new Promise(resolve => setTimeout(resolve, 2000));
        retries++;
        continue;
      }
      
      // For other errors, throw immediately
      throw error;
    }
  }
  
  // If we've exhausted retries, throw the last error
  throw lastError || new Error('Maximum retries exceeded');
}

// Examples are implemented as functions that can be called when needed
export {
  setupApiClients,
  createMetaCampaign,
  publishTweet,
  createGoogleCampaign,
  createCrossplatformCampaign,
  handleApiErrors
};
