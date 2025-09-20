# Frontend Implementation Guide: Page Type Field Integration

**Date**: September 12, 2025  
**Backend Changes**: Deployed and Live  
**API Version**: v3  
**Endpoint**: `/api/v3/pages`

---

## OVERVIEW

The backend now returns a new `page_type` field in the WF7 pages endpoint, exposing Honeybee categorization results. This field contains values like `"contact_root"`, `"career_contact"`, `"unknown"`, etc., allowing users to filter and select pages by category.

---

## API CHANGES SUMMARY

### New Response Field
The GET `/api/v3/pages` endpoint now includes:

```json
{
  "pages": [
    {
      "id": "uuid",
      "url": "https://example.com/contact",
      "title": "Contact Us",
      "page_type": "contact_root",  // ← NEW FIELD
      "curation_status": "New",
      "processing_status": null,
      // ... other existing fields
    }
  ],
  "filters_applied": {
    "page_type": "contact_root"  // ← NEW FILTER TRACKING
  }
}
```

### New Query Parameter
- **Parameter**: `page_type`
- **Type**: Optional string
- **Values**: `"contact_root"`, `"career_contact"`, `"about_root"`, `"services_root"`, `"unknown"`, etc.
- **Example**: `GET /api/v3/pages?page_type=contact_root&limit=50`

### New Bulk Update Filter
The filtered update endpoint now accepts `page_type` in the request body:

```json
POST /api/v3/pages/status/filtered
{
  "status": "Selected",
  "page_type": "contact_root",  // ← NEW FILTER
  "page_curation_status": "New"
}
```

---

## FRONTEND IMPLEMENTATION STEPS

### Step 1: Update Type Definitions

Add the new field to your TypeScript interfaces:

```typescript
// types/pages.ts
export interface Page {
  id: string;
  url: string;
  title: string | null;
  domain_id: string | null;
  curation_status: string | null;
  processing_status: string | null;
  page_type: string | null;  // ← ADD THIS
  updated_at: string | null;
  created_at: string | null;
  error: string | null;
}

export interface PageFilters {
  page_curation_status?: string;
  page_processing_status?: string;
  page_type?: string;  // ← ADD THIS
  url_contains?: string;
}

export interface FilteredUpdateRequest {
  status: string;
  page_curation_status?: string;
  page_processing_status?: string;
  page_type?: string;  // ← ADD THIS
  url_contains?: string;
}
```

### Step 2: Add Page Type Filter UI Component

Create a dropdown/select component for page type filtering:

```typescript
// components/PageTypeFilter.tsx
import React from 'react';

const PAGE_TYPE_OPTIONS = [
  { value: '', label: 'All Page Types' },
  { value: 'contact_root', label: 'Contact Pages' },
  { value: 'career_contact', label: 'Career Pages' },
  { value: 'about_root', label: 'About Pages' },
  { value: 'services_root', label: 'Services Pages' },
  { value: 'menu_root', label: 'Menu Pages' },
  { value: 'pricing_root', label: 'Pricing Pages' },
  { value: 'team_root', label: 'Team Pages' },
  { value: 'legal_root', label: 'Legal Pages' },
  { value: 'wp_prospect', label: 'WordPress Prospects' },
  { value: 'unknown', label: 'Unknown/Uncategorized' }
];

interface PageTypeFilterProps {
  value: string;
  onChange: (value: string) => void;
}

export const PageTypeFilter: React.FC<PageTypeFilterProps> = ({ value, onChange }) => {
  return (
    <div className="filter-group">
      <label htmlFor="page-type-filter" className="filter-label">
        Page Type
      </label>
      <select
        id="page-type-filter"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="filter-select"
      >
        {PAGE_TYPE_OPTIONS.map(option => (
          <key={option.value} value={option.value}>
            {option.label}
          </key>
        ))}
      </select>
    </div>
  );
};
```

### Step 3: Update Main Pages Component

Integrate the page type filter into your existing pages list component:

