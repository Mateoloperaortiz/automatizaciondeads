/**
 * Ad Visual Editor
 * Interactive visual editor for ad content customization
 */

import { adTemplateService } from './ad-template-service.js';
import { toastService } from './services/toast-service.js';

class AdVisualEditor {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container with ID '${containerId}' not found.`);
            return;
        }
        
        this.currentPlatform = 'meta';
        this.adData = {
            headline: '',
            text: '',
            cta: 'apply_now',
            imageUrl: '/static/img/ad-templates/placeholder.jpg',
            backgroundColor: '#ffffff',
            headlineColor: '#1a1a1a',
            textColor: '#4a4a4a',
            buttonColor: '#4361ee',
            buttonTextColor: '#ffffff',
            borderRadius: '8',
            fontFamily: 'Inter, sans-serif'
        };
        
        this.selectedElement = null;
        this.isEditing = false;
        
        this.init();
    }
    
    /**
     * Initialize the editor
     */
    init() {
        this.createEditorUI();
        this.createAdPreview();
        this.bindEvents();
        this.updatePreview();
    }
    
    /**
     * Create the editor UI
     */
    createEditorUI() {
        this.container.innerHTML = `
            <div class="visual-editor-container">
                <div class="editor-toolbar">
                    <div class="platform-selector">
                        <button data-platform="meta" class="platform-btn active">
                            <i class="fab fa-facebook"></i> Meta
                        </button>
                        <button data-platform="google" class="platform-btn">
                            <i class="fab fa-google"></i> Google
                        </button>
                        <button data-platform="twitter" class="platform-btn">
                            <i class="fab fa-twitter"></i> X (Twitter)
                        </button>
                    </div>
                    
                    <div class="editor-actions">
                        <button id="undoBtn" class="editor-btn" title="Undo">
                            <i class="fas fa-undo"></i>
                        </button>
                        <button id="resetBtn" class="editor-btn" title="Reset to Default">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                        <button id="saveTemplateBtn" class="editor-btn" title="Save as Template">
                            <i class="fas fa-save"></i>
                        </button>
                        <button id="templateGalleryBtn" class="editor-btn" title="Template Gallery">
                            <i class="fas fa-photo-video"></i>
                        </button>
                    </div>
                </div>
                
                <div class="editor-content">
                    <!-- Left panel: Ad Preview -->
                    <div class="preview-panel">
                        <div class="preview-container">
                            <div class="ad-preview meta-preview active" id="metaAdPreview">
                                <!-- Meta Ad Preview content will be inserted here -->
                            </div>
                            
                            <div class="ad-preview google-preview" id="googleAdPreview">
                                <!-- Google Ad Preview content will be inserted here -->
                            </div>
                            
                            <div class="ad-preview twitter-preview" id="twitterAdPreview">
                                <!-- Twitter Ad Preview content will be inserted here -->
                            </div>
                        </div>
                        
                        <div class="preview-controls">
                            <div class="preview-size-control">
                                <button class="size-btn active" data-size="100">100%</button>
                                <button class="size-btn" data-size="75">75%</button>
                                <button class="size-btn" data-size="50">50%</button>
                            </div>
                            
                            <div class="device-preview-control">
                                <button class="device-btn active" data-device="desktop">
                                    <i class="fas fa-desktop"></i>
                                </button>
                                <button class="device-btn" data-device="tablet">
                                    <i class="fas fa-tablet-alt"></i>
                                </button>
                                <button class="device-btn" data-device="mobile">
                                    <i class="fas fa-mobile-alt"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Right panel: Editor Controls -->
                    <div class="editor-controls">
                        <div class="controls-tabs">
                            <button class="tab-btn active" data-tab="content">Content</button>
                            <button class="tab-btn" data-tab="style">Style</button>
                            <button class="tab-btn" data-tab="layout">Layout</button>
                        </div>
                        
                        <div class="controls-content">
                            <!-- Content Tab -->
                            <div class="tab-content active" id="contentTab">
                                <div class="control-group">
                                    <label for="adHeadline">Headline</label>
                                    <input type="text" id="adHeadline" class="form-control" placeholder="Enter compelling headline..." value="${this.adData.headline}">
                                    <div class="character-count">
                                        <span id="headlineCount">0</span>/<span id="headlineMax">40</span>
                                    </div>
                                </div>
                                
                                <div class="control-group">
                                    <label for="adText">Ad Text</label>
                                    <textarea id="adText" class="form-control" rows="4" placeholder="Describe the job opportunity...">${this.adData.text}</textarea>
                                    <div class="character-count">
                                        <span id="textCount">0</span>/<span id="textMax">125</span>
                                    </div>
                                </div>
                                
                                <div class="control-group">
                                    <label for="adCta">Call to Action</label>
                                    <select id="adCta" class="form-control">
                                        <option value="apply_now" ${this.adData.cta === 'apply_now' ? 'selected' : ''}>Apply Now</option>
                                        <option value="learn_more" ${this.adData.cta === 'learn_more' ? 'selected' : ''}>Learn More</option>
                                        <option value="see_jobs" ${this.adData.cta === 'see_jobs' ? 'selected' : ''}>See Jobs</option>
                                        <option value="sign_up" ${this.adData.cta === 'sign_up' ? 'selected' : ''}>Sign Up</option>
                                    </select>
                                </div>
                                
                                <div class="control-group">
                                    <label>Ad Image</label>
                                    <div class="media-upload-container">
                                        <div class="media-upload">
                                            <input type="file" id="adImage" class="media-input" accept="image/*">
                                            <div class="upload-placeholder">
                                                <i class="fas fa-cloud-upload-alt"></i>
                                                <span>Drag & drop image or click to upload</span>
                                            </div>
                                            <div class="media-preview" style="display: none;">
                                                <img id="imagePreview" src="#" alt="Ad image preview">
                                                <button class="btn btn-sm btn-danger remove-media">
                                                    <i class="fas fa-trash"></i>
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Style Tab -->
                            <div class="tab-content" id="styleTab">
                                <div class="control-group">
                                    <label for="fontFamily">Font Family</label>
                                    <select id="fontFamily" class="form-control">
                                        <option value="Inter, sans-serif" ${this.adData.fontFamily === 'Inter, sans-serif' ? 'selected' : ''}>Inter</option>
                                        <option value="Roboto, sans-serif" ${this.adData.fontFamily === 'Roboto, sans-serif' ? 'selected' : ''}>Roboto</option>
                                        <option value="'Open Sans', sans-serif" ${this.adData.fontFamily === "'Open Sans', sans-serif" ? 'selected' : ''}>Open Sans</option>
                                        <option value="'Montserrat', sans-serif" ${this.adData.fontFamily === "'Montserrat', sans-serif" ? 'selected' : ''}>Montserrat</option>
                                        <option value="'Poppins', sans-serif" ${this.adData.fontFamily === "'Poppins', sans-serif" ? 'selected' : ''}>Poppins</option>
                                    </select>
                                </div>
                                
