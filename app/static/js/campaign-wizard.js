/**
 * Campaign Creation Wizard
 * Handles campaign creation UI and API interactions
 */

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
        
        // Create a FormData object
        const formData = new FormData();
        formData.append('image', file);
        
        try {
            // Show loading state
            showUploadingState();
            
            // Upload to image storage API
            const response = await fetch('/api/uploads/image', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Save image URL to campaign data
                campaignData.ad_image_url = data.url;
                
                // Update UI
                document.querySelectorAll('.preview-image img, .tweet-image img').forEach(img => {
                    img.src = data.url;
                });
                
                hideUploadingState();
                showNotification('Image uploaded successfully', 'success');
            } else {
                hideUploadingState();
                showNotification('Failed to upload image', 'error');
            }
        } catch (error) {
            console.error('Error uploading image:', error);
            hideUploadingState();
            showNotification('Error uploading image', 'error');
        }
    });
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
 * Handle campaign form submission
 */
async function handleCampaignSubmit(e) {
    e.preventDefault();
    
    // Collect all form data
    collectFormData();
    
    // Validate before submission
    if (!validateCampaignData()) {
        return;
    }
    
    try {
        // Show loading state
        showLoadingState();
        
        // Send data to API
        const response = await fetch('/api/campaigns', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: campaignData.title,
                description: campaignData.description,
                platform_id: parseInt(campaignData.platform_ids[0]), // Primary platform
                job_opening_id: campaignData.job_opening_ids[0], // Primary job
                segment_id: campaignData.segment_ids.length > 0 ? campaignData.segment_ids[0] : null,
                budget: campaignData.budget,
                
                // Enhanced ad content fields
                ad_headline: campaignData.ad_headline,
                ad_text: campaignData.ad_text,
                ad_cta: campaignData.ad_cta,
                ad_image_url: campaignData.ad_image_url,
                platform_specific: campaignData.platform_specific
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Hide loading state
            hideLoadingState();
            
            // Show success and redirect
            showNotification('Campaign created successfully!', 'success');
            
            // Redirect to campaign detail page after a delay
            setTimeout(() => {
                window.location.href = `/campaigns/${data.data.id}`;
            }, 1500);
        } else {
            // Hide loading state
            hideLoadingState();
            
            // Show error
            showNotification('Failed to create campaign: ' + (data.message || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error creating campaign:', error);
        hideLoadingState();
        showNotification('Error creating campaign. Please try again.', 'error');
    }
}

/**
 * Validate campaign data before submission
 */
function validateCampaignData() {
    // Check title
    if (!campaignData.title) {
        showNotification('Campaign title is required', 'error');
        return false;
    }
    
    // Check dates
    if (!campaignData.start_date || !campaignData.end_date) {
        showNotification('Campaign start and end dates are required', 'error');
        return false;
    }
    
    // Check if start date is before end date
    if (new Date(campaignData.start_date) >= new Date(campaignData.end_date)) {
        showNotification('Start date must be before end date', 'error');
        return false;
    }
    
    // Check budget
    if (!campaignData.budget || campaignData.budget <= 0) {
        showNotification('Campaign budget must be greater than 0', 'error');
        return false;
    }
    
    // Check platforms
    if (campaignData.platform_ids.length === 0) {
        showNotification('Please select at least one platform', 'error');
        return false;
    }
    
    // Check jobs
    if (campaignData.job_opening_ids.length === 0) {
        showNotification('Please select at least one job opening', 'error');
        return false;
    }
    
    // Check ad content
    if (!campaignData.ad_headline || !campaignData.ad_text) {
        showNotification('Ad headline and text are required', 'error');
        return false;
    }
    
    return true;
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