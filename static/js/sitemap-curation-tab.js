document.addEventListener('DOMContentLoaded', () => {
    console.log("Sitemap Curation Tab JS Loaded");
    
    // Check if the global getJwtToken function exists
    if (typeof getJwtToken !== 'function') {
        console.error("Global getJwtToken function not found. Ensure google-maps-common.js is loaded before this script.");
        return; // Exit initialization if authentication function is missing
    }

    // --- Configuration & State ---
    const API_BASE_URL = '/api/v3';
    // Removed hardcoded token for security - now using getJwtToken() from google-maps-common.js
    const PAGE_SIZE = 15;

    let currentPage = 1;
    let totalPages = 1;
    let currentFilters = {
        deep_scrape_curation_status: 'New' // Default filter
    };
    let selectedSitemapFileIds = new Set(); // Stores selected UUIDs

    // --- DOM Element References ---
    const sitemapCurationTab = document.querySelector('.tab[data-panel="sitemapCurationPanel"]');
    const panel = document.getElementById('sitemapCurationPanel');
    if (!panel) {
        console.error("Sitemap Curation Panel not found!");
        return; // Stop if panel doesn't exist
    }

    // Filters
    const domainFilterInput = panel.querySelector('#sitemapDomainFilter'); // Assuming typeahead exists
    const curationStatusFilter = panel.querySelector('#sitemapDeepCurationStatusFilter');
    const urlFilterInput = panel.querySelector('#sitemapUrlFilter');
    const typeFilter = panel.querySelector('#sitemapTypeFilter'); // Add IDs in HTML if missing
    const discoveryFilter = panel.querySelector('#sitemapDiscoveryMethodFilter'); // Add IDs in HTML if missing
    const applyFiltersBtn = panel.querySelector('#sitemapApplyFiltersBtn');
    const resetFiltersBtn = panel.querySelector('#sitemapResetFiltersBtn');

    // Domain Suggestions
    const domainSuggestionsContainer = panel.querySelector('#sitemapDomainSuggestions');
    const domainIdInput = panel.querySelector('#sitemapDomainIdFilter'); // Hidden input, might not be needed if using data attribute

    // Status Message
    const statusMessageDiv = panel.querySelector('#sitemapStatusMessage');

    // Table
    const table = panel.querySelector('#sitemapCurationTable');
    const tableBody = panel.querySelector('#sitemapCurationTableBody');
    const selectAllCheckbox = panel.querySelector('#sitemapSelectAllCheckbox'); // Add ID in HTML if missing

    // Pagination
    const paginationControls = panel.querySelector('#sitemapPaginationControls');
    const prevPageBtn = panel.querySelector('#sitemapPrevPageBtn');
    const nextPageBtn = panel.querySelector('#sitemapNextPageBtn');
    const paginationInfo = panel.querySelector('#sitemapPaginationInfo');

    // Batch Update
    const batchUpdateSection = panel.querySelector('#sitemapBatchUpdateSection');
    const batchStatusSelect = panel.querySelector('#sitemapBatchStatusSelect');
    const batchUpdateBtn = panel.querySelector('#sitemapBatchUpdateBtn');
    const clearSelectionBtn = panel.querySelector('#sitemapClearSelectionBtn');


    // --- Helper Functions ---

    // Debounce function
    function debounce(func, delay) {
        let timeoutId;
        return function(...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                func.apply(this, args);
            }, delay);
        };
    }

    function showStatusMessage(message, isError = false) {
        if (!statusMessageDiv) return;
        statusMessageDiv.textContent = message;
        statusMessageDiv.className = `alert ${isError ? 'alert-danger' : 'alert-success'}`;
        statusMessageDiv.style.display = 'block';
        // Optionally hide after a delay
        // setTimeout(() => statusMessageDiv.style.display = 'none', 5000);
    }

    function hideStatusMessage() {
        if (!statusMessageDiv) return;
        statusMessageDiv.style.display = 'none';
    }

    function setLoadingState(isLoading) {
        // Improved visual loading indicators
        const buttonsToDisable = [
            applyFiltersBtn, resetFiltersBtn, prevPageBtn, nextPageBtn,
            batchUpdateBtn, clearSelectionBtn
        ];
        const inputsToDisable = [
            domainFilterInput, curationStatusFilter, urlFilterInput,
            typeFilter, discoveryFilter, batchStatusSelect
        ];

        if (isLoading) {
            console.log("Loading data...");
            if (tableBody) tableBody.innerHTML = `<tr><td colspan="7" class="text-center"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr>`;

            buttonsToDisable.forEach(btn => {
                if (btn) {
                    btn.disabled = true;
                    // Add spinner icon to specific buttons
                    if (btn === applyFiltersBtn || btn === batchUpdateBtn) {
                        // Store original text if not already stored
                        if (!btn.dataset.originalText) {
                            btn.dataset.originalText = btn.innerHTML;
                        }
                        btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Processing...`;
                    }
                }
            });
            inputsToDisable.forEach(input => {
                if (input) input.disabled = true;
            });
             if (selectAllCheckbox) selectAllCheckbox.disabled = true;

        } else {
            console.log("Loading complete.");
             buttonsToDisable.forEach(btn => {
                 if (btn) {
                    // Restore original text and remove spinner if added
                    if (btn.dataset.originalText) {
                        btn.innerHTML = btn.dataset.originalText;
                        delete btn.dataset.originalText; // Clean up
                    }
                    // Specific enable logic might depend on state (e.g., pagination, selection)
                    // We re-enable most, but pagination/batch buttons get updated by their specific functions
                    if (![prevPageBtn, nextPageBtn, batchUpdateBtn, clearSelectionBtn].includes(btn)) {
                         btn.disabled = false;
                    }
                 }
             });
             inputsToDisable.forEach(input => {
                 if (input) input.disabled = false;
             });
             if (selectAllCheckbox) selectAllCheckbox.disabled = !tableBody || tableBody.rows.length === 0 || (tableBody.rows.length === 1 && tableBody.rows[0].cells.length < 7); // Disable if table is empty or shows loading/error message
             // Call updatePagination and updateBatchControls to set correct button states
             updatePagination(currentPage, totalPages, totalItemsState); // Need to store totalItems
             updateBatchControls(); // This will correctly set enable/disable state for batch buttons
        }
    }

    // --- Store totalItems globally for setLoadingState
    let totalItemsState = 0;

    function updateBatchControls() {
        if (!batchUpdateSection || !batchUpdateBtn || !clearSelectionBtn) return;
        const token = getJwtToken();
        if (!token) {
            showStatusMessage('JWT Token is required for authentication.', true);
            return;
        }
        const count = selectedSitemapFileIds.size;
        if (count > 0) {
            batchUpdateSection.style.display = 'block';
            batchUpdateBtn.textContent = `Update ${count} Selected`;
            batchUpdateBtn.disabled = !batchStatusSelect.value; // Disable if no status selected
            clearSelectionBtn.style.display = 'inline-block';
        } else {
            batchUpdateSection.style.display = 'none';
            clearSelectionBtn.style.display = 'none';
        }
    }


    // --- Domain Typeahead Functions ---
    async function fetchDomainSuggestions(query) {
        if (!query || query.length < 2) {
            hideDomainSuggestions();
            return;
        }
        console.log(`Fetching domain suggestions for: ${query}`);
        // Removed size limit (was &size=10) to fetch all matching suggestions for better usability during MVP.
        // TODO: Consider re-adding a limit post-MVP if performance becomes an issue with many domains.
        // Corrected parameter name to match backend router ('domain_filter')
        const url = `${API_BASE_URL}/domains/?domain_filter=${encodeURIComponent(query)}`;

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${getJwtToken()}`,
                    'Accept': 'application/json'
                }
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            renderDomainSuggestions(data.items || []);
        } catch (error) {
            console.error('Error fetching domain suggestions:', error);
            // Optionally show a small error in the suggestions box
            if (domainSuggestionsContainer) {
                 domainSuggestionsContainer.innerHTML = '<div class="suggestion-item text-danger">Error loading suggestions</div>';
                 domainSuggestionsContainer.style.display = 'block';
            }
        }
    }

    function renderDomainSuggestions(suggestions) {
        if (!domainSuggestionsContainer) return;
        domainSuggestionsContainer.innerHTML = ''; // Clear previous suggestions

        if (suggestions.length === 0) {
            domainSuggestionsContainer.innerHTML = '<div class="suggestion-item text-muted">No matching domains found</div>';
        } else {
            suggestions.forEach(domain => {
                const item = document.createElement('div');
                item.className = 'suggestion-item';
                item.textContent = domain.domain; // Display domain name
                item.dataset.domainId = domain.id; // Store ID on the element
                item.addEventListener('click', handleDomainSuggestionClick);
                domainSuggestionsContainer.appendChild(item);
            });
        }
        domainSuggestionsContainer.style.display = 'block';
    }

    function handleDomainSuggestionClick(event) {
        const selectedDomain = event.target.textContent;
        const selectedDomainId = event.target.dataset.domainId;

        if (domainFilterInput) {
            domainFilterInput.value = selectedDomain;
            // Store the ID directly on the input element using a data attribute
            domainFilterInput.dataset.selectedDomainId = selectedDomainId;
            console.log(`Selected Domain: ${selectedDomain}, ID: ${selectedDomainId}`);
        }
        // If using the hidden input (optional)
        // if (domainIdInput) {
        //     domainIdInput.value = selectedDomainId;
        // }
        hideDomainSuggestions();
    }

    function hideDomainSuggestions() {
        if (domainSuggestionsContainer) {
            domainSuggestionsContainer.style.display = 'none';
        }
    }

     // Debounced version of fetchDomainSuggestions
    const debouncedFetchDomainSuggestions = debounce(fetchDomainSuggestions, 300); // 300ms delay

    // --- Core Functions ---

    async function fetchData() {
        setLoadingState(true);
        hideStatusMessage();
        const params = new URLSearchParams({
            page: currentPage,
            size: PAGE_SIZE,
            sort_by: 'updated_at', // Add default sort field
            sort_desc: 'true',     // Add default sort direction
            ...currentFilters // Spread current filters
        });

        // Remove empty filter values
        for (let key in currentFilters) {
            if (!currentFilters[key]) {
                params.delete(key);
            }
        }

        const url = `${API_BASE_URL}/sitemap-files/?${params.toString()}`;
        console.log(`Fetching: ${url}`);

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${getJwtToken()}`,
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error fetching data' }));
                throw new Error(`HTTP error! Status: ${response.status} - ${errorData.detail}`);
            }

            const data = await response.json();
            console.log("Data received:", data);
            renderTable(data.items);
            updatePagination(data.page, data.pages, data.total);
            updateBatchControls(); // Update controls based on persisted selection state across pages

        } catch (error) {
            console.error('Error fetching sitemap files:', error);
            showStatusMessage(`Error fetching data: ${error.message}`, true);
            if (tableBody) tableBody.innerHTML = '<tr><td colspan="7">Error loading data.</td></tr>'; // Indicate error in table
        } finally {
            setLoadingState(false);
        }
    }

    function renderTable(items) {
        if (!tableBody) return;
        tableBody.innerHTML = ''; // Clear existing rows

        if (!items || items.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7">No sitemap files found matching the criteria.</td></tr>';
            if (selectAllCheckbox) selectAllCheckbox.checked = false;
             if (selectAllCheckbox) selectAllCheckbox.disabled = true;
            return;
        }
         if (selectAllCheckbox) selectAllCheckbox.disabled = false;

        let allVisibleChecked = true; // Assume all are checked initially

        items.forEach(item => {
            const row = tableBody.insertRow();
            row.dataset.id = item.id; // Store ID on the row

            // Checkbox Cell
            const cellCheckbox = row.insertCell();
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = item.id;
            checkbox.checked = selectedSitemapFileIds.has(item.id);
            checkbox.addEventListener('change', handleRowSelection);
            cellCheckbox.appendChild(checkbox);

            if (!checkbox.checked) {
                allVisibleChecked = false; // If any are not checked, flag it
            }

            // Data Cells (adjust indices based on actual table headers)
            row.insertCell().textContent = item.sitemap_url || 'N/A';
            row.insertCell().textContent = item.domain_name || 'N/A';

            // Curation Status Cell with Badge
            const curationStatusCell = row.insertCell();
            const curationStatus = item.deep_scrape_curation_status || 'New';
            curationStatusCell.innerHTML = `<span class="badge badge-${curationStatus.toLowerCase().replace(/[^a-z0-9]+/g, '_')}">${curationStatus}</span>`;

            // Process Status Cell with Badge
            const processStatusCell = row.insertCell();
            const processStatus = item.deep_scrape_process_status;
            if (processStatus) {
                 processStatusCell.innerHTML = `<span class="badge badge-${processStatus.toLowerCase()}">${processStatus}</span>`;
            } else {
                 processStatusCell.textContent = 'N/A';
            }

             // Original Status Cell with Badge
            const originalStatusCell = row.insertCell();
            const originalStatus = item.status;
             if (originalStatus) {
                 originalStatusCell.innerHTML = `<span class="badge badge-${originalStatus.toLowerCase()}">${originalStatus}</span>`;
             } else {
                 originalStatusCell.textContent = 'N/A';
             }

            // Updated At
            row.insertCell().textContent = item.updated_at ? new Date(item.updated_at).toLocaleString() : 'N/A';

             // Highlight row if selected
            if (checkbox.checked) {
                row.classList.add('selected-row'); // Add a class for styling selected rows
            }
        });

        // Update Select All checkbox state
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = allVisibleChecked;
        }
    }

    function updatePagination(page, pages, total) {
        currentPage = page;
        totalPages = pages;
        totalItemsState = total; // Store total items
        if (!paginationInfo || !prevPageBtn || !nextPageBtn) return;

        if (total === 0) {
             paginationInfo.textContent = 'No items found';
        } else {
             paginationInfo.textContent = `Page ${page} of ${pages} (${total} items)`;
        }


        prevPageBtn.disabled = page <= 1;
        nextPageBtn.disabled = page >= pages;
    }


    // --- Event Handlers ---

    function handleRowSelection(event) {
        console.log('handleRowSelection triggered', event.target.value, event.target.checked);
        const checkbox = event.target;
        const id = checkbox.value;
        const row = checkbox.closest('tr');

        if (checkbox.checked) {
            selectedSitemapFileIds.add(id);
             if (row) row.classList.add('selected-row');
        } else {
            selectedSitemapFileIds.delete(id);
             if (row) row.classList.remove('selected-row');
            // If we uncheck any row, the "Select All" must be unchecked
            if (selectAllCheckbox) selectAllCheckbox.checked = false;
        }
        updateBatchControls();
         // Check if all visible rows are now checked to update Select All state
        checkAllVisibleSelected();
    }

     function checkAllVisibleSelected() {
        if (!selectAllCheckbox) return;
        const visibleCheckboxes = tableBody.querySelectorAll('input[type="checkbox"]');
        if (visibleCheckboxes.length === 0) {
            selectAllCheckbox.checked = false;
            return;
        }
        let allChecked = true;
        visibleCheckboxes.forEach(cb => {
            if (!cb.checked) {
                allChecked = false;
            }
        });
        selectAllCheckbox.checked = allChecked;
    }

    function handleSelectAll(event) {
        const isChecked = event.target.checked;
        const visibleCheckboxes = tableBody.querySelectorAll('input[type="checkbox"]');

        visibleCheckboxes.forEach(checkbox => {
            const id = checkbox.value;
            const row = checkbox.closest('tr');
            checkbox.checked = isChecked;
            if (isChecked) {
                selectedSitemapFileIds.add(id);
                if (row) row.classList.add('selected-row');
            } else {
                selectedSitemapFileIds.delete(id);
                 if (row) row.classList.remove('selected-row');
            }
        });
        updateBatchControls();
    }

    function handleApplyFilters() {
        currentFilters = {
            // Read domain_id from the data attribute set by the suggestion click handler
            domain_id: domainFilterInput ? domainFilterInput.dataset.selectedDomainId : undefined,
            deep_scrape_curation_status: curationStatusFilter ? curationStatusFilter.value : undefined,
            url_contains: urlFilterInput ? urlFilterInput.value.trim() : undefined,
            sitemap_type: typeFilter ? typeFilter.value : undefined,
            discovery_method: discoveryFilter ? discoveryFilter.value : undefined
        };
        // Remove undefined/empty filters
        Object.keys(currentFilters).forEach(key => {
            if (currentFilters[key] === undefined || currentFilters[key] === '') {
                delete currentFilters[key];
            }
        });
        currentPage = 1; // Reset to first page on new filter application
        fetchData();
    }

    function handleResetFilters() {
        // Reset UI elements
        if (domainFilterInput) {
             domainFilterInput.value = '';
             delete domainFilterInput.dataset.selectedDomainId; // Clear stored ID
         }
        if (curationStatusFilter) curationStatusFilter.value = 'New'; // Default
        if (urlFilterInput) urlFilterInput.value = '';
        if (typeFilter) typeFilter.value = '';
        if (discoveryFilter) discoveryFilter.value = '';

        // Reset filters state to default and fetch
        currentFilters = { deep_scrape_curation_status: 'New' };
        currentPage = 1;
        fetchData();
    }

    function handlePagination(direction) {
        if (direction === 'prev' && currentPage > 1) {
            currentPage--;
        } else if (direction === 'next' && currentPage < totalPages) {
            currentPage++;
        }
        fetchData();
    }

    async function performBatchUpdate() {
        const newStatus = batchStatusSelect.value;
        if (!newStatus || selectedSitemapFileIds.size === 0) {
            showStatusMessage("Please select a status and at least one item.", true);
            return;
        }

        setLoadingState(true);
        hideStatusMessage();

        const payload = {
            sitemap_file_ids: Array.from(selectedSitemapFileIds),
            deep_scrape_curation_status: newStatus
        };

        console.log("Sending batch update:", payload);

        try {
            const response = await fetch(`${API_BASE_URL}/sitemap-files/status`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${getJwtToken()}`,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                 const errorData = await response.json().catch(() => ({ detail: 'Unknown error during batch update' }));
                throw new Error(`HTTP error! Status: ${response.status} - ${errorData.detail}`);
            }

            const result = await response.json();
            console.log("Batch update result:", result);

            // Construct success message based on response counts
            let message = `Successfully updated curation status for ${result.updated_count} items.`;
            if (result.hasOwnProperty('queued_count')) {
                 if (result.queued_count < result.updated_count) {
                    message += ` ${result.queued_count} items queued for processing (${result.updated_count - result.queued_count} item(s) were likely already processing).`;
                 } else if (result.queued_count === result.updated_count && newStatus === 'Selected') {
                     message += ` All ${result.queued_count} items queued for processing.`;
                 } else if (result.queued_count > 0 && newStatus !== 'Selected'){
                     // This case shouldn't happen based on backend logic, but good to acknowledge
                     message += ` ${result.queued_count} items were unexpectedly queued.`;
                 }
            }

            showStatusMessage(message, false);
            selectedSitemapFileIds.clear();
            if(selectAllCheckbox) selectAllCheckbox.checked = false;
            updateBatchControls();
            fetchData(); // Refresh data on the current page

        } catch (error) {
            console.error('Error performing batch update:', error);
            showStatusMessage(`Batch update failed: ${error.message}`, true);
        } finally {
             // Ensure loading state is cleared even if fetchData isn't called due to error prior
            setLoadingState(false);
             updateBatchControls(); // Reset batch controls state after attempt
        }
    }

     function handleClearSelection() {
        selectedSitemapFileIds.clear();
        // Uncheck all visible checkboxes
        const visibleCheckboxes = tableBody.querySelectorAll('input[type="checkbox"]');
        visibleCheckboxes.forEach(checkbox => {
             checkbox.checked = false;
             const row = checkbox.closest('tr');
             if (row) row.classList.remove('selected-row');
        });
        if (selectAllCheckbox) selectAllCheckbox.checked = false;
        updateBatchControls();
    }


    // --- Initialization & Event Listeners ---

    function initializeTab() {
        console.log("Initializing Sitemap Curation Tab");
        // Set up initial state for filters if needed
        if (curationStatusFilter) curationStatusFilter.value = 'New';

        // Attach event listeners
        if (applyFiltersBtn) applyFiltersBtn.addEventListener('click', handleApplyFilters);
        if (resetFiltersBtn) resetFiltersBtn.addEventListener('click', handleResetFilters);
        if (prevPageBtn) prevPageBtn.addEventListener('click', () => handlePagination('prev'));
        if (nextPageBtn) nextPageBtn.addEventListener('click', () => handlePagination('next'));
        if (selectAllCheckbox) selectAllCheckbox.addEventListener('change', handleSelectAll);
        if (batchUpdateBtn) batchUpdateBtn.addEventListener('click', performBatchUpdate);
         if (clearSelectionBtn) clearSelectionBtn.addEventListener('click', handleClearSelection);

        // --- Domain Typeahead Listener ---
        if (domainFilterInput) {
            domainFilterInput.addEventListener('input', (event) => {
                const query = event.target.value.trim();
                // Clear stored domain ID if user clears or changes input without selecting suggestion
                 delete domainFilterInput.dataset.selectedDomainId;
                debouncedFetchDomainSuggestions(query);
            });

            // Hide suggestions if user clicks outside the input/suggestions
            document.addEventListener('click', (event) => {
                if (domainFilterInput && !domainFilterInput.contains(event.target) && domainSuggestionsContainer && !domainSuggestionsContainer.contains(event.target)) {
                    hideDomainSuggestions();
                }
            });
        }

        // Initial data fetch
        fetchData();
        updateBatchControls(); // Hide batch section initially
    }

    // --- Tab Activation Logic ---
    // Use MutationObserver to detect when the panel becomes visible
    const observer = new MutationObserver((mutationsList, observer) => {
        for(const mutation of mutationsList) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                 // Check if the panel is being displayed
                if (panel.style.display !== 'none' && panel.style.display !== '') {
                    console.log("Sitemap Curation Panel activated.");
                     // Check if it needs initialization (e.g., first time shown)
                     if (!panel.dataset.initialized) {
                        initializeTab();
                        panel.dataset.initialized = 'true'; // Mark as initialized
                     }
                }
            }
        }
    });

     // Start observing the panel for changes in style attribute (related to display)
    if (panel) {
         observer.observe(panel, { attributes: true });
         // Also check initial state in case it's the default active tab
        if (panel.style.display !== 'none' && panel.style.display !== '' && !panel.dataset.initialized) {
            initializeTab();
            panel.dataset.initialized = 'true';
        }
    } else {
         console.error("Sitemap Curation Panel does not exist for observer.");
    }

     // Fallback/Alternative: Listen for clicks on the tab button itself
     // This might trigger initialization slightly before the panel is fully visible
     // but is less reliant on the specific show/hide mechanism.
     if (sitemapCurationTab) {
         sitemapCurationTab.addEventListener('click', () => {
             // Use a small delay to allow the panel display style to potentially update
             setTimeout(() => {
                if (panel && panel.style.display !== 'none' && !panel.dataset.initialized) {
                     console.log("Sitemap Curation Tab clicked, initializing...");
                    initializeTab();
                     panel.dataset.initialized = 'true';
                 }
             }, 50); // 50ms delay, adjust if needed
         });
     }

});
