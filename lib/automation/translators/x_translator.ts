import { JobAd } from '@/lib/db/schema';
import { PlatformAgnosticTargeting } from '../taxonomy_mapper';

// --- X Ads API Specific Types (Simplified Placeholders - Consult X Ads API Docs) ---
export interface XCampaignPayload {
    name: string;
    funding_instrument_id: string; // Required, ID of the funding source
    start_time?: string; // ISO 8601
    end_time?: string; // ISO 8601
    daily_budget_amount_local_micro?: number; // In micro-currency units (e.g., USD cents * 10000)
    status: 'ACTIVE' | 'PAUSED' | 'DRAFT';
    entity_status: 'ACTIVE' | 'PAUSED' | 'DRAFT'; // X API often uses entity_status
    objective: string; // e.g., 'WEBSITE_CLICKS', 'ENGAGEMENT', 'REACH'
}

export interface XLineItemTargetingCriteria {
    // Examples - X targeting is quite different from Meta's flexible_spec
    locations?: Array<{ country_code: string; targeting_type: string; location_type: string }>;
    // For keywords, interests, followers of users, etc.
    // This part needs significant research into X Ads API targeting options.
    // e.g., conversation_topics?: Array<{ id: string }>, interests?: Array<{ id: string }>
    [key: string]: any;
}

export interface XLineItemPayload {
    name: string;
    campaign_id: string; // To link to the created campaign
    placements: Array<'ALL_ON_X' | 'X_PROFILE' | 'PUBLISHER_NETWORK'>;
    objective: string; // Must align with campaign objective
    bid_amount_local_micro?: number;
    // bid_type?: string;
    // charge_by?: string;
    product_type: 'PROMOTED_TWEET'; // For standard tweet ads
    status: 'ACTIVE' | 'PAUSED' | 'DRAFT';
    targeting_criteria: XLineItemTargetingCriteria[];
    // ... other fields like start/end time if not inherited from campaign ...
}

// X Ads often use Tweet IDs for creatives. You might promote existing tweets or create "dark" tweets (promoted-only).
export interface XAdCreativePayload { // This is more about identifying the tweet to be promoted
    tweet_ids: string[]; // Array of Tweet IDs to be used as creatives
    // Or parameters to create a new promoted-only tweet if API supports that directly in ad creation
}

export interface XFullAdStructure {
    campaignPayload: XCampaignPayload;
    lineItemPayload: XLineItemPayload;
    // creativePayload: XAdCreativePayload; // Creatives (Tweets) are usually linked in Line Item or Ad Group
    tweetIdsToPromote: string[]; // Pass Tweet IDs to the API caller
}

/**
 * Translates generic job ad details and platform-agnostic targeting
 * into the structure required for creating X Ads (Campaign, Line Item).
 *
 * @param jobAd The core JobAd object from your database.
 * @param targetingParams The PlatformAgnosticTargeting object from the taxonomy_mapper.
 * @param fundingInstrumentId The ID of the funding instrument for the X Ads account.
 * @returns A XFullAdStructure object containing payloads for X Ads API calls, or null if critical info is missing.
 */
