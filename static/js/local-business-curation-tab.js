// JavaScript logic for the Local Business Curation tab in scraper-sky-mvp.html
document.addEventListener('DOMContentLoaded', function() {
    console.log("Local Business Curation Tab JS Loaded");

    // Ensure common functions are available
    if (typeof getJwtToken !== 'function' || typeof showStatus !== 'function') {
        console.error("Common utility functions not found. Ensure google-maps-common.js is loaded before this script.");
        // return;
    }

    // Local Business Curation Variables & Elements
    const localBusinessTableBody = document.getElementById('localBusinessTableBody');
    const localBusinessPaginationInfo = document.getElementById('localBusinessPaginationInfo');
    const localBusinessPrevBtn = document.getElementById('localBusinessPrevBtn');
    const localBusinessNextBtn = document.getElementById('localBusinessNextBtn');
    const selectAllLocalBusinessCheckbox = document.getElementById('selectAllLocalBusinessCheckbox');
    const localBusinessBatchUpdateControls = document.getElementById('localBusinessBatchUpdateControls');
    const localBusinessBatchStatusUpdate = document.getElementById('localBusinessBatchStatusUpdate');
    const applyLocalBusinessBatchUpdateBtn = document.getElementById('applyLocalBusinessBatchUpdate');
    const clearLocalBusinessSelectionBtn = document.getElementById('clearLocalBusinessSelection');
    const localBusinessStatusFilter = document.getElementById('localBusinessStatusFilter');
    const localBusinessNameFilter = document.getElementById('localBusinessNameFilter');
    const applyLocalBusinessFiltersBtn = document.getElementById('applyLocalBusinessFilters');
    const resetLocalBusinessFiltersBtn = document.getElementById('resetLocalBusinessFilters');
    const localBusinessStatusDiv = document.getElementById('localBusinessStatus'); // For status messages

    let currentLocalBusinessPage = 1;
    const localBusinessPageSize = 15;
    let totalLocalBusinessPages = 0;
    let totalLocalBusinessItems = 0;
    let selectedLocalBusinessIds = new Set();

    // Add direct tab activation listener
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function() {
            if (this.dataset.panel === 'localBusinessCuration') {
                console.log('Local Business Curation tab activated directly by click');
                setTimeout(() => fetchLocalBusinessData(1), 100); // Small delay to ensure DOM is ready
            }
        });
    });

    // Make fetchLocalBusinessData global so it can be called from common.js
    window.fetchLocalBusinessData = fetchLocalBusinessData;

    // Function to fetch local business data
    async function fetchLocalBusinessData(page = 1) {
        const token = getJwtToken();
        if (!token) {
            showStatus('JWT Token is required.', 'error', 'localBusinessStatus');
            return;
        }

        // Reset UI elements
        if (localBusinessTableBody) localBusinessTableBody.innerHTML = '<tr><td colspan="6" class="text-center">Fetching data... <i class="fas fa-spinner fa-spin"></i></td></tr>';
        if (localBusinessPrevBtn) localBusinessPrevBtn.disabled = true;
        if (localBusinessNextBtn) localBusinessNextBtn.disabled = true;
        if (selectAllLocalBusinessCheckbox) selectAllLocalBusinessCheckbox.checked = false;
        clearLocalBusinessSelection();

        // Build query parameters
        let queryParams = new URLSearchParams({
            page: page,
            size: localBusinessPageSize
        });

        // Add filters if they are set
        const statusFilter = localBusinessStatusFilter ? localBusinessStatusFilter.value : '';
        const nameFilter = localBusinessNameFilter ? localBusinessNameFilter.value : '';

        if (statusFilter) {
            queryParams.append('status', statusFilter);
        }
        if (nameFilter) {
            queryParams.append('business_name', nameFilter);
        }

        const apiUrl = `/api/v3/local-businesses?${queryParams.toString()}`;
        const fetchFn = typeof debugFetch === 'function' ? debugFetch : fetch;

        try {
            showStatus('Fetching local businesses...', 'info', 'localBusinessStatus');
            const response = await fetchFn(apiUrl, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error fetching local businesses' }));
                throw new Error(`HTTP error! Status: ${response.status} - ${errorData.detail || response.statusText}`);
            }

            const data = await response.json();

            if (data && data.items) {
                renderLocalBusinessTable(data.items);
                currentLocalBusinessPage = data.page;
                totalLocalBusinessPages = data.pages;
                totalLocalBusinessItems = data.total;
                updateLocalBusinessPagination();
                showStatus(`Loaded ${data.items.length} of ${data.total} local businesses.`, 'success', 'localBusinessStatus');
            } else {
                if (localBusinessTableBody) localBusinessTableBody.innerHTML = '<tr><td colspan="6" class="text-center">No local businesses found for the current filter.</td></tr>';
                updateLocalBusinessPagination(true);
                showStatus('No local businesses found.', 'info', 'localBusinessStatus');
            }
        } catch (error) {
            console.error('Error fetching local businesses:', error);
            if (localBusinessTableBody) localBusinessTableBody.innerHTML = `<tr><td colspan="6" class="text-center text-danger">Error loading data: ${error.message}</td></tr>`;
            updateLocalBusinessPagination(true);
            showStatus(`Error fetching local businesses: ${error.message}`, 'error', 'localBusinessStatus');
        }
    }

    // Function to render the local business table
    function renderLocalBusinessTable(items) {
        if (!localBusinessTableBody) return;
        localBusinessTableBody.innerHTML = '';
        if (!items || items.length === 0) {
            localBusinessTableBody.innerHTML = '<tr><td colspan="6" class="text-center">No data available.</td></tr>';
            return;
        }

        items.forEach(item => {
            const row = localBusinessTableBody.insertRow();
            row.dataset.businessId = item.id;

            // Checkbox cell
            const cellCheckbox = row.insertCell();
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'form-check-input local-business-select-checkbox'; // Unique class
            checkbox.value = item.id;
            checkbox.checked = selectedLocalBusinessIds.has(item.id);
            checkbox.addEventListener('change', handleLocalBusinessRowSelection);
            cellCheckbox.appendChild(checkbox);

            // Data cells
            row.insertCell().textContent = item.business_name || 'N/A';
            row.insertCell().textContent = item.full_address || 'N/A';

            // Website URL with link
            const websiteCell = row.insertCell();
            if (item.website_url) {
                const link = document.createElement('a');
                let url = item.website_url;
                if (!url.startsWith('http://') && !url.startsWith('https://')) {
                    url = 'http://' + url;
                }
                link.href = url;
                link.textContent = item.website_url;
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
                websiteCell.appendChild(link);
            } else {
                websiteCell.textContent = 'N/A';
            }

            // Status with badge
            const statusCell = row.insertCell();
            const statusBadge = document.createElement('span');
            const statusText = item.status || 'New';
            statusBadge.className = `badge badge-${statusText.toLowerCase().replace(/[^a-z0-9]+/g, '_')}`;
            statusBadge.textContent = statusText;
            statusCell.appendChild(statusBadge);

            // Domain extraction status with badge
            const domainStatusCell = row.insertCell();
            if (item.domain_extraction_status) {
                const domainStatusBadge = document.createElement('span');
                const domainStatus = item.domain_extraction_status.toLowerCase();
                let badgeClass = 'secondary'; // Default
                switch(domainStatus) {
                    case 'completed': badgeClass = 'complete'; break;
                    case 'queued': badgeClass = 'queued'; break;
                    case 'processing': badgeClass = 'processing'; break;
                    case 'failed': badgeClass = 'failed'; break;
                }
                domainStatusBadge.className = `badge badge-${badgeClass}`;
                domainStatusBadge.textContent = item.domain_extraction_status;
                domainStatusCell.appendChild(domainStatusBadge);
            } else {
                domainStatusCell.textContent = 'N/A';
            }

            // Apply selected style if needed
            if (checkbox.checked) {
                row.classList.add('selected-row');
            }
        });
    }

    // Function to update local business pagination
    function updateLocalBusinessPagination(isEmpty = false) {
        if (!localBusinessPaginationInfo || !localBusinessPrevBtn || !localBusinessNextBtn) return;
        if (isEmpty) {
            localBusinessPaginationInfo.textContent = 'Page 0 of 0 (0 items)';
            localBusinessPrevBtn.disabled = true;
            localBusinessNextBtn.disabled = true;
        } else {
            localBusinessPaginationInfo.textContent = `Page ${currentLocalBusinessPage} of ${totalLocalBusinessPages} (${totalLocalBusinessItems} items)`;
            localBusinessPrevBtn.disabled = currentLocalBusinessPage <= 1;
            localBusinessNextBtn.disabled = currentLocalBusinessPage >= totalLocalBusinessPages;
        }
    }

    // Function to handle local business row selection
    function handleLocalBusinessRowSelection(event) {
        const checkbox = event.target;
        const businessId = checkbox.value;
        const row = checkbox.closest('tr');

        if (checkbox.checked) {
            selectedLocalBusinessIds.add(businessId);
            if (row) row.classList.add('selected-row');
        } else {
            selectedLocalBusinessIds.delete(businessId);
            if (row) row.classList.remove('selected-row');
            if (selectAllLocalBusinessCheckbox) selectAllLocalBusinessCheckbox.checked = false;
        }
        updateLocalBusinessBatchControls();
    }

    // Function to toggle select all for local businesses
    function toggleSelectAllLocalBusiness(event) {
        if (!localBusinessTableBody) return;
        const isChecked = event.target.checked;
        const visibleCheckboxes = localBusinessTableBody.querySelectorAll('.local-business-select-checkbox');

        visibleCheckboxes.forEach(checkbox => {
            const businessId = checkbox.value;
            const row = checkbox.closest('tr');
            checkbox.checked = isChecked;
            if (isChecked) {
                selectedLocalBusinessIds.add(businessId);
                if (row) row.classList.add('selected-row');
            } else {
                selectedLocalBusinessIds.delete(businessId);
                if (row) row.classList.remove('selected-row');
            }
        });
        updateLocalBusinessBatchControls();
    }

    // Function to update local business batch controls
    function updateLocalBusinessBatchControls() {
        if (!localBusinessBatchUpdateControls || !applyLocalBusinessBatchUpdateBtn || !clearLocalBusinessSelectionBtn || !localBusinessBatchStatusUpdate) return;
        const count = selectedLocalBusinessIds.size;
        if (count > 0) {
            localBusinessBatchUpdateControls.style.display = 'block';
            applyLocalBusinessBatchUpdateBtn.textContent = `Update ${count} Selected`;
            applyLocalBusinessBatchUpdateBtn.disabled = false;
            clearLocalBusinessSelectionBtn.disabled = false;
        } else {
            localBusinessBatchUpdateControls.style.display = 'none';
            applyLocalBusinessBatchUpdateBtn.textContent = 'Update 0 Selected';
            applyLocalBusinessBatchUpdateBtn.disabled = true;
            clearLocalBusinessSelectionBtn.disabled = true;
        }
        localBusinessBatchStatusUpdate.value = "";
    }

    // Function to clear local business selection
    function clearLocalBusinessSelection() {
        selectedLocalBusinessIds.clear();
        if (localBusinessTableBody) {
            localBusinessTableBody.querySelectorAll('.local-business-select-checkbox').forEach(cb => {
                cb.checked = false;
                const row = cb.closest('tr');
                if (row) row.classList.remove('selected-row');
            });
        }
        if (selectAllLocalBusinessCheckbox) selectAllLocalBusinessCheckbox.checked = false;
        updateLocalBusinessBatchControls();
    }

    // Function to batch update local business status
    async function batchUpdateLocalBusinessStatus() {
        const token = getJwtToken();
        if (!token) {
            showStatus('JWT Token is required.', 'error', 'localBusinessStatus');
            return;
        }

        const businessIdsToUpdate = Array.from(selectedLocalBusinessIds);
        const targetStatus = localBusinessBatchStatusUpdate ? localBusinessBatchStatusUpdate.value : null;

        if (businessIdsToUpdate.length === 0) {
            showStatus('No items selected for update.', 'warning', 'localBusinessStatus');
            return;
        }
        if (!targetStatus) {
            showStatus('Please select a target status.', 'warning', 'localBusinessStatus');
            return;
        }

        const apiUrl = '/api/v3/local-businesses/status';
        const payload = {
            local_business_ids: businessIdsToUpdate,
            status: targetStatus
        };

        if (applyLocalBusinessBatchUpdateBtn) {
            applyLocalBusinessBatchUpdateBtn.disabled = true;
            applyLocalBusinessBatchUpdateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
        }

        const fetchFn = typeof debugFetch === 'function' ? debugFetch : fetch;

        try {
            showStatus('Sending batch update for local businesses...', 'info', 'localBusinessStatus');
            const response = await fetchFn(apiUrl, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error during batch update' }));
                throw new Error(`HTTP error! Status: ${response.status} - ${errorData.detail || response.statusText}`);
            }

            const result = await response.json();
            const updatedCount = result.updated_count || 0;
            const queuedCount = result.queued_count || 0; // Capture queued for domain extraction count

            showStatus(`Successfully updated status for ${updatedCount} businesses. Queued for domain extraction: ${queuedCount}.`, 'success', 'localBusinessStatus');
            clearLocalBusinessSelection();
            fetchLocalBusinessData(currentLocalBusinessPage); // Refresh after update

        } catch (error) {
            console.error('Error updating local business status:', error);
            showStatus(`Error updating status: ${error.message}`, 'error', 'localBusinessStatus');
        } finally {
            updateLocalBusinessBatchControls(); // Reset button state
        }
    }

    // Function to reset local business filters
    function resetLocalBusinessFilters() {
        if (localBusinessStatusFilter) localBusinessStatusFilter.value = 'New'; // Default to 'New'
        if (localBusinessNameFilter) localBusinessNameFilter.value = '';
        fetchLocalBusinessData(1); // Fetch page 1 with reset filters
    }

    // Event Listeners for Local Business Curation
    if (localBusinessPrevBtn) localBusinessPrevBtn.addEventListener('click', () => {
        if (currentLocalBusinessPage > 1) {
            fetchLocalBusinessData(currentLocalBusinessPage - 1);
        }
    });

    if (localBusinessNextBtn) localBusinessNextBtn.addEventListener('click', () => {
        if (currentLocalBusinessPage < totalLocalBusinessPages) {
            fetchLocalBusinessData(currentLocalBusinessPage + 1);
        }
    });

    if (selectAllLocalBusinessCheckbox) selectAllLocalBusinessCheckbox.addEventListener('change', toggleSelectAllLocalBusiness);

    if (applyLocalBusinessBatchUpdateBtn) applyLocalBusinessBatchUpdateBtn.addEventListener('click', batchUpdateLocalBusinessStatus);

    if (clearLocalBusinessSelectionBtn) clearLocalBusinessSelectionBtn.addEventListener('click', clearLocalBusinessSelection);

    if (applyLocalBusinessFiltersBtn) applyLocalBusinessFiltersBtn.addEventListener('click', () => fetchLocalBusinessData(1)); // Fetch page 1 on apply

    if (resetLocalBusinessFiltersBtn) resetLocalBusinessFiltersBtn.addEventListener('click', resetLocalBusinessFilters);

    // Initial data load check (handled by tab switching logic in common.js primarily)
    const initialActiveTab = document.querySelector('.tab.tab-active');
    if (initialActiveTab && initialActiveTab.dataset.panel === 'localBusinessCuration') {
        console.log("Local Business Curation Tab JS: Initial fetch check.");
        fetchLocalBusinessData(1);
    }

    // Initialize controls state
    updateLocalBusinessBatchControls();

});
