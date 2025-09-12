# **WF7 Page Type Filter Enhancement PRD**
*Product Requirements Document for page_type Field Integration*
*Author: Claude AI*
*Date: September 11, 2025*

## **Executive Summary**

**Objective**: Add `page_type` field visibility and filtering capabilities to the WF7 page curation endpoint to enable targeted workflow management of Honeybee-categorized pages.

**Business Value**: Enable WF7 operators to efficiently filter and process high-value contact pages (e.g., `contact_root` pages with `New` status) identified by the Honeybee categorization system.

**Scope**: Single endpoint modification with backward compatibility.

---

## **1. Business Requirements**

### **1.1 User Story**
**As a** WF7 workflow operator  
**I want to** filter pages by both curation status AND page type  
**So that** I can efficiently process high-value contact pages identified by Honeybee  

### **1.2 Specific Use Case**
**Primary Need**: View and filter pages that are:
- `page_curation_status = "New"` (unprocessed)
- `page_type = "contact_root"` (high-value contact pages)

This combination represents the highest-priority pages for manual curation workflow.

### **1.3 Success Criteria**
- ✅ Ability to filter by `page_type` via query parameter
- ✅ `page_type` field visible in API response  
- ✅ Combined filtering works (status + type)
- ✅ No performance degradation
- ✅ Backward compatibility maintained

---

## **2. Technical Context**

### **2.1 Honeybee System Integration**
The `page_type` field is populated by the Honeybee categorization system with the following values:

**High-Value Types:**
- `contact_root` - Root contact pages (confidence: 0.9)
- `career_contact` - Career contact pages (confidence: 0.7)  
- `legal_root` - Legal/privacy pages (confidence: 0.6)
- `wp_prospect` - WordPress signals (confidence: 0.9)

**Default Type:**
- `unknown` - Uncategorized pages (confidence: 0.2)

### **2.2 Current Endpoint State**
**Endpoint**: `GET /api/v3/pages`  
**File**: `src/routers/v3/WF7_V3_L3_1of1_PagesRouter.py:32-94`

**Existing Filters:**
- `page_curation_status` (New, Selected, Queued, Processing, Complete, Error)
- `page_processing_status` (Queued, Processing, Complete, Error, Filtered)  
- `url_contains` (string search)

**Missing**: `page_type` filter and response field

---

## **3. Technical Specifications**

### **3.1 Database Schema (Verified)**
```sql
-- Field exists in pages table
page_type TEXT NULL
```
**Model Reference**: `src/models/page.py:91`
```python
page_type: Column[Optional[str]] = Column(Text, nullable=True)
```

### **3.2 API Specification**

#### **Request Parameters (Addition)**
```python
page_type: Optional[str] = Query(
    None, 
    description="Filter by page type (contact_root, career_contact, legal_root, wp_prospect, unknown)"
)
```

#### **Response Schema (Addition)**
```json
{
  "pages": [
    {
      "id": "uuid",
      "url": "string", 
      "title": "string",
      "domain_id": "uuid",
      "curation_status": "string",
      "processing_status": "string", 
      "page_type": "contact_root",  // NEW FIELD
      "updated_at": "iso-string",
      "created_at": "iso-string",
      "error": "string"
    }
  ],
  "total": 100,
  "offset": 0,
  "limit": 50,
  "filters_applied": {
    "page_curation_status": "New",
    "page_processing_status": null,
    "url_contains": null,
    "page_type": "contact_root"  // NEW FIELD
  }
}
```

#### **Example Usage**
```bash
# Get all new contact_root pages for processing
GET /api/v3/pages?page_curation_status=New&page_type=contact_root

# Get all career contact pages regardless of status
GET /api/v3/pages?page_type=career_contact

# Combined filtering for specific workflow
GET /api/v3/pages?page_curation_status=New&page_type=contact_root&limit=20
```

---

## **4. Implementation Plan**

### **4.1 Code Changes Required**

#### **File**: `src/routers/v3/WF7_V3_L3_1of1_PagesRouter.py`

**Change 1**: Add query parameter (around line 40)
```python
page_type: Optional[str] = Query(None, description="Filter by page type")
```

**Change 2**: Add filter logic (around line 55)
```python
if page_type:
    filters.append(Page.page_type == page_type)
```

**Change 3**: Add to response (around line 82)
```python
"page_type": page.page_type,
```

