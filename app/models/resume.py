from typing import List, Optional
from pydantic import BaseModel

class NormalizedResume(BaseModel):
    """
    Structured Resume data extracted from a raw file/text.
    """
    skills: List[str] = []
    years_of_experience: float = 0.0
    visa_status: str = "US Citizen" 
    role_family: str = "Software Engineer"
    education: List[str] = []
    experience_bullets: List[str] = []
    
    model_config = {
        "extra": "ignore"
    }
