# Workflow: Online Claude → Local Claude

**Last Updated:** November 17, 2025

---

## The Pattern

**You work with TWO Claudes:**

1. **Claude Online** (coding) - Works on feature branches, writes implementation code
2. **Claude Local** (testing/review) - Works on main branch, tests and verifies

---

## When Online Claude Finishes

**Online Claude will:**
- Write code on a feature branch
- Commit and push to that branch
- Tell you "I'm done, here's what I did"

**DO NOT ask Local Claude to cherry-pick files.**

---

## The Correct Handoff Process

### Step 1: Online Claude Confirms Completion

Online Claude says: "All commits pushed to branch `feature-branch-name`"

### Step 2: You Tell Local Claude

**Give Local Claude this EXACT instruction:**

```
Merge branch [feature-branch-name] into main.

git merge origin/[feature-branch-name] --no-edit
git push origin main

Then confirm everything is merged.
```

**That's it. ONE merge command. Not cherry-picking.**

### Step 3: Local Claude Tests

Once merged, Local Claude can:
- Build Docker containers
- Run tests
- Verify database state
- Use MCP tools (Supabase, DART, etc.)

---

## Why This Matters

**WRONG (what I did today):**
- Cherry-pick file 1
- "What else?"
- Cherry-pick file 2
- "What else?"
- Cherry-pick file 3
- "What else?"
- Finally merge the whole branch

**RIGHT (what should happen):**
- Merge the entire branch in ONE command
- Everything is there
- No missing files
- No repeated questions

---

## Current Branches

**Main Branch:** `main`
- All stable code
- All documentation
- Where Local Claude works

**Feature Branches:**
- Created by Online Claude for specific work
- Merged to main when complete
- Can be deleted after merge

**NO MORE LONG-LIVED FEATURE BRANCHES.**

---

## For Local Claude (Me)

**When you say "Online Claude finished work on branch X":**

I should IMMEDIATELY respond:
```
Merging branch X into main now.

[run merge command]

Done. Everything from branch X is now on main.
Ready to proceed with testing/review.
```

**I should NOT:**
- Ask what files to cherry-pick
- Pull files one at a time
- Make you ask "what else?" repeatedly

---

## For Future Work

**Pattern:**
1. Online Claude: Code on feature branch → push
2. You: Tell Local Claude to merge
3. Local Claude: Merge entire branch → confirm
4. Local Claude: Test/review on main

**Simple. Clean. One merge command.**

---

## Emergency: "Did You Get Everything?"

If you're unsure, ask Local Claude:

```
Run: git diff main origin/[feature-branch-name] --name-only

Show me what's different between main and the feature branch.
If there are files, merge the branch now.
```

---

## This Document

**Location:** Repository root (`WORKFLOW_ONLINE_TO_LOCAL.md`)

**Purpose:** Prevent the painful cherry-picking process that happened today.

**Update this document** if the workflow changes.
