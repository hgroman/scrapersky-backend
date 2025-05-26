# Phase 1.5: Multi-Agent Vector DB Enhancement

## SQL Schema Migration for Multi-Agent Architecture

### Enhanced fix_patterns Table
```sql
-- Add multi-agent support columns to existing fix_patterns table
ALTER TABLE fix_patterns ADD COLUMN IF NOT EXISTS
  -- Agent Targeting & Access Control
  target_personas TEXT[] DEFAULT '{}', -- ['Layer1Agent', 'PatternGuardian', 'Scribe']
  knowledge_type TEXT DEFAULT 'pattern', -- 'pattern', 'convention', 'validation_rule', 'template', 'governance'
  access_permissions JSONB DEFAULT '{"read": ["all"], "write": ["PatternGuardian"], "validate": ["PatternGuardian"]}',
  
  -- Context Awareness
  context_triggers TEXT[] DEFAULT '{}', -- ['enum_creation', 'router_auth', 'service_transaction']
  agent_priority INTEGER DEFAULT 50, -- 1-100, higher = more important for agent decisions
  
  -- Validation & Governance
  validation_rules JSONB DEFAULT '{}', -- Agent-specific validation logic
  governance_level TEXT DEFAULT 'tactical', -- 'tactical', 'strategic', 'architectural'
  
  -- Memory & Learning
  agent_feedback JSONB DEFAULT '{}', -- Track how agents use this knowledge
  success_contexts TEXT[] DEFAULT '{}', -- Where this pattern worked well
  failure_contexts TEXT[] DEFAULT '{}', -- Where this pattern failed
  
  -- Versioning for Agent Memory
  knowledge_version SEMVER DEFAULT '1.0.0',
  superseded_by UUID REFERENCES fix_patterns(id),
  active_for_agents BOOLEAN DEFAULT TRUE;

-- Enhanced indexes for agent queries
CREATE INDEX IF NOT EXISTS idx_fix_patterns_target_personas 
  ON fix_patterns USING GIN (target_personas);
CREATE INDEX IF NOT EXISTS idx_fix_patterns_knowledge_type 
  ON fix_patterns (knowledge_type);
CREATE INDEX IF NOT EXISTS idx_fix_patterns_context_triggers 
  ON fix_patterns USING GIN (context_triggers);
CREATE INDEX IF NOT EXISTS idx_fix_patterns_governance_level 
  ON fix_patterns (governance_level);
CREATE INDEX IF NOT EXISTS idx_fix_patterns_agent_priority 
  ON fix_patterns (agent_priority DESC);
```

### Agent Memory Context Table
```sql
-- New table for agent working memory sessions
CREATE TABLE agent_memory_sessions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  agent_type TEXT NOT NULL, -- 'Layer1Agent', 'PatternGuardian', etc.
  dart_task_id TEXT NOT NULL,
  prd_context JSONB, -- Current PRD being worked on
  
  -- Knowledge Assembly
  retrieved_patterns UUID[] DEFAULT '{}', -- Pattern IDs pulled for this session
  active_knowledge JSONB DEFAULT '{}', -- Assembled working memory
  context_embeddings VECTOR(1536), -- Embedded context for similarity matching
  
  -- Session Tracking
  session_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  session_end TIMESTAMP WITH TIME ZONE,
  session_status TEXT DEFAULT 'active', -- 'active', 'completed', 'failed', 'escalated'
  
  -- Learning
  decisions_made JSONB DEFAULT '{}', -- What the agent decided and why
  patterns_applied UUID[] DEFAULT '{}', -- Which patterns were actually used
  outcomes JSONB DEFAULT '{}', -- Success/failure feedback
  
  FOREIGN KEY (dart_task_id) REFERENCES dart_tasks(id) -- Assuming DART task table exists
);

CREATE INDEX ON agent_memory_sessions (agent_type);
CREATE INDEX ON agent_memory_sessions (dart_task_id);
CREATE INDEX ON agent_memory_sessions (session_status);
CREATE INDEX ON agent_memory_sessions USING ivfflat (context_embeddings vector_cosine_ops);
```

