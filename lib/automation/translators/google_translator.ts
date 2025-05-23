import { JobAd } from '@/lib/db/schema';
import { PlatformAgnosticTargeting } from '../taxonomy_mapper';
// Import enums and resource types from the google-ads-api library
import { enums, resources, ResourceNames } from 'google-ads-api';

// --- Google Ads API Specific Types (Aligned with client library expecting object literals for nested fields) ---

// This will be the direct type for creating a CampaignBudget resource
interface GoogleCampaignBudgetPayload extends Partial<resources.CampaignBudget> {
    // Required fields for creation are typically name, amount_micros
    name: string;
    amount_micros: number; // jobAd.budgetDaily converted to micros
    delivery_method?: enums.BudgetDeliveryMethod; // e.g., STANDARD
    // Other fields like period, explicitly_shared can be added
}

// For Campaign.network_settings, use an object literal for simplicity and directness
interface GoogleCampaignNetworkSettingsObject {
    target_google_search?: boolean;
    target_search_network?: boolean;
    target_content_network?: boolean; 
    target_partner_search_network?: boolean;
}

// This will be the direct type for creating a Campaign resource
interface GoogleCampaignResourcePayload extends Partial<resources.Campaign> {
    // Required fields usually name, advertising_channel_type, status, campaign_budget, bidding_strategy_type
    name: string;
    advertising_channel_type: enums.AdvertisingChannelType;
    status: enums.CampaignStatus;
    campaign_budget?: string; // Resource name of the CampaignBudget, set after budget creation
    bidding_strategy_type?: enums.BiddingStrategyType;
    network_settings?: GoogleCampaignNetworkSettingsObject; 
    start_date?: string; // YYYY-MM-DD
    end_date?: string; // YYYY-MM-DD
    // Other campaign settings like frequency_caps, geo_target_type_setting etc.
}

// These will be direct types for creating AdGroup, AdGroupCriterion, AdGroupAd resources
interface GoogleAdGroupResourcePayload extends Partial<resources.AdGroup> {
    name: string;
    campaign: string; // Resource name of the campaign
    status: enums.AdGroupStatus;
    type?: enums.AdGroupType;
    cpc_bid_micros?: number; // For manual CPC at ad group level
}

// Shapes for object literals for AdGroupCriterion fields
interface GoogleKeywordInfoLiteral { text?: string; match_type?: enums.KeywordMatchType }
interface GoogleLocationInfoLiteral { geo_target_constant?: string }

// AdGroupAd payload will be an instance of resources.AdGroupAd
// Here we define shapes for its nested ad data.
interface GoogleAdTextAssetLiteral { text?: string; pinned_field?: enums.ServedAssetFieldType }
interface GoogleResponsiveSearchAdInfoLiteral {
    headlines: GoogleAdTextAssetLiteral[];
    descriptions: GoogleAdTextAssetLiteral[];
    path1?: string;
    path2?: string;
}
interface GoogleAdLiteral extends Partial<resources.Ad> { // Use Partial for top-level Ad structure
    name?: string;
    final_urls: string[];
    responsive_search_ad?: GoogleResponsiveSearchAdInfoLiteral;
    type?: enums.AdType;
}

export interface GoogleFullAdStructure {
    campaignBudgetPayload: GoogleCampaignBudgetPayload;
    campaignPayload: GoogleCampaignResourcePayload;
    adGroupPayload: GoogleAdGroupResourcePayload;
    // These will be constructed as resource instances by the translator now
    adPayload: resources.AdGroupAd; 
    adGroupCriteriaPayloads: resources.AdGroupCriterion[]; 
}

/**
 * Translates generic job ad details and platform-agnostic targeting
 * into structures for creating Google Ads, aligned with the google-ads-api client library.
 */
