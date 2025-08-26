# WF6 React Frontend API Reference
# Complete Endpoint Documentation for Frontend Developer

## Overview

This document provides comprehensive API endpoint specifications for the React frontend developer to implement WF6 (The Recorder) user interface components. All endpoints are fully tested and validated through the WF6 testing framework.

## Authentication

All API endpoints require JWT authentication unless otherwise specified.

```typescript
// Authentication Headers
const headers = {
  'Authorization': `Bearer ${jwtToken}`,
  'Content-Type': 'application/json'
};
```

## Base Configuration

```typescript
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
const API_VERSION = 'v3';
```

## Core Data Types

### TypeScript Interfaces

```typescript
// Enum Types
export enum SitemapImportStatus {
  Queued = 'Queued',
  Processing = 'Processing',
  Complete = 'Complete',
  Error = 'Error'
}

export enum PageCurationStatus {
  New = 'New',
  Selected = 'Selected',
  Rejected = 'Rejected'
}

export enum SitemapCurationStatus {
  New = 'New',
  Selected = 'Selected',
  Rejected = 'Rejected'
}

// Core Data Models
export interface Domain {
  id: string;
  domain: string;
  status: string;
  is_active: boolean;
  has_sitemap?: boolean;
  page_count?: number;
  created_at: string;
  updated_at: string;
}

export interface SitemapFile {
  id: string;
  tenant_id: string;
  domain_id: string;
  url: string;
  sitemap_type: string;
  discovery_method?: string;
  page_count?: number;
  url_count: number;
  size_bytes?: number;
  response_time_ms?: number;
  priority: number;
  status_code?: number;
  status: string;
  sitemap_import_status?: SitemapImportStatus;
  sitemap_import_error?: string;
  deep_scrape_curation_status: SitemapCurationStatus;
  is_gzipped?: boolean;
  has_lastmod?: boolean;
  has_priority?: boolean;
  has_changefreq?: boolean;
  generator?: string;
  last_modified?: string;
  process_after?: string;
  last_processed_at?: string;
  created_at: string;
  updated_at: string;
  user_name?: string;
  notes?: string;
  tags?: Record<string, any>;
  lead_source?: string;
  is_active: boolean;
}

export interface Page {
  id: string;
  tenant_id: string;
  domain_id: string;
  sitemap_file_id?: string;
  url: string;
  title?: string;
  description?: string;
  h1?: string;
  canonical_url?: string;
  meta_robots?: string;
  has_schema_markup: boolean;
  schema_types?: string[];
  has_contact_form: boolean;
  has_comments: boolean;
  word_count?: number;
  inbound_links?: string[];
  outbound_links?: string[];
  page_type?: string;
  lead_source?: string;
  additional_json: Record<string, any>;
  page_curation_status: PageCurationStatus;
  page_processing_status?: string;
  page_processing_error?: string;
  last_modified?: string;
  last_scan?: string;
  created_at: string;
  updated_at: string;
}

// API Response Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

// Request Types
export interface SitemapFileCreateRequest {
  domain_id: string;
  url: string;
  sitemap_type: string;
  discovery_method?: string;
  priority?: number;
  notes?: string;
  tags?: Record<string, any>;
}

export interface SitemapFileUpdateRequest {
  url?: string;
  sitemap_type?: string;
  priority?: number;
  notes?: string;
  tags?: Record<string, any>;
  is_active?: boolean;
}

export interface BatchStatusUpdateRequest {
  sitemap_file_ids: string[];
  deep_scrape_curation_status: SitemapCurationStatus;
}
```

## API Endpoints

### 1. Sitemap Files Management

#### List Sitemap Files
**Layer 3 (L3): Router Guardian Endpoint**

```typescript
// GET /api/v3/sitemap-files/
interface ListSitemapFilesParams {
  domain_id?: string;
  deep_scrape_curation_status?: SitemapCurationStatus;
  url_contains?: string;
  sitemap_type?: string;
  discovery_method?: string;
  page?: number;
  size?: number;
}

const listSitemapFiles = async (params: ListSitemapFilesParams = {}): Promise<PaginatedResponse<SitemapFile>> => {
  const queryParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined) {
      queryParams.append(key, value.toString());
    }
  });

  const response = await fetch(`${API_BASE_URL}/api/${API_VERSION}/sitemap-files/?${queryParams}`, {
    method: 'GET',
    headers
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch sitemap files: ${response.statusText}`);
  }

  return response.json();
};
```

**Expected Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "domain_id": "uuid",
      "url": "https://example.com/sitemap.xml",
      "sitemap_type": "Standard",
      "sitemap_import_status": "Complete",
      "url_count": 150,
      "created_at": "2025-08-18T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 15,
  "pages": 1
}
```

