from app.models.normalized_job import NormalizedJob
from app.models.resume import NormalizedResume

class OTPMEngine:
    """
    OA Trigger Probability Metric (OTPM) Engine.
    Calculates P(OA | Resume, Job).
    """
    
    def calculate_probability(self, job: NormalizedJob, resume: NormalizedResume) -> float:
        """
        Returns a probability between 0.0 and 1.0.
        """
        score = 0.5  # Base probability (neutral)

        # 1. Experience Check (Critical)
        experience_gap = resume.years_of_experience - job.experience_years
        if experience_gap >= 0:
            score += 0.2  # Meets or exceeds
        elif experience_gap >= -1:
            score -= 0.1  # Slightly under (within 1 year)
        else:
            score -= 0.3  # Significantly under

        # 2. Skill Match (Keyword Density)
        # Calculate overlap
        job_skills = set(job.required_skills)
        resume_skills = set(resume.skills)
        
        if not job_skills:
            # If job has no parsed skills, assume neutral or slight positive if title matches
            overlap_ratio = 1.0 
        else:
            intersection = job_skills.intersection(resume_skills)
            overlap_ratio = len(intersection) / len(job_skills)
        
        # Add score based on coverage
        if overlap_ratio >= 0.8:
            score += 0.3
        elif overlap_ratio >= 0.5:
            score += 0.1
        elif overlap_ratio < 0.2:
            score -= 0.2

        # 3. Visa "Kill Switch"
        # If Job says "US Citizen Only" (UNLIKELY sponsorship) and Resume says "Visa Required"
        if job.visa_sponsorship == "UNLIKELY" and resume.visa_status == "Visa Required":
            score -= 0.5
        elif job.visa_sponsorship == "LIKELY" and resume.visa_status == "Visa Required":
            score += 0.1
            
        # 4. Entry Level Friendly
        # If job asks for 0 experience, boost score for anyone
        if job.experience_years == 0:
             score += 0.1

        # Clamp score 0..1
        return max(0.0, min(1.0, score))

    def get_recommendation(self, probability: float) -> str:
        if probability >= 0.8:
            return "STRONG APPLY"
        elif probability >= 0.6:
            return "APPLY"
        elif probability >= 0.4:
            return "LOW PRIORITY"
        else:
            return "SKIP"