### Agent Knowledge Retrieval Functions
```sql
-- Primary function for agent knowledge assembly
CREATE OR REPLACE FUNCTION get_agent_knowledge(
  agent_type TEXT,
  layer_context INTEGER DEFAULT NULL,
  task_context TEXT DEFAULT NULL,
  prd_context JSONB DEFAULT NULL,
  knowledge_types TEXT[] DEFAULT ARRAY['pattern', 'convention'],
  governance_levels TEXT[] DEFAULT ARRAY['tactical', 'strategic'],
  max_patterns INTEGER DEFAULT 20
)
RETURNS TABLE (
  pattern_id UUID,
  title TEXT,
  knowledge_type TEXT,
  priority_score FLOAT,
  relevance_score FLOAT,
  pattern_content JSONB,
  usage_guidance TEXT,
  validation_rules JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
  context_embedding VECTOR(1536);
  search_text TEXT;
BEGIN
  -- Build search context from inputs
  search_text := COALESCE(task_context, '') || ' ' || 
                 COALESCE(prd_context->>'description', '') || ' ' ||
                 CASE WHEN layer_context IS NOT NULL THEN 'layer_' || layer_context::TEXT ELSE '' END;
  
  -- Generate embedding for context (simplified - use OpenAI API in practice)
  context_embedding := array_fill(0.0, ARRAY[1536])::VECTOR(1536);
  
  RETURN QUERY
  SELECT 
    fp.id,
    fp.title,
    fp.knowledge_type,
    -- Priority scoring based on agent fit and context
    (fp.agent_priority::FLOAT / 100.0 + 
     CASE WHEN agent_type = ANY(fp.target_personas) THEN 0.5 ELSE 0.0 END +
     CASE WHEN layer_context IS NOT NULL AND layer_context = ANY(fp.layers) THEN 0.3 ELSE 0.0 END
    ) AS priority_score,
    -- Relevance scoring based on content similarity
    (fp.content_embedding <-> context_embedding) * -1 + 1 AS relevance_score,
    -- Assembled pattern content for agent consumption
    jsonb_build_object(
      'problem_description', fp.problem_description,
      'solution_steps', fp.solution_steps,
      'code_before', fp.code_before,
      'code_after', fp.code_after,
      'verification_steps', fp.verification_steps,
      'prevention_guidance', fp.prevention_guidance,
      'learnings', fp.learnings,
      'tags', fp.tags,
      'applied_count', fp.applied_count,
      'success_rate', fp.success_rate
    ) AS pattern_content,
    -- Agent-specific usage guidance
    CASE 
      WHEN agent_type = 'PatternGuardian' THEN 'Validate against: ' || fp.verification_steps
      WHEN agent_type LIKE 'Layer%Agent' THEN 'Apply within layer constraints: ' || fp.solution_steps
      WHEN agent_type = 'Scribe' THEN 'Reference for PRD: ' || fp.problem_description
      ELSE fp.solution_steps
    END AS usage_guidance,
    fp.validation_rules
  FROM fix_patterns fp
  WHERE 
    -- Agent access control
    (agent_type = ANY(fp.target_personas) OR 'all' = ANY(fp.target_personas)) AND
    fp.active_for_agents = TRUE AND
    -- Context filtering
    (layer_context IS NULL OR layer_context = ANY(fp.layers)) AND
    (knowledge_types IS NULL OR fp.knowledge_type = ANY(knowledge_types)) AND
    (governance_levels IS NULL OR fp.governance_level = ANY(governance_levels)) AND
    -- Permissions check
    fp.access_permissions->>'read' ? agent_type OR 
    fp.access_permissions->>'read' ? 'all'
  ORDER BY 
    priority_score DESC,
    relevance_score DESC,
    fp.applied_count DESC
  LIMIT max_patterns;
END;
$$;

-- Function for agent to start a working memory session
CREATE OR REPLACE FUNCTION start_agent_session(
  agent_type TEXT,
  dart_task_id TEXT,
  prd_context JSONB DEFAULT NULL,
  task_description TEXT DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
  session_id UUID;
  knowledge_assembly JSONB;
  retrieved_patterns UUID[];
BEGIN
  -- Generate session ID
  session_id := gen_random_uuid();
  
  -- Retrieve relevant knowledge for this agent and context
  SELECT 
    jsonb_agg(
      jsonb_build_object(
        'pattern_id', pattern_id,
        'title', title,
        'knowledge_type', knowledge_type,
        'priority', priority_score,
        'content', pattern_content,
        'guidance', usage_guidance
      )
    ),
    array_agg(pattern_id)
  INTO knowledge_assembly, retrieved_patterns
  FROM get_agent_knowledge(
    agent_type, 
    NULL, -- layer context
    task_description,
    prd_context
  );
  
  -- Create session record
  INSERT INTO agent_memory_sessions (
    id, agent_type, dart_task_id, prd_context,
    retrieved_patterns, active_knowledge
  ) VALUES (
    session_id, agent_type, dart_task_id, prd_context,
    retrieved_patterns, knowledge_assembly
  );
  
  RETURN session_id;
END;
$$;
```

