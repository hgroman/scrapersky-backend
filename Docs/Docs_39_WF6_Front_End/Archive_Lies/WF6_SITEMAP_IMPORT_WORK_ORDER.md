# WF6 SITEMAP IMPORT TAB - COMPREHENSIVE WORK ORDER

**Date**: August 24, 2025  
**Tab Position**: 6th tab (between Export Center and Smart Alerts)  
**Component Name**: Sitemap Import (WF6 - The Recorder)  
**Status**: READY FOR IMPLEMENTATION

---

## EXISTING TABS ANALYSIS COMPLETE

### Established Patterns from Tabs 1-5
1. **Tab 1 (Discovery Scan)**: Single search form with real-time status polling
2. **Tab 2 (Staging Editor)**: CRUD table with batch operations, checkboxes, status dropdowns
3. **Tab 3 (Local Business Curation)**: Advanced filtering + batch CRUD operations
4. **Tab 4 (Performance Insights)**: Analytics display (placeholder)
5. **Tab 5 (Export Center)**: Data export functionality (placeholder)

### Common CRUD Pattern Identified
- **Table-based interface** with checkboxes for multi-select
- **Batch operations panel** with status dropdown and update buttons
- **Filter controls** for data refinement
- **Pagination** for large datasets
- **Real-time status updates** with polling
- **Consistent authentication** using session tokens

---

## WF6 API ENDPOINTS SPECIFICATION

### Primary Endpoint
```
GET /api/v3/sitemap-files/
```
**Parameters:**
- `domain_id` (optional UUID)
- `deep_scrape_curation_status` (optional: New|Selected|Maybe|Not a Fit|Archived)
- `url_contains` (optional string)
- `sitemap_type` (optional string)
- `discovery_method` (optional string)
- `page` (optional integer, default: 1)
- `size` (optional integer, default: 15, max: 200)
- `tenant_id` (required UUID)

### Batch Update Endpoint
```
PUT /api/v3/sitemap-files/sitemap_import_curation/status
```
**Request Body:**
```json
{
  "sitemap_file_ids": ["uuid1", "uuid2", "uuid3"],
  "deep_scrape_curation_status": "Selected",
  "tenant_id": "tenant-uuid"
}
```
**Response:**
```json
{
  "updated_count": 3,
  "queued_count": 3
}
```

### Authentication
- **Headers**: `Authorization: Bearer ${session.access_token}`
- **Content-Type**: `application/json`

---

## DATA STRUCTURE SPECIFICATION

### SitemapFile Interface
```typescript
interface SitemapFile {
  id: string;                           // UUID
  url: string;                          // Sitemap URL
  domain_id?: string;                   // Associated domain UUID
  deep_scrape_curation_status: string;  // New|Selected|Maybe|Not a Fit|Archived
  sitemap_import_status?: string;       // Queued|Processing|Complete|Failed
  sitemap_type?: string;                // Type classification
  discovery_method?: string;            // How it was discovered
  created_at: string;                   // ISO timestamp
  updated_at: string;                   // ISO timestamp
  domain?: {                            // Optional domain details
    domain_name: string;
    id: string;
  };
}

interface SitemapResponse {
  items: SitemapFile[];
  page: number;
  pages: number;
  total: number;
}

interface Filters {
  deep_scrape_curation_status: string;
  url_contains: string;
  domain_id: string;
  sitemap_type: string;
  discovery_method: string;
}
```

---

## COMPONENT ARCHITECTURE

### File Structure
```
src/components/staging/SitemapImport.tsx    # Main component
src/types/sitemap.ts                        # TypeScript interfaces
```

### Component Hierarchy
```
SitemapImport
├── Filter Controls Card
│   ├── Status Dropdown (deep_scrape_curation_status)
│   ├── URL Search Input
│   ├── Domain Dropdown
│   ├── Sitemap Type Dropdown
│   ├── Discovery Method Dropdown
│   └── Apply/Reset Buttons
├── Status Info Banner
├── Batch Update Panel (when items selected)
│   ├── Status Dropdown
│   ├── Update Button
│   └── Clear Selection Button
├── Data Table
│   ├── Select All Checkbox
│   ├── Individual Row Checkboxes
│   ├── URL Column (with external link)
│   ├── Domain Column
│   ├── Curation Status Column (with badges)
│   ├── Import Status Column (with badges)
│   └── Updated At Column
└── Pagination Controls
```

---

## IMPLEMENTATION REQUIREMENTS

