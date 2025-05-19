import { MetaCampaignPayload, MetaAdSetPayload, MetaAdCreativePayload, MetaFullAdStructure } from '../translators/meta_translator';
import { JobAd } from '@/lib/db/schema';
import { PlatformAgnosticTargeting } from '../taxonomy_mapper';

const META_GRAPH_API_VERSION = 'v19.0'; // Or your desired API version
const META_GRAPH_API_BASE_URL = `https://graph.facebook.com/${META_GRAPH_API_VERSION}`;

interface MetaApiResponse {
    id?: string;
    error?: {
        message: string;
        type: string;
        code: number;
        error_subcode?: number;
        fbtrace_id: string;
    };
    // Other fields might be present depending on the endpoint
}

/**
 * Helper function to make API calls to Meta Graph API.
 */
async function callMetaApi<T = MetaApiResponse>(
    endpoint: string, 
    accessToken: string, 
    method: 'GET' | 'POST' | 'DELETE' = 'GET', 
    body: Record<string, any> | null = null
): Promise<T> {
    const headers: Record<string, string> = {
        'Authorization': `Bearer ${accessToken}`,
    };
    if (method === 'POST' && body) {
        headers['Content-Type'] = 'application/json';
    }

    const url = `${META_GRAPH_API_BASE_URL}${endpoint}`;
    console.log(`Calling Meta API: ${method} ${url}`);
    if (body) console.log('Request body:', JSON.stringify(body, null, 2));

    try {
        const response = await fetch(url, {
            method: method,
            headers: headers,
            body: body ? JSON.stringify(body) : undefined,
        });

        const responseData = await response.json();
        console.log('Meta API Response:', JSON.stringify(responseData, null, 2));

        if (!response.ok || responseData.error) {
            const errorInfo = responseData.error || { message: `HTTP error! status: ${response.status}`, code: response.status };
            console.error('Meta API Error:', errorInfo);
            // Throw an error that can be caught by the calling function
            throw new Error(`Meta API Error (${errorInfo.code} ${errorInfo.type || 'HTTPError'}): ${errorInfo.message}`);
        }
        return responseData as T;
    } catch (error: any) {
        console.error(`Network or parsing error calling Meta API ${method} ${url}:`, error);
        throw new Error(`Failed to call Meta API: ${error.message}`);
    }
}


/**
 * Creates a new ad campaign on Meta.
 * @param adAccountId The Ad Account ID (e.g., 'act_XXXXXXXXXXXXX').
 * @param campaignPayload The payload from meta_translator.
 * @param accessToken The valid Meta access token.
 * @returns The ID of the newly created campaign if successful.
 */
async function createMetaCampaign(
    adAccountId: string,
    campaignPayload: MetaCampaignPayload,
    accessToken: string
): Promise<string | null> {
    try {
        const endpoint = `/${adAccountId}/campaigns`;
        const response = await callMetaApi(endpoint, accessToken, 'POST', campaignPayload);
        return response.id || null;
    } catch (error) {
        console.error('Failed to create Meta campaign:', error);
        return null;
    }
}

/**
 * Creates a new ad set on Meta.
 * @param adAccountId The Ad Account ID.
 * @param adSetPayload The payload from meta_translator (with campaign_id filled).
 * @param accessToken The valid Meta access token.
 * @returns The ID of the newly created ad set if successful.
 */
async function createMetaAdSet(
    adAccountId: string,
    adSetPayload: MetaAdSetPayload,
    accessToken: string
): Promise<string | null> {
    try {
        const endpoint = `/${adAccountId}/adsets`;
        const response = await callMetaApi(endpoint, accessToken, 'POST', adSetPayload);
        return response.id || null;
    } catch (error) {
        console.error('Failed to create Meta ad set:', error);
        return null;
    }
}

/**
 * Creates a new ad creative on Meta.
 * @param adAccountId The Ad Account ID.
 * @param adCreativePayload The payload from meta_translator.
 * @param accessToken The valid Meta access token.
 * @returns The ID of the newly created ad creative if successful.
 */
async function createMetaAdCreative(
    adAccountId: string,
    adCreativePayload: MetaAdCreativePayload,
    accessToken: string
): Promise<string | null> {
    try {
        const endpoint = `/${adAccountId}/adcreatives`;
        const response = await callMetaApi(endpoint, accessToken, 'POST', adCreativePayload);
        return response.id || null;
    } catch (error) {
        console.error('Failed to create Meta ad creative:', error);
        return null;
    }
}

/**
 * Creates a new ad on Meta.
 * @param adAccountId The Ad Account ID.
 * @param adName The name for the ad.
 * @param adSetId The ID of the ad set this ad belongs to.
 * @param creativeId The ID of the ad creative to use.
 * @param status The status for the ad ('ACTIVE' or 'PAUSED').
 * @param accessToken The valid Meta access token.
 * @returns The ID of the newly created ad if successful.
 */
async function createMetaAd(
    adAccountId: string,
    adName: string,
    adSetId: string,
    creativeId: string,
    status: 'ACTIVE' | 'PAUSED',
    accessToken: string
): Promise<string | null> {
    try {
        const adPayload = {
            name: adName,
            adset_id: adSetId,
            creative: { creative_id: creativeId },
            status: status,
        };
        const endpoint = `/${adAccountId}/ads`;
        const response = await callMetaApi(endpoint, accessToken, 'POST', adPayload);
        return response.id || null;
    } catch (error) {
        console.error('Failed to create Meta ad:', error);
        return null;
    }
}

