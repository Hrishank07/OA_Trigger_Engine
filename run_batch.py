import sys
import os
import time
from playwright.sync_api import sync_playwright
from app.scraping.linkedin import LinkedInScraper
from app.normalization.job_parser import JobParser
from app.storage.excel_exporter import ExcelExporter
from app.models.resume import NormalizedResume
from app.otpm.engine import OTPMEngine

def setup_resume():
    """Handles resume selection or manual input."""
    print("\n--- Resume Profile Setup ---")
    
    resume_folder = "resumes"
    if not os.path.exists(resume_folder):
        os.makedirs(resume_folder)
        
    resume_files = [f for f in os.listdir(resume_folder) if f.endswith(".pdf") or f.endswith(".txt")]
    resume = None
    from app.normalization.resume_parser import ResumeParser
    r_parser = ResumeParser()

    if resume_files:
        print("Found resumes:")
        for i, f in enumerate(resume_files):
            print(f"[{i+1}] {f}")
        
        choice = input("Select resume to use (number) or press Enter to skip: ").strip()
        if choice and choice.isdigit() and 1 <= int(choice) <= len(resume_files):
            selected_file = os.path.join(resume_folder, resume_files[int(choice)-1])
            print(f"Loading {selected_file}...")
            
            # Ask for overrides
            ov_exp = input("Override Years of Experience? (Enter number or skip): ").strip()
            ov_visa = input("Visa Status? (Type 'Visa Required' or 'US Citizen' [default Visa Required]): ").strip()
            
            user_inputs = {}
            if ov_exp: user_inputs["years_of_experience"] = ov_exp
            if ov_visa: user_inputs["visa_status"] = ov_visa
            
            try:
                resume = r_parser.parse_file(selected_file, user_inputs)
                print(f"Loaded Resume: {len(resume.skills)} skills, {resume.years_of_experience} years exp.")
            except Exception as e:
                print(f"Error parsing resume: {e}")
                resume = None
    
    if not resume:
        # Manual Fallback
        if not resume_files:
            print(f"No resumes found in '{resume_folder}/'. Using manual input.")
        else:
            print("Skipping file selection. Using manual input.")

        res_exp_str = input("Years of Experience (e.g. 0, 3, 5) [default 0]: ").strip()
        res_exp = float(res_exp_str) if res_exp_str else 0.0
        
        res_visa = input("Visa Status (Type 'Visa Required' or 'US Citizen' [default Visa Required]): ").strip()
        if not res_visa: res_visa = "Visa Required"
        
        res_skills_str = input("Top Skills (comma separated, e.g. Python, React, AWS): ").strip()
        res_skills = [s.strip().lower() for s in res_skills_str.split(",") if s.strip()]
        
        resume = NormalizedResume(
            years_of_experience=res_exp,
            visa_status=res_visa,
            skills=res_skills
        )
    return resume

def run_batch():
    print("OA Trigger Engine - Batch Search Mode")
    print("-" * 30)
    
    # 1. Select Mode
    print("Select Mode:")
    print("1) Scrape Only (Quick - No Analysis)")
    print("2) Scrape + Analyze (OTPM Score)")
    mode_choice = input("Choice (1/2) [default 2]: ").strip()
    mode = "analyze" if mode_choice != "1" else "scrape"
    
    # 2. Search Parameters
    query = input("Enter search keywords (e.g., 'Software Engineer') [default 'Software']: ").strip()
    if not query: query = "Software"
    
    location = input("Enter location (e.g., 'United States', 'Remote') [default 'United States']: ").strip()
    if not location: location = "United States"
    
    # Filter Prompts
    time_filter = input("Time Filter (e.g. 1h, 12h, 24h, week, month) [default '24h']: ").strip().lower()
    if not time_filter: time_filter = "24h"
    # Allow any input that ends with 'h' or matches keys
    if time_filter not in ["24h", "week", "month"] and not time_filter.endswith("h"): 
        print(f"Warning: Unknown time filter '{time_filter}', defaulting to 24h")
        time_filter = "24h"
    
    level_filter = input("Experience Level (internship/entry/associate/mid_senior [any]) [default 'entry']: ").strip().lower()
    if not level_filter: level_filter = "entry"
    
    # Limit Prompt
    limit_str = input("How many jobs to scrape? (number or 'all') [default 10]: ").strip().lower()
    if limit_str == "all":
        limit = 1000 # Practical safe cap
    else:
        try:
            limit = int(limit_str) if limit_str else 10
        except ValueError:
            limit = 10
            print("Invalid number, defaulting to 10.")
    
    filters = {}
    if time_filter: filters["time"] = time_filter
    if level_filter: filters["experience"] = [level_filter]
    
    # 3. Resume Setup (Only if Analyzing)
    resume = None
    otpm_engine = None
    
    if mode == "analyze":
        resume = setup_resume()
        otpm_engine = OTPMEngine()

    print(f"\nStarting batch process for: '{query}' in '{location}'...")
    print(f"Targeting {limit} jobs.")
    
    with sync_playwright() as p:
        # headless=False to see it working
        scraper = LinkedInScraper(p, headless=False)
        scraper.start_browser()
        
        # Search
        print("\nStep 1: Searching for jobs...")
        jobs_list, total_count_str = scraper.search_jobs(query, location, filters=filters, limit=limit)
        
        print(f"\n=== MATCH FOUND: {total_count_str} Total Jobs Available ===")
        
        if not jobs_list:
            print("No jobs found. Exiting.")
            return

        print(f"Found {len(jobs_list)} jobs (Top {limit}). Queueing for details...")
        
        full_jobs = []
        
        # Scrape Details
        print("\nStep 2: Scraping job details...")
        for i, search_result in enumerate(jobs_list):
            print(f"[{i+1}/{len(jobs_list)}] Scraping: {search_result.title} @ {search_result.company}")
            
            # Memory Safety
            if i > 0 and i % 5 == 0:
                 pass # LinkedInScraper manages page lifecycle per job, so we are safe.

            full_job = scraper.scrape_job(search_result.url)
            if full_job:
                if full_job.company == "Unknown Company": full_job.company = search_result.company
                if full_job.location == "Unknown Location": full_job.location = search_result.location
                full_jobs.append(full_job)
            else:
                print("   Failed to scrape details.")
            
            # Simple delay to be nice
            time.sleep(2)

        # Normalize & Analyze
        print("\nStep 3: Normalizing & Analyzing...")
        parser = JobParser()
        normalized_jobs = []
        otpm_scores = []
        recommendations = []
        
        for job in full_jobs:
            n_job = parser.parse(job)
            normalized_jobs.append(n_job)
            
            if mode == "analyze" and resume and otpm_engine:
                score = otpm_engine.calculate_probability(n_job, resume)
                rec = otpm_engine.get_recommendation(score)
                otpm_scores.append(score)
                recommendations.append(rec)
                print(f"   -> {job.company}: P(OA)={score:.2f} [{rec}]")
            else:
                otpm_scores.append(0.0)
                recommendations.append("N/A")
        
        # Export
        print("\nStep 4: Exporting to Excel...")
        filename = f"jobs_{query.replace(' ', '_')}.xlsx"
        ExcelExporter.export(normalized_jobs, full_jobs, otpm_scores, recommendations, filename)
        
        print("\nDone!")

if __name__ == "__main__":
    run_batch()
