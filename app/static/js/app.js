/**
 * MagnetoCursor - Advanced Ad Automation
 * Modern UI components and interactions
 * Version 2.0
 */

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle functionality
    initializeSidebar();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize dropdowns
    initializeDropdowns();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Add page transition animations
    addPageTransitions();
    
    // Dark mode toggle (if exists)
    initializeDarkMode();
    
    // Add scroll animations if library exists
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true
        });
    }
});

/**
 * Initialize sidebar behavior
 */
function initializeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const mobileToggle = document.getElementById('mobile-toggle');
    const mainContent = document.querySelector('.main-content');
    
    // Check for saved state
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (sidebarCollapsed && sidebar) {
        sidebar.classList.add('collapsed');
        if (mainContent) mainContent.classList.add('collapsed-sidebar');
    }
    
    // Desktop sidebar toggle
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            if (mainContent) mainContent.classList.toggle('collapsed-sidebar');
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        });
    }
    
    // Mobile sidebar toggle
    if (mobileToggle && sidebar) {
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.toggle('expanded');
        });
    }
    
    // Close mobile sidebar when clicking outside
    document.addEventListener('click', function(event) {
        if (!sidebar) return;
        
        const isClickInside = sidebar.contains(event.target) || 
                             (mobileToggle && mobileToggle.contains(event.target));
        
        if (!isClickInside && sidebar.classList.contains('expanded') && window.innerWidth < 992) {
            sidebar.classList.remove('expanded');
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (sidebar && sidebar.classList.contains('expanded') && window.innerWidth >= 992) {
            sidebar.classList.remove('expanded');
        }
    });
}

/**
 * Initialize tooltips functionality
 */
function initializeTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    
    tooltipTriggerList.forEach(function(tooltipTriggerEl) {
        tooltipTriggerEl.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.classList.add('tooltip');
            tooltip.textContent = this.getAttribute('data-bs-title');
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            
            setTimeout(() => tooltip.classList.add('show'), 10);
            
            this.addEventListener('mouseleave', function() {
                tooltip.classList.remove('show');
                setTimeout(() => tooltip.remove(), 300);
            }, { once: true });
        });
    });
}

/**
 * Initialize dropdown functionality
 */
function initializeDropdowns() {
    const userProfile = document.querySelector('.user-profile');
    
    if (userProfile) {
        userProfile.addEventListener('click', function(event) {
            event.stopPropagation();
            
            // Check if dropdown already exists
            const existingDropdown = document.querySelector('.user-dropdown');
            if (existingDropdown) {
                existingDropdown.remove();
                return;
            }
            
            // Create dropdown
            const dropdown = document.createElement('div');
            dropdown.classList.add('user-dropdown');
            
            const dropdownItems = [
                { icon: 'user', text: 'Profile', link: '#' },
                { icon: 'cog', text: 'Settings', link: '#' },
                { icon: 'sign-out-alt', text: 'Logout', link: '#' }
            ];
            
            dropdownItems.forEach(item => {
                const link = document.createElement('a');
                link.href = item.link;
                link.innerHTML = `<i class="fas fa-${item.icon}"></i> ${item.text}`;
                dropdown.appendChild(link);
            });
            
            // Position dropdown
            const rect = userProfile.getBoundingClientRect();
            dropdown.style.top = rect.bottom + 10 + 'px';
            dropdown.style.right = 10 + 'px';
            
            document.body.appendChild(dropdown);
            
            // Show dropdown with animation
            setTimeout(() => dropdown.classList.add('show'), 10);
            
            // Close dropdown when clicking outside
            document.addEventListener('click', function() {
                if (dropdown) {
                    dropdown.classList.remove('show');
                    setTimeout(() => dropdown.remove(), 300);
                }
            }, { once: true });
        });
    }
    
    // Custom dropdowns
    const dropdownButtons = document.querySelectorAll('.dropdown > button');
    dropdownButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const dropdown = document.createElement('div');
            dropdown.classList.add('custom-dropdown');
            
            // Create dropdown based on button id
            if (button.id === 'sortDropdown') {
                const options = [
                    'Name (A-Z)',
                    'Name (Z-A)',
                    'Size (Largest first)',
                    'Size (Smallest first)',
                    'Date Created (Newest first)',
                    'Date Created (Oldest first)'
                ];
                
                options.forEach(option => {
                    const item = document.createElement('a');
                    item.href = '#';
                    item.textContent = option;
                    item.addEventListener('click', function(e) {
                        e.preventDefault();
                        console.log('Sort by:', option);
                        dropdown.remove();
                    });
                    dropdown.appendChild(item);
                });
            }
            
            // Position dropdown
            const rect = button.getBoundingClientRect();
            dropdown.style.top = rect.bottom + 5 + 'px';
            dropdown.style.left = rect.left + 'px';
            
            document.body.appendChild(dropdown);
            
            // Show dropdown with animation
            setTimeout(() => dropdown.classList.add('show'), 10);
            
            // Close dropdown when clicking outside
            document.addEventListener('click', function() {
                dropdown.classList.remove('show');
                setTimeout(() => dropdown.remove(), 300);
            }, { once: true });
        });
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form.needs-validation');
    
    forms.forEach(form => {
        // Stop form submission for invalid forms
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
        
        // Live validation as user types
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                checkInput(input);
            });
            
            input.addEventListener('input', function() {
                if (input.classList.contains('is-invalid')) {
                    checkInput(input);
                }
            });
        });
    });
}

