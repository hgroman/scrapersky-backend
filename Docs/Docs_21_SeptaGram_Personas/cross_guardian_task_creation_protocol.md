# Cross-Guardian Task Creation Protocol v1.0

**Purpose:** This document provides the authoritative standard for creating tasks between Guardian Personas (both Layer and Workflow). Adherence to this protocol ensures all inter-guardian communication is clear, actionable, traceable, and efficient.

---

### **1. When to Create a Cross-Guardian Task**

Create a task for another Guardian in the following scenarios:

*   **Urgent Issues:** A blocking problem in production or staging requires immediate attention.
*   **Cross-Layer Dependencies:** An issue identified in one layer requires analysis or action from another (e.g., a Layer 3 Router issue requires Layer 2 Schema analysis).
*   **Configuration Changes:** A Layer 5 recommendation requires implementation by a Workflow Guardian.
*   **Pattern Violations:** An architectural compliance issue is discovered and needs to be assigned for remediation.
*   **Knowledge Gaps:** A Guardian requires information or analysis from another to proceed with its own tasks.

---

### **2. Task Placement Strategy**

*   **For Workflow Guardians (WF1-WF7):** Create tasks in their dartboard when you need them to **execute a change**, make a **decision**, or **coordinate a business workflow**.
*   **For Layer Guardians (L0-L7):** Create tasks in their dartboard when you need them to **provide analysis**, answer a **compliance question**, or offer **expert pattern guidance**.

---

### **3. Task Title Templates**

Use standardized prefixes for immediate clarity.

*   **Urgent Implementation:** `URGENT: [Action] - [Brief Description]`
    *   *Example: "URGENT: Add LOG_LEVEL=DEBUG for Staging Debugging"*
*   **Cross-Layer Coordination:** `[Source] -> [Target]: [Issue]`
    *   *Example: "L5 -> WF4: Database Session Dependency Conflict"*
*   **Pattern Compliance:** `COMPLIANCE: [Pattern] Violation in [File]`
    *   *Example: "COMPLIANCE: Dependency Injection Violation in UserService"*
*   **Knowledge Request:** `QUERY: [Guardian] Analysis Needed - [Topic]`
    *   *Example: "QUERY: L2 Schema Guardian Analysis Needed - Pydantic v2 Migration"*

---

### **4. Essential Task Components**

Every task description **MUST** contain the following sections for completeness.

#### **A. Context Block**
*A quick summary to establish the situation.*
```markdown
**Issue:** [A one-line problem statement.]
**Impact:** [Who or what is affected by this issue.]
**Timeline:** [Urgency level: Immediate, High, Medium, Low]
**Requesting Guardian:** [Your Guardian Name and ID]
```

#### **B. Technical Details**
*The specific, actionable information.*
```markdown
**File(s) Affected:**
- `src/path/to/file.py` (Lines X-Y)
- `config/file.yml` (Section Z)

**Current State:** [Describe what exists now.]
**Required State:** [Describe what should exist after the fix.]
**Pattern Reference:** [Cite the specific Blueprint section or document.]
```

#### **C. Implementation Guidance**
*Provide a clear path to resolution.*
```markdown
**Code Example:**
```python
# Current (problematic)
old_pattern_here()

# Required (compliant)
new_pattern_here()
```

**Verification Steps:**
1. [How to test the change.]
2. [What to verify works correctly.]
3. [How to confirm compliance is met.]
```

#### **D. Cross-Layer Impact Assessment**
*Consider the ripple effects.*
```markdown
**Dependencies:** [List other files, components, or layers affected.]
**Breaking Changes:** [Describe any potential breaking changes.]
**Testing Required:** [Specify what needs to be validated (e.g., unit, integration).]
**Rollback Plan:** [Briefly describe how to undo the change if needed.]
```

---

### **5. Critical Tag Strategy**

Use a combination of tags for easy filtering and routing.

*   **Priority:** `urgent`, `critical`, `high`, `medium`, `low`
*   **Domain:** `configuration`, `database`, `security`, `performance`, `ui`, `testing`
*   **Workflow/Layer:** `wf1`, `wf2`... `l1`, `l2`... `cross-workflow`, `cross-layer`
*   **Component:** `docker-compose`, `settings-py`, `fastapi-router`, `pydantic-schema`

---

### **6. The Guardian Boot Note (Emergency Protocol)**

For extreme emergencies requiring action on a Guardian's next activation:

1.  Create a task in the target Guardian's dartboard.
2.  Set the title to **exactly** `[Workflow/LayerPrefix]_GUARDIAN_BOOT_NOTE`.
    *   *Example: `WF4_GUARDIAN_BOOT_NOTE`*
3.  The description **MUST** contain clear, numbered action items. The target Guardian is programmed to execute these immediately upon booting. Use this with extreme caution.

---

### **7. The "Perfect Task" Example**

This is a gold-standard example based on the `LOG_LEVEL` request.

**Title:** `URGENT: Add LOG_LEVEL=DEBUG for Staging Environment Debugging`

**Tags:** `urgent`, `debugging`, `staging`, `configuration`, `docker-compose`

**Description:**
**Issue:** Staging environment debugging requires enhanced log visibility.
**Impact:** Investigation of a critical staging issue is currently blocked.
**Timeline:** Immediate
**Requesting Guardian:** Layer 5 Config Conductor

**File(s) Affected:**
- `docker-compose.yml` (backend service environment section)
- `.env` (for the staging environment)

**Current State:** No `LOG_LEVEL` environment variable is configured.
**Required State:** A `LOG_LEVEL` variable exists, allowing a `DEBUG` override.
**Pattern Reference:** Layer 5 Blueprint Section 2.1 - Environment Variable Management

**Code Example:**
```yaml
# In docker-compose.yml backend service `environment:` block:
LOG_LEVEL: ${LOG_LEVEL:-INFO}
```

**Verification Steps:**
1. Add `LOG_LEVEL=DEBUG` to the staging `.env` file.
2. Restart the service (`docker-compose up -d backend`).
3. Confirm that `DEBUG` level logs appear in the container output (`docker-compose logs -f backend`).

**Cross-Layer Impact Assessment:**
**Dependencies:** All layers benefit from enhanced logging.
**Breaking Changes:** None. This is an additive and optional configuration.
**Testing Required:** Log output verification.
**Rollback Plan:** Remove the `LOG_LEVEL` line from `docker-compose.yml`.