// --- Creative Asset Upload Functions --- 
interface MetaAdImageUploadResponse {
    images?: { [key: string]: { hash: string; url: string; } };
    hash?: string; // Sometimes top-level for single image
    error?: any;
}

export async function uploadMetaAdImageByUrl(
    adAccountId: string,
    imageUrl: string,
    accessToken: string
): Promise<string | null> { // Returns image_hash
    console.log(`Downloading image from URL: ${imageUrl} for Ad Account: ${adAccountId}`);
    try {
        const imageResponse = await fetch(imageUrl);
        if (!imageResponse.ok) throw new Error(`Failed to download image. Status: ${imageResponse.status}`);
        const imageBuffer = await imageResponse.arrayBuffer();
        const imageBase64 = Buffer.from(imageBuffer).toString('base64');

        const endpoint = `${META_GRAPH_API_BASE_URL}/${adAccountId}/adimages`;
        const formData = new FormData();
        formData.append('bytes', imageBase64);
        
        console.log(`Uploading image bytes for Ad Account: ${adAccountId}`);
        const uploadResponse = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${accessToken}` },
            body: formData, 
        });
        const responseData: MetaAdImageUploadResponse = await uploadResponse.json();
        console.log('Meta Image Upload Response:', responseData);
        if (!uploadResponse.ok || responseData.error) {
            const errorInfo = responseData.error || { message: `Upload HTTP error! status: ${uploadResponse.status}` };
            throw new Error(`Meta Image Upload Error: ${errorInfo.message || 'Unknown upload error'}`);
        }
        if (responseData.images && Object.keys(responseData.images).length > 0) {
            return responseData.images[Object.keys(responseData.images)[0]].hash;
        }
        if (responseData.hash) return responseData.hash; // Fallback for simpler direct hash response
        console.error('No image hash found in Meta upload response.', responseData);
        return null;
    } catch (error: any) {
        console.error(`Failed to process/upload image ${imageUrl}:`, error.message);
        return null;
    }
}

/**
 * Main function to orchestrate the creation of a full ad structure on Meta.
 * @param adAccountId The Ad Account ID.
 * @param fullAdStructure Payloads from the meta_translator.
 * @param accessToken Valid Meta access token.
 * @returns An object with IDs of created entities, or null if any step fails.
 */
export async function postAdToMeta(
    adAccountId: string, 
    fullAdStructure: MetaFullAdStructure, // Expects the fully translated structure
    accessToken: string
    // No longer needs jobAdCreativeAssetUrl or jobAd object directly, as translator handled it with imageHash
): Promise<{ campaignId: string; adSetId: string; creativeId: string; adId: string; imageHash?: string; } | null> {
    console.log(`Posting to Meta Ad Account: ${adAccountId} using pre-translated structure.`);
    
    // The imageHash should already be incorporated into fullAdStructure.adCreativePayload by the translator
    // If an image was uploaded, its hash would have been passed to translateToMetaAd, which then puts it in the payload.
    const imageHashFromPayload = fullAdStructure.adCreativePayload.object_story_spec?.link_data?.image_hash;
    
    const campaignId = await createMetaCampaign(adAccountId, fullAdStructure.campaignPayload, accessToken);
    if (!campaignId) { console.error("Meta ad posting failed at campaign creation."); return null; }
    console.log(`Meta Campaign created with ID: ${campaignId}`);

    const adSetPayloadWithCampaignId = { ...fullAdStructure.adSetPayload, campaign_id: campaignId };
    const adSetId = await createMetaAdSet(adAccountId, adSetPayloadWithCampaignId, accessToken);
    if (!adSetId) { console.error("Meta ad posting failed at ad set creation."); return null; }
    console.log(`Meta Ad Set created with ID: ${adSetId}`);

    // adCreativePayload from fullAdStructure should already have image_hash if one was uploaded and translated
    const creativeId = await createMetaAdCreative(adAccountId, fullAdStructure.adCreativePayload, accessToken);
    if (!creativeId) { console.error("Meta ad posting failed at ad creative creation."); return null; }
    console.log(`Meta Ad Creative created with ID: ${creativeId}`);

    const adName = fullAdStructure.adCreativePayload.name || `Ad for Ad Account ${adAccountId} - Creative ${creativeId}`;
    const adId = await createMetaAd(adAccountId, adName, adSetId, creativeId, 'PAUSED', accessToken);
    if (!adId) { console.error("Meta ad posting failed at ad creation."); return null; }
    console.log(`Meta Ad created with ID: ${adId}. Final status: PAUSED.`);

    return {
        campaignId,
        adSetId,
        creativeId,
        adId,
        imageHash: imageHashFromPayload, // Return the hash that was actually used in the creative
    };
}

// TODOs still apply, especially around robust error handling, video thumbnails, and precise API params for uploads.

// TODO:
// - More sophisticated error handling and retry logic for API calls.
// - Function to update ad status (e.g., from PAUSED to ACTIVE). 
// - Function to update ad status (e.g., from PAUSED to ACTIVE). 