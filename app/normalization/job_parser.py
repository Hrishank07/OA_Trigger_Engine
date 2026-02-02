import re
from typing import List, Set
from app.models.job import Job
from app.models.normalized_job import NormalizedJob

class JobParser:
    """
    Parses raw Job objects into NormalizedJob objects using rule-based extraction.
    """
    
    # Common tech skills to check for (extensible list)
    COMMON_SKILLS = {
        "python", "java", "c++", "javascript", "typescript", "react", "angular", "vue",
        "aws", "azure", "gcp", "docker", "kubernetes", "sql", "nosql", "redis",
        "mongodb", "postgresql", "mysql", "django", "flask", "fastapi", "spring",
        "node.js", "go", "golang", "rust", "ruby", "rails", "php", "swift", "kotlin",
        "terraform", "jenkins", "gitlab", "github", "linux", "git",
        "ansible", "bash", "shell", "scripting", "sre", "ci/cd", "circleci",
        "prometheus", "grafana", "elasticsearch", "kafka"
    }
    
    VISA_KEYWORDS_POSITIVE = {
        "visa sponsorship", "sponsor", "h1b"
    }
    
    VISA_KEYWORDS_NEGATIVE = {
        "us citizen", "green card", "permanent resident", "no sponsorship", "not sponsor"
    }

    def parse(self, job: Job) -> NormalizedJob:
        description_lower = job.description.lower()
        
        required_skills = self._extract_skills(description_lower)
        experience_years = self._extract_experience(description_lower)
        visa_sponsorship = self._extract_visa_status(description_lower)
        
        return NormalizedJob(
            job_id=job.id,
            required_skills=required_skills,
            experience_years=experience_years,
            visa_sponsorship=visa_sponsorship,
            keywords=list(required_skills) # Basic keyword set matches skills for now
        )

    def _extract_skills(self, text: str) -> List[str]:
        found_skills = []
        for skill in self.COMMON_SKILLS:
            # Special handling for skills with punctuation
            if skill in {'c++', 'node.js', 'c#', '.net', 'ci/cd'}:
                 # Simple substring check often safer for these chars, 
                 # but let's try to be smart about boundaries if possible.
                 # For now, literal check is robust enough for these specific terms.
                 if skill in text:
                     found_skills.append(skill)
            else:
                # Standard word boundary regex for "clean" words
                # \bpython\b
                pattern = re.compile(r'\b' + re.escape(skill) + r'\b')
                if pattern.search(text):
                    found_skills.append(skill)
        return sorted(found_skills)

    def _extract_experience(self, text: str) -> float:
        # Patterns: "5+ years", "3-5 years", "2 to 3 years"
        patterns = [
            r'(\d+)\s*\+\s*years',
            r'(\d+)\s*-\s*\d+\s*years',
            r'(\d+)\s*to\s*\d+\s*years',
            r'(\d+)\s*years'
        ]
        
        for p in patterns:
            matches = re.findall(p, text)
            if matches:
                 # Heuristic: The first mentioned year count is often the requirement.
                 # e.g. "Requirements: 3+ years experience"
                 for m in matches:
                    try:
                        y = float(m)
                        # Filter out unlikely numbers (e.g. "2024 years")
                        if 0 < y < 20: 
                            return y
                    except:
                        pass
                        
        return 0.0

    def _extract_visa_status(self, text: str) -> str:
        # Check negative signals first (US Citizen only)
        for keyword in self.VISA_KEYWORDS_NEGATIVE:
            if keyword in text:
                return "UNLIKELY"
                
        # Check positive signals
        for keyword in self.VISA_KEYWORDS_POSITIVE:
            if keyword in text:
                return "LIKELY"
                
        return "UNCLEAR"
