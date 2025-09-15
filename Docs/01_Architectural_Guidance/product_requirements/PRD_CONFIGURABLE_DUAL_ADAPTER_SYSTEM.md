# PRD: Configurable Dual Adapter System
**Product:** ScraperSky Workflow Automation
**Date:** 2025-09-14
**Version:** 1.0
**Author:** Claude (The Architect)

## Problem Statement

ScraperSky's current pipeline requires **manual intervention** at every workflow stage. While this ensures quality control, it creates operational bottlenecks and prevents automated high-throughput processing. The system needs **configurable automation** that maintains quality while enabling systematic processing.

## Vision

Transform ScraperSky from a manual-only system into a **dual-mode platform** where operations teams can configure each workflow stage to run in:
- **Manual Mode**: Human-curated quality control (current behavior)
- **Auto Mode**: AI-driven automatic progression based on quality thresholds
- **Hybrid Mode**: Auto-process high-confidence items, manual review for edge cases

## Success Metrics

- **Throughput**: 10x increase in processing volume for auto-mode workflows
- **Quality**: Maintain >95% quality scores for auto-selected items
- **Operational Efficiency**: 80% reduction in manual intervention time
- **Control**: Zero unintended auto-processing (strict configuration controls)

## Core Requirements

### 1. Workflow Configuration System

#### 1.1 Configuration Model
```sql
CREATE TABLE workflow_automation_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_name VARCHAR(50) NOT NULL, -- WF3, WF4, WF5, WF6, WF7
    mode VARCHAR(20) NOT NULL,          -- manual, auto, hybrid
    auto_threshold DECIMAL(3,2),        -- 0.60 = 60% confidence minimum
    quality_criteria JSONB,             -- Specific quality rules per workflow
    enabled BOOLEAN DEFAULT false,      -- Safety: explicit activation required
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 1.2 Per-Workflow Configuration
- **WF2 (Places Deep Scan)**: Auto-select based on Google rating, review count, business verification status, place types priority
- **WF3 (Local Business)**: Auto-select based on Google Maps rating, review count, completeness
- **WF4 (Domain)**: Auto-select based on domain authority, SSL status, response time
- **WF5 (Sitemap)**: Auto-select based on URL count, structure quality, accessibility
- **WF6 (Pages)**: Auto-select based on Honeybee confidence, page type priority
- **WF7 (Page Processing)**: Auto-select based on contact signal strength, page quality

### 2. Enhanced Dual Adapter Logic

#### 2.1 Current Behavior (Manual Only)
```python
# User Action Required
if request.status == Selected:
    item.processing_status = Queued
```

#### 2.2 Enhanced Behavior (Configurable)
```python
# Check configuration for this workflow
config = await get_workflow_config(workflow_name)

if config.mode == "manual":
    # Current behavior - require user selection
    if request.status == Selected:
        item.processing_status = Queued

elif config.mode == "auto":
    # Auto-mode - evaluate quality and auto-select
    quality_score = await evaluate_quality(item, config.quality_criteria)
    if quality_score >= config.auto_threshold:
        item.curation_status = Selected
        item.processing_status = Queued
        item.auto_selected = True
        item.quality_score = quality_score

elif config.mode == "hybrid":
    # Hybrid - auto-process high confidence, manual for others
    quality_score = await evaluate_quality(item, config.quality_criteria)
    if quality_score >= config.auto_threshold:
        item.curation_status = Selected
        item.processing_status = Queued
        item.auto_selected = True
    # Else: leave for manual review