                                <div class="control-group">
                                    <label for="backgroundColor">Background Color</label>
                                    <div class="color-picker-container">
                                        <input type="color" id="backgroundColor" value="${this.adData.backgroundColor}">
                                        <input type="text" id="backgroundColorText" class="form-control color-input" value="${this.adData.backgroundColor}">
                                    </div>
                                </div>
                                
                                <div class="control-group">
                                    <label for="headlineColor">Headline Color</label>
                                    <div class="color-picker-container">
                                        <input type="color" id="headlineColor" value="${this.adData.headlineColor}">
                                        <input type="text" id="headlineColorText" class="form-control color-input" value="${this.adData.headlineColor}">
                                    </div>
                                </div>
                                
                                <div class="control-group">
                                    <label for="textColor">Text Color</label>
                                    <div class="color-picker-container">
                                        <input type="color" id="textColor" value="${this.adData.textColor}">
                                        <input type="text" id="textColorText" class="form-control color-input" value="${this.adData.textColor}">
                                    </div>
                                </div>
                                
                                <div class="control-group">
                                    <label for="buttonColor">Button Color</label>
                                    <div class="color-picker-container">
                                        <input type="color" id="buttonColor" value="${this.adData.buttonColor}">
                                        <input type="text" id="buttonColorText" class="form-control color-input" value="${this.adData.buttonColor}">
                                    </div>
                                </div>
                                
                                <div class="control-group">
                                    <label for="buttonTextColor">Button Text Color</label>
                                    <div class="color-picker-container">
                                        <input type="color" id="buttonTextColor" value="${this.adData.buttonTextColor}">
                                        <input type="text" id="buttonTextColorText" class="form-control color-input" value="${this.adData.buttonTextColor}">
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Layout Tab -->
                            <div class="tab-content" id="layoutTab">
                                <div class="control-group">
                                    <label for="borderRadius">Border Radius</label>
                                    <div class="range-control">
                                        <input type="range" id="borderRadius" min="0" max="24" value="${this.adData.borderRadius}" class="form-range">
                                        <input type="number" id="borderRadiusValue" class="form-control range-value" value="${this.adData.borderRadius}" min="0" max="24">
                                    </div>
                                </div>
                                
