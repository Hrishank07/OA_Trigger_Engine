import sys
from playwright.sync_api import sync_playwright
from app.scraping.linkedin import LinkedInScraper

def verify_linkedin_scraping():
    url = input("Enter LinkedIn Job URL to scrape: ").strip()
    if not url:
        print("No URL provided.")
        return

    print(f"\nAttempting to scrape coverage for: {url}")
    print("Launching browser (headless=False) to observe...")

    with sync_playwright() as p:
        # Initialize with headless=False to see what happens
        scraper = LinkedInScraper(p, headless=False)
        scraper.start_browser()
        
        try:
            job = scraper.scrape_job(url)
            
            if job:
                print("\n✅ SUCCESS! Job Scraped:")
                print(f"Title: {job.title}")
                print(f"Company: {job.company}")
                print(f"Location: {job.location}")
                print(f"Description Length: {len(job.description)} chars")
                
                print("\n🧠 Normalizing...")
                from app.normalization.job_parser import JobParser
                parser = JobParser()
                normalized = parser.parse(job)
                
                print(f"Skills: {normalized.required_skills}")
                print(f"Experience: {normalized.experience_years} years")
                print(f"Visa Sponsorship: {normalized.visa_sponsorship}")
                
                print("-" * 20)
                print("Description Preview:")
                print(job.description[:500] + "...")
            else:
                print("\n❌ FAILED: Could not scrape job details.")
                
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
        finally:
            input("\nPress Enter to close browser...")
            scraper.stop_browser()

if __name__ == "__main__":
    verify_linkedin_scraping()
