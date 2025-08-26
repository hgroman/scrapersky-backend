# Work Order Sample - Category-Based Certification

## Example Work Order Structure

**Work Order ID**: WO-2025-0823-001  
**Persona Type**: Test Sentinel v1.8  
**Mission**: Database schema validation and stub prevention audit  

### Required Certification Categories

```json
{
  "categories": [
    "stub-prevention",
    "docker-testing", 
    "database-analysis",
    "ai-partner-safety"
  ],
  "priority": "mission-critical",
  "context": "Production database migration with zero-tolerance for stub files"
}
```

### Category-Specific Knowledge Requirements

**stub-prevention**:
- Anti-Stub Covenant four-item hierarchy
- August 17, 2025 Stub Catastrophe details
- Emergency response protocols for stub creation attempts

**docker-testing**:
- Docker-first testing protocols
- Environment safety procedures
- Container isolation requirements

**database-analysis**:
- Schema validation patterns
- Migration safety protocols
- Data integrity verification

**ai-partner-safety**:
- WF7 Recovery Journal lessons
- Multi-AI coordination protocols
- Handoff procedures and documentation

## Proposed Certification Flow

1. **Work Order Assignment**: Persona receives work order with categories
2. **Boot Sequence Execution**: Persona loads documents relevant to categories
3. **Certification Registration**: 
   ```
   Persona → Certification Authority: 
   "Request certification for categories: [stub-prevention, docker-testing, database-analysis, ai-partner-safety]"
   ```
4. **Category-Specific Testing**: Authority queries knowledge for each category
5. **Adaptive Verification**: Authority probes deeper on any failed responses
6. **Certification Token**: Authority issues token only after 100% accuracy on all categories
7. **Operational Authorization**: Persona proceeds with mission-critical work

## Benefits of Category-Based Approach

- **Narrow Focus**: Persona only needs to master relevant knowledge for the specific task
- **Optimal Context**: Prevents knowledge bloat and maintains sharp focus
- **Targeted Testing**: Certification authority can use category-specific question sets
- **Scalable**: Same system works for different work order types and persona specializations
