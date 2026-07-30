"""
Core scoring logic for the resume screener.

Two signals are combined into a final score per candidate:
1. Content similarity — TF-IDF + cosine similarity between the job
   description and the resume's full text. Captures overall topical overlap,
   not just exact skill keywords.
2. Skill match — the fraction of skills mentioned in the job description
   that were also found in the resume, using the curated skill list.

The two are blended with a user-adjustable weight so you can decide whether
skill-keyword overlap or overall content similarity should matter more.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.text_processor import clean_text, extract_skills


def compute_content_similarity(jd_text: str, resume_texts: list) -> list:
    """
    Fit one TF-IDF vectorizer across the JD + all resumes so they share a
    vocabulary, then return the cosine similarity of each resume to the JD.
    """
    corpus = [clean_text(jd_text)] + [clean_text(t) for t in resume_texts]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    jd_vector = tfidf_matrix[0]
    resume_vectors = tfidf_matrix[1:]

    similarities = cosine_similarity(jd_vector, resume_vectors)[0]
    return similarities.tolist()


def compute_skill_match(jd_skills: set, resume_skills: set) -> dict:
    """Return match percentage plus matched/missing skill lists."""
    if not jd_skills:
        return {"score": 0.0, "matched": [], "missing": []}

    matched = jd_skills & resume_skills
    missing = jd_skills - resume_skills
    score = len(matched) / len(jd_skills)

    return {
        "score": score,
        "matched": sorted(matched),
        "missing": sorted(missing),
    }


def rank_candidates(jd_text: str, candidates: list, skill_weight: float = 0.5) -> list:
    """
    candidates: list of dicts, each with at least {"name": str, "text": str}
    skill_weight: 0.0-1.0, how much the skill-match score counts vs content
                  similarity (1 - skill_weight goes to content similarity)

    Returns the same candidates list, each augmented with score fields,
    sorted by final_score descending.
    """
    jd_skills = extract_skills(jd_text)
    resume_texts = [c["text"] for c in candidates]

    content_scores = compute_content_similarity(jd_text, resume_texts)

    results = []
    for candidate, content_score in zip(candidates, content_scores):
        resume_skills = extract_skills(candidate["text"])
        skill_result = compute_skill_match(jd_skills, resume_skills)

        final_score = (
            skill_weight * skill_result["score"]
            + (1 - skill_weight) * content_score
        )

        results.append({
            **candidate,
            "content_similarity": round(content_score * 100, 1),
            "skill_match_score": round(skill_result["score"] * 100, 1),
            "final_score": round(final_score * 100, 1),
            "matched_skills": skill_result["matched"],
            "missing_skills": skill_result["missing"],
        })

    results.sort(key=lambda r: r["final_score"], reverse=True)
    return results


def build_skill_coverage_matrix(jd_text: str, results: list) -> dict:
    """
    Build a candidates x required-skills coverage grid, for a visual
    "who has what" comparison table.

    Returns {"skills": [sorted skill list], "rows": [{"name": ..., "coverage": {skill: bool}}]}
    """
    jd_skills = sorted(extract_skills(jd_text))

    rows = []
    for r in results:
        matched = set(r["matched_skills"])
        rows.append({
            "name": r["name"],
            "coverage": {skill: (skill in matched) for skill in jd_skills},
        })

    return {"skills": jd_skills, "rows": rows}
