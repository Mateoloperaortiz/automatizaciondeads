import { JobAd } from '@/lib/db/schema'; // Assuming JobAd type from your DB schema
import { PlatformAgnosticTargeting } from '../taxonomy_mapper';

// --- Meta API Specific Types (More detailed based on research) --- 
export interface MetaCampaignPayload {
    name: string;
    objective: 'LINK_CLICKS' | 'CONVERSIONS' | 'REACH' | 'LEAD_GENERATION' | 'OUTCOME_LEADS' | string;
    status: 'ACTIVE' | 'PAUSED';
    special_ad_categories: string[]; // Always ['EMPLOYMENT'] for job ads
    buying_type?: string;
    daily_budget?: number; // In cents, for CBO
    lifetime_budget?: number; // In cents, for CBO
}

interface MetaFlexibleSpecGroup {
    // Each key is a targeting type, e.g., interests, behaviors, education_majors, work_positions
    // The value is an array of objects, usually {id: string, name?: string}
    interests?: Array<{ id: string; name?: string }>;
    behaviors?: Array<{ id: string; name?: string }>;
    education_majors?: Array<{ id: string; name?: string }>;
    work_positions?: Array<{ id: string; name?: string }>; // For job titles
    // ... other detailed targeting types ...
}

interface MetaTargetingSpec {
    geo_locations?: { 
        countries?: string[]; 
        regions?: Array<{key: string}>; 
        cities?: Array<{key: string}>;
        location_types?: Array<'home' | 'recent'>;
    };
    age_min?: number;
    age_max?: number;
    genders?: number[]; // [1] for Male, [2] for Female
    flexible_spec?: MetaFlexibleSpecGroup[];
    publisher_platforms?: ('facebook' | 'instagram' | 'audience_network' | 'messenger')[];
    facebook_positions?: string[]; // e.g., ['feed', 'instant_article']
    instagram_positions?: string[]; // e.g., ['stream', 'story']
    device_platforms?: ('mobile' | 'desktop')[];
    // exclusions?: MetaFlexibleSpecGroup[]; // To exclude audiences
}

export interface MetaAdSetPayload {
    name: string;
    campaign_id: string; 
    status: 'ACTIVE' | 'PAUSED';
    billing_event?: 'IMPRESSIONS' | 'LINK_CLICKS' | string;
    optimization_goal?: 'LINK_CLICKS' | 'REACH' | 'OFFSITE_CONVERSIONS' | string;
    bid_strategy?: 'LOWEST_COST_WITHOUT_CAP' | string;
    daily_budget?: number; // In cents
    start_time?: string; // ISO 8601 format
    end_time?: string; // ISO 8601 format, optional
    targeting: MetaTargetingSpec;
    promoted_object?: { page_id?: string }; // For some objectives like Page Likes
}

interface MetaLinkData {
    message: string;
    link: string;
    name?: string; // Headline
    caption?: string; 
    description?: string;
    image_hash?: string; // Use this after uploading image
    call_to_action: { type: string; value?: { link: string } };
}
interface MetaVideoData {
    video_id: string; // Use this after uploading video
    image_url: string; // Thumbnail URL for the video
    title?: string; // Headline for video ad
    message?: string; // Primary text for video ad
    call_to_action: { type: string; value?: { link: string } };
}

export interface MetaAdCreativePayload {
    name: string;
    page_id?: string; // Required if object_story_spec is used, taken from DEFAULT_META_PAGE_ID
    object_story_spec?: {
        page_id: string; 
        link_data?: MetaLinkData;
        video_data?: MetaVideoData;
        instagram_actor_id?: string; // If posting to Instagram from a specific Insta account
    };
    asset_feed_spec?: { // For dynamic creatives, multiple assets
        // ... structure for asset feeds ...
    };
    // OR if using an existing page post:
    // object_id?: string; // Page ID
    // effective_object_story_id?: string; // Post ID (especially for unpublished/dark posts)
}

export interface MetaFullAdStructure {
    campaignPayload: MetaCampaignPayload;
    adSetPayload: MetaAdSetPayload;
    adCreativePayload: MetaAdCreativePayload;
}

const DEFAULT_META_PAGE_ID = process.env.META_DEFAULT_PAGE_ID || 'YOUR_FACEBOOK_PAGE_ID';

