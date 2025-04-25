import json
from pathlib import Path

# --- Mock Data (replace with actual file reads) ---

# Load all used modules (ensure this file exists)
all_modules_path = Path("reports/all_used_modules.json")
if all_modules_path.exists():
    with open(all_modules_path, "r") as f:
        all_modules = json.load(f)
else:
    print(f"Error: {all_modules_path} not found. Please run the full trace first.")
    all_modules = []  # Default to empty list to avoid crashing, but map will be incomplete

# Load dependencies for LocalMiner (ensure this file exists)
deps_google_maps_api_path = Path("reports/deps_google_maps_api.json")
if deps_google_maps_api_path.exists():
    with open(deps_google_maps_api_path, "r") as f:
        deps_google_maps_api = json.load(f)
else:
    print(
        f"Warning: {deps_google_maps_api_path} not found. Mapping for LocalMiner will be incomplete."
    )
    deps_google_maps_api = []

# Load dependencies for StagingEditor (ensure this file exists)
deps_places_staging_path = Path("reports/deps_places_staging.json")
if deps_places_staging_path.exists():
    with open(deps_places_staging_path, "r") as f:
        deps_places_staging = json.load(f)
else:
    print(
        f"Warning: {deps_places_staging_path} not found. Mapping for StagingEditor will be incomplete."
    )
    deps_places_staging = []

# --- Load dependencies for LocalBusinessCuration ---
deps_local_business_curation_path = Path("reports/deps_local_businesses.json")
if deps_local_business_curation_path.exists():
    with open(deps_local_business_curation_path, "r") as f:
        deps_local_business_curation = json.load(f)
else:
    print(
        f"Warning: {deps_local_business_curation_path} not found. Mapping for LocalBusinessCuration will be incomplete."
    )
    deps_local_business_curation = []

# --- Load dependencies for DomainCuration ---
deps_domains_path = Path("reports/deps_domains.json")
if deps_domains_path.exists():
    with open(deps_domains_path, "r") as f:
        deps_domains = json.load(f)
else:
    print(
        f"Warning: {deps_domains_path} not found. Mapping for DomainCuration will be incomplete."
    )
    deps_domains = []

# --- Load dependencies for SitemapCuration ---
deps_sitemap_files_path = Path("reports/deps_sitemap_files.json")
if deps_sitemap_files_path.exists():
    with open(deps_sitemap_files_path, "r") as f:
        deps_sitemap_files = json.load(f)
else:
    print(
        f"Warning: {deps_sitemap_files_path} not found. Mapping for SitemapCuration will be incomplete."
    )
    deps_sitemap_files = []

# --- Load dependencies for DomainScanning ---
deps_modernized_page_scraper_path = Path("reports/deps_modernized_page_scraper.json")
if deps_modernized_page_scraper_path.exists():
    with open(deps_modernized_page_scraper_path, "r") as f:
        deps_modernized_page_scraper = json.load(f)
else:
    print(
        f"Warning: {deps_modernized_page_scraper_path} not found. Mapping for DomainScanning will be incomplete."
    )
    deps_modernized_page_scraper = []

# --- Load dependencies for ContentMap ---
deps_modernized_sitemap_path = Path("reports/deps_modernized_sitemap.json")
if deps_modernized_sitemap_path.exists():
    with open(deps_modernized_sitemap_path, "r") as f:
        deps_modernized_sitemap = json.load(f)
else:
    print(
        f"Warning: {deps_modernized_sitemap_path} not found. Mapping for ContentMap will be incomplete."
    )
    deps_modernized_sitemap = []

# --- Load dependencies for BatchProcessing (Batch Sitemap) ---
deps_batch_sitemap_path = Path("reports/deps_batch_sitemap.json")
if deps_batch_sitemap_path.exists():
    with open(deps_batch_sitemap_path, "r") as f:
        deps_batch_sitemap = json.load(f)
else:
    print(
        f"Warning: {deps_batch_sitemap_path} not found. Mapping for BatchProcessing (Sitemap) will be incomplete."
    )
    deps_batch_sitemap = []

# --- Load dependencies for DBPortal ---
deps_db_portal_path = Path("reports/deps_db_portal.json")
if deps_db_portal_path.exists():
    with open(deps_db_portal_path, "r") as f:
        deps_db_portal = json.load(f)
else:
    print(
        f"Warning: {deps_db_portal_path} not found. Mapping for DBPortal will be incomplete."
    )
    deps_db_portal = []

# --- Load dependencies for DevTools ---
deps_dev_tools_path = Path("reports/deps_dev_tools.json")
if deps_dev_tools_path.exists():
    with open(deps_dev_tools_path, "r") as f:
        deps_dev_tools = json.load(f)
else:
    print(
        f"Warning: {deps_dev_tools_path} not found. Mapping for DevTools will be incomplete."
    )
    deps_dev_tools = []

# --- TODO: Load dependency lists for other features here ---
# Example:
# deps_local_business_curation_path = Path("reports/deps_local_businesses.json")
# if deps_local_business_curation_path.exists():
#     with open(deps_local_business_curation_path, 'r') as f:
#         deps_local_business_curation = json.load(f)
# else:
#     print(f"Warning: {deps_local_business_curation_path} not found. Mapping for LocalBusinessCuration will be incomplete.")
#     deps_local_business_curation = []


# Initialize the mapping dictionary
functional_map = {
    filepath: {"Mapped Business Function(s)": [], "Entry Point(s)": [], "Notes": ""}
    for filepath in all_modules
}

# --- STEP 1: Map files based DIRECTLY on feature dependency lists --- #

