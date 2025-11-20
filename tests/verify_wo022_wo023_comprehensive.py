import sys
import os
import uuid
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.models.base import Base
from src.models.local_business import LocalBusiness, PlaceStatusEnum, DomainExtractionStatusEnum
from src.models.domain import Domain, SitemapCurationStatusEnum
from src.models.sitemap import SitemapFile
from src.models.place import Place
from src.models.tenant import Tenant

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database Connection (Ensure DATABASE_URL is set)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable not set.")
    sys.exit(1)

# Convert async URL to sync for testing
if "asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    # Remove asyncpg-specific parameters
    DATABASE_URL = DATABASE_URL.replace("?ssl=true", "?sslmode=require")
    DATABASE_URL = DATABASE_URL.replace("&ssl=true", "")
    logger.info(f"Converted async URL to sync for testing")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def run_verification():
    session = SessionLocal()
    try:
        logger.info("🚀 Starting Comprehensive Verification for WO-022 & WO-023...")

        # --- Setup: Get a valid Tenant ID ---
        # We need a valid tenant for FK tests. If none exists, we might need to create one or fail.
        # Assuming at least one tenant exists or we use the default ID if it exists.
        valid_tenant_id = "550e8400-e29b-41d4-a716-446655440000" # Default from models
        
        # Verify tenant exists
        # (Skipping explicit check, assuming dev/prod env has the default tenant or we catch FK error)

        # --- TEST 1: WO-023 LocalBusiness Enum Fix ---
        logger.info("🔹 TEST 1: Verifying LocalBusiness Status (WO-023)...")
        lb_id = uuid.uuid4()
        lb = LocalBusiness(
            id=lb_id,
            tenant_id=uuid.UUID(valid_tenant_id), 
            business_name=f"Test Business {lb_id}",
            status=PlaceStatusEnum.Maybe, # This was the problematic value
            domain_extraction_status=DomainExtractionStatusEnum.Queued
        )
        session.add(lb)
        session.commit()
        
        # Verify Read
        saved_lb = session.get(LocalBusiness, lb_id)
        if saved_lb.status == PlaceStatusEnum.Maybe:
            logger.info("✅ TEST 1 PASSED: Successfully saved and retrieved LocalBusiness with status 'Maybe'.")
        else:
            logger.error(f"❌ TEST 1 FAILED: Retrieved status {saved_lb.status} does not match 'Maybe'.")
            return False

        # --- TEST 2: WO-022 Domain Enum Rename ---
        logger.info("🔹 TEST 2: Verifying Domain Sitemap Curation Status (WO-022)...")
        domain_id = uuid.uuid4()
        domain_name = f"test-domain-{domain_id}.com"
        domain = Domain(
            id=domain_id,
            domain=domain_name,
            tenant_id=uuid.UUID(valid_tenant_id),
            sitemap_curation_status=SitemapCurationStatusEnum.Selected # Uses renamed DB type
        )
        session.add(domain)
        session.commit()
        
        saved_domain = session.get(Domain, domain_id)
        if saved_domain.sitemap_curation_status == SitemapCurationStatusEnum.Selected:
            logger.info("✅ TEST 2 PASSED: Successfully saved Domain with SitemapCurationStatusEnum.")
        else:
            logger.error("❌ TEST 2 FAILED: Enum value mismatch.")
            return False

        # --- TEST 3: WO-022 Foreign Key Enforcement ---
        logger.info("🔹 TEST 3: Verifying Foreign Key Constraint Enforcement...")
        invalid_tenant_id = uuid.uuid4() # Random UUID that shouldn't exist in tenants table
        
        place = Place(
            place_id=f"place_{uuid.uuid4()}",
            name="Invalid Tenant Place",
            tenant_id=invalid_tenant_id # Should trigger FK violation
        )
        session.add(place)
        
        try:
            session.commit()
            logger.error("❌ TEST 3 FAILED: DB allowed saving a record with INVALID tenant_id. FK missing?")
            return False
        except IntegrityError:
            session.rollback()
            logger.info("✅ TEST 3 PASSED: Database correctly blocked invalid tenant_id (IntegrityError).")

        # --- Cleanup ---
        logger.info("🧹 Cleaning up test data...")
        session.delete(saved_lb)
        session.delete(saved_domain)
        session.commit()
        
        logger.info("🎉 ALL TESTS PASSED SUCCESSFULLY!")
        return True

    except Exception as e:
        logger.error(f"❌ An unexpected error occurred: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    if run_verification():
        sys.exit(0)
    else:
        sys.exit(1)
