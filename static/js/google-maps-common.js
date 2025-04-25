// Common utility functions and tab switching logic for scraper-sky-mvp.html

// Utility function to safely get JWT token
function getJwtToken() {
    const jwtInput = document.getElementById('jwt'); // Assumes input with ID 'jwt' exists
    return jwtInput ? jwtInput.value : null;
}

// Utility function to display status messages
function showStatus(message, type = 'info', elementId = 'status') {
    let statusElement = document.getElementById(elementId);
    if (!statusElement) {
        console.error(`Status element with ID "${elementId}" not found.`);
        // Optionally create a default status area if needed, depending on context
        return; // Exit if element not found
    }
    statusElement.textContent = message;
    statusElement.className = `alert alert-${type === 'error' ? 'danger' : type}`; // Map 'error' to 'danger' for Bootstrap
    statusElement.style.display = 'block';
    // Optional: Hide after a delay?
    // setTimeout(() => { statusElement.style.display = 'none'; }, 5000);
}

// Utility function to debug fetch requests
window.debugFetch = function(url, options) {
    console.log(`[DEBUG] Fetch request to: ${url}`);
    console.log('[DEBUG] Fetch options:', options);

    return fetch(url, options)
        .then(response => {
            console.log(`[DEBUG] Response status: ${response.status}`);
            // Clone response to read text without consuming the body for subsequent handlers
            return response.clone().text().then(text => {
                try {
                    // Attempt to parse as JSON for logging
                    const data = JSON.parse(text);
                    console.log('[DEBUG] Response data (JSON):', data);
                } catch (e) {
                    // Log as text if not JSON
                    console.log('[DEBUG] Response data (Text):', text);
                }
                return response; // Return the original response for chaining
            });
        })
        .catch(error => {
            console.error('[DEBUG] Fetch error:', error);
            throw error; // Re-throw the error for proper error handling
        });
};

// Tab Switching Logic
document.addEventListener('DOMContentLoaded', function() {
    console.log("Google Maps Common JS Loaded and DOM ready");

    const tabs = document.querySelectorAll('.tab');
    const panels = document.querySelectorAll('.panel');
    const jwtInput = document.getElementById('jwt'); // Needed for initial fetch calls

    if (!tabs.length || !panels.length) {
        console.error("Could not find tab or panel elements for setup.");
        return;
    }

    tabs.forEach((tab) => {
        tab.addEventListener('click', function() {
            // Deactivate all
            tabs.forEach(t => t.classList.remove('tab-active'));
            panels.forEach(p => p.classList.remove('panel-active'));

            // Activate clicked
            this.classList.add('tab-active');
            const panelId = this.dataset.panel;
            const panel = document.getElementById(panelId);
            if (panel) {
                panel.classList.add('panel-active');
            } else {
                console.error(`Panel with ID ${panelId} not found`);
            }

            // Trigger data fetch for specific tabs when they become active
            // Ensure the corresponding functions are globally available or defined within this common scope
            // Note: Specific fetch functions (like fetchStagingData) will be moved to their respective files later.
            // The initial fetch might need to be triggered differently after refactoring.
            console.log(`Tab ${panelId} activated. Triggering fetch if necessary.`);
            switch (panelId) {
                case 'singleSearch':
                    if (typeof fetchSearchHistory === 'function') fetchSearchHistory();
                    break;
                case 'stagingEditor':
                    if (typeof fetchStagingData === 'function') fetchStagingData(1);
                    break;
                case 'localBusinessCuration':
                    if (typeof fetchLocalBusinessData === 'function') fetchLocalBusinessData(1);
                    break;
                case 'domainCurationPanel':
                    if (typeof fetchDomainCurationData === 'function') fetchDomainCurationData(1);
                    break;
                case 'sitemapCurationPanel': // Assumes function exists in sitemap-curation-tab.js
                    if (typeof fetchSitemapData === 'function') fetchSitemapData(1);
                    break;
                // Add cases for batchSearchPanel and resultsView if they need data on activation
            }
        });
    });

    // Global error handlers (moved inside DOMContentLoaded)
    window.addEventListener('error', function(e) {
        console.error('Global error caught:', e.error || e.message, e);
    });

    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled Promise rejection caught:', e.reason);
    });

    // Initial data load for the default active tab (assuming it's singleSearch)
    const initialActiveTab = document.querySelector('.tab.tab-active');
    if (initialActiveTab && initialActiveTab.dataset.panel === 'singleSearch') {
        if (typeof fetchSearchHistory === 'function') {
             console.log("Initial load: Fetching search history for default tab.");
            fetchSearchHistory();
        }
    }
    // Add similar checks if other tabs could be the default
    else if (initialActiveTab && initialActiveTab.dataset.panel === 'stagingEditor') {
         if (typeof fetchStagingData === 'function') fetchStagingData(1);
    }
     else if (initialActiveTab && initialActiveTab.dataset.panel === 'localBusinessCuration') {
         if (typeof fetchLocalBusinessData === 'function') fetchLocalBusinessData(1);
    }
    else if (initialActiveTab && initialActiveTab.dataset.panel === 'domainCurationPanel') {
         if (typeof fetchDomainCurationData === 'function') fetchDomainCurationData(1);
    }
    else if (initialActiveTab && initialActiveTab.dataset.panel === 'sitemapCurationPanel') {
         if (typeof fetchSitemapData === 'function') fetchSitemapData(1);
    }

});