export function translateToGoogleAd(
    jobAd: JobAd,
    targetingParams: PlatformAgnosticTargeting,
    // customerId is used by the API caller to build resource names, not directly in these payloads
): GoogleFullAdStructure | null {
    console.log(`Translating ad ID ${jobAd.id} for Google Ads with targeting:`, targetingParams);

    // --- 1. Construct Campaign Budget Payload ---
    if (!jobAd.budgetDaily) {
        console.error(`Google Ads: Daily budget is required for ad ID ${jobAd.id}`);
        return null;
    }
    const dailyBudgetMicros = Math.round(parseFloat(jobAd.budgetDaily as string) * 1000000); // 1 USD = 1,000,000 micros
    
    const campaignBudgetPayload: GoogleCampaignBudgetPayload = {
        name: `Budget - ${jobAd.title.substring(0, 100)} - ${jobAd.id} - ${Date.now()}`,
        amount_micros: dailyBudgetMicros,
        delivery_method: enums.BudgetDeliveryMethod.STANDARD,
        // explicitly_shared: false, // If not a shared budget
    };

    // --- 2. Construct Campaign Payload ---
    const campaignName = `Job Ad: ${jobAd.title.substring(0,100)} - Camp - ${jobAd.id}`;
    const campaignPayload: GoogleCampaignResourcePayload = {
        name: campaignName,
        advertising_channel_type: enums.AdvertisingChannelType.SEARCH,
        status: enums.CampaignStatus.PAUSED,
        bidding_strategy_type: enums.BiddingStrategyType.TARGET_SPEND,
        network_settings: { // Using object literal for network_settings
            target_google_search: true,
            target_search_network: true, 
            target_content_network: false, 
        },
        start_date: jobAd.scheduleStart ? new Date(jobAd.scheduleStart).toISOString().split('T')[0] : undefined,
        end_date: jobAd.scheduleEnd ? new Date(jobAd.scheduleEnd).toISOString().split('T')[0] : undefined,
    };

    // --- 3. Construct Ad Group Payload ---
    const adGroupName = `Job Ad: ${jobAd.title.substring(0,100)} - AdGrp - ${jobAd.id}`;
    const adGroupPayload: GoogleAdGroupResourcePayload = {
        name: adGroupName,
        campaign: '{{GOOGLE_CAMPAIGN_RESOURCE_NAME}}', // Placeholder, filled by API caller
        status: enums.AdGroupStatus.PAUSED,
        type: enums.AdGroupType.SEARCH_STANDARD,
        // cpc_bid_micros: 1000000, // Example: $1 CPC, if using Manual CPC at ad group level
    };

    // --- 4. Construct Ad Group Criteria (Targeting) Payloads ---
    const adGroupCriteriaPayloads: resources.AdGroupCriterion[] = []; // Array of resource instances
    
    // Location Mapping - creating resources.AdGroupCriterion with LocationInfo
    // For a production system, this mapping should be externalized and more comprehensive.
    // Google provides a downloadable CSV of all geo target constants.
    // Example: https://developers.google.com/google-ads/api/reference/data/geotargets
    const geoTargetLookup: Record<string, number | undefined> = {
        'COUNTRY_US': 2840, // United States
        'COUNTRY_CA': 2124, // Canada
        'STATE_CA_US': 21137, // California, US
        'STATE_NY_US': 21167, // New York, US
        'CITY_NYC_NY_US': 1023191, // New York City, NY, US
        'CITY_SF_CA_US': 1014221, // San Francisco, CA, US (Note: Google's ID for SF is 1014221, not 1014044 as in example)
        // Add more common codes as needed or implement a more robust lookup from an external file
    };

    if (targetingParams.locations && targetingParams.locations.length > 0) {
        targetingParams.locations.forEach(locCode => {
            const geoTargetId = geoTargetLookup[locCode];
            let geoTargetConstantResourceName: string | undefined;

            if (geoTargetId) {
                geoTargetConstantResourceName = ResourceNames.geoTargetConstant(geoTargetId);
            } else {
                console.warn(`Google Ads Translator: No geo target constant ID found for location code: ${locCode}. Skipping.`);
            }
            
            if (geoTargetConstantResourceName) {
                adGroupCriteriaPayloads.push(
                    new resources.AdGroupCriterion({
                        ad_group: '{{GOOGLE_ADGROUP_RESOURCE_NAME}}', // Will be replaced by caller
                        status: enums.AdGroupCriterionStatus.ENABLED,
                        location: { // Object literal for LocationInfo shape
                            geo_target_constant: geoTargetConstantResourceName,   
                        },
                    })
                );
            }
        });
    }

    // Keyword Mapping - creating resources.AdGroupCriterion with KeywordInfo
    const keywordsToTarget: string[] = [];
    if (jobAd.title) keywordsToTarget.push(jobAd.title); // Add job title
    if (targetingParams.skillKeywords) keywordsToTarget.push(...targetingParams.skillKeywords);
    if (targetingParams.industries) {
        targetingParams.industries.forEach(ind => {
            if (ind === 'TECH_SOFTWARE_DEV') keywordsToTarget.push('software engineer jobs', 'developer roles');
            if (ind === 'BIZ_SALES') keywordsToTarget.push('sales jobs', 'account executive positions');
        });
    }
    if (targetingParams.seniority) {
        targetingParams.seniority.forEach(sen => {
            if (sen === 'SENIORITY_SENIOR') keywordsToTarget.push('senior software engineer', 'senior developer');
            if (sen === 'SENIORITY_ENTRY') keywordsToTarget.push('entry level software jobs', 'junior developer roles');
        });
    }
    const uniqueKeywords = [...new Set(keywordsToTarget)];
    uniqueKeywords.forEach(keywordText => {
        if (keywordText.trim() !== '') {
            adGroupCriteriaPayloads.push(
                new resources.AdGroupCriterion({
                    ad_group: '{{GOOGLE_ADGROUP_RESOURCE_NAME}}', // Will be replaced by caller
                    status: enums.AdGroupCriterionStatus.ENABLED,
                    keyword: { // Object literal for KeywordInfo shape                   
                        text: keywordText,
                        match_type: enums.KeywordMatchType.BROAD,
                    },
                })
            );
        }
    });
    // TODO: Audience Segment mapping (User Lists, In-Market, Affinity etc.)

    // --- 5. Construct Ad (AdGroupAd) Payload ---
    const adName = `Job Ad RSA: ${jobAd.title.substring(0,50)} - ${jobAd.id}`;
    let headlines: GoogleAdTextAssetLiteral[] = [
        { text: jobAd.title.slice(0, 30) },
        { text: `Apply: ${(jobAd.companyName ?? jobAd.title).slice(0, 22)}` },
        { text: (jobAd.companyName ?? 'Top Company').slice(0, 30) },
    ];
    if (jobAd.companyName) {
        headlines.push({ text: jobAd.companyName.slice(0,30) }); // Add a 4th if companyName exists
    }
    headlines = headlines.slice(0,15); // Max 15 headlines

    let descriptions: GoogleAdTextAssetLiteral[] = [
        { text: jobAd.descriptionShort.slice(0, 90) },
        { text: `Join ${(jobAd.companyName ?? 'us')} as a ${jobAd.title.slice(0, 30)}. Apply today!`.slice(0, 90) },
    ];
    if (jobAd.descriptionLong && jobAd.descriptionLong.length > 10) { // Add a 3rd if long desc exists
        descriptions.push({ text: jobAd.descriptionLong.slice(0,90) });
    }
    descriptions = descriptions.slice(0,4); // Max 4 descriptions

    const adPayload = new resources.AdGroupAd({
        ad_group: '{{GOOGLE_ADGROUP_RESOURCE_NAME}}', 
        status: enums.AdGroupAdStatus.PAUSED,
        ad: new resources.Ad({
            name: adName, 
            type: enums.AdType.RESPONSIVE_SEARCH_AD,
            final_urls: [jobAd.targetUrl],
            responsive_search_ad: { // Object literal for ResponsiveSearchAdInfo shape
                headlines: headlines,
                descriptions: descriptions,
            },
        }),
    });
    // Handle creativeAssetUrl for Display Ads (upload to AssetService, get resource name, link here)
    if (jobAd.creativeAssetUrl && campaignPayload.advertising_channel_type === enums.AdvertisingChannelType.DISPLAY) {
        console.warn('Google Translator: Creative asset handling for Display Ads needs AssetService integration.');
        // Example: adPayload.ad.responsive_display_ad = new resources.ResponsiveDisplayAdInfo({...})
    }

    return {
        campaignBudgetPayload,
        campaignPayload,
        adGroupPayload,
        adPayload, 
        adGroupCriteriaPayloads, 
    };
}