### 1. Type System Updates
**File**: `src/types/rbac.ts`
```typescript
export type ServiceTab =
  | 'discovery-scan'
  | 'review-organize'
  | 'performance-insights'
  | 'deep-analysis'
  | 'export-center'
  | 'sitemap-import'        // ADD THIS LINE
  | 'smart-alerts'
  | 'control-center';
```

### 2. ServiceTabs Component Update
**File**: `src/components/services/ServiceTabs.tsx`
```typescript
// Insert at position 5 (between export-center and smart-alerts)
const tabs: { id: ServiceTab; label: string; icon: React.ReactNode }[] = [
  { id: "discovery-scan", label: "Discovery Scan", icon: <Search className="w-4 h-4" /> },
  { id: "review-organize", label: "Review & Organize", icon: <LayoutGrid className="w-4 h-4" /> },
  { id: "performance-insights", label: "Performance Insights", icon: <Activity className="w-4 h-4" /> },
  { id: "deep-analysis", label: "Deep Analysis", icon: <LineChart className="w-4 h-4" /> },
  { id: "export-center", label: "Export Center", icon: <Download className="w-4 h-4" /> },
  { id: "sitemap-import", label: "Sitemap Import", icon: <FileSearch className="w-4 h-4" /> }, // NEW
  { id: "smart-alerts", label: "Smart Alerts", icon: <Bell className="w-4 h-4" /> },
  { id: "control-center", label: "Control Center", icon: <Settings className="w-4 h-4" /> }
];
```

### 3. LocalMiner Route Addition
**File**: `src/pages/LocalMiner.tsx`
```typescript
// Insert between export-center and smart-alerts routes
<Route 
  path="sitemap-import" 
  element={
    <ProtectedRoute requiredFeature="localminer" requiredTab="sitemap-import">
      <ServiceTabs service="localminer" defaultTab="sitemap-import">
        <SitemapImport />
      </ServiceTabs>
    </ProtectedRoute>
  } 
/>
```

---

## UI/UX SPECIFICATIONS

### Filter Controls
- **5 filter fields** in responsive grid layout
- **Status dropdown**: New, Selected, Maybe, Not a Fit, Archived
- **URL search**: Text input with placeholder "Search sitemap URLs..."
- **Domain dropdown**: Populated from available domains
- **Type/Method dropdowns**: Based on available values
- **Apply/Reset buttons**: Standard button styling

### Data Table Columns
1. **Checkbox** (12px width)
2. **Sitemap URL** (with external link icon)
3. **Domain** (domain name or "N/A")
4. **Curation Status** (colored badges)
5. **Import Status** (colored badges with processing indicators)
6. **Updated** (formatted timestamp)

### Status Badge Colors
```typescript
const getStatusVariant = (status: string) => {
  switch (status?.toLowerCase()) {
    case 'new': return 'secondary';
    case 'selected': return 'default';
    case 'maybe': return 'outline';
    case 'not a fit': return 'destructive';
    case 'archived': return 'destructive';
    case 'queued': return 'warning';
    case 'processing': return 'warning';
    case 'complete': return 'default';
    case 'failed': return 'destructive';
    default: return 'secondary';
  }
};
```

### Real-time Updates
- **Polling interval**: 5 seconds for import status updates
- **Auto-refresh**: When items are in "Queued" or "Processing" state
- **Toast notifications**: Success/error feedback for batch operations

---

## FUNCTIONAL REQUIREMENTS

### Core Operations
1. **List Sitemap Files**: Paginated table with filtering
2. **Multi-select**: Checkboxes for individual and bulk selection
3. **Batch Status Update**: Update multiple records simultaneously
4. **Real-time Monitoring**: Auto-refresh processing status
5. **Filter & Search**: Multiple filter criteria support

### Batch Update Flow
1. User selects multiple sitemap files via checkboxes
2. Batch update panel appears with status dropdown
3. User selects target status (Selected/Not a Fit/etc.)
4. System calls PUT endpoint with selected IDs
5. Backend auto-queues "Selected" items for WF6 processing
6. UI refreshes data and shows success message
7. Real-time polling monitors processing progress

### Error Handling
- **Authentication errors**: Redirect to login
- **API failures**: Toast error messages
- **Network issues**: Retry mechanisms
- **Validation errors**: Form field highlighting

---

## TECHNICAL SPECIFICATIONS

### API Integration
- **Base URL**: `https://scrapersky-backend.onrender.com`
- **Authentication**: JWT Bearer token from session
- **Tenant ID**: From `session.user.user_metadata.tenant_id`
- **Error handling**: Consistent with existing tabs
- **Polling**: 5-second intervals for status updates

