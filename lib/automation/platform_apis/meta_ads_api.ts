import { MetaCampaignPayload, MetaAdSetPayload, MetaAdCreativePayload, MetaFullAdStructure } from '../translators/meta_translator';

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
    id?: string; 
    hash?: string; 
    images?: { 
        [key: string]: { 
            hash: string;
            url: string; 
            url_128x128?: string;
        };
    };
    error?: any;
}

async function uploadMetaAdImageByUrl(
    adAccountId: string,
    imageUrl: string,
    accessToken: string
): Promise<string | null> { // Returns image_hash
    console.log(`Downloading image from URL: ${imageUrl} for Ad Account: ${adAccountId}`);
    try {
        // 1. Download the image from the provided URL
        const imageResponse = await fetch(imageUrl);
        if (!imageResponse.ok) {
            throw new Error(`Failed to download image from ${imageUrl}. Status: ${imageResponse.status}`);
        }
        const imageBuffer = await imageResponse.arrayBuffer(); // Get as ArrayBuffer
        const imageBase64 = Buffer.from(imageBuffer).toString('base64');

        // 2. Upload the image bytes to Meta
        const endpoint = `${META_GRAPH_API_BASE_URL}/${adAccountId}/adimages`;
        const formData = new FormData();
        formData.append('bytes', imageBase64);
        // formData.append('name', 'advertised_image.jpg'); // Optional: can give it a name
        // Access token is in the header

        console.log(`Uploading image bytes for Ad Account: ${adAccountId}`);
        const uploadResponse = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                // 'Content-Type' will be set automatically by fetch for FormData
            },
            body: formData, 
        });

        const responseData: MetaAdImageUploadResponse = await uploadResponse.json();
        console.log('Meta Image Upload API Response:', JSON.stringify(responseData, null, 2));

        if (!uploadResponse.ok || responseData.error) {
            const errorInfo = responseData.error || { message: `HTTP error! status: ${uploadResponse.status}` };
            console.error('Meta Image Upload Error:', errorInfo);
            throw new Error(`Meta Image Upload Error: ${errorInfo.message || 'Unknown upload error'}`);
        }
        
        // Extract hash from the nested structure: responseData.images[some_key].hash
        if (responseData.images && Object.keys(responseData.images).length > 0) {
            const firstImageKey = Object.keys(responseData.images)[0];
            const imageHash = responseData.images[firstImageKey]?.hash;
            if (imageHash) {
                return imageHash;
            }
        }
        console.error('No image hash found in Meta upload response.', responseData);
        return null;

    } catch (error: any) {
        console.error(`Failed to process and upload Meta ad image from URL ${imageUrl}:`, error.message);
        return null;
    }
}

interface MetaAdVideoUploadResponse {
    id: string; // This is the video_id
    video_id?: string; // Some API versions might return this alias
    error?: any;
}

/**
 * Uploads a video to Meta from a URL.
 * For simplicity, this attempts a direct upload via file_url.
 * For large videos, Meta's resumable upload protocol is recommended.
 */
async function uploadMetaAdVideoByUrl(
    adAccountId: string,
    videoUrl: string,
    accessToken: string,
    title?: string,
    description?: string
): Promise<string | null> { // Returns video_id
    console.log(`Attempting to upload video from URL: ${videoUrl} for Ad Account: ${adAccountId}`);
    const endpoint = `${META_GRAPH_API_BASE_URL}/${adAccountId}/advideos`;
    
    const formData = new FormData();
    formData.append('file_url', videoUrl); // Parameter for Meta to fetch the video from this URL
    if (title) formData.append('title', title);
    if (description) formData.append('description', description);
    // Access token will be in the Authorization header

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
            body: formData,
        });

        const responseData: MetaAdVideoUploadResponse = await response.json();
        console.log('Meta Video Upload API Response:', JSON.stringify(responseData, null, 2));

        if (!response.ok || responseData.error) {
            const errorInfo = responseData.error || { message: `HTTP error! status: ${response.status}` };
            console.error('Meta Video Upload Error:', errorInfo);
            throw new Error(`Meta Video Upload Error: ${errorInfo.message || 'Unknown upload error'}`);
        }
        
        const videoId = responseData.id || responseData.video_id;
        if (videoId) {
            return videoId;
        }
        console.error('No video_id found in Meta upload response.', responseData);
        return null;

    } catch (error: any) {
        console.error(`Failed to upload Meta ad video from URL ${videoUrl}:`, error.message);
        return null;
    }
}