                                <div class="control-group">
                                    <label>Layout Templates</label>
                                    <div class="layout-templates">
                                        <div class="layout-template" data-layout="standard">
                                            <div class="layout-preview standard-layout"></div>
                                            <span>Standard</span>
                                        </div>
                                        <div class="layout-template" data-layout="image-left">
                                            <div class="layout-preview image-left-layout"></div>
                                            <span>Image Left</span>
                                        </div>
                                        <div class="layout-template" data-layout="image-right">
                                            <div class="layout-preview image-right-layout"></div>
                                            <span>Image Right</span>
                                        </div>
                                        <div class="layout-template" data-layout="minimalist">
                                            <div class="layout-preview minimalist-layout"></div>
                                            <span>Minimalist</span>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="control-group">
                                    <label>Color Presets</label>
                                    <div class="color-presets">
                                        <div class="color-preset" data-preset="modern-blue" style="background: linear-gradient(to right, #4361ee, #3f37c9);">
                                        </div>
                                        <div class="color-preset" data-preset="warm-orange" style="background: linear-gradient(to right, #ff9f1c, #ffbf69);">
                                        </div>
                                        <div class="color-preset" data-preset="cool-green" style="background: linear-gradient(to right, #2ec4b6, #cbf3f0);">
                                        </div>
                                        <div class="color-preset" data-preset="monochrome" style="background: linear-gradient(to right, #2b2d42, #8d99ae);">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add character counters initial values
        this.updateCharacterCount('adHeadline', 'headlineCount');
        this.updateCharacterCount('adText', 'textCount');
    }
    
    /**
     * Create ad preview containers
     */
    createAdPreview() {
        // Meta ad preview
        const metaPreview = document.getElementById('metaAdPreview');
        metaPreview.innerHTML = `
            <div class="preview-header">
                <img src="/static/img/avatar.png" alt="Company" class="preview-logo">
                <div class="preview-meta">
                    <span class="company-name">Company Name</span>
                    <span class="sponsored">Sponsored</span>
                </div>
            </div>
            
            <div class="preview-text">
                <p class="preview-headline" contenteditable="true">Your compelling headline will appear here</p>
                <p class="preview-description" contenteditable="true">Your ad description will appear here. Make it engaging to attract the right candidates for the job opening.</p>
            </div>
            
            <div class="preview-image">
                <img src="${this.adData.imageUrl}" alt="Ad preview">
            </div>
            
            <div class="preview-cta">
                <button class="btn btn-primary">Apply Now</button>
            </div>
        `;
        
        // Google ad preview
        const googlePreview = document.getElementById('googleAdPreview');
        googlePreview.innerHTML = `
            <div class="google-ad">
                <div class="google-ad-tag">Ad</div>
                <div class="google-headline" contenteditable="true">Your compelling headline will appear here</div>
                <div class="google-url">www.yourcompany.com/careers</div>
                <div class="google-description" contenteditable="true">Your ad description will appear here. Make it engaging to attract the right candidates.</div>
            </div>
        `;
        
        // Twitter ad preview
        const twitterPreview = document.getElementById('twitterAdPreview');
        twitterPreview.innerHTML = `
            <div class="tweet">
                <div class="tweet-header">
                    <img src="/static/img/avatar.png" alt="Company" class="tweet-avatar">
                    <div class="tweet-meta">
                        <span class="twitter-name">Company Name</span>
                        <span class="twitter-handle">@company</span>
                    </div>
                </div>
                
                <div class="tweet-content">
                    <p class="tweet-text" contenteditable="true">Your tweet text will appear here. #JobOpening #Hiring</p>
                </div>
                
                <div class="tweet-image">
                    <img src="${this.adData.imageUrl}" alt="Tweet image">
                </div>
                
                <div class="tweet-footer">
                    <span class="tweet-sponsored">Promoted</span>
                </div>
            </div>
        `;
        
        // Make all contenteditable elements interactive
        const editableElements = this.container.querySelectorAll('[contenteditable="true"]');
        editableElements.forEach(element => {
            element.addEventListener('focus', () => {
                this.selectedElement = element;
                this.isEditing = true;
            });
            
            element.addEventListener('blur', () => {
                this.isEditing = false;
                this.updateAdDataFromEditable();
            });
            
            element.addEventListener('input', () => {
                this.updateAdDataFromEditable();
            });
        });
    }
    
    /**
     * Bind events to UI elements
     */
    bindEvents() {
        // Platform selector
        const platformButtons = this.container.querySelectorAll('.platform-btn');
        platformButtons.forEach(button => {
            button.addEventListener('click', () => {
                const platform = button.getAttribute('data-platform');
                this.switchPlatform(platform);
                
                // Update button states
                platformButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
            });
        });
        
        // Tab switching
        const tabButtons = this.container.querySelectorAll('.tab-btn');
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tab = button.getAttribute('data-tab');
                this.switchTab(tab);
                
                // Update button states
                tabButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
            });
        });
        
        // Content inputs
        const adHeadline = document.getElementById('adHeadline');
        const adText = document.getElementById('adText');
        const adCta = document.getElementById('adCta');
        
        if (adHeadline) {
            adHeadline.addEventListener('input', () => {
                this.adData.headline = adHeadline.value;
                this.updatePreview();
                this.updateCharacterCount('adHeadline', 'headlineCount');
            });
        }
        
        if (adText) {
            adText.addEventListener('input', () => {
                this.adData.text = adText.value;
                this.updatePreview();
                this.updateCharacterCount('adText', 'textCount');
            });
        }
        
        if (adCta) {
            adCta.addEventListener('change', () => {
                this.adData.cta = adCta.value;
                this.updatePreview();
            });
        }
        
        // Image upload
        const adImage = document.getElementById('adImage');
        const removeMedia = this.container.querySelector('.remove-media');
        
        if (adImage) {
            adImage.addEventListener('change', (e) => {
                this.handleImageUpload(e);
            });
        }
        
        if (removeMedia) {
            removeMedia.addEventListener('click', (e) => {
                e.preventDefault();
                this.resetImage();
            });
        }
        
        // Style controls
        const fontFamily = document.getElementById('fontFamily');
        const backgroundColor = document.getElementById('backgroundColor');
        const backgroundColorText = document.getElementById('backgroundColorText');
        const headlineColor = document.getElementById('headlineColor');
        const headlineColorText = document.getElementById('headlineColorText');
        const textColor = document.getElementById('textColor');
        const textColorText = document.getElementById('textColorText');
        const buttonColor = document.getElementById('buttonColor');
        const buttonColorText = document.getElementById('buttonColorText');
        const buttonTextColor = document.getElementById('buttonTextColor');
        const buttonTextColorText = document.getElementById('buttonTextColorText');
        
        if (fontFamily) {
            fontFamily.addEventListener('change', () => {
                this.adData.fontFamily = fontFamily.value;
                this.updatePreview();
            });
        }
        
        this.setupColorPicker(backgroundColor, backgroundColorText, 'backgroundColor');
        this.setupColorPicker(headlineColor, headlineColorText, 'headlineColor');
        this.setupColorPicker(textColor, textColorText, 'textColor');
        this.setupColorPicker(buttonColor, buttonColorText, 'buttonColor');
        this.setupColorPicker(buttonTextColor, buttonTextColorText, 'buttonTextColor');
        
        // Layout controls
        const borderRadius = document.getElementById('borderRadius');
        const borderRadiusValue = document.getElementById('borderRadiusValue');
        
        if (borderRadius && borderRadiusValue) {
            borderRadius.addEventListener('input', () => {
                const value = borderRadius.value;
                this.adData.borderRadius = value;
                borderRadiusValue.value = value;
                this.updatePreview();
            });
            
            borderRadiusValue.addEventListener('input', () => {
                const value = borderRadiusValue.value;
                if (value >= 0 && value <= 24) {
                    this.adData.borderRadius = value;
                    borderRadius.value = value;
                    this.updatePreview();
                }
            });
        }
        
        // Layout templates
        const layoutTemplates = this.container.querySelectorAll('.layout-template');
        layoutTemplates.forEach(template => {
            template.addEventListener('click', () => {
                const layout = template.getAttribute('data-layout');
                this.applyLayoutTemplate(layout);
                
                // Update active state
                layoutTemplates.forEach(t => t.classList.remove('active'));
                template.classList.add('active');
            });
        });
        
        // Color presets
        const colorPresets = this.container.querySelectorAll('.color-preset');
        colorPresets.forEach(preset => {
            preset.addEventListener('click', () => {
                const presetName = preset.getAttribute('data-preset');
                this.applyColorPreset(presetName);
                
                // Update active state
                colorPresets.forEach(p => p.classList.remove('active'));
                preset.classList.add('active');
            });
        });
        
        // Preview size controls
        const sizeButtons = this.container.querySelectorAll('.size-btn');
        sizeButtons.forEach(button => {
            button.addEventListener('click', () => {
                const size = button.getAttribute('data-size');
                this.setPreviewSize(size);
                
                // Update button states
                sizeButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
            });
        });
        
        // Device preview controls
        const deviceButtons = this.container.querySelectorAll('.device-btn');
        deviceButtons.forEach(button => {
            button.addEventListener('click', () => {
                const device = button.getAttribute('data-device');
                this.setDevicePreview(device);
                
                // Update button states
                deviceButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
            });
        });
        
        // Editor action buttons
        const undoBtn = document.getElementById('undoBtn');
        const resetBtn = document.getElementById('resetBtn');
        const saveTemplateBtn = document.getElementById('saveTemplateBtn');
        const templateGalleryBtn = document.getElementById('templateGalleryBtn');
        
        if (undoBtn) {
            undoBtn.addEventListener('click', () => {
                // Currently just resets to defaults, but could be enhanced with history
                this.resetToDefaults();
            });
        }
        
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this._showConfirmationModal(
                    'Reset to Default',
                    'Are you sure you want to reset to default settings? This will lose all your customizations.',
                    'Reset',
                    'Cancel'
                ).then(confirmed => {
                    if (confirmed) {
                        this.resetToDefaults();
                        // Show toast notification
                        toastService.info('Ad settings have been reset to defaults');
                    }
                });
            });
        }
        
        if (saveTemplateBtn) {
            saveTemplateBtn.addEventListener('click', () => {
                this.saveAsTemplate();
            });
        }
        
        if (templateGalleryBtn) {
            templateGalleryBtn.addEventListener('click', () => {
                this.showTemplateGallery();
            });
        }
    }
    
    /**
     * Setup a color picker and its text input
     */
    setupColorPicker(colorInput, textInput, dataProperty) {
        if (!colorInput || !textInput) return;
        
        colorInput.addEventListener('input', () => {
            const value = colorInput.value;
            this.adData[dataProperty] = value;
            textInput.value = value;
            this.updatePreview();
        });
        
        textInput.addEventListener('input', () => {
            const value = textInput.value;
            if (value.match(/^#([0-9A-F]{3}){1,2}$/i)) {
                this.adData[dataProperty] = value;
                colorInput.value = value;
                this.updatePreview();
            }
        });
        
        textInput.addEventListener('blur', () => {
            // Reset to color input value if invalid
            textInput.value = colorInput.value;
        });
    }
    
    /**
     * Switch between platforms (Meta, Google, Twitter)
     */
    switchPlatform(platform) {
        this.currentPlatform = platform;
        
        // Update platform-specific character limits
        this.updatePlatformLimits();
        
        // Show the appropriate preview
        const previews = this.container.querySelectorAll('.ad-preview');
        previews.forEach(preview => {
            preview.classList.remove('active');
        });
        
        const activePreview = this.container.querySelector(`.${platform}-preview`);
        if (activePreview) {
            activePreview.classList.add('active');
        }
    }
    
    /**
     * Switch between editor tabs
     */
    switchTab(tab) {
        const tabContents = this.container.querySelectorAll('.tab-content');
        tabContents.forEach(content => {
            content.classList.remove('active');
        });
        
        const activeTab = document.getElementById(`${tab}Tab`);
        if (activeTab) {
            activeTab.classList.add('active');
        }
    }
    
    /**
     * Update character count for text inputs
     */
    updateCharacterCount(inputId, countId) {
        const input = document.getElementById(inputId);
        const count = document.getElementById(countId);
        const max = document.getElementById(inputId === 'adHeadline' ? 'headlineMax' : 'textMax');
        
        if (!input || !count || !max) return;
        
        const length = input.value.length;
        count.textContent = length;
        
        const maxValue = parseInt(max.textContent);
        const countWrapper = count.closest('.character-count');
        
        if (countWrapper) {
            countWrapper.classList.remove('limit-reached', 'limit-exceeded');
            
            if (length >= maxValue * 0.8 && length <= maxValue) {
                countWrapper.classList.add('limit-reached');
            } else if (length > maxValue) {
                countWrapper.classList.add('limit-exceeded');
            }
        }
    }
    
    /**
     * Update platform-specific character limits
     */
    updatePlatformLimits() {
        const headlineMax = document.getElementById('headlineMax');
        const textMax = document.getElementById('textMax');
        
        if (!headlineMax || !textMax) return;
        
        switch (this.currentPlatform) {
            case 'meta':
                headlineMax.textContent = '40';
                textMax.textContent = '125';
                break;
            case 'google':
                headlineMax.textContent = '30';
                textMax.textContent = '90';
                break;
            case 'twitter':
                headlineMax.textContent = '50';
                textMax.textContent = '230';
                break;
        }
        
        // Update character counts to reflect new limits
        this.updateCharacterCount('adHeadline', 'headlineCount');
        this.updateCharacterCount('adText', 'textCount');
    }
    
    /**
     * Handle image upload
     */
    handleImageUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // Check file type
        if (!file.type.match('image.*')) {
            toastService.error('Please select an image file');
            return;
        }
        
        // Check file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            toastService.error('Image file should be less than 5MB');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            this.setImage(e.target.result);
        };
        reader.readAsDataURL(file);
    }
    
    /**
     * Set the ad image
     */
    setImage(imageUrl) {
        this.adData.imageUrl = imageUrl;
        
        // Update preview
        this.updatePreview();
        
        // Show image preview
        const uploadPlaceholder = this.container.querySelector('.upload-placeholder');
        const mediaPreview = this.container.querySelector('.media-preview');
        const imagePreview = document.getElementById('imagePreview');
        
        if (uploadPlaceholder && mediaPreview && imagePreview) {
            uploadPlaceholder.style.display = 'none';
            mediaPreview.style.display = 'block';
            imagePreview.src = imageUrl;
        }
    }
    
    /**
     * Reset the image
     */
    resetImage() {
        this.adData.imageUrl = '/static/img/ad-templates/placeholder.jpg';
        
        // Update preview
        this.updatePreview();
        
        // Reset upload form
        const uploadPlaceholder = this.container.querySelector('.upload-placeholder');
        const mediaPreview = this.container.querySelector('.media-preview');
        const adImage = document.getElementById('adImage');
        
        if (uploadPlaceholder && mediaPreview && adImage) {
            uploadPlaceholder.style.display = 'flex';
            mediaPreview.style.display = 'none';
            adImage.value = '';
        }
    }
    
    /**
     * Apply a layout template
     */
    applyLayoutTemplate(layout) {
        switch (layout) {
            case 'standard':
                // Default layout, no changes needed
                break;
            case 'image-left':
                // Image on left, text on right
                // We would modify the preview HTML structure here
                break;
            case 'image-right':
                // Image on right, text on left
                // We would modify the preview HTML structure here
                break;
            case 'minimalist':
                // Clean, minimal design
                this.adData.backgroundColor = '#ffffff';
                this.adData.headlineColor = '#000000';
                this.adData.textColor = '#666666';
                this.adData.buttonColor = '#000000';
                this.adData.buttonTextColor = '#ffffff';
                this.adData.borderRadius = '0';
                this.adData.fontFamily = "'Montserrat', sans-serif";
                break;
        }
        
        this.updateControlValues();
        this.updatePreview();
    }
    
    /**
     * Apply a color preset
     */
    applyColorPreset(preset) {
        switch (preset) {
            case 'modern-blue':
                this.adData.backgroundColor = '#ffffff';
                this.adData.headlineColor = '#4361ee';
                this.adData.textColor = '#2b2d42';
                this.adData.buttonColor = '#4361ee';
                this.adData.buttonTextColor = '#ffffff';
                break;
            case 'warm-orange':
                this.adData.backgroundColor = '#ffffff';
                this.adData.headlineColor = '#ff9f1c';
                this.adData.textColor = '#2b2d42';
                this.adData.buttonColor = '#ff9f1c';
                this.adData.buttonTextColor = '#ffffff';
                break;
            case 'cool-green':
                this.adData.backgroundColor = '#f8f9fa';
                this.adData.headlineColor = '#2ec4b6';
                this.adData.textColor = '#3d5a80';
                this.adData.buttonColor = '#2ec4b6';
                this.adData.buttonTextColor = '#ffffff';
                break;
            case 'monochrome':
                this.adData.backgroundColor = '#f8f9fa';
                this.adData.headlineColor = '#2b2d42';
                this.adData.textColor = '#8d99ae';
                this.adData.buttonColor = '#2b2d42';
                this.adData.buttonTextColor = '#ffffff';
                break;
        }
        
        this.updateControlValues();
        this.updatePreview();
    }
    
    /**
     * Update control values based on adData
     */
    updateControlValues() {
        // Update colors
        const controls = [
            { id: 'backgroundColor', prop: 'backgroundColor' },
            { id: 'backgroundColorText', prop: 'backgroundColor' },
            { id: 'headlineColor', prop: 'headlineColor' },
            { id: 'headlineColorText', prop: 'headlineColor' },
            { id: 'textColor', prop: 'textColor' },
            { id: 'textColorText', prop: 'textColor' },
            { id: 'buttonColor', prop: 'buttonColor' },
            { id: 'buttonColorText', prop: 'buttonColor' },
            { id: 'buttonTextColor', prop: 'buttonTextColor' },
            { id: 'buttonTextColorText', prop: 'buttonTextColor' }
        ];
        
        controls.forEach(control => {
            const element = document.getElementById(control.id);
            if (element) {
                element.value = this.adData[control.prop];
            }
        });
        
        // Update slider values
        const borderRadius = document.getElementById('borderRadius');
        const borderRadiusValue = document.getElementById('borderRadiusValue');
        
        if (borderRadius && borderRadiusValue) {
            borderRadius.value = this.adData.borderRadius;
            borderRadiusValue.value = this.adData.borderRadius;
        }
        
        // Update font family
        const fontFamily = document.getElementById('fontFamily');
        if (fontFamily) {
            fontFamily.value = this.adData.fontFamily;
        }
    }
    
    /**
     * Set preview size
     */
    setPreviewSize(size) {
        const previewContainer = this.container.querySelector('.preview-container');
        if (!previewContainer) return;
        
        previewContainer.style.transform = `scale(${size / 100})`;
    }
    
    /**
     * Set device preview mode
     */
    setDevicePreview(device) {
        const previewContainer = this.container.querySelector('.preview-container');
        if (!previewContainer) return;
        
        // Remove existing device classes
        previewContainer.classList.remove('desktop-view', 'tablet-view', 'mobile-view');
        
        // Add new device class
        previewContainer.classList.add(`${device}-view`);
        
        // Adjust preview container size based on device
        switch (device) {
            case 'desktop':
                previewContainer.style.maxWidth = '100%';
                break;
            case 'tablet':
                previewContainer.style.maxWidth = '768px';
                break;
            case 'mobile':
                previewContainer.style.maxWidth = '375px';
                break;
        }
    }
    
    /**
     * Reset to default settings
     */
    resetToDefaults() {
        this.adData = {
            headline: '',
            text: '',
            cta: 'apply_now',
            imageUrl: '/static/img/ad-templates/placeholder.jpg',
            backgroundColor: '#ffffff',
            headlineColor: '#1a1a1a',
            textColor: '#4a4a4a',
            buttonColor: '#4361ee',
            buttonTextColor: '#ffffff',
            borderRadius: '8',
            fontFamily: 'Inter, sans-serif'
        };
        
        // Reset form inputs
        const adHeadline = document.getElementById('adHeadline');
        const adText = document.getElementById('adText');
        const adCta = document.getElementById('adCta');
        
        if (adHeadline) adHeadline.value = '';
        if (adText) adText.value = '';
        if (adCta) adCta.value = 'apply_now';
        
        // Reset image
        this.resetImage();
        
        // Update controls and preview
        this.updateControlValues();
        this.updateCharacterCount('adHeadline', 'headlineCount');
        this.updateCharacterCount('adText', 'textCount');
        this.updatePreview();
    }
    
    /**
     * Save the current design as a template
     */
    saveAsTemplate() {
        // Use modal dialog instead of prompt
        this._showTemplateNameModal().then(templateName => {
            if (!templateName) return;
            
            const template = {
                name: templateName,
                data: { ...this.adData },
                createdAt: new Date().toISOString()
            };
            
            // Use the template service to save
            adTemplateService.saveTemplate(template)
                .then(savedTemplate => {
                    // Show success toast
                    toastService.success(`Template "${templateName}" saved successfully!`);
                    
                    // Dispatch event for other components that might be listening
                    const event = new CustomEvent('template:created', { 
                        detail: { template: savedTemplate } 
                    });
                    document.dispatchEvent(event);
                })
                .catch(error => {
                    // Error is already handled by the service, but we can add extra handling here
                    console.error('Template save error:', error);
                });
        });
    }
    
    /**
     * Display a modal dialog for template name input
     * @returns {Promise<string>} - Resolves with template name or null if cancelled
     * @private
     */
    _showTemplateNameModal() {
        return new Promise(resolve => {
            // Create modal container if it doesn't exist
            let modalContainer = document.getElementById('adEditorModal');
            if (!modalContainer) {
                modalContainer = document.createElement('div');
                modalContainer.id = 'adEditorModal';
                document.body.appendChild(modalContainer);
            }
            
            // Set up modal HTML
            modalContainer.innerHTML = `
                <div class="modal-overlay">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3>Save Template</h3>
                            <button class="modal-close" aria-label="Close">×</button>
                        </div>
                        <div class="modal-body">
                            <form id="templateNameForm">
                                <div class="form-group">
                                    <label for="templateName">Template Name</label>
                                    <input type="text" id="templateName" class="form-control" 
                                           placeholder="Enter a name for your template" required>
                                </div>
                                <div class="form-actions">
                                    <button type="button" class="btn btn-secondary" id="cancelTemplateBtn">Cancel</button>
                                    <button type="submit" class="btn btn-primary" id="saveTemplateBtn">Save Template</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            `;
            
            // Add modal styles if not already added
            if (!document.getElementById('adEditorModalStyles')) {
                const styleEl = document.createElement('style');
                styleEl.id = 'adEditorModalStyles';
                styleEl.textContent = `
                    .modal-overlay {
                        position: fixed;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background-color: rgba(0, 0, 0, 0.5);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        z-index: 9999;
                    }
                    
                    .modal-content {
                        background-color: white;
                        border-radius: 8px;
                        max-width: 500px;
                        width: 100%;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                        overflow: hidden;
                    }
                    
                    .modal-header {
                        padding: 16px 24px;
                        border-bottom: 1px solid #eee;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }
                    
                    .modal-header h3 {
                        margin: 0;
                        font-size: 18px;
                    }
                    
                    .modal-close {
                        background: none;
                        border: none;
                        font-size: 24px;
                        cursor: pointer;
                        color: #999;
                    }
                    
                    .modal-body {
                        padding: 24px;
                    }
                    
                    .form-group {
                        margin-bottom: 20px;
                    }
                    
                    .form-group label {
                        display: block;
                        margin-bottom: 8px;
                        font-weight: 500;
                    }
                    
                    .form-control {
                        width: 100%;
                        padding: 10px 12px;
                        font-size: 14px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                    }
                    
                    .form-actions {
                        display: flex;
                        justify-content: flex-end;
                        gap: 12px;
                    }
                    
                    .btn {
                        padding: 10px 16px;
                        border-radius: 4px;
                        font-weight: 500;
                        cursor: pointer;
                        border: none;
                    }
                    
                    .btn-primary {
                        background-color: #4361ee;
                        color: white;
                    }
                    
                    .btn-secondary {
                        background-color: #f8f9fa;
                        border: 1px solid #ddd;
                        color: #333;
                    }
                `;
                document.head.appendChild(styleEl);
            }
            
            // Show modal
            modalContainer.style.display = 'block';
            
            // Focus the input
            setTimeout(() => {
                const templateNameInput = document.getElementById('templateName');
                if (templateNameInput) {
                    templateNameInput.focus();
                }
            }, 100);
            
            // Handle form submission
            const form = document.getElementById('templateNameForm');
            if (form) {
                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    const templateName = document.getElementById('templateName').value.trim();
                    modalContainer.style.display = 'none';
                    resolve(templateName);
                });
            }
            
            // Handle cancel
            const cancelBtn = document.getElementById('cancelTemplateBtn');
            if (cancelBtn) {
                cancelBtn.addEventListener('click', () => {
                    modalContainer.style.display = 'none';
                    resolve(null);
                });
            }
            
            // Handle close
            const closeBtn = modalContainer.querySelector('.modal-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    modalContainer.style.display = 'none';
                    resolve(null);
                });
            }
            
            // Close on outside click
            modalContainer.querySelector('.modal-overlay').addEventListener('click', (e) => {
                if (e.target === modalContainer.querySelector('.modal-overlay')) {
                    modalContainer.style.display = 'none';
                    resolve(null);
                }
            });
            
            // Handle escape key
            const handleEscape = (e) => {
                if (e.key === 'Escape') {
                    modalContainer.style.display = 'none';
                    resolve(null);
                    document.removeEventListener('keydown', handleEscape);
                }
            };
            document.addEventListener('keydown', handleEscape);
        });
    }
    
    /**
     * Show a confirmation modal dialog
     * @param {string} title - Modal title
     * @param {string} message - Confirmation message
     * @param {string} confirmText - Text for confirm button
     * @param {string} cancelText - Text for cancel button
     * @returns {Promise<boolean>} - Resolves with true if confirmed, false if cancelled
     * @private
     */
    _showConfirmationModal(title, message, confirmText = 'Confirm', cancelText = 'Cancel') {
        return new Promise(resolve => {
            // Create modal container if it doesn't exist
            let modalContainer = document.getElementById('adEditorConfirmModal');
            if (!modalContainer) {
                modalContainer = document.createElement('div');
                modalContainer.id = 'adEditorConfirmModal';
                document.body.appendChild(modalContainer);
            }
            
            // Set up modal HTML
            modalContainer.innerHTML = `
                <div class="modal-overlay">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3>${title}</h3>
                            <button class="modal-close" aria-label="Close">×</button>
                        </div>
                        <div class="modal-body">
                            <p>${message}</p>
                            <div class="form-actions">
                                <button type="button" class="btn btn-secondary" id="cancelConfirmBtn">${cancelText}</button>
                                <button type="button" class="btn btn-primary" id="confirmBtn">${confirmText}</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Add modal styles if not already added (styles are shared with template modal)
            if (!document.getElementById('adEditorModalStyles')) {
                // Modal styles already added by template modal
                // If not, they would be added here
            }
            
            // Show modal
            modalContainer.style.display = 'block';
            
            // Focus the confirm button
            setTimeout(() => {
                const confirmBtn = document.getElementById('confirmBtn');
                if (confirmBtn) {
                    confirmBtn.focus();
                }
            }, 100);
            
            // Handle confirm
            const confirmBtn = document.getElementById('confirmBtn');
            if (confirmBtn) {
                confirmBtn.addEventListener('click', () => {
                    modalContainer.style.display = 'none';
                    resolve(true);
                });
            }
            
            // Handle cancel
            const cancelBtn = document.getElementById('cancelConfirmBtn');
            if (cancelBtn) {
                cancelBtn.addEventListener('click', () => {
                    modalContainer.style.display = 'none';
                    resolve(false);
                });
            }
            
            // Handle close
            const closeBtn = modalContainer.querySelector('.modal-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    modalContainer.style.display = 'none';
                    resolve(false);
                });
            }
            
            // Close on outside click
            modalContainer.querySelector('.modal-overlay').addEventListener('click', (e) => {
                if (e.target === modalContainer.querySelector('.modal-overlay')) {
                    modalContainer.style.display = 'none';
                    resolve(false);
                }
            });
            
            // Handle escape key
            const handleEscape = (e) => {
                if (e.key === 'Escape') {
                    modalContainer.style.display = 'none';
                    resolve(false);
                    document.removeEventListener('keydown', handleEscape);
                }
            };
            document.addEventListener('keydown', handleEscape);
        });
    }
    
    /**
     * Load a template
     * @param {string|Object} template - Template name, ID or template object
     * @returns {Promise<boolean>} - Success status
     */
    async loadTemplate(template) {
        try {
            let templateData;
            
            // If template is an object, use it directly
            if (typeof template === 'object') {
                templateData = template;
            } else {
                // Otherwise fetch it by ID
                templateData = await adTemplateService.getTemplate(template);
            }
            
            if (!templateData || !templateData.data) {
                toastService.error('Template not found or invalid');
                return false;
            }
            
            // Apply template data
            this.adData = { ...templateData.data };
            
            // Update UI controls and preview
            this.updateControlValues();
            this.updateCharacterCount('adHeadline', 'headlineCount');
            this.updateCharacterCount('adText', 'textCount');
            this.updatePreview();
            
            // Show success message
            toastService.success(`Template "${templateData.name}" loaded successfully`);
            return true;
        } catch (error) {
            toastService.error(`Error loading template: ${error.message}`);
            console.error('Error loading template:', error);
            return false;
        }
    }
    
    /**
     * Load templates and display template gallery
     */
    showTemplateGallery() {
        // Fetch templates first
        adTemplateService.getTemplates()
            .then(templates => {
                if (!templates || templates.length === 0) {
                    toastService.info('No saved templates found');
                    return;
                }
                
                this._showTemplateGalleryModal(templates);
            })
            .catch(error => {
                toastService.error(`Error loading templates: ${error.message}`);
                console.error('Error loading templates:', error);
            });
    }
    
    /**
     * Show template gallery modal
     * @param {Array} templates - List of templates
     * @private
     */
    _showTemplateGalleryModal(templates) {
        // Create modal container if it doesn't exist
        let modalContainer = document.getElementById('templateGalleryModal');
        if (!modalContainer) {
            modalContainer = document.createElement('div');
            modalContainer.id = 'templateGalleryModal';
            document.body.appendChild(modalContainer);
        }
        
        // Generate template cards HTML
        const templateCardsHtml = templates.map(template => `
            <div class="template-card" data-template-id="${template.id || ''}">
                <div class="template-preview" style="
                    background-color: ${template.data?.backgroundColor || '#ffffff'};
                    color: ${template.data?.textColor || '#333333'};
                    border-radius: ${template.data?.borderRadius || '0'}px;
                    font-family: ${template.data?.fontFamily || 'inherit'};
                ">
                    <div class="template-headline" style="color: ${template.data?.headlineColor || '#000000'}">
                        ${template.data?.headline || 'Template Preview'}
                    </div>
                    <div class="template-button" style="
                        background-color: ${template.data?.buttonColor || '#4361ee'};
                        color: ${template.data?.buttonTextColor || '#ffffff'};
                        border-radius: ${template.data?.borderRadius || '0'}px;
                    ">
                        ${this._getCtaText(template.data?.cta)}
                    </div>
                </div>
                <div class="template-card-footer">
                    <div class="template-name">${template.name}</div>
                    <div class="template-date">${this._formatDate(template.createdAt)}</div>
                    <div class="template-actions">
                        <button class="template-load-btn" data-template-id="${template.id || ''}" title="Load template">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="template-delete-btn" data-template-id="${template.id || ''}" title="Delete template">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Set up modal HTML
        modalContainer.innerHTML = `
            <div class="modal-overlay">
                <div class="modal-content template-gallery-modal">
                    <div class="modal-header">
                        <h3>Template Gallery</h3>
                        <button class="modal-close" aria-label="Close">×</button>
                    </div>
                    <div class="modal-body">
                        <div class="template-gallery">
                            ${templateCardsHtml}
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" id="closeGalleryBtn">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add gallery specific styles if not already added
        if (!document.getElementById('templateGalleryStyles')) {
            const styleEl = document.createElement('style');
            styleEl.id = 'templateGalleryStyles';
            styleEl.textContent = `
                .template-gallery-modal {
                    max-width: 900px;
                    width: 90%;
                    max-height: 80vh;
                    display: flex;
                    flex-direction: column;
                }
                
                .template-gallery-modal .modal-body {
                    overflow-y: auto;
                    padding: 12px;
                }
                
                .template-gallery {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                    gap: 16px;
                }
                
                .template-card {
                    border: 1px solid #eee;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    transition: transform 0.2s, box-shadow 0.2s;
                }
                
                .template-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }
                
                .template-preview {
                    height: 120px;
                    padding: 16px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                }
                
                .template-headline {
                    font-weight: bold;
                    margin-bottom: 8px;
                    font-size: 14px;
                    line-height: 1.4;
                    max-height: 40px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    display: -webkit-box;
                    -webkit-line-clamp: 2;
                    -webkit-box-orient: vertical;
                }
                
                .template-button {
                    padding: 6px 12px;
                    font-size: 12px;
                    font-weight: 500;
                    display: inline-block;
                    margin-top: auto;
                    text-align: center;
                }
                
                .template-card-footer {
                    padding: 12px;
                    background-color: #f8f9fa;
                }
                
                .template-name {
                    font-weight: 500;
                    margin-bottom: 4px;
                }
                
                .template-date {
                    font-size: 12px;
                    color: #666;
                    margin-bottom: 8px;
                }
                
                .template-actions {
                    display: flex;
                    gap: 8px;
                    justify-content: flex-end;
                }
                
                .template-actions button {
                    background: none;
                    border: none;
                    cursor: pointer;
                    padding: 4px 8px;
                    border-radius: 4px;
                }
                
                .template-load-btn {
                    color: #4361ee;
                }
                
                .template-delete-btn {
                    color: #dc3545;
                }
                
                .template-actions button:hover {
                    background-color: rgba(0,0,0,0.05);
                }
                
                .modal-footer {
                    padding: 16px 24px;
                    border-top: 1px solid #eee;
                    text-align: right;
                }
            `;
            document.head.appendChild(styleEl);
        }
        
        // Show modal
        modalContainer.style.display = 'block';
        
        // Handle load template
        const loadButtons = modalContainer.querySelectorAll('.template-load-btn');
        loadButtons.forEach(button => {
            button.addEventListener('click', async () => {
                const templateId = button.getAttribute('data-template-id');
                if (templateId) {
                    const template = templates.find(t => t.id === templateId);
                    if (template) {
                        modalContainer.style.display = 'none';
                        await this.loadTemplate(template);
                    }
                }
            });
        });
        
        // Handle delete template
        const deleteButtons = modalContainer.querySelectorAll('.template-delete-btn');
        deleteButtons.forEach(button => {
            button.addEventListener('click', async () => {
                const templateId = button.getAttribute('data-template-id');
                if (templateId) {
                    const template = templates.find(t => t.id === templateId);
                    if (template) {
                        // Show confirmation dialog
                        const confirmed = await this._showConfirmationModal(
                            'Delete Template',
                            `Are you sure you want to delete the template "${template.name}"?`,
                            'Delete',
                            'Cancel'
                        );
                        
                        if (confirmed) {
                            try {
                                await adTemplateService.deleteTemplate(templateId);
                                toastService.success(`Template "${template.name}" deleted successfully`);
                                
                                // Remove template card from gallery
                                const card = button.closest('.template-card');
                                if (card) {
                                    card.style.opacity = '0';
                                    setTimeout(() => {
                                        card.remove();
                                        
                                        // If no templates left, close gallery
                                        const remainingCards = modalContainer.querySelectorAll('.template-card');
                                        if (remainingCards.length === 0) {
                                            modalContainer.style.display = 'none';
                                            toastService.info('No more templates available');
                                        }
                                    }, 300);
                                }
                            } catch (error) {
                                toastService.error(`Error deleting template: ${error.message}`);
                            }
                        }
                    }
                }
            });
        });
        
        // Handle close
        const closeBtn = modalContainer.querySelector('.modal-close');
        const closeGalleryBtn = document.getElementById('closeGalleryBtn');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                modalContainer.style.display = 'none';
            });
        }
        
        if (closeGalleryBtn) {
            closeGalleryBtn.addEventListener('click', () => {
                modalContainer.style.display = 'none';
            });
        }
        
        // Close on outside click
        modalContainer.querySelector('.modal-overlay').addEventListener('click', (e) => {
            if (e.target === modalContainer.querySelector('.modal-overlay')) {
                modalContainer.style.display = 'none';
            }
        });
        
        // Handle escape key
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                modalContainer.style.display = 'none';
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
    }
    
    /**
     * Get CTA button text from code
     * @param {string} ctaCode - CTA code
     * @returns {string} - CTA text
     * @private
     */
    _getCtaText(ctaCode) {
        switch (ctaCode) {
            case 'apply_now': return 'Apply Now';
            case 'learn_more': return 'Learn More';
            case 'see_jobs': return 'See Jobs';
            case 'sign_up': return 'Sign Up';
            default: return 'Apply Now';
        }
    }
    
    /**
     * Format date string
     * @param {string} dateString - ISO date string
     * @returns {string} - Formatted date
     * @private
     */
    _formatDate(dateString) {
        if (!dateString) return '';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString(undefined, { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
            });
        } catch (e) {
            return dateString;
        }
    }
    
    /**
     * Update ad preview based on current data
     */
    updatePreview() {
        if (this.isEditing) return; // Don't update while user is editing
        
        // Get text content from inputs if they exist
        const adHeadline = document.getElementById('adHeadline');
        const adText = document.getElementById('adText');
        const adCta = document.getElementById('adCta');
        
        const headline = adHeadline ? adHeadline.value : this.adData.headline;
        const text = adText ? adText.value : this.adData.text;
        const cta = adCta ? adCta.value : this.adData.cta;
        
        // Update Meta preview
        const metaPreview = document.getElementById('metaAdPreview');
        if (metaPreview) {
            const previewHeadline = metaPreview.querySelector('.preview-headline');
            const previewDescription = metaPreview.querySelector('.preview-description');
            const previewImage = metaPreview.querySelector('.preview-image img');
            const previewButton = metaPreview.querySelector('.preview-cta button');
            
            if (previewHeadline) previewHeadline.textContent = headline || 'Your compelling headline will appear here';
            if (previewDescription) previewDescription.textContent = text || 'Your ad description will appear here. Make it engaging to attract the right candidates for the job opening.';
            if (previewImage) previewImage.src = this.adData.imageUrl;
            
            if (previewButton) {
                switch (cta) {
                    case 'apply_now':
                        previewButton.textContent = 'Apply Now';
                        break;
                    case 'learn_more':
                        previewButton.textContent = 'Learn More';
                        break;
                    case 'see_jobs':
                        previewButton.textContent = 'See Jobs';
                        break;
                    case 'sign_up':
                        previewButton.textContent = 'Sign Up';
                        break;
                    default:
                        previewButton.textContent = 'Apply Now';
                }
                
                previewButton.style.backgroundColor = this.adData.buttonColor;
                previewButton.style.color = this.adData.buttonTextColor;
                previewButton.style.borderRadius = `${this.adData.borderRadius}px`;
            }
            
            // Apply styles
            metaPreview.style.fontFamily = this.adData.fontFamily;
            metaPreview.style.backgroundColor = this.adData.backgroundColor;
            
            if (previewHeadline) previewHeadline.style.color = this.adData.headlineColor;
            if (previewDescription) previewDescription.style.color = this.adData.textColor;
        }
        
        // Update Google preview
        const googlePreview = document.getElementById('googleAdPreview');
        if (googlePreview) {
            const googleHeadline = googlePreview.querySelector('.google-headline');
            const googleDescription = googlePreview.querySelector('.google-description');
            
            if (googleHeadline) googleHeadline.textContent = headline || 'Your compelling headline will appear here';
            if (googleDescription) googleDescription.textContent = text || 'Your ad description will appear here. Make it engaging to attract the right candidates.';
            
            // Apply styles
            googlePreview.style.fontFamily = this.adData.fontFamily;
            
            if (googleHeadline) googleHeadline.style.color = this.adData.headlineColor;
            if (googleDescription) googleDescription.style.color = this.adData.textColor;
        }
        
        // Update Twitter preview
        const twitterPreview = document.getElementById('twitterAdPreview');
        if (twitterPreview) {
            const tweetText = twitterPreview.querySelector('.tweet-text');
            const tweetImage = twitterPreview.querySelector('.tweet-image img');
            
            if (tweetText) tweetText.textContent = `${headline}: ${text} #JobOpening #Hiring`.trim();
            if (tweetImage) tweetImage.src = this.adData.imageUrl;
            
            // Apply styles
            twitterPreview.style.fontFamily = this.adData.fontFamily;
            
            if (tweetText) tweetText.style.color = this.adData.textColor;
        }
    }
    
    /**
     * Update adData based on contenteditable elements
     */
    updateAdDataFromEditable() {
        if (!this.selectedElement) return;
        
        const element = this.selectedElement;
        
        if (element.classList.contains('preview-headline')) {
            this.adData.headline = element.textContent;
            const adHeadline = document.getElementById('adHeadline');
            if (adHeadline) adHeadline.value = this.adData.headline;
            this.updateCharacterCount('adHeadline', 'headlineCount');
        } else if (element.classList.contains('preview-description')) {
            this.adData.text = element.textContent;
            const adText = document.getElementById('adText');
            if (adText) adText.value = this.adData.text;
            this.updateCharacterCount('adText', 'textCount');
        } else if (element.classList.contains('google-headline')) {
            this.adData.headline = element.textContent;
            const adHeadline = document.getElementById('adHeadline');
            if (adHeadline) adHeadline.value = this.adData.headline;
            this.updateCharacterCount('adHeadline', 'headlineCount');
        } else if (element.classList.contains('google-description')) {
            this.adData.text = element.textContent;
            const adText = document.getElementById('adText');
            if (adText) adText.value = this.adData.text;
            this.updateCharacterCount('adText', 'textCount');
        } else if (element.classList.contains('tweet-text')) {
            // Parse tweet text to extract headline and text
            const tweetText = element.textContent;
            const colonIndex = tweetText.indexOf(':');
            
            if (colonIndex > 0) {
                const headline = tweetText.substring(0, colonIndex).trim();
                let text = tweetText.substring(colonIndex + 1).trim();
                
                // Remove hashtags
                const hashtagIndex = text.indexOf('#');
                if (hashtagIndex > 0) {
                    text = text.substring(0, hashtagIndex).trim();
                }
                
                this.adData.headline = headline;
                this.adData.text = text;
                
                const adHeadline = document.getElementById('adHeadline');
                const adText = document.getElementById('adText');
                
                if (adHeadline) adHeadline.value = this.adData.headline;
                if (adText) adText.value = this.adData.text;
                
                this.updateCharacterCount('adHeadline', 'headlineCount');
                this.updateCharacterCount('adText', 'textCount');
            }
        }
    }
    
    /**
     * Get the current ad data
     */
    getAdData() {
        return { ...this.adData };
    }
}

// Initialize the editor when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if the editor container exists
    if (document.getElementById('adVisualEditor')) {
        window.adEditor = new AdVisualEditor('adVisualEditor');
    }
});