/**
 * Check validity of a single input
 * @param {HTMLElement} input - Input element to validate
 */
function checkInput(input) {
    const feedbackElement = input.nextElementSibling;
    
    if (input.checkValidity()) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        
        if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
            feedbackElement.style.display = 'none';
        }
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
        
        if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
            feedbackElement.style.display = 'block';
        }
    }
}

/**
 * Add page transition animations
 */
function addPageTransitions() {
    // Add animation classes to elements
    document.querySelectorAll('.animate-fadeIn').forEach((element, index) => {
        element.style.animationDelay = `${index * 0.1}s`;
    });
    
    document.querySelectorAll('.animate-slideInLeft').forEach((element, index) => {
        element.style.animationDelay = `${index * 0.1}s`;
    });
    
    document.querySelectorAll('.animate-slideInRight').forEach((element, index) => {
        element.style.animationDelay = `${index * 0.1}s`;
    });
    
    document.querySelectorAll('.animate-slideInUp').forEach((element, index) => {
        element.style.animationDelay = `${index * 0.1}s`;
    });
}

/**
 * Initialize dark mode toggle functionality
 */
function initializeDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    
    if (darkModeToggle) {
        // Check for saved preference
        const prefersDarkMode = localStorage.getItem('darkMode') === 'true';
        
        if (prefersDarkMode) {
            document.documentElement.setAttribute('data-theme', 'dark');
        }
        
        darkModeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            
            if (currentTheme === 'dark') {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('darkMode', 'false');
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('darkMode', 'true');
            }
        });
    }
}

/**
 * Create loading indicator
 * Use this for AJAX requests
 * @param {HTMLElement} container - Container to show loader in
 * @returns {HTMLElement} - The loader element
 */
function createLoader(container) {
    const loader = document.createElement('div');
    loader.classList.add('loader');
    loader.innerHTML = `
        <div class="spinner"></div>
        <p>Loading...</p>
    `;
    
    if (container) {
        container.appendChild(loader);
    }
    
    return loader;
}

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, error, warning, info)
 * @param {number} duration - How long to show the toast in ms
 */
function showToast(message, type = 'info', duration = 3000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.classList.add('toast-container');
        document.body.appendChild(toastContainer);
    }
    
    // Create toast
    const toast = document.createElement('div');
    toast.classList.add('toast', `toast-${type}`);
    
    // Add icon based on type
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'exclamation-circle';
    if (type === 'warning') icon = 'exclamation-triangle';
    
    toast.innerHTML = `
        <div class="toast-icon">
            <i class="fas fa-${icon}"></i>
        </div>
        <div class="toast-content">
            <p>${message}</p>
        </div>
        <button class="toast-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Show with animation
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Handle close button
    const closeButton = toast.querySelector('.toast-close');
    closeButton.addEventListener('click', () => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    });
    
    // Auto dismiss after duration
    setTimeout(() => {
        if (toast.parentNode) {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
}

// Add toast and loader styles
const style = document.createElement('style');
style.textContent = `
    /* Toast notifications */
    .toast-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    .toast {
        display: flex;
        align-items: center;
        background: white;
        border-radius: var(--radius);
        padding: 12px 16px;
        box-shadow: var(--shadow-lg);
        min-width: 300px;
        max-width: 450px;
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.3s ease;
    }
    
    .toast.show {
        opacity: 1;
        transform: translateY(0);
    }
    
    .toast-success {
        border-left: 4px solid var(--success-500);
    }
    
    .toast-error {
        border-left: 4px solid var(--danger-500);
    }
    
    .toast-warning {
        border-left: 4px solid var(--warning-500);
    }
    
    .toast-info {
        border-left: 4px solid var(--primary-500);
    }
    
    .toast-icon {
        margin-right: 12px;
        font-size: 18px;
    }
    
    .toast-success .toast-icon {
        color: var(--success-500);
    }
    
    .toast-error .toast-icon {
        color: var(--danger-500);
    }
    
    .toast-warning .toast-icon {
        color: var(--warning-500);
    }
    
    .toast-info .toast-icon {
        color: var(--primary-500);
    }
    
    .toast-content {
        flex: 1;
    }
    
    .toast-content p {
        margin: 0;
    }
    
    .toast-close {
        background: none;
        border: none;
        cursor: pointer;
        color: var(--neutral-400);
        transition: color 0.2s ease;
    }
    
    .toast-close:hover {
        color: var(--neutral-600);
    }
    
    /* Loader */
    .loader {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    
    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid var(--neutral-200);
        border-top: 4px solid var(--primary-500);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 10px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Custom dropdown */
    .custom-dropdown {
        position: absolute;
        background-color: white;
        border-radius: var(--radius);
        box-shadow: var(--shadow-lg);
        min-width: 180px;
        z-index: var(--z-dropdown);
        overflow: hidden;
        opacity: 0;
        transform: translateY(-10px);
        transition: opacity var(--transition-fast) var(--ease-out),
                    transform var(--transition-fast) var(--ease-out);
    }
    
    .custom-dropdown.show {
        opacity: 1;
        transform: translateY(0);
    }
    
    .custom-dropdown a {
        display: block;
        padding: 10px 15px;
        color: var(--text-dark);
        text-decoration: none;
        transition: background-color 0.2s ease;
    }
    
    .custom-dropdown a:hover {
        background-color: var(--neutral-100);
    }
`;

document.head.appendChild(style);