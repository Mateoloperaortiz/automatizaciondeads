import { db } from '@/lib/db/drizzle';
import { jobAds, socialPlatformConnections, JobAd } from '@/lib/db/schema';
import { eq, and, lte, gte, isNull, or } from 'drizzle-orm';
import { mapAudiencePrimitivesToTargeting, PlatformAgnosticTargeting } from './taxonomy_mapper';
import { translateToMetaAd } from './translators/meta_translator';
import { postAdToMeta, uploadMetaAdImageByUrl, uploadMetaAdVideoByUrl, fetchMetaVideoThumbnailUrl } from './platform_apis/meta_ads_api';
import { decrypt } from '@/lib/security/crypto';
import { getTeamForUser } from '@/lib/db/queries';

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
        let processedCount = 0;
        let successfullyPostedToAnyPlatformCount = 0;

        for (const ad of eligibleAds) {
            console.log(`Processing ad ID: ${ad.id}, Title: ${ad.title}`);
            let overallAdProcessingStatus: JobAd['status'] = 'error_processing';
            let postedToMeta = false;
            let metaAdPlatformId: string | null = null;
            let metaCampaignPlatformId: string | null = null;
            let metaAdSetPlatformId: string | null = null;

            const platformPostResults: Record<string, boolean> = {
                meta: false,
                x: false,
                google: false,
            };
            const platformAdIds: Partial<Pick<JobAd, 'metaCampaignId' | 'metaAdSetId' | 'metaAdId' | 'xCampaignId' | 'xLineItemId' | 'xPromotedTweetId' | 'googleCampaignResourceId' | 'googleAdGroupResourceId' | 'googleAdResourceId'> > = {};

            try {
                await db.update(jobAds).set({ status: 'processing', updatedAt: new Date() }).where(eq(jobAds.id, ad.id));

                const segmentationResult = await callPythonSegmentationService(ad.descriptionShort || ad.title);
                if (!segmentationResult || !segmentationResult.derived_audience_primitives) {
                    console.error(`Segmentation failed for ad ID: ${ad.id}.`);
                    overallAdProcessingStatus = 'segmentation_failed';
                    await db.update(jobAds).set({ status: overallAdProcessingStatus, updatedAt: new Date() }).where(eq(jobAds.id, ad.id));
                    continue;
                }

                const mappedTargeting = mapAudiencePrimitivesToTargeting(
                    segmentationResult.derived_audience_primitives,
                    segmentationResult.cluster_assignment_confidence
                );
                console.log(`Ad ID: ${ad.id} - Mapped Targeting:`, mappedTargeting);

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
                                console.log(`Ad ID: ${ad.id} - Creative asset URL provided, attempting image upload: ${ad.creativeAssetUrl}`);
                                imageHashForTranslator = await uploadMetaAdImageByUrl(
                                    metaConnection.platformAccountId, 
                                    ad.creativeAssetUrl, 
                                    decryptedAccessToken
                                );
                                if (imageHashForTranslator) {
                                    console.log(`Ad ID: ${ad.id} - Image uploaded to Meta, hash: ${imageHashForTranslator}`);
                                } else {
                                    console.warn(`Ad ID: ${ad.id} - Failed to upload image to Meta. Ad will be created without image if possible.`);
                                }
                            }

                            const metaPayloads = translateToMetaAd(
                                ad, 
                                mappedTargeting, 
                                imageHashForTranslator
                            );

                            if (metaPayloads) {
                                const metaPostResult = await postAdToMeta(
                                    metaConnection.platformAccountId, 
                                    metaPayloads,
                                    decryptedAccessToken
                                );
                                if (metaPostResult && metaPostResult.adId) {
                                    console.log(`Ad ID: ${ad.id} - Successfully posted to Meta. Meta Ad ID: ${metaPostResult.adId}`);
                                    postedToMeta = true;
                                    metaAdPlatformId = metaPostResult.adId;
                                    metaCampaignPlatformId = metaPostResult.campaignId;
                                    metaAdSetPlatformId = metaPostResult.adSetId;
                                    platformPostResults.meta = true;
                                    platformAdIds.metaCampaignId = metaPostResult.campaignId;
                                    platformAdIds.metaAdSetId = metaPostResult.adSetId;
                                    platformAdIds.metaAdId = metaPostResult.adId;
                                } else {
                                    console.error(`Ad ID: ${ad.id} - Failed to post to Meta (postAdToMeta returned null/error).`);
                                }
                            } else {
                                console.error(`Ad ID: ${ad.id} - Failed to translate ad for Meta.`);
                            }
                        } catch (metaError) {
                            console.error(`Ad ID: ${ad.id} - Error during Meta posting process:`, metaError);
                        }
                    } else {
                        console.warn(`Ad ID: ${ad.id} - No active Meta connection or Ad Account ID for team ${ad.teamId}.`);
                    }
                } else {
                    console.log(`Ad ID: ${ad.id} - Meta platform not enabled.`);
                }

                if (ad.platformsXEnabled) {
                    console.log(`Ad ID: ${ad.id} - Attempting X post...`);
                    const xConnection = await db.query.socialPlatformConnections.findFirst({
                        where: and(eq(socialPlatformConnections.teamId, ad.teamId), eq(socialPlatformConnections.platformName, 'x'), eq(socialPlatformConnections.status, 'active'))
                    });
                    const xAdsAppAccountId = process.env.X_ADS_ACCOUNT_ID; // App-wide Ad Account ID
                    const xAppUserAccessToken = process.env.X_USER_ACCESS_TOKEN;
                    const xAppUserTokenSecret = process.env.X_USER_ACCESS_TOKEN_SECRET;

                    if (xConnection && xAdsAppAccountId && xAppUserAccessToken && xAppUserTokenSecret && xConnection.fundingInstrumentId) {
                        try {
                            // For X, translator needs fundingInstrumentId
                            const xPayloads = translateToXAd(ad, mappedTargeting, xConnection.fundingInstrumentId);
                            if (xPayloads) {
                                const result = await postAdToX(xAdsAppAccountId, xPayloads, xAppUserAccessToken, xAppUserTokenSecret, ad);
                                if (result?.lineItemId) { // lineItemId is a key indicator of success for X
                                    console.log(`Ad ID: ${ad.id} - Successfully posted to X. X Campaign ID: ${result.campaignId}, X Line Item ID: ${result.lineItemId}`);
                                    platformPostResults.x = true;
                                    platformAdIds.xCampaignId = result.campaignId;
                                    platformAdIds.xLineItemId = result.lineItemId;
                                    platformAdIds.xPromotedTweetId = result.promotedTweetId;
                                }
                            }
                        } catch (e) { console.error(`Ad ID: ${ad.id} - Error in X post:`, e); }
                    } else console.warn(`Ad ID: ${ad.id} - X Ads prerequisites not met (connection, fundingID, or app credentials/AdAccountID in .env).`);
                }

                if (ad.platformsGoogleEnabled) {
                    console.log(`Ad ID: ${ad.id} - Attempting Google Ads post...`);
                    const googleConnection = await db.query.socialPlatformConnections.findFirst({
                        where: and(eq(socialPlatformConnections.teamId, ad.teamId), eq(socialPlatformConnections.platformName, 'google'), eq(socialPlatformConnections.status, 'active'))
                    });
                    const googleDeveloperToken = process.env.GOOGLE_DEVELOPER_TOKEN;
                    const googleLoginCustomerId = process.env.GOOGLE_LOGIN_CUSTOMER_ID; // MCC

                    if (googleConnection?.refreshToken && googleConnection.platformAccountId && googleDeveloperToken) {
                        try {
                            const decryptedRefreshToken = decrypt(googleConnection.refreshToken); // Assuming refresh token is encrypted
                            const googlePayloads = translateToGoogleAd(ad, mappedTargeting);
                            if (googlePayloads) {
                                const result = await postAdToGoogle(
                                    { refreshToken: decryptedRefreshToken, platformAccountId: googleConnection.platformAccountId }, 
                                    googlePayloads
                                );
                                if (result?.adResourceName) {
                                    console.log(`Ad ID: ${ad.id} - Successfully posted to Google Ads. Google Campaign Resource ID: ${result.campaignResourceName}, Google Ad Group Resource ID: ${result.adGroupResourceName}, Google Ad Resource ID: ${result.adResourceName}`);
                                    platformPostResults.google = true;
                                    platformAdIds.googleCampaignResourceId = result.campaignResourceName;
                                    platformAdIds.googleAdGroupResourceId = result.adGroupResourceName;
                                    platformAdIds.googleAdResourceId = result.adResourceName;
                                }
                            }
                        } catch (e) { console.error(`Ad ID: ${ad.id} - Error in Google Ads post:`, e); }
                    } else console.warn(`Ad ID: ${ad.id} - Google Ads prerequisites not met (connection/refreshToken, platformAccountID, or developer token).`);
                }

                const platformsAttempted = (ad.platformsMetaEnabled ? 1:0) + (ad.platformsXEnabled ? 1:0) + (ad.platformsGoogleEnabled ? 1:0);
                const platformsSucceeded = (platformPostResults.meta ? 1:0) + (platformPostResults.x ? 1:0) + (platformPostResults.google ? 1:0);

                if (platformsSucceeded > 0) {
                    successfullyPostedToAnyPlatformCount++;
                    if (platformsSucceeded === platformsAttempted && platformsAttempted > 0) {
                        overallAdProcessingStatus = 'live';
                    } else if (platformsAttempted > 0) {
                        overallAdProcessingStatus = 'partially_live';
                    } else {
                        overallAdProcessingStatus = 'processed_no_platforms';
                    }
                } else if (platformsAttempted > 0) {
                    overallAdProcessingStatus = 'post_failed_all';
                } else {
                    overallAdProcessingStatus = 'processed_no_platforms';
                }
                
                await db.update(jobAds).set({
                    status: overallAdProcessingStatus, 
                    ...platformAdIds,
                    metaCampaignId: metaCampaignPlatformId,
                    metaAdSetId: metaAdSetPlatformId,
                    metaAdId: metaAdPlatformId,
                    updatedAt: new Date() 
                }).where(eq(jobAds.id, ad.id));
                
                console.log(`Ad ID: ${ad.id} finished processing. Final status: ${overallAdProcessingStatus}`);
                processedCount++;

            } catch (error) {
                console.error(`Unhandled error processing ad ID: ${ad.id}:`, error);
                await db.update(jobAds).set({ status: 'error_processing', updatedAt: new Date() }).where(eq(jobAds.id, ad.id));
            }
        }
        console.log('Finished processing scheduled ads.');
        return { message: `Attempted to process ${processedCount} ads. Successfully posted (to at least one platform): ${successfullyPostedToAnyPlatformCount}.`, processedCount };

    } catch (error) {
        console.error('Error in processScheduledAds function:', error);
        return { error: 'Failed to query or process ads.', processedCount: 0 };
    }
} 