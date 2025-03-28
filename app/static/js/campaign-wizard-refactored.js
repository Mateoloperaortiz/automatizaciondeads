/**
 * Campaign Creation Wizard
 * Handles campaign creation UI and API interactions using service layer
 */

// Import services
import { campaignService } from './services/index.js';

// Store campaign data for submission
let campaignData = {
    title: '',
    description: '',
    platform_ids: [],
    job_opening_ids: [],
    segment_ids: [],
    budget: 0,
    start_date: '',
    end_date: '',
    ad_headline: '',
    ad_text: '',
    ad_cta: '',
    ad_image_url: '',
    platform_specific: {}
};

// Initialize on document ready
document.addEventListener('DOMContentLoaded', function() {
    // Form submission handler
    const submitForm = document.getElementById('campaign-submit');
    if (submitForm) {
        submitForm.addEventListener('click', handleCampaignSubmit);
    }
    
    // Initialize image upload handler
    initImageUploader();
});

/**
 * Initialize image upload handling
 */
function initImageUploader() {
    const imageUploader = document.getElementById('ad-image');
    if (!imageUploader) return;
    
    imageUploader.addEventListener('change', async function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        try {
            // Show loading state
            showUploadingState();
            
            // Using our service layer for uploading
            const data = await campaignService.uploadCampaignImage(file, updateProgressBar);
            
            if (data.success) {
                // Save image URL to campaign data
                campaignData.ad_image_url = data.url;
                
                // Update UI
                document.querySelectorAll('.preview-image img, .tweet-image img').forEach(img => {
                    img.src = data.url;
                });
                
                hideUploadingState();
                showToast('Image uploaded successfully', 'success');
            } else {
                hideUploadingState();
                showToast('Failed to upload image', 'error');
            }
        } catch (error) {
            console.error('Error captured by service layer:', error);
            hideUploadingState();
        }
    });
}

/**
 * Update progress bar during upload
 * @param {number} percent - Upload progress percentage
 */
function updateProgressBar(percent) {
    const uploadPlaceholder = document.querySelector('.upload-placeholder');
    if (uploadPlaceholder) {
        uploadPlaceholder.innerHTML = `
            <div class="progress">
                <div class="progress-bar" style="width: ${percent}%"></div>
            </div>
            <span>Uploading image... ${Math.round(percent)}%</span>
        `;
    }
}

/**
 * Show uploading state in the UI
 */
function showUploadingState() {
    const uploadPlaceholder = document.querySelector('.upload-placeholder');
    if (uploadPlaceholder) {
        uploadPlaceholder.innerHTML = `
            <div class="spinner"></div>
            <span>Uploading image...</span>
        `;
    }
}

/**
 * Hide uploading state in the UI
 */
function hideUploadingState() {
    const uploadPlaceholder = document.querySelector('.upload-placeholder');
    const mediaPreview = document.querySelector('.media-preview');
    
    if (uploadPlaceholder) {
        uploadPlaceholder.style.display = 'none';
    }
    
    if (mediaPreview) {
        mediaPreview.style.display = 'block';
    }
}

/**
 * Collect all form data into the campaignData object
 */
function collectFormData() {
    // Basic information
    campaignData.title = document.getElementById('campaign-name').value;
    campaignData.description = document.getElementById('campaign-description').value;
    campaignData.start_date = document.getElementById('start-date').value;
    campaignData.end_date = document.getElementById('end-date').value;
    campaignData.budget = parseFloat(document.getElementById('campaign-budget').value);
    
    // Platforms
    campaignData.platform_ids = [];
    document.querySelectorAll('.platform-option input:checked').forEach(platform => {
        const platformId = platform.id.replace('platform-', '');
        campaignData.platform_ids.push(platformId);
    });
    
    // Segments
    campaignData.segment_ids = [];
    document.querySelectorAll('.segment-card.selected').forEach(segment => {
        const segmentId = segment.getAttribute('data-segment-id');
        if (segmentId) campaignData.segment_ids.push(parseInt(segmentId));
    });
    
    // Jobs
    campaignData.job_opening_ids = [];
    document.querySelectorAll('.selected-job-item').forEach(job => {
        const jobId = job.getAttribute('data-job-id');
        if (jobId) campaignData.job_opening_ids.push(parseInt(jobId));
    });
    
    // Ad content
    campaignData.ad_headline = document.getElementById('ad-headline').value;
    campaignData.ad_text = document.getElementById('ad-text').value;
    campaignData.ad_cta = document.getElementById('ad-cta').value;
    
    // Platform-specific content
    collectPlatformSpecificContent();
}

/**
 * Collect platform-specific content settings
 */