### State Management
```typescript
const [data, setData] = useState<SitemapResponse | null>(null);
const [loading, setLoading] = useState(false);
const [currentPage, setCurrentPage] = useState(1);
const [selectedIds, setSelectedIds] = useState<string[]>([]);
const [batchStatus, setBatchStatus] = useState<string>('');
const [updating, setUpdating] = useState(false);
const [filters, setFilters] = useState<Filters>({...});
const [appliedFilters, setAppliedFilters] = useState<Filters>({...});
const [polling, setPolling] = useState(false);
```

### Performance Considerations
- **Pagination**: 15 items per page (matching existing tabs)
- **Debounced search**: 300ms delay for URL search
- **Optimistic updates**: Immediate UI feedback
- **Memory cleanup**: Clear intervals on unmount

---

## TESTING REQUIREMENTS

### Manual Testing Checklist
- [ ] Filter by each status type
- [ ] Search by URL contains
- [ ] Select individual items
- [ ] Select all items on page
- [ ] Batch update to "Selected" status
- [ ] Batch update to "Not a Fit" status
- [ ] Verify real-time status updates
- [ ] Test pagination navigation
- [ ] Verify external URL links
- [ ] Test authentication handling

### API Testing
- [ ] GET endpoint with all filter combinations
- [ ] PUT endpoint with valid sitemap IDs
- [ ] Error handling for invalid requests
- [ ] Tenant isolation verification
- [ ] Rate limiting compliance

---

## DEPLOYMENT CHECKLIST

### Pre-deployment
- [ ] Type definitions updated
- [ ] ServiceTabs component updated
- [ ] LocalMiner routes added
- [ ] SitemapImport component created
- [ ] Icons imported (FileSearch)
- [ ] Error boundaries implemented

### Post-deployment
- [ ] Tab navigation functional
- [ ] API endpoints responding
- [ ] Real-time updates working
- [ ] Batch operations functional
- [ ] UI matches design patterns
- [ ] Performance acceptable

---

## SUCCESS CRITERIA

1. **Tab Integration**: New tab appears in correct position (6th)
2. **Data Loading**: Sitemap files load with pagination
3. **Filtering**: All filter controls function correctly
4. **Batch Operations**: Multi-select and status updates work
5. **Real-time Updates**: Processing status updates automatically
6. **UI Consistency**: Matches existing tab styling and behavior
7. **Performance**: Loads within 2 seconds, smooth interactions
8. **Error Handling**: Graceful failure states and user feedback

---

## APPENDIX: BACKEND CLARIFICATION QUESTIONS

### API Endpoint Questions
1. **Domain Dropdown Population**: What endpoint should we use to populate the domain dropdown filter? Is there a `/api/v3/domains/` endpoint that returns domain options?

2. **Sitemap Type Values**: What are the possible values for `sitemap_type`? Should we hardcode options or fetch them dynamically?

3. **Discovery Method Values**: What are the possible values for `discovery_method`? Should we hardcode options or fetch them dynamically?

4. **Response Field Confirmation**: Does the GET `/api/v3/sitemap-files/` response include the nested `domain` object with `domain_name` and `id` fields as specified in our interface?

5. **Status Transition Rules**: Are there any business rules about which status transitions are allowed? (e.g., can "Archived" items be moved back to "Selected"?)

6. **Polling Optimization**: Should we only poll for status updates when there are items in "Queued" or "Processing" state, or should we always poll?

### Data Validation Questions
7. **Required Fields**: Which fields in the SitemapFile interface are guaranteed to be present vs optional?

8. **URL Validation**: Should we validate sitemap URLs on the frontend before display, or trust the backend data?

9. **Tenant Isolation**: Is the `tenant_id` parameter sufficient for data isolation, or are there additional security considerations?

### Performance Questions
10. **Pagination Limits**: Is the 200 max page size a hard limit, or can it be increased for admin users?

11. **Filter Performance**: Are there any performance considerations for the `url_contains` filter on large datasets?

12. **Batch Update Limits**: Is there a maximum number of sitemap files that can be updated in a single batch operation?

### Integration Questions
13. **WF6 Service Integration**: After marking items as "Selected", how long does it typically take for the WF6 service to process them? This affects our polling frequency.

14. **Error Handling**: What specific error codes/messages should we expect from the batch update endpoint for different failure scenarios?

15. **Real-time Events**: Are there any WebSocket or Server-Sent Events available for real-time status updates, or should we stick with polling?
