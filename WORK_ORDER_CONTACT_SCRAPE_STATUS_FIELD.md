# Work Order: Add Contact Scrape Status Field to Pages Table

**ID:** WO-2025-09-13-001
**Priority:** High
**Type:** Data Architecture Fix

## Problem

WF7 background service creates fake contact records (`notfound_pageID@domain.com`) when no contacts are found, polluting the contacts table with 2,763+ garbage records.

## Solution

Add `contact_scrape_status` field to pages table to track contact extraction results instead of creating fake contact records.

## Required Changes

### 1. Add Enum (`src/models/enums.py`)
```python
class ContactScrapeStatus(str, Enum):
    New = "New"
    ContactFound = "ContactFound"
    NoContactFound = "NoContactFound"
    Error = "Error"
    NotAFit = "NotAFit"
```

### 2. Update Page Model (`src/models/page.py`)
```python
contact_scrape_status = Column(
    Enum(ContactScrapeStatus, create_type=False, native_enum=True),
    nullable=False,
    default=ContactScrapeStatus.New,
    index=True,
)
```

### 3. Database Migration
```sql
-- Create enum type
CREATE TYPE contact_scrape_status AS ENUM ('New', 'ContactFound', 'NoContactFound', 'Error', 'NotAFit');

-- Add column with default
ALTER TABLE pages ADD COLUMN contact_scrape_status contact_scrape_status DEFAULT 'New' NOT NULL;

-- Add index
CREATE INDEX idx_pages_contact_scrape_status ON pages(contact_scrape_status);

-- Update existing records that have fake contacts to 'NoContactFound'
UPDATE pages SET contact_scrape_status = 'NoContactFound'
WHERE id IN (
    SELECT DISTINCT page_id FROM contacts
    WHERE email LIKE 'notfound_%@%'
);
```

### 4. Update WF7 Service (`src/services/WF7_V2_L4_1of2_PageCurationService.py`)

**Replace lines 94-98:**
```python
# OLD - Creates fake contact
page_id_short = str(page_id).split('-')[0]
contact_email = f"notfound_{page_id_short}@{domain_name}"
contact_name = f"No Contact Found - {domain_name}"

# NEW - Update page status
page.contact_scrape_status = ContactScrapeStatus.NoContactFound.value
await session.commit()
continue  # Skip contact creation
```

**Add after successful contact creation:**
```python
# Mark page as having contact found
page.contact_scrape_status = ContactScrapeStatus.ContactFound.value
```

### 5. Cleanup Fake Contacts
```sql
-- Delete fake contact records
DELETE FROM contacts WHERE email LIKE 'notfound_%@%';
```

## Files to Modify

1. `src/models/enums.py` - Add ContactScrapeStatus enum
2. `src/models/page.py` - Add contact_scrape_status field
3. `src/services/WF7_V2_L4_1of2_PageCurationService.py` - Update logic
4. `migrations/` - New migration file
5. `src/schemas/` - Update page schemas if needed

## Verification

- Contacts table contains only real contact records
- Pages table tracks contact scrape status correctly
- WF7 service no longer creates fake contacts
- Can query pages by contact scrape status

## Rollback Plan

Revert migration, restore WF7 service logic to create fake contacts.