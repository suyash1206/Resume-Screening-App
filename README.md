# AI Resume Screening System

A Streamlit web app that ranks candidate resumes against a job description
using NLP-based text similarity and skill-keyword matching.

## Features
- Upload multiple resumes at once (PDF or DOCX)
- Paste in a job description to screen against
- Ranks candidates by a blended **content similarity** + **skill match** score
- Shows matched vs. missing skills per candidate, with a plain-language
  "skill gap" note on what a candidate would need to become a stronger fit
- **Highlights matched skills directly inside the resume text**
- **Skill coverage matrix** — a table showing which required skills each
  candidate does/doesn't have, at a glance
- **Comparison bar chart** of skill match % vs. content similarity % across candidates
- **Downloadable PDF report** summarizing the ranking and per-candidate gap analysis
- Downloadable CSV of results
- Minimum-score filter to hide weak matches
- Extracts email/phone automatically
- Adjustable weighting between the two scoring signals
- Custom color theme for a more presentable look

## Project structure
```
resume_screening_app/
├── app.py                    # Streamlit UI — run this
├── requirements.txt
├── .streamlit/
│   └── config.toml           # color theme
└── utils/
    ├── resume_parser.py      # PDF/DOCX text + contact-info extraction
    ├── text_processor.py     # text cleaning + skill extraction
    ├── matcher.py             # TF-IDF similarity + skill-match scoring/ranking
    ├── skills_data.py         # curated list of skills to detect
    ├── highlighter.py         # highlights matched skills inside resume text
    └── pdf_report.py          # builds the downloadable PDF report
```

## Setup

1. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the app:
   ```
   streamlit run app.py
   ```

4. Your browser will open to `http://localhost:8501`. Paste a job
   description, upload some resumes, and click **Screen Candidates**.

## How the scoring works

Each resume gets two sub-scores:

1. **Content similarity** — the resume text and job description are both
   converted to TF-IDF vectors (fit on the same vocabulary), then compared
   with cosine similarity. This captures overall topical overlap even for
   wording the skill list doesn't know about.

2. **Skill match** — `utils/skills_data.py` has a curated list of ~150
   common technical and soft skills. Both the JD and each resume are
   scanned for these (as whole words/phrases, so "machine learning" won't
   falsely match on just "learning"). The score is:
   `(skills in both JD and resume) / (skills in JD)`.

The final score is a weighted blend of the two, controlled by the slider in
the sidebar (default 50/50).

Each candidate is also labeled **Strong fit** (≥60%), **Moderate fit**
(30–59%), or **Weak fit** (<30%) in the results table — these thresholds are
just a simple heuristic in `app.py` (`fit_label()`), easy to adjust if you
want different cutoffs.

## Extending this project (ideas for your capstone writeup)

- **Better NLP**: swap TF-IDF for sentence embeddings (e.g.
  `sentence-transformers`) to catch semantic matches TF-IDF misses (e.g.
  "led a team" vs. "leadership").
- **Named entity recognition**: use spaCy to pull out education, years of
  experience, and job titles instead of relying only on the fixed skill list.
- **Learned ranking**: if you have historical hire/no-hire labels, train a
  classifier (e.g. logistic regression on the feature scores) instead of a
  fixed weighted blend.
- **Bias auditing**: since this automates a hiring-adjacent decision, it's
  worth documenting what the model does/doesn't account for, and testing
  whether scores vary in unexpected ways across resumes.

## Notes
- Scanned/image-only PDFs won't extract text (no OCR is built in) — the app
  will flag these instead of silently scoring them as empty.
- The skill list in `skills_data.py` is easy to edit — add domain-specific
  skills for the roles you're screening for.

## Demo data for presentations

`sample_data/job_description.txt` and `sample_data/resumes/` contain a
ready-made Data Scientist job description and 5 fictional candidate resumes
with a deliberate spread — 2 strong matches, 2 medium, 1 clear mismatch — so
a live demo shows the ranking clearly working.

To use them: paste the contents of `job_description.txt` into the job
description box, then upload all 5 PDFs from `sample_data/resumes/`.

(`generate_sample_resumes.py` is the script that created them — you don't
need to run it, the PDFs are already included. It needs `reportlab`
installed only if you want to regenerate or add more sample resumes.)
