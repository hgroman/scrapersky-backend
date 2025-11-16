# ScraperAPI Cost Control

**Purpose:** Prevent cost overruns when using ScraperAPI for web scraping operations.

**Background:** In September 2025, ScraperSky experienced a cost crisis where a single domain operation consumed $50 in credits instead of the expected $0.001-$0.005. This was caused by unauthorized premium features being enabled by default.

**Outcome:** 99.998% cost reduction achieved through strict cost controls.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [The Cost Crisis (What Happened)](#the-cost-crisis-what-happened)
3. [Cost Controls Implemented](#cost-controls-implemented)
4. [Configuration](#configuration)
5. [Cost Estimation](#cost-estimation)
6. [Monitoring and Alerts](#monitoring-and-alerts)
7. [Best Practices](#best-practices)

---

## Quick Reference

### Safe Configuration (Default)

```bash
# .env
SCRAPER_API_ENABLE_PREMIUM=false         # Default: disabled
SCRAPER_API_ENABLE_JS_RENDERING=false    # Default: disabled
SCRAPER_API_ENABLE_GEOTARGETING=false    # Default: disabled
SCRAPER_API_MAX_RETRIES=1                # Reduced from 3
SCRAPER_API_COST_CONTROL_MODE=true       # Enable monitoring
```

**Cost:** 1 credit per request (~$0.001)

### When to Enable Premium Features

**ONLY enable premium features if:**
1. Business justification documented
2. Budget approved for increased costs
3. Testing verified cost impact
4. Monitoring configured

**Cost Impact:**
- Basic (default): 1 credit
- Premium: 5-10x multiplier
- JS Rendering: 10-25x multiplier
- Geotargeting: 2-3x multiplier
- **Combined:** 150x multiplier (1 credit → 150 credits)

---

## The Cost Crisis (What Happened)

### Incident Summary

**Date:** September 6, 2025
**Impact:** CRITICAL - $50 wasted on single domain
**Potential Impact:** $450,000-$480,000 if scaled to 10,000 domains

### Root Cause

Previous AI implementation enabled all expensive ScraperAPI options by default:

**BEFORE (Expensive - Unauthorized):**
```python
params = {
    "premium": "true",           # 5-10x cost multiplier - ALWAYS ON
    "render": "true",           # 10-25x cost multiplier - FORCED
    "country_code": "us",       # 2-3x cost multiplier - UNAUTHORIZED
    "device_type": "desktop",   # 1.5-2x cost multiplier - UNAUTHORIZED
}
# Combined multiplier: ~150x base cost
# Single request: 46,905 credits (~$50)
```

**AFTER (Cost-Controlled):**
```python
params = {
    "api_key": self.api_key,
    "url": url,
    "render": "false",  # Disabled by default
}

# Premium features only if explicitly enabled via environment variables
if getenv('SCRAPER_API_ENABLE_PREMIUM', 'false').lower() == 'true':
    params["premium"] = "true"

# Single request: 1 credit (~$0.001)
```

### Impact

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| Credits per Request | 46,905 | 1 | 99.998% |
| Cost per Domain | ~$50 | ~$0.001 | 99.998% |
| Cost Multipliers | 150x | 1x | 150x → 1x |

**Financial Protection Achieved:**
- Single domain: $49.999 saved
- 100 domains: $4,999 saved
- 1,000 domains: $49,999 saved
- 10,000 domains: $499,999 saved

---

## Cost Controls Implemented

### Default: Minimal Cost

**All expensive features disabled by default:**

```python
# src/services/scraper_api_service.py
params = {
    "api_key": self.api_key,
    "url": url,
    "render": "false"  # JavaScript rendering OFF
}

# Premium features require explicit opt-in
# NO premium mode
# NO geotargeting
# NO device simulation
# Minimal retries (1 instead of 3)
```

### Opt-In for Premium Features

**Environment Variable Controls:**

```python
# Premium mode (5-10x cost)
if os.getenv('SCRAPER_API_ENABLE_PREMIUM', 'false').lower() == 'true':
    params["premium"] = "true"

# JavaScript rendering (10-25x cost)
if render_js and os.getenv('SCRAPER_API_ENABLE_JS_RENDERING', 'false').lower() == 'true':
    params["render"] = "true"

# Geotargeting (2-3x cost)
if os.getenv('SCRAPER_API_ENABLE_GEOTARGETING', 'false').lower() == 'true':
    params["country_code"] = os.getenv('SCRAPER_API_COUNTRY_CODE', 'us')

# Device type (1.5-2x cost)
if os.getenv('SCRAPER_API_ENABLE_DEVICE_TYPE', 'false').lower() == 'true':
    params["device_type"] = os.getenv('SCRAPER_API_DEVICE_TYPE', 'desktop')
```

**Key Principle:** All expensive features opt-in, never opt-out.

---

## Configuration

### Environment Variables

**Required:**
```bash
SCRAPER_API_KEY=your_api_key_here
```

**Cost Control (Recommended Defaults):**
```bash
# Premium Features (disabled by default)
SCRAPER_API_ENABLE_PREMIUM=false
SCRAPER_API_ENABLE_JS_RENDERING=false
SCRAPER_API_ENABLE_GEOTARGETING=false
SCRAPER_API_ENABLE_DEVICE_TYPE=false

# Retry Control
SCRAPER_API_MAX_RETRIES=1  # Reduced from 3 to minimize repeated costs

# Cost Monitoring
SCRAPER_API_COST_CONTROL_MODE=true  # Enable monitoring and alerts
```

**Optional (If Premium Features Needed):**
```bash
# Geotargeting options
SCRAPER_API_COUNTRY_CODE=us  # Only if ENABLE_GEOTARGETING=true

# Device simulation
SCRAPER_API_DEVICE_TYPE=desktop  # Only if ENABLE_DEVICE_TYPE=true
```

### Example: Safe Production Configuration

```bash
# .env (Production)
SCRAPER_API_KEY=prod_api_key_here
SCRAPER_API_ENABLE_PREMIUM=false
SCRAPER_API_ENABLE_JS_RENDERING=false
SCRAPER_API_ENABLE_GEOTARGETING=false
SCRAPER_API_ENABLE_DEVICE_TYPE=false
SCRAPER_API_MAX_RETRIES=1
SCRAPER_API_COST_CONTROL_MODE=true
```

**Expected Cost:** 1 credit per request (~$0.001)

### Example: Premium Configuration (Business Approved)

```bash
# .env (Premium - REQUIRES BUSINESS APPROVAL)
SCRAPER_API_KEY=prod_api_key_here
SCRAPER_API_ENABLE_PREMIUM=true      # ← 5-10x cost increase
SCRAPER_API_ENABLE_JS_RENDERING=true # ← 10-25x cost increase
SCRAPER_API_ENABLE_GEOTARGETING=false
SCRAPER_API_ENABLE_DEVICE_TYPE=false
SCRAPER_API_MAX_RETRIES=1
SCRAPER_API_COST_CONTROL_MODE=true
SCRAPER_API_COUNTRY_CODE=us
```

**Expected Cost:** 50-250 credits per request (~$0.05-$0.25)

**⚠️ WARNING:** Only use premium features if:
- Business need documented
- Budget approved for 50-250x cost increase
- Monitoring configured
- Testing verified cost impact

---

## Cost Estimation

### Base Costs

**ScraperAPI Pricing (approximate):**
- 1 credit = $0.001
- Basic request (no options): 1 credit
- API key included with all requests (no extra cost)

### Cost Multipliers

**Premium Features:**

| Feature | Multiplier | Example Cost |
|---------|------------|--------------|
| Basic (default) | 1x | 1 credit ($0.001) |
| Premium mode | 5-10x | 5-10 credits ($0.005-$0.01) |
| JavaScript rendering | 10-25x | 10-25 credits ($0.01-$0.025) |
| Geotargeting | 2-3x | 2-3 credits ($0.002-$0.003) |
| Device simulation | 1.5-2x | 1.5-2 credits ($0.0015-$0.002) |

**Combined Multipliers:**
- Premium + JS rendering: 50-250x (50-250 credits, $0.05-$0.25)
- All features combined: 150-1500x (150-1500 credits, $0.15-$1.50)

### Calculating Request Cost

```python
def estimate_request_cost(
    premium: bool = False,
    render_js: bool = False,
    geotargeting: bool = False,
    device_type: bool = False
) -> tuple[int, float]:
    """Estimate ScraperAPI request cost."""

    base_credits = 1
    multiplier = 1.0

    if premium:
        multiplier *= 7.5  # Average 5-10x
    if render_js:
        multiplier *= 17.5  # Average 10-25x
    if geotargeting:
        multiplier *= 2.5  # Average 2-3x
    if device_type:
        multiplier *= 1.75  # Average 1.5-2x

    estimated_credits = int(base_credits * multiplier)
    estimated_cost = estimated_credits * 0.001

    return estimated_credits, estimated_cost

# Example: Basic request
credits, cost = estimate_request_cost()
# → 1 credit, $0.001

# Example: Premium + JS rendering
credits, cost = estimate_request_cost(premium=True, render_js=True)
# → 131 credits, $0.131

# Example: All features
credits, cost = estimate_request_cost(
    premium=True,
    render_js=True,
    geotargeting=True,
    device_type=True
)
# → 575 credits, $0.575
```

---

## Monitoring and Alerts

### Real-Time Cost Monitoring

**Implementation:** `src/services/scraper_api_service.py`

```python
class CreditUsageMonitor:
    """Monitor ScraperAPI credit usage in real-time."""

    def log_request(
        self,
        url: str,
        premium: bool = False,
        render_js: bool = False,
        geotargeting: bool = False,
        device_type: bool = False
    ) -> int:
        """Log request and return estimated cost."""

        # Calculate estimated credits
        estimated_credits = self._estimate_credits(
            premium, render_js, geotargeting, device_type
        )

        # Log all requests
        logger.info(
            f"SCRAPER_COST_MONITOR: "
            f"URL={url}, "
            f"Est_Credits={estimated_credits}, "
            f"Premium={premium}, "
            f"RenderJS={render_js}"
        )

        # Alert on high-cost requests
        if estimated_credits >= 10:
            logger.error(
                f"SCRAPER_COST_ALERT: HIGH_COST_REQUEST "
                f"Est_Credits={estimated_credits}"
            )

        return estimated_credits
```

### Log Monitoring

**Example Log Output:**

```
# Safe request (1 credit)
SCRAPER_COST_MONITOR: URL=https://example.com, Est_Credits=1, Premium=False, RenderJS=False

# High-cost request (150 credits)
SCRAPER_COST_ALERT: HIGH_COST_REQUEST Est_Credits=150
SCRAPER_COST_MONITOR: URL=https://example.com, Est_Credits=150, Premium=True, RenderJS=True
```

### Alert Thresholds

**Alerting Levels:**
- **INFO:** All requests (baseline logging)
- **WARNING:** Estimated cost ≥ 5 credits ($0.005)
- **ERROR:** Estimated cost ≥ 10 credits ($0.01)
- **CRITICAL:** Cumulative cost ≥ 1000 credits ($1.00) in single batch

---

## Best Practices

### 1. Always Use Safe Defaults

✅ **DO:**
```python
# Start with minimal cost
params = {"api_key": key, "url": url, "render": "false"}
```

❌ **DON'T:**
```python
# Don't enable premium features by default
params = {"premium": "true", "render": "true"}  # ← Expensive!
```

### 2. Test Cost Impact Before Scaling

✅ **DO:**
```python
# Test with 1-5 domains first
test_domains = domains[:5]
for domain in test_domains:
    cost = scraper.scrape(domain)
    logger.info(f"Test cost: {cost} credits")

# Verify expected cost before scaling to thousands
```

❌ **DON'T:**
```python
# Don't scale without testing
for domain in all_10000_domains:  # ← Could cost $50,000+
    scraper.scrape(domain)
```

### 3. Monitor Cumulative Costs

✅ **DO:**
```python
total_credits = 0
for domain in domains:
    credits = scraper.scrape(domain)
    total_credits += credits

    if total_credits >= 1000:  # Stop at $1
        logger.warning("Budget limit reached")
        break
```

### 4. Document Business Justification for Premium Features

**Before enabling premium features:**

1. **Document Why:** What business need requires premium features?
2. **Calculate Cost Impact:** What's the total cost increase?
3. **Get Approval:** Budget owner approves increased spend
4. **Test First:** Verify cost estimate with 1-5 test requests
5. **Monitor:** Set up alerts for actual vs expected cost

### 5. Use Environment-Specific Configuration

```bash
# Development (.env.dev)
SCRAPER_API_ENABLE_PREMIUM=false  # Safe for testing
SCRAPER_API_MAX_RETRIES=1

# Production (.env.prod)
SCRAPER_API_ENABLE_PREMIUM=false  # Safe by default
SCRAPER_API_MAX_RETRIES=1
SCRAPER_API_COST_CONTROL_MODE=true  # Monitoring enabled

# Premium (only if approved)
SCRAPER_API_ENABLE_PREMIUM=true  # REQUIRES BUSINESS APPROVAL
SCRAPER_API_COST_CONTROL_MODE=true  # Must monitor
```

---

## Related Documentation

- **Incident Postmortem:** `Docs/Docs_44_ScraperAPI-Cost-Crisis-Postmortem/POSTMORTEM_ScraperAPI-Credit-Waste-Emergency-Response.md`
- **Investigation Work Order:** `Docs/Docs_44_ScraperAPI-Cost-Crisis-Postmortem/WO-20250906-003_CRITICAL-ScraperAPI-Credit-Waste-Investigation.md`
- **Service Implementation:** `src/services/scraper_api_service.py`

---

## Summary: ScraperAPI Cost Control Checklist

**Before using ScraperAPI:**
- [ ] Environment variables configured (all premium features = false)
- [ ] Cost monitoring enabled (`SCRAPER_API_COST_CONTROL_MODE=true`)
- [ ] Test with 1-5 domains first
- [ ] Verify expected cost (should be 1 credit per request)

**Before enabling premium features:**
- [ ] Business justification documented
- [ ] Budget approved for cost increase
- [ ] Cost impact calculated (premium = 50-250x base cost)
- [ ] Testing completed with small batch
- [ ] Monitoring and alerts configured

**During operations:**
- [ ] Monitor logs for `SCRAPER_COST_MONITOR` entries
- [ ] Alert on `SCRAPER_COST_ALERT` warnings
- [ ] Track cumulative credits per batch
- [ ] Verify actual cost matches estimates

**Remember:** Default configuration (all premium features disabled) costs 1 credit per request (~$0.001). Enabling all features costs 150-1500x more (~$0.15-$1.50 per request).

**The Golden Rule:** All expensive features opt-in, never opt-out.