## Agent Knowledge Templates & Examples

### Template: Layer 1 Agent Pattern
```json
{
  "title": "Standard Enum Definition Pattern",
  "knowledge_type": "convention",
  "target_personas": ["Layer1Agent", "PatternGuardian"],
  "context_triggers": ["enum_creation", "status_field_definition"],
  "governance_level": "tactical",
  "agent_priority": 95,
  "access_permissions": {
    "read": ["Layer1Agent", "PatternGuardian", "Scribe"],
    "write": ["PatternGuardian"],
    "validate": ["Layer1Agent", "PatternGuardian"]
  },
  "validation_rules": {
    "Layer1Agent": {
      "must_inherit": "(str, Enum)",
      "naming_pattern": "^[A-Z][a-zA-Z]*Status$",
      "required_values": ["New", "Queued", "Processing", "Complete", "Error", "Skipped"]
    },
    "PatternGuardian": {
      "file_location": "src/models/{source_table_name}.py",
      "database_enum_naming": "snake_case_with_layer_prefix"
    }
  },
  "pattern_content": {
    "problem_description": "Need to define status enums following ScraperSky conventions",
    "solution_steps": "1. Inherit from (str, Enum)\n2. Use WorkflowNameTitleCase naming\n3. Include standard status values\n4. Define in appropriate model file",
    "code_before": "class MyStatusEnum(Enum):\n    PENDING = 'pending'",
    "code_after": "class PageCurationStatus(str, Enum):\n    New = 'New'\n    Queued = 'Queued'\n    Processing = 'Processing'\n    Complete = 'Complete'\n    Error = 'Error'\n    Skipped = 'Skipped'"
  }
}
```

### Template: Pattern Guardian Validation Rule
```json
{
  "title": "Router Authentication Boundary Validation",
  "knowledge_type": "validation_rule", 
  "target_personas": ["PatternGuardian"],
  "context_triggers": ["router_creation", "authentication_check"],
  "governance_level": "architectural",
  "agent_priority": 99,
  "validation_rules": {
    "PatternGuardian": {
      "check_type": "security_boundary",
      "pattern": "JWT authentication must occur ONLY at router level",
      "violations": [
        "Services handling JWT tokens",
        "Database operations checking authentication",
        "Background tasks with auth logic"
      ],
      "enforcement": "BLOCK_MERGE"
    }
  }
}
```

### Template: Scribe PRD Pattern
```json
{
  "title": "Multi-Layer Workflow PRD Template",
  "knowledge_type": "template",
  "target_personas": ["Scribe"],
  "context_triggers": ["workflow_creation", "prd_authoring"],
  "governance_level": "strategic",
  "pattern_content": {
    "prd_structure": {
      "sections": ["Overview", "Layer Breakdown", "Dependencies", "Success Criteria"],
      "layer_tasks": {
        "Layer1": "Model and enum definitions",
        "Layer2": "Schema creation and validation",
        "Layer3": "Router and endpoint implementation",
        "Layer4": "Service and scheduler logic"
      },
      "dart_integration": "Each layer task must reference parent PRD task"
    }
  }
}
```

## Enhanced Marching Orders Integration