interface MetaVideoThumbnailNode {
    uri: string;
    is_preferred: boolean;
    // Other fields like width, height might be present
}
interface MetaVideoThumbnailsResponse {
    thumbnails?: {
        data: MetaVideoThumbnailNode[];
    };
    picture?: string; // Fallback direct picture field
    id: string; // Video ID echo
    error?: any;
}

/**
 * Fetches available thumbnail URLs for a given Meta video ID.
 */
async function fetchMetaVideoThumbnailUrl(
    videoId: string, 
    accessToken: string
): Promise<string | null> {
    console.log(`Fetching thumbnails for Meta video ID: ${videoId}`);
    try {
        const fieldsToRequest = 'thumbnails{uri,is_preferred},picture'; // Common fields
        const endpoint = `/${videoId}?fields=${encodeURIComponent(fieldsToRequest)}`;
        
        // Using callMetaApi as it's a GET request with no complex body for OAuth1.0a signing issues
        const response = await callMetaApi<MetaVideoThumbnailsResponse>(endpoint, accessToken, 'GET');

        if (response.error) {
            console.warn(`Error fetching thumbnails for video ${videoId}:`, response.error);
            return null;
        }

        if (response.thumbnails && response.thumbnails.data && response.thumbnails.data.length > 0) {
            const preferredThumbnail = response.thumbnails.data.find(t => t.is_preferred);
            if (preferredThumbnail && preferredThumbnail.uri) {
                console.log(`Found preferred thumbnail for video ${videoId}: ${preferredThumbnail.uri}`);
                return preferredThumbnail.uri;
            }
            const firstThumbnailUri = response.thumbnails.data[0].uri;
            if (firstThumbnailUri) {
                 console.log(`Using first available thumbnail for video ${videoId}: ${firstThumbnailUri}`);
                return firstThumbnailUri;
            }
        } else if (response.picture) {
            console.log(`Using 'picture' field as thumbnail for video ${videoId}: ${response.picture}`);
            return response.picture;
        }
        console.warn(`No suitable thumbnails found for Meta video ID: ${videoId}`, response);
        return null;
    } catch (error: any) {
        console.error(`Failed to fetch thumbnails for Meta video ID ${videoId}:`, error.message);
        return null;
    }
}

/**
 * Main function to orchestrate the creation of a full ad structure on Meta.
 * @param adAccountId The Ad Account ID.
 * @param fullAdStructure Payloads from the meta_translator.
 * @param accessToken Valid Meta access token.
 * @param jobAdCreativeAssetUrl Optional URL of the image/video to upload.
 * @param jobAd Optional job-specific ad information.
 * @returns An object with IDs of created entities, or null if any step fails.
 */
