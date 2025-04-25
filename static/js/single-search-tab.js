// JavaScript logic for the Single Search tab in scraper-sky-mvp.html
document.addEventListener('DOMContentLoaded', function() {
    console.log("Single Search Tab JS Loaded");

    // Ensure common functions are available (assuming google-maps-common.js loaded first)
    if (typeof getJwtToken !== 'function' || typeof showStatus !== 'function') {
        console.error("Common utility functions not found. Ensure google-maps-common.js is loaded before this script.");
        // return; // Optional: Stop execution if common functions are missing
    }

    // Single Search Variables & Elements
    const searchBtn = document.getElementById('searchBtn');
    const statusDiv = document.getElementById('status');
    const statusContent = document.getElementById('statusContent');
    const progressFill = document.getElementById('progressFill');
    const searchHistoryList = document.getElementById('searchHistoryList');
    const refreshHistoryBtn = document.getElementById('refreshHistoryBtn');
    // Potentially shared variables (consider scoping or global access)
    let currentJobId = null; // Specific to single search status checking
    let statusCheckInterval = null;
    // let lastCompletedJobId = null; // This seems shared with Results Viewer - Needs careful handling

    // Function to fetch search history
    function fetchSearchHistory() {
        // const tenant = document.getElementById('tenant').value; // Defined in HTML, accessible globally
        const jwt = getJwtToken(); // Use common function

        if (!jwt) {
            if (searchHistoryList) searchHistoryList.innerHTML = '<p class="placeholder">Please enter a JWT token</p>';
            return;
        }

        if (!searchHistoryList) {
            console.error("Search history list element not found.");
            return;
        }
        searchHistoryList.innerHTML = '<p class="placeholder">Loading search history...</p>';

        // Use debugFetch if available
        const fetchFn = typeof debugFetch === 'function' ? debugFetch : fetch;

        // TODO: Update tenant_id handling if needed - currently hardcoded in HTML
        const tenant_id = document.getElementById('tenant')?.value || '550e8400-e29b-41d4-a716-446655440000';

        fetchFn(`/api/v3/localminer-discoveryscan/search/history?limit=10&tenant_id=${tenant_id}`, {
            headers: {
                'Authorization': `Bearer ${jwt}`
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.detail || 'Error fetching search history');
                });
            }
            return response.json();
        })
        .then(data => {
            if (!searchHistoryList) return; // Check again in case element disappears
            if (data.length === 0) {
                searchHistoryList.innerHTML = '<p class="placeholder">No search history found</p>';
                return;
            }

            // Create a table for the search history
            let html = `
                <table class="table" style="color: white;">
                    <thead>
                        <tr>
                            <th>Business Type</th>
                            <th>Location</th>
                            <th>Date</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            data.forEach(search => {
                const date = new Date(search.created_at).toLocaleString();
                const radius = search.params && search.params.radius_km ? search.params.radius_km : 10;

                html += `
                    <tr>
                        <td>${search.business_type || 'N/A'}</td>
                        <td>${search.location || 'N/A'}</td>
                        <td>${date}</td>
                        <td>
                            <button class="reuse-search btn btn-sm btn-outline-info me-1"
                                data-business-type="${search.business_type || ''}"
                                data-location="${search.location || ''}"
                                data-radius="${radius}">
                                Reuse
                            </button>
                            <button class="view-results btn btn-sm btn-outline-light"
                                    data-job-id="${search.id}">
                                Results
                            </button>
                        </td>
                    </tr>
                `;
            });

            html += `
                    </tbody>
                </table>
            `;

            searchHistoryList.innerHTML = html;

            // Add event listeners AFTER table is in the DOM
            searchHistoryList.querySelectorAll('.reuse-search').forEach(button => {
                button.addEventListener('click', function() {
                    document.getElementById('businessType').value = this.dataset.businessType;
                    document.getElementById('location').value = this.dataset.location;
                    document.getElementById('radius').value = this.dataset.radius;
                    // Scroll to the form
                    document.getElementById('businessType').scrollIntoView({ behavior: 'smooth' });
                });
            });

            searchHistoryList.querySelectorAll('.view-results').forEach(button => {
                button.addEventListener('click', function() {
                    // Find the results tab and click it programmatically
                    const resultsTab = document.querySelector('.tab[data-panel="resultsView"]');
                    if (resultsTab) {
                        resultsTab.click(); // This should trigger the tab switch logic in common.js
                        // Now, ensure the fetchResults function (from results-viewer-tab.js) is called
                        // We need to handle potential loading order issues. A small delay might be a temporary workaround,
                        // but a more robust solution involves ensuring fetchResults is defined and callable.
                        if (typeof fetchResults === 'function') {
                             console.log("Calling fetchResults for job ID:" + this.dataset.jobId);
                            fetchResults(this.dataset.jobId);
                        } else {
                            console.error('fetchResults function not found. Check loading order or scope.');
                            // Fallback: Maybe set a global variable?
                            window.requestedJobIdForResults = this.dataset.jobId;
                            alert('Switching to Results tab. Data might load shortly.');
                        }
                    } else {
                        console.error("Could not find Results Viewer tab button.");
                    }
                });
            });
        })
        .catch(error => {
            if (searchHistoryList) searchHistoryList.innerHTML = `<p class="placeholder text-danger">Error fetching search history: ${error.message}</p>`;
        });
    }

    // Fetch search history after a successful search completes
    function updateSearchHistoryAfterSearch() {
        setTimeout(fetchSearchHistory, 1000); // Short delay to ensure database is updated
    }

    // Function to check single search status
    function checkStatus() {
        if (!currentJobId) return;
        const jwt = getJwtToken(); // Use common function

        // Use debugFetch if available
        const fetchFn = typeof debugFetch === 'function' ? debugFetch : fetch;

        fetchFn(`/api/v3/localminer-discoveryscan/search/status/${currentJobId}`, {
            headers: {
                'Authorization': `Bearer ${jwt}`
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    // Stop polling on certain errors (like 404 Not Found)
                    if (response.status === 404) {
                         clearInterval(statusCheckInterval);
                         throw new Error(err.detail || 'Job not found. Stopping status checks.');
                    }
                    throw new Error(err.detail || 'Error checking status');
                });
            }
            return response.json();
        })
        .then(data => {
            let progress = data.progress || 0;
            if (data.status === 'running' || data.status === 'pending') {
                progress = Math.max(0.05, progress); // Show minimal progress for running/pending
            } else if (data.status === 'complete') {
                progress = 1.0;
            }

            if(progressFill) progressFill.style.width = `${progress * 100}%`;

            let statusHtml = `
                <p><strong>Status:</strong> <span class="badge badge-${data.status?.toLowerCase()}">${data.status || 'Unknown'}</span></p>
                <p><strong>Job ID:</strong> ${data.job_id}</p>
                <p><strong>Search Query:</strong> ${data.search_query || 'N/A'} in ${data.search_location || 'N/A'}</p>
            `;

            if (data.total_places !== undefined) {
                statusHtml += `<p><strong>Total Places Found:</strong> ${data.total_places}</p>`;
            }
            if (data.stored_places !== undefined) {
                statusHtml += `<p><strong>Places Stored:</strong> ${data.stored_places}</p>`;
            }
            if (data.created_at) {
                statusHtml += `<p><strong>Started At:</strong> ${new Date(data.created_at).toLocaleString()}</p>`;
            }
            if (data.completed_at) {
                statusHtml += `<p><strong>Completed At:</strong> ${new Date(data.completed_at).toLocaleString()}</p>`;
            }
            if (data.error) {
                statusHtml += `<p class="text-danger"><strong>Error:</strong> ${data.error}</p>`;
            }

            if (statusContent) statusContent.innerHTML = statusHtml;

            if (data.status === 'complete' || data.status === 'failed') {
                clearInterval(statusCheckInterval);
                if(searchBtn) searchBtn.disabled = false;

                if (data.status === 'complete') {
                    // Store the job ID for potential use in Results tab
                    // Needs careful handling if Results Viewer is in separate file
                    window.lastCompletedSingleSearchJobId = currentJobId;

                    // Add a button to view results only if not already present
                    if (statusContent && !document.getElementById('viewResultsBtn')) {
                         const viewResultsBtn = document.createElement('button');
                         viewResultsBtn.id = 'viewResultsBtn';
                         viewResultsBtn.className = 'button-primary btn btn-success mt-3'; // Added btn classes
                         viewResultsBtn.textContent = 'View Results';
                         viewResultsBtn.addEventListener('click', function() {
                             const resultsTab = document.querySelector('.tab[data-panel="resultsView"]');
                             if (resultsTab) resultsTab.click(); // Trigger tab switch
                             // Attempt to call fetchResults after a short delay
                             setTimeout(() => {
                                 if (typeof fetchResults === 'function') {
                                     fetchResults(currentJobId);
                                 } else {
                                     console.error('fetchResults function not available after tab switch.');
                                     window.requestedJobIdForResults = currentJobId;
                                     alert('Switched to Results tab. Loading data...');
                                 }
                            }, 100); // Delay to allow tab switch and script load
                         });
                         statusContent.appendChild(viewResultsBtn);
                    }
                    // Update search history after search completes successfully
                    updateSearchHistoryAfterSearch();
                }
            }
        })
        .catch(error => {
            console.error('Error checking status:', error);
            if (statusContent) statusContent.innerHTML += `<p class="text-danger">Error checking status: ${error.message}</p>`;
            clearInterval(statusCheckInterval);
            if(searchBtn) searchBtn.disabled = false;
        });
    }

    // Event Listener for Single Search Button
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            const businessType = document.getElementById('businessType').value;
            const location = document.getElementById('location').value;
            const radius = document.getElementById('radius').value;
            const maxResults = document.getElementById('maxResults').value;
            const tenant = document.getElementById('tenant').value;
            const jwt = getJwtToken(); // Use common function

            if (!businessType || !location) {
                showStatus('Please enter both business type and location', 'warning');
                return;
            }
            if (!jwt) {
                showStatus('Please enter a JWT token', 'warning');
                return;
            }

            searchBtn.disabled = true;
            if(statusDiv) statusDiv.style.display = 'block';
            if(statusContent) statusContent.innerHTML = '<p>Starting search...</p>';
            if(progressFill) progressFill.style.width = '0%';
            if(statusCheckInterval) clearInterval(statusCheckInterval); // Clear previous interval if any

            // Use debugFetch if available
            const fetchFn = typeof debugFetch === 'function' ? debugFetch : fetch;

            fetchFn('/api/v3/localminer-discoveryscan/search/places', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${jwt}`
                },
                body: JSON.stringify({
                    business_type: businessType,
                    location: location,
                    radius_km: parseInt(radius),
                    max_results: parseInt(maxResults),
                    tenant_id: tenant
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.detail || 'Error starting search');
                    });
                }
                return response.json();
            })
            .then(data => {
                currentJobId = data.job_id;
                if (statusContent) {
                    statusContent.innerHTML = `
                        <p><strong>Search started!</strong></p>
                        <p>Job ID: ${currentJobId}</p>
                        <p>Business Type: ${businessType}</p>
                        <p>Location: ${location}</p>
                        <p>Status: <span class="badge badge-pending">Pending</span></p>
                    `;
                }
                // Start checking status
                statusCheckInterval = setInterval(checkStatus, 3000); // Check every 3 seconds
            })
            .catch(error => {
                console.error('Error starting search:', error);
                if (statusContent) showStatus(`Error starting search: ${error.message}`, 'error');
                searchBtn.disabled = false;
            });
        });
    } else {
        console.error("Search button not found.");
    }

    // Event Listener for Refresh History Button
    if (refreshHistoryBtn) {
        refreshHistoryBtn.addEventListener('click', fetchSearchHistory);
    } else {
        console.error("Refresh History button not found.");
    }

    // Initial actions for Single Search tab (if it's the default active tab)
    // This logic is partially handled in common.js now, but we ensure fetchSearchHistory is called if this is the active tab on load.
    const initialActiveTab = document.querySelector('.tab.tab-active');
    if (initialActiveTab && initialActiveTab.dataset.panel === 'singleSearch') {
         console.log("Single Search Tab JS: Initial fetch history check.");
        fetchSearchHistory(); // Call directly on load if this tab is active
    }

});
