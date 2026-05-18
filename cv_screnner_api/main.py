"""
TalentIQ — AI CV Screener API
==============================
FastAPI backend — production ready
Endpoints:
  POST /api/screen     → Upload CVs + job → get top N candidates
  POST /api/parse-cv   → Parse single CV → structured JSON
  POST /api/parse-job  → Parse job description → structured JSON
  GET  /api/health     → Health check
  GET  /docs           → Swagger UI
"""

import re
import io
import json
import datetime
import warnings
warnings.filterwarnings("ignore")

from typing import List, Optional, Dict, Any
from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ── Lazy-load heavy models ────────────────────────────────────
_nlp        = None
_sbert      = None
_models_ready = False

def get_nlp():
    global _nlp
    if _nlp is None:
        import spacy
        try:    _nlp = spacy.load("en_core_web_sm")
        except: _nlp = spacy.load("fr_core_news_sm")
    return _nlp

def get_sbert():
    global _sbert
    if _sbert is None:
        from sentence_transformers import SentenceTransformer
        _sbert = SentenceTransformer("all-MiniLM-L6-v2")
    return _sbert


# ═══════════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════════
app = FastAPI(
    title="TalentIQ CV Screener API",
    description="AI-powered CV screening and candidate ranking",
    version="2.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════
# PYDANTIC SCHEMAS
# ═══════════════════════════════════════════════════════════════
class JobInput(BaseModel):
    title: str
    description: str = ""
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    required_degree: str = "bachelor"
    required_experience_min: float = 0
    required_experience_max: float = 99
    top_n: int = 10

class CandidateResult(BaseModel):
    rank: int
    candidate_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    score: float
    semantic_score: float
    skill_score: float
    experience_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    experience_years: float
    education_level: str
    certifications: List[str]
    languages: List[str]
    linkedin: Optional[str]
    github: Optional[str]
    filename: str

class ScreenResponse(BaseModel):
    job_title: str
    total_cvs_processed: int
    top_candidates: List[CandidateResult]
    processing_time_seconds: float


# ═══════════════════════════════════════════════════════════════
# SKILL SYNONYMS
# ═══════════════════════════════════════════════════════════════
SKILL_SYNONYMS: Dict[str, List[str]] = {
    "python":           ["py","python3","python 3"],
    "javascript":       ["js","vanilla js","es6","ecmascript"],
    "typescript":       ["ts","type script"],
    "java":             ["java ee","java se","core java","j2ee"],
    "c++":              ["cpp","c plus plus"],
    "c#":               ["csharp","c sharp"],
    "r":                ["r language","rstudio","tidyverse"],
    "go":               ["golang","go lang"],
    "rust":             ["rust lang"],
    "php":              ["php7","php8"],
    "ruby":             ["ruby on rails","rails","ror"],
    "shell":            ["bash","shell script","zsh"],
    "sql":              ["structured query language","t-sql","pl/sql","sequel"],
    "mysql":            ["my sql"],
    "postgresql":       ["postgres","pg","postgre","psql"],
    "mongodb":          ["mongo","mongo db"],
    "redis":            ["redis cache"],
    "elasticsearch":    ["elastic search","elastic"],
    "pandas":           ["pd"],
    "numpy":            ["np"],
    "matplotlib":       ["mpl","pyplot"],
    "seaborn":          ["sns"],
    "plotly":           ["plotly express"],
    "power bi":         ["powerbi","power-bi","pbi","microsoft power bi","msbi"],
    "tableau":          ["tableau desktop","tableau public","tableau server"],
    "excel":            ["ms excel","microsoft excel","vba excel"],
    "google sheets":    ["gsheets","google spreadsheet"],
    "looker":           ["looker studio","google data studio","data studio"],
    "qlik":             ["qlikview","qlik sense"],
    "apache spark":     ["spark","pyspark","spark sql"],
    "hadoop":           ["apache hadoop","hdfs","mapreduce"],
    "kafka":            ["apache kafka"],
    "airflow":          ["apache airflow"],
    "dbt":              ["data build tool"],
    "databricks":       ["azure databricks"],
    "snowflake":        ["snowflake db"],
    "bigquery":         ["google bigquery","gcp bigquery"],
    "machine learning": ["ml","machine-learning","apprentissage automatique"],
    "deep learning":    ["dl","deep-learning","neural networks"],
    "scikit-learn":     ["sklearn","scikit learn"],
    "tensorflow":       ["tf","tensorflow2"],
    "pytorch":          ["torch"],
    "keras":            ["keras api"],
    "xgboost":          ["xgb"],
    "natural language processing": ["nlp","text mining","text analysis"],
    "computer vision":  ["image recognition","object detection","image processing"],
    "bert":             ["roberta","distilbert","camembert"],
    "transformers":     ["hugging face","huggingface"],
    "opencv":           ["cv2","open cv"],
    "data visualization": ["data viz","dataviz","built dashboards",
                           "interactive dashboards","dashboard creation","visualisation"],
    "react":            ["react.js","reactjs","react js"],
    "vue":              ["vue.js","vuejs"],
    "angular":          ["angular.js","angularjs"],
    "next.js":          ["nextjs","next js"],
    "node.js":          ["nodejs","node js","node","express.js"],
    "django":           ["django rest","drf"],
    "fastapi":          ["fast api"],
    "flask":            ["flask python"],
    "spring":           ["spring boot","springframework"],
    "rest api":         ["restful","api rest","restful api","web api"],
    "docker":           ["docker container","dockerfile","docker-compose","containerization"],
    "kubernetes":       ["k8s","kubectl","kube","helm"],
    "aws":              ["amazon web services","amazon cloud","ec2","s3","lambda"],
    "azure":            ["microsoft azure","azure devops"],
    "google cloud":     ["gcp","google cloud platform"],
    "terraform":        ["hashicorp terraform","infrastructure as code","iac"],
    "ci/cd":            ["cicd","continuous integration","continuous delivery","github actions","gitlab ci"],
    "linux":            ["ubuntu","debian","centos","unix"],
    "git":              ["github","gitlab","bitbucket","version control"],
    "figma":            ["figma design"],
    "adobe xd":         ["xd","adobexd"],
    "photoshop":        ["adobe photoshop"],
    "react native":     ["reactnative","react-native"],
    "flutter":          ["flutter framework"],
    "android":          ["android studio","android sdk"],
    "ios":              ["xcode","objective-c"],
    "firebase":         ["google firebase"],
    "agile":            ["scrum","kanban","sprint","agile methodology"],
    "autocad":          ["auto cad","autocad 2d","autocad 3d"],
    "revit":            ["autodesk revit","bim revit"],
    "solidworks":       ["solid works"],
    "matlab":           ["matlab simulink"],
    "sap":              ["sap erp","sap s/4hana","sap fi"],
    "excel":            ["ms excel","microsoft excel","vba excel","spreadsheet"],
    "powerpoint":       ["ms ppt","ppt","microsoft powerpoint","power point"],
    "google analytics": ["ga","ga4","google analytics 4"],
    "google ads":       ["google adwords","adwords"],
}

SYNONYM_LOOKUP: Dict[str, str] = {}
for canonical, synonyms in SKILL_SYNONYMS.items():
    SYNONYM_LOOKUP[canonical.lower()] = canonical
    for syn in synonyms:
        SYNONYM_LOOKUP[syn.lower()] = canonical

EDU_RANK_MAP = {"phd":5,"master":4,"bachelor":3,"associate":2,"high_school":1,"other":0,"any":0}
MONTHS_MAP = {
    "january":1,"february":2,"march":3,"april":4,"may":5,"june":6,
    "july":7,"august":8,"september":9,"october":10,"november":11,"december":12,
    "jan":1,"feb":2,"mar":3,"apr":4,"jun":6,"jul":7,"aug":8,
    "sep":9,"oct":10,"nov":11,"dec":12,
    "janvier":1,"février":2,"mars":3,"avril":4,"mai":5,"juin":6,
    "juillet":7,"août":8,"septembre":9,"octobre":10,"novembre":11,"décembre":12,
}


# ═══════════════════════════════════════════════════════════════
# SKILL HELPERS
# ═══════════════════════════════════════════════════════════════
def normalize_skill(skill: str) -> str:
    return SYNONYM_LOOKUP.get(skill.strip().lower(), skill.strip().lower())

def normalize_skills_list(skills: List[str]) -> List[str]:
    return sorted(set(normalize_skill(s) for s in skills if s.strip()))

def extract_skills_from_text(text: str) -> List[str]:
    text_lower = text.lower()
    found = set()
    for syn in sorted(SYNONYM_LOOKUP.keys(), key=len, reverse=True):
        pattern = r"(?<![a-z0-9\-])" + re.escape(syn) + r"(?![a-z0-9\-])"
        if re.search(pattern, text_lower):
            found.add(SYNONYM_LOOKUP[syn])
    return sorted(found)

def fuzzy_skill_match(skill: str, candidates: List[str], threshold: int = 82) -> Optional[str]:
    from rapidfuzz import fuzz, process
    if not candidates: return None
    result = process.extractOne(skill, candidates, scorer=fuzz.token_sort_ratio)
    return result[0] if result and result[1] >= threshold else None


# ═══════════════════════════════════════════════════════════════
# CV PARSERS
# ═══════════════════════════════════════════════════════════════
def extract_text(file_bytes: bytes, filename: str) -> str:
    fname = filename.lower()
    if fname.endswith(".pdf"):
        import pdfplumber
        text = ""
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: text += t + "\n"
        return text.strip()
    elif fname.endswith((".docx", ".doc")):
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    else:
        return file_bytes.decode("utf-8", errors="ignore")

def extract_email(text: str) -> Optional[str]:
    m = re.search(r"[\w._%+\-]+@[\w.\-]+\.[a-zA-Z]{2,}", text)
    return m.group(0).lower() if m else None

def extract_phone(text: str) -> Optional[str]:
    m = re.search(r"(\+?[\d][\d\s\-.]{7,14}[\d])", text)
    return m.group(0).strip() if m else None

def extract_name(text: str) -> Optional[str]:
    nlp = get_nlp()
    if nlp:
        doc = nlp(text[:600])
        for ent in doc.ents:
            if ent.label_ in ("PERSON", "PER") and len(ent.text.split()) >= 2:
                return ent.text.strip()
    for line in text.split("\n")[:5]:
        line = line.strip()
        if 2 <= len(line.split()) <= 4 and re.match(r"^[A-Za-zÀ-ÿ\s\-\']+$", line):
            return line
    return None

def extract_linkedin(text: str) -> Optional[str]:
    m = re.search(r"linkedin\.com/in/[\w\-]+", text.lower())
    return "https://" + m.group(0) if m else None

def extract_github(text: str) -> Optional[str]:
    m = re.search(r"github\.com/[\w\-]+", text.lower())
    return "https://" + m.group(0) if m else None

def parse_date(s: str):
    s = s.strip().lower()
    now = datetime.datetime.now()
    if s in ("present","current","now","ongoing","today","présent","en cours"):
        return (now.year, now.month)
    for mn, mv in MONTHS_MAP.items():
        m = re.search(re.escape(mn) + r"\s+(\d{4})", s)
        if m: return (int(m.group(1)), mv)
    m = re.match(r"^(\d{1,2})[/\-](\d{4})$", s)
    if m: return (int(m.group(2)), int(m.group(1)))
    m = re.match(r"^(\d{4})$", s)
    if m: return (int(m.group(1)), 6)
    return None

def extract_experience_years(text: str) -> float:
    for p in [
        r"(\d+)\+?\s*years?\s+(?:of\s+)?(?:work\s+)?experience",
        r"(\d+)\+?\s*ans?\s+d.expérience",
    ]:
        m = re.search(p, text.lower())
        if m: return float(m.group(1))

    WORK_KW  = ["experience","work history","employment","expérience professionnelle"]
    EDU_KW   = ["education","formation","university","college","school"]
    STAGE_KW = ["intern","internship","stage","trainee"]

    lines = text.split("\n")
    in_work, work_lines = False, []
    for line in lines:
        ll = line.lower().strip()
        if any(kw in ll for kw in WORK_KW) and len(ll) < 50:
            in_work = True
        elif any(kw in ll for kw in EDU_KW) and len(ll) < 50:
            in_work = False
        if in_work:
            work_lines.append(line)

    work_text = " ".join(work_lines)
    if not work_text.strip(): return 0.0

    DATE_RE = (
        r"((?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)?"
        r"\.?\s*\d{4})"
        r"\s*[\-–—/to]+\s*"
        r"((?:present|current|now|ongoing|"
        r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)?"
        r"\.?\s*(?:\d{4}|present|current|now|ongoing))"
    )

    total_months = 0
    for m in re.finditer(DATE_RE, work_text.lower()):
        full = m.group(0)
        sep_match = re.search(r"[\-–—/]|(?<=\d)\s+to\s+", full)
        if not sep_match: continue
        start_str = full[:sep_match.start()].strip()
        end_str   = full[sep_match.end():].strip()
        s = parse_date(start_str)
        e = parse_date(end_str)
        if not s or not e: continue
        dur = max(0, (e[0]*12+e[1]) - (s[0]*12+s[1]))
        if dur <= 0 or dur > 600: continue
        ctx = work_text[max(0,m.start()-150):m.end()+150].lower()
        is_stage = any(kw in ctx for kw in STAGE_KW) or dur <= 4
        if not is_stage:
            total_months += dur

    return round(total_months / 12, 1)