feature_deps = {
    # UI/Feature Name : (Entry Point File, List of Dependent Files)
    "LocalMiner": ("src/routers/google_maps_api.py", deps_google_maps_api),
    "StagingEditor": ("src/routers/places_staging.py", deps_places_staging),
    "LocalBusinessCuration": (
        "src/routers/local_businesses.py",
        deps_local_business_curation,
    ),
    "DomainCuration": ("src/routers/domains.py", deps_domains),
    "SitemapCuration": ("src/routers/sitemap_files.py", deps_sitemap_files),
    "DomainScanning": (
        "src/routers/modernized_page_scraper.py",
        deps_modernized_page_scraper,
    ),
    "ContentMap": ("src/routers/modernized_sitemap.py", deps_modernized_sitemap),
    # --- Non-UI features mapped via specific entry points/keywords ---
    "BatchProcessing": ("src/routers/batch_sitemap.py", deps_batch_sitemap),
    "DBPortal": ("src/routers/db_portal.py", deps_db_portal),
    "DevTool": ("src/routers/dev_tools.py", deps_dev_tools),
}

# Keep track of which feature an entry point belongs to
entry_point_to_feature = {v[0]: k for k, v in feature_deps.items()}

for business_function, (entry_point, dep_list) in feature_deps.items():
    for filepath in dep_list:
        if filepath in functional_map:
            # Directly add the business function mapping
            if (
                business_function
                not in functional_map[filepath]["Mapped Business Function(s)"]
            ):
                functional_map[filepath]["Mapped Business Function(s)"].append(
                    business_function
                )
            # Add the entry point that pulled this file in
            if entry_point not in functional_map[filepath]["Entry Point(s)"]:
                functional_map[filepath]["Entry Point(s)"].append(entry_point)

# --- STEP 2: Refine mappings: Identify Core/Shared, Apply Generic Categories --- #

# Keywords ONLY for generic categories (applied if file has NO specific UI mapping yet)
core_fastapi_keywords = ["src/main.py", "src/core/", "src/health/"]
scheduler_keywords = ["_scheduler.py", "scheduler_instance.py"]
# Add other generic keywords if needed, but avoid broad ones like 'db/' or 'models/' initially

# Sets to track counts
core_shared_files = set()
core_fastapi_files = set()
scheduler_files = set()
batch_files = set()  # Will be populated if 'BatchProcessing' mapping exists
db_portal_files = set()  # Will be populated if 'DBPortal' mapping exists
dev_tool_files = set()  # Will be populated if 'DevTool' mapping exists
# ScrapingTask needs separate handling if not covered by a specific entry point trace
scraping_task_files = set()
unmapped_files = set()
mapped_counts = {}  # Count files per specific feature

for filepath, data in functional_map.items():
    current_mappings = data["Mapped Business Function(s)"]
    num_mappings = len(current_mappings)

    if num_mappings > 1:
        # Mapped to multiple features -> Core/Shared
        data["Original Functions"] = sorted(current_mappings)
        data["Mapped Business Function(s)"] = ["Core/Shared"]
        core_shared_files.add(filepath)
    elif num_mappings == 1:
        # Mapped to exactly one feature
        feature = current_mappings[0]
        mapped_counts[feature] = mapped_counts.get(feature, 0) + 1
        # Increment specific category counts if applicable
        if feature == "BatchProcessing":
            batch_files.add(filepath)
        if feature == "DBPortal":
            db_portal_files.add(filepath)
        if feature == "DevTool":
            dev_tool_files.add(filepath)
        # Keep the specific feature mapping
    else:  # num_mappings == 0
        # Not mapped by any feature trace, try generic keywords
        assigned_category = None
        for keyword in core_fastapi_keywords:
            if keyword in filepath:
                assigned_category = "CoreFastAPI"
                core_fastapi_files.add(filepath)
                break
        if not assigned_category:
            for keyword in scheduler_keywords:
                if keyword in filepath:
                    assigned_category = "BackgroundScheduler"
                    scheduler_files.add(filepath)
                    break
        # Add check for ScrapingTask if needed (e.g., using 'tasks/' keyword)
        if not assigned_category and "tasks/" in filepath:
            assigned_category = "ScrapingTask"
            scraping_task_files.add(filepath)

        if assigned_category:
            data["Mapped Business Function(s)"] = [assigned_category]
        else:
            # Still unmapped after direct traces and generic keywords
            data["Mapped Business Function(s)"] = ["Unmapped"]
            unmapped_files.add(filepath)

# --- STEP 3: Generate Summary and Report --- #

# Ensure all counts are captured correctly in the summary
summary = {
    "Total Used Files Analyzed": len(all_modules),
    "Files Mapped (Specific Features)": mapped_counts,
    "Files Categorized as Core/Shared": len(core_shared_files),
    "Files Categorized as CoreFastAPI": len(core_fastapi_files),
    "Files Categorized as BackgroundScheduler": len(scheduler_files),
    # Specific counts are derived from mapped_counts or direct sets now
    "Files Associated with BatchProcessing": len(batch_files),
    "Files Associated with ScrapingTask": len(scraping_task_files),
    "Files Associated with DevTool": len(dev_tool_files),
    "Files Associated with DBPortal": len(db_portal_files),
    "Unmapped Files Count": len(unmapped_files),
    "Unmapped Files List": sorted(list(unmapped_files)),
}

# report_path = Path("project-docs") / "functional_dependency_map.json" # OLD PATH
report_path = (
    Path("Docs/Docs_0_Architecture_and_Status") / "functional_dependency_map.json"
)  # NEW PATH
report_path.parent.mkdir(parents=True, exist_ok=True)

output_data = {"summary": summary, "file_mappings": functional_map}

with open(report_path, "w") as f:
    json.dump(output_data, f, indent=2)

print(f"Functional dependency map generated: {report_path}")