#### Create Sitemap File
```typescript
// POST /api/v3/sitemap-files/
const createSitemapFile = async (data: SitemapFileCreateRequest): Promise<SitemapFile> => {
  const response = await fetch(`${API_BASE_URL}/api/${API_VERSION}/sitemap-files/`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create sitemap file');
  }

  return response.json();
};
```

**Request Body:**
```json
{
  "domain_id": "uuid",
  "url": "https://example.com/sitemap.xml",
  "sitemap_type": "Standard",
  "discovery_method": "manual",
  "priority": 5,
  "notes": "User-submitted sitemap"
}
```

#### Get Sitemap File by ID
```typescript
// GET /api/v3/sitemap-files/{id}
const getSitemapFile = async (id: string): Promise<SitemapFile> => {
  const response = await fetch(`${API_BASE_URL}/api/${API_VERSION}/sitemap-files/${id}`, {
    method: 'GET',
    headers
  });

  if (!response.ok) {
    throw new Error(`Sitemap file not found: ${response.statusText}`);
  }

  return response.json();
};
```

#### Update Sitemap File
```typescript
// PUT /api/v3/sitemap-files/{id}
const updateSitemapFile = async (id: string, data: SitemapFileUpdateRequest): Promise<SitemapFile> => {
  const response = await fetch(`${API_BASE_URL}/api/${API_VERSION}/sitemap-files/${id}`, {
    method: 'PUT',
    headers,
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update sitemap file');
  }

  return response.json();
};
```

