# Operations Documentation

**Purpose:** Critical operational procedures, cost controls, and security incident documentation.

---

## What's Inside

### Vector Database (`Vector-Database.md`)

**Purpose:** Semantic search across ScraperSky architectural documentation

**What it does:**
- Converts queries to embeddings (OpenAI)
- Searches PostgreSQL vector database (pgvector)
- Returns relevant documentation chunks

**Quick Start:**
```bash
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "your query"
```

**Cost:** ~$0.0001 per query

**Critical Anti-Patterns:**
- ❌ Never pass vectors as string literals (causes dimension mismatch)
- ❌ Never hold DB connections during embedding generation (timeout)
- ❌ Never use direct SQL for vector search (use RPC function)

**When to read:** Before using semantic search

---

### ScraperAPI Cost Control (`ScraperAPI-Cost-Control.md`)

**Purpose:** Prevent cost overruns when scraping with ScraperAPI

**Background:** September 2025 cost crisis
- Single domain operation: $50 instead of $0.001
- Potential impact: $450,000-$480,000 if scaled
- Resolution: 99.998% cost reduction

**Safe Defaults:**
```bash
SCRAPER_API_ENABLE_PREMIUM=false
SCRAPER_API_ENABLE_JS_RENDERING=false
SCRAPER_API_ENABLE_GEOTARGETING=false
```

**Cost:** 1 credit per request (~$0.001)

**Critical Rule:** All expensive features opt-in, never opt-out

**When to read:**
- Before using ScraperAPI
- Before enabling premium features
- When investigating unexpected costs

---

### Security Incidents (`Security-Incidents.md`)

**Purpose:** Document known vulnerabilities and remediation status

**Critical Vulnerabilities (as of Nov 2025):**

🔴 **CATASTROPHIC: DB Portal Exposed**
- NO authentication on `/api/v3/db-portal/query`
- Allows arbitrary SQL execution
- Fix time: 5 minutes
- Status: ⚠️ UNRESOLVED

🔴 **CRITICAL: Dev Token Works in Production**
- Hardcoded token `"scraper_sky_2024"` works in ALL environments
- Full admin access
- Fix time: 10 minutes
- Status: ⚠️ UNRESOLVED

🟠 **HIGH: No Rate Limiting**
- Zero protection against brute force
- Fix time: 2 hours
- Status: ⚠️ UNRESOLVED

**Immediate Actions (2.5 hours total):**
1. Add auth to DB Portal (5 min)
2. Add environment check to dev token (10 min)
3. Implement rate limiting (2 hours)

**When to read:**
- Before deploying to production
- When reviewing security posture
- After security audit

---

## When to Use Each Document

**I need to search documentation:**
→ `Vector-Database.md`

**I'm using ScraperAPI:**
→ `ScraperAPI-Cost-Control.md`

**I'm reviewing security:**
→ `Security-Incidents.md`

**I need to fix security issues immediately:**
→ `Security-Incidents.md` → "Immediate Actions" section

---

## Operations Checklist

### Before Production Deployment

- [ ] **Security:** Read `Security-Incidents.md`
- [ ] **Security:** Fix 2 CATASTROPHIC issues (15 minutes)
- [ ] **Security:** Implement rate limiting (2 hours)
- [ ] **Costs:** Verify ScraperAPI configuration (all premium features = false)
- [ ] **Monitoring:** Enable cost monitoring (`SCRAPER_API_COST_CONTROL_MODE=true`)

### Ongoing Operations

- [ ] **Weekly:** Review ScraperAPI costs (should be ~$0.001 per request)
- [ ] **Monthly:** Review security incident status
- [ ] **Quarterly:** Security audit

---

## Emergency Procedures

### High ScraperAPI Costs Detected

1. **Check configuration:** Are premium features enabled?
2. **Check logs:** Look for `SCRAPER_COST_ALERT` warnings
3. **Disable premium features:** Set all to `false`
4. **Verify:** Test with single request, expect 1 credit

**Reference:** `ScraperAPI-Cost-Control.md` → "The Cost Crisis"

---

### Security Incident Detected

1. **Stop the bleeding:** Disable affected endpoints/features
2. **Review:** Check `Security-Incidents.md` for similar issues
3. **Fix:** Follow remediation guidance
4. **Test:** Verify fix in staging
5. **Deploy:** Push to production
6. **Document:** Update `Security-Incidents.md` with new incident

---

## Summary

**3 Critical Operations Documents:**

1. **Vector Database** - Semantic search (don't pass vectors as strings)
2. **ScraperAPI Cost Control** - Prevent $450k waste (all premium features = false)
3. **Security Incidents** - 2 CATASTROPHIC vulnerabilities to fix (15 minutes)

**Before production:** Fix security issues, verify cost controls.

**Remember:** Operations docs exist to prevent disasters that already happened once.
