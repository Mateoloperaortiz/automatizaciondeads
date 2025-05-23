import { XCampaignPayload, XLineItemPayload, XFullAdStructure } from '../translators/x_translator';
import OAuth from 'oauth-1.0a';
// Node.js crypto for nonce is not used by oauth-1.0a library directly for this setup
import crypto from 'crypto'; // Use Node's native crypto

// Base URL for X Ads API (ensure this is the correct version, e.g., /12/)
const X_ADS_API_BASE_URL = 'https://ads-api.twitter.com/12'; 

// App Credentials (from .env)
const X_CONSUMER_KEY = process.env.X_CONSUMER_KEY;
const X_CONSUMER_SECRET = process.env.X_CONSUMER_SECRET;

interface XApiResponse {
    data?: any;
    errors?: Array<{ code: number; message: string; details?: any }>;
    next_cursor?: string | null;
}

interface XFundingInstrument {
    id: string;
    cancelled: boolean;
    deleted: boolean;
    able_to_fund: boolean;
    type: string; // e.g., 'CREDIT_LINE', 'CREDIT_CARD'
    name?: string; // Older versions might have name, newer have description
    description?: string;
    // ... other fields from API response ...
}

interface XFundingInstrumentsResponse extends XApiResponse {
    data: XFundingInstrument[];
}

/**
 * Helper function to make API calls to X Ads API using OAuth 1.0a.
 */
async function callXApi<T = XApiResponse>(
    endpoint: string,
    userAccessToken: string,
    userTokenSecret: string,
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
    payload?: Record<string, any> | null, // Can be form data or JSON data for body
    queryParams?: Record<string, any> | null,
    // Explicit content type for payload; defaults to form-urlencoded for POST/PUT if payload exists and not specified
    contentTypeHeader?: 'application/json' | 'application/x-www-form-urlencoded' 
): Promise<T> {
    if (!X_CONSUMER_KEY || !X_CONSUMER_SECRET) {
        throw new Error('X Consumer Key or Secret is not configured in environment variables.');
    }

    const oauth = new OAuth({
        consumer: { key: X_CONSUMER_KEY, secret: X_CONSUMER_SECRET },
        signature_method: 'HMAC-SHA1',
        hash_function(base_string, key) {
            return crypto.createHmac('sha1', key).update(base_string).digest('base64');
        }
    });

    let baseUrlForSignature = `${X_ADS_API_BASE_URL}${endpoint}`;
    let finalFetchUrl = baseUrlForSignature;
    
    // All URL query parameters are signed if present
    const signedParameters = queryParams ? { ...queryParams } : {};

    const requestDataForSigning: OAuth.RequestOptions = {
        url: baseUrlForSignature, // Base URL for signature
        method: method,
        data: signedParameters, // Start with URL query params for signing
    };

    let fetchBody: string | null = null;
    const headers: HeadersInit = {};

    if (queryParams) {
        finalFetchUrl = `${baseUrlForSignature}?${new URLSearchParams(queryParams as Record<string, string>).toString()}`;
    }

    if (method === 'POST' || method === 'PUT') {
        if (payload) {
            let resolvedContentType = contentTypeHeader;
            if (!resolvedContentType && payload && Object.keys(payload).length > 0) {
                // Default to form-urlencoded if contentType not specified but payload exists,
                // as this seems common for X Ads API based on campaign creation.
                resolvedContentType = 'application/x-www-form-urlencoded';
            }

            if (resolvedContentType === 'application/x-www-form-urlencoded') {
                headers['Content-Type'] = 'application/x-www-form-urlencoded';
                fetchBody = new URLSearchParams(payload as Record<string, string>).toString();
                // Add form body parameters to the signature data
                requestDataForSigning.data = { ...signedParameters, ...payload };
            } else if (resolvedContentType === 'application/json') {
                headers['Content-Type'] = 'application/json';
                fetchBody = JSON.stringify(payload);
                // JSON body parameters are NOT added to signature data by default in OAuth 1.0a
                // requestDataForSigning.data remains just signedParameters (URL query params)
            }
        }
    }
    // For GET/DELETE, queryParams (if any) are already in requestDataForSigning.data via signedParameters. No body.

    const token = { key: userAccessToken, secret: userTokenSecret };
    const authorization = oauth.authorize(requestDataForSigning, token);
    headers['Authorization'] = oauth.toHeader(authorization)['Authorization'];
    
    // Mask Authorization header for logging
    const safeHeaders = { ...headers };
    if (safeHeaders['Authorization']) {
        safeHeaders['Authorization'] = '[REDACTED]';
    }
    // Optionally, mask sensitive query/body data here if needed

    console.log(`Calling X Ads API: ${method} [URL REDACTED FOR SENSITIVITY]`);
    if (fetchBody) console.log('X Ads Request body: [REDACTED FOR SENSITIVITY]');
    console.log('X Ads Headers:', safeHeaders);
    console.log('X Ads Request Data for Signing:', requestDataForSigning);

    try {
        const response = await fetch(finalFetchUrl, {
            method: method,
            headers: headers,
            body: fetchBody,
        });
        const responseData = await response.json(); // Assume X Ads API always returns JSON
        console.log('X Ads API Response:', JSON.stringify(responseData, null, 2));

        if (!response.ok || (responseData.errors && responseData.errors.length > 0)) {
            const errorInfo = responseData.errors ? responseData.errors[0] : { message: `HTTP error! status: ${response.status}`, code: response.status };
            console.error('X Ads API Error:', errorInfo);
            throw new Error(`X Ads API Error (${errorInfo.code || response.status}): ${errorInfo.message}`);
        }
        return responseData as T;
    } catch (error: any) {
        console.error(`Network or parsing error calling X Ads API ${method} ${finalFetchUrl}:`, error);
        if (error.response && typeof error.response.json === 'function') { // If fetch error includes response
             console.error("X API Raw Error Response:", await error.response.json());
        }
        throw new Error(`Failed to call X Ads API: ${error.message}`);
    }
}

