// test-meta-image-upload.ts
import { config } from 'dotenv';
config({ path: '.env' }); // Load .env variables

import { 
    uploadMetaAdImageByUrl 
} from './lib/automation/platform_apis/meta_ads_api'; // Adjust path as needed

async function testImageUploadWorkflow() {
    const adAccountId = process.env.TEST_META_AD_ACCOUNT_ID;
    const accessToken = process.env.TEST_META_USER_ACCESS_TOKEN; 
    const imageUrl = process.env.TEST_IMAGE_URL; // You'll need to add this to your .env

    if (!adAccountId || !accessToken || !imageUrl) {
        console.error(
            'Please ensure TEST_META_AD_ACCOUNT_ID, TEST_META_USER_ACCESS_TOKEN, and TEST_IMAGE_URL are set in your .env file. \n' +
            'TEST_IMAGE_URL should be a real, publicly accessible URL to a test image (e.g., JPG, PNG).'
        );
        return;
    }

    console.log(`--- Test Parameters for Image Upload ---`);
    console.log(`Ad Account ID: ${adAccountId}`);
    console.log(`Access Token: ${accessToken ? accessToken.substring(0, 15) + '...' : 'Not Set'}`);
    console.log(`Image URL: ${imageUrl}`);
    console.log(`---------------------------------------`);

    console.log("\n--- Starting Image Upload Test ---");
    const imageHash = await uploadMetaAdImageByUrl(
        adAccountId,
        imageUrl,
        accessToken
    );

    if (imageHash) {
        console.log(`SUCCESS: Image uploaded. Image Hash: ${imageHash}`);
        // Here, you would typically proceed to use this imageHash to create an ad creative
        // For example, pass it to translateToMetaAd and then postAdToMeta
        console.log("Next step would be to use this hash in an ad creative payload.");
    } else {
        console.error("ERROR: Image upload failed. No image hash obtained.");
    }
}

testImageUploadWorkflow().catch(err => {
    console.error("Unhandled error in testImageUploadWorkflow:", err);
}); 