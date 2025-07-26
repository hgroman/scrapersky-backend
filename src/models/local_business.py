import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.sql import func

# Import the actual PlaceStatusEnum definition
from .place import PlaceStatusEnum

try:
    from .base import Base
except ImportError:
    print(
        "Warning: Could not import Base using relative path '.base'. Trying absolute path 'src.models.base'."
    )
    try:
        from src.models.base import Base
    except ImportError:
        raise ImportError(
            "Could not import Base from either '.base' or 'src.models.base'. Ensure the path is correct."
        )


# Define the enum for the domain extraction background process status
# Values MUST match the database enum values exactly (case-sensitive)
class DomainExtractionStatusEnum(enum.Enum):
    Queued = "Queued"
    Processing = "Processing"
    Completed = "Completed"
    Error = "Error"


class LocalBusiness(Base):
    __tablename__ = "local_businesses"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    place_id = Column(String, unique=True, nullable=True, index=True)
    lead_source = Column(Text, nullable=True)
    business_name = Column(Text, nullable=True, index=True)
    full_address = Column(Text, nullable=True)
    street_address = Column(Text, nullable=True)
    city = Column(Text, nullable=True, index=True)
    state = Column(Text, nullable=True, index=True)
    zip = Column(Text, nullable=True, index=True)
    country = Column(Text, nullable=True)
    phone = Column(Text, nullable=True)
    main_category = Column(Text, nullable=True)
    extra_categories = Column(ARRAY(Text), nullable=True)
    rating = Column(Numeric(3, 2), nullable=True)
    reviews_count = Column(Integer, nullable=True)
    price_text = Column(Text, nullable=True)
    website_url = Column(String, nullable=True)
    business_verified = Column(Boolean, nullable=True)
    monday_hours = Column(Text, nullable=True)
    tuesday_hours = Column(Text, nullable=True)
    wednesday_hours = Column(Text, nullable=True)
    thursday_hours = Column(Text, nullable=True)
    friday_hours = Column(Text, nullable=True)
    saturday_hours = Column(Text, nullable=True)
    sunday_hours = Column(Text, nullable=True)
    timezone = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    latitude = Column(Numeric(10, 7), nullable=True)
    longitude = Column(Numeric(10, 7), nullable=True)
    food_featured = Column(Boolean, nullable=True)
    hotel_featured = Column(Boolean, nullable=True)
    service_options = Column(ARRAY(Text), nullable=True)
    highlights = Column(ARRAY(Text), nullable=True)
    popular_for = Column(ARRAY(Text), nullable=True)
    accessibility = Column(ARRAY(Text), nullable=True)
    offerings = Column(ARRAY(Text), nullable=True)
    dining_options = Column(ARRAY(Text), nullable=True)
    amenities = Column(ARRAY(Text), nullable=True)
    atmosphere = Column(ARRAY(Text), nullable=True)
    crowd = Column(ARRAY(Text), nullable=True)
    planning = Column(ARRAY(Text), nullable=True)
    payments = Column(ARRAY(Text), nullable=True)
    children = Column(ARRAY(Text), nullable=True)
    parking = Column(ARRAY(Text), nullable=True)
    pets = Column(ARRAY(Text), nullable=True)
    additional_json = Column(JSONB, nullable=True, server_default="{}")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Use PlaceStatusEnum as it defines the shared user-facing statuses
    status = Column(
        Enum(
            PlaceStatusEnum,
            name="place_status_enum",
            create_type=False,
            native_enum=True,
        ),
        default=PlaceStatusEnum.New,
        nullable=False,
        index=True,
    )

    # New Enum specifically for tracking domain extraction workflow for this business
    # THIS ENUM MUST ADHERE TO PASCALCASE STANDARD
    domain_extraction_status = Column(
        Enum(
            DomainExtractionStatusEnum,  # Reference the updated Enum
            name="domain_extraction_status",  # Fixed: Use actual DB enum name
            create_type=False
        ),
        nullable=True,
        default=DomainExtractionStatusEnum.Queued,
        index=True,
    )
    domain_extraction_error = Column(String, nullable=True)  # To store error messages

    def to_dict(self):
        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            if isinstance(value, uuid.UUID):
                result[c.name] = str(value)
            elif isinstance(value, datetime):
                result[c.name] = value.isoformat()
            elif hasattr(value, "quantize"):
                result[c.name] = float(value) if value is not None else None
            else:
                result[c.name] = value
        return result

    def __repr__(self):
        return f"<LocalBusiness(id={self.id}, name='{self.business_name}')>"
