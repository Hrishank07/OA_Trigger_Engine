import pandas as pd
from typing import List
from app.models.job import Job
from app.models.normalized_job import NormalizedJob

class ExcelExporter:
    @staticmethod
    def export(
        normalized_jobs: List[NormalizedJob], 
        original_jobs: List[Job], 
        scores: List[float] = None,
        recommendations: List[str] = None,
        filename: str = "jobs_export.xlsx"
    ):
        """
        Exports jobs to an Excel file with two sheets: 
        1. 'Jobs': The detailed list.
        2. 'Analysis': Summary statistics.
        """
        
        # 1. Prepare Data for 'Jobs' Sheet
        job_map = {j.id: j for j in original_jobs}
        data = []
        
        if not scores: scores = [0.0] * len(normalized_jobs)
        if not recommendations: recommendations = ["N/A"] * len(normalized_jobs)
        
        for i, n_job in enumerate(normalized_jobs):
            orig = job_map.get(n_job.job_id)
            if not orig: continue
            
            # Repost Check
            posted_text = orig.raw_data.get("posted_text", "")
            status = "Repost" if "repost" in posted_text.lower() else "Fresh"
            
            data.append({
                "Company": orig.company,
                "Role": orig.title,
                "Location": orig.location,
                "Status": status,
                "Posted Text": posted_text,
                "OTPM Probability": float(f"{scores[i]:.2f}"),
                "Recommendation": recommendations[i],
                "Visa Sponsorship": n_job.visa_sponsorship,
                "Experience Years": n_job.experience_years,
                "Skills Found": ", ".join(n_job.keywords),
                "URL": orig.url
            })
            
        df_jobs = pd.DataFrame(data)
        
        # 2. Prepare Data for 'Analysis' Sheet
        # Stats: Total Jobs, Fresh vs Repost, Avg OTPM, Visa Friendly Count, Top Skills
        
        total_jobs = len(df_jobs)
        fresh_count = len(df_jobs[df_jobs["Status"] == "Fresh"]) if not df_jobs.empty else 0
        repost_count = total_jobs - fresh_count
        avg_score = df_jobs["OTPM Probability"].mean() if not df_jobs.empty else 0.0
        
        strong_apply_count = len(df_jobs[df_jobs["Recommendation"] == "STRONG APPLY"]) if not df_jobs.empty else 0
        apply_count = len(df_jobs[df_jobs["Recommendation"] == "APPLY"]) if not df_jobs.empty else 0
        
        # Frequency of extracted skills
        all_skills = []
        for s_str in df_jobs["Skills Found"]:
             if s_str:
                 all_skills.extend([s.strip() for s in s_str.split(",") if s.strip()])
        
        from collections import Counter
        skill_counts = Counter(all_skills).most_common(5)
        top_skills_str = ", ".join([f"{k} ({v})" for k,v in skill_counts])
        
        analysis_data = [
            {"Metric": "Total Jobs Found", "Value": total_jobs},
            {"Metric": "Fresh Jobs", "Value": fresh_count},
            {"Metric": "Reposts", "Value": repost_count},
            {"Metric": "Average OTPM Score", "Value": f"{avg_score:.2f}"},
            {"Metric": "Strong Apply Candidates", "Value": strong_apply_count},
            {"Metric": "Apply Candidates", "Value": apply_count},
            {"Metric": "Top 5 Needed Skills", "Value": top_skills_str}
        ]
        df_analysis = pd.DataFrame(analysis_data)
        
        # 3. Write to Excel
        try:
            # Ensure filename ends with .xlsx
            if not filename.endswith(".xlsx"):
                filename = filename.replace(".csv", "") + ".xlsx"
                
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df_jobs.to_excel(writer, sheet_name='Jobs', index=False)
                df_analysis.to_excel(writer, sheet_name='Analysis', index=False)
                
            print(f"Successfully exported {len(data)} jobs to {filename}")
        except Exception as e:
            print(f"Error exporting Excel: {e}")
