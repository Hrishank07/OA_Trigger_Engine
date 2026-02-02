from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, HttpUrl

class Job(BaseModel):
    """
    Normalized Job model representing a job posting.
    """
    id: str  # Unique identifier (could be URL hash or platform ID)
    title: str
    company: str
    location: str
    description: str  # Full HTML or text description
    url: str
    source: str  # e.g., "linkedin", "jobright", "simplify"
    posted_date: Optional[datetime] = None
    
    # Raw platform-specific data for debugging/extension
    raw_data: Dict[str, Any] = {}

    model_config = {
        "extra": "ignore"
    }
