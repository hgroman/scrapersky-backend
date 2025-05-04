Below is a **concise** but **complete** set of instructions to **rip out tenant checks** (while **keeping** JWT and the existing tenant-related columns/tables) so that everything defaults to a single “placeholder tenant” behind the scenes. After that, I provide a **template** prompt you can feed into Claude (or any other AI) so it knows exactly how to systematically remove references from your code.

---

# **Part A: High-Level Strategy**

1. **Keep All Columns/Tables**: You will **not** drop or rename your tenant/role/feature tables in the database; you just won’t enforce them in the backend code.
2. **Keep JWT**: You want to remain able to authenticate users with a token. That’s still valid – no changes needed to your JWT logic for now.
3. **Remove or Neutralize Tenant Checks**:
   - Anywhere the code does `select(Tenant)` or tries to create a missing tenant → **remove** or **comment out** that logic.
   - Anywhere the code does `if tenant not found → fail` → remove or set a default.
   - If the code depends on `tenant_id` from a user object, default it to some stable UUID (e.g., `"550e8400-e29b-41d4-a716-446655440000"`) **without** verifying it in the DB.
4. **Remove or Neutralize Feature/RBAC Checks**:
   - You likely have references to `FeatureFlag`, `SidebarFeature`, or role-based dependencies. If they’re purely for backend enforcement, **comment out** or **remove** them. The front end can still query the same DB tables if needed (the backend just won’t block anything).
5. **Default Tenant**: Hard-code all “new domain records” or “new sitemaps” to store a single **default** tenant ID. No DB check or creation.

If you do these steps, the code no longer tries to “lookup tenant.” The DB columns remain, but get filled with the default. Meanwhile, your front end can continue to read from the roles or features tables if it wants.

---

# **Part B: File-by-File Removal Checklist**

Use your favorite “global search” (or ask your local AI) to find references to:

1. **`tenant_id`**
2. **`Tenant`** (the model import or creation)
3. **`require_permission`, `require_feature_enabled`, or any old RBAC calls**
4. **`FeatureFlag`, `SidebarFeature`, or any relationship referencing them**
5. **`args = Query(...)` / `kwargs = Query(...)`** leftover from your old wrappers (if any remain).

Then handle them as follows:

### 1. `src/services/sitemap/processing_service.py`
- **Remove** or **comment out** lines that do `tenant_check = await session.execute(select(Tenant)....)`.
- **Remove** any “create a new tenant if missing” blocks.
- **Remove** or “comment out” any references that raise exceptions if the tenant doesn’t exist.
- In the “domain creation” logic, simply do:
  ```python
  domain_obj = Domain(
      domain=clean_domain,
      tenant_id="550e8400-e29b-41d4-a716-446655440000",
      ...
  )
  ```
  or whatever default ID you prefer.
- If it sets `tenant_uuid` from the user, just keep the line that _parses_ it and never tries to confirm that tenant in the DB.

### 2. **Any router** that uses `Depends(check_sitemap_access)` or similar
- If that `check_sitemap_access` function tries to verify tenant existence or run `require_permission(...)`, remove/comment out the lines that do so.
- You can keep the function to parse `tenant_id` from a JWT or user dictionary but skip the DB verification part.

### 3. **`SidebarFeature` → `FeatureFlag`** (if you see “mapper failed to initialize” errors)
- If your code has a relationship to a non-existent `FeatureFlag` model, **comment out** that relationship.
- If your DB table `feature_flags` still physically exists and you want to keep it for the front-end, that’s fine – just don’t forcibly load it in the backend if it’s not stable.
- Alternatively, fix the relationship so it references an actual `FeatureFlag` model that still exists.

### 4. **`auth` or `dependencies.py`** code referencing roles
- If you see lines like `require_role_level(user, ROLE_HIERARCHY["ADMIN"])`, remove or comment them.
- Keep the JWT logic that extracts the user ID. You just no longer fail the request if user’s role doesn’t match.

### 5. **Database Migrations** (Optional Step)
- You’re not dropping or renaming tenant tables. So you can skip any migration changes.
- Just be sure your code doesn’t create or require that a row be present in `Tenant`.

**Result**: The system will store a default tenant ID (like `"550e8400-e29b-41d4-a716-446655440000"`) in every domain or job record, but **never** check if that row exists. Meanwhile, your front end can still show or manage roles/features in the DB if it wants.

---

# **Part C: Example Prompt to Give Another AI**

Below is a template prompt you can feed line-by-line to Claude (or another code-transforming AI). **You** just supply each file’s content after the “---” markers.

```plaintext
System message:
"You are a coding transformation assistant. The user wants to remove all enforced tenant checks, RBAC, or FeatureFlag references, but keep the JWT logic and the existing DB columns for roles/tenants. They do not want to drop the actual tables or columns. They just want to skip or remove code that queries or creates these tenant/feature rows.
They also want a default tenant_id used for any new domain or sitemap.
Please preserve the code's structure, but remove or comment out references to tenant checks, rbac checks, or attempts to find/create a tenant.
No changes to the rest of the logic.
No changes to JWT-based authentication.
Keep domain/sitemap creation logic, but always set tenant_id to the default.
Do not rename or drop the columns—just do not force them to exist inß the DB."

User message:
"Below is a file:
--- START FILE ---
[PASTE THE CONTENTS OF processing_service.py HERE]
--- END FILE ---
Please transform this code accordingly, returning the complete updated file."
```

**Repeat** for any other file that has references to tenant checks or feature flags.

---

## **Conclusion / Next Steps**

1. **Keep JWT** exactly as is.
2. **Remove tenant checks** from your backend code. Hard-code any “tenant_id” usage to a default.
3. **Remove** or **comment out** references to `FeatureFlag` or other “RBAC” calls.
4. **Leave the underlying DB schema** alone – you can reintroduce real tenant checks later, once the scraping core is stable.

That’s it! This approach ensures your code no longer bombs on “tenant or user not found” while preserving the **columns/tables** for a future iteration of multi-tenant support.
