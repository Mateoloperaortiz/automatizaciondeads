/**
 * MagnetoCursor Tooltip System
 * 
 * This script provides interactive tooltips for technical terms and concepts
 * throughout the application. It scans for elements with data-tooltip attributes
 * and initializes Bootstrap tooltips with technical explanations.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Technical term definitions
    const tooltipDefinitions = {
        // Campaign related terms
        'campaign': 'A structured advertising initiative targeting specific audience segments with job openings on social media platforms.',
        'campaign-status': 'The current state of a campaign: draft (not published), active (running), paused (temporarily stopped), completed (finished), or rejected.',
        'campaign-budget': 'The maximum amount to spend on a campaign across all platforms. Can be set as daily, lifetime, or per-platform.',
        
        // Audience segmentation related terms
        'segment': 'A group of potential candidates with similar characteristics, created through machine learning clustering algorithms.',
        'segmentation': 'The process of dividing potential candidates into groups based on demographics, experience, interests, or behavior.',
        'clustering': 'A machine learning technique used to group similar candidates together based on their attributes.',
        'k-means': 'A specific clustering algorithm that groups data points into k clusters by minimizing the variance within each cluster.',
        'silhouette-score': 'A metric measuring how well-defined clusters are, ranging from -1 to 1, with higher values indicating better clustering.',
        
        // Social media platform related terms
        'meta-ads': 'The advertising platform for Facebook and Instagram, allowing targeted job ads based on user interests, demographics, and behaviors.',
        'x-ads': 'The advertising platform for X (formerly Twitter), enabling targeted job ads based on user interests, keywords, and engagement behavior.',
        'google-ads': 'Google\'s advertising platform that can display job ads on Google Search, YouTube, and partner websites based on search queries and interests.',
        'conversion-tracking': 'The process of measuring when users complete desired actions after seeing an ad, such as submitting a job application.',
        
        // API related terms
        'api': 'Application Programming Interface - a set of rules and protocols that allows different software applications to communicate with each other.',
        'api-key': 'A unique identifier used to authenticate API requests from your application to the MagnetoCursor API.',
        'rest-api': 'Representational State Transfer API - an architectural style for designing networked applications that uses HTTP requests to access and manipulate data.',
        'endpoint': 'A specific URL in the API that represents a resource or functionality that can be accessed by clients.',
        'rate-limit': 'A restriction on the number of API requests a client can make within a specified time period.',
        
        // Authentication related terms
        'oauth': 'An open standard for access delegation, commonly used to grant applications limited access to user accounts on services without sharing credentials.',
        'token': 'A temporary authentication credential used to access resources after successful authentication.',
        'jwt': 'JSON Web Token - a compact, URL-safe means of representing claims to be transferred between two parties.',
        
        // Collaboration related terms
        'collaboration': 'The ability for multiple users to work together on campaigns with different permission levels.',
        'role': 'A set of permissions that determine what actions a user can perform in the system.',
        'permission': 'A specific authorization to perform certain actions within the system.',
        'team': 'A group of users who can collaborate on campaigns and share resources.'
    };
    
    // Find all elements with data-tooltip attribute
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    // Initialize Bootstrap tooltips for each element
    tooltipElements.forEach(element => {
        const tooltipKey = element.getAttribute('data-tooltip');
        const definition = tooltipDefinitions[tooltipKey] || 'Definition not available';
        
        // Add a question mark icon if not present
        if (!element.querySelector('.tooltip-icon')) {
            const icon = document.createElement('i');
            icon.className = 'bi bi-question-circle-fill tooltip-icon ms-1';
            icon.style.fontSize = '0.75em';
            icon.style.opacity = '0.6';
            element.appendChild(icon);
        }
        
        // Initialize Bootstrap tooltip
        new bootstrap.Tooltip(element, {
            title: definition,
            html: true,
            placement: element.getAttribute('data-tooltip-placement') || 'top'
        });
        
        // Add hover styling
        element.classList.add('has-tooltip');
    });
    
    // Add global tooltip styling
    if (!document.getElementById('tooltip-styles')) {
        const style = document.createElement('style');
        style.id = 'tooltip-styles';
        style.textContent = `
            .has-tooltip {
                text-decoration: underline dotted;
                cursor: help;
            }
            .tooltip-icon {
                color: #6c757d;
            }
            .has-tooltip:hover .tooltip-icon {
                color: #007bff;
            }
            .tooltip {
                max-width: 300px;
            }
            .tooltip-inner {
                text-align: left;
                padding: 10px;
                font-size: 0.9rem;
                box-shadow: 0 2px 5px rgba(0,0,0,0.15);
            }
        `;
        document.head.appendChild(style);
    }
});

/**
 * Dynamically adds a tooltip to any element
 * @param {string} selector - CSS selector for the element to add tooltip to
 * @param {string} term - The technical term key (from tooltipDefinitions)
 * @param {string} placement - Optional tooltip placement (top, bottom, left, right)
 */
function addTooltipToElement(selector, term, placement = 'top') {
    const element = document.querySelector(selector);
    if (element) {
        element.setAttribute('data-tooltip', term);
        element.setAttribute('data-tooltip-placement', placement);
        
        // Reinitialize tooltips
        const event = new Event('tooltips:reinitialize');
        document.dispatchEvent(event);
    }
}