function collectPlatformSpecificContent() {
    // Meta specifics
    if (campaignData.platform_ids.includes('meta')) {
        campaignData.platform_specific.meta = {
            headline: campaignData.ad_headline,
            text: campaignData.ad_text,
            cta: campaignData.ad_cta,
            image_url: campaignData.ad_image_url
        };
    }
    
    // Google specifics
    if (campaignData.platform_ids.includes('google')) {
        campaignData.platform_specific.google = {
            headline: campaignData.ad_headline.substring(0, 30),
            description_line1: campaignData.ad_text.substring(0, 90),
            description_line2: campaignData.ad_text.length > 90 ? 
                campaignData.ad_text.substring(90, 180) : '',
            final_url: 'https://www.magneto365.com/job/' + campaignData.job_opening_ids[0]
        };
    }
    
    // Twitter specifics
    if (campaignData.platform_ids.includes('x')) {
        campaignData.platform_specific.twitter = {
            tweet_text: `${campaignData.ad_headline}: ${campaignData.ad_text.substring(0, 180)}... #JobOpening #Hiring`,
            image_url: campaignData.ad_image_url,
            website_url: 'https://www.magneto365.com/job/' + campaignData.job_opening_ids[0]
        };
    }
}

/**
 * Handle campaign form submission using service layer
 */
async function handleCampaignSubmit(e) {
    e.preventDefault();
    
    // Collect all form data
    collectFormData();
    
    // Using service layer validation
    const validation = campaignService.validateCampaignData(campaignData);
    if (!validation.valid) {
        showToast(validation.errors[0], 'error');
        return;
    }
    
    try {
        // Show loading state
        showLoadingState();
        
        // Prepare data for API
        const apiData = {
            title: campaignData.title,
            description: campaignData.description,
            platform_id: parseInt(campaignData.platform_ids[0]), // Primary platform
            job_opening_id: campaignData.job_opening_ids[0],    // Primary job
            segment_id: campaignData.segment_ids.length > 0 ? campaignData.segment_ids[0] : null,
            budget: campaignData.budget,
            
            // Enhanced ad content fields
            ad_headline: campaignData.ad_headline,
            ad_text: campaignData.ad_text,
            ad_cta: campaignData.ad_cta,
            ad_image_url: campaignData.ad_image_url,
            platform_specific: campaignData.platform_specific
        };
        
        // Using service layer to create campaign
        const data = await campaignService.createCampaign(apiData);
        
        if (data.success) {
            // Hide loading state
            hideLoadingState();
            
            // Show success and redirect
            showToast('Campaign created successfully!', 'success');
            
            // Redirect to campaign detail page after a delay
            setTimeout(() => {
                window.location.href = `/campaigns/${data.data.id}`;
            }, 1500);
        } else {
            // This should be handled by the error handler, but just in case
            hideLoadingState();
            showToast('Failed to create campaign: ' + (data.message || 'Unknown error'), 'error');
        }
    } catch (error) {
        // The service layer will handle this error, but we need to update UI
        hideLoadingState();
    }
}

/**
 * Show loading state during API calls
 */
function showLoadingState() {
    // Disable submit button
    const submitBtn = document.getElementById('campaign-submit');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<div class="spinner-sm"></div> Creating Campaign...`;
    }
}

/**
 * Hide loading state after API calls
 */
function hideLoadingState() {
    // Re-enable submit button
    const submitBtn = document.getElementById('campaign-submit');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `Create Campaign`;
    }
}

/**
 * Update real-time preview based on form input
 * @param {string} platform - The platform to update ('meta', 'google', 'twitter')
 */
function updatePreview(platform) {
    const headline = document.getElementById('ad-headline').value || 'Your compelling headline will appear here';
    const adText = document.getElementById('ad-text').value || 'Your ad description will appear here.';
    const cta = document.getElementById('ad-cta').value || 'apply_now';
    
    // Update appropriate preview based on platform
    switch(platform) {
        case 'meta':
            document.querySelector('.preview-headline').textContent = headline;
            document.querySelector('.preview-description').textContent = adText;
            
            // Update CTA button
            const ctaButton = document.querySelector('.preview-cta button');
            if (cta === 'apply_now') ctaButton.textContent = 'Apply Now';
            if (cta === 'learn_more') ctaButton.textContent = 'Learn More';
            if (cta === 'see_jobs') ctaButton.textContent = 'See Jobs';
            if (cta === 'sign_up') ctaButton.textContent = 'Sign Up';
            break;
            
        case 'google':
            document.querySelector('.google-headline').textContent = 
                headline.length > 30 ? headline.substring(0, 27) + '...' : headline;
            document.querySelector('.google-description').textContent = 
                adText.length > 90 ? adText.substring(0, 87) + '...' : adText;
            break;
            
        case 'twitter':
            const tweetText = `${headline}: ${adText.substring(0, 180)}... #JobOpening #Hiring`;
            document.querySelector('.tweet-text').textContent = tweetText;
            break;
    }
}