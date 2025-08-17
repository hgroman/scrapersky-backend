# Git Status Diagnostics Guide

**Purpose:** Use git status as system health monitor

## Health Indicators

### 🟢 Healthy Patterns
- **Post-Crisis Learning:** 20-50 files, structured response
- **Active Development:** <20 uncommitted, regular commits
- **Documentation Balance:** 3:1 doc:code ratio

### 🟡 Warning Patterns  
- **Analysis Paralysis:** 50-80 files uncommitted
- **Documentation Overwhelm:** 5:1 doc:code ratio
- **Crisis Markers:** URGENT/CRITICAL in filenames

### 🔴 Crisis Patterns
- **System Breakdown:** 80+ files, no commits for days
- **Framework Abandonment:** Empty directories with plans
- **Panic Mode:** BROKEN/EMERGENCY markers

## Diagnostic Commands

```bash
# File count check
git status --short | wc -l

# Doc:code ratio
git status --short | grep -E "\.md$" | wc -l
git status --short | grep -E "\.(py|js|ts)$" | wc -l

# Crisis markers
git status | grep -E "CRITICAL|URGENT|BROKEN|EMERGENCY"

# Age analysis
find . -name "*.md" -mtime +10 | wc -l
```

## Recovery Protocols

| Pattern | Action |
|---------|--------|
| 80+ files | STOP - Commit or defer |
| 7:1 ratio | STOP - Implement before documenting |
| Crisis markers | Address immediately or archive |