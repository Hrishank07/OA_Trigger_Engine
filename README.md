# OA Trigger Engine

## 📌 Overview

**OA Trigger Engine** is a local-first system that emulates how modern **ATS (Applicant Tracking Systems)** and **initial recruiter screening** work, with one clear goal:

> **Estimate the probability that a given resume will trigger an Online Assessment (OA) for a specific job posting.**

Instead of generic “job fit” scores, this project focuses on the **earliest and most critical funnel stage** in modern hiring:  
**getting past automated screening and triggering an OA or recruiter action.**

---

## 🎯 Problem This Project Solves

In today’s job market:

- ATS systems filter resumes using **hard thresholds** (skills, experience, keywords)
- Recruiters skim resumes in **5–8 seconds**
- Most rejections happen **before any human interview**

Job seekers waste time applying blindly.

This project answers a more practical question:

> *“Given my resume, which jobs am I most likely to get an OA from?”*

---

## 🧠 Core Concept: OTPM

### OA Trigger Probability Metric (OTPM)

OTPM is the **core scoring function** of this system.

It estimates:

```

P(OA triggered | resume, job, ATS logic + human skim)

```

OTPM is:
- **Probabilistic** (0.0 → 1.0)
- **Threshold-aware** (mirrors ATS behavior)
- **Explainable** (clear breakdown of why a job is recommended or skipped)

OTPM is **not**:
- A job-fit score
- An interview probability
- A resume quality metric

---

## 🔁 End-to-End Pipeline

```

SCRAPE → NORMALIZE → COMPARE (OTPM) → RECOMMEND

```

### 1. Scrape
- Collect jobs opened recently from:
  - LinkedIn
  - Jobright
  - Simplify
- Extract full job descriptions and metadata

### 2. Normalize (ATS-style)
- Convert raw text into structured fields:
  - Required skills
  - Preferred skills
  - Experience requirements
  - Role family & seniority
  - Visa / location signals
  - New-grad vs experienced friendliness

### 3. Compare (OTPM Engine)
- Compare a normalized job against a normalized resume
- Apply ATS-like thresholds for:
  - Required skills
  - Required experience
- Incorporate human skim signals:
  - Title alignment
  - Stack salience in top bullets
- Output OA trigger probability

### 4. Recommend
- Translate OTPM + metadata into clear actions:
  - **STRONG APPLY**
  - **APPLY**
  - **LOW PRIORITY**
  - **SKIP**
- Include tags like:
  - Visa sponsorship likelihood
  - New-grad / experienced friendliness
  - Risk flags

---

## 🏗️ System Design Principles

- **Local-first**: Runs on a student’s machine
- **Free-first**: No paid cloud dependencies
- **Deterministic by default**: Same input → same output
- **Explainable**: Every score has a reason
- **Extensible**: Learning, calibration, and auto-tailoring can be added later

---

## 🧱 Project Structure

```

oa-trigger-engine/
│
├── app/
│   ├── scraping/        # Job scrapers
│   ├── normalization/   # ATS-style parsing & extraction
│   ├── otpm/            # OA Trigger Probability Metric (core logic)
│   ├── recommendation/  # Decision engine
│   ├── models/          # Typed schemas (jobs, resume, results)
│   ├── storage/         # SQLite persistence
│   └── main.py          # Entry point
│
├── data/                # Local data storage (ignored by git)
├── requirements.txt
├── .env
└── README.md

````

---

## 🧮 OTPM Signals (High-Level)

OTPM is derived from five primary signals:

1. **Required Skill Threshold** (ATS gate)
2. **Required Experience Threshold** (ATS gate)
3. **ATS Keyword Density** (parsing & automation)
4. **Title / Role Family Match** (human skim)
5. **Stack Salience in Top Resume Bullets** (human skim)

Hard failures (e.g., missing skills, visa mismatch) sharply reduce probability.

---

## 📤 Output Example

```json
{
  "company": "Stripe",
  "role": "Software Engineer II",
  "oa_trigger_probability": 0.78,
  "recommendation": "STRONG APPLY",
  "visa_sponsorship": "LIKELY",
  "experienced_friendly": true,
  "summary": "Strong skill and experience match; clear backend alignment"
}
````

---

## 🧑🎓 Target Users

* Students and early-career engineers
* International students navigating visa constraints
* Anyone applying to high-volume tech roles with OAs

---

## 🚫 What This Project Is Not

* Not an auto-apply bot (yet)
* Not a resume generator
* Not a recruiter replacement
* Not a guarantee of interviews

This is a **decision-support system**, not a magic button.

---

## 🛣️ Future Extensions

* Outcome-based calibration (learn from OA results)
* Company-specific ATS heuristics
* Resume keyword injection / tailoring
* Auto-apply integration
* Simple web dashboard

---

## ⚖️ Disclaimer

This project is for **educational and personal use only**.
It does not scrape or interact with platforms in ways intended to bypass security controls.

---

## 🧠 One-Line Summary

> **OA Trigger Engine helps you apply smarter by estimating which jobs are most likely to give you an Online Assessment.**