```

### 3. Quality Evaluation Framework

#### 3.1 Per-Workflow Quality Criteria

**WF2 - Places Deep Scan Quality:**
```json
{
  "min_rating": 4.0,
  "min_review_count": 5,
  "priority_place_types": ["restaurant", "store", "hospital", "school"],
  "required_business_status": "OPERATIONAL",
  "exclude_place_types": ["cemetery", "funeral_home"],
  "max_address_distance_km": 50
}
```

**WF3 - Local Business Quality:**
```json
{
  "min_rating": 4.0,
  "min_review_count": 10,
  "required_fields": ["phone", "address", "website"],
  "blacklist_keywords": ["permanently closed", "temporarily closed"]
}
```

**WF4 - Domain Quality:**
```json
{
  "min_domain_authority": 30,
  "ssl_required": true,
  "max_response_time_ms": 3000,
  "exclude_patterns": ["parked", "construction", "coming-soon"]
}
```

**WF5 - Sitemap Quality:**
```json
{
  "min_url_count": 10,
  "max_url_count": 50000,
  "required_sections": ["contact", "about"],
  "format_compliance": 0.9
}
```

**WF6 - Page Creation Quality (Honeybee):**
```json
{
  "min_confidence": 0.6,
  "priority_types": ["CONTACT_ROOT", "CAREER_CONTACT", "LEGAL_ROOT"],
  "max_path_depth": 3,
  "exclude_low_value": true
}
```

### 4. Frontend Configuration Interface

#### 4.1 Workflow Dashboard
```
Workflow Automation Control Panel
┌─────────────────────────────────────────────────┐
│ WF3: Local Business → Domain                    │
│ Mode: [Manual ▼] [Auto] [Hybrid]               │
│ Auto Threshold: [75%] ────────○────── 100%     │
│ Status: ✅ Active (processing 45 items/hour)    │
│ Quality: 98.2% ✅                               │
│ [Configure Rules] [View Activity]              │
├─────────────────────────────────────────────────┤
│ WF4: Domain → Sitemap Analysis                  │
│ Mode: [Manual] [Auto ▼] [Hybrid]               │
│ Auto Threshold: [60%] ──○────────────── 100%   │
│ Status: ⚠️  Paused (manual override)            │
│ Quality: 94.1% ✅                               │
│ [Configure Rules] [View Activity]              │
└─────────────────────────────────────────────────┘
```

#### 4.2 Rule Configuration Interface
```
WF3: Local Business Quality Rules
┌─────────────────────────────────────────────────┐
│ Minimum Google Rating: [4.0] ⭐                │
│ Minimum Reviews: [10] 💬                       │
│ Required Fields:                                │
│ ☑️ Phone Number  ☑️ Address  ☑️ Website        │
│ ☑️ Business Hours                               │
│                                                 │
│ Exclusion Keywords:                             │
│ • permanently closed                            │
│ • temporarily closed                            │
│ • out of business                               │
│ [+ Add Keyword]                                 │
│                                                 │
│ [Test Rules] [Save Configuration]              │
└─────────────────────────────────────────────────┘
```

### 5. Safety and Control Features

#### 5.1 Circuit Breakers
- **Quality Monitoring**: Auto-pause if quality drops below threshold
- **Volume Limits**: Maximum items per hour per workflow
- **Error Rate Limits**: Auto-pause if error rate exceeds 5%

#### 5.2 Override Controls
- **Emergency Stop**: Instant pause for all auto-processing
- **Manual Override**: Force manual review for specific items
- **Rollback Capability**: Revert auto-decisions within 24 hours

#### 5.3 Audit Trail
- **Decision Log**: Track all auto-selection decisions with reasoning
- **Quality Metrics**: Historical performance tracking
- **User Attribution**: Who enabled/disabled auto-mode when

## Technical Implementation Plan

### Phase 1: Configuration Infrastructure (Week 1)
1. **Database Schema**: Create workflow_automation_config table
2. **Config Service**: CRUD operations for workflow configuration
3. **Config API**: REST endpoints for frontend integration

### Phase 2: Enhanced Dual Adapters (Week 2-3)
1. **Quality Evaluation Engine**: Implement per-workflow quality assessment
2. **Enhanced Dual Adapter Logic**: Update all 6 dual adapters (WF2-WF7)
3. **Safety Controls**: Circuit breakers and override mechanisms

**Technical Note: WF2 Deep Scan Status Field**
- The `places_staging.deep_scan_status` field was recently fixed to prevent auto-queuing
- Current behavior: `default=None` ensures manual curation required
- Auto-mode implementation: Set `deep_scan_status='Queued'` when quality criteria met
- Field values: `NULL` (manual review needed), `Queued`, `Processing`, `Completed`, `Error`

### Phase 3: Frontend Controls (Week 4)
1. **Configuration Dashboard**: Workflow automation control panel
2. **Rule Builder**: Quality criteria configuration interface
3. **Monitoring Dashboard**: Real-time activity and quality metrics

### Phase 4: Testing and Rollout (Week 5-6)
1. **A/B Testing**: Compare auto vs manual processing quality
2. **Gradual Rollout**: Enable auto-mode for one workflow at a time
3. **Performance Tuning**: Optimize quality evaluation algorithms

## Risk Mitigation

### Quality Risks
- **Mitigation**: Extensive testing, gradual rollout, quality monitoring
- **Fallback**: Automatic reversion to manual mode on quality degradation

### Operational Risks
- **Mitigation**: Circuit breakers, override controls, audit trails
- **Fallback**: Emergency stop functionality, manual override capability

### Technical Risks
- **Mitigation**: Comprehensive testing, staged deployment, rollback plans
- **Fallback**: Configuration disable switches, database rollback procedures

## Success Criteria

### MVP Success (Phase 1-2)
- [ ] All 6 workflows have configurable auto/manual modes (WF2-WF7)
- [ ] Quality evaluation framework operational
- [ ] Safety controls prevent runaway automation

### Full Success (Phase 3-4)
- [ ] Operations team can configure workflows via frontend
- [ ] Auto-mode achieves 10x throughput improvement
- [ ] Quality maintains >95% for auto-selected items
- [ ] Zero incidents of uncontrolled automation

## Long-term Vision

Transform ScraperSky into a **self-optimizing pipeline** where:
- AI learns optimal quality thresholds from user corrections
- Quality criteria automatically adjust based on domain expertise
- Pipeline automatically scales processing based on data quality
- Operations team focuses on exception handling rather than routine processing

This configurable dual adapter system positions ScraperSky as both a **precision manual tool** and a **high-throughput automation platform**, providing the flexibility to match operational needs with business requirements.