import sys
import os
from sqlalchemy import inspect

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.models.local_business import LocalBusiness

def verify_local_business_enum():
    print("Verifying LocalBusiness.status enum mapping...")
    
    # Inspect the status column
    status_column = LocalBusiness.__table__.columns['status']
    
    # Check the enum name
    enum_name = status_column.type.name
    print(f"Found enum name: {enum_name}")
    
    expected_name = "place_status_enum"
    
    if enum_name == expected_name:
        print("SUCCESS: LocalBusiness.status is correctly mapped to 'place_status_enum'.")
        return True
    else:
        print(f"FAILURE: LocalBusiness.status is mapped to '{enum_name}', expected '{expected_name}'.")
        return False

if __name__ == "__main__":
    if verify_local_business_enum():
        sys.exit(0)
    else:
        sys.exit(1)
