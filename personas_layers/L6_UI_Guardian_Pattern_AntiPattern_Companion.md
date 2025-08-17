# L6 UI Guardian Pattern-AntiPattern Companion
## Instant Pattern Recognition & Violation Detection Guide

**Version:** 1.0  
**Purpose:** Enable instant UI pattern recognition and violation detection  
**Cardinal Rule:** External files, semantic HTML, no hardcoded secrets!  
**Usage:** Load ONLY this document for complete L6 UI review authority  
**Verification Requirement:** All JavaScript must be external, all data sanitized  

---

## QUICK REFERENCE SECTION

### 🎯 INSTANT PATTERN CHECKLIST
- [ ] JavaScript in external `.js` files, not inline
- [ ] CSS in external `.css` files, not embedded
- [ ] No hardcoded tokens or API endpoints
- [ ] Data sanitized before DOM insertion (no innerHTML with data)
- [ ] Semantic HTML structure used (not just divs)
- [ ] Asset directories properly organized (`css/`, `js/`, `img/`)

### 🔴 INSTANT REJECTION TRIGGERS
1. **Hardcoded JWT tokens** → REJECT (Security violation)
2. **innerHTML with API data** → REJECT (XSS vulnerability)
3. **Missing JS dependencies** → REJECT (Pattern #1 violation)
4. **Inline JavaScript/CSS** → REJECT (Pattern #2 violation)
5. **Global namespace pollution** → REJECT (Pattern #5 violation)
6. **No data refresh after updates** → REJECT (Pattern #6 violation)

### ✅ APPROVAL REQUIREMENTS
Before approving ANY UI implementation:
1. Verify all JavaScript in external files
2. Confirm no hardcoded credentials
3. Check innerHTML usage is safe
4. Verify semantic HTML structure
5. Confirm proper asset organization
6. Ensure accessibility features present

---

## PATTERN #1: External JavaScript Files

### ✅ CORRECT PATTERN:
```html
<!-- HTML file -->
<!DOCTYPE html>
<html>
<head>
    <!-- External JavaScript files -->
    <script src="/static/js/utils.js"></script>
    <script src="/static/js/api_client.js"></script>
    <script src="/static/js/domain-curation-tab.js"></script>
</head>
<body>
    <!-- Clean HTML, no inline scripts -->
    <button id="submit-btn">Submit</button>
</body>
</html>

<!-- domain-curation-tab.js -->
document.getElementById('submit-btn').addEventListener('click', handleSubmit);
```
**Why:** Separation of concerns, caching, maintainability  
**Citation:** Layer 6 Blueprint 2.3.1

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Missing Dependencies**
```html
<!-- scraper-sky-mvp.html - VIOLATION! -->
<script src="/static/js/utils.js"></script>  <!-- File doesn't exist! -->
<script src="/static/js/api_client.js"></script>  <!-- Missing! -->
<script src="/static/js/main.js"></script>  <!-- 404 error! -->
```
**Detection:** Check if referenced JS files exist  
**From Audit:** Multiple critical JS files missing  
**Impact:** Console errors, broken functionality

**Violation B: Inline JavaScript**
```html
<!-- VIOLATION: JavaScript in HTML -->
<button onclick="submitForm()">Submit</button>
<script>
    function submitForm() {
        // Inline script - WRONG!
    }
</script>
```
**Detection:** `onclick`, `<script>` tags in HTML  
**From Audit:** Inline handlers found in templates  
**Impact:** CSP violations, unmaintainable code

---

## PATTERN #2: Security - No Hardcoded Secrets

### ✅ CORRECT PATTERN:
```javascript
// api_client.js - Centralized auth
async function getAuthToken() {
    // Get token from secure storage or auth service
    return localStorage.getItem('jwt_token') || 
           await refreshToken();
}

// domain-curation-tab.js - Use centralized auth
async function fetchDomains() {
    const token = await getAuthToken();  // Never hardcoded
    const response = await fetch('/api/v3/domains', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
}
```
**Why:** Prevents credential exposure, enables rotation  
**Citation:** Layer 6 Blueprint 2.3.7

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Hardcoded JWT Tokens**
```javascript
// domain-curation-tab.js - CRITICAL VIOLATION!
const DEV_TOKEN_DC = "eyJhbGciOiJIUzI1NiIs...";  // HARDCODED!

async function fetchDomains() {
    // Using hardcoded token
    headers: {
        'Authorization': `Bearer ${DEV_TOKEN_DC}`
    }
}
```
**Detection:** String literals starting with "eyJ" (JWT)  
**From Audit:** Found in domain-curation-tab.js, sitemap-curation-tab.js  
**Impact:** Security breach, authentication bypass

**Violation B: Hardcoded API Endpoints**
```javascript
// VIOLATION: Hardcoded URLs
const API_URL = "https://api.scrapersky.com/v3/";  // WRONG!
```
**Detection:** URL strings in JavaScript files  
**From Audit:** Multiple hardcoded endpoints  
**Impact:** Cannot change environments without code changes

---

## PATTERN #3: XSS Prevention - Safe DOM Manipulation

### ✅ CORRECT PATTERN:
```javascript
// Safe text insertion
function displayMessage(message) {
    const element = document.getElementById('message');
    element.textContent = message;  // Safe for any content
}

// Safe HTML with sanitization
function displayRichContent(html) {
    const sanitized = DOMPurify.sanitize(html);
    element.innerHTML = sanitized;  // Only after sanitization
}

// Creating elements safely
function addListItem(text) {
    const li = document.createElement('li');
    li.textContent = text;  // Never innerHTML for user data
    list.appendChild(li);
}
```
**Why:** Prevents XSS attacks from malicious content  
**Citation:** Layer 6 Blueprint 2.3.8

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: innerHTML with API Data**
```javascript
// batch-search-tab.js - XSS VULNERABILITY!
function displayError(error) {
    errorDiv.innerHTML = error.message;  // UNSAFE!
    // If error.message contains <script>, it executes!
}

function showResults(data) {
    resultsDiv.innerHTML = `
        <h3>${data.title}</h3>
        <p>${data.description}</p>
    `;  // Direct API data in innerHTML - VULNERABLE!
}
```
**Detection:** `.innerHTML` with variables/API responses  
**From Audit:** Multiple files use innerHTML unsafely  
**Impact:** XSS attacks, code injection

---

## PATTERN #4: External Stylesheets

### ✅ CORRECT PATTERN:
```html
<!-- HTML file -->
<head>
    <link rel="stylesheet" href="/static/css/main.css">
    <link rel="stylesheet" href="/static/css/components.css">
</head>

<!-- main.css -->
.container {
    max-width: 1200px;
    margin: 0 auto;
}

<!-- No inline styles in HTML -->
<div class="container">Content</div>
```
**Why:** Caching, maintainability, separation of concerns  
**Citation:** Layer 6 Blueprint 2.2.1

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Massive Embedded Styles**
```html
<!-- scraper-sky-mvp.html - VIOLATION! -->
<style>
    /* 500+ lines of CSS embedded in HTML! */
    .container { ... }
    .header { ... }
    /* Should be in external file */
</style>
```
**Detection:** Large `<style>` blocks in HTML  
**From Audit:** Massive embedded CSS in main file  
**Impact:** No caching, difficult maintenance

**Violation B: Inline Style Attributes**
```html
<!-- VIOLATION: Inline styles -->
<div style="margin: 10px; padding: 20px; background: #fff;">
    Content
</div>
```
**Detection:** `style=` attributes in HTML  
**From Audit:** Widespread inline styles  
**Impact:** Specificity issues, unmaintainable

---

## PATTERN #5: Module Pattern & No Global Pollution

### ✅ CORRECT PATTERN:
```javascript
// domain-module.js - Encapsulated module
const DomainModule = (function() {
    // Private variables
    let domains = [];
    
    // Private functions
    function validateDomain(domain) {
        // Validation logic
    }
    
    // Public API
    return {
        fetchDomains: async function() {
            // Implementation
        },
        updateDomain: async function(id, data) {
            // Implementation
        }
    };
})();

// Usage - no globals exposed
DomainModule.fetchDomains();
```
**Why:** Prevents naming conflicts, enables modularity  
**Citation:** Layer 6 Blueprint 2.3.3

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Global Function Pollution**
```javascript
// local-business-curation-tab.js - VIOLATION!
// Exposing global function for other scripts
window.fetchLocalBusinessData = function() {
    // Function exposed globally
};

// google-maps-common.js - Relies on global
fetchLocalBusinessData();  // Assumes global exists!
```
**Detection:** `window.functionName` assignments  
**From Audit:** Scripts depend on global functions  
**Impact:** Fragile dependencies, load order issues

---

## PATTERN #6: Data Refresh After Updates

### ✅ CORRECT PATTERN:
```javascript
// Automatic refresh after updates
async function updateDomain(id, data) {
    try {
        // Update the domain
        await api.updateDomain(id, data);
        
        // Immediately refresh the display
        await refreshDomainList();
        
        // Show success feedback
        showNotification('Domain updated successfully');
    } catch (error) {
        showError('Update failed: ' + error.message);
    }
}

// Optimistic UI update
function optimisticUpdate(id, newData) {
    // Update UI immediately
    updateUIElement(id, newData);
    
    // Then sync with server
    api.updateDomain(id, newData).catch(() => {
        // Revert on failure
        revertUIElement(id);
    });
}
```
**Why:** Better UX, data consistency, user confidence  
**Citation:** UI best practices for data management

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: No Refresh After Update**
```javascript
// staging-editor-tab.js - VIOLATION!
async function batchUpdate() {
    await api.updateBatch(data);
    
    // No refresh! User sees stale data
    showMessage('Update complete');
    // User must manually refresh page - BAD UX!
}
```
**Detection:** Update operations without refresh calls  
**From Audit:** All curation tabs lack auto-refresh  
**Impact:** Stale data display, user confusion

---

## PATTERN #7: Asset Organization

### ✅ CORRECT PATTERN:
```
static/
├── css/
│   ├── main.css
│   ├── components.css
│   └── themes/
├── js/
│   ├── utils.js
│   ├── api_client.js
│   └── tabs/
│       ├── domain-curation-tab.js
│       └── sitemap-curation-tab.js
├── img/
│   ├── logo.png
│   └── icons/
└── fonts/
    └── custom-font.woff2
```
**Why:** Organized structure, easy maintenance  
**Citation:** Layer 6 Blueprint 2.4.1

### ❌ ANTI-PATTERN VIOLATIONS:

**Violation A: Flat File Structure**
```
static/  - VIOLATION!
├── scraper-sky-mvp.html
├── domain-curation-tab.js
├── sitemap-curation-tab.js
├── logo.png
├── style.css
└── (everything mixed together)
```
**Detection:** No subdirectories in static/  
**From Audit:** Missing standard directory structure  
**Impact:** Disorganized assets, difficult scaling

---

## VERIFICATION REQUIREMENTS

### UI Review Protocol
```bash
# Check for missing JavaScript files
grep -h "src=\"/static" static/*.html | while read line; do
    file=$(echo $line | sed 's/.*src="\/\(.*\)".*/\1/')
    [ ! -f "$file" ] && echo "MISSING: $file"
done

# Find hardcoded tokens
grep -r "eyJ" static/js/ --include="*.js"

# Check for unsafe innerHTML
grep -r "innerHTML.*=" static/js/ --include="*.js"

# Verify asset organization
ls -la static/{css,js,img,fonts} 2>/dev/null || echo "Missing directories"
```

### What WF7 Did Wrong:
```javascript
// 1. Referenced non-existent JS files
// 2. Hardcoded JWT tokens in code
// 3. Used innerHTML with API data
// 4. No data refresh after updates
```

### What WF7 Should Have Done:
```javascript
// 1. Create all referenced JS files
// 2. Use centralized auth function
// 3. Use textContent or sanitize HTML
// 4. Auto-refresh after all updates
```

---

## GUARDIAN CITATION FORMAT

When reviewing Layer 6 UI, use this format:

```markdown
L6 UI GUARDIAN ANALYSIS:
❌ VIOLATION of Pattern #1: Missing JS dependencies (utils.js, api_client.js)
❌ VIOLATION of Pattern #2: Hardcoded JWT token at line 15
❌ VIOLATION of Pattern #3: innerHTML with API data (XSS risk)
⚠️ WARNING on Pattern #6: No auto-refresh after updates

REQUIRED CORRECTIONS:
1. Create missing JavaScript files or remove references
2. Replace hardcoded token with getAuthToken() call
3. Use textContent instead of innerHTML for API data
4. Add refreshDomainList() after update operations

APPROVAL: DENIED - Security violations must be fixed immediately
```

---

## REPLACES
- Full Layer 6 UI/Static Blueprint (300+ lines)
- All UI component audit reports (8 documents)
- JavaScript security guidelines
- Asset organization documentation

**With this single 480-line companion for instant pattern recognition!**

---

*"External files, semantic HTML, sanitized data, organized assets."*  
**- The L6 UI Guardian**