// --- UPDATED WITH YOUR LATEST RESEARCH (and keeping some placeholders) --- 
const META_TARGETING_IDS = {
    // Verified from your search for "Software Engineering":
    INTEREST_SOFTWARE_ENGINEERING_IT: '6003380970205', // "Ingeniería de software (tecnología de la información)"
    INTEREST_SOFTWARE_DEVELOPMENT_SW: '6003409558536', // "Desarrollo de software (software)"
    INTEREST_CASE_TOOLS: '6003477759544', // "Herramienta CASE" (matches your earlier 8020 in concept)
    INTEREST_DOCKER_SOFTWARE: '6019214301359', // Added Docker interest ID

    // Broader interest you found previously, still relevant:
    INTEREST_COMPUTER_PROGRAMMING: '85267820', 
    
    // Placeholders for other categories - NEED YOUR RESEARCH
    INDUSTRY_SALES: 'FAKE_SALES_INTEREST_ID', 
    SKILL_PYTHON: 'FAKE_PYTHON_INTEREST_ID', 
    SKILL_JAVASCRIPT: 'FAKE_JS_INTEREST_ID', 
    INTEREST_SENIOR_PROFESSIONALS: 'FAKE_SENIOR_INTEREST_ID',
};
// --- END OF IDs TO BE REPLACED/VERIFIED --- 