**Change 4**: Add to filters tracking (around line 93)
```python
"page_type": page_type
```

### **4.2 Testing Requirements**

**Unit Tests:**
- Filter by `page_type` only
- Combined filters (`page_curation_status` + `page_type`)
- Null/empty `page_type` handling
- Invalid `page_type` values

**Integration Tests:**  
- End-to-end API response validation
- Database query performance with new filter
- Pagination with `page_type` filter

**Manual Testing Scenarios:**
```bash
# Scenario 1: Primary use case
GET /api/v3/pages?page_curation_status=New&page_type=contact_root

# Scenario 2: Page type only
GET /api/v3/pages?page_type=contact_root

# Scenario 3: Invalid page type (should return empty results)
GET /api/v3/pages?page_type=invalid_type

# Scenario 4: Null values handling
GET /api/v3/pages?page_type=unknown
```

---

## **5. Risk Assessment**

### **5.1 Low Risk**
- **Field Exists**: `page_type` column already exists in database
- **Data Populated**: Honeybee system actively populates this field  
- **Simple Addition**: No existing functionality modified
- **Backward Compatible**: New parameter is optional

### **5.2 Considerations**
- **Performance**: Additional filter adds WHERE clause - monitor query performance
- **Data Quality**: Some older pages may have NULL `page_type` values
- **API Documentation**: Update API docs with new parameter

### **5.3 Rollback Plan**
Simple parameter removal if issues arise - no data changes involved.

---

## **6. Acceptance Criteria**

### **6.1 Functional Requirements**
- [ ] API accepts `page_type` query parameter without errors
- [ ] Filtering returns only pages matching specified `page_type`
- [ ] `page_type` field appears in response JSON
- [ ] Combined filtering works correctly (`status` + `type`)
- [ ] Empty/null `page_type` handled gracefully
- [ ] Invalid `page_type` values return appropriate results

### **6.2 Non-Functional Requirements**
- [ ] Response time remains under 500ms for typical queries
- [ ] Backward compatibility: existing clients unaffected  
- [ ] API documentation updated
- [ ] Comprehensive test coverage added

### **6.3 Business Validation**
- [ ] WF7 operators can efficiently filter for `New` + `contact_root` pages
- [ ] Workflow efficiency demonstrably improved
- [ ] No regression in existing WF7 functionality

---

## **7. Dependencies & Prerequisites**

### **7.1 Technical Dependencies**
- ✅ **Database Schema**: `page_type` column exists
- ✅ **Data Population**: Honeybee system populating field
- ✅ **Model Definition**: Page model includes `page_type`  
- ✅ **Endpoint Framework**: FastAPI router structure in place

### **7.2 No Blockers Identified**
All prerequisites are met. Implementation can proceed immediately.

---

## **8. Success Metrics**

### **8.1 Technical Metrics**
- **API Response Time**: < 500ms for filtered queries
- **Test Coverage**: 100% for new filtering logic
- **Zero Regression**: All existing tests continue passing

### **8.2 Business Metrics**
- **Workflow Efficiency**: Time to identify target pages reduced
- **Operator Satisfaction**: Positive feedback on filtering capability
- **Usage Adoption**: `page_type` parameter used in production queries

---

## **9. Implementation Timeline**

**Estimated Effort**: 2-4 hours development + testing

**Phase 1 (1 hour)**: Code implementation
- Add query parameter
- Add filter logic  
- Update response schema
- Update filters tracking

**Phase 2 (1-2 hours)**: Testing
- Unit tests for new filtering
- Integration test scenarios
- Manual testing validation

**Phase 3 (30 minutes)**: Documentation
- Update API documentation
- Update endpoint comments

**Total Timeline**: Same-day implementation possible

---

## **10. Conclusion**

This enhancement provides immediate business value by enabling targeted filtering of high-value pages identified by the Honeybee categorization system. The implementation is low-risk, backward-compatible, and leverages existing infrastructure.

**The primary business outcome**: WF7 operators can now efficiently identify and process `New` pages of type `contact_root`, significantly improving workflow efficiency for the highest-value contact page processing.

**Technical foundation**: Built on the solid Honeybee system specification, this enhancement safely extends existing functionality without architectural changes.

---

**This PRD provides complete implementation guidance while maintaining alignment with the ScraperSky system architecture and WF7 workflow requirements.**