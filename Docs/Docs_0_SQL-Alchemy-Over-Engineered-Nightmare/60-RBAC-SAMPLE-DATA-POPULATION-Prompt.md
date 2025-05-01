Below is a **single, comprehensive prompt** you can copy/paste directly into Cursor. It will instruct it to create **one script** (`populate_rbac_sample_data.py`) that inserts **all** the sample data you need:

1. **Roles & Permissions** (mapping each role to relevant permissions).
2. **Eight MVP Services** in `feature_flags` (LocalMiner, ContentMap, etc.).
3. **Six Tabs** per service in `sidebar_features` (Control Center, Discovery Scan, etc.).
4. **Tenant Feature Assignments** for at least one tenant.
5. **Sample User** assignments (user_roles) so you can test the final system thoroughly.

This prompt is as explicit as possible, covering each table and the exact content. **Copy and paste** it into your Cursor environment, and Cursor should generate the entire script.

---

## **The Prompt**

**Cursor, please create a Python script named `populate_rbac_sample_data.py` that does the following:**

---

### **1) Connect to the Database**

- Use **environment variables** (like `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_NAME`) to assemble the connection string.
- Prompt for the **database password** securely if needed (similar to the `secure_verify.py` approach).
- Commit changes in a **single transaction** (or roll back if something fails).

---

### **2) Insert Sample Permissions & Map Them to Roles**

**We have four roles** in the `roles` table by default:

- `USER`
- `ADMIN`
- `SUPER_ADMIN`
- `GLOBAL_ADMIN`

**We have these six existing default permissions**:

1. `view_dashboard`
2. `manage_users`
3. `manage_roles`
4. `manage_permissions`
5. `configure_features`
6. `manage_api_keys`

**But we also want more specific service-based permissions** for each MVP service. Let’s define them as:

- `start_localminer`, `view_localminer`, `start_contentmap`, `view_contentmap`, etc. (One “start*” and one “view*” for each service).

Specifically, for 8 services:

1. LocalMiner: `start_localminer`, `view_localminer`
2. ContentMap: `start_contentmap`, `view_contentmap`
3. FrontendScout: `start_frontendscout`, `view_frontendscout`
4. SiteHarvest: `start_siteharvest`, `view_siteharvest`
5. EmailHunter: `start_emailhunter`, `view_emailhunter`
6. ActionQueue: `start_actionqueue`, `view_actionqueue`
7. SocialRadar: `start_socialradar`, `view_socialradar`
8. ContactLaunchpad: `start_contactlaunchpad`, `view_contactlaunchpad`

Insert these **new permissions** into the `permissions` table if they’re not already present. Then map them to roles in `role_permissions`. For example:

- **ADMIN** can `start_` any service, and also `view_` them.
- **USER** can only `view_` them.
- **SUPER_ADMIN** and **GLOBAL_ADMIN** get **all** of them.

The script should:

1. **Check** if each permission already exists (by name).
2. If not, **insert** it.
3. Then **insert** rows into `role_permissions`, ensuring no duplicates.

---

### **3) Insert 8 Services into `feature_flags`**

We want to treat each service as a **feature**. For each, provide:

| **name**           | **description**                          | **default_enabled** |
| ------------------ | ---------------------------------------- | ------------------- |
| `localminer`       | `Google Maps scraping and analysis tool` | `false`             |
| `contentmap`       | `Sitemap analyzer for content structure` | `false`             |
| `frontendscout`    | `Homepage scraping and insights`         | `false`             |
| `siteharvest`      | `Full-site scraper for deeper data`      | `false`             |
| `emailhunter`      | `Email scraping tool`                    | `false`             |
| `actionqueue`      | `Follow-up queue manager`                | `false`             |
| `socialradar`      | `Social media scraping & lead gen`       | `false`             |
| `contactlaunchpad` | `Contact staging & management`           | `false`             |

Insert each row if it doesn’t exist yet, giving it a `description` as above. Mark `default_enabled=false` for all.

---

### **4) Assign Some Features to Tenants (`tenant_features`)**

- **Assume** you have at least one test tenant in `tenants` (like `"tenant_id=12345678-1234-1234-1234-123456789abc"`).
- For demonstration, **enable** 3 or 4 features for that tenant, e.g. `localminer`, `contentmap`, `actionqueue`, etc. (set `is_enabled=true`).
- For any other features not assigned, keep them disabled so you can see the difference in the UI.

---

### **5) Populate 6 Tabs per Service into `sidebar_features`**