export async function postAdToMeta(
    adAccountId: string, 
    fullAdStructure: MetaFullAdStructure,
    accessToken: string,
    jobAdCreativeAssetUrl?: string | null, 
    jobAd?: { title: string; descriptionShort: string; targetUrl: string; videoThumbnailUrl?: string | null } 
): Promise<{ campaignId: string; adSetId: string; creativeId: string; adId: string; imageHash?: string; videoId?:string; thumbnailUrl?: string; } | null> {
    console.log(`Posting to Meta Ad Account: ${adAccountId}`);
    
    let imageHashToUse: string | undefined = undefined;
    let videoIdToUse: string | undefined = undefined;
    let finalThumbnailUrl: string | undefined = undefined; // For video thumbnail

    if (jobAdCreativeAssetUrl) {
        const isLikelyImage = /\.(jpeg|jpg|gif|png)$/i.test(jobAdCreativeAssetUrl);
        const isLikelyVideo = /\.(mp4|mov|avi|wmv|mkv|webm)$/i.test(jobAdCreativeAssetUrl);

        if (isLikelyImage) {
            const uploadedImageHash = await uploadMetaAdImageByUrl(adAccountId, jobAdCreativeAssetUrl, accessToken);
            if (uploadedImageHash) {
                imageHashToUse = uploadedImageHash;
                console.log(`Image uploaded successfully, hash: ${imageHashToUse}`);
                // The translator will use this if passed correctly
            } else {
                console.warn("Failed to upload image asset for Meta, proceeding without it.");
            }
        } else if (isLikelyVideo) {
            const uploadedVideoId = await uploadMetaAdVideoByUrl(
                adAccountId, 
                jobAdCreativeAssetUrl, 
                accessToken,
                jobAd?.title, // Pass title for video metadata if available
                jobAd?.descriptionShort // Pass description for video metadata if available
            );
            if (uploadedVideoId) {
                videoIdToUse = uploadedVideoId;
                console.log(`Video uploaded successfully, ID: ${videoIdToUse}`);
                
                // Strategy 1: Fetch Meta-generated thumbnail
                const fetchedThumbnail = await fetchMetaVideoThumbnailUrl(videoIdToUse, accessToken);
                if (fetchedThumbnail) {
                    finalThumbnailUrl = fetchedThumbnail;
                } else {
                    // Strategy 2 (Fallback): Check if user provided a thumbnail URL via jobAd object
                    if (jobAd?.videoThumbnailUrl) {
                        finalThumbnailUrl = jobAd.videoThumbnailUrl;
                        console.log(`Using user-provided thumbnail URL: ${finalThumbnailUrl}`);
                    } else {
                        console.warn(`Video ID ${videoIdToUse} obtained, but no thumbnail URL could be fetched or was provided. Creative might fail or use a poor default.`);
                    }
                }
            } else {
                console.warn("Failed to upload video asset for Meta, proceeding without it.");
            }
        }
    } 
    
    // Pass the hashes/IDs and thumbnail to the translator
    // The translator function signature was already updated to accept these
    const finalCreativePayload = fullAdStructure.adCreativePayload;
    if (videoIdToUse && finalThumbnailUrl && finalCreativePayload.object_story_spec?.video_data) {
        finalCreativePayload.object_story_spec.video_data.video_id = videoIdToUse;
        finalCreativePayload.object_story_spec.video_data.image_url = finalThumbnailUrl;
    } else if (imageHashToUse && finalCreativePayload.object_story_spec?.link_data) {
        finalCreativePayload.object_story_spec.link_data.image_hash = imageHashToUse;
    }
    // If it's a video but no thumbnail, the translator will create link_data, which is not ideal for video ads.
    // It's better if translateToMetaAd itself receives all necessary info (videoId, thumbnail) to decide if it can make video_data.
    // The current translateToMetaAd structure prioritizes video if videoId AND thumbnailImageUrl are present.

    const campaignId = await createMetaCampaign(adAccountId, fullAdStructure.campaignPayload, accessToken);
    if (!campaignId) {
        console.error("Meta ad posting failed at campaign creation.");
        return null;
    }
    console.log(`Meta Campaign created with ID: ${campaignId}`);

    const adSetPayloadWithCampaignId = { ...fullAdStructure.adSetPayload, campaign_id: campaignId };
    const adSetId = await createMetaAdSet(adAccountId, adSetPayloadWithCampaignId, accessToken);
    if (!adSetId) {
        console.error("Meta ad posting failed at ad set creation.");
        return null;
    }
    console.log(`Meta Ad Set created with ID: ${adSetId}`);

    // Use the potentially modified finalCreativePayload
    const creativeId = await createMetaAdCreative(adAccountId, finalCreativePayload, accessToken);
    if (!creativeId) {
        console.error("Meta ad posting failed at ad creative creation.");
        return null;
    }
    console.log(`Meta Ad Creative created with ID: ${creativeId}`);

    const adName = finalCreativePayload.name || `Ad for ${adAccountId} - ${new Date().toISOString()}`;
    const adId = await createMetaAd(adAccountId, adName, adSetId, creativeId, 'PAUSED', accessToken);
    if (!adId) {
        console.error("Meta ad posting failed at ad creation.");
        return null;
    }
    console.log(`Meta Ad created with ID: ${adId}. Final status: PAUSED.`);

    return {
        campaignId,
        adSetId,
        creativeId,
        adId,
        imageHash: imageHashToUse,
        videoId: videoIdToUse,
        thumbnailUrl: finalThumbnailUrl
    };
}

// TODOs still apply, especially around robust error handling, video thumbnails, and precise API params for uploads.

// TODO:
// - Implement image/video asset uploading if creativeAssetUrl is a local path or needs to be hosted by Meta.
// - More sophisticated error handling and retry logic for API calls.
// - Function to update ad status (e.g., from PAUSED to ACTIVE). 