def extract_education(text: str) -> Dict:
    EDU_PAT = [
        (r"ph\.?d|doctorat|doctorate",                  "phd"),
        (r"master|m\.?sc?|mba|m\.?eng|m2",             "master"),
        (r"bachelor|b\.?sc?|b\.?eng|b\.?a|licence|bac\+[345]", "bachelor"),
        (r"associate|bac\+[12]|dut|bts|hnd",            "associate"),
        (r"high school|baccalauréat|bac\b",              "high_school"),
    ]
    results, seen = [], set()
    for line in text.split("\n"):
        for pat, lvl in EDU_PAT:
            if re.search(pat, line.lower()) and line.strip() not in seen and len(line.strip()) > 5:
                results.append({"raw": line.strip()[:100], "level": lvl})
                seen.add(line.strip())
    EDU_RANK = {"phd":5,"master":4,"bachelor":3,"associate":2,"high_school":1,"other":0}
    best = max(results, key=lambda x: EDU_RANK.get(x["level"],0)) if results else {"level":"other","raw":""}
    return {"entries": results[:3], "highest_level": best["level"]}

def extract_certifications(text: str) -> List[str]:
    CERT_KW = ["certified","certification","certificate","aws certified","google certified",
               "pmp","cissp","ccna","cpa","cfa","scrum master"]
    certs = []
    for line in text.split("\n"):
        if any(kw in line.lower() for kw in CERT_KW) and 5 < len(line.strip()) < 120:
            if line.strip() not in certs:
                certs.append(line.strip())
    return certs[:10]

