import { db } from '@/lib/db/drizzle';
import { jobAds, socialPlatformConnections, JobAd } from '@/lib/db/schema';
import { eq, and, lte, gte, isNull, or } from 'drizzle-orm';
import { mapAudiencePrimitivesToTargeting, PlatformAgnosticTargeting } from './taxonomy_mapper';
import { translateToMetaAd, MetaFullAdStructure } from './translators/meta_translator';
import { postAdToMeta } from './platform_apis/meta_ads_api';
import { decrypt } from '@/lib/security/crypto';
import { getTeamForUser } from '@/lib/db/queries';

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
        let successfullyPostedCount = 0;

        for (const ad of eligibleAds) {
            console.log(`Processing ad ID: ${ad.id}, Title: ${ad.title}`);
            let adProcessingStatus: JobAd['status'] = 'error_processing';
            let metaPostSuccessful = false;

            try {
                await db.update(jobAds).set({ status: 'processing', updatedAt: new Date() }).where(eq(jobAds.id, ad.id));

                const segmentationResult = await callPythonSegmentationService(ad.descriptionShort || ad.title);
                if (!segmentationResult || !segmentationResult.derived_audience_primitives) {
                    console.error(`Segmentation failed for ad ID: ${ad.id}.`);
                    adProcessingStatus = 'segmentation_failed';
                    await db.update(jobAds).set({ status: adProcessingStatus, updatedAt: new Date() }).where(eq(jobAds.id, ad.id));
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
                            const metaPayloads = translateToMetaAd(ad, mappedTargeting, undefined, undefined, undefined);

                            if (metaPayloads) {
                                const metaPostResult = await postAdToMeta(
                                    metaConnection.platformAccountId,
                                    metaPayloads,
                                    decryptedAccessToken,
                                    ad.creativeAssetUrl,
                                    {
                                        title: ad.title,
                                        descriptionShort: ad.descriptionShort || '',
                                        targetUrl: ad.targetUrl,
                                        videoThumbnailUrl: (ad as any).videoThumbnailUrl || null
                                    }
                                );
                                if (metaPostResult && metaPostResult.adId) {
                                    console.log(`Ad ID: ${ad.id} - Successfully posted to Meta. Meta Ad ID: ${metaPostResult.adId}`);
                                    metaPostSuccessful = true;
                                } else {
                                    console.error(`Ad ID: ${ad.id} - Failed to post to Meta.`);
                                }
                            } else {
                                console.error(`Ad ID: ${ad.id} - Failed to translate ad for Meta.`);
                            }
                        } catch (metaError) {
                            console.error(`Ad ID: ${ad.id} - Error during Meta posting process:`, metaError);
                        }
                    } else {
                        console.warn(`Ad ID: ${ad.id} - No active Meta connection found for team ${ad.teamId} or missing Ad Account ID.`);
                    }
                } else {
                    console.log(`Ad ID: ${ad.id} - Meta platform not enabled.`);
                }

                if (metaPostSuccessful) {
                    adProcessingStatus = 'live';
                    successfullyPostedCount++;
                } else if (ad.platformsMetaEnabled && !metaPostSuccessful) {
                    adProcessingStatus = 'post_failed_meta';
                } else {
                    adProcessingStatus = 'processed_no_platforms';
                }
                
                await db.update(jobAds).set({ status: adProcessingStatus, updatedAt: new Date() }).where(eq(jobAds.id, ad.id));
                console.log(`Ad ID: ${ad.id} finished processing. Status: ${adProcessingStatus}`);
                processedCount++;

            } catch (error) {
                console.error(`Unhandled error processing ad ID: ${ad.id}:`, error);
                await db.update(jobAds).set({ status: 'error_processing', updatedAt: new Date() }).where(eq(jobAds.id, ad.id));
            }
        }
        console.log('Finished processing scheduled ads.');
        return { message: `Attempted to process ${processedCount} ads. Successfully posted (to at least one platform, placeholder): ${successfullyPostedCount}.`, processedCount };

    } catch (error) {
        console.error('Error in processScheduledAds function:', error);
        return { error: 'Failed to query or process ads.', processedCount: 0 };
    }
} 