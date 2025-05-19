Here's a technical work order formatted for an AI pairing partner (using industry-specific terminology and search patterns it would recognize):

````markdown
# WORK ORDER: LEGACY API VERSIONING ERADICATION

**Objective:**
`FULL_ELIMINATION(v1/v2/v3)` via `CODEBASE_SANITIZATION` with `ZERO_DOWNTIME`
**Priority:** `P0`
**Context Hash:** `SCRPRSKY-APIv3-LEGACY-ERADICATE-23Q3`

---

## WORK INSTRUCTIONS

1. **TARGET IDENTIFICATION**

   - **Pattern Match:**
     ```regex
     \/(v1|v2|v3)\/|version=[\"']?\d
     ```
   - **File Focus:**
     `main.py`, `*_routers/*`, `docs/*`, `config/versioning.py`

2. **DOCUMENTATION PURGE**

   - **Target Block:**
     ```python
     # LEGACY DOC BLOCK [hash:4D9F2C]
     html_content = \"\"\"
     <!-- Versioning Tab Content -->
     \"\"\"
     ```
   - **Replacement Protocol:**
     ```diff
     - <li><strong>v1</strong> - Legacy endpoints</li>
     + <li><strong>Unified API</strong> - Current endpoints</li>
     ```

3. **ROUTE SANITIZATION**

   - **Versioned Route Pattern:**
     ```python
     @app\.(get|post|put|delete)\(["']/api/v\d/
     ```
   - **Migration Protocol:**

     ```python
     # BEFORE
     @app.post("/api/v3/sitemap/scan")

     # AFTER
     @app.post("/api/sitemap/scan")
     ```

4. **DEPENDENCY CLEANSE**
   - **Version-Specific Imports:**
     ```python
     from .legacy import (VersionedScanner, v3_adaptor)
     ```
   - **Elimination Pattern:**
     ```regex
     (v1|v2|v3)(Adapter|Router|Schema)\b
     ```

---

## CODE SEARCH PATTERNS

1. **Versioned Endpoint Detection**
   ```ruby
   grep -nre '\/api\/v[0-9]' --include=*.py
   ```
````

2. **Schema Version Lock**

   ```sql
   SELECT column_name
   FROM information_schema.columns
   WHERE table_name='api_requests'
   AND column_name LIKE '%version%';
   ```

3. **Documentation Debt**
   ```python
   re.findall(r'We recommend using v\d', html_content)
   ```

---

## VALIDATION CRITERIA

1. **Post-Execution Sanity Check**

   ```bash
   curl -s http://localhost:8000/docs | jq '.paths | keys[]' | grep -c 'v[0-9]'
   # Expected: 0
   ```

2. **Versioning Genealogy Report**

   ```python
   def generate_legacy_report():
       return {
           'remaining_versioned_endpoints': CodeSearch.count('/v\d/'),
           'documentation_references': DocAnalysis.find_legacy_mentions(),
           'schema_vestiges': DatabaseScan.find_version_columns()
       }
   ```

3. **Swagger Conformity Check**
   ```json
   {
     "validation_checks": {
       "version_free_paths": "ALL",
       "consistent_naming": "RESTful_2023",
       "error_responses": "RFC7807"
     }
   }
   ```

---

## COLLABORATION PROTOCOL

**If Uncertain:**

```python
if (context.get('versioning_ambiguity') or
    (legacy_condition_detected and not config['FULL_ERADICATION_MODE']):
        raise NeedsHumanClarification(
            "Versioning ambiguity detected at " +
            frame_info.lineno,
            suggested_fixes=analyze_version_alternatives()
        )
```

**Rollback Plan:**

```bash
# If validation_score < 95%
git checkout -b LEGACY_FALLBACK_$(date +%s)
git restore --source=LEGACY_ANCHOR_TAG .
```

---

**WORK ORDER SIGNATURE:**
`[AI_PAIRING_SYSTEM_VALID]::SCRPRSKY-LEGACY-ERADICATE::23.8.1::CONFIRMED`

```

This work order uses several patterns an enterprise AI would recognize:

1. **Semantic Versioning Hashes** (`SCRPRSKY-APIv3-LEGACY-ERADICATE-23Q3`)
2. **Regex-Based Code Search Instructions**
3. **Validation-as-Code Patterns**
4. **Conditional Rollback Protocols**
5. **Contextual Error Handling** (`NeedsHumanClarification`)

The structure enables:
- Direct pattern matching in codebases
- Clear success/failure metrics
- Automated validation checks
- Safe rollback procedures

Would you like me to add any domain-specific constraints or additional collaboration protocols for your particular system architecture?
```
