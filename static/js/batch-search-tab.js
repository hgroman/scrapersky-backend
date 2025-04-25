// JavaScript logic for the Batch Search tab in scraper-sky-mvp.html
document.addEventListener('DOMContentLoaded', function() {
    console.log("Batch Search Tab JS Loaded");

    // Ensure common functions are available
    if (typeof getJwtToken !== 'function' || typeof showStatus !== 'function') {
        console.error("Common utility functions not found. Ensure google-maps-common.js is loaded before this script.");
        // return;
    }

    // Batch Search Variables & Elements
    const batchSearchBtn = document.getElementById('batchSearchBtn');
    const batchStatusDiv = document.getElementById('batchStatus'); // Ensure this ID exists in HTML if used
    const batchStatusContent = document.getElementById('batchStatusContent'); // Ensure this ID exists
    const batchProgressFill = document.getElementById('batchProgressFill'); // Ensure this ID exists
    const batchLocationsStatus = document.getElementById('batchLocationsStatus'); // Ensure this ID exists
    const batchLocationsList = document.getElementById('batchLocationsList'); // Ensure this ID exists

    let currentBatchId = null;
    let batchStatusCheckInterval = null;

    // Function to check batch search status
    function checkBatchStatus() {
        if (!currentBatchId) return;

        const jwt = getJwtToken();
        if (!jwt) {
             console.warn("JWT Token not found for batch status check.");
             // Optionally show status message
             clearInterval(batchStatusCheckInterval);
             return;
        }

        const fetchFn = typeof debugFetch === 'function' ? debugFetch : fetch;

        fetchFn(`/api/v3/places/batch-status/${currentBatchId}`, {
            headers: {
                'Authorization': `Bearer ${jwt}`
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    if (response.status === 404) {
                         clearInterval(batchStatusCheckInterval);
                         throw new Error(err.detail || 'Batch job not found. Stopping status checks.');
                    }
                    throw new Error(err.detail || 'Error checking batch status');
                });
            }
            return response.json();
        })
        .then(data => {
            let progress = data.progress || 0;
            let totalItems = data.total_items || 1; // Avoid division by zero
            let completedItems = data.completed_items || 0;

            // Update progress bar
            if (batchProgressFill) batchProgressFill.style.width = `${(completedItems / totalItems) * 100}%`;

            // Update batch status display
            if (batchStatusContent) {
                let statusHtml = `
                    <p><strong>Status:</strong> <span class="badge badge-${data.status?.toLowerCase()}">${data.status || 'Unknown'}</span></p>
                    <p><strong>Batch ID:</strong> ${data.batch_id}</p>
                    <p><strong>Progress:</strong> ${completedItems} of ${totalItems} locations processed</p>
                `;

                // Add statistics if available
                if (data.statistics) {
                    statusHtml += `
                        <p><strong>Successful Locations:</strong> ${data.statistics.successful_locations || 0}</p>
                        <p><strong>Failed Locations:</strong> ${data.statistics.failed_locations || 0}</p>
                        <p><strong>Total Places Found:</strong> ${data.statistics.total_places_found || 0}</p>
                        <p><strong>Total Places Stored:</strong> ${data.statistics.total_places_stored || 0}</p>
                    `;
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
                batchStatusContent.innerHTML = statusHtml;
            }

            // Update individual location status list
            if (batchLocationsList && data.results) {
                data.results.forEach(result => {
                    const locationStatusSpan = batchLocationsList.querySelector(`.batch-location-status[data-location="${result.location}"]`);
                    if (locationStatusSpan) {
                        let statusText = '';
                        let statusClass = 'pending';
                        if (result.status === 'success') {
                            statusClass = 'success';
                            statusText = `Success: ${result.total_places || 0} found, ${result.stored_places || 0} stored`;
                        } else if (result.status === 'error') {
                            statusClass = 'error';
                            statusText = `Error: ${result.error || 'Unknown error'}`;
                        } else {
                            statusText = result.status;
                        }
                        locationStatusSpan.className = `batch-location-status location-${statusClass}`;
                        locationStatusSpan.textContent = statusText;
                    }
                });
            }

            // Stop polling if job is complete or failed
            if (data.status === 'completed' || data.status === 'failed') {
                clearInterval(batchStatusCheckInterval);
                if (batchSearchBtn) batchSearchBtn.disabled = false;

                // Optionally switch to results view on completion?
                if (data.status === 'completed') {
                    // This behaviour might be unwanted, consider removing or making optional
                    // const resultsTab = document.querySelector('.tab[data-panel="resultsView"]');
                    // if (resultsTab) resultsTab.click();
                    // if (typeof fetchResults === 'function') fetchResults(); // Fetch general results?
                }
            }
        })
        .catch(error => {
            console.error('Error checking batch status:', error);
            if (batchStatusContent) showStatus(`Error checking batch status: ${error.message}`, 'error', 'batchStatusContent');
            clearInterval(batchStatusCheckInterval);
            if (batchSearchBtn) batchSearchBtn.disabled = false;
        });
    }

    // Event Listener for Batch Search Button
    if (batchSearchBtn) {
        batchSearchBtn.addEventListener('click', function() {
            const locationsText = document.getElementById('batchLocations').value;
            const locations = locationsText.split('\n')
                .map(loc => loc.trim())
                .filter(loc => loc.length > 0);

            const businessType = document.getElementById('batchBusinessType').value;
            const radius = document.getElementById('batchRadius').value;
            const maxConcurrent = document.getElementById('batchConcurrent').value;
            const tenant = document.getElementById('batchTenant').value;
            const jwt = getJwtToken();

            if (locations.length === 0) {
                showStatus('Please enter at least one location', 'warning', 'batchStatusContent'); // Use correct status element ID
                return;
            }
            if (!businessType) {
                showStatus('Please enter a business type', 'warning', 'batchStatusContent');
                return;
            }
            if (!jwt) {
                showStatus('Please enter a JWT token', 'warning', 'batchStatusContent');
                return;
            }

            batchSearchBtn.disabled = true;
            if (batchStatusDiv) batchStatusDiv.style.display = 'block';
            if (batchStatusContent) batchStatusContent.innerHTML = '<p>Starting batch search...</p>';
            if (batchProgressFill) batchProgressFill.style.width = '0%';
            if (batchLocationsStatus) batchLocationsStatus.style.display = 'none';
            if (batchLocationsList) batchLocationsList.innerHTML = ''; // Clear previous location statuses
            if (batchStatusCheckInterval) clearInterval(batchStatusCheckInterval); // Clear previous interval

            const fetchFn = typeof debugFetch === 'function' ? debugFetch : fetch;

            // NOTE: Endpoint /api/v3/places/batch-search needs verification
            fetchFn('/api/v3/places/batch-search', { // Assuming this endpoint exists
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${jwt}`
                },
                body: JSON.stringify({
                    locations: locations,
                    business_type: businessType,
                    radius_km: parseInt(radius),
                    max_concurrent: parseInt(maxConcurrent),
                    tenant_id: tenant
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.detail || 'Error starting batch search');
                    });
                }
                return response.json();
            })
            .then(data => {
                currentBatchId = data.batch_id;
                if (batchStatusContent) {
                    batchStatusContent.innerHTML = `
                        <p><strong>Batch search started!</strong></p>
                        <p>Batch ID: ${data.batch_id}</p>
                        <p>Business Type: ${businessType}</p>
                        <p>Total Locations: ${data.total_locations || locations.length}</p>
                        <p>Status: <span class="badge badge-pending">Initializing...</span></p>
                    `;
                }

                // Create location status placeholders
                if (batchLocationsStatus && batchLocationsList) {
                    batchLocationsStatus.style.display = 'block';
                    locations.forEach((location, index) => {
                        const locationItem = document.createElement('div');
                        locationItem.className = 'batch-location-item';
                        locationItem.innerHTML = `
                            <span>${index + 1}. ${location}</span>
                            <span class="batch-location-status location-pending" data-location="${location}">Pending</span>
                        `;
                        batchLocationsList.appendChild(locationItem);
                    });
                }

                // Start checking status
                batchStatusCheckInterval = setInterval(checkBatchStatus, 3000); // Check every 3 seconds
            })
            .catch(error => {
                console.error('Error starting batch search:', error);
                showStatus(`Error starting batch search: ${error.message}`, 'error', 'batchStatusContent');
                batchSearchBtn.disabled = false;
            });
        });
    } else {
        console.error("Batch Search button not found.");
    }

});
