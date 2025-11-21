import sys
import os
from sqlalchemy import inspect

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.models.local_business import LocalBusiness
    from src.models.domain import Domain
    from src.models.sitemap import SitemapFile, SitemapUrl
    from src.models.place import Place
    print("✅ All models imported successfully.")
except ImportError as e:
    print(f"❌ ImportError: {e}")
    sys.exit(1)

def verify_models():
    print("Verifying model definitions...")
    
    # Check LocalBusiness
    lb_status = LocalBusiness.__table__.columns['status'].type.name
    lb_domain_status = LocalBusiness.__table__.columns['domain_extraction_status'].type.name
    print(f"LocalBusiness.status: {lb_status}")
    print(f"LocalBusiness.domain_extraction_status: {lb_domain_status}")
    
    if lb_status != "place_status_enum":
        print("❌ LocalBusiness.status mismatch")
        return False
    if lb_domain_status != "domain_extraction_status_enum":
        print("❌ LocalBusiness.domain_extraction_status mismatch")
        return False

    # Check Domain
    d_sitemap_status = Domain.__table__.columns['sitemap_curation_status'].type.name
    print(f"Domain.sitemap_curation_status: {d_sitemap_status}")
    if d_sitemap_status != "sitemap_curation_status_enum":
        print("❌ Domain.sitemap_curation_status mismatch")
        return False

    # Check SitemapFile
    sf_curation_status = SitemapFile.__table__.columns['deep_scrape_curation_status'].type.name
    print(f"SitemapFile.deep_scrape_curation_status: {sf_curation_status}")
    if sf_curation_status != "sitemap_curation_status_enum":
        print("❌ SitemapFile.deep_scrape_curation_status mismatch")
        return False

    # Check Place
    p_status = Place.__table__.columns['status'].type.name
    print(f"Place.status: {p_status}")
    if p_status != "place_status_enum":
        print("❌ Place.status mismatch")
        return False

    print("✅ All enum mappings verified.")
    return True

if __name__ == "__main__":
    if verify_models():
        sys.exit(0)
    else:
        sys.exit(1)