Each of our MVP services has these 6 tabs:

1. `Control Center`
2. `Discovery Scan`
3. `Deep Analysis`
4. `Review & Export`
5. `Smart Alerts`
6. `Performance Insights`

So for each of the 8 features in `feature_flags`, create 6 corresponding rows in `sidebar_features`. For instance:

- **feature_id** → points to the correct row in `feature_flags` (`localminer`, etc.)
- **sidebar_name** = one of the 6 above
- **url_path** = `/{serviceName}/{tabName}` or however you prefer, e.g. `/localminer/control-center`
- **icon** = maybe a placeholder icon name or `NULL`
- **display_order** = numeric sort order if you want (like 1 for “Control Center,” 2 for “Discovery Scan,” etc.)

This means each service has exactly 6 sub-entries in the sidebar. In total, `8 * 6 = 48` entries. The script can do a loop:

```
for each service in (localminer, contentmap, ...):
    for each tab in (control_center, discovery_scan, ...):
        insert into sidebar_features(feature_id, sidebar_name, url_path, icon, display_order, created_at, updated_at)
```

---

### **6) Sample Users & Roles (`user_roles`)**

- Let’s say we have two test user IDs, `testuser1` and `testuser2`, from our `profiles` or `auth.users` table.
  - **testuser1** → assign as `ADMIN`
  - **testuser2** → assign as `USER`
- The script can do something like:
  ```sql
  INSERT INTO user_roles(id, user_id, role_id, created_at)
  VALUES (gen_random_uuid(), 'testuser1-uuid', (SELECT id FROM roles WHERE name='ADMIN'), now())
  ```
- That way, you can see how the UI changes if you log in as `testuser1` vs `testuser2`.

---

### **7) Execution & Safety Checks**

- **Check** for duplicates (like if `feature_flags` already has `localminer`).
- Print out inserted rows so we see the final data.
- End with a **“Sample data inserted successfully!”** message.

---

### **8) Provide Clear Instructions to Run**

The script should:

1. Prompt for DB password.
2. Insert data.
3. Print results.
4. Commit changes.

**Example** usage:

```bash
python populate_rbac_sample_data.py
```

---

## **All-In-One Prompt to Cursor**

Below is the final text you can copy/paste:

---

**Cursor, please create a script named `populate_rbac_sample_data.py` that does the following:**

1. **Connect to the database** using environment variables (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`) and a **securely prompted** password (like `secure_verify.py`).
2. **Insert new permissions** for each MVP service:
   - `[start_localminer, view_localminer, start_contentmap, view_contentmap, ...]`
   - Only insert them if they don’t already exist in `permissions`.
3. **Assign these permissions** to roles in `role_permissions`:
   - **USER**: only the `view_` ones for each service
   - **ADMIN**: both `start_` and `view_` for each service
   - **SUPER_ADMIN** and **GLOBAL_ADMIN**: get **all** permissions
4. **Insert 8 features** into `feature_flags` if missing:
   - `localminer, contentmap, frontendscout, siteharvest, emailhunter, actionqueue, socialradar, contactlaunchpad`
   - Use `false` as `default_enabled` for all, plus a short description (like `"Google Maps Scraper"`).
5. **Assign 3-4 features** to a test tenant in `tenant_features` (set `is_enabled=true` for them). Print which features you enabled.
6. **Create 6 sub-tabs** in `sidebar_features` for each feature:
   - Sub-tabs: `Control Center, Discovery Scan, Deep Analysis, Review & Export, Smart Alerts, Performance Insights`.
   - Example `url_path`: `/{featureName}/{subTabName}` or any pattern you like. `icon` can be `NULL` or `'mdi-something'`.
   - Use `display_order` to keep them sorted from 1..6 for each feature.
7. **Assign sample roles** to 2 test users in `user_roles`:
   - `'testuser1-uuid'` → `'ADMIN'`
   - `'testuser2-uuid'` → `'USER'`
     (Adjust them to real user UUIDs from `profiles` or `auth.users` if needed.)
8. **Avoid duplicates** (if we rerun, it shouldn’t add duplicates).
9. **Print a summary** of what was inserted.
10. End with a commit and a message: `"RBAC sample data inserted successfully!"`.

**Make sure** the script is fully **self-contained**, uses a **single transaction** or careful error handling, and prints any errors if something goes wrong. Finally, **provide instructions** on how to run it from the command line.

## **Now generate the code** for `populate_rbac_sample_data.py`.

That’s the **full measure** to get you 150% sample data. Good luck!