def extract_languages(text: str) -> List[str]:
    LANGS = ["english","french","arabic","spanish","german","italian","portuguese",
             "chinese","japanese","russian","dutch","hindi","korean","darija"]
    tl = text.lower()
    return [l.capitalize() for l in LANGS if re.search(r"\b" + l + r"\b", tl)]

def parse_cv_file(file_bytes: bytes, filename: str) -> Dict:
    text   = extract_text(file_bytes, filename)
    if len(text.strip()) < 30:
        raise ValueError(f"Could not extract text from {filename}")
    skills = extract_skills_from_text(text)
    edu    = extract_education(text)
    return {
        "filename":         filename,
        "name":             extract_name(text),
        "email":            extract_email(text),
        "phone":            extract_phone(text),
        "linkedin":         extract_linkedin(text),
        "github":           extract_github(text),
        "skills":           skills,
        "skill_count":      len(skills),
        "experience_years": extract_experience_years(text),
        "education":        edu,
        "certifications":   extract_certifications(text),
        "languages":        extract_languages(text),
        "raw_text":         text,
    }


# ═══════════════════════════════════════════════════════════════
# SCORING ENGINE
# ═══════════════════════════════════════════════════════════════
WEIGHTS = {"semantic": 0.40, "skill": 0.40, "experience": 0.20}

