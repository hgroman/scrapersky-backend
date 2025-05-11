# In: src/models/{source_table}.py

from enum import Enum
from typing import Optional # Add Optional if needed for nullable columns
from sqlalchemy import Column, Text # Add other required SQLA types
from sqlalchemy.dialects.postgresql import ENUM as PgEnum # Use PgEnum for DB types
# Import Base, BaseModel, other necessary items...
# from .base import Base, BaseModel

# --- {WorkflowNameTitle} Workflow Enums ---
class {WorkflowName}CurationStatus(str, Enum):
    New = "New"
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"
    Skipped = "Skipped"
    # Add additional values only if absolutely necessary for this specific workflow

class {WorkflowName}ProcessingStatus(str, Enum):
    Queued = "Queued"
    Processing = "Processing"
    Complete = "Complete"  # Standard value across all workflows
    Error = "Error"

# --- Update SQLAlchemy Model ---
class {SourceTableTitle}(Base, BaseModel): # Assuming Base, BaseModel inheritance
    __tablename__ = "{source_table}s" # Or just {source_table} if that\'s the convention

    # ... existing columns ...

    # --- Add New Workflow Columns ---
    {workflow_name}_curation_status = Column(
        PgEnum({WorkflowName}CurationStatus, name="{workflow_name}curationstatus", create_type=False),
        nullable=False,
        server_default={WorkflowName}CurationStatus.New.value,
        index=True # Add index for status filtering
    )

    {workflow_name}_processing_status = Column(
        PgEnum({WorkflowName}ProcessingStatus, name="{workflow_name}processingstatus", create_type=False),
        nullable=True, # Typically nullable, set when curation triggers queueing
        index=True # Add index for scheduler polling
    )

    {workflow_name}_processing_error = Column(
        Text,
        nullable=True
    )

    # ... existing relationships etc. ...
