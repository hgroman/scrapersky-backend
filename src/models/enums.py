import enum

# Existing Enums...

class SitemapAnalysisStatusEnum(str, enum.Enum):
    pending = "pending" # Initial state when domain is created/reset
    queued = "queued" # Scheduler picked it up, waiting for adapter
    processing = "processing" # Adapter sent to API
    submitted = "submitted" # API accepted (202)
    failed = "failed" # Adapter or API call failed

class DomainStatusEnum(str, enum.Enum):
    pending = "pending" # Ready for metadata extraction
    processing = "processing" # Metadata extraction in progress
    completed = "completed" # Metadata extraction successful
    error = "error" # Metadata extraction failed