// Placeholder: Function to create/get Tweet ID if not provided directly
async function ensureTweetCreative(
    accountId: string, 
    jobAd: { title: string; descriptionShort: string; targetUrl: string }, 
    userAccessToken: string, userTokenSecret: string // Updated signature
): Promise<string | null> {
    console.warn("ensureTweetCreative is a placeholder. Needs X API v2 Tweet creation logic using OAuth 1.0a.");
    // Example: Construct tweet text
    let tweetText = `${jobAd.title} - ${jobAd.descriptionShort}`;
    if (tweetText.length + jobAd.targetUrl.length + 1 > 280) {
        tweetText = `${jobAd.title.substring(0, 279 - jobAd.targetUrl.length - 4)}... ${jobAd.targetUrl}`;
    } else {
        tweetText = `${tweetText} ${jobAd.targetUrl}`;
    }
    // This would call POST /2/tweets using callXApi (OAuth 1.0a signed)
    // const tweetPayload = { text: tweetText };
    // const createdTweet = await callXApi(...);
    // return createdTweet?.data?.id;
    return `dummy_tweet_id_${new Date().getTime()}`;
}

/**
 * Fetches the active Funding Instrument ID for a given X Ads Account.
 */
export async function fetchXFundingInstrumentId(
    adsAccountId: string,
    userAccessToken: string,
    userTokenSecret: string
): Promise<string | null> {
    console.log(`Fetching funding instruments for X Ads Account: ${adsAccountId}`);
    try {
        // GET request, no payload, no specific queryParams here, no specific contentType
        const response = await callXApi<XFundingInstrumentsResponse>(
            `/accounts/${adsAccountId}/funding_instruments`,
            userAccessToken,
            userTokenSecret,
            'GET',
            null, // no payload
            null  // no queryParams
        );

        if (response && response.data && response.data.length > 0) {
            // Find an active, usable funding instrument
            // Prioritize non-cancelled, not deleted, and able_to_fund
            const suitableInstrument = 
                response.data.find(fi => fi.able_to_fund && !fi.cancelled && !fi.deleted) ||
                response.data.find(fi => !fi.cancelled && !fi.deleted) || // Fallback if none are explicitly able_to_fund but not cancelled/deleted
                response.data[0]; // Fallback to the first one if no better option
            
            if (suitableInstrument) {
                console.log(`Found suitable X Funding Instrument: ID ${suitableInstrument.id}, Type: ${suitableInstrument.type}, Desc: ${suitableInstrument.description || suitableInstrument.name}`);
                return suitableInstrument.id;
            }
        }
        console.warn(`No suitable funding instrument found for X Ads Account: ${adsAccountId}. Response data:`, response.data);
        return null;
    } catch (error: any) {
        console.error(`Failed to fetch X funding instruments for account ${adsAccountId}:`, error.message);
        return null;
    }
}

/**
 * Main function to orchestrate posting an ad to X (Twitter).
 * @param accountId Your X Ads Account ID.
 * @param xAdStructure Payloads from the x_translator.
 * @param accessToken Valid X Ads API access token (OAuth 1.0a or OAuth 2.0 depending on setup).
 * @param jobAd Original job ad data for creative text if needed.
 * @returns An object with IDs of created entities, or null if any step fails.
 */
