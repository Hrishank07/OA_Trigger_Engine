from typing import List, Optional
from pydantic import BaseModel

class NormalizedJob(BaseModel):
    """
    Structured job data extracted from a raw Job.
    """
    job_id: str
    required_skills: List[str] = []
    experience_years: float = 0.0
    visa_sponsorship: str = "UNCLEAR"  # LIKELY, UNLIKELY, UNCLEAR
    keywords: List[str] = []
    
    model_config = {
        "extra": "ignore"
    }