def compute_skill_score(cv_skills: List[str], job: Dict) -> Dict:
    cv_set   = set(normalize_skill(s) for s in cv_skills)
    req_set  = set(job["required_skills"])
    pref_set = set(job["preferred_skills"])

    matched_req  = cv_set & req_set
    matched_pref = cv_set & pref_set
    unmatched    = req_set - matched_req

    fuzzy_matched = set()
    for skill in unmatched:
        match = fuzzy_skill_match(skill, list(cv_set))
        if match: fuzzy_matched.add(skill)

    all_matched_req = matched_req | fuzzy_matched
    missing_req     = req_set - all_matched_req

    req_score  = len(all_matched_req) / len(req_set)  if req_set  else 1.0
    pref_score = len(matched_pref)    / len(pref_set) if pref_set else 0.5
    skill_score = req_score * 0.80 + pref_score * 0.20

    return {
        "skill_score":    round(skill_score, 4),
        "matched_skills": sorted(all_matched_req | matched_pref),
        "missing_skills": sorted(missing_req),
    }

def compute_experience_score(exp_years: float, exp_min: float, exp_max: float) -> float:
    if exp_min <= exp_years <= exp_max: return 1.0
    if exp_years > exp_max: return max(0.70, 1.0 - (exp_years - exp_max) * 0.03)
    return max(0.0, 1.0 - (exp_min - exp_years) * 0.15)