### Add to Phase 1: Enhanced Schema Setup
```python
# After basic table creation, enhance for multi-agent use
def setup_multi_agent_architecture():
    """
    Enhance basic vector DB for multi-agent architecture
    """
    print("🔧 Enhancing schema for multi-agent architecture...")
    
    # 1. Add agent-specific columns
    mcp_tool("supabase-mcp-server", "execute_sql", {
        "project_id": "ddfldwzhdhhzhxywqnyz",
        "sql": MULTI_AGENT_SCHEMA_MIGRATION
    })
    
    # 2. Create agent memory sessions table
    mcp_tool("supabase-mcp-server", "execute_sql", {
        "project_id": "ddfldwzhdhhzhxywqnyz",
        "sql": AGENT_MEMORY_SESSIONS_TABLE
    })
    
    # 3. Create agent knowledge functions
    mcp_tool("supabase-mcp-server", "execute_sql", {
        "project_id": "ddfldwzhdhhzhxywqnyz",
        "sql": AGENT_KNOWLEDGE_FUNCTIONS
    })
    
    print("✅ Multi-agent architecture ready!")

# Test multi-agent knowledge retrieval
def test_agent_knowledge_system():
    """
    Validate agent-specific knowledge retrieval works
    """
    # Test Layer 1 Agent knowledge retrieval
    layer1_knowledge = mcp_tool("supabase-mcp-server", "execute_sql", {
        "project_id": "ddfldwzhdhhzhxywqnyz",
        "sql": """
        SELECT * FROM get_agent_knowledge(
          'Layer1Agent',
          1, -- Layer 1 context
          'enum definition needed',
          NULL,
          ARRAY['pattern', 'convention'],
          ARRAY['tactical', 'strategic'],
          5
        );
        """
    })
    
    # Test Pattern Guardian knowledge retrieval
    guardian_knowledge = mcp_tool("supabase-mcp-server", "execute_sql", {
        "project_id": "ddfldwzhdhhzhxywqnyz",
        "sql": """
        SELECT * FROM get_agent_knowledge(
          'PatternGuardian',
          NULL,
          'validation needed',
          NULL,
          ARRAY['validation_rule', 'pattern'],
          ARRAY['tactical', 'strategic', 'architectural'],
          10
        );
        """
    })
    
    print(f"🧠 Layer1Agent knowledge slices: {len(layer1_knowledge)}")
    print(f"🛡️ PatternGuardian knowledge slices: {len(guardian_knowledge)}")
    
    return len(layer1_knowledge) > 0 and len(guardian_knowledge) > 0
```

### Enhanced Pattern Extraction for Multi-Agent
```python
def extract_multi_agent_pattern(fix_details, file_audit_record, dart_task_id):
    """
    Extract pattern with multi-agent metadata
    """
    # Determine which agents need this knowledge
    target_personas = determine_target_personas(fix_details, file_audit_record)
    
    # Classify knowledge type
    knowledge_type = classify_knowledge_type(fix_details)
    
    # Extract context triggers
    context_triggers = extract_context_triggers(fix_details)
    
    # Build agent-specific validation rules
    validation_rules = build_validation_rules(fix_details, target_personas)
    
    pattern_data = {
        # ... existing pattern fields ...
        
        # NEW: Multi-agent fields
        'target_personas': target_personas,
        'knowledge_type': knowledge_type,
        'context_triggers': context_triggers,
        'agent_priority': calculate_agent_priority(fix_details),
        'governance_level': determine_governance_level(fix_details),
        'validation_rules': validation_rules,
        'access_permissions': build_access_permissions(target_personas),
        'knowledge_version': '1.0.0',
        'active_for_agents': True
    }
    
    return pattern_data

def determine_target_personas(fix_details, file_audit_record):
    """
    Determine which agents should have access to this pattern
    """
    personas = []
    
    # Layer-specific agent
    layer_agent = f"Layer{file_audit_record.layer_number}Agent"
    personas.append(layer_agent)
    
    # Always include Pattern Guardian for validation
    personas.append("PatternGuardian")
    
    # Include Scribe if it's a workflow-level pattern
    if 'workflow' in fix_details.pattern_type.lower():
        personas.append("Scribe")
    
    # Include Dean if it's architectural
    if fix_details.governance_level == 'architectural':
        personas.append("Dean")
    
    return personas
```

## Summary: What This Unlocks

1. **🎯 Targeted Knowledge**: Each agent gets exactly the knowledge it needs
2. **🔒 Access Control**: Proper permissions and governance levels
3. **🧠 Working Memory**: Agents can assemble context-specific knowledge
4. **🛡️ Validation Rules**: Pattern Guardian can enforce standards automatically  
5. **📋 PRD Templates**: Scribe can use proven workflow patterns
6. **⚖️ Governance**: Dean can access architectural decision patterns

This enhancement transforms your vector DB from "pattern storage" into a **true agentic knowledge dispatch system** that enables the 10-persona architecture you envisioned. 

**Ready to implement Phase 1.5?** 🚀