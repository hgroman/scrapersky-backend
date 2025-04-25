// JavaScript logic for the Results Viewer tab in scraper-sky-mvp.html
document.addEventListener('DOMContentLoaded', function() {
    console.log("Results Viewer Tab JS Loaded");

    // Ensure common functions are available
    if (typeof getJwtToken !== 'function' || typeof showStatus !== 'function' || typeof debugFetch !== 'function') {
        console.error("Common utility functions (getJwtToken, showStatus, debugFetch) not found. Ensure google-maps-common.js is loaded before this script.");
        // Optionally display an error to the user or disable functionality
        // return;
    }

    // Results Viewer Variables & Elements
    const resultsTableBody = document.querySelector('#resultsTable tbody'); // More specific selector
    const refreshResultsBtn = document.getElementById('refreshResultsBtn');
    const applyFiltersBtn = document.getElementById('applyFiltersBtn');
    const prevPageBtn = document.getElementById('prevPageBtn');
    const nextPageBtn = document.getElementById('nextPageBtn');
    const pageInfo = document.getElementById('pageInfo');
    const resultsStats = document.getElementById('resultsStats');
    // Filter inputs
    const filterStatusSelect = document.getElementById('filterStatus');
    const filterBusinessTypeInput = document.getElementById('filterBusinessType');
    const filterLocationInput = document.getElementById('filterLocation');
    const sortBySelect = document.getElementById('sortBy');
    const sortDirSelect = document.getElementById('sortDir');
    const resultsLimitInput = document.getElementById('resultsLimit');
    // Status element for this tab (assuming one exists or is needed)
    // const resultsViewerStatusDiv = document.getElementById('resultsViewerStatus'); // Need to add this ID to HTML if displaying status here

    let currentResultsPage = 1;
    let totalResultsPages = 0;
    let totalResultsItems = 0;
    let resultsPageSize = 100; // Default, read from input
    let selectedResultPlaceIds = new Set(); // Use a unique name for this tab's selection
    let currentFilterJobId = null; // Store the job ID being viewed

    // Shared variable access (assuming common script sets it on window)
    // Example: window.lastCompletedSingleSearchJobId

    // Function to fetch results
    async function fetchResults(specificJobId = null) {
        // Determine which job ID to use
        const jobIdToUse = specificJobId || currentFilterJobId || window.lastCompletedSingleSearchJobId || null;

        if (!jobIdToUse) {
            if (resultsTableBody) resultsTableBody.innerHTML = '<tr><td colspan="6" class="placeholder">No search job ID specified. Run a search first or select one from history.</td></tr>';
            updateResultsPagination(true);
            updateResultsStatistics(null); // Clear stats
            // Use common showStatus if available
            if (typeof showStatus === 'function') showStatus('No search job selected.', 'info', 'status'); // Use main status area
            return;
        }

        currentFilterJobId = jobIdToUse; // Remember the job ID being viewed

        const token = getJwtToken();
        if (!token) {
            if (typeof showStatus === 'function') showStatus('JWT Token is required.', 'warning', 'status');
            return;
        }

        // Read filters and pagination settings from inputs
        const status = filterStatusSelect ? filterStatusSelect.value : '';
        const businessType = filterBusinessTypeInput ? filterBusinessTypeInput.value : '';
        const location = filterLocationInput ? filterLocationInput.value : '';
        const sortBy = sortBySelect ? sortBySelect.value : 'search_time';
        const sortDir = sortDirSelect ? sortDirSelect.value : 'desc';
        resultsPageSize = resultsLimitInput ? parseInt(resultsLimitInput.value) : 100;
        const offset = (currentResultsPage - 1) * resultsPageSize;

        // Reset UI
        if (resultsTableBody) resultsTableBody.innerHTML = '<tr><td colspan="6" class="text-center">Fetching results... <i class="fas fa-spinner fa-spin"></i></td></tr>';
        if (prevPageBtn) prevPageBtn.disabled = true;
        if (nextPageBtn) nextPageBtn.disabled = true;
        clearResultsSelection(); // Clear selection when loading new results

        // Construct API URL
        // Uses OLD localminer-discoveryscan endpoint structure
        let url = `/api/v3/localminer-discoveryscan/results/${jobIdToUse}?limit=${resultsPageSize}&offset=${offset}`;
        if (status) url += `&filter_status=${status}`;
        if (businessType) url += `&filter_business_type=${encodeURIComponent(businessType)}`;
        if (location) url += `&filter_location=${encodeURIComponent(location)}`;
        if (sortBy) url += `&sort_by=${sortBy}`;
        if (sortDir) url += `&sort_dir=${sortDir}`;

        console.log(`Fetching results from: ${url}`);

        try {
            if (typeof showStatus === 'function') showStatus(`Fetching results for job ${jobIdToUse}...`, 'info', 'status');
            const response = await debugFetch(url, { // Use debugFetch if available
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error fetching results' }));
                throw new Error(`HTTP error! Status: ${response.status} - ${errorData.detail || response.statusText}`);
            }

            const data = await response.json();
            console.log('Results data:', data);

            // Clear current results
            if (resultsTableBody) resultsTableBody.innerHTML = '';
            totalResultsItems = data.total || 0;
            totalResultsPages = Math.ceil(totalResultsItems / resultsPageSize);

            // Update pagination and statistics
            updateResultsPagination();
            updateResultsStatistics(data);

            if (!data.places || data.places.length === 0) {
                if (resultsTableBody) resultsTableBody.innerHTML = '<tr><td colspan="6" class="placeholder">No results found for this job and filter.</td></tr>';
                if (typeof showStatus === 'function') showStatus('No results found.', 'info', 'status');
                return;
            }

            renderResultsTable(data.places);
            if (typeof showStatus === 'function') showStatus(`Loaded ${data.places.length} of ${totalResultsItems} results.`, 'success', 'status');
            addResultsBatchUpdateControls(); // Ensure controls are present

        } catch (error) {
            console.error('Error fetching results:', error);
            if (resultsTableBody) resultsTableBody.innerHTML = `<tr><td colspan="6" class="placeholder text-danger">Error fetching results: ${error.message}</td></tr>`;
            if (typeof showStatus === 'function') showStatus(`Error fetching results: ${error.message}`, 'error', 'status');
            updateResultsPagination(true); // Reset pagination on error
        }
    }

    // Function to render the results table
    function renderResultsTable(places) {
         if (!resultsTableBody) return;
         resultsTableBody.innerHTML = ''; // Clear just in case

         places.forEach(place => {
            const row = resultsTableBody.insertRow();
            row.dataset.placeId = place.place_id;

            if (selectedResultPlaceIds.has(place.place_id)) {
                row.classList.add('selected-row');
            }

            // Click handler for selection
            row.addEventListener('click', function(e) {
                // Avoid selection change if clicking on interactive elements
                if (e.target.tagName !== 'BUTTON' && e.target.tagName !== 'SELECT' && e.target.tagName !== 'OPTION' && !e.target.closest('button') && !e.target.closest('select')) {
                    toggleResultSelection(place.place_id);
                }
            });

            // Data cells
            row.insertCell().textContent = place.name || 'N/A';
            row.insertCell().textContent = place.formatted_address || place.vicinity || 'N/A';
            row.insertCell().textContent = place.rating ? `${place.rating} ★` : 'N/A';
            row.insertCell().textContent = place.business_type || 'N/A';

            // Status dropdown (using legacy approach)
            const statusCell = row.insertCell();
            const statusSelect = document.createElement('select');
            statusSelect.className = 'form-select form-select-sm'; // Add Bootstrap classes
            const statusOptions = ['New', 'Selected', 'Maybe', 'Not a Fit', 'Archived'];
            statusOptions.forEach(optionValue => {
                const optionEl = document.createElement('option');
                optionEl.value = optionValue;
                optionEl.textContent = optionValue;
                // Check against API status format (usually snake_case)
                 if (place.status && place.status.toLowerCase() === optionValue.toLowerCase().replace(/\s+/g, '_')) {
                     optionEl.selected = true;
                 }
                statusSelect.appendChild(optionEl);
            });
            statusSelect.addEventListener('change', function() {
                updateLegacyPlaceStatus(place.place_id, this.value);
            });
            statusCell.appendChild(statusSelect);

            // Actions cell
            const actionsCell = row.insertCell();
            // Notes button (Placeholder)
            const notesBtn = document.createElement('button');
            notesBtn.textContent = 'Notes';
            notesBtn.className = 'btn btn-sm btn-outline-secondary me-1 disabled'; // Disabled for now
            notesBtn.title = 'Notes editing not implemented yet';
            // notesBtn.addEventListener('click', function() {
            //     const notes = prompt('Enter notes for this place:', place.notes || '');
            //     if (notes !== null) {
            //         updatePlaceNotes(place.place_id, notes);
            //     }
            // });
            actionsCell.appendChild(notesBtn);

            // Details tooltip
            const detailsSpan = document.createElement('span');
            detailsSpan.className = 'tooltip';
            detailsSpan.innerHTML = '<i class="fas fa-info-circle text-secondary"></i>'; // Use an icon
            const tooltipText = document.createElement('span');
            tooltipText.className = 'tooltiptext';
            tooltipText.innerHTML = `
                <strong>Place ID:</strong> ${place.place_id}<br>
                <strong>Searched:</strong> ${new Date(place.search_time).toLocaleString()}<br>
                <strong>Added:</strong> ${place.created_at ? new Date(place.created_at).toLocaleString() : 'N/A'}<br>
                <strong>Type:</strong> ${place.business_type || 'N/A'}<br>
                <strong>Phone:</strong> ${place.formatted_phone_number || 'N/A'}<br>
                <strong>Website:</strong> ${place.website ? `<a href="${place.website}" target="_blank">${place.website}</a>` : 'N/A'}<br>
                <strong>Rating:</strong> ${place.rating || 'N/A'} (${place.user_ratings_total || 0} reviews)<br>
                <strong>Notes:</strong> ${place.notes || 'N/A'}
            `;
            detailsSpan.appendChild(tooltipText);
            actionsCell.appendChild(detailsSpan);
         });
    }

    // Function to update results statistics display
    function updateResultsStatistics(data) {
        if (!resultsStats) return;
        resultsStats.innerHTML = '';
        if (!data || data.total === undefined) {
            resultsStats.style.display = 'none';
            return;
        }
        resultsStats.style.display = 'flex';
        const statItems = [
            { label: 'Total Found', value: data.total },
            { label: 'Displaying', value: `${data.offset + 1} - ${Math.min(data.offset + data.limit, data.total)}` },
            // Add status counts if available in the API response
            // { label: 'New', value: data.stats?.new || 0 },
            // { label: 'Selected', value: data.stats?.selected || 0 },
        ];
        if (data.filters) {
            if (data.filters.status) statItems.push({ label: 'Status Filter', value: data.filters.status });
            if (data.filters.business_type) statItems.push({ label: 'Type Filter', value: data.filters.business_type });
            if (data.filters.location) statItems.push({ label: 'Location Filter', value: data.filters.location });
        }
        statItems.forEach(item => {
            const statItem = document.createElement('div');
            statItem.className = 'stat-item';
            statItem.innerHTML = `<div class="stat-value">${item.value}</div><div class="stat-label">${item.label}</div>`;
            resultsStats.appendChild(statItem);
        });
    }

    // Function to update results pagination controls
    function updateResultsPagination(isEmpty = false) {
        if (!pageInfo || !prevPageBtn || !nextPageBtn) return;
        if (isEmpty || totalResultsItems === 0) {
            pageInfo.textContent = 'Page 0 of 0';
            prevPageBtn.disabled = true;
            nextPageBtn.disabled = true;
        } else {
            resultsPageSize = resultsLimitInput ? parseInt(resultsLimitInput.value) : 100; // Ensure page size is current
            totalResultsPages = Math.ceil(totalResultsItems / resultsPageSize);
            pageInfo.textContent = `Page ${currentResultsPage} of ${totalResultsPages}`;
            prevPageBtn.disabled = currentResultsPage <= 1;
            nextPageBtn.disabled = currentResultsPage >= totalResultsPages;
        }
    }

    // Function to add batch update controls (legacy)
    function addResultsBatchUpdateControls() {
        const resultsViewPanel = document.getElementById('resultsView');
        const filterSection = resultsViewPanel ? resultsViewPanel.querySelector('.filter-section') : null;
        if (filterSection && !document.getElementById('resultsBatchUpdateControls')) {
            const batchUpdateContainer = document.createElement('div');
            batchUpdateContainer.id = 'resultsBatchUpdateControls'; // Unique ID
            batchUpdateContainer.className = 'mt-4 p-3 border rounded border-secondary';
            batchUpdateContainer.style.backgroundColor = 'rgba(0,0,0,0.2)';
            batchUpdateContainer.style.display = 'none'; // Initially hidden
            batchUpdateContainer.innerHTML = `
                <h5>Batch Update Selected Places (Legacy)</h5>
                <div class="row align-items-end">
                    <div class="col-md-4">
                        <label for="resultsBatchStatusUpdate">Set Status:</label>
                        <select id="resultsBatchStatusUpdate" class="form-select form-select-sm">
                            <option value="New">New</option>
                            <option value="Selected">Selected</option>
                            <option value="Maybe">Maybe</option>
                            <option value="Not a Fit">Not a Fit</option>
                            <option value="Archived">Archived</option>
                        </select>
                    </div>
                    <div class="col-md-5">
                         <button id="applyResultsBatchUpdate" class="btn btn-primary btn-sm">Update 0 Selected</button>
                         <button id="clearResultsSelection" class="btn btn-secondary btn-sm ms-2">Clear Selection</button>
                    </div>
                </div>
            `;
            filterSection.appendChild(batchUpdateContainer);

            // Add listeners for the new controls
            document.getElementById('applyResultsBatchUpdate').addEventListener('click', function() {
                const status = document.getElementById('resultsBatchStatusUpdate').value;
                if (selectedResultPlaceIds.size > 0) {
                    batchUpdateLegacyStatus(Array.from(selectedResultPlaceIds), status);
                } else {
                    alert('Please select at least one place to update');
                }
            });
            document.getElementById('clearResultsSelection').addEventListener('click', clearResultsSelection);
        }
    }

    // Function to update the results batch control state
    function updateResultsSelectionCounter() {
        const counterDiv = document.getElementById('resultsBatchUpdateControls'); // Container div
        const applyBtn = document.getElementById('applyResultsBatchUpdate');
        const clearBtn = document.getElementById('clearResultsSelection');

        if (!counterDiv || !applyBtn || !clearBtn) return;

        const count = selectedResultPlaceIds.size;
        applyBtn.textContent = `Update ${count} Selected`;

        if (count > 0) {
            counterDiv.style.display = 'block';
            applyBtn.disabled = false;
            clearBtn.disabled = false;
        } else {
            counterDiv.style.display = 'none';
            applyBtn.disabled = true;
            clearBtn.disabled = true;
        }
    }

    // Function to toggle selection for a result row
    function toggleResultSelection(placeId) {
        if (selectedResultPlaceIds.has(placeId)) {
            selectedResultPlaceIds.delete(placeId);
        } else {
            selectedResultPlaceIds.add(placeId);
        }
        // Update visual state of the row
        const row = resultsTableBody ? resultsTableBody.querySelector(`tr[data-place-id="${placeId}"]`) : null;
        if (row) {
             row.classList.toggle('selected-row', selectedResultPlaceIds.has(placeId));
        }
        updateResultsSelectionCounter();
    }

    // Function to clear results selection
    function clearResultsSelection() {
        selectedResultPlaceIds.clear();
        if (resultsTableBody) {
            resultsTableBody.querySelectorAll('tr.selected-row').forEach(row => {
                row.classList.remove('selected-row');
            });
        }
        updateResultsSelectionCounter();
    }

    // Function to update place status using LEGACY endpoint
    async function updateLegacyPlaceStatus(placeId, status) {
        const tenant = document.getElementById('tenant')?.value || 'default-tenant'; // Get tenant ID, provide default if missing
        const jwt = getJwtToken();
        if (!jwt) {
             if (typeof showStatus === 'function') showStatus('JWT Token needed', 'warning', 'status');
             return;
        }

        console.warn(`Using LEGACY endpoint for status update: POST /api/v3/localminer-discoveryscan/places/staging/status`);

        try {
            const response = await debugFetch('/api/v3/localminer-discoveryscan/places/staging/status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${jwt}`
                },
                body: JSON.stringify({
                    place_ids: [placeId],
                    status: status, // Use the user-friendly status from dropdown
                    tenant_id: tenant
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Error updating status' }));
                throw new Error(errorData.detail);
            }

            const data = await response.json();
            console.log('Legacy status updated:', data);
            if (typeof showStatus === 'function') showStatus(`Status updated to ${status}`, 'success', 'status');
            // No automatic refresh, let user decide with refresh button
        } catch (error) {
            console.error('Error updating legacy status:', error);
            if (typeof showStatus === 'function') showStatus(`Error updating status: ${error.message}`, 'error', 'status');
            // Revert dropdown on error? Maybe not, as the backend state is unknown.
        }
    }

    // Function to batch update status using LEGACY endpoint
    async function batchUpdateLegacyStatus(placeIds, status) {
        const tenant = document.getElementById('tenant')?.value || 'default-tenant';
        const jwt = getJwtToken();
        if (!jwt) {
             if (typeof showStatus === 'function') showStatus('JWT Token needed', 'warning', 'status');
             return;
        }

        console.warn(`Using LEGACY endpoint for batch update: POST /api/v3/localminer-discoveryscan/places/staging/batch`);
        const applyBtn = document.getElementById('applyResultsBatchUpdate');
        if (applyBtn) applyBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
        if (applyBtn) applyBtn.disabled = true;


        try {
            const response = await debugFetch('/api/v3/localminer-discoveryscan/places/staging/batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${jwt}`
                },
                body: JSON.stringify({
                    place_ids: placeIds,
                    status: status, // Use user-friendly status
                    tenant_id: tenant
                })
            });

            if (!response.ok) {
                 const errorData = await response.json().catch(() => ({ detail: 'Error updating statuses' }));
                throw new Error(errorData.detail);
            }
            const data = await response.json();
            console.log('Legacy batch update successful:', data);
            const updatedCount = data.updated || data.updated_count || placeIds.length;
            if (typeof showStatus === 'function') showStatus(`Updated ${updatedCount} places to ${status}`, 'success', 'status');
            fetchResults(currentFilterJobId); // Refresh results to show changes
            clearResultsSelection(); // Clear selection after successful update

        } catch (error) {
            console.error('Error in legacy batch update:', error);
            if (typeof showStatus === 'function') showStatus(`Error updating places: ${error.message}`, 'error', 'status');
        } finally {
             // Restore button text and enable it
             if (applyBtn) updateResultsSelectionCounter(); // This will reset the button text/state
        }
    }

    // Function to update place notes (Placeholder - No API endpoint)
    // async function updatePlaceNotes(placeId, notes) {
    //     console.log(`Updating notes for ${placeId} to: ${notes}`);
    //     if (typeof showStatus === 'function') showStatus('Notes update functionality not yet implemented in backend', 'info', 'status');
        // Add API call here when available
    // }

    // Event Listeners for Results Viewer
    if (refreshResultsBtn) refreshResultsBtn.addEventListener('click', () => fetchResults());
    if (applyFiltersBtn) applyFiltersBtn.addEventListener('click', () => {
        currentResultsPage = 1; // Reset page on filter change
        fetchResults();
    });
    if (prevPageBtn) prevPageBtn.addEventListener('click', () => {
        if (currentResultsPage > 1) {
            currentResultsPage--;
            fetchResults(currentFilterJobId);
        }
    });
    if (nextPageBtn) nextPageBtn.addEventListener('click', () => {
        if (currentResultsPage < totalResultsPages) {
            currentResultsPage++;
            fetchResults(currentFilterJobId);
        }
    });

    // Add listener for the results viewer tab itself to load data when activated
    const resultsViewerTab = document.querySelector('.tab[data-panel="resultsView"]');
    if (resultsViewerTab) {
        resultsViewerTab.addEventListener('click', function() {
             // Only fetch if the panel is actually becoming active
             // The main tab switching logic should handle the active classes
             // Check if the panel is active or about to be activated
             const panel = document.getElementById('resultsView');
             // Fetch only if panel is not already active or if no data loaded yet
             if (panel && !panel.classList.contains('panel-active') || (resultsTableBody && resultsTableBody.innerHTML.includes('placeholder'))) {
                  console.log("Results Viewer tab clicked, fetching data...");
                  fetchResults(); // Fetch with current filters/jobId
             }
        });

        // Handle initial load if this tab is active by default
        if (resultsViewerTab.classList.contains('tab-active')) {
             const panel = document.getElementById('resultsView');
             if (panel && panel.classList.contains('panel-active')) {
                 console.log("Results Viewer tab active on initial load, fetching data...");
                 fetchResults();
             }
        }
    }

    // Make fetchResults globally accessible for other tabs to call if needed
    window.fetchResultsViewerData = fetchResults;

});