export function translateToXAd(
    jobAd: JobAd,
    targetingParams: PlatformAgnosticTargeting,
    fundingInstrumentId: string // X Ads API requires this
): XFullAdStructure | null {
    console.log(`Translating ad ID ${jobAd.id} for X with targeting:`, targetingParams);

    if (!fundingInstrumentId) {
        console.error('X Ads: funding_instrument_id is required.');
        return null;
    }

    // --- 1. Construct Campaign Payload ---
    const campaignName = `Job Ad: ${jobAd.title} - X Campaign - ${jobAd.id}`;
    const campaignPayload: XCampaignPayload = {
        name: campaignName,
        funding_instrument_id: fundingInstrumentId,
        start_time: jobAd.scheduleStart ? new Date(jobAd.scheduleStart).toISOString() : undefined,
        end_time: jobAd.scheduleEnd ? new Date(jobAd.scheduleEnd).toISOString() : undefined,
        daily_budget_amount_local_micro: jobAd.budgetDaily ? Math.round(parseFloat(jobAd.budgetDaily as string) * 100 * 10000) : undefined,
        status: 'PAUSED', // Start paused
        entity_status: 'PAUSED',
        objective: 'WEBSITE_CLICKS', // Common for job ads
    };

    // --- 2. Construct Line Item Payload ---
    const lineItemName = `Job Ad: ${jobAd.title} - X Line Item - ${jobAd.id}`;
    const targetingCriteria: XLineItemTargetingCriteria[] = [];

    // Location Mapping (Example - X uses country codes mainly)
    const xLocations: Array<{ country_code: string; targeting_type: string; location_type: string; }> = [];
    if (targetingParams.locations && targetingParams.locations.length > 0) {
        targetingParams.locations.forEach(locCode => {
            if (locCode === 'COUNTRY_US') xLocations.push({ country_code: 'US', targeting_type: 'LOCATION', location_type: 'COUNTRIES' });
            if (locCode === 'COUNTRY_CA') xLocations.push({ country_code: 'CA', targeting_type: 'LOCATION', location_type: 'COUNTRIES' });
            // X location targeting for cities/regions is more complex, often by specific geo IDs or broader regions.
            // "Remote" might mean targeting multiple countries or using keyword/interest targeting for "remote work".
        });
    }
    if (xLocations.length > 0) {
        targetingCriteria.push({ locations: xLocations });
    }

    // Keyword/Interest Mapping (Placeholder - X has its own taxonomy)
    // You would map `targetingParams.skillKeywords`, `targetingParams.industries` to X's conversation topics, interests, etc.
    // This requires research into X Ads API targeting options and their IDs/formats.
    if (targetingParams.skillKeywords && targetingParams.skillKeywords.length > 0) {
        // Example: targetingCriteria.push({ keywords: targetingParams.skillKeywords });
        console.warn('X Translator: Skill/Keyword mapping to X Ads targeting is a placeholder.');
    }
    if (targetingParams.industries && targetingParams.industries.length > 0) {
        console.warn('X Translator: Industry mapping to X Ads targeting is a placeholder.');
    }

    const lineItemPayload: XLineItemPayload = {
        name: lineItemName,
        campaign_id: '{{X_CAMPAIGN_ID}}', // Placeholder, will be replaced
        placements: ['ALL_ON_X'],
        objective: 'WEBSITE_CLICKS',
        product_type: 'PROMOTED_TWEET',
        status: 'PAUSED',
        targeting_criteria: targetingCriteria,
        // bid_amount_local_micro: ... // Optional, can use auto-bid
    };

    // --- 3. Identify Tweet ID(s) for Creative ---
    // For X, you usually promote an existing Tweet or create a Promoted-Only Tweet.
    // For this MVP, let's assume the `creativeAssetUrl` field in JobAd might hold a Tweet ID if it's simple text ad,
    // or we need a way to compose/create a tweet.
    // This is a major simplification.
    let tweetIds: string[] = [];
    if (jobAd.creativeAssetUrl && jobAd.creativeAssetUrl.startsWith('TWEET_ID:')) {
        tweetIds.push(jobAd.creativeAssetUrl.replace('TWEET_ID:',''));
    } else {
        // Placeholder: if no tweet ID, the API caller might need to create a simple text tweet.
        // This is where you'd construct the tweet content from jobAd.title, descriptionShort, targetUrl.
        console.warn('X Translator: No specific Tweet ID provided. Ad creation will need to compose/create a tweet.');
        // For now, pass an empty array, API caller will need to handle tweet creation/selection.
    }
    if (tweetIds.length === 0) {
        console.log("X Translator: No Tweet ID to promote. Engine will need to handle tweet creation.")
        // Fallback: construct text for a new tweet, actual creation is in API caller
    }

    return {
        campaignPayload,
        lineItemPayload,
        tweetIdsToPromote: tweetIds // Or pass structured tweet content to create
    };
} 