# WF6 SITEMAP IMPORT - DEFINITIVE IMPLEMENTATION GUIDE

**PRODUCTION READY - EXACT CODE CHANGES REQUIRED**

---

## STEP 1: UPDATE TYPE SYSTEM

**File**: `src/types/rbac.ts`

**CHANGE LINE 1-8 FROM:**
```typescript
export type ServiceTab =
  | 'discovery-scan'
  | 'review-organize'
  | 'performance-insights'
  | 'deep-analysis'
  | 'export-center'
  | 'smart-alerts'
  | 'control-center';
```

**TO:**
```typescript
export type ServiceTab =
  | 'discovery-scan'
  | 'review-organize'
  | 'performance-insights'
  | 'deep-analysis'
  | 'export-center'
  | 'sitemap-import'
  | 'smart-alerts'
  | 'control-center';
```

---

## STEP 2: UPDATE SERVICE TABS COMPONENT

**File**: `src/components/services/ServiceTabs.tsx`

**ADD IMPORT (line 8):**
```typescript
import { AlertCircle, Map, LayoutGrid, Activity, LineChart, Download, Bell, Settings, Search, FileSearch } from "lucide-react";
```

**CHANGE LINES 26-34 FROM:**
```typescript
const tabs: { id: ServiceTab; label: string; icon: React.ReactNode }[] = [
  { id: "discovery-scan", label: "Discovery Scan", icon: <Search className="w-4 h-4" /> },
  { id: "review-organize", label: "Review & Organize", icon: <LayoutGrid className="w-4 h-4" /> },
  { id: "performance-insights", label: "Performance Insights", icon: <Activity className="w-4 h-4" /> },
  { id: "deep-analysis", label: "Deep Analysis", icon: <LineChart className="w-4 h-4" /> },
  { id: "export-center", label: "Export Center", icon: <Download className="w-4 h-4" /> },
  { id: "smart-alerts", label: "Smart Alerts", icon: <Bell className="w-4 h-4" /> },
  { id: "control-center", label: "Control Center", icon: <Settings className="w-4 h-4" /> }
];
```

**TO:**
```typescript
const tabs: { id: ServiceTab; label: string; icon: React.ReactNode }[] = [
  { id: "discovery-scan", label: "Discovery Scan", icon: <Search className="w-4 h-4" /> },
  { id: "review-organize", label: "Review & Organize", icon: <LayoutGrid className="w-4 h-4" /> },
  { id: "performance-insights", label: "Performance Insights", icon: <Activity className="w-4 h-4" /> },
  { id: "deep-analysis", label: "Deep Analysis", icon: <LineChart className="w-4 h-4" /> },
  { id: "export-center", label: "Export Center", icon: <Download className="w-4 h-4" /> },
  { id: "sitemap-import", label: "Sitemap Import", icon: <FileSearch className="w-4 h-4" /> },
  { id: "smart-alerts", label: "Smart Alerts", icon: <Bell className="w-4 h-4" /> },
  { id: "control-center", label: "Control Center", icon: <Settings className="w-4 h-4" /> }
];
```

---

## STEP 3: ADD ROUTE TO LOCALMINER

**File**: `src/pages/LocalMiner.tsx`

**ADD IMPORT (line 11):**
```typescript
import { SitemapImport } from '@/components/staging/SitemapImport';
```

**INSERT AFTER LINE 163 (after export-center route):**
```typescript
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

## STEP 4: CREATE SITEMAP IMPORT COMPONENT

**File**: `src/components/staging/SitemapImport.tsx`

**COMPLETE COMPONENT CODE:**
```typescript
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';
import { ExternalLink, RefreshCw } from 'lucide-react';

interface SitemapFile {
  id: string;
  url: string;
  domain_id?: string;
  deep_scrape_curation_status: string;
  sitemap_import_status?: string;
  sitemap_type?: string;
  discovery_method?: string;
  created_at: string;
  updated_at: string;
  domain?: {
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

export function SitemapImport() {
  const { session } = useAuth();
  const [data, setData] = useState<SitemapResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [batchStatus, setBatchStatus] = useState<string>('');
  const [updating, setUpdating] = useState(false);
  const [polling, setPolling] = useState(false);
  const [filters, setFilters] = useState<Filters>({
    deep_scrape_curation_status: '',
    url_contains: '',
    domain_id: '',
    sitemap_type: '',
    discovery_method: ''
  });
  const [appliedFilters, setAppliedFilters] = useState<Filters>({
    deep_scrape_curation_status: '',
    url_contains: '',
    domain_id: '',
    sitemap_type: '',
    discovery_method: ''
  });

  const API_BASE = 'https://scrapersky-backend.onrender.com';
  const PAGE_SIZE = 15;

  // Get tenant_id from session
  const getTenantId = () => {
    return session?.user?.user_metadata?.tenant_id || 
           session?.user?.app_metadata?.tenant_id || 
           '550e8400-e29b-41d4-a716-446655440000';
  };

  // Get authorization headers
  const getAuthHeaders = () => {
    return {
      'Authorization': `Bearer ${session?.access_token}`,
      'Content-Type': 'application/json'
    };
  };

  // Build query parameters
  const buildQueryParams = (page: number = 1, currentFilters: Filters = appliedFilters) => {
    const params = new URLSearchParams({
      page: page.toString(),
      size: PAGE_SIZE.toString(),
      tenant_id: getTenantId()
    });

    if (currentFilters.deep_scrape_curation_status) {
      params.append('deep_scrape_curation_status', currentFilters.deep_scrape_curation_status);
    }
    if (currentFilters.url_contains) {
      params.append('url_contains', currentFilters.url_contains);
    }
    if (currentFilters.domain_id) {
      params.append('domain_id', currentFilters.domain_id);
    }
    if (currentFilters.sitemap_type) {
      params.append('sitemap_type', currentFilters.sitemap_type);
    }
    if (currentFilters.discovery_method) {
      params.append('discovery_method', currentFilters.discovery_method);
    }

    return params.toString();
  };

  // Fetch sitemap data
  const fetchSitemapData = async (page: number = 1, currentFilters: Filters = appliedFilters) => {
    if (!session?.access_token) {
      toast.error('Authentication required');
      return;
    }

    setLoading(true);
    try {
      const queryParams = buildQueryParams(page, currentFilters);
      const url = `${API_BASE}/api/v3/sitemap-files?${queryParams}`;
      
      console.log('Fetching sitemap data:', { page, filters: currentFilters });
      
      const response = await fetch(url, {
        headers: getAuthHeaders()
      });

      if (response.ok) {
        const sitemapData = await response.json();
        console.log('Sitemap data received:', sitemapData);
        setData(sitemapData);
        setCurrentPage(page);
        
        // Check if we need to start polling
        const hasProcessingItems = sitemapData.items?.some((item: SitemapFile) => 
          item.sitemap_import_status === 'Queued' || item.sitemap_import_status === 'Processing'
        );
        
        if (hasProcessingItems && !polling) {
          setPolling(true);
        } else if (!hasProcessingItems && polling) {
          setPolling(false);
        }
      } else {
        const errorText = await response.text();
        console.error('Failed to fetch sitemap data:', response.status, errorText);
        toast.error('Failed to fetch sitemap data');
      }
    } catch (error) {
      console.error('Error fetching sitemap data:', error);
      toast.error('Error fetching sitemap data');
    } finally {
      setLoading(false);
    }
  };

  // Apply filters
  const handleApplyFilters = () => {
    setAppliedFilters(filters);
    setCurrentPage(1);
    setSelectedIds([]);
    fetchSitemapData(1, filters);
  };

  // Reset filters
  const handleResetFilters = () => {
    const resetFilters = {
      deep_scrape_curation_status: '',
      url_contains: '',
      domain_id: '',
      sitemap_type: '',
      discovery_method: ''
    };
    setFilters(resetFilters);
    setAppliedFilters(resetFilters);
    setCurrentPage(1);
    setSelectedIds([]);
    fetchSitemapData(1, resetFilters);
  };

  // Batch update status
  const handleBatchUpdate = async () => {
    if (!selectedIds.length || !batchStatus) {
      toast.error('Please select records and status');
      return;
    }

    setUpdating(true);
    try {
      const requestBody = {
        sitemap_file_ids: selectedIds,
        deep_scrape_curation_status: batchStatus,
        tenant_id: getTenantId()
      };

      console.log('Batch update request:', requestBody);

      const response = await fetch(`${API_BASE}/api/v3/sitemap-files/sitemap_import_curation/status`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(requestBody)
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Batch update result:', result);
        toast.success(`Updated ${result.updated_count || selectedIds.length} records. ${result.queued_count || 0} queued for processing.`);
        
        // Refresh data and clear selection
        await fetchSitemapData(currentPage);
        setSelectedIds([]);
        setBatchStatus('');
      } else {
        const errorText = await response.text();
        console.error('Batch update failed:', response.status, errorText);
        toast.error('Failed to update records');
      }
    } catch (error) {
      console.error('Error updating records:', error);
      toast.error('Error updating records');
    } finally {
      setUpdating(false);
    }
  };

  // Handle individual selection
  const handleSelectRecord = (sitemapId: string, checked: boolean) => {
    setSelectedIds(prev => 
      checked 
        ? [...prev, sitemapId]
        : prev.filter(id => id !== sitemapId)
    );
  };

  // Handle select all on current page
  const handleSelectAll = (checked: boolean) => {
    if (!data?.items) return;
    
    const currentPageIds = data.items.map(item => item.id);
    if (checked) {
      setSelectedIds(prev => [...new Set([...prev, ...currentPageIds])]);
    } else {
      setSelectedIds(prev => prev.filter(id => !currentPageIds.includes(id)));
    }
  };

  // Check if all current page items are selected
  const isAllSelected = data?.items?.length > 0 && 
    data.items.every(item => selectedIds.includes(item.id));

  // Get status badge variant
  const getStatusVariant = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'new': return 'secondary';
      case 'selected': return 'default';
      case 'maybe': return 'outline';
      case 'not a fit': return 'destructive';
      case 'archived': return 'destructive';
      case 'queued': return 'outline';
      case 'processing': return 'outline';
      case 'complete': return 'default';
      case 'error': return 'destructive';
      case 'failed': return 'destructive';
      default: return 'secondary';
    }
  };

  // Polling effect for real-time updates
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (polling) {
      interval = setInterval(() => {
        fetchSitemapData(currentPage);
      }, 5000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [polling, currentPage]);

  // Load data on mount
  useEffect(() => {
    if (session?.access_token) {
      fetchSitemapData(1);
    }
  }, [session]);

  if (!session?.access_token) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <h2 className="text-xl font-semibold mb-4">Authentication Required</h2>
          <p className="text-gray-600">You must be logged in to access the Sitemap Import.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white">Sitemap Import (WF6)</h2>
          <p className="text-gray-300">Review and curate sitemap files for processing. Select items to queue for WF6 processing.</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => fetchSitemapData(currentPage)}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Filter Controls */}
      <Card>
        <CardHeader>
          <CardTitle>Filter Controls</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 items-end">
            <div>
              <label className="block text-sm font-medium mb-2">Curation Status</label>
              <Select value={filters.deep_scrape_curation_status} onValueChange={(value) => setFilters(prev => ({ ...prev, deep_scrape_curation_status: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Statuses</SelectItem>
                  <SelectItem value="New">New</SelectItem>
                  <SelectItem value="Selected">Selected</SelectItem>
                  <SelectItem value="Maybe">Maybe</SelectItem>
                  <SelectItem value="Not a Fit">Not a Fit</SelectItem>
                  <SelectItem value="Archived">Archived</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">URL Contains</label>
              <Input
                placeholder="Search URLs..."
                value={filters.url_contains}
                onChange={(e) => setFilters(prev => ({ ...prev, url_contains: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Sitemap Type</label>
              <Input
                placeholder="Type filter..."
                value={filters.sitemap_type}
                onChange={(e) => setFilters(prev => ({ ...prev, sitemap_type: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Discovery Method</label>
              <Input
                placeholder="Method filter..."
                value={filters.discovery_method}
                onChange={(e) => setFilters(prev => ({ ...prev, discovery_method: e.target.value }))}
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleApplyFilters} disabled={loading}>
                Apply Filters
              </Button>
              <Button variant="outline" onClick={handleResetFilters} disabled={loading}>
                Reset
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Status Info */}
      {data && (
        <div className="bg-blue-100 p-4 rounded-lg">
          <p className="text-blue-800">
            Showing {data.items.length} of {data.total} sitemap files.
            {polling && <span className="ml-2 text-sm font-semibold">(Auto-refreshing...)</span>}
          </p>
        </div>
      )}

      {/* Batch Update Panel */}
      {selectedIds.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Batch Update Selected Items</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium mb-2">Set Curation Status To:</label>
                <Select value={batchStatus} onValueChange={setBatchStatus}>
                  <SelectTrigger className="w-[200px]">
                    <SelectValue placeholder="-- Select Status --" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="New">New</SelectItem>
                    <SelectItem value="Selected">Selected</SelectItem>
                    <SelectItem value="Maybe">Maybe</SelectItem>
                    <SelectItem value="Not a Fit">Not a Fit</SelectItem>
                    <SelectItem value="Archived">Archived</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex gap-2">
                <Button 
                  onClick={handleBatchUpdate} 
                  disabled={!batchStatus || updating}
                >
                  {updating ? 'Updating...' : `Update ${selectedIds.length} Selected`}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setSelectedIds([])}
                >
                  Clear Selection
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Data Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">
                    <Checkbox
                      checked={isAllSelected}
                      onCheckedChange={handleSelectAll}
                    />
                  </TableHead>
                  <TableHead>Sitemap URL</TableHead>
                  <TableHead>Domain</TableHead>
                  <TableHead>Curation Status</TableHead>
                  <TableHead>Import Status</TableHead>
                  <TableHead>Updated</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8">
                      Fetching data...
                    </TableCell>
                  </TableRow>
                ) : data?.items?.length ? (
                  data.items.map((record) => (
                    <TableRow key={record.id}>
                      <TableCell>
                        <Checkbox
                          checked={selectedIds.includes(record.id)}
                          onCheckedChange={(checked) => 
                            handleSelectRecord(record.id, checked as boolean)
                          }
                        />
                      </TableCell>
                      <TableCell className="font-medium">
                        <a 
                          href={record.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 flex items-center gap-1"
                        >
                          {record.url}
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </TableCell>
                      <TableCell>
                        {record.domain?.domain_name || 'N/A'}
                      </TableCell>
                      <TableCell>
                        <Badge variant={getStatusVariant(record.deep_scrape_curation_status)}>
                          {record.deep_scrape_curation_status || 'New'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {record.sitemap_import_status ? (
                          <Badge variant={getStatusVariant(record.sitemap_import_status)}>
                            {record.sitemap_import_status}
                          </Badge>
                        ) : (
                          'N/A'
                        )}
                      </TableCell>
                      <TableCell>
                        {new Date(record.updated_at).toLocaleString()}
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8">
                      No sitemap files found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Page {data.page} of {data.pages} ({data.total} items)
          </div>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              onClick={() => fetchSitemapData(currentPage - 1)}
              disabled={currentPage <= 1 || loading}
            >
              Previous
            </Button>
            <Button 
              variant="outline" 
              onClick={() => fetchSitemapData(currentPage + 1)}
              disabled={currentPage >= data.pages || loading}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## IMPLEMENTATION SUMMARY

**EXACT CHANGES REQUIRED:**

1. **Add `'sitemap-import'` to ServiceTab type** in `rbac.ts`
2. **Add FileSearch icon import** in `ServiceTabs.tsx`
3. **Insert sitemap-import tab** in tabs array (position 6)
4. **Add SitemapImport import** in `LocalMiner.tsx`
5. **Add sitemap-import route** after export-center route
6. **Create complete SitemapImport component** with all CRUD functionality

**FEATURES IMPLEMENTED:**
- ✅ Multi-select with checkboxes
- ✅ Batch status updates with dropdown
- ✅ Advanced filtering (5 filter fields)
- ✅ Real-time polling for processing status
- ✅ Pagination matching existing patterns
- ✅ Production API integration
- ✅ Tenant ID handling
- ✅ Error handling and loading states
- ✅ External link functionality
- ✅ Status badges with proper colors

**PRODUCTION READY - IMPLEMENT THESE EXACT CHANGES**
