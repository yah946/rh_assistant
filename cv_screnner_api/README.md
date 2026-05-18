# TalentIQ CV Screener — API Integration Guide

## Run locally

```bash
# 1. Install
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 2. Start server
uvicorn main:app --reload --port 8000

# 3. Open docs
http://localhost:8000/docs
```

---

## API Endpoints

### POST `/api/screen` — Main endpoint
Upload CVs + job → get top N candidates

**Form data:**
- `files` → multiple PDF/DOCX files
- `job`   → JSON string (see below)

**job JSON:**
```json
{
  "title": "Senior Data Analyst",
  "description": "We are looking for a data analyst...",
  "required_skills": ["Python", "SQL", "Power BI"],
  "preferred_skills": ["Tableau", "Machine Learning"],
  "required_degree": "bachelor",
  "required_experience_min": 2,
  "required_experience_max": 8,
  "top_n": 10
}
```

**Response:**
```json
{
  "job_title": "Senior Data Analyst",
  "total_cvs_processed": 150,
  "processing_time_seconds": 12.4,
  "top_candidates": [
    {
      "rank": 1,
      "candidate_name": "Alice Martin",
      "email": "alice@email.com",
      "score": 94.2,
      "semantic_score": 91.0,
      "skill_score": 96.5,
      "experience_score": 100.0,
      "matched_skills": ["python", "sql", "power bi", "pandas"],
      "missing_skills": ["tableau"],
      "experience_years": 5,
      "education_level": "master",
      "certifications": ["AWS Certified Data Analytics"],
      "languages": ["English", "French"],
      "linkedin": "https://linkedin.com/in/alice",
      "github": null,
      "filename": "Alice_CV.pdf"
    }
  ]
}
```

### POST `/api/parse-cv` — Parse single CV
Upload one file → get structured JSON

### POST `/api/parse-job` — Parse job description
Send job JSON → get normalized version

### GET `/api/health` — Health check

---

## JavaScript / Frontend integration

```javascript
// ── Screen multiple CVs ─────────────────────────────────────
async function screenCVs(cvFiles, jobDescription) {
  const formData = new FormData()

  // Add all CV files
  cvFiles.forEach(file => formData.append('files', file))

  // Add job as JSON string
  formData.append('job', JSON.stringify(jobDescription))

  const response = await fetch('http://localhost:8000/api/screen', {
    method: 'POST',
    body: formData,
    // No Content-Type header — browser sets it automatically for FormData
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail)
  }

  return await response.json()
}

// ── Usage ───────────────────────────────────────────────────
const job = {
  title: 'Senior Data Analyst',
  description: 'We are looking for...',
  required_skills: ['Python', 'SQL', 'Power BI'],
  preferred_skills: ['Tableau', 'Machine Learning'],
  required_degree: 'bachelor',
  required_experience_min: 2,
  required_experience_max: 8,
  top_n: 10,
}

const fileInput = document.getElementById('cv-upload')
const result = await screenCVs(Array.from(fileInput.files), job)

console.log(`Processed ${result.total_cvs_processed} CVs`)
console.log(`Top candidate: ${result.top_candidates[0].candidate_name} — ${result.top_candidates[0].score}%`)
```

---

## React integration example

```jsx
import { useState } from 'react'

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'

export function CVScreener() {
  const [files, setFiles]       = useState([])
  const [results, setResults]   = useState(null)
  const [loading, setLoading]   = useState(false)

  const job = {
    title: 'Senior Data Analyst',
    description: 'Looking for a data analyst...',
    required_skills: ['Python', 'SQL', 'Power BI'],
    preferred_skills: ['Tableau', 'Machine Learning'],
    required_degree: 'bachelor',
    required_experience_min: 2,
    required_experience_max: 8,
    top_n: 10,
  }

  async function handleScreen() {
    setLoading(true)
    const formData = new FormData()
    files.forEach(f => formData.append('files', f))
    formData.append('job', JSON.stringify(job))

    try {
      const res = await fetch(`${API_URL}/api/screen`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      setResults(data)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <input
        type="file"
        multiple
        accept=".pdf,.docx"
        onChange={e => setFiles(Array.from(e.target.files))}
      />
      <button onClick={handleScreen} disabled={loading || !files.length}>
        {loading ? 'Analyzing...' : `Screen ${files.length} CVs`}
      </button>

      {results && results.top_candidates.map(c => (
        <div key={c.rank}>
          <h3>#{c.rank} {c.candidate_name} — {c.score}%</h3>
          <p>Matched: {c.matched_skills.join(', ')}</p>
          <p>Missing: {c.missing_skills.join(', ')}</p>
        </div>
      ))}
    </div>
  )
}
```

---

## Deploy to Railway / Render

```bash
# Procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT

# railway.json
{
  "build": {"builder": "NIXPACKS"},
  "deploy": {
    "startCommand": "python -m spacy download en_core_web_sm && uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/api/health"
  }
}
```
