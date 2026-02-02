from app.normalization.resume_parser import ResumeParser
import os
import sys

def verify_resume(filepath: str):
    parser = ResumeParser()
    try:
        print(f"Parsing: {filepath}")
        resume = parser.parse_file(filepath)
        
        print("\n--- Parsed Resume ---")
        print(f"Role Family: {resume.role_family}")
        print(f"Visa Status: {resume.visa_status} (Default)")
        print(f"Experience Years: {resume.years_of_experience}")
        print(f"Skills Found: {resume.skills}")
        print(f"Education Lines: {len(resume.education)}")
        print(f"Experience Bullets: {len(resume.experience_bullets)}")
        
        print("\n--- Top 3 Exp Bullets ---")
        for b in resume.experience_bullets[:3]:
            print(f"- {b}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Check resumes folder
    folder = "resumes"
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Created '{folder}' directory. Please put a PDF there.")
        sys.exit(0)
        
    files = [f for f in os.listdir(folder) if f.endswith(".pdf") or f.endswith(".txt")]
    if not files:
        print(f"No files found in '{folder}'. Please add a resume.")
        sys.exit(0)
    
    # Parse the first one found
    verify_resume(os.path.join(folder, files[0]))