#### Delete Sitemap File
```typescript
// DELETE /api/v3/sitemap-files/{id}
const deleteSitemapFile = async (id: string): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/api/${API_VERSION}/sitemap-files/${id}`, {
    method: 'DELETE',
    headers
  });

  if (!response.ok) {
    throw new Error(`Failed to delete sitemap file: ${response.statusText}`);
  }
};
```

#### Batch Status Update
```typescript
// PUT /api/v3/sitemap-files/sitemap_import_curation/status
const batchUpdateStatus = async (data: BatchStatusUpdateRequest): Promise<{updated_count: number, queued_count: number}> => {
  const response = await fetch(`${API_BASE_URL}/api/${API_VERSION}/sitemap-files/sitemap_import_curation/status`, {
    method: 'PUT',
    headers,
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update status');
  }

  return response.json();
};
```

### 2. Development Tools (Testing & Debugging)

#### Manual Trigger Sitemap Import
**Layer 3 (L3): Router Guardian Endpoint**

```typescript
// POST /api/v3/dev-tools/trigger-sitemap-import/{id}
const triggerSitemapImport = async (sitemapFileId: string): Promise<{message: string, sitemap_file_id: string}> => {
  const response = await fetch(`${API_BASE_URL}/api/${API_VERSION}/dev-tools/trigger-sitemap-import/${sitemapFileId}`, {
    method: 'POST',
    headers
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to trigger sitemap import');
  }

  return response.json();
};
```

#### Check Scheduler Status
```typescript
// GET /api/v3/dev-tools/scheduler_status
interface SchedulerJob {
  id: string;
  name: string;
  trigger: string;
  next_run_time?: string;
  pending: boolean;
}

interface SchedulerStatus {
  status: 'running' | 'stopped';
  jobs: SchedulerJob[];
  total_jobs: number;
  timestamp: string;
}

const getSchedulerStatus = async (): Promise<SchedulerStatus> => {
  const response = await fetch(`${API_BASE_URL}/api/${API_VERSION}/dev-tools/scheduler_status`, {
    method: 'GET',
    headers
  });

  if (!response.ok) {
    throw new Error(`Failed to get scheduler status: ${response.statusText}`);
  }

  return response.json();
};
```

### 3. Health Check Endpoints

#### Application Health
```typescript
// GET /health
const checkHealth = async (): Promise<{status: string}> => {
  const response = await fetch(`${API_BASE_URL}/health`, {
    method: 'GET'
  });

  return response.json();
};
```

#### Database Health
```typescript
// GET /health/db
const checkDatabaseHealth = async (): Promise<{status: string}> => {
  const response = await fetch(`${API_BASE_URL}/health/db`, {
    method: 'GET'
  });

  return response.json();
};
```

## React Component Integration Examples

### Sitemap Files List Component
```typescript
import React, { useState, useEffect } from 'react';

interface SitemapFilesListProps {
  domainId?: string;
}

const SitemapFilesList: React.FC<SitemapFilesListProps> = ({ domainId }) => {
  const [sitemapFiles, setSitemapFiles] = useState<SitemapFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    const fetchSitemapFiles = async () => {
      try {
        setLoading(true);
        const response = await listSitemapFiles({ 
          domain_id: domainId, 
          page, 
          size: 15 
        });
        setSitemapFiles(response.items);
        setTotalPages(response.pages);
      } catch (error) {
        console.error('Failed to fetch sitemap files:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSitemapFiles();
  }, [domainId, page]);

  const handleStatusUpdate = async (ids: string[], status: SitemapCurationStatus) => {
    try {
      await batchUpdateStatus({ sitemap_file_ids: ids, deep_scrape_curation_status: status });
      // Refresh the list
      const response = await listSitemapFiles({ domain_id: domainId, page, size: 15 });
      setSitemapFiles(response.items);
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };

  const handleTriggerImport = async (id: string) => {
    try {
      await triggerSitemapImport(id);
      // Refresh the list to show updated status
      const response = await listSitemapFiles({ domain_id: domainId, page, size: 15 });
      setSitemapFiles(response.items);
    } catch (error) {
      console.error('Failed to trigger import:', error);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="sitemap-files-list">
      <h2>Sitemap Files</h2>
      <table>
        <thead>
          <tr>
            <th>URL</th>
            <th>Type</th>
            <th>Import Status</th>
            <th>URL Count</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {sitemapFiles.map((file) => (
            <tr key={file.id}>
              <td>{file.url}</td>
              <td>{file.sitemap_type}</td>
              <td>
                <span className={`status ${file.sitemap_import_status?.toLowerCase()}`}>
                  {file.sitemap_import_status || 'Pending'}
                </span>
              </td>
              <td>{file.url_count}</td>
              <td>
                <button onClick={() => handleTriggerImport(file.id)}>
                  Trigger Import
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {/* Pagination */}
      <div className="pagination">
        <button 
          disabled={page === 1} 
          onClick={() => setPage(page - 1)}
        >
          Previous
        </button>
        <span>Page {page} of {totalPages}</span>
        <button 
          disabled={page === totalPages} 
          onClick={() => setPage(page + 1)}
        >
          Next
        </button>
      </div>
    </div>
  );
};
```

### Create Sitemap File Form
```typescript
import React, { useState } from 'react';

interface CreateSitemapFileFormProps {
  domainId: string;
  onSuccess: (sitemapFile: SitemapFile) => void;
}

const CreateSitemapFileForm: React.FC<CreateSitemapFileFormProps> = ({ domainId, onSuccess }) => {
  const [formData, setFormData] = useState<SitemapFileCreateRequest>({
    domain_id: domainId,
    url: '',
    sitemap_type: 'Standard',
    discovery_method: 'manual',
    priority: 5
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const sitemapFile = await createSitemapFile(formData);
      onSuccess(sitemapFile);
      setFormData({ ...formData, url: '', notes: '' }); // Reset form
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create sitemap file');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="create-sitemap-form">
      <h3>Add Sitemap File</h3>
      
      {error && <div className="error">{error}</div>}
      
      <div className="form-group">
        <label htmlFor="url">Sitemap URL *</label>
        <input
          id="url"
          type="url"
          value={formData.url}
          onChange={(e) => setFormData({ ...formData, url: e.target.value })}
          required
          placeholder="https://example.com/sitemap.xml"
        />
      </div>

      <div className="form-group">
        <label htmlFor="sitemap_type">Sitemap Type</label>
        <select
          id="sitemap_type"
          value={formData.sitemap_type}
          onChange={(e) => setFormData({ ...formData, sitemap_type: e.target.value })}
        >
          <option value="Standard">Standard</option>
          <option value="Index">Index</option>
          <option value="News">News</option>
          <option value="Video">Video</option>
          <option value="Image">Image</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="priority">Priority</label>
        <input
          id="priority"
          type="number"
          min="1"
          max="10"
          value={formData.priority}
          onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
        />
      </div>

      <div className="form-group">
        <label htmlFor="notes">Notes</label>
        <textarea
          id="notes"
          value={formData.notes || ''}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          placeholder="Optional notes about this sitemap"
        />
      </div>

      <button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create Sitemap File'}
      </button>
    </form>
  );
};
```

### Status Monitor Component
```typescript
import React, { useState, useEffect } from 'react';

const StatusMonitor: React.FC = () => {
  const [healthStatus, setHealthStatus] = useState<{app: string, db: string}>({
    app: 'unknown',
    db: 'unknown'
  });
  const [schedulerStatus, setSchedulerStatus] = useState<SchedulerStatus | null>(null);

  useEffect(() => {
    const checkStatuses = async () => {
      try {
        const [appHealth, dbHealth, scheduler] = await Promise.all([
          checkHealth(),
          checkDatabaseHealth(),
          getSchedulerStatus()
        ]);
        
        setHealthStatus({
          app: appHealth.status,
          db: dbHealth.status
        });
        setSchedulerStatus(scheduler);
      } catch (error) {
        console.error('Failed to check statuses:', error);
      }
    };

    checkStatuses();
    const interval = setInterval(checkStatuses, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="status-monitor">
      <h3>System Status</h3>
      
      <div className="status-grid">
        <div className={`status-item ${healthStatus.app}`}>
          <span>Application</span>
          <span className="status-value">{healthStatus.app}</span>
        </div>
        
        <div className={`status-item ${healthStatus.db}`}>
          <span>Database</span>
          <span className="status-value">{healthStatus.db}</span>
        </div>
        
        <div className={`status-item ${schedulerStatus?.status}`}>
          <span>Scheduler</span>
          <span className="status-value">{schedulerStatus?.status || 'unknown'}</span>
        </div>
      </div>

      {schedulerStatus && (
        <div className="scheduler-jobs">
          <h4>Active Jobs ({schedulerStatus.total_jobs})</h4>
          <ul>
            {schedulerStatus.jobs.map((job) => (
              <li key={job.id}>
                <strong>{job.name}</strong>
                <span>Next run: {job.next_run_time ? new Date(job.next_run_time).toLocaleString() : 'N/A'}</span>
                {job.pending && <span className="pending">Pending</span>}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
```

## Error Handling

### Standard Error Response Format
```typescript
interface ApiError {
  detail: string;
  status_code: number;
}

// Error handling utility
const handleApiError = (error: any): string => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};
```

## Real-time Updates

### WebSocket Integration (Future Enhancement)
```typescript
// WebSocket connection for real-time status updates
const useWebSocketUpdates = (sitemapFileId: string) => {
  const [status, setStatus] = useState<SitemapImportStatus>();

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/sitemap-files/${sitemapFileId}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'status_update') {
        setStatus(data.status);
      }
    };

    return () => ws.close();
  }, [sitemapFileId]);

  return status;
};
```

## Testing Integration

### Mock Data for Development
```typescript
export const mockSitemapFiles: SitemapFile[] = [
  {
    id: 'mock-1',
    tenant_id: 'tenant-1',
    domain_id: 'domain-1',
    url: 'https://example.com/sitemap.xml',
    sitemap_type: 'Standard',
    sitemap_import_status: SitemapImportStatus.Complete,
    url_count: 150,
    priority: 5,
    deep_scrape_curation_status: SitemapCurationStatus.New,
    is_active: true,
    created_at: '2025-08-18T10:00:00Z',
    updated_at: '2025-08-18T10:30:00Z'
  }
];
```

This comprehensive API reference provides everything needed to build a complete React frontend for WF6 workflow management, with full TypeScript support and tested endpoint specifications.
