# In src/main.py or your main API router file (e.g., src/api.py)

# Import the router instance from its workflow-specific file
# Example: from src.routers.page_curation import router as page_curation_router
from src.routers.{workflow_name} import router as {workflow_name}_router # Adjust alias as preferred

# ... FastAPI app (app) or main API router (e.g., api_v3_router) setup ...

# Include the workflow-specific router.
# The prefix here, combined with any app-level prefix, forms the base for the endpoint.
# Example for page_curation (source_table_name 'page', source_table_plural_name 'pages'):
# app.include_router(
#     page_curation_router,
#     prefix="/api/v3/pages", # Forms /api/v3/pages/status for the /status endpoint
#     tags=["PageCuration | Pages"]
# )

app.include_router(
    {workflow_name}_router, # Use the imported router instance
    tags=["{WorkflowNameTitleCase} | {SourceTableTitleCasePlural}"], # Example: "PageCuration | Pages"
    prefix="/api/v3/{source_table_plural_name}" # Example: "/api/v3/pages"
)