export function translateToMetaAd(
    jobAd: JobAd,
    targetingParams: PlatformAgnosticTargeting,
    imageHash?: string, 
    videoId?: string, 
    thumbnailImageUrl?: string 
): MetaFullAdStructure | null {
    console.log(`Translating ad ID ${jobAd.id} for Meta. Targeting:`, targetingParams, `Image Hash: ${imageHash}, Video ID: ${videoId}`);

    if (!DEFAULT_META_PAGE_ID || DEFAULT_META_PAGE_ID === 'YOUR_FACEBOOK_PAGE_ID') {
        console.error('META_DEFAULT_PAGE_ID is not configured. Cannot create Meta ad creative.');
        return null;
    }

    const campaignName = `Job Ad: ${jobAd.title} - Campaign - ${jobAd.id}`;
    const campaignPayload: MetaCampaignPayload = {
        name: campaignName,
        objective: 'LINK_CLICKS', 
        status: 'PAUSED',
        special_ad_categories: ['EMPLOYMENT'],
        buying_type: 'AUCTION',
    };

    const adSetName = `Job Ad: ${jobAd.title} - Ad Set - ${jobAd.id}`;
    const dailyBudgetCents = jobAd.budgetDaily ? Math.round(parseFloat(jobAd.budgetDaily as string) * 100) : undefined;
    if (!dailyBudgetCents) {
        console.error(`Ad ID ${jobAd.id}: Daily budget is required for Meta ad set.`);
        return null;
    }
    const startTimeISO = jobAd.scheduleStart ? new Date(jobAd.scheduleStart).toISOString() : undefined;
    const endTimeISO = jobAd.scheduleEnd ? new Date(jobAd.scheduleEnd).toISOString() : undefined;

    const metaTargeting: MetaTargetingSpec = {
        geo_locations: { countries: ['US'], location_types: ['home', 'recent'] }, 
        publisher_platforms: ['facebook', 'instagram'],
        facebook_positions: ['feed'], 
        instagram_positions: ['stream'], 
        device_platforms: ['mobile', 'desktop']
    };

    // Location Mapping (as before, simplified)
    if (targetingParams.locations && targetingParams.locations.length > 0) {
        const countries: string[] = [];
        const cities: Array<{key: string}> = []; 
        let hasSpecificLocation = false;
        targetingParams.locations.forEach(locCode => {
            if (locCode === 'COUNTRY_US') { countries.push('US'); hasSpecificLocation = true; }
            else if (locCode === 'COUNTRY_CA') { countries.push('CA'); hasSpecificLocation = true; }
            else if (locCode === 'LOCATION_REMOTE') {
                if (!countries.includes('US')) countries.push('US'); 
                hasSpecificLocation = true; 
            }
        });
        if (hasSpecificLocation) {
            metaTargeting.geo_locations = {}; 
            if (countries.length > 0) metaTargeting.geo_locations.countries = countries;
            if (cities.length > 0) metaTargeting.geo_locations.cities = cities;
        }
    }

    // Detailed Targeting with flexible_spec
    const flexibleSpecGroups: MetaFlexibleSpecGroup[] = [];
    let currentGroup: MetaFlexibleSpecGroup = {};
    currentGroup.interests = currentGroup.interests || [];

    // Map Industries to Meta Interests 
    if (targetingParams.industries && targetingParams.industries.length > 0) {
        targetingParams.industries.forEach(industryCode => {
            if (industryCode === 'TECH_SOFTWARE_DEV') {
                currentGroup.interests?.push({ id: META_TARGETING_IDS.INTEREST_SOFTWARE_ENGINEERING_IT, name: 'Software engineering (information technology)' });
                currentGroup.interests?.push({ id: META_TARGETING_IDS.INTEREST_SOFTWARE_DEVELOPMENT_SW, name: 'Software development (software)' });
                currentGroup.interests?.push({ id: META_TARGETING_IDS.INTEREST_COMPUTER_PROGRAMMING, name: 'Computer Programming' });
            }
            if (industryCode === 'BIZ_SALES') {
                 currentGroup.interests?.push({ id: META_TARGETING_IDS.INDUSTRY_SALES, name: 'Sales Interest Placeholder' });
            }
        });
    }

    // Map SkillKeywords to Meta Interests
    if (targetingParams.skillKeywords && targetingParams.skillKeywords.length > 0) {
        targetingParams.skillKeywords.forEach(skill => {
            const skillLower = skill.toLowerCase();
            if (skillLower === 'python' && META_TARGETING_IDS.SKILL_PYTHON !== 'FAKE_PYTHON_INTEREST_ID') {
                currentGroup.interests?.push({ id: META_TARGETING_IDS.SKILL_PYTHON, name: 'Python (Programming Language)' });
            } else if (skillLower === 'javascript' && META_TARGETING_IDS.SKILL_JAVASCRIPT !== 'FAKE_JS_INTEREST_ID') {
                 currentGroup.interests?.push({ id: META_TARGETING_IDS.SKILL_JAVASCRIPT, name: 'JavaScript' });
            } else if (skillLower === 'docker' && META_TARGETING_IDS.INTEREST_DOCKER_SOFTWARE) {
                 currentGroup.interests?.push({ id: META_TARGETING_IDS.INTEREST_DOCKER_SOFTWARE, name: 'Docker (software)'});
            }
        });
    }
    
    // Map Seniority 
    if (targetingParams.seniority && targetingParams.seniority.length > 0) {
        targetingParams.seniority.forEach(seniorityCode => {
            if (seniorityCode === 'SENIORITY_SENIOR' && META_TARGETING_IDS.INTEREST_SENIOR_PROFESSIONALS !== 'FAKE_SENIOR_INTEREST_ID') {
                currentGroup.interests?.push({ id: META_TARGETING_IDS.INTEREST_SENIOR_PROFESSIONALS, name: 'Senior Professionals Interest' }); 
            }
        });
    }

    // Consolidate interests to avoid duplicates if mapped from different sources
    if (currentGroup.interests && currentGroup.interests.length > 0) {
        currentGroup.interests = Array.from(new Map(currentGroup.interests.map(item => [item.id, item])).values());
    } else {
        // If no interests were added, remove the empty array to avoid API error
        delete currentGroup.interests;
    }

    if (Object.keys(currentGroup).length > 0) {
        flexibleSpecGroups.push(currentGroup);
    }
    if (flexibleSpecGroups.length > 0) {
        metaTargeting.flexible_spec = flexibleSpecGroups;
    } else {
        delete metaTargeting.flexible_spec; 
    }

    const adSetPayload: MetaAdSetPayload = {
        name: adSetName,
        campaign_id: '{{CAMPAIGN_ID}}', 
        status: 'PAUSED',
        billing_event: 'IMPRESSIONS', 
        optimization_goal: 'LINK_CLICKS',
        daily_budget: dailyBudgetCents,
        start_time: startTimeISO,
        end_time: endTimeISO,
        targeting: metaTargeting,
    };

    const creativeName = `Job Ad: ${jobAd.title} - Creative - ${jobAd.id}`;
    const adCreativePayload: MetaAdCreativePayload = {
        name: creativeName,
        page_id: DEFAULT_META_PAGE_ID, 
    };

    if (videoId && thumbnailImageUrl) { 
        adCreativePayload.object_story_spec = {
            page_id: DEFAULT_META_PAGE_ID,
            video_data: {
                video_id: videoId,
                image_url: thumbnailImageUrl, 
                title: jobAd.title,
                message: jobAd.descriptionShort,
                call_to_action: { type: 'APPLY_NOW', value: { link: jobAd.targetUrl } },
            }
        };
    } else if (imageHash) {
        adCreativePayload.object_story_spec = {
            page_id: DEFAULT_META_PAGE_ID,
            link_data: {
                message: jobAd.descriptionShort,
                link: jobAd.targetUrl,
                name: jobAd.title,
                image_hash: imageHash,
                call_to_action: { type: 'APPLY_NOW', value: { link: jobAd.targetUrl } },
            }
        };
    } else { 
         adCreativePayload.object_story_spec = {
            page_id: DEFAULT_META_PAGE_ID,
            link_data: {
                message: jobAd.descriptionShort,
                link: jobAd.targetUrl,
                name: jobAd.title,
                call_to_action: { type: 'APPLY_NOW', value: { link: jobAd.targetUrl } },
            }
        };
    }

    return {
        campaignPayload,
        adSetPayload,
        adCreativePayload,
    };
} 