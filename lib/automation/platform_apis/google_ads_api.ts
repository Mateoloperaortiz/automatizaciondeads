import { GoogleFullAdStructure } from '../translators/google_translator';
import { 
    GoogleAdsApi, 
    // GoogleAdsClient, // Remove explicit import if not directly exported or causing issues
    enums, 
    resources, 
    ResourceNames, 
    toMicros,
    // Import MutateOperationResponse if it's an exported type, otherwise use any for now
    // types, // Example if it was under a 'types' namespace
} from 'google-ads-api';
import { SocialPlatformConnection } from '@/lib/db/schema'; // To type connection details

// --- Google Ads API Client Initialization --- 

/**
 * Initializes and returns a Google Ads API client instance for a specific customer.
 *
 * @param refreshToken The OAuth refresh token for the user/account authorizing the app.
 * @param targetCustomerId The Google Ads Customer ID (CID) to operate on (without hyphens).
 * @returns Initialized GoogleAdsClient for the target customer.
 * @throws Error if required credentials are not configured.
 */
function getGoogleAdsClient(
    refreshToken: string,
    targetCustomerId: string
) { // Let TypeScript infer the return type, or use the correct one you find
    const clientId = process.env.GOOGLE_CLIENT_ID;
    const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
    const developerToken = process.env.GOOGLE_DEVELOPER_TOKEN;
    const loginCustomerId = process.env.GOOGLE_LOGIN_CUSTOMER_ID; // Optional MCC ID

    if (!clientId || !clientSecret || !developerToken) {
        console.error('Google Ads API client credentials (ID, Secret, Dev Token) not configured in .env');
        throw new Error('Google Ads API credentials missing.');
    }
    if (!refreshToken) {
        throw new Error('Google Ads: Refresh token is required to initialize client.');
    }
    if (!targetCustomerId) {
        throw new Error('Google Ads: Target Customer ID is required.');
    }

    const apiClient = new GoogleAdsApi({
        client_id: clientId,
        client_secret: clientSecret,
        developer_token: developerToken,
    });

    return apiClient.Customer({
        customer_id: targetCustomerId, 
        login_customer_id: loginCustomerId, // Can be undefined if not using MCC
        refresh_token: refreshToken,
    });
}

// Helper to extract resource name from a MutateOperationResponse
// The exact type for opResp would be MutateOperationResponse from the library if exported and known.
// Using 'any' for now to match the dynamic result field access.
function getResourceNameFromOperationResponse(opResp: any): string | undefined {
    if (!opResp) return undefined;
    if (opResp.campaign_budget_result) return opResp.campaign_budget_result.resource_name;
    if (opResp.campaign_result) return opResp.campaign_result.resource_name;
    if (opResp.ad_group_result) return opResp.ad_group_result.resource_name;
    if (opResp.ad_group_criterion_result) return opResp.ad_group_criterion_result.resource_name;
    if (opResp.ad_group_ad_result) return opResp.ad_group_ad_result.resource_name;
    // Add other _result types as needed
    return undefined;
}

// --- Main Ad Posting Orchestration --- 

/**
 * Main function to orchestrate posting an ad to Google Ads using the client library.
 *
 * @param googleConnection Details of the stored Google connection (includes refreshToken, platformAccountId as target CID).
 * @param googleAdStructure Payloads from the google_translator (needs to be adapted for client library objects).
 * @param jobAdBudgetDaily The daily budget for the ad in the format of a string, number, or null.
 * @returns An object with resource names of created entities, or null if any step fails.
 */
export async function postAdToGoogle(
    googleConnection: Pick<SocialPlatformConnection, 'refreshToken' | 'platformAccountId'>, 
    googleAdStructure: GoogleFullAdStructure,
    jobAdBudgetDaily: string | number | null
): Promise<{ 
    campaignResourceName?: string; 
    campaignBudgetResourceName?: string;
    adGroupResourceName?: string; // Will be undefined in this test
    adResourceName?: string;    // Will be undefined in this test
    criteriaResourceNames?: string[]; // Will be empty in this test
} | null> {
    if (!googleConnection.refreshToken) {
        console.error('Google Ads: Refresh token missing from connection details.');
        return null;
    }
    if (!googleConnection.platformAccountId) {
        console.error('Google Ads: Target Customer ID (platformAccountId) missing from connection details.');
        return null;
    }
    if (!jobAdBudgetDaily) {
        console.error('Google Ads: Job ad daily budget missing.');
        return null;
    }

    const targetCustomerId = googleConnection.platformAccountId!.replace(/-/g, '');
    console.log(`Posting to Google Ads Customer ID: ${targetCustomerId} (Campaign & Budget ONLY TEST)`);

    try {
        const client = getGoogleAdsClient(googleConnection.refreshToken, targetCustomerId);

        const tempBudgetResourceName = ResourceNames.campaignBudget(targetCustomerId, "-1");
        const tempCampaignResourceName = ResourceNames.campaign(targetCustomerId, "-2");
        // const tempAdGroupResourceName = ResourceNames.adGroup(targetCustomerId, "-3"); // Not used in this test

        const operations: any[] = [];
        
        const budgetAmountMicros = toMicros(parseFloat(jobAdBudgetDaily as string));
        if (isNaN(budgetAmountMicros)) {
            console.error("Google Ads: Invalid budget amount after conversion to micros.");
            return null;
        }
        // 1. Campaign Budget Operation
        operations.push({
            entity: 'campaign_budget', operation: 'create', 
            resource: { 
                resource_name: tempBudgetResourceName, 
                name: googleAdStructure.campaignBudgetPayload.name,
                amount_micros: budgetAmountMicros,
                delivery_method: googleAdStructure.campaignBudgetPayload.delivery_method || enums.BudgetDeliveryMethod.STANDARD,
            }
        });

        // 2. Campaign Operation
        operations.push({
            entity: 'campaign', operation: 'create', 
            resource: { 
                resource_name: tempCampaignResourceName, 
                ...googleAdStructure.campaignPayload,
                campaign_budget: tempBudgetResourceName, 
            }
        });

        // --- Temporarily comment out AdGroup, Criteria, and Ad operations for initial testing ---
        /*
        operations.push({
            entity: 'ad_group', operation: 'create', 
            resource: { 
                resource_name: tempAdGroupResourceName, 
                ...googleAdStructure.adGroupPayload,
                campaign: tempCampaignResourceName, 
            }
        });
        if (googleAdStructure.adGroupCriteriaPayloads && googleAdStructure.adGroupCriteriaPayloads.length > 0) {
            googleAdStructure.adGroupCriteriaPayloads.forEach(criterionInstanceFromTranslator => {
                const criterionResourceLiteral = {
                    ...criterionInstanceFromTranslator, 
                    ad_group: tempAdGroupResourceName, 
                };
                delete (criterionResourceLiteral as any).resource_name; 
                operations.push({
                    entity: 'ad_group_criterion',
                    operation: 'create',
                    resource: criterionResourceLiteral 
                });
            });
        }
        const adGroupAdInstanceFromTranslator = googleAdStructure.adPayload;
        const adGroupAdResourceLiteral = {
            ...adGroupAdInstanceFromTranslator,
            ad_group: tempAdGroupResourceName,
        };
        delete (adGroupAdResourceLiteral as any).resource_name; 
        operations.push({
            entity: 'ad_group_ad', 
            operation: 'create', 
            resource: adGroupAdResourceLiteral
        });
        */

        console.log(`Submitting ${operations.length} operations to Google Ads API (Campaign & Budget ONLY TEST)...`);
        const mutateResponse = await client.mutateResources(operations, { partial_failure: true, validate_only: false });

        if (mutateResponse.partial_failure_error && mutateResponse.partial_failure_error.details) {
            console.warn("Google Ads: Partial failure occurred during mutate operation.");
            mutateResponse.partial_failure_error.details.forEach((detail: any) => {
                const opIndex = detail.path?.index || 0;
                const entityType = operations[opIndex]?.entity || 'unknown_entity';
                const fieldPath = detail.path?.field_name ? `${detail.path.field_name}` : 'N/A';
                console.error(`  Error for operation ${opIndex} (${entityType}) at path ${fieldPath}: ${detail.message}`);
            });
        }
        
        const responses = mutateResponse.mutate_operation_responses || [];
        const finalResults = {
            campaignBudgetResourceName: getResourceNameFromOperationResponse(responses[0]),
            campaignResourceName: getResourceNameFromOperationResponse(responses[1]),
            adGroupResourceName: undefined, // Not created in this test
            adResourceName: undefined,    // Not created in this test
            criteriaResourceNames: [],    // Not created in this test
        };

        console.log("Google Ads entities created/attempted (Campaign & Budget ONLY TEST):", finalResults);

        if (!finalResults.campaignBudgetResourceName || !finalResults.campaignResourceName) {
             console.error("Google Ads: Failed to create Campaign Budget or Campaign.");
             responses.forEach((opResponse: any, index: number) => {
                if (operations[index] && !getResourceNameFromOperationResponse(opResponse)) {
                    const entityType = operations[index].entity;
                    let specificError = 'Unknown error in operation response';
                    if (opResponse[`${entityType}_result`]?.partial_failure_error) {
                        specificError = opResponse[`${entityType}_result`].partial_failure_error.message;
                    } else if (opResponse.partial_failure_error) { // General partial failure for this op
                        specificError = opResponse.partial_failure_error.message;
                    }
                    console.error(`Operation ${index} (${entityType}) failed. Error:`, specificError, opResponse);
                }
             });
             return null;
        }
        return finalResults;

    } catch (error: any) {
        console.error("Error in postAdToGoogle (Campaign & Budget ONLY TEST) orchestration:", error.message);
        if (error.errors) console.error("Google Ads API Specific Errors:", JSON.stringify(error.errors, null, 2));
        return null;
    }
}

// TODOs from previous version are still highly relevant, especially:
// - Implement proper OAuth 2.0 flow for Google Ads (callback needs to store refresh_token & target Customer ID).
// - Refine google_translator.ts to produce objects matching google-ads-api library's resource structures.
// - Implement detailed targeting translation (GeoTargetConstants, Audience Segments).
// - Implement asset uploading for Display/Video ads via Google Ads AssetService.
// - Handle Google Ads API specific error codes and rate limits more gracefully. 