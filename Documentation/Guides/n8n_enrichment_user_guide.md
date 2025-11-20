# n8n Contact Enrichment - User Guide

**Feature:** Contact Enrichment via n8n  
**Status:** ✅ Production Ready  
**Last Updated:** 2025-11-19

---

## What is Contact Enrichment?

Contact enrichment automatically finds and adds missing information about your contacts, including:
- 📞 Additional phone numbers
- 🏢 Company information (name, website, industry, size)
- 📍 Physical addresses
- 🔗 Social media profiles (LinkedIn, Twitter, Facebook)
- 📧 Additional email addresses
- 📊 Data quality scores

This data is gathered from multiple sources (Clearbit, Hunter.io, LinkedIn API, etc.) and stored directly in your contact records.

---

## How It Works

### The Two-Way Integration

```
Step 1: Send Contact to n8n (WO-020)
  ↓
Step 2: n8n Enriches Contact (external workflows)
  ↓
Step 3: n8n Returns Enriched Data (WO-021)
  ↓
Step 4: Data Stored in 15 Database Fields
```

### What Gets Enriched?

When you send a contact to n8n for enrichment, the system attempts to find:

1. **Contact Information**
   - Additional phone numbers
   - Alternative email addresses
   - Physical mailing address

2. **Professional Information**
   - Company name and website
   - Industry and company size
   - Job title verification

3. **Social Presence**
   - LinkedIn profile URL
   - Twitter handle
   - Facebook profile
   - Other social networks

4. **Data Quality**
   - Confidence score (0-100)
   - Which data sources were used
   - How long enrichment took
   - Estimated cost per contact

---

## Using Contact Enrichment

### Step 1: Select Contacts for Enrichment

1. Open the **Contact Launchpad**
2. Select one or more contacts
3. Click the **"Sync to n8n"** button

**What happens:**
- Contact status changes to "Selected"
- Contact is queued for enrichment
- Background scheduler picks it up within 1-5 minutes

### Step 2: Wait for Enrichment

**Processing time:** 10-30 seconds per contact (varies by data source availability)

**Status indicators:**
- 🟡 **Pending** - Waiting in queue
- 🔵 **Processing** - Currently being enriched
- 🟢 **Complete** - Enrichment successful
- 🟠 **Partial** - Some data found, but not all
- 🔴 **Failed** - Enrichment failed (will retry automatically)

### Step 3: View Enriched Data

Once enrichment is complete, the contact record will show:

**New Fields Available:**
- **Enriched Phone** - Additional phone number (if found)
- **Enriched Address** - Complete mailing address
- **Social Profiles** - Links to social media accounts
- **Company Info** - Employer details
- **Additional Emails** - Alternative email addresses
- **Confidence Score** - Data quality rating (0-100)

**Example:**
```
Original Contact:
  Name: John Doe
  Email: john@example.com
  Phone: (empty)
  Company: (empty)

After Enrichment:
  Name: John Doe
  Email: john@example.com
  Phone: +1-555-0123 ← NEW
  Company: Acme Corp ← NEW
  LinkedIn: https://linkedin.com/in/johndoe ← NEW
  Address: 123 Main St, San Francisco, CA 94102 ← NEW
  Confidence Score: 85/100 ← NEW
```

---

## Understanding Enrichment Status

### Complete ✅
All requested data was found and added to the contact.

**What you'll see:**
- All 15 enrichment fields populated
- High confidence score (70-100)
- Multiple data sources used

### Partial ⚠️
Some data was found, but not everything.

**What you'll see:**
- Some enrichment fields populated
- Medium confidence score (40-70)
- Fewer data sources used

**Common reasons:**
- Contact has limited online presence
- Some data sources didn't have information
- Privacy settings blocked certain data

### Failed ❌
Enrichment could not be completed.

**What you'll see:**
- Error message in enrichment_error field
- No new data added
- System will retry automatically (up to 3 times)

**Common reasons:**
- Invalid email address
- Contact doesn't exist online
- Data source API errors
- Network issues

