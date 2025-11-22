# WF7 Contact Extraction Failure – Post-Mortem Summary (2025-11-22)

## TL;DR
Everything up to WF5 worked perfectly.  
WF7 ran, hit the page, but **failed to extract the contact** that is visibly present on http://www.sfwheels.com/contact.php  
→ Result: `PageProcessingStatus.Error`, no row in `contacts` table.

| Stage | What Happened | Status | Timestamp (UTC) | Evidence / Log Excerpt |
|-------|---------------|--------|-----------------|-------------------------|
| WF1   | Places search → 10 records | Success | ~08:22 | Deep scan queue processed |
| WF2   | Deep scan → 10 LocalBusiness | Success | 08:22 – 08:23 | 10 jobs completed |
| WF3   | You selected 7 LocalBusiness | Success | 08:27:24 | `Attempted to queue 7 businesses for domain extraction` |
| WF3   | 7 Domains created (incl. sfwheels.com) | Success | ~08:28 – 08:30 | `Extracted domain 'sfwheels.com'` |
| WF4   | Sitemaps discovered via robots.txt + common path | Success | 08:29:14 & 08:37:17 | `Added sitemap from robots.txt: http://www.sfwheels.com/sitemap.xml` |
| WF5   | Sitemap parsed → 14 URLs inserted | Success | 08:29:17 & later | `sitemap.get('urls') returned 14 URLs` |
| WF5   | You selected one sitemap file | Success | 08:39:42 | `Batch curation status update... updated_count: 1, queued_count: 1` |
| WF5   | 14 pages inserted into `pages` table | Success | 08:40:14 | `Bulk insert completed: 14 rows inserted` |
| WF7   | Page http://www.sfwheels.com/contact.php marked Selected | Success | ~08:44 | UI shows `PageCurationStatus.Selected` |
| WF7   | Scheduler picked it up and attempted extraction | Failed | ~08:44:21 | `PageProcessingStatus.Error` |
| Contacts table | **No contact row created** despite visible phone/email on page | Failed | — | Manual inspection confirms contact exists |

### Exact Failing Record (as of 2025-11-22 ~08:44 UTC)
```
URL:               http://www.sfwheels.com/contact.php
PageCurationStatus: Selected
PageProcessingStatus: Error
Processed At:      11/22/2025, 12:44:21 AM (UTC)
Contact in DB:     NONE (expected: phone + email visible on page)
```

### Root Cause Hypothesis (most likely)
The current WF7 scraper logic (in `src/services/page_scraper/` or the modernized scraper) does **not** correctly parse the contact block on this specific page layout.

Common culprits we have seen before:
- Contact inside `<script>` or loaded via JS
- Phone/email in SVG/text-as-image
- Anti-bot obfuscation (e.g. Cloudflare-style)
- Selector too strict / outdated

### Next Actions (prioritized)
1. **Immediate** – Pull the exact HTML of `http://www.sfwheels.com/contact.php` (via browser or `curl`) and share it.
2. Run the page through the current scraper locally with DEBUG logging enabled.
3. Identify which extractor failed (legacy Honeybee? modernized_page_scraper? contact_regex?).
4. Fix / add fallback pattern → re-queue the page → verify contact appears.

**The pipeline is 100 % healthy up to page insertion.**  
Only the **final contact extraction step** needs one targeted fix.
