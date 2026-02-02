import sys
from playwright.sync_api import sync_playwright
from app.scraping.linkedin import LinkedInScraper
from app.normalization.job_parser import JobParser
from app.storage.csv_exporter import CsvExporter

def run_batch():
    print("OA Trigger Engine - Batch Search Mode")
    print("-" * 30)
    
    query = input("Enter search keywords (e.g., 'Software Engineer'): ").strip()
    location = input("Enter location (e.g., 'United States', 'Remote'): ").strip()
    
    # Filter Prompts
    time_filter = input("Time Filter (24h/week/android [any]): ").strip().lower()
    if time_filter not in ["24h", "week"]: time_filter = None
    
    level_filter = input("Experience Level (internship/entry/associate/mid_senior [any]): ").strip().lower()
    
    # Limit Prompt
    try:
        limit_str = input("How many jobs to scrape? (default 10): ").strip()
        limit = int(limit_str) if limit_str else 10
    except ValueError:
        limit = 10
        print("Invalid number, defaulting to 10.")
    
    # allow comma separated? simple for now
    filters = {}
    if time_filter: filters["time"] = time_filter
    if level_filter: filters["experience"] = [level_filter]
    
    if not query or not location:
        print("Query and Location are required.")
        return

    print(f"\nStarting batch process for: '{query}' in '{location}'...")
    print(f"Targeting {limit} jobs.")
    
    with sync_playwright() as p:
        # headless=False to see it working and avoid basic blocks
        scraper = LinkedInScraper(p, headless=False)
        scraper.start_browser()
        
        # 1. Search
        print("\nStep 1: Searching for jobs...")
        jobs_list = scraper.search_jobs(query, location, filters=filters, limit=limit)
        
        if not jobs_list:
            print("No jobs found. Exiting.")
            return
            
        print(f"Found {len(jobs_list)} jobs. Queueing for details...")
        
        full_jobs = []
        
        # 2. Scrape Details
        print("\nStep 2: Scraping job details...")
        for i, search_result in enumerate(jobs_list):
            print(f"[{i+1}/{len(jobs_list)}] Scraping: {search_result.title} @ {search_result.company}")
            full_job = scraper.scrape_job(search_result.url)
            if full_job:
                # Merge metadata from search if scraped data missing (fallback)
                if full_job.company == "Unknown Company": full_job.company = search_result.company
                if full_job.location == "Unknown Location": full_job.location = search_result.location
                
                full_jobs.append(full_job)
            else:
                print("   Failed to scrape details.")
            
            # Simple delay to be nice
            scraper.get_page().wait_for_timeout(2000)

        # 3. Normalize
        print("\nStep 3: Normalizing data...")
        parser = JobParser()
        normalized_jobs = [parser.parse(job) for job in full_jobs]
        
        # 4. Export
        print("\nStep 4: Exporting to CSV...")
        filename = f"jobs_{query.replace(' ', '_')}.csv"
        CsvExporter.export(normalized_jobs, full_jobs, filename)
        
        print("\nDone!")

if __name__ == "__main__":
    run_batch()