---

## Data Quality and Confidence Scores

### Confidence Score (0-100)

**90-100: Excellent**
- Multiple sources confirmed the data
- High-quality, recent information
- Very likely to be accurate

**70-89: Good**
- Data found from reliable sources
- Most information confirmed
- Likely to be accurate

**50-69: Fair**
- Limited sources available
- Some information may be outdated
- Use with caution

**Below 50: Poor**
- Very limited data found
- Low confidence in accuracy
- Verify before using

### Data Sources

The enrichment process uses multiple data sources:
- **Clearbit** - Company and professional data
- **Hunter.io** - Email verification and discovery
- **LinkedIn API** - Professional profiles
- **Custom scrapers** - Public web data

**More sources = Higher confidence**

---

## Privacy and Compliance

### What Data is Collected?

Only **publicly available** information is collected:
- Data from public websites
- Information from professional networks (LinkedIn, etc.)
- Company directories
- Public records

### GDPR Compliance

- ✅ Only public data is collected
- ✅ Data sources are documented
- ✅ Users can request data deletion
- ✅ Confidence scores help assess data quality

### Data Retention

- Enriched data is stored in your database
- You control retention policies
- Data can be deleted at any time
- Enrichment can be re-run to update information

---

## Troubleshooting

### Contact Not Enriching

**Problem:** Contact status stays "Pending" for more than 5 minutes

**Solutions:**
1. Check that n8n webhook URL is configured
2. Verify contact has valid email address
3. Check system logs for errors
4. Contact support if issue persists

### Low Confidence Scores

**Problem:** Enrichment completes but confidence score is below 50

**Solutions:**
1. Verify contact email is correct
2. Check if contact has online presence
3. Try enriching again later (data sources update)
4. Manually verify and update information

### Partial Results

**Problem:** Only some fields are populated

**This is normal!** Not all contacts have all information available online.

**What to do:**
- Use what data is available
- Manually add missing information if needed
- Re-enrich periodically as data sources update

---

## Best Practices

### When to Enrich Contacts

✅ **Good times to enrich:**
- After importing new contacts
- Before CRM sync (Brevo, HubSpot)
- Before email campaigns
- Quarterly data refresh

❌ **Avoid enriching:**
- Contacts with invalid emails
- Test/dummy contacts
- Contacts you plan to delete

### Batch Enrichment

**For large lists:**
1. Select contacts in batches of 50-100
2. Wait for batch to complete before starting next
3. Monitor confidence scores
4. Review and verify high-value contacts

### Cost Management

**Enrichment costs vary by data source:**
- Average: $0.10-0.25 per contact
- Cost tracked in `enrichment_cost_estimate` field
- Review costs regularly
- Focus on high-value contacts first

---

## FAQ

### How long does enrichment take?
**10-30 seconds per contact.** Batch processing happens every 1-5 minutes.

### Can I re-enrich a contact?
**Yes!** Send the contact to n8n again. The system will update with fresh data.

### What if enrichment fails?
**Automatic retries.** The system will retry up to 3 times with exponential backoff (5, 10, 20 minutes).

### Is my data secure?
**Yes.** All webhook communication uses Bearer token authentication. Data is stored in your secure database.

### Can I see what changed?
**Yes.** Check the `enrichment_completed_at` timestamp and `enrichment_sources` field to see when and where data came from.

### What if I don't want certain data?
**Contact support.** We can configure which fields to populate and which data sources to use.

---

## Related Documentation

- **Technical Details:** See router header in `src/routers/v3/n8n_webhook_router.py`
- **Maintenance Guide:** `Documentation/Operations/n8n_enrichment_maintenance.md`
- **Integration Guide:** `Documentation/N8N_TRIGGER_FIELDS.md`
- **Work Order:** `Documentation/Work_Orders/WO-021_COMPLETE.md`

---

**Questions or Issues?**  
Contact your system administrator or check the maintenance guide for troubleshooting steps.

**Last Updated:** 2025-11-19  
**Version:** 1.0
