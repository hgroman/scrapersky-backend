# WF7 TROUBLESHOOTING PLAN - REAL EMPIRICAL TESTING

## THE PROBLEM
WF7 service claims to process pages but NO CONTACTS appear in the database. Previous AI wasted hours with fake fixes. This plan follows empirical testing methodology.

## PHASE 1: FIND URLS WITH ACTUAL CONTACT INFO
**NO SKIPPING - TEST UNTIL WE FIND WORKING DATA**

### Step 1.1: Create URL Testing Script
```python
# test_url_scraping.py
# This script will:
# - Take a URL as input
# - Use ScraperAPI to fetch content
# - Extract ALL emails found
# - Extract ALL phone numbers found  
# - Show what would be inserted into database
```

### Step 1.2: Test These URL Categories
- [ ] Local plumber websites (e.g., "Bob's Plumbing Denver")
- [ ] Local dentist offices (e.g., "Smith Family Dentistry")
- [ ] Local restaurants with contact pages
- [ ] Real estate agent websites
- [ ] Small law firms
- [ ] Auto repair shops
- [ ] HVAC service companies
- [ ] Local veterinary clinics
- [ ] Accounting firms
- [ ] Home cleaning services

### Step 1.3: Success Criteria
✅ Find at least 5 URLs with REAL emails (not info@, not noreply@)
✅ Find at least 3 URLs with REAL phone numbers
✅ Document each working URL and its contacts
❌ DO NOT PROCEED WITHOUT THIS DATA

## PHASE 2: VERIFY EXTRACTION PATTERNS WORK

### Step 2.1: Test Regex on Real HTML
- Test email pattern: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
- Test phone pattern: `\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}`
- Verify patterns catch all variations found

### Step 2.2: Create Golden Dataset
```
URL                           | Expected Email        | Expected Phone
------------------------------|----------------------|----------------
[Working URL 1]               | real@email.com       | 555-123-4567
[Working URL 2]               | contact@business.com | (555) 234-5678
[Working URL 3]               | name@company.com     | 555.345.6789
[Working URL 4]               | info@realplace.com   | +1 555 456 7890
[Working URL 5]               | hello@actual.com     | 555-567-8901
```

## PHASE 3: TEST DATABASE INSERTION DIRECTLY

### Step 3.1: Create Database Test Script
```python
# test_db_insert.py
# This script will:
# - Create a Contact object with test data
# - Insert using session.add()
# - Commit using session.commit()
# - Query database to verify it exists
# - Print the contact ID created
```

### Step 3.2: Test Cases
- [ ] Insert new contact - verify it appears
- [ ] Insert duplicate email - verify constraint behavior
- [ ] Insert with all fields populated
- [ ] Insert with minimal fields
- [ ] Verify created_at and updated_at are set

## PHASE 4: DIAGNOSE THE SERVICE FAILURE

### Step 4.1: Add Heavy Logging to Service
```python
# In WF7_V2_L4_1of2_PageCurationService.py add:
logging.info(f"1. Starting processing for page {page_id}")
logging.info(f"2. Page URL: {page.url}")
logging.info(f"3. HTML content length: {len(html_content)}")
logging.info(f"4. Emails found: {emails}")
logging.info(f"5. Phones found: {phones}")
logging.info(f"6. About to session.add() contact: {contact_email}")
logging.info(f"7. After session.add() - before commit")
logging.info(f"8. After commit - contact should be in DB")
# Then query to verify:
logging.info(f"9. Verified contact in DB: {contact.id}")
```

### Step 4.2: Process Single Page Manually
- Use working URL from Phase 1
- Watch logs for each step
- Query database after EACH log
- Find where contact disappears

### Step 4.3: Transaction Analysis
Check for:
- [ ] Nested transaction issues (`async with session.begin()`)
- [ ] Missing commits
- [ ] Rollback on exception
- [ ] Session scope problems

## PHASE 5: FIX THE ACTUAL PROBLEM

### Step 5.1: The Likely Fix
```python
# REMOVE the nested transaction:
# async with session.begin():  # DELETE THIS LINE

# Just use session directly:
session.add(new_contact)
await session.commit()  # Explicit commit

# Verify it worked:
await session.refresh(new_contact)
logging.info(f"Contact created with ID: {new_contact.id}")
```

### Step 5.2: Test Fix with Golden URLs
- [ ] Process each golden URL
- [ ] Verify contact appears in database
- [ ] Check no duplicates created
- [ ] Confirm all fields populated correctly

## PHASE 6: FULL END-TO-END VALIDATION

### Step 6.1: Local Testing
- [ ] Run test_wf7_end_to_end.py with working URL
- [ ] Set 5 pages to "Selected" status  
- [ ] Let scheduler process them
- [ ] Count contacts before and after
- [ ] Verify all 5 create contacts

### Step 6.2: Production Deployment
- [ ] Deploy ONLY after local success
- [ ] Process 10 pages in production
- [ ] Monitor Supabase table directly
- [ ] Count actual contacts created
- [ ] NO ASSUMPTIONS - only database proof

## CRITICAL RULES

### WHAT I MUST DO:
✅ Test URLs iteratively until finding ones with contacts
✅ Verify every step with database queries
✅ Use real data, not fake placeholders
✅ Test locally before any deployment
✅ Count actual database records

### WHAT I MUST NOT DO:
❌ Skip URL discovery phase
❌ Assume ScraperAPI works without testing
❌ Claim success without database proof
❌ Deploy untested code
❌ Trust logs over actual database state

## PROGRESS TRACKING

- [ ] Phase 1: Found 5+ working URLs with real contacts
- [ ] Phase 2: Verified extraction patterns work
- [ ] Phase 3: Proven database insertion works
- [ ] Phase 4: Identified exact failure point
- [ ] Phase 5: Fixed and tested with golden URLs
- [ ] Phase 6: Validated end-to-end locally
- [ ] Phase 6: Deployed and verified in production

## EMPIRICAL EVIDENCE REQUIRED

Before claiming ANY success, I must show:
1. The URL tested
2. The HTML content length received  
3. The emails and phones extracted
4. The database query showing contact exists
5. The contact ID created
6. Screenshot/proof of Supabase table

**NO ASSUMPTIONS. NO FAKE FIXES. ONLY EMPIRICAL PROOF.**