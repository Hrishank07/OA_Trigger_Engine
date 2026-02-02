import csv
from typing import List
from app.models.normalized_job import NormalizedJob
from app.models.job import Job

class CsvExporter:
    @staticmethod
    def export_with_scores(
        normalized_jobs: List[NormalizedJob], 
        original_jobs: List[Job], 
        scores: List[float],
        recommendations: List[str],
        filename: str = "jobs_export.csv"
    ):
        """
        Exports jobs to a CSV file includes OTPM scores.
        """
        
        # Create a lookup for original jobs
        job_map = {j.id: j for j in original_jobs}
        
        headers = [
            "Company", "Role", "Location", 
            "Status", "Posted Text",
            "OTPM Probability", "Recommendation",
            "Visa Sponsorship", "Experience (Years)", "Skills Found", 
            "URL"
        ]
        
        rows = []
        for i, n_job in enumerate(normalized_jobs):
            orig = job_map.get(n_job.job_id)
            if not orig: continue
            
            # Determine Status (Fresh vs Repost)
            status = "Fresh"
            posted_text = orig.raw_data.get("posted_text", "")
            if "repost" in posted_text.lower():
                status = "Repost"
            
            row = [
                orig.company,
                orig.title,
                orig.location,
                status,
                posted_text,
                f"{scores[i]:.2f}",
                recommendations[i],
                n_job.visa_sponsorship,
                n_job.experience_years,
                ", ".join(n_job.keywords),
                orig.url
            ]
            rows.append(row)
            
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            print(f"Successfully exported {len(rows)} jobs to {filename}")
        except Exception as e:
            print(f"Error exporting CSV: {e}")

    @staticmethod
    def export(normalized_jobs: List[NormalizedJob], original_jobs: List[Job], filename: str = "jobs_export.csv"):
        # Legacy support or redirect
        scores = [0.0] * len(normalized_jobs)
        recs = ["N/A"] * len(normalized_jobs)
        CsvExporter.export_with_scores(normalized_jobs, original_jobs, scores, recs, filename)
