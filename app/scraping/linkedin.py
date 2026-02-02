from typing import List, Optional
from app.models.job import Job
from app.scraping.base import BaseScraper

class LinkedInScraper(BaseScraper):
    def start_browser(self):
        # Override to inject random User-Agent
        from fake_useragent import UserAgent
        ua = UserAgent()
        user_agent = ua.random
        print(f"Starting browser with UA: {user_agent}")
        super().start_browser(user_agent=user_agent)

    def _jitter(self, min_sec: float = 2.0, max_sec: float = 5.0):
        """Random sleep to mimic human behavior."""
        import time
        import random
        sleep_time = random.uniform(min_sec, max_sec)
        print(f"Sleeping for {sleep_time:.2f}s...")
        time.sleep(sleep_time)

    def scrape_job(self, url: str) -> Optional[Job]:
        """
        Scrapes a LinkedIn job posting.
        Note: LinkedIn acts differently for logged-in vs public views.
        This focuses on the public job view.
        """
        print(f"Scraping LinkedIn URL: {url}")
        
        # Jitter before action
        self._jitter(1.0, 3.0)
        
        page = self.get_page()
        try:
            # direct navigation to the job URL
            # Reduced timeout to 15s to fail fast
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # Simple check to see if we got a job page or auth wall
            # Common public job page selectors
            try:
                # Wait for title to appear
                page.wait_for_selector(".top-card-layout__title, h1", timeout=5000)
            except Exception:
                print("Could not find job title - possibly auth walled or invalid URL")
                return None

            title = page.locator(".top-card-layout__title").first.or_(page.locator("h1").first).inner_text().strip()
            
            # Company
            # Strategy: Try multiple specific selectors, fallback to anything that looks like a company link/text
            company_selectors = [
                ".top-card-layout__first-subline .topcard__org-name-link",
                ".job-details-jobs-unified-top-card__company-name",
                ".topcard__org-name-link",
                "a[data-tracking-control-name='public_jobs_topcard-org-name']"
            ]
            company = "Unknown Company"
            for selector in company_selectors:
                el = page.locator(selector).first
                if el.count():
                    company = el.inner_text().strip()
                    break

            # Location
            location_selectors = [
                ".top-card-layout__first-subline .topcard__flavor--bullet",
                ".job-details-jobs-unified-top-card__primary-description span",
                "span.topcard__flavor--bullet"
            ]
            
            location = "Unknown Location"
            for selector in location_selectors:
                el = page.locator(selector).first
                if el.count():
                    location = el.inner_text().strip()
                    break

            # Description (using html2text to clean)
            import html2text
            h = html2text.HTML2Text()
            h.ignore_links = True
            
            # Show more button might need clicking if it exists, though usually full text is in DOM
            # .show-more-less-html__markup is common for public pages
            desc_locator = page.locator(".show-more-less-html__markup").first
            if not desc_locator.count():
                 desc_locator = page.locator("#job-details").first
            
            raw_html = desc_locator.inner_html() if desc_locator.count() else ""
            description = h.handle(raw_html)
            
            # Jitter inside page just in case we need to act more human
            self._jitter(0.5, 1.5)

            return Job(
                id=url, # using URL as ID for now
                title=title,
                company=company,
                location=location,
                description=description,
                url=url,
                source="linkedin",
                raw_data={"html_content_length": len(raw_html)}
            )

        except Exception as e:
            print(f"Error scraping LinkedIn: {e}")
            return None
        finally:
            page.close()

    def search_jobs(self, query: str, location: str, filters: dict = None, limit: int = 10) -> List[Job]:
        """
        Searches for jobs on LinkedIn (public view) with filters.
        filters: dict with keys 'time' (str), 'experience' (List[str])
        """
        print(f"Searching LinkedIn for '{query}' in '{location}' with filters: {filters}")
        page = self.get_page()
        jobs_found = []
        
        try:
            # Construct search URL
            base_url = "https://www.linkedin.com/jobs/search"
            params = [
                f"keywords={query}",
                f"location={location}"
            ]
            
            if filters:
                # Time filter
                if filters.get("time") == "24h":
                    params.append("f_TPR=r86400")
                elif filters.get("time") == "week":
                     params.append("f_TPR=r604800")
                     
                # Experience filter
                # 1=Internship, 2=Entry level, 3=Associate, 4=Mid-Senior, 5=Director, 6=Executive
                # LinkedIn joins these with commas: f_E=2,3
                exp_map = {
                    "internship": "1",
                    "entry": "2",
                    "associate": "3",
                    "mid_senior": "4",
                    "director": "5"
                }
                exp_vals = []
                for level in filters.get("experience", []):
                    if val := exp_map.get(level.lower()):
                        exp_vals.append(val)
                
                if exp_vals:
                    params.append(f"f_E={','.join(exp_vals)}")

            search_url = f"{base_url}?{'&'.join(params)}"
            print(f"URL: {search_url}")
            
            self._jitter(1.0, 2.0)
            page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
            
            # Extract Total Job Count (Best Attempt)
            total_jobs_text = "Unknown"
            try:
                # Selectors for result count: usually "1,000+" or "54"
                count_el = page.locator(".results-context-header__job-count").first
                if count_el.count():
                    total_jobs_text = count_el.inner_text().strip()
            except:
                pass
            
            print(f"Indices say: {total_jobs_text} total jobs found.")

            # Wait for job list to load
            try:
                page.wait_for_selector(".jobs-search__results-list li, ul.jobs-search__results-list", timeout=10000)
            except:
                print("No results found or page structure changed.")
                return []

            # Dynamic Scroll Loop
            # We want to load enough jobs to satisfy 'limit'.
            # LinkedIn loads ~25 jobs per scroll usually.
            print(f"Scrolling to load at least {limit} jobs...")
            
            current_count = 0
            retries = 0
            while current_count < limit and retries < 5:
                # Scroll to bottom
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                self._jitter(1.5, 3.0)
                
                # Check new count
                job_cards_locator = page.locator(".jobs-search__results-list li")
                new_count = job_cards_locator.count()
                
                if new_count == current_count:
                    # No new jobs loaded? Try 'See more' button if exists
                    try:
                        see_more_btn = page.locator("button.infinite-scroller__show-more-button").first
                        if see_more_btn.count() and see_more_btn.is_visible():
                            print("Clicking 'See more jobs' button...")
                            see_more_btn.click()
                            self._jitter(2.0, 4.0)
                        else:
                            retries += 1
                    except:
                        retries += 1
                else:
                    retries = 0 # Reset retries if we found more jobs
                    print(f"Loaded {new_count} jobs so far...")
                
                current_count = new_count
                
                # Safety break
                if retries >= 3:
                     print("Suggests end of list or stuck. Stopping scroll.")
                     break

            # Extract job cards
            job_cards = page.locator(".jobs-search__results-list li")
            count = job_cards.count()
            print(f"Final Count on Page: {count}. Processing top {limit}...")

            for i in range(min(count, limit)):
                card = job_cards.nth(i)
                try:
                    # Link usually is in an 'a' tag with class 'base-card__full-link' or similar
                    link_el = card.locator("a.base-card__full-link").first
                    if not link_el.count():
                         link_el = card.locator("a").first # Fallback
                    
                    url = link_el.get_attribute("href")
                    if not url: continue
                    
                    # Clean URL (remove tracking params)
                    if "?" in url:
                        url = url.split("?")[0]
                        
                    title = card.locator(".base-search-card__title").first.inner_text().strip()
                    company = card.locator(".base-search-card__subtitle").first.inner_text().strip()
                    
                    # Extract "posted" text for Repost detection
                    # Usually in a 'time' tag or '.job-search-card__listdate'
                    posted_text = ""
                    time_el = card.locator("time").first
                    if time_el.count():
                        posted_text = time_el.inner_text().strip()
                    
                    # Create placeholder job
                    jobs_found.append(Job(
                        id=url, 
                        title=title,
                        company=company,
                        location=location, # Default to search loc if specific not found
                        description="", # Empty for now
                        url=url,
                        source="linkedin",
                        raw_data={"posted_text": posted_text}
                    ))
                    
                except Exception as e:
                    print(f"Error parsing card {i}: {e}")
                    continue

            return jobs_found

        except Exception as e:
            print(f"Error during search: {e}")
            return []
        finally:
            page.close()