def build_job_dict(job_input: JobInput) -> Dict:
    req_skills  = normalize_skills_list(job_input.required_skills)
    pref_skills = normalize_skills_list(job_input.preferred_skills)
    full_text = (
        f"Job Title: {job_input.title}\n"
        f"{job_input.description}\n"
        f"Required Skills: {', '.join(req_skills)}\n"
        f"Preferred Skills: {', '.join(pref_skills)}\n"
        f"Education: {job_input.required_degree}\n"
        f"Experience: {job_input.required_experience_min} to {job_input.required_experience_max} years"
    )
    return {
        "title":           job_input.title,
        "required_skills": req_skills,
        "preferred_skills": pref_skills,
        "exp_min":         job_input.required_experience_min,
        "exp_max":         job_input.required_experience_max,
        "full_text":       full_text,
    }

def rank_all(cvs: List[Dict], job: Dict, top_n: int = 10) -> List[Dict]:
    sbert = get_sbert()
    from sklearn.metrics.pairwise import cosine_similarity as cos_sim

    # Batch encode all CVs + job
    texts = [
        f"{cv.get('raw_text','')[:3000]} Skills: {', '.join(cv.get('skills',[]))}"
        for cv in cvs
    ]
    job_emb = sbert.encode([job["full_text"]], normalize_embeddings=True)
    cv_embs = sbert.encode(texts, normalize_embeddings=True, batch_size=32, show_progress_bar=False)
    semantic_scores = (cv_embs @ job_emb.T).flatten().tolist()

    results = []
    for cv, sem in zip(cvs, semantic_scores):
        skill_result = compute_skill_score(cv.get("skills", []), job)
        exp_score    = compute_experience_score(
            cv.get("experience_years", 0),
            job["exp_min"], job["exp_max"]
        )
        final = (
            max(0, min(1, sem)) * WEIGHTS["semantic"] +
            skill_result["skill_score"]  * WEIGHTS["skill"] +
            exp_score                    * WEIGHTS["experience"]
        )
        results.append({
            "candidate_name":   cv.get("name") or cv.get("filename", "Unknown"),
            "email":            cv.get("email"),
            "phone":            cv.get("phone"),
            "score":            round(final * 100, 1),
            "semantic_score":   round(max(0, min(1, sem)) * 100, 1),
            "skill_score":      round(skill_result["skill_score"] * 100, 1),
            "experience_score": round(exp_score * 100, 1),
            "matched_skills":   skill_result["matched_skills"],
            "missing_skills":   skill_result["missing_skills"],
            "experience_years": cv.get("experience_years", 0),
            "education_level":  cv.get("education", {}).get("highest_level", "unknown"),
            "certifications":   cv.get("certifications", []),
            "languages":        cv.get("languages", []),
            "linkedin":         cv.get("linkedin"),
            "github":           cv.get("github"),
            "filename":         cv.get("filename", ""),
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    for i, r in enumerate(results):
        r["rank"] = i + 1
    return results[:top_n]


# ═══════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {
        "name":    "TalentIQ CV Screener API",
        "version": "2.0.0",
        "docs":    "/docs",
        "status":  "running",
    }

@app.get("/api/health")
def health():
    return {"status": "ok", "models": {"sbert": _sbert is not None, "spacy": _nlp is not None}}


@app.post("/api/screen", response_model=ScreenResponse, summary="Upload CVs + Job → Top N candidates")
async def screen_cvs(
    files: List[UploadFile] = File(..., description="CV files (PDF or DOCX)"),
    job:   str              = Form(...,  description="Job description as JSON string"),
):
    """
    Main endpoint.
    - Upload multiple CV files (PDF/DOCX)
    - Pass job description as JSON in `job` form field
    - Returns top N ranked candidates

    **job JSON format:**
    ```json
    {
      "title": "Senior Data Analyst",
      "description": "We are looking for...",
      "required_skills": ["Python", "SQL", "Power BI"],
      "preferred_skills": ["Tableau", "Machine Learning"],
      "required_degree": "bachelor",
      "required_experience_min": 2,
      "required_experience_max": 8,
      "top_n": 10
    }
    ```
    """
    import time
    start = time.time()

    # Parse job input
    try:
        job_data = JobInput(**json.loads(job))
    except Exception as e:
        raise HTTPException(400, f"Invalid job JSON: {e}")

    if not files:
        raise HTTPException(400, "No CV files uploaded")

    # Parse all CVs
    parsed_cvs, errors = [], []
    for f in files:
        try:
            content = await f.read()
            cv = parse_cv_file(content, f.filename)
            parsed_cvs.append(cv)
        except Exception as e:
            errors.append({"file": f.filename, "error": str(e)})

    if not parsed_cvs:
        raise HTTPException(422, f"Could not parse any CVs. Errors: {errors}")

    # Build job dict + rank
    job_dict     = build_job_dict(job_data)
    top_candidates = rank_all(parsed_cvs, job_dict, top_n=job_data.top_n)

    elapsed = round(time.time() - start, 2)

    return ScreenResponse(
        job_title=job_data.title,
        total_cvs_processed=len(parsed_cvs),
        top_candidates=top_candidates,
        processing_time_seconds=elapsed,
    )


@app.post("/api/parse-cv", summary="Parse a single CV → structured JSON")
async def parse_cv_endpoint(file: UploadFile = File(...)):
    """Parse one CV file and return structured JSON (no scoring)."""
    try:
        content = await file.read()
        cv = parse_cv_file(content, file.filename)
        cv.pop("raw_text", None)   # don't return raw text in API
        return cv
    except Exception as e:
        raise HTTPException(422, str(e))


@app.post("/api/parse-job", summary="Parse + normalize a job description")
async def parse_job_endpoint(job: JobInput):
    """Normalize and parse a job description."""
    job_dict = build_job_dict(job)
    job_dict.pop("full_text", None)
    return job_dict
