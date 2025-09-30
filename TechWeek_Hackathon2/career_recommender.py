# career_recommender.py

import pandas as pd
import google.generativeai as genai
import re
import json
from typing import List

# --- Data Loading ---
try:
    job_data = pd.read_csv("datafile/job_applicant_dataset.csv")
    if 'Resume' in job_data.columns:
        job_data['Resume'] = job_data['Resume'].fillna('')
    else:
        print("Warning: 'Resume' column not found in dataset. Pre-filtering will not work.")
        job_data = pd.DataFrame()
except FileNotFoundError:
    print("Warning: datafile/job_applicant_dataset.csv not found. Recommender is disabled.")
    job_data = pd.DataFrame()

async def extract_skills_from_text(resume_text: str) -> List[str]:
    """Uses the AI to quickly extract a list of skills from raw resume text for filtering."""
    if not resume_text:
        return []
    try:
        model = genai.GenerativeModel('gemini-2.5-pro')
        prompt = f"From the following resume text, extract all key skills. Return them as a single, comma-separated string. Example: Python, SQL, Project Management, FastAPI.\n\nTEXT: \"{resume_text}\""
        response = await model.generate_content_async(prompt)
        skills = [skill.strip() for skill in response.text.split(',')]
        return skills
    except Exception as e:
        print(f"Error extracting skills: {e}")
        return []

def find_top_matching_jobs(user_skills: List[str], top_n: int = 10) -> List[str]:
    """Performs a pre-filtering step to find the most relevant jobs from the CSV."""
    if job_data.empty or 'Resume' not in job_data.columns or not user_skills:
        return []
    user_skills_set = {skill.lower() for skill in user_skills}
    def calculate_match_score(job_skills_str: str) -> int:
        job_skills = {skill.strip().lower() for skill in job_skills_str.split(',')}
        return len(user_skills_set.intersection(job_skills))
    job_data['match_score'] = job_data['Resume'].apply(calculate_match_score)
    top_jobs = job_data.sort_values(by='match_score', ascending=False).head(top_n)
    return top_jobs["Job Roles"].tolist()

def create_recommendation_prompt(resume_text: str, relevant_jobs: List[str]) -> str:
    """Creates the final prompt using the full resume text and a pre-filtered job list."""
    return f"""
You are an expert AI career counselor. Analyze the candidate's resume text and recommend the most suitable careers

**Candidate's Full Resume Text:**
---
{resume_text}
---

**Your Task:**
1.  Deeply analyze the candidate's experience and skills from their full resume text.
2. Provide the top 3 career recommendations.
3.  For each recommendation, provide a "match_score" (a percentage from 0-100) and a brief "justification".
4.  **Strictly** provide your output as a single, clean JSON object.

**JSON Output Format:**
```json
{{
  "recommendations": [
    {{ "job_title": "...", "match_score": 90, "justification": "..." }},
    {{ "job_title": "...", "match_score": 82, "justification": "..." }},
    {{ "job_title": "...", "match_score": 75, "justification": "..." }}
  ]
}}

"""

async def recommend_careers(resume_text: str) -> List[dict]:
    """The main function to generate dataset-specific recommendations from raw resume text."""
    try:
        extracted_skills = await extract_skills_from_text(resume_text)
        relevant_job_titles = find_top_matching_jobs(extracted_skills, top_n=10)

        if not relevant_job_titles:
            return []

        prompt = create_recommendation_prompt(resume_text, relevant_job_titles)
        model = genai.GenerativeModel('gemini-2.5-pro')
        response = await model.generate_content_async(prompt)

        match = re.search(r"```json\n(.*?)\n```", response.text, re.DOTALL)
        json_str = match.group(1) if match else response.text
        parsed_json = json.loads(json_str)
        return parsed_json.get("recommendations", [])

    except Exception as e:
        print(f"Error in recommend_careers: {e}")
        return []