export async function postAdToX(
    accountId: string, // This is the X Ads Account ID from your .env or socialPlatformConnections
    xAdStructure: XFullAdStructure,
    // These user-specific tokens come from your .env or socialPlatformConnections
    userAccessToken: string, 
    userTokenSecret: string,
    jobAd: { title: string; descriptionShort: string; targetUrl: string; creativeAssetUrl?: string | null }
): Promise<{ campaignId: string; lineItemId: string; promotedTweetId?: string; } | null> {
    console.log(`Posting to X Ads Account: ${accountId}`);
    if (!userAccessToken || !userTokenSecret) {
        console.error("User Access Token or Secret for X Ads is missing.");
        return null;
    }
    // Ensure funding_instrument_id is present in campaignPayload
    if (!xAdStructure.campaignPayload.funding_instrument_id) {
        console.error("X Ads: funding_instrument_id is missing in campaign payload for postAdToX.");
        return null;
    }

    try {
        // Campaign creation: POST with form-urlencoded data
        const campaignResponse = await callXApi<{data: {id: string}}>(
            `/accounts/${accountId}/campaigns`,
            userAccessToken, userTokenSecret,
            'POST',
            xAdStructure.campaignPayload as Record<string, any>, // payload is form data
            null, // no URL queryParams
            'application/x-www-form-urlencoded' // explicit contentType
        );
        const campaignId = campaignResponse?.data?.id;
        if (!campaignId) {
            console.error("X Ads: Failed to create campaign.");
            return null;
        }
        console.log(`X Campaign created with ID: ${campaignId}`);

        let lineItemPayloadWithCampaign = { ...xAdStructure.lineItemPayload, campaign_id: campaignId };
        let tweetIdsToUse = xAdStructure.tweetIdsToPromote;
        if (!tweetIdsToUse || tweetIdsToUse.length === 0) {
            const newTweetId = await ensureTweetCreative(accountId, jobAd, userAccessToken, userTokenSecret);
            if (newTweetId) tweetIdsToUse = [newTweetId];
            else { console.error("X Ads: Failed to get or create a Tweet."); return null; }
        }
        
        // For creating line items that promote tweets, you often include tweet_ids in the line item payload directly.
        // The X Ads API documentation for POST /accounts/:account_id/line_items needs to be checked for the exact structure.
        // It might be `promoted_tweet_ids` or similar, or part of a `creatives` array within the line item.
        // Assuming lineItemPayloadWithCampaign includes a field like `tweet_ids` (as per x_translator.ts)
        const finalLineItemPayload = { ...lineItemPayloadWithCampaign, tweet_ids: tweetIdsToUse };
        // X Ads API often uses form-data for POST.
        // However, the original code for line items used the `body` parameter of callXApi,
        // which was then treated as JSON. We'll maintain this assumption for line items.
        // If line items also need form-urlencoded, the contentType should be changed.
        const lineItemResponse = await callXApi<{data: {id: string}}>(
            `/accounts/${accountId}/line_items`,
            userAccessToken, userTokenSecret,
            'POST',
            finalLineItemPayload, // payload is JSON data
            null, // no URL queryParams
            'application/json' // explicit contentType
        );
        const lineItemId = lineItemResponse?.data?.id;
        if (!lineItemId) {
            console.error("X Ads: Failed to create line item.");
            return null;
        }
        console.log(`X Line Item created with ID: ${lineItemId} promoting tweet(s): ${tweetIdsToUse.join(', ')}`);

        return {
            campaignId,
            lineItemId,
            promotedTweetId: tweetIdsToUse[0] 
        };
    } catch (error) {
        console.error("Error in postAdToX orchestration:", error);
        return null;
    }
}

// TODOs are critical for X Ads API:
// - OAuth 1.0a: Correctly implement request signing. The current `callXApi` is a complex placeholder.
//   The library `oauth-1.0a` needs careful integration for signing requests, including handling nonces, timestamps, and the signature base string.
// - X Ads API Endpoints & Payloads: Verify all paths (e.g., `/12/accounts/...`) and the exact JSON or form-data structures for campaigns, line items, targeting criteria, and tweet promotion.
// - Funding Instrument ID: This is required for campaign creation and needs to be fetched and stored.
// - Tweet Creation/Selection: Robustly implement `ensureTweetCreative` to create a new tweet via X API v2 or allow selection of existing tweets.
// - Targeting in x_translator.ts: Map your agnostic targeting to X's specific criteria (keywords, interests, follower look-alikes, conversation topics, device, geo, etc.).
