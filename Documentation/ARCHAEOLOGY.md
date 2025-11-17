# Code Archaeology Guide
**Purpose:** How to investigate code history  
**Last Updated:** November 17, 2025

---

## Essential Git Commands

### Find when a file was created
```bash
git log --diff-filter=A --follow -- path/to/file.py
```

### Find when a file was deleted
```bash
git log --all --full-history -- path/to/file.py
```

### Find all commits touching a file
```bash
git log --oneline --follow -- path/to/file.py
```

### Find when a function was added/removed
```bash
git log -p -S "function_name" -- path/to/file.py
```

### Find who last modified each line
```bash
git blame path/to/file.py
```

### Find commits by message keyword
```bash
git log --all --grep="sitemap"
```

### Find commits in a date range
```bash
git log --after="2025-09-01" --before="2025-09-10"
```

### See what changed in a commit
```bash
git show <commit-hash>
```

---

## Investigation Workflows

### Scenario: "Why does this code exist?"

1. **Find who added it:**
   ```bash
   git blame src/services/some_service.py
   ```

2. **Get commit details:**
   ```bash
   git show <commit-hash>
   ```

3. **Check for related incidents:**
   ```bash
   grep -r "<commit-hash>" Documentation/INCIDENTS/
   ```

4. **Check for decisions:**
   ```bash
   grep -r "<commit-hash>" Documentation/DECISIONS/
   ```

---

### Scenario: "When was this feature removed?"

1. **Find commits mentioning it:**
   ```bash
   git log --all -S "feature_name"
   ```

2. **See what was removed:**
   ```bash
   git show <commit-hash>
   ```

3. **Check commit message:**
   Look for reasoning in commit message

4. **Check decision log:**
   ```bash
   ls Documentation/DECISIONS/ | grep <date>
   ```

---

### Scenario: "Has this ever worked?"

1. **Find related commits:**
   ```bash
   git log --all --grep="feature"
   ```

2. **Check for incidents:**
   ```bash
   ls Documentation/INCIDENTS/ | grep feature
   ```

3. **Check test history:**
   ```bash
   git log -- tests/test_feature.py
   ```

4. **Try old version:**
   ```bash
   git checkout <old-commit>
   # Test manually
   git checkout main
   ```

---

## Real Examples

### Example 1: Sitemap Job Processor

**Question:** When was it disabled?
```bash
git log -p -S "DISABLED as per new PRD" -- src/services/sitemap_scheduler.py
```
**Result:** Commit 0aaaad6, Sept 9, 2025

**Question:** Why was it disabled?
```bash
git show 0aaaad6
```
**Commit message:** "fix: Commit status updates and improve transaction handling"  
**Comment in code:** "This entire workflow is being replaced by the modern, SDK-based sitemap_import_scheduler"

**Question:** Was replacement implemented?
```bash
grep -r "job_type.*sitemap" src/services/sitemap_import_scheduler.py
```
**Result:** No matches - processes SitemapFile records, not Job records  
**Conclusion:** Replacement was NOT implemented

---

### Example 2: DomainToSitemapAdapterService

**Question:** When was it created?
```bash
git log --diff-filter=A --follow -- src/services/domain_to_sitemap_adapter_service.py
```
**Result:** Commit d522109, April 24, 2025

**Question:** Was it ever deleted?
```bash
git log --all --full-history -- src/services/domain_to_sitemap_adapter_service.py | grep -i delete
```
**Result:** Commit 79f145e, June 28, 2025 - "Deleted DomainToSitemapAdapterService"

**Question:** When was it restored?
```bash
git log --diff-filter=A --follow -- src/services/domain_to_sitemap_adapter_service.py
```
**Result:** Multiple creation dates - restored after deletion

---

## Tips

1. **Always check commit messages** - They often explain "why"
2. **Look for related files** - Changes often span multiple files
3. **Check test files** - Tests show intended behavior
4. **Read PR descriptions** - More context than commit messages
5. **Check INCIDENTS/** - Past failures explain current code
6. **Check DECISIONS/** - Architectural choices explained

---

## Common Pitfalls

❌ **Don't assume code is correct** - It might be a bug  
❌ **Don't assume code is used** - It might be dead code  
❌ **Don't assume recent = better** - Regressions happen  
✅ **Do verify with tests** - Run them to confirm behavior  
✅ **Do check multiple sources** - Git + docs + incidents  
✅ **Do ask "why"** - Every line has a reason

---

## Investigation Checklist

When investigating unfamiliar code:

- [ ] Run `git blame` to see who wrote it
- [ ] Check commit message for context
- [ ] Search INCIDENTS/ for related problems
- [ ] Search DECISIONS/ for architectural choices
- [ ] Check if tests exist
- [ ] Verify code is actually used (grep for calls)
- [ ] Check for TODOs or FIXMEs
- [ ] Look for related files that changed together

---

**For more investigation techniques:**
- [INCIDENTS/](./INCIDENTS/) - Real investigation examples
- [PATTERNS.md](./PATTERNS.md) - Common patterns to recognize
- [DECISIONS/](./DECISIONS/) - Why things are the way they are
