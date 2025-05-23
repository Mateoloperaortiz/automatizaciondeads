import { db } from '@/lib/db/drizzle';
import { jobAds, socialPlatformConnections, JobAd } from '@/lib/db/schema';
import { eq, and, lte, gte, isNull, or } from 'drizzle-orm';
import { mapAudiencePrimitivesToTargeting, PlatformAgnosticTargeting } from './taxonomy_mapper';
import { translateToMetaAd } from './translators/meta_translator';
import { postAdToMeta, uploadMetaAdImageByUrl } from './platform_apis/meta_ads_api';
import { decrypt } from '@/lib/security/crypto';
// import { getTeamForUser } from '@/lib/db/queries'; // Not directly used in this file
import { TEST_ACCOUNTS_ONLY } from '@/lib/config';

// X (Twitter) Imports
import { translateToXAd } from './translators/x_translator';
import { postAdToX } from './platform_apis/x_ads_api';

// Google Ads Imports
import { translateToGoogleAd } from './translators/google_translator';
import { postAdToGoogle } from './platform_apis/google_ads_api';

interface AudiencePrimitive {
    category: string;
    value: string;
    confidence?: number;
}

interface PythonSegmentationResponse {
    derived_audience_primitives: AudiencePrimitive[];
    assigned_cluster_id?: string;
    cluster_assignment_confidence?: number;
}

// Add interface for cluster profiles
interface ClusterProfile {
    name: string;
    industry?: string;
    skills?: string[];
    seniority?: string;
    keywords?: string[];
}

// Cache for cluster profiles
let clusterProfilesCache: Record<string, ClusterProfile> | null = null;

async function loadClusterProfiles(): Promise<Record<string, ClusterProfile>> {
    if (clusterProfilesCache) {
        return clusterProfilesCache;
    }
    
    try {
        const fs = await import('fs').then(m => m.promises);
        const path = await import('path');
        const profilesPath = path.join(process.cwd(), 'services/audience_segmentation_service/models/cluster_profiles.json');
        const profilesData = await fs.readFile(profilesPath, 'utf-8');
        clusterProfilesCache = JSON.parse(profilesData);
        console.log('Loaded cluster profiles:', Object.keys(clusterProfilesCache || {}));
        return clusterProfilesCache || {};
    } catch (error) {
        console.error('Failed to load cluster profiles:', error);
        return {};
    }
}

async function callPythonSegmentationService(jobAdText: string): Promise<PythonSegmentationResponse | null> {
    const serviceUrl = process.env.PYTHON_SEGMENTATION_SERVICE_URL;
    if (!serviceUrl) {
        console.error("PYTHON_SEGMENTATION_SERVICE_URL is not set.");
        return null;
    }
    try {
        console.log(`Calling Python service for ad text: ${jobAdText.substring(0, 50)}...`);
        const response = await fetch(serviceUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_ad_text: jobAdText }),
        });
        if (!response.ok) {
            console.error(`Python service call failed with status ${response.status}:`, await response.text());
            return null;
        }
        const data = await response.json();
        console.log("Received from Python service:", data);
        return data as PythonSegmentationResponse;
    } catch (error) {
        console.error("Error calling Python segmentation service:", error);
        return null;
    }
}

export async function processScheduledAds() {
    console.log('Starting to process scheduled ads...');
    const now = new Date();
    let adsAttemptedInLoop = 0;
    let adsSuccessfullyPostedToAnyPlatform = 0;

    try {
        const eligibleAds = await db
            .select()
            .from(jobAds)
            .where(
                and(
                    eq(jobAds.status, 'scheduled'),
                    lte(jobAds.scheduleStart, now),
                    or(
                        isNull(jobAds.scheduleEnd),
                        gte(jobAds.scheduleEnd, now)
                    )
                )
            );

        if (eligibleAds.length === 0) {
            console.log('No eligible scheduled ads found at this time.');
            return { message: 'No eligible ads to process.', processedCount: 0 };
        }

        console.log(`Found ${eligibleAds.length} eligible ad(s) to process.`);

        for (const ad of eligibleAds) {
            adsAttemptedInLoop++;
            console.log(`Processing ad ID: ${ad.id}, Title: ${ad.title} (Attempt ${adsAttemptedInLoop} of ${eligibleAds.length})`);
            
            let overallAdStatusForDb: JobAd['status'] = 'error_processing'; // Default status if anything goes wrong early
            const platformPostSuccess: Record<string, boolean> = { meta: false, x: false, google: false };
            const platformAdIdsToStore: Partial<Pick<JobAd, 'metaCampaignId' | 'metaAdSetId' | 'metaAdId' | 'xCampaignId' | 'xLineItemId' | 'xPromotedTweetId' | 'googleCampaignResourceId' | 'googleAdGroupResourceId' | 'googleAdResourceId'>> = {};

            try {
                await db.update(jobAds).set({ status: 'processing', updatedAt: new Date() }).where(eq(jobAds.id, ad.id));

                const segmentationResult = await callPythonSegmentationService(ad.descriptionShort || ad.title);
                
                if (!segmentationResult || !segmentationResult.derived_audience_primitives) {
                    console.error(`Segmentation failed for ad ID: ${ad.id}.`);
                    overallAdStatusForDb = 'segmentation_failed';
                } else {
                    // Store segmentation results first
                    const segmentationDataToStore: Partial<JobAd> = {
                        derivedAudiencePrimitives: segmentationResult.derived_audience_primitives as any,
                        audienceClusterId: segmentationResult.assigned_cluster_id || null,
                        audienceConfidence: segmentationResult.cluster_assignment_confidence?.toString() || null,
                        segmentationProcessedAt: new Date(),
                    };

                    let mappedTargeting: PlatformAgnosticTargeting;
                    const CONFIDENCE_THRESHOLD = 0.25; // As per ADS_AUTOMATION_PLAN.md

                    if (segmentationResult.cluster_assignment_confidence !== undefined && 
                        segmentationResult.cluster_assignment_confidence < CONFIDENCE_THRESHOLD) {
                        
                        console.warn(`Ad ID: ${ad.id} - Segmentation confidence (${segmentationResult.cluster_assignment_confidence}) is below threshold (${CONFIDENCE_THRESHOLD}). Falling back to broad targeting.`);
                        // For broad targeting, we might pass minimal or no specific primitives,
                        // relying on the job ad text itself for keyword generation in translators,
                        // and perhaps only very broad location targeting if available directly from the job ad.
                        // Or, define a default set of broad primitives.
                        // For simplicity, let's assume mapAudiencePrimitivesToTargeting can handle empty derived_audience_primitives
                        // and will produce a "broad" PlatformAgnosticTargeting object.
                        // Alternatively, create a specific "broad" PlatformAgnosticTargeting here.
                        // Let's opt for creating a default broad targeting object directly.
                        mappedTargeting = {
                            locations: [], // Or a default broad location if applicable from ad.location or team settings
                            skillKeywords: [], // Rely on ad title/description for keywords in translators
                            industries: [],
                            seniority: [],
                            // Potentially other fields set to broad defaults
                        };
                        // We could also pass an empty array to mapAudiencePrimitivesToTargeting if it's designed to handle it:
                        // mappedTargeting = mapAudiencePrimitivesToTargeting([], 0); 
                    } else {
                        console.log(`Ad ID: ${ad.id} - Segmentation confidence (${segmentationResult.cluster_assignment_confidence ?? 'N/A'}) met or exceeded threshold / not applicable.`);
                        mappedTargeting = mapAudiencePrimitivesToTargeting(
                            segmentationResult.derived_audience_primitives,
                            segmentationResult.cluster_assignment_confidence
                        );
                    }
                    console.log(`Ad ID: ${ad.id} - Final Mapped Targeting:`, mappedTargeting);

                    // Store the mapped targeting and get cluster profile name
                    segmentationDataToStore.mappedTargeting = mappedTargeting as any;
                    
                    // Get cluster profile name from the segmentation result or derive it
                    if (segmentationResult.assigned_cluster_id) {
                        const clusterProfiles = await loadClusterProfiles();
                        const profile = clusterProfiles[segmentationResult.assigned_cluster_id];
                        segmentationDataToStore.audienceClusterProfileName = profile?.name || `Cluster ${segmentationResult.assigned_cluster_id}`;
                    }

                    // Save segmentation data to database
                    await db.update(jobAds).set({
                        ...segmentationDataToStore,
                        updatedAt: new Date()
                    }).where(eq(jobAds.id, ad.id));
                    console.log(`Ad ID: ${ad.id} - Segmentation results saved to database.`);

                    // Meta Platform Logic
                    if (ad.platformsMetaEnabled) {
                        console.log(`Ad ID: ${ad.id} - Attempting to post to Meta...`);
                        const metaConnection = await db.query.socialPlatformConnections.findFirst({
                            where: and(
                                eq(socialPlatformConnections.teamId, ad.teamId),
                                eq(socialPlatformConnections.platformName, 'meta'),
                                eq(socialPlatformConnections.status, 'active')
                            )
                        });

                        if (metaConnection && metaConnection.accessToken && metaConnection.platformAccountId) {
                            try {
                                const decryptedAccessToken = decrypt(metaConnection.accessToken);
                                let imageHashForTranslator: string | undefined = undefined;
                                if (ad.creativeAssetUrl) {
                                    imageHashForTranslator = (await uploadMetaAdImageByUrl(
                                        metaConnection.platformAccountId,
                                        ad.creativeAssetUrl,
                                        decryptedAccessToken
                                    )) || undefined;
                                    if (imageHashForTranslator) console.log(`Ad ID: ${ad.id} - Image uploaded to Meta, hash: ${imageHashForTranslator}`);
                                    else console.warn(`Ad ID: ${ad.id} - Failed to upload image to Meta.`);
                                }
                                const metaPayloads = translateToMetaAd(ad, mappedTargeting, imageHashForTranslator);
                                if (metaPayloads) {
                                    const metaPostResult = await postAdToMeta(metaConnection.platformAccountId, metaPayloads, decryptedAccessToken);
                                    if (metaPostResult && metaPostResult.adId) {
                                        console.log(`Ad ID: ${ad.id} - Successfully posted to Meta. Meta Ad ID: ${metaPostResult.adId}`);
                                        platformPostSuccess.meta = true;
                                        platformAdIdsToStore.metaCampaignId = metaPostResult.campaignId;
                                        platformAdIdsToStore.metaAdSetId = metaPostResult.adSetId;
                                        platformAdIdsToStore.metaAdId = metaPostResult.adId;
                                    } else console.error(`Ad ID: ${ad.id} - Failed to post to Meta.`);
                                } else console.error(`Ad ID: ${ad.id} - Failed to translate ad for Meta.`);
                            } catch (metaError) { console.error(`Ad ID: ${ad.id} - Error during Meta posting:`, metaError); }
                        } else console.warn(`Ad ID: ${ad.id} - No active Meta connection for team ${ad.teamId}.`);
                    } else console.log(`Ad ID: ${ad.id} - Meta platform not enabled.`);

                    // X (Twitter) Platform Logic
                    if (ad.platformsXEnabled) {
                        console.log(`Ad ID: ${ad.id} - Attempting to post to X Ads...`);
                        const xConnection = await db.query.socialPlatformConnections.findFirst({
                            where: and(eq(socialPlatformConnections.teamId, ad.teamId), eq(socialPlatformConnections.platformName, 'x'), eq(socialPlatformConnections.status, 'active'))
                        });
                        const xAdsAppAccountId = process.env.X_ADS_ACCOUNT_ID;
                        const xAppUserAccessToken = process.env.X_USER_ACCESS_TOKEN;
                        const xAppUserTokenSecret = process.env.X_USER_ACCESS_TOKEN_SECRET;
                        const fundingIdForTranslator = xConnection?.fundingInstrumentId || undefined;

                        if (xConnection && xAdsAppAccountId && xAppUserAccessToken && xAppUserTokenSecret && fundingIdForTranslator) {
                            try {
                                const xPayloads = translateToXAd(ad, mappedTargeting, fundingIdForTranslator);
                                if (xPayloads) {
                                    const xPostResult = await postAdToX(xAdsAppAccountId, xPayloads, xAppUserAccessToken, xAppUserTokenSecret, ad);
                                    if (xPostResult && xPostResult.lineItemId) {
                                        console.log(`Ad ID: ${ad.id} - Successfully posted to X. X LineItem ID: ${xPostResult.lineItemId}`);
                                        platformPostSuccess.x = true;
                                        platformAdIdsToStore.xCampaignId = xPostResult.campaignId;
                                        platformAdIdsToStore.xLineItemId = xPostResult.lineItemId;
                                        platformAdIdsToStore.xPromotedTweetId = xPostResult.promotedTweetId;
                                    } else console.error(`Ad ID: ${ad.id} - Failed to post to X.`);
                                } else console.error(`Ad ID: ${ad.id} - Failed to translate ad for X.`);
                            } catch (xError) { console.error(`Ad ID: ${ad.id} - Error during X posting:`, xError); }
                        } else console.warn(`Ad ID: ${ad.id} - X Ads prerequisites not met.`);
                    } else console.log(`Ad ID: ${ad.id} - X platform not enabled.`);

                    // Google Ads Platform Logic
                    if (ad.platformsGoogleEnabled) {
                        console.log(`Ad ID: ${ad.id} - Attempting to post to Google Ads...`);
                        const googleConnection = await db.query.socialPlatformConnections.findFirst({
                            where: and(eq(socialPlatformConnections.teamId, ad.teamId), eq(socialPlatformConnections.platformName, 'google'), eq(socialPlatformConnections.status, 'active'))
                        });
                        if (googleConnection && googleConnection.refreshToken && googleConnection.platformAccountId) {
                            try {
                                const decryptedRefreshToken = decrypt(googleConnection.refreshToken);
                                const googlePayloads = translateToGoogleAd(ad, mappedTargeting);
                                if (googlePayloads) {
                                    const googlePostResult = await postAdToGoogle(
                                        { refreshToken: decryptedRefreshToken, platformAccountId: googleConnection.platformAccountId },
                                        googlePayloads,
                                        ad.budgetDaily
                                    );
                                    if (googlePostResult && googlePostResult.campaignResourceName) {
                                        console.log(`Ad ID: ${ad.id} - Successfully posted to Google Ads. Google Campaign: ${googlePostResult.campaignResourceName}`);
                                        platformPostSuccess.google = true;
                                        platformAdIdsToStore.googleCampaignResourceId = googlePostResult.campaignResourceName;
                                        // platformAdIdsToStore.googleAdGroupResourceId = googlePostResult.adGroupResourceName; // If/when returned
                                        // platformAdIdsToStore.googleAdResourceId = googlePostResult.adResourceName; // If/when returned
                                    } else console.error(`Ad ID: ${ad.id} - Failed to post to Google Ads.`);
                                } else console.error(`Ad ID: ${ad.id} - Failed to translate ad for Google Ads.`);
                            } catch (googleError) { console.error(`Ad ID: ${ad.id} - Error during Google Ads posting:`, googleError); }
                        } else console.warn(`Ad ID: ${ad.id} - Google Ads prerequisites not met.`);
                    } else console.log(`Ad ID: ${ad.id} - Google platform not enabled.`);
                } // End of if segmentationResult was successful

                // Determine overall status based on platform successes
                if (overallAdStatusForDb !== 'segmentation_failed') { 
                    // This block executes if segmentation was successful OR if overallAdStatusForDb is still 'error_processing' (initial default)
                    const platformsAttemptedCount = [ad.platformsMetaEnabled, ad.platformsXEnabled, ad.platformsGoogleEnabled].filter(Boolean).length;
                    const platformsSucceededCount = Object.values(platformPostSuccess).filter(Boolean).length;

                    if (platformsAttemptedCount === 0) {
                        overallAdStatusForDb = 'processed_no_platforms';
                    } else if (platformsSucceededCount === platformsAttemptedCount) {
                        overallAdStatusForDb = 'live';
                    } else if (platformsSucceededCount > 0) {
                        overallAdStatusForDb = 'partially_live';
                    } else { // platformsAttemptedCount > 0 but platformsSucceededCount === 0
                        overallAdStatusForDb = 'post_failed_all';
                    }
                }
                // If overallAdStatusForDb was 'segmentation_failed', it remains so.
                // If it was 'error_processing' initially and segmentation succeeded, the above block sets a more specific status.

                await db.update(jobAds).set({
                    status: overallAdStatusForDb,
                    ...platformAdIdsToStore,
                    updatedAt: new Date()
                }).where(eq(jobAds.id, ad.id));
                
                if (overallAdStatusForDb === 'live' || overallAdStatusForDb === 'partially_live') {
                    adsSuccessfullyPostedToAnyPlatform++;
                }
                console.log(`Ad ID: ${ad.id} final status: ${overallAdStatusForDb}`);

            } catch (error) {
                console.error(`Unhandled error processing ad ID ${ad.id}:`, error);
                // Ensure status is updated to error_processing if an unhandled exception occurs in the try block
                await db.update(jobAds).set({ status: 'error_processing', updatedAt: new Date() }).where(eq(jobAds.id, ad.id));
            }
        }
        console.log('Finished processing ads.');
        return { message: `Attempted to process ${adsAttemptedInLoop} ads. Successfully posted to at least one platform: ${adsSuccessfullyPostedToAnyPlatform}.`, processedCount: adsAttemptedInLoop };

    } catch (error) {
        console.error('Error in processScheduledAds main try-catch:', error);
        return { error: 'Failed to query/process ads due to a top-level error.', processedCount: 0 };
    }
}
