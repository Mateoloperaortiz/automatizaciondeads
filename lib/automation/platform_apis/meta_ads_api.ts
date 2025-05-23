import { MetaCampaignPayload, MetaAdSetPayload, MetaAdCreativePayload, MetaFullAdStructure } from '../translators/meta_translator';
import { JobAd } from '@/lib/db/schema';
import { PlatformAgnosticTargeting } from '../taxonomy_mapper';
import { TEST_ACCOUNTS_ONLY } from '@/lib/config';

const META_GRAPH_API_VERSION = 'v19.0'; // Or your desired API version
const META_GRAPH_API_BASE_URL = `https://graph.facebook.com/${META_GRAPH_API_VERSION}`;

interface MetaApiErrorResponse {
    message: string;
    type: string;
    code: number;
    error_subcode?: number;
    fbtrace_id: string;
    // Meta might also include 'error_user_title' and 'error_user_msg'
    error_user_title?: string;
    error_user_msg?: string;
}
interface MetaApiResponse {
    id?: string;
    error?: MetaApiErrorResponse;
    // Other fields might be present depending on the endpoint
}

export class MetaApiError extends Error {
    public readonly type?: string;
    public readonly code?: number;
    public readonly subcode?: number;
    public readonly fbtrace_id?: string;
    public readonly userTitle?: string;
    public readonly userMsg?: string;
    public readonly status?: number; // HTTP status

    constructor(
        message: string,
        apiError?: MetaApiErrorResponse,
        httpStatus?: number
    ) {
        super(message);
        this.name = 'MetaApiError';
        this.status = httpStatus;
        if (apiError) {
            this.type = apiError.type;
            this.code = apiError.code;
            this.subcode = apiError.error_subcode;
            this.fbtrace_id = apiError.fbtrace_id;
            this.userTitle = apiError.error_user_title;
            this.userMsg = apiError.error_user_msg;
        }
        // Ensure the prototype is correctly set for instanceof checks
        Object.setPrototypeOf(this, MetaApiError.prototype);
    }
}

const RETRYABLE_ERROR_CODES = [
    1, // Unknown error (sometimes transient)
    2, // Service temporarily unavailable
    4, // Application-level throttling
    17, // User request limit reached
    32, // Page-level throttling (for page-related calls)
    613, // Calls to this API have exceeded the rate limit
    80004, // Application request limit reached (older code, sometimes still seen)
    // Add more specific subcodes if known, e.g., error_subcode for rate limiting
];

const DEFAULT_MAX_RETRIES = 3;
const DEFAULT_RETRY_DELAY_MS = 1000; // Initial delay, can be made exponential

/**
 * Helper function to make API calls to Meta Graph API with retry logic.
 */
async function callMetaApi<T = MetaApiResponse>(
    endpoint: string,
    accessToken: string,
    method: 'GET' | 'POST' | 'DELETE' = 'GET',
    body: Record<string, any> | null = null,
    maxRetries: number = DEFAULT_MAX_RETRIES,
    retryDelayMs: number = DEFAULT_RETRY_DELAY_MS
): Promise<T> {
    const headers: Record<string, string> = {
        'Authorization': `Bearer ${accessToken}`,
    };
    if (method === 'POST' && body) {
        headers['Content-Type'] = 'application/json';
    }

    // Construct the URL and append the access_token as a query parameter
    let url = `${META_GRAPH_API_BASE_URL}${endpoint}`;
    const urlObj = new URL(url);
    // If the endpoint already has query params, preserve them
    urlObj.searchParams.append('access_token', accessToken);
    url = urlObj.toString();

    let attempts = 0;
    while (attempts < maxRetries) {
        console.log(`Calling Meta API (Attempt ${attempts}/${maxRetries + 1}): ${method} ${url}`);
        if (body) console.log('Request body:', JSON.stringify(body, null, 2));

        try {
            const response = await fetch(url, {
                method: method,
                headers: headers,
                body: body ? JSON.stringify(body) : undefined,
            });

            const responseData: MetaApiResponse = await response.json();
            console.log('Meta API Response:', JSON.stringify(responseData, null, 2));

            if (!response.ok || responseData.error) {
                const errorInfo = responseData.error || {
                    message: `HTTP error! status: ${response.status}`,
                    code: response.status, // Use HTTP status as code if no API error code
                    type: 'HTTPError',
                    fbtrace_id: response.headers.get('x-fb-trace-id') || 'N/A',
                };
                
                const apiError = new MetaApiError(
                    `Meta API Error (${errorInfo.code} ${errorInfo.type}): ${errorInfo.message}`,
                    errorInfo,
                    response.status
                );

                if (RETRYABLE_ERROR_CODES.includes(apiError.code || 0) && attempts <= maxRetries) {
                    console.warn(`Retryable Meta API error (Code: ${apiError.code}). Attempt ${attempts} of ${maxRetries + 1}. Retrying in ${retryDelayMs * attempts}ms...`);
                    await new Promise(resolve => setTimeout(resolve, retryDelayMs * attempts)); // Exponential backoff
                    continue; // Retry the loop
                }
                throw apiError; // Non-retryable error or max retries exceeded
            }
            return responseData as T;
        } catch (error: any) {
            if (error instanceof MetaApiError) { // Re-throw MetaApiError
                throw error;
            }
            // Handle network errors or other unexpected issues
            console.error(`Network or parsing error calling Meta API (Attempt ${attempts}/${maxRetries + 1}) ${method} ${url}:`, error);
            if (attempts <= maxRetries) {
                console.warn(`Retrying due to network/parsing error. Attempt ${attempts} of ${maxRetries + 1}. Retrying in ${retryDelayMs * attempts}ms...`);
 await new Promise(r => setTimeout(r, retryDelayMs * (2 ** (attempts - 1))));
                continue;
            }
            throw new MetaApiError(`Failed to call Meta API after ${attempts} attempts: ${error.message}`);
        }
    }
    // Should not be reached if loop logic is correct, but as a fallback:
    throw new MetaApiError(`Exhausted retries for Meta API call to ${method} ${url}`);
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
        const response = await callMetaApi<{id: string}>(endpoint, accessToken, 'POST', campaignPayload);
        return response.id || null;
    } catch (error: any) {
        if (error instanceof MetaApiError) {
            console.error(`Meta API Error creating campaign (Code: ${error.code}, Type: ${error.type}, Trace: ${error.fbtrace_id}): ${error.message}`);
        } else {
            console.error('Failed to create Meta campaign due to an unexpected error:', error.message);
        }
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
        const response = await callMetaApi<{id: string}>(endpoint, accessToken, 'POST', adSetPayload);
        return response.id || null;
    } catch (error: any) {
         if (error instanceof MetaApiError) {
            console.error(`Meta API Error creating ad set (Code: ${error.code}, Type: ${error.type}, Trace: ${error.fbtrace_id}): ${error.message}`);
        } else {
            console.error('Failed to create Meta ad set due to an unexpected error:', error.message);
        }
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
        const response = await callMetaApi<{id: string}>(endpoint, accessToken, 'POST', adCreativePayload);
        return response.id || null;
    } catch (error: any) {
        if (error instanceof MetaApiError) {
            console.error(`Meta API Error creating ad creative (Code: ${error.code}, Type: ${error.type}, Trace: ${error.fbtrace_id}): ${error.message}`);
        } else {
            console.error('Failed to create Meta ad creative due to an unexpected error:', error.message);
        }
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
        const response = await callMetaApi<{id: string}>(endpoint, accessToken, 'POST', adPayload);
        return response.id || null;
    } catch (error: any) {
        if (error instanceof MetaApiError) {
            console.error(`Meta API Error creating ad (Code: ${error.code}, Type: ${error.type}, Trace: ${error.fbtrace_id}): ${error.message}`);
        } else {
            console.error('Failed to create Meta ad due to an unexpected error:', error.message);
        }
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
        
        // Convert buffer to base64
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

    if (TEST_ACCOUNTS_ONLY) {
        console.log('TEST_ACCOUNTS_ONLY is enabled - skipping Meta API calls.');
        return {
            campaignId: 'test_campaign',
            adSetId: 'test_adset',
            creativeId: 'test_creative',
            adId: 'test_ad',
            imageHash: imageHashFromPayload,
        };
    }
    
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
