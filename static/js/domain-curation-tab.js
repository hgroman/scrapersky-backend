document.addEventListener('DOMContentLoaded', () => {
    console.log("Domain Curation Tab JS Loaded");

    // ======================================================
    // Domain Curation Logic (Adapted from Local Business)
    // ======================================================

    // --- Configuration & State ---
    const API_BASE_URL_DC = '/api/v3'; // Use unique prefix if needed
    // Removed hardcoded token for security
    const PAGE_SIZE_DC = 15;

    let currentDomainCurationPage = 1;
    let totalDomainCurationPages = 1;
    let totalDomainCurationItems = 0;
    let selectedDomainIds = new Set(); // Stores selected UUIDs

    // --- DOM Element References (Scoped within panel) ---
    const domainCurationTab = document.querySelector('.tab[data-panel="domainCurationPanel"]');
    const panelDC = document.getElementById('domainCurationPanel'); // Renamed to avoid conflict
    let domainCurationStatusFilter, domainCurationNameFilter, applyDomainCurationFiltersBtn, resetDomainCurationFiltersBtn;
    let domainCurationTableBody, selectAllDomainCurationCheckbox;
    let domainCurationPaginationInfo, domainCurationPrevBtn, domainCurationNextBtn;
    let domainCurationBatchUpdateControls, domainCurationBatchStatusUpdate, applyDomainCurationBatchUpdateBtn, clearDomainCurationSelectionBtn;
    let domainCurationStatusDiv;

    // Function to query elements *after* panel is confirmed available
    function queryDCElements() {
        if (!panelDC) return false;
        domainCurationStatusFilter = panelDC.querySelector('#domainCurationStatusFilter');
        domainCurationNameFilter = panelDC.querySelector('#domainCurationNameFilter');
        applyDomainCurationFiltersBtn = panelDC.querySelector('#applyDomainCurationFiltersBtn');
        resetDomainCurationFiltersBtn = panelDC.querySelector('#resetDomainCurationFiltersBtn');
        domainCurationTableBody = panelDC.querySelector('#domainCurationTableBody');
        selectAllDomainCurationCheckbox = panelDC.querySelector('#selectAllDomainCurationCheckbox');
        domainCurationPaginationInfo = panelDC.querySelector('#domainCurationPaginationInfo');
        domainCurationPrevBtn = panelDC.querySelector('#domainCurationPrevBtn');
        domainCurationNextBtn = panelDC.querySelector('#domainCurationNextBtn');
        domainCurationBatchUpdateControls = panelDC.querySelector('#domainCurationBatchUpdateControls');
        domainCurationBatchStatusUpdate = panelDC.querySelector('#domainCurationBatchStatusUpdate');
        applyDomainCurationBatchUpdateBtn = panelDC.querySelector('#applyDomainCurationBatchUpdateBtn');
        clearDomainCurationSelectionBtn = panelDC.querySelector('#clearDomainCurationSelectionBtn');
        domainCurationStatusDiv = panelDC.querySelector('#domainCurationStatus'); // For showStatus

        // ADDED: Debug logs to check elements
        console.log("DOM ELEMENTS DEBUG:");
        console.log("- Batch Controls div found:", !!domainCurationBatchUpdateControls);
        console.log("- Status dropdown found:", !!domainCurationBatchStatusUpdate);
        console.log("- Apply button found:", !!applyDomainCurationBatchUpdateBtn);
        console.log("- Clear button found:", !!clearDomainCurationSelectionBtn);

        return true; // Indicate elements are likely found
    }

    // --- Helper Functions ---
    function getJwtTokenDC() { // Using global getJwtToken function
        // Check if the global function exists
        if (typeof getJwtToken !== 'function') {
            console.error("Global getJwtToken function not found. Ensure google-maps-common.js is loaded.");
            return null;
        }
        return getJwtToken();
    }

    function showStatusDC(message, type = 'info', targetDivId = 'domainCurationStatus') { // Renamed
        const targetDiv = panelDC ? panelDC.querySelector(`#${targetDivId}`) : null;
        if (!targetDiv) {
            console.warn(`showStatusDC: Target div #${targetDivId} not found in panel.`);
            return;
        }
        targetDiv.textContent = message;
        targetDiv.className = `alert alert-${type === 'error' ? 'danger' : type}`; // Map types
        targetDiv.style.display = 'block';
        // Optional: Hide after delay
    }

    function hideStatusDC(targetDivId = 'domainCurationStatus') { // Renamed
        const targetDiv = panelDC ? panelDC.querySelector(`#${targetDivId}`) : null;
        if (targetDiv) {
            targetDiv.style.display = 'none';
        }
    }

    function initializeTooltips(container) {
        if (!container) return;
        const tooltipTriggerList = [].slice.call(container.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            // Ensure no existing tooltip instance before creating a new one
            let tooltipInstance = bootstrap.Tooltip.getInstance(tooltipTriggerEl);
            if (!tooltipInstance) {
                tooltipInstance = new bootstrap.Tooltip(tooltipTriggerEl);
            }
            return tooltipInstance;
        });
    }

    // --- Core Functions (Modified for safety) ---

    async function fetchDomainCurationData(page = 1) {
        if (!panelDC || !queryDCElements()) {
            console.error("fetchDomainCurationData: Panel or elements not available.");
            return; // Don't fetch if panel isn't ready
        }

        const token = getJwtTokenDC();
        if (!token) {
            showStatusDC('JWT Token is required.', 'error');
            return;
        }
        hideStatusDC();
        // Basic Loading state (can be enhanced)
        if(domainCurationTableBody) domainCurationTableBody.innerHTML = '<tr><td colspan="6" class="text-center"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr>';

        currentDomainCurationPage = page;
        const queryParams = new URLSearchParams({
            page: currentDomainCurationPage,
            size: PAGE_SIZE_DC
        });

        const statusFilter = domainCurationStatusFilter ? domainCurationStatusFilter.value : '';
        const nameFilter = domainCurationNameFilter ? domainCurationNameFilter.value : '';

        if (statusFilter) {
            queryParams.append('sitemap_curation_status', statusFilter); // API param name
        }
        if (nameFilter) {
            queryParams.append('domain', nameFilter); // API param name
        }

        const apiUrl = `${API_BASE_URL_DC}/domains?${queryParams.toString()}`; // Use the correct endpoint
        console.log(`Fetching DC: ${apiUrl}`);

        try {
            const response = await fetch(apiUrl, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error fetching domains' }));
                throw new Error(`HTTP error! Status: ${response.status} - ${errorData.detail || response.statusText}`);
            }

            const data = await response.json();
            console.log("DC Data received:", data);

            if (data && data.items) {
                renderDomainCurationTable(data.items);
                currentDomainCurationPage = data.page;
                totalDomainCurationPages = data.pages;
                totalDomainCurationItems = data.total;
                updateDomainCurationPagination();
            } else {
                if (domainCurationTableBody) domainCurationTableBody.innerHTML = '<tr><td colspan="6" class="text-center">No domains found for the current filter.</td></tr>';
                updateDomainCurationPagination(true); // Update pagination even if no data
            }
        } catch (error) {
            console.error('Error fetching domains:', error);
            if (domainCurationTableBody) domainCurationTableBody.innerHTML = `<tr><td colspan="6" class="text-center">Error loading data: ${error.message}</td></tr>`;
            updateDomainCurationPagination(true); // Reset pagination on error
            showStatusDC(`Error fetching domains: ${error.message}`, 'error');
        }
    }

    function renderDomainCurationTable(items) {
        if (!domainCurationTableBody) {
            console.error("renderDomainCurationTable: domainCurationTableBody not found!");
            return; // Added null check
        }
        domainCurationTableBody.innerHTML = ''; // Clear previous rows
        if (!items || items.length === 0) {
            domainCurationTableBody.innerHTML = '<tr><td colspan="6" class="text-center">No data available.</td></tr>'; // colspan=6
            if (selectAllDomainCurationCheckbox) selectAllDomainCurationCheckbox.disabled = true;
            return;
        }
        if (selectAllDomainCurationCheckbox) selectAllDomainCurationCheckbox.disabled = false;

        let allVisibleChecked = true;

        items.forEach(item => {
            const row = domainCurationTableBody.insertRow();
            row.dataset.domainId = item.id; // Store domain id on the row

            // Checkbox cell
            const cellCheckbox = row.insertCell();
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'form-check-input domain-curation-select-checkbox'; // Unique class
            checkbox.value = item.id;
            checkbox.checked = selectedDomainIds.has(item.id); // Maintain checked state across pages
            checkbox.addEventListener('change', handleDomainCurationRowSelection);
            cellCheckbox.appendChild(checkbox);

            if (!checkbox.checked) allVisibleChecked = false;

            // Data cells
            row.insertCell().textContent = item.domain || 'N/A';

            // Sitemap Curation Status with badge
            const curationStatusCell = row.insertCell();
            const curationStatusBadge = document.createElement('span');
            const curationStatus = item.sitemap_curation_status || 'New';
            // Create a CSS-friendly class name (e.g., "not_a_fit")
            const curationStatusClass = `badge badge-${curationStatus.toLowerCase().replace(/[^a-z0-9]+/g, '_')}`;
            curationStatusBadge.className = curationStatusClass; // Use Bootstrap badge classes + custom status
            curationStatusBadge.textContent = curationStatus;
            curationStatusCell.appendChild(curationStatusBadge);

            // Sitemap Analysis Status with badge
            const analysisStatusCell = row.insertCell();
            if (item.sitemap_analysis_status) {
                const analysisStatusBadge = document.createElement('span');
                const analysisStatusClass = `badge badge-${item.sitemap_analysis_status.toLowerCase()}`; // Ensure lowercase for class
                analysisStatusBadge.className = analysisStatusClass;
                analysisStatusBadge.textContent = item.sitemap_analysis_status;
                analysisStatusCell.appendChild(analysisStatusBadge);
            } else {
                analysisStatusCell.textContent = 'N/A';
            }

             // Analysis Error with tooltip
             const errorCell = row.insertCell();
             if (item.sitemap_analysis_error) {
                 const errorSpan = document.createElement('span');
                 errorSpan.style.cursor = 'pointer';
                  // Display first part of error, show full on hover/click potentially
                 const shortError = item.sitemap_analysis_error.length > 30 ? item.sitemap_analysis_error.substring(0, 27) + '...' : item.sitemap_analysis_error;
                  errorSpan.textContent = shortError;
                 errorSpan.setAttribute('data-bs-toggle', 'tooltip'); // Add Bootstrap attribute
                 errorSpan.setAttribute('data-bs-placement', 'top'); // Optional: placement
                 errorSpan.setAttribute('title', item.sitemap_analysis_error); // Bootstrap uses title
                  errorCell.appendChild(errorSpan);
              } else {
                  errorCell.textContent = '-'; // Placeholder if no error
              }


            // Updated At
            row.insertCell().textContent = item.updated_at ? new Date(item.updated_at).toLocaleString() : 'N/A';

            // Apply selected style if needed
            if (checkbox.checked) {
                row.classList.add('selected-row'); // Add custom class for selected row highlighting
            }
        });

        // Update Select All Checkbox state
        if (selectAllDomainCurationCheckbox) {
            selectAllDomainCurationCheckbox.checked = allVisibleChecked;
        }

        updateDomainCurationBatchControls(); // Update button count after rendering
        initializeTooltips(domainCurationTableBody); // Initialize tooltips after rendering rows
    }

    function updateDomainCurationPagination(isEmpty = false) {
        if (!panelDC || !queryDCElements()) return;

        if (isEmpty || totalDomainCurationItems === 0) {
            if(domainCurationPaginationInfo) domainCurationPaginationInfo.textContent = 'Page 0 of 0 (0 items)';
            if(domainCurationPrevBtn) domainCurationPrevBtn.disabled = true;
            if(domainCurationNextBtn) domainCurationNextBtn.disabled = true;
        } else {
            if(domainCurationPaginationInfo) domainCurationPaginationInfo.textContent = `Page ${currentDomainCurationPage} of ${totalDomainCurationPages} (${totalDomainCurationItems} items)`;
            if(domainCurationPrevBtn) domainCurationPrevBtn.disabled = currentDomainCurationPage <= 1;
            if(domainCurationNextBtn) domainCurationNextBtn.disabled = currentDomainCurationPage >= totalDomainCurationPages;
        }
    }

    // --- Checkbox / Selection Logic --- Fixes Applied ---

    function handleDomainCurationRowSelection(event) {
        if (!event || !event.target) return;
        const checkbox = event.target;
        const domainId = checkbox.value; // Assuming value holds the UUID
        const row = checkbox.closest('tr');

        if (checkbox.checked) {
            selectedDomainIds.add(domainId);
            if (row) row.classList.add('selected-row');
            console.log("Added DC ID:", domainId, "Current selection:", selectedDomainIds);
        } else {
            selectedDomainIds.delete(domainId);
            if (row) row.classList.remove('selected-row');
            console.log("Removed DC ID:", domainId, "Current selection:", selectedDomainIds);
        }

        // Update Select All checkbox if necessary
        checkAllVisibleDomainCurationSelected();
        updateDomainCurationBatchControls(); // Update button count
    }

    function checkAllVisibleDomainCurationSelected() {
        if (!panelDC || !queryDCElements()) return;
        const visibleCheckboxes = panelDC.querySelectorAll('.domain-curation-select-checkbox');
        let allChecked = visibleCheckboxes.length > 0; // Start true only if there are checkboxes
        visibleCheckboxes.forEach(cb => {
            if (!cb.checked) {
                allChecked = false;
            }
        });
        if (selectAllDomainCurationCheckbox) {
            selectAllDomainCurationCheckbox.checked = allChecked;
        }
    }

    function toggleSelectAllDomainCuration(event) {
        if (!panelDC || !queryDCElements() || !event || !event.target) return;
        const isChecked = event.target.checked;
        console.log(`Select All toggled to: ${isChecked}`);
        const visibleCheckboxes = panelDC.querySelectorAll('.domain-curation-select-checkbox');

        visibleCheckboxes.forEach(checkbox => {
            const domainId = checkbox.value;
            checkbox.checked = isChecked;
            const row = checkbox.closest('tr');
            if (isChecked) {
                selectedDomainIds.add(domainId);
                if (row) row.classList.add('selected-row');
            } else {
                selectedDomainIds.delete(domainId);
                if (row) row.classList.remove('selected-row');
            }
        });

        console.log("Selection after Select All:", selectedDomainIds);
        updateDomainCurationBatchControls(); // Update button count
    }

    // --- Batch Update Logic ---

    function updateDomainCurationBatchControls() {
        if (!panelDC || !queryDCElements()) {
            console.warn("updateDomainCurationBatchControls: Panel or elements not ready.");
            return;
        }

        const selectedCount = selectedDomainIds.size;
        console.log(`Updating batch controls, selected count: ${selectedCount}`);

        if (applyDomainCurationBatchUpdateBtn) {
            applyDomainCurationBatchUpdateBtn.textContent = `Update ${selectedCount} Selected`;
            applyDomainCurationBatchUpdateBtn.disabled = selectedCount === 0;
        }
        if (clearDomainCurationSelectionBtn) {
            clearDomainCurationSelectionBtn.disabled = selectedCount === 0;
        }
        // Show/hide controls based on selection
        // if (domainCurationBatchUpdateControls) {
        //     domainCurationBatchUpdateControls.style.display = selectedCount > 0 ? 'block' : 'none';
        // }
    }

    function clearDomainCurationSelection() {
        console.log("Clearing DC selection");
        selectedDomainIds.clear();
        if (panelDC) {
            const checkboxes = panelDC.querySelectorAll('.domain-curation-select-checkbox');
            checkboxes.forEach(cb => {
                cb.checked = false;
                const row = cb.closest('tr');
                if (row) row.classList.remove('selected-row');
            });
            if (selectAllDomainCurationCheckbox) selectAllDomainCurationCheckbox.checked = false;
        }
        updateDomainCurationBatchControls(); // Update button count
    }

    async function batchUpdateDomainCurationStatus() {
        if (!panelDC || !queryDCElements()) return;

        const token = getJwtTokenDC();
        if (!token) {
            showStatusDC('JWT Token is required.', 'error');
            return;
        }

        const domainIdsToUpdate = Array.from(selectedDomainIds);
        const targetStatus = domainCurationBatchStatusUpdate ? domainCurationBatchStatusUpdate.value : '';

        if (domainIdsToUpdate.length === 0) {
            showStatusDC('No items selected for update.', 'warning');
            return;
        }
        if (!targetStatus) {
            showStatusDC('Please select a target status.', 'warning');
            return;
        }

        const apiUrl = `${API_BASE_URL_DC}/domains/sitemap-curation/status`; // Correct endpoint
        const payload = {
            domain_ids: domainIdsToUpdate,
            sitemap_curation_status: targetStatus
        };

        if(applyDomainCurationBatchUpdateBtn) {
            applyDomainCurationBatchUpdateBtn.disabled = true;
            applyDomainCurationBatchUpdateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
        }
        hideStatusDC();

        try {
            const response = await fetch(apiUrl, {
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
            const queuedCount = result.queued_count || 0;

            showStatusDC(`Successfully updated status for ${updatedCount} domains. Queued for sitemap analysis: ${queuedCount}.`, 'success');
            clearDomainCurationSelection(); // This already calls updateDomainCurationBatchControls
            fetchDomainCurationData(currentDomainCurationPage); // Refresh current page

        } catch (error) {
            console.error('Error updating domain sitemap curation status:', error);
            showStatusDC(`Error updating status: ${error.message}`, 'error');
        } finally {
            // Ensure button is re-enabled and text restored based on the *current* selection state
            // updateDomainCurationBatchControls(); // clearDomainCurationSelection already calls this, so it might be redundant here unless an error occurred without clearing selection
            if(applyDomainCurationBatchUpdateBtn) { // Check again as state might have changed
                // Get the latest count after potential clearing or errors
                const currentCount = selectedDomainIds.size;
                applyDomainCurationBatchUpdateBtn.innerHTML = `Update ${currentCount} Selected`;
                // Disable if count is 0 OR if the status dropdown is empty
                applyDomainCurationBatchUpdateBtn.disabled = currentCount === 0 || !domainCurationBatchStatusUpdate || !domainCurationBatchStatusUpdate.value;
            }
             // Ensure clear button state is also correct
            if (clearDomainCurationSelectionBtn) {
                clearDomainCurationSelectionBtn.disabled = selectedDomainIds.size === 0;
            }
        }
    }

    function resetDomainCurationFilters() {
         if (!queryDCElements()) return;
        if(domainCurationStatusFilter) domainCurationStatusFilter.value = ''; // Reset to default/empty
        if(domainCurationNameFilter) domainCurationNameFilter.value = '';
        fetchDomainCurationData(1); // Fetch page 1 with reset filters
    }

    function handleDCPagination(direction) {
        if (direction === 'prev' && currentDomainCurationPage > 1) {
            fetchDomainCurationData(currentDomainCurationPage - 1);
        } else if (direction === 'next' && currentDomainCurationPage < totalDomainCurationPages) {
            fetchDomainCurationData(currentDomainCurationPage + 1);
        }
    }

    // --- Initialization & Event Listeners ---
    function initializeDomainCurationTab() {
        console.log("Initializing Domain Curation Tab");
        if (!queryDCElements()) {
             console.error("Cannot initialize Domain Curation Tab: Panel or elements not found.");
             return;
        }
        panelDC.dataset.initialized = 'true'; // Mark as initialized

        // ADDED: Make batch controls visible by default
        if (domainCurationBatchUpdateControls) {
            domainCurationBatchUpdateControls.style.display = 'block';
            console.log("Forced batch controls to be visible");
        }

        // Attach event listeners ONLY after confirming elements exist
        if (domainCurationPrevBtn) domainCurationPrevBtn.addEventListener('click', () => handleDCPagination('prev'));
        if (domainCurationNextBtn) domainCurationNextBtn.addEventListener('click', () => handleDCPagination('next'));
        if (selectAllDomainCurationCheckbox) selectAllDomainCurationCheckbox.addEventListener('change', toggleSelectAllDomainCuration);
        if (applyDomainCurationBatchUpdateBtn) applyDomainCurationBatchUpdateBtn.addEventListener('click', batchUpdateDomainCurationStatus);
        if (clearDomainCurationSelectionBtn) clearDomainCurationSelectionBtn.addEventListener('click', clearDomainCurationSelection);
        if (applyDomainCurationFiltersBtn) applyDomainCurationFiltersBtn.addEventListener('click', () => fetchDomainCurationData(1));
        if (resetDomainCurationFiltersBtn) resetDomainCurationFiltersBtn.addEventListener('click', resetDomainCurationFilters);

        // Initial data fetch
        fetchDomainCurationData(1);
        updateDomainCurationBatchControls(); // Initial state for batch controls
    }

    // --- Tab Activation Logic ---
    if (panelDC) {
        const observerDC = new MutationObserver((mutationsList) => {
            for(const mutation of mutationsList) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    if (panelDC.style.display !== 'none' && panelDC.style.display !== '' && !panelDC.dataset.initialized) {
                        console.log("Domain Curation Panel activated via Observer.");
                        initializeDomainCurationTab();
                    }
                }
            }
        });
        observerDC.observe(panelDC, { attributes: true });

        // Check initial state in case it's the default active tab
        if (panelDC.style.display !== 'none' && panelDC.style.display !== '' && !panelDC.dataset.initialized) {
             console.log("Domain Curation Panel active on load.");
            initializeDomainCurationTab();
        }
    }

    // Fallback: Listen for clicks on the tab button itself
    if (domainCurationTab) {
        domainCurationTab.addEventListener('click', () => {
            // Use a small delay to allow the panel display style to potentially update
            setTimeout(() => {
                if (panelDC && panelDC.style.display !== 'none' && !panelDC.dataset.initialized) {
                    console.log("Domain Curation Tab clicked, initializing...");
                    initializeDomainCurationTab();
                }
            }, 50); // 50ms delay
        });
    }

});
