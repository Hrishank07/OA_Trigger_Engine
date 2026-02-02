# OA Trigger Engine

## Overview

**OA Trigger Engine** is a local-first analysis system designed to estimate the likelihood that a resume will trigger an **Online Assessment (OA)** during the initial stages of job screening.

The system scrapes publicly available job postings, normalizes them using **ATS-aligned heuristics**, and evaluates them against a candidate profile to produce an **OA Trigger Probability Metric (OTPM)**. The output is intended to help candidates prioritize applications where automated screening is most likely to advance them to the next stage.

The project is designed to run entirely on a local machine, with no mandatory cloud dependencies.

---

## Problem Statement

Modern hiring pipelines rely heavily on automated systems:

- Applicant Tracking Systems (ATS) apply hard thresholds on skills, experience, and keywords
- Recruiters perform rapid, shallow resume reviews
- Most rejections occur before any interview or human interaction

As a result, candidates lack visibility into which applications are worth pursuing.

This project addresses the following question:

> *Given a resume and a job posting, how likely is it that the application will trigger an Online Assessment or initial screening action?*

---

## System Architecture

The system follows a standard extract–transform–analyze pipeline:

Scrape → Normalize → OTPM Evaluation → Recommendation → Export


### Pipeline Stages

1. **Scrape**
   - Collects job postings and full descriptions from job boards using headless browser automation.
   - Focuses on publicly accessible job listings.

2. **Normalize**
   - Converts unstructured job descriptions into structured, ATS-style representations.
   - Extracts required skills, experience thresholds, visa signals, seniority indicators, and other screening-relevant attributes.

3. **OTPM Evaluation**
   - Applies deterministic, threshold-aware logic to compare a normalized job against a normalized resume.
   - Produces a probability estimate representing the likelihood of triggering an OA.

4. **Recommendation**
   - Translates the probability estimate and metadata into actionable guidance (e.g., apply, deprioritize, skip).

5. **Export**
   - Outputs results in CSV format for manual review and tracking.

---

## Core Metric: OTPM

### OA Trigger Probability Metric (OTPM)

OTPM estimates:

P(OA triggered | resume, job, ATS logic + initial recruiter skim)


Key characteristics:
- Output range: `0.0 – 1.0`
- Threshold-aware (mirrors ATS behavior rather than linear scoring)
- Deterministic and explainable
- Focused exclusively on **pre-interview screening**

OTPM is **not**:
- A job fit score
- An interview success predictor
- A resume quality metric

---

## Normalization Logic

Normalization is intentionally rule-based and ATS-aligned.

### Job Normalization Includes:
- Required vs preferred skill extraction
- Minimum experience parsing (e.g., “3+ years”, “5–7 years”)
- Role family and seniority inference
- Visa sponsorship signals
- Entry-level vs experienced-role classification
- Repost vs fresh posting detection

### Resume Normalization Includes:
- Experience bullet extraction
- Skill and keyword indexing
- Experience duration estimation
- Title and role-family mapping
- Parsing integrity checks

---

## Key Features

### Job Scraping
- Batch scraping by keyword and location
- Support for time-based filters (e.g., past 24 hours)
- Pagination and dynamic scrolling support
- Public-view scraping only

### Robustness and Safety
- User-agent rotation
- Randomized delays between actions
- Aggressive timeouts to avoid hanging sessions
- Designed for low-frequency, personal use

### Output and Review
- CSV-based output for transparency
- Clear columns describing job attributes and screening signals
- No automatic application submission

---

## Technology Stack

- **Language**: Python 3.12+
- **Browser Automation**: Playwright
- **Data Modeling**: Pydantic
- **Parsing**: Regex and heuristic rules
- **Storage / Output**: CSV (local filesystem)

---
