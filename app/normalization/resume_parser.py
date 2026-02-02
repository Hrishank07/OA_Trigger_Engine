import re
import os
from app.models.resume import NormalizedResume
from app.normalization.job_parser import JobParser
from app.extraction.pdf_utils import PdfUtils

class ResumeParser:
    """
    Parses raw Resume text/PDF into NormalizedResume objects.
    """
    def __init__(self):
        self._parser_tool = JobParser()

    def parse_file(self, filepath: str, user_inputs: dict = None) -> NormalizedResume:
        """
        Parses a file (PDF or Text).
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Resume file not found: {filepath}")
            
        text = ""
        if filepath.lower().endswith(".pdf"):
            text = PdfUtils.extract_text(filepath)
        else:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
                
        return self.parse_text(text, user_inputs)

    def parse_text(self, text: str, user_inputs: dict = None) -> NormalizedResume:
        description_lower = text.lower()
        
        # 1. Extract Skills (Global search)
        skills = self._parser_tool._extract_skills(description_lower)
        
        # 2. Extract Experience Years (Global search)
        experience_years = self._parser_tool._extract_experience(description_lower)
        
        # 3. Section Extraction (Heuristic)
        # Identify blocks for Education and Experience
        education_bullets = self._extract_section_bullets(text, ["education", "academic"])
        experience_bullets = self._extract_section_bullets(text, ["experience", "employment", "work history", "projects"])
        
        # 4. User Overrides
        visa_status = "US Citizen"
        role_family = "Software Engineer"
        
        if user_inputs:
            if "years_of_experience" in user_inputs:
                experience_years = float(user_inputs["years_of_experience"])
            if "visa_status" in user_inputs:
                visa_status = user_inputs["visa_status"]
            if "role" in user_inputs:
                role_family = user_inputs["role"]

        return NormalizedResume(
            skills=skills,
            years_of_experience=experience_years,
            visa_status=visa_status,
            role_family=role_family,
            education=education_bullets,
            experience_bullets=experience_bullets
        )

    def _extract_section_bullets(self, text: str, keywords: list) -> list:
        """
        Rough heuristic to find a section by keyword and extract lines that look like bullets.
        """
        lines = text.split('\n')
        in_section = False
        bullets = []
        
        for line in lines:
            clean_line = line.strip().lower()
            # Start of section?
            if any(k in clean_line for k in keywords) and len(clean_line) < 30:
                in_section = True
                continue
            
            # Use 'End' or next section header to stop?
            # Hard to guess next section, so we just grab valid bullets until we hit something that looks like a header
            if in_section:
                # Heuristic: Uppercase short line might be next header
                if line.strip().isupper() and len(line.strip()) < 20 and len(line.strip()) > 3:
                     # likely next header
                     in_section = False
                     continue
                
                # Bullet detection
                if line.strip().startswith(('•', '-', '*', '·')) or len(line.strip()) > 10:
                    bullets.append(line.strip())
        
        return bullets
