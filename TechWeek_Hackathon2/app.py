import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
import os
import re
import google.generativeai as genai
from PIL import Image
import io
import json
from markdown_it import MarkdownIt

app = FastAPI()

# --- Configuration ---
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
md = MarkdownIt()

# Configure Gemini API at startup
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("ERROR: GEMINI_API_KEY environment variable not found.")

# --- Data Loading ---
try:
    job_data = pd.read_csv("datafile/job_applicant_dataset.csv")
except FileNotFoundError:
    print("Error: job_applicant_dataset.csv not found.")
    job_data = pd.DataFrame() # Create an empty dataframe to avoid errors

def get_job_roles():
    """Gets unique job roles from the dataset."""
    if not job_data.empty:
        return job_data["Job Roles"].unique().tolist()
    return []

# --- Helper Functions ---
def get_prompt(job_role):
    """Generates the prompt for the Gemini API."""
    required_skills_str = "Any"
    if not job_data.empty and job_role in job_data["Job Roles"].values:
        skills_series = job_data[job_data["Job Roles"] == job_role]["Resume"]
        if not skills_series.empty:
            required_skills_str = skills_series.iloc[0]

    prompt_template = '''
You are an expert career advisor and resume analyzer. 
The user uploads a resume image. 

Your task:
1. Extract all readable text from the resume.
2. Summarize the applicant’s background in structured form.
3. Compare the extracted skills and experiences with BOTH:
   - (a) the following job dataset information (if relevant): {skills_placeholder}
   - (b) general industry standards and best practices for the role.
4. Identify:
   - Skills the applicant already has (matched_skills)
   - Missing or weak skills the applicant needs (missing_skills)
   - Recommended next steps (recommendations)
   - Career positioning advice (career_positioning)

Output format:
(1) JSON (for backend processing)
```json
{{
  "resume_text": "...",
  "summary": {{
    "education": [],
    "experience": [],
    "skills": [],
    "certifications": []
  }},
  "analysis": {{
    "matched_skills": [],
    "missing_skills": [],
    "recommendations": [],
    "career_positioning": []
  }}
}}
```

(2) Human-Friendly Career Feedback (Markdown format, visually structured like a report card):

# 🔍 Your Profile Analysis

## ⚠️ Missing Skills
- List in bullet points

## 🎯 Recommendations
- Action items with **bold highlights** and clear next steps

## 🌟 Career Positioning Advice
- Practical tips on how to improve resume presentation, storytelling, or role positioning

'''
    return prompt_template.format(skills_placeholder=required_skills_str)

# --- API Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the home page."""
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/upload_page", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Serves the main page with job roles."""
    job_roles = get_job_roles()
    return templates.TemplateResponse("index.html", {"request": request, "job_roles": job_roles})

@app.post("/upload", response_class=HTMLResponse)
async def upload_resume(request: Request, resume: UploadFile = File(...), job_role: str = Form(...)):
    """Handles resume upload, analysis, and displays the result."""
    if not API_KEY:
        return templates.TemplateResponse("error.html", {"request": request, "message": "GEMINI_API_KEY environment variable not set."})
    
    try:
        print("Analyzing resume for job role:", job_role)
        model = genai.GenerativeModel('models/gemini-pro-latest')
        prompt = get_prompt(job_role)
        image_bytes = await resume.read()
        resume_image = Image.open(io.BytesIO(image_bytes))

        response = await model.generate_content_async([prompt, resume_image])
        text_response = response.text
        print("Analysis generated:", text_response)

        # --- Enhanced Parsing Logic ---
        json_part_str = "{}"
        try:
            json_match = re.search(r"```json\n(.*?)\n```", text_response, re.DOTALL)
            if json_match:
                json_part_str = json_match.group(1).strip()
        except Exception as e:
            print(f"JSON parsing regex failed: {e}")
        analysis_data = json.loads(json_part_str)
        print("Analysis data parsed:", analysis_data)

        def extract_section(header):
            try:
                # Use regex to find the header and capture content until the next header or end of string
                pattern = re.compile(f"## {re.escape(header)}\n(.*?)(?=\n## |$)", re.DOTALL)
                match = pattern.search(text_response)
                if match:
                    return md.render(match.group(1).strip())
            except Exception as e:
                print(f"Error extracting section {header}: {e}")
            return "<p>Content not available.</p>"

        recommendations_html = extract_section("🎯 Recommendations")
        career_advice_html = extract_section("🌟 Career Positioning Advice")

        # Calculate score for visualizations
        analysis_skills = analysis_data.get('analysis', {})
        matched_skills = analysis_skills.get('matched_skills', [])
        missing_skills = analysis_skills.get('missing_skills', [])
        matched_count = len(matched_skills)
        missing_count = len(missing_skills)
        total_skills = matched_count + missing_count
        score = (matched_count / total_skills) * 100 if total_skills > 0 else 0
        print("Score calculated:", score)

        return templates.TemplateResponse("result.html", {
            "request": request, 
            "filename": resume.filename, 
            "score": score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "recommendations_html": recommendations_html,
            "career_advice_html": career_advice_html,
            "analysis_data": analysis_data
        })

    except Exception as e:
        print(f"An error occurred: {e}")
        return templates.TemplateResponse("error.html", {"request": request, "message": f"An error occurred during analysis: {e}"})

