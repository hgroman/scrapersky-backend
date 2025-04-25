// JavaScript logic for the Staging Editor tab in scraper-sky-mvp.html
document.addEventListener('DOMContentLoaded', function() {
    console.log("Staging Editor Tab JS Loaded");

    // Ensure common functions are available
    if (typeof getJwtToken !== 'function' || typeof showStatus !== 'function') {
        console.error("Common utility functions not found. Ensure google-maps-common.js is loaded before this script.");
        // return;
    }

    // Staging Editor Variables & Elements
    const stagingTableBody = document.getElementById('stagingTableBody');
    const stagingPaginationInfo = document.getElementById('stagingPaginationInfo');
    const stagingPrevBtn = document.getElementById('stagingPrevBtn');
    const stagingNextBtn = document.getElementById('stagingNextBtn');
    const selectAllStagingCheckbox = document.getElementById('selectAllStagingCheckbox');
    const stagingBatchUpdateControls = document.getElementById('stagingBatchUpdateControls');
    const stagingBatchStatusUpdate = document.getElementById('stagingBatchStatusUpdate');
    const applyStagingBatchUpdateBtn = document.getElementById('applyStagingBatchUpdate');
    const clearStagingSelectionBtn = document.getElementById('clearStagingSelection');
    const stagingStatusDiv = document.getElementById('stagingStatus'); // Assuming this element exists for status messages

    console.log("Staging Editor DOM elements:", {
        stagingTableBody: !!stagingTableBody,
        stagingPaginationInfo: !!stagingPaginationInfo,
        stagingPrevBtn: !!stagingPrevBtn,
        stagingNextBtn: !!stagingNextBtn,
        selectAllStagingCheckbox: !!selectAllStagingCheckbox,
        stagingBatchUpdateControls: !!stagingBatchUpdateControls,
        stagingBatchStatusUpdate: !!stagingBatchStatusUpdate,
        applyStagingBatchUpdateBtn: !!applyStagingBatchUpdateBtn,
        clearStagingSelectionBtn: !!clearStagingSelectionBtn,
        stagingStatusDiv: !!stagingStatusDiv
    });

    let currentStagingPage = 1;
    const stagingPageSize = 15; // Default page size
    let totalStagingPages = 0;
    let totalStagingItems = 0;
    let selectedStagingPlaceIds = new Set();

    // Add direct tab activation listener
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function() {
            if (this.dataset.panel === 'stagingEditor') {
                console.log('Staging Editor tab activated directly by click');
                setTimeout(() => fetchStagingData(1), 100); // Small delay to ensure DOM is ready
            }
        });
    });

    // Make fetchStagingData global so it can be called from common.js
    window.fetchStagingData = fetchStagingData;

    // Function to fetch staging data
    async function fetchStagingData(page = 1) {
        console.log(`Starting fetchStagingData(${page})...`);

        const token = getJwtToken();
        if (!token) {
            console.error("JWT Token is missing");
            showStatus('JWT Token is required.', 'warning', 'stagingStatus');
            return;
        }

        // Reset UI elements before fetch
        if (stagingTableBody) stagingTableBody.innerHTML = '<tr><td colspan="5" class="text-center">Fetching data... <i class="fas fa-spinner fa-spin"></i></td></tr>';
        if (stagingPrevBtn) stagingPrevBtn.disabled = true;
        if (stagingNextBtn) stagingNextBtn.disabled = true;
        if (selectAllStagingCheckbox) selectAllStagingCheckbox.checked = false;
        clearStagingSelection(); // Clear selection on new data load

        // Define filters (currently static, could be dynamic)
        // const statusFilter = 'New'; // Example filter
        // const apiUrl = `/api/v3/places/staging/?page=${page}&size=${stagingPageSize}&status=${statusFilter}`;
        const apiUrl = `/api/v3/places/staging?page=${page}&size=${stagingPageSize}`; // Fetch all statuses for now
        console.log(`API URL: ${apiUrl}`);

        const fetchFn = typeof debugFetch === 'function' ? debugFetch : fetch;
        console.log(`Using fetch function: ${typeof debugFetch === 'function' ? 'debugFetch' : 'fetch'}`);

        try {
            console.log("Starting API request...");
            showStatus('Fetching staging data...', 'info', 'stagingStatus');
            const response = await fetchFn(apiUrl, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            console.log(`API response status: ${response.status}`);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error fetching staging data' }));
                throw new Error(`HTTP error! Status: ${response.status} - ${errorData.detail || response.statusText}`);
            }

            const data = await response.json();
            console.log(`API data received with ${data?.items?.length || 0} items`);

            if (data && data.items) {
                renderStagingTable(data.items);
                currentStagingPage = data.page;
                totalStagingPages = data.pages;
                totalStagingItems = data.total;
                updateStagingPagination();
                showStatus(`Loaded ${data.items.length} of ${data.total} staging records.`, 'success', 'stagingStatus');
            } else {
                if (stagingTableBody) stagingTableBody.innerHTML = '<tr><td colspan="5" class="text-center">No staging data found.</td></tr>';
                updateStagingPagination(true); // Reset pagination
                showStatus('No staging data found.', 'info', 'stagingStatus');
            }
        } catch (error) {
            console.error('Error fetching staging data:', error);
            if (stagingTableBody) stagingTableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Error loading data: ${error.message}</td></tr>`;
            updateStagingPagination(true); // Reset pagination on error
            showStatus(`Error fetching staging data: ${error.message}`, 'error', 'stagingStatus');
        }
    }

    // Function to render the staging table
    function renderStagingTable(items) {
        if (!stagingTableBody) return;
        stagingTableBody.innerHTML = ''; // Clear previous rows
        if (!items || items.length === 0) {
            stagingTableBody.innerHTML = '<tr><td colspan="5" class="text-center">No data available.</td></tr>';
            return;
        }

        items.forEach(item => {
            const row = stagingTableBody.insertRow();
            // Store both place_id (string) and internal staging ID (int) if available and needed
            row.dataset.placeId = item.place_id;
            // row.dataset.stagingId = item.id; // Assuming API returns internal ID as 'id'

            // Checkbox cell
            const cellCheckbox = row.insertCell();
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'form-check-input staging-select-checkbox'; // Unique class
            checkbox.value = item.place_id; // Use place_id as the value for selection
            checkbox.checked = selectedStagingPlaceIds.has(item.place_id);
            checkbox.addEventListener('change', handleStagingRowSelection);
            cellCheckbox.appendChild(checkbox);

            // Data cells - Use correct keys from API response
            row.insertCell().textContent = item.business_name || 'N/A'; // Example: use business_name
            row.insertCell().textContent = item.address || item.search_location || 'N/A'; // Example: use address or fallback

            // Main Status Badge
            const statusCell = row.insertCell();
            const statusBadge = document.createElement('span');
            const statusText = item.status || 'Unknown';
            statusBadge.className = `badge badge-${statusText.toLowerCase().replace(/[^a-z0-9]+/g, '_')}`;
            statusBadge.textContent = statusText;
            statusCell.appendChild(statusBadge);

            // Deep Scan Status Badge
            const deepScanStatusCell = row.insertCell();
            const deepScanStatusText = item.deep_scan_status || 'N/A'; // Assuming API returns this field
            const deepScanBadge = document.createElement('span');
            // Map DeepScanStatusEnum values to badge classes
            let deepScanClass = 'secondary'; // Default badge class
            if (deepScanStatusText) {
                switch (deepScanStatusText.toLowerCase()) {
                    case 'queued': deepScanClass = 'queued'; break;
                    case 'processing': deepScanClass = 'processing'; break;
                    case 'completed': deepScanClass = 'completed'; break;
                    case 'error': deepScanClass = 'error'; break;
                }
            }
            deepScanBadge.className = `badge badge-${deepScanClass}`;
            deepScanBadge.textContent = deepScanStatusText;
            deepScanStatusCell.appendChild(deepScanBadge);

            // Apply selected style if checkbox is checked
            if (checkbox.checked) {
                row.classList.add('selected-row'); // Use consistent selection class
            }
        });
    }

    // Function to update pagination controls
    function updateStagingPagination(isEmpty = false) {
        if (!stagingPaginationInfo || !stagingPrevBtn || !stagingNextBtn) return;
        if (isEmpty) {
            stagingPaginationInfo.textContent = 'Page 0 of 0 (0 items)';
            stagingPrevBtn.disabled = true;
            stagingNextBtn.disabled = true;
        } else {
            stagingPaginationInfo.textContent = `Page ${currentStagingPage} of ${totalStagingPages} (${totalStagingItems} items)`;
            stagingPrevBtn.disabled = currentStagingPage <= 1;
            stagingNextBtn.disabled = currentStagingPage >= totalStagingPages;
        }
    }

    // Function to handle row selection changes
    function handleStagingRowSelection(event) {
        const checkbox = event.target;
        const placeId = checkbox.value;
        const row = checkbox.closest('tr');

        if (checkbox.checked) {
            selectedStagingPlaceIds.add(placeId);
            if (row) row.classList.add('selected-row');
        } else {
            selectedStagingPlaceIds.delete(placeId);
            if (row) row.classList.remove('selected-row');
            // Uncheck "select all" if any item is deselected
            if (selectAllStagingCheckbox) selectAllStagingCheckbox.checked = false;
        }
        updateStagingBatchControls();
    }

    // Function to handle "select all" checkbox changes
    function toggleSelectAllStaging(event) {
        if (!stagingTableBody) return;
        const isChecked = event.target.checked;
        const visibleCheckboxes = stagingTableBody.querySelectorAll('.staging-select-checkbox');

        visibleCheckboxes.forEach(checkbox => {
            const placeId = checkbox.value;
            const row = checkbox.closest('tr');
            checkbox.checked = isChecked;
            if (isChecked) {
                selectedStagingPlaceIds.add(placeId);
                if (row) row.classList.add('selected-row');
            } else {
                selectedStagingPlaceIds.delete(placeId);
                if (row) row.classList.remove('selected-row');
            }
        });
        updateStagingBatchControls();
    }

    // Function to update the visibility and state of batch controls
    function updateStagingBatchControls() {
        if (!stagingBatchUpdateControls || !applyStagingBatchUpdateBtn || !clearStagingSelectionBtn || !stagingBatchStatusUpdate) return;
        const count = selectedStagingPlaceIds.size;
        if (count > 0) {
            stagingBatchUpdateControls.style.display = 'block';
            applyStagingBatchUpdateBtn.textContent = `Update ${count} Selected`;
            applyStagingBatchUpdateBtn.disabled = false;
            clearStagingSelectionBtn.disabled = false;
        } else {
            stagingBatchUpdateControls.style.display = 'none';
            applyStagingBatchUpdateBtn.textContent = 'Update 0 Selected';
            applyStagingBatchUpdateBtn.disabled = true;
            clearStagingSelectionBtn.disabled = true;
        }
        // Reset status dropdown when selection changes
        stagingBatchStatusUpdate.value = "";
    }

    // Function to clear the current selection
    function clearStagingSelection() {
        selectedStagingPlaceIds.clear();
        if (stagingTableBody) {
            stagingTableBody.querySelectorAll('.staging-select-checkbox').forEach(cb => {
                cb.checked = false;
                const row = cb.closest('tr');
                if (row) row.classList.remove('selected-row');
            });
        }
        if (selectAllStagingCheckbox) selectAllStagingCheckbox.checked = false;
        updateStagingBatchControls();
    }

    // Function to perform batch status update
    async function batchUpdateStagingStatus() {
        const token = getJwtToken();
        if (!token) {
            showStatus('JWT Token is required.', 'error', 'stagingStatus');
            return;
        }

        const placeIdsToUpdate = Array.from(selectedStagingPlaceIds);
        const targetStatus = stagingBatchStatusUpdate ? stagingBatchStatusUpdate.value : null;

        if (placeIdsToUpdate.length === 0) {
            showStatus('No items selected for update.', 'warning', 'stagingStatus');
            return;
        }
        if (!targetStatus) {
            showStatus('Please select a target status.', 'warning', 'stagingStatus');
            return;
        }

        // Use the correct API endpoint for batch updates
        const apiUrl = '/api/v3/places/staging/status';
        const payload = {
            place_ids: placeIdsToUpdate,
            status: targetStatus // API expects the string value from the dropdown
        };

        if (applyStagingBatchUpdateBtn) {
            applyStagingBatchUpdateBtn.disabled = true;
            applyStagingBatchUpdateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
        }

        const fetchFn = typeof debugFetch === 'function' ? debugFetch : fetch;

        try {
            console.log('Sending batch update with payload:', JSON.stringify(payload));
            showStatus('Sending batch update...', 'info', 'stagingStatus');
            const response = await fetchFn(apiUrl, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            console.log(`Batch update response status: ${response.status}`);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error during batch update' }));
                console.error('Batch update error details:', errorData);
                throw new Error(`HTTP error! Status: ${response.status} - ${errorData.detail || response.statusText}`);
            }

            const result = await response.json();
            const updatedCount = result.updated_count || 0;
            const queuedCount = result.queued_count || 0; // Capture queued count

            showStatus(`Successfully updated status for ${updatedCount} items. Queued for deep scan: ${queuedCount}.`, 'success', 'stagingStatus');
            clearStagingSelection();
            fetchStagingData(currentStagingPage); // Refresh current page after update

        } catch (error) {
            console.error('Error updating staging status:', error);
            showStatus(`Error updating status: ${error.message}`, 'error', 'stagingStatus');
        } finally {
            // Ensure controls are re-enabled and text reset
            updateStagingBatchControls();
        }
    }


    // Event Listeners for Staging Editor
    if (stagingPrevBtn) stagingPrevBtn.addEventListener('click', () => {
        if (currentStagingPage > 1) {
            fetchStagingData(currentStagingPage - 1);
        }
    });

    if (stagingNextBtn) stagingNextBtn.addEventListener('click', () => {
        if (currentStagingPage < totalStagingPages) {
            fetchStagingData(currentStagingPage + 1);
        }
    });

    if (selectAllStagingCheckbox) selectAllStagingCheckbox.addEventListener('change', toggleSelectAllStaging);

    if (applyStagingBatchUpdateBtn) applyStagingBatchUpdateBtn.addEventListener('click', batchUpdateStagingStatus);

    if (clearStagingSelectionBtn) clearStagingSelectionBtn.addEventListener('click', clearStagingSelection);

    // Initial data load if this tab is active when the page loads
    // This is now handled primarily by the tab switching logic in common.js,
    // but we can add a safety check here too.
    const initialActiveTab = document.querySelector('.tab.tab-active');
    if (initialActiveTab && initialActiveTab.dataset.panel === 'stagingEditor') {
        console.log("Staging Editor Tab JS: Initial fetch check.");
        fetchStagingData(1); // Fetch first page on load if active
    }

    // Initialize staging controls state on load
    updateStagingBatchControls();

});