```typescript
// components/PagesList.tsx
import React, { useState, useEffect } from 'react';
import { PageTypeFilter } from './PageTypeFilter';

export const PagesList: React.FC = () => {
  const [filters, setFilters] = useState<PageFilters>({
    page_curation_status: '',
    page_processing_status: '',
    page_type: '',  // ← ADD THIS
    url_contains: ''
  });

  const [pages, setPages] = useState<Page[]>([]);

  // Update your existing filter change handler
  const handleFilterChange = (filterKey: keyof PageFilters, value: string) => {
    setFilters(prev => ({
      ...prev,
      [filterKey]: value
    }));
  };

  // Update your API call to include page_type
  const fetchPages = async () => {
    const params = new URLSearchParams();
    if (filters.page_curation_status) params.append('page_curation_status', filters.page_curation_status);
    if (filters.page_processing_status) params.append('page_processing_status', filters.page_processing_status);
    if (filters.page_type) params.append('page_type', filters.page_type);  // ← ADD THIS
    if (filters.url_contains) params.append('url_contains', filters.url_contains);

    const response = await fetch(`/api/v3/pages?${params.toString()}`);
    const data = await response.json();
    setPages(data.pages);
  };

  return (
    <div className="pages-list">
      <div className="filters-section">
        {/* Your existing filters */}
        <PageTypeFilter
          value={filters.page_type}
          onChange={(value) => handleFilterChange('page_type', value)}
        />
      </div>
      
      {/* Pages table/list */}
      <div className="pages-content">
        {/* Your existing pages rendering logic */}
      </div>
    </div>
  );
};
```

### Step 4: Display Page Type in Table/List

Add the page type column to your pages display:

```typescript
// In your pages table component
<table className="pages-table">
  <thead>
    <tr>
      <th>URL</th>
      <th>Title</th>
      <th>Page Type</th>  {/* ← ADD THIS COLUMN */}
      <th>Curation Status</th>
      <th>Processing Status</th>
      <th>Actions</th>
    </tr>
  </thead>
  <tbody>
    {pages.map(page => (
      <tr key={page.id}>
        <td>{page.url}</td>
        <td>{page.title || 'No Title'}</td>
        <td>
          <span className={`page-type-badge page-type-${page.page_type}`}>
            {formatPageType(page.page_type)}
          </span>
        </td>
        <td>{page.curation_status}</td>
        <td>{page.processing_status}</td>
        <td>{/* Your action buttons */}</td>
      </tr>
    ))}
  </tbody>
</table>
```

### Step 5: Add Page Type Formatting Helper

Create a helper function to display user-friendly page type labels:

```typescript
// utils/pageTypeUtils.ts
export const formatPageType = (pageType: string | null): string => {
  if (!pageType) return 'Unknown';
  
  const typeMap: Record<string, string> = {
    'contact_root': 'Contact Page',
    'career_contact': 'Career Page', 
    'about_root': 'About Page',
    'services_root': 'Services Page',
    'menu_root': 'Menu Page',
    'pricing_root': 'Pricing Page',
    'team_root': 'Team Page',
    'legal_root': 'Legal Page',
    'wp_prospect': 'WordPress Prospect',
    'unknown': 'Uncategorized'
  };
  
  return typeMap[pageType] || pageType;
};

export const getPageTypeColor = (pageType: string | null): string => {
  if (!pageType) return 'gray';
  
  const colorMap: Record<string, string> = {
    'contact_root': 'green',
    'career_contact': 'blue',
    'about_root': 'purple',
    'services_root': 'orange',
    'menu_root': 'teal',
    'pricing_root': 'yellow',
    'team_root': 'pink',
    'legal_root': 'red',
    'wp_prospect': 'indigo',
    'unknown': 'gray'
  };
  
  return colorMap[pageType] || 'gray';
};
```

### Step 6: Update Bulk Operations

Update your "Select All" functionality to include page type filtering:

```typescript
// In your bulk operations component
const handleSelectAllFiltered = async () => {
  const requestBody: FilteredUpdateRequest = {
    status: 'Selected'
  };

  // Include active filters
  if (filters.page_curation_status) {
    requestBody.page_curation_status = filters.page_curation_status;
  }
  if (filters.page_processing_status) {
    requestBody.page_processing_status = filters.page_processing_status;
  }
  if (filters.page_type) {  // ← ADD THIS
    requestBody.page_type = filters.page_type;
  }
  if (filters.url_contains) {
    requestBody.url_contains = filters.url_contains;
  }

  const response = await fetch('/api/v3/pages/status/filtered', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody)
  });

  const result = await response.json();
  console.log(`Updated ${result.updated_count} pages, queued ${result.queued_count} for processing`);
};
```