@app.get("/career_roadmap", response_class=HTMLResponse)
async def career_roadmap_get(request: Request):
    return templates.TemplateResponse("career_roadmap.html", {"request": request, "roadmap": None})

@app.post("/career_roadmap", response_class=HTMLResponse)
async def career_roadmap_post(request: Request, current_job: str = Form(...)):
    """Generates and parses a career roadmap using the Gemini API."""
    if not API_KEY:
        return templates.TemplateResponse("error.html", {"request": request, "message": "GEMINI_API_KEY environment variable not set."})

    try:
        print(f"--- Generating roadmap for: {current_job} ---")
        model = genai.GenerativeModel('models/gemini-pro-latest')
        prompt = f"Generate a detailed career roadmap for a '{current_job}'. Provide the output as a single line of text, with each job and duration separated by a '|' character. For example: Junior Software Engineer (0-3 years) | Software Engineer (3-5 years) | Senior Software Engineer (5+ years)"
        print(f"Prompt: {prompt}")
        response = await model.generate_content_async(prompt)
        roadmap_text = response.text
        print(f"Roadmap generated (raw text): {roadmap_text}")

        # Parse the roadmap
        if '|' in roadmap_text:
            roadmap_parts = roadmap_text.split('|')
        else:
            roadmap_parts = re.split(r'→', roadmap_text)

        parsed_roadmap = []
        for part in roadmap_parts:
            part = part.strip()
            match = re.match(r'(.*?)\s*\((.*?)\)$', part)
            if match:
                job_title = match.group(1).strip()
                duration = match.group(2).strip()
                parsed_roadmap.append({"job": job_title, "duration": duration})
            else:
                # Handle cases where there is no duration
                parsed_roadmap.append({"job": part, "duration": None})
        
        print(f"Roadmap parsed: {parsed_roadmap}")
        print("--- Roadmap generation complete ---")

        return templates.TemplateResponse("career_roadmap.html", {"request": request, "roadmap": parsed_roadmap, "current_job": current_job})

    except Exception as e:
        print(f"An error occurred during roadmap generation: {e}")
        return templates.TemplateResponse("error.html", {"request": request, "message": f"An error occurred during roadmap generation: {e}"})

@app.get("/global_career_map", response_class=HTMLResponse)
async def global_career_map(request: Request):
    return templates.TemplateResponse("global_career_map.html", {"request": request})

@app.get("/suggested_career", response_class=HTMLResponse)
async def suggested_career_get(request: Request):
    return templates.TemplateResponse("suggested_career.html", {"request": request, "suggestions": None})

@app.post("/suggested_career", response_class=HTMLResponse)
async def suggested_career_post(request: Request, analysis_data: str = Form(...)):
    """Generates career suggestions based on resume analysis."""
    if not API_KEY:
        return templates.TemplateResponse("error.html", {"request": request, "message": "GEMINI_API_KEY not set."})

    try:
        analysis = json.loads(analysis_data)
        skills = analysis.get("summary", {}).get("skills", [])
        experience = analysis.get("summary", {}).get("experience", [])

        if not skills and not experience:
            return templates.TemplateResponse("suggested_career.html", {"request": request, "suggestions": []})

        print("Generating career suggestions for skills:", skills, "and experience:", experience)
        model = genai.GenerativeModel('models/gemini-pro-latest')
        prompt = f"Based on the following skills: {skills} and experience: {experience}, suggest 3 alternative career paths. For each path, provide a job title, a brief description, and why it might be a good fit."
        
        response = await model.generate_content_async(prompt)
        suggestions_text = response.text
        print("Suggestions generated:", suggestions_text)

        # Basic parsing of the response
        suggestions = []
        for suggestion_part in suggestions_text.split("\n\n"):
            lines = suggestion_part.strip().split('\n')
            if len(lines) >= 3:
                title = lines[0].replace("**", "").strip()
                description = lines[1].strip()
                fit = '\n'.join(lines[2:]).strip()
                suggestions.append({"title": title, "description": description, "fit": fit})

        print("Suggestions parsed:", suggestions)

        return templates.TemplateResponse("suggested_career.html", {"request": request, "suggestions": suggestions})

    except Exception as e:
        print(f"An error occurred: {e}")
        return templates.TemplateResponse("error.html", {"request": request, "message": f"Error: {e}"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)