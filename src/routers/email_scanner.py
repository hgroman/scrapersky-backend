from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime
import logging

from ..db.sb_connection import db  # Supabase connection from sb_connection.py
from ..tasks.email_scraper import scan_website_for_emails  # Ensure this function works with Supabase

router = APIRouter(prefix="/email-scanner", tags=["email-scanner"])
logger = logging.getLogger(__name__)

class EmailScanningResponse(BaseModel):
    domain_id: int
    domain: str
    total_pages: int
    pages_scanned: int = 0
    contacts_found: int = 0
    scan_timestamp: str
    status: str = "running"

# Temporary in-memory storage for scan statuses (MVP solution)
scan_jobs: Dict[int, EmailScanningResponse] = {}

@router.get("/domains", response_model=List[Dict[str, Any]])
def get_available_domains():
    """Retrieve a list of domains available for scanning using Supabase."""
    try:
        with db.get_cursor() as cur:
            cur.execute("SELECT id, domain FROM domains")
            rows = cur.fetchall()
            domains = [{"id": row["id"], "domain": row["domain"], "pages": 0} for row in rows]
            return domains
    except Exception as e:
        logger.error(f"Error retrieving domains: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve domains")

@router.post("/scan/{domain_id}", response_model=EmailScanningResponse)
def scan_domain(domain_id: int, background_tasks: BackgroundTasks):
    """Initiate scanning for email addresses on a given domain using Supabase."""
    if domain_id in scan_jobs:
        return scan_jobs[domain_id]
    
    try:
        with db.get_cursor() as cur:
            cur.execute("SELECT id, domain FROM domains WHERE id = %s", (domain_id,))
            domain = cur.fetchone()
            if not domain:
                raise HTTPException(status_code=404, detail="Domain not found")
    except Exception as e:
        logger.error(f"Error fetching domain {domain_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving domain information")
    
    # Initialize scan status
    scan_status = EmailScanningResponse(
        domain_id=domain_id,
        domain=domain["domain"],
        total_pages=100,  # Limit to 100 pages for now
        scan_timestamp=datetime.utcnow().isoformat(),
        status="pending"
    )
    scan_jobs[domain_id] = scan_status

    # Queue the email scanning task as a background task.
    # Ensure that scan_website_for_emails is updated to use the Supabase connection.
    background_tasks.add_task(scan_website_for_emails, domain_id, client=db)
    logger.info(f"Email scan initiated for domain_id {domain_id}")

    return scan_status

@router.get("/scan/{domain_id}/status", response_model=EmailScanningResponse)
def get_scan_status(domain_id: int):
    """Retrieve the current scan status for a domain using Supabase."""
    if domain_id not in scan_jobs:
        logger.warning(f"Scan job not found for domain_id {domain_id}")
        raise HTTPException(status_code=404, detail="Scan job not found")
    
    try:
        with db.get_cursor() as cur:
            # Ensure that your contacts table has a column `domain_id` that references domains.id
            cur.execute("SELECT COUNT(*) as contact_count FROM contacts WHERE domain_id = %s", (domain_id,))
            result = cur.fetchone()
            contacts_count = result["contact_count"] if result else 0
            scan_jobs[domain_id].contacts_found = contacts_count
    except Exception as e:
        logger.error(f"Error updating scan status for domain_id {domain_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving scan status")
    
    return scan_jobs[domain_id]