### Step 7: Add CSS Styling

Add styles for the page type badges:

```css
/* styles/pages.css */
.page-type-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: capitalize;
}

.page-type-contact_root { background-color: #d1fae5; color: #065f46; }
.page-type-career_contact { background-color: #dbeafe; color: #1e40af; }
.page-type-about_root { background-color: #e9d5ff; color: #7c2d12; }
.page-type-services_root { background-color: #fed7aa; color: #9a3412; }
.page-type-menu_root { background-color: #ccfbf1; color: #134e4a; }
.page-type-pricing_root { background-color: #fef3c7; color: #92400e; }
.page-type-team_root { background-color: #fce7f3; color: #be185d; }
.page-type-legal_root { background-color: #fee2e2; color: #991b1b; }
.page-type-wp_prospect { background-color: #e0e7ff; color: #3730a3; }
.page-type-unknown { background-color: #f3f4f6; color: #374151; }

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: white;
  font-size: 14px;
}
```

---

## TESTING CHECKLIST

### Functional Testing
- [ ] Page type filter dropdown displays all options
- [ ] Filtering by page type returns correct results
- [ ] Page type values display correctly in the table
- [ ] "Select All" with page type filter works correctly
- [ ] Bulk operations respect page type filtering
- [ ] Page type badges have appropriate styling

### Integration Testing
- [ ] API calls include page_type parameter when filter is active
- [ ] Response parsing handles page_type field correctly
- [ ] Filter combinations work (e.g., page_type + curation_status)
- [ ] Clearing filters resets page_type to "All Page Types"

### User Experience Testing
- [ ] Page type labels are user-friendly (not raw enum values)
- [ ] Visual distinction between different page types
- [ ] Filter state persists during navigation
- [ ] Loading states work correctly with new filter

---

## EXAMPLE API RESPONSES

### GET /api/v3/pages?page_type=contact_root

```json
{
  "pages": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "url": "https://example.com/contact",
      "title": "Contact Us",
      "domain_id": "456e7890-e89b-12d3-a456-426614174001", 
      "curation_status": "New",
      "processing_status": null,
      "page_type": "contact_root",
      "updated_at": "2025-09-12T14:30:00Z",
      "created_at": "2025-09-12T10:15:00Z",
      "error": null
    }
  ],
  "total": 1,
  "offset": 0,
  "limit": 100,
  "filters_applied": {
    "page_curation_status": null,
    "page_processing_status": null,
    "page_type": "contact_root",
    "url_contains": null
  }
}
```

### POST /api/v3/pages/status/filtered

```json
{
  "status": "Selected",
  "page_type": "contact_root",
  "page_curation_status": "New"
}
```

**Response:**
```json
{
  "updated_count": 15,
  "queued_count": 15
}
```

---

## TROUBLESHOOTING

### Common Issues

1. **Page type not displaying**: Check that your TypeScript interface includes the `page_type` field
2. **Filter not working**: Ensure the API call includes the `page_type` parameter
3. **Bulk operations failing**: Verify the request body includes `page_type` when the filter is active
4. **Styling issues**: Confirm CSS classes match the actual enum values from the backend

### Debug Steps

1. Check browser network tab to verify API calls include `page_type` parameter
2. Log the API response to confirm `page_type` field is present
3. Verify filter state management includes the new `page_type` field
4. Test with different page type values to ensure all categories work

---

## DEPLOYMENT NOTES

- **Backend Status**: ✅ Deployed and Live
- **Breaking Changes**: None (additive changes only)
- **Backward Compatibility**: Full compatibility maintained
- **Database**: No migration required
- **API Version**: v3 (existing endpoints enhanced)

The backend changes are live and ready for frontend integration. The new `page_type` field will enable users to efficiently filter and categorize pages based on Honeybee's AI categorization results.
