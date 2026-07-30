"""
AI Resume Screening System
---------------------------
Upload a batch of resumes (PDF/DOCX), paste in a job description, and get
a ranked list of candidates scored on content similarity + skill overlap,
with skill highlighting, comparison charts, and a downloadable PDF report.

Run with:  streamlit run app.py
"""

import pandas as pd
import streamlit as st

from utils.resume_parser import parse_resume, extract_contact_info
from utils.matcher import rank_candidates, build_skill_coverage_matrix
from utils.text_processor import extract_skills
from utils.highlighter import highlight_skills
from utils.pdf_report import build_pdf_report

st.set_page_config(page_title="AI Resume Screening System", page_icon="📄", layout="wide")

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown("""
<style>
.app-header {
    background: linear-gradient(90deg, #0f2438 0%, #1f5c99 100%);
    padding: 28px 32px;
    border-radius: 12px;
    color: white;
    margin-bottom: 24px;
}
.app-header h1 { margin: 0; font-size: 1.8rem; }
.app-header p { margin: 6px 0 0 0; opacity: 0.85; font-size: 0.95rem; }

.skill-highlight {
    background-color: #ffd966;
    color: #1a1a1a;
    padding: 1px 4px;
    border-radius: 4px;
    font-weight: 600;
}
.resume-text {
    max-height: 420px;
    overflow-y: auto;
    padding: 14px;
    background: #161920;
    border: 1px solid #2a2e37;
    border-radius: 8px;
    color: #e6e6e6;
    font-family: "SFMono-Regular", Consolas, monospace;
    font-size: 0.85rem;
    line-height: 1.6;
    white-space: pre-wrap;
}
.skill-badge {
    display: inline-block;
    padding: 4px 11px;
    margin: 3px 4px 3px 0;
    border-radius: 14px;
    font-size: 0.82rem;
    font-weight: 500;
}
.skill-badge-matched { background: #163b24; color: #6fcf97; }
.skill-badge-missing { background: #3a1620; color: #f28b82; }

.fit-strong { color: #4ade80; font-weight: 700; }
.fit-moderate { color: #fbbf24; font-weight: 700; }
.fit-weak { color: #f87171; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
    <h1>📄 AI Resume Screening System</h1>
    <p>Upload resumes, paste a job description, and get a ranked, skill-matched shortlist in seconds.</p>
</div>
""", unsafe_allow_html=True)


def fit_label(score: float) -> str:
    if score >= 60:
        return "Strong fit"
    elif score >= 30:
        return "Moderate fit"
    return "Weak fit"


def fit_css_class(score: float) -> str:
    if score >= 60:
        return "fit-strong"
    elif score >= 30:
        return "fit-moderate"
    return "fit-weak"


# ---------------------------------------------------------------------------
# Sidebar: scoring controls
# ---------------------------------------------------------------------------
st.sidebar.header("⚙️ Scoring settings")
skill_weight = st.sidebar.slider(
    "Weight given to skill-keyword match vs. overall content similarity",
    min_value=0.0, max_value=1.0, value=0.5, step=0.05,
    help="1.0 = rank purely on matched skills. 0.0 = rank purely on how "
         "similar the resume text reads to the job description overall."
)
min_score = st.sidebar.slider(
    "Hide candidates scoring below this final score (%)",
    min_value=0, max_value=100, value=0, step=5,
)
st.sidebar.markdown(
    "**How scoring works**\n\n"
    "- *Content similarity*: TF-IDF + cosine similarity between the resume "
    "and job description text.\n"
    "- *Skill match*: % of skills mentioned in the job description that "
    "were also found in the resume, using a curated skill list.\n\n"
    "Final score is a weighted blend of the two."
)

# ---------------------------------------------------------------------------
# Main inputs
# ---------------------------------------------------------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Job description")
    jd_text = st.text_area(
        "Paste the job description here",
        height=250,
        placeholder="e.g. We are looking for a Data Scientist with strong "
                    "Python, SQL, and machine learning skills...",
    )

with col2:
    st.subheader("2. Resumes")
    uploaded_files = st.file_uploader(
        "Upload one or more resumes (PDF or DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True,
    )

run = st.button("🔍 Screen Candidates", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Run screening
# ---------------------------------------------------------------------------
if run:
    if not jd_text.strip():
        st.error("Please paste a job description first.")
    elif not uploaded_files:
        st.error("Please upload at least one resume.")
    else:
        candidates = []
        parse_errors = []

        with st.spinner("Reading resumes..."):
            for f in uploaded_files:
                try:
                    text = parse_resume(f)
                    if not text.strip():
                        parse_errors.append(f"{f.name}: no extractable text found (is it a scanned image?)")
                        continue
                    contact = extract_contact_info(text)
                    candidates.append({
                        "name": f.name,
                        "text": text,
                        "email": contact["email"],
                        "phone": contact["phone"],
                    })
                except Exception as e:
                    parse_errors.append(f"{f.name}: {e}")

        for err in parse_errors:
            st.warning(err)

        if candidates:
            with st.spinner("Scoring candidates..."):
                all_results = rank_candidates(jd_text, candidates, skill_weight=skill_weight)
                results = [r for r in all_results if r["final_score"] >= min_score]
                jd_skills = extract_skills(jd_text)

            if not results:
                st.warning("No candidates meet the minimum score filter. Try lowering it in the sidebar.")
                st.stop()

            # Keep results in session state so the PDF download button (which
            # triggers a rerun) doesn't force re-screening.
            st.session_state["results"] = results
            st.session_state["jd_text"] = jd_text
            st.session_state["skill_weight"] = skill_weight

if "results" in st.session_state:
    results = st.session_state["results"]
    jd_text_saved = st.session_state["jd_text"]
    skill_weight_saved = st.session_state["skill_weight"]

    st.subheader("Results")

    # --- Top recommendation callout ---
    top = results[0]
    st.success(
        f"**🏆 Top match: {top['name']}** — {top['final_score']}% overall fit "
        f"({top['skill_match_score']}% skill match, {top['content_similarity']}% content similarity)"
    )

    # --- Summary metrics ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Candidates screened", len(results))
    m2.metric("Top score", f"{top['final_score']}%")
    m3.metric("Required skills detected", len(extract_skills(jd_text_saved)))
    strong_fits = sum(1 for r in results if r["final_score"] >= 60)
    m4.metric("Strong fits (≥60%)", strong_fits)

    # --- Summary table ---
    df = pd.DataFrame([{
        "Rank": i + 1,
        "Candidate": r["name"],
        "Fit": fit_label(r["final_score"]),
        "Final Score (%)": r["final_score"],
        "Skill Match (%)": r["skill_match_score"],
        "Content Similarity (%)": r["content_similarity"],
        "Email": r["email"],
        "Phone": r["phone"],
    } for i, r in enumerate(results)])

    st.dataframe(df, use_container_width=True, hide_index=True)

    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download results as CSV",
            data=csv,
            file_name="resume_screening_results.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with dl_col2:
        pdf_bytes = build_pdf_report(jd_text_saved, results, skill_weight_saved)
        st.download_button(
            "⬇️ Download PDF report",
            data=pdf_bytes,
            file_name="resume_screening_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    # --- Comparison chart: skill match vs content similarity ---
    st.subheader("Score comparison")
    chart_df = df.set_index("Candidate")[["Skill Match (%)", "Content Similarity (%)"]]
    st.bar_chart(chart_df)

    # --- Skill coverage matrix ---
    st.subheader("Skill coverage matrix")
    st.caption("Which required skills each candidate covers (✅ = found in resume)")
    matrix = build_skill_coverage_matrix(jd_text_saved, results)
    if matrix["skills"]:
        coverage_df = pd.DataFrame(
            {row["name"]: {skill: ("✅" if row["coverage"][skill] else "—") for skill in matrix["skills"]}
             for row in matrix["rows"]}
        )
        coverage_df.index.name = "Skill"
        st.dataframe(coverage_df, use_container_width=True)
    else:
        st.info("No specific skills were detected in the job description to compare against.")

    # --- Candidate details ---
    st.subheader("Candidate details")
    for r in results:
        css_class = fit_css_class(r["final_score"])
        with st.expander(f"{r['name']} — {r['final_score']}% match ({fit_label(r['final_score'])})"):
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**Final score**<br><span class='{css_class}'>{r['final_score']}%</span>", unsafe_allow_html=True)
            c1.progress(min(int(r["final_score"]), 100))
            c2.markdown(f"**Skill match**<br>{r['skill_match_score']}%", unsafe_allow_html=True)
            c2.progress(min(int(r["skill_match_score"]), 100))
            c3.markdown(f"**Content similarity**<br>{r['content_similarity']}%", unsafe_allow_html=True)
            c3.progress(min(int(r["content_similarity"]), 100))

            st.markdown(f"**Contact:** {r['email']} | {r['phone']}")

            st.markdown("**✅ Matched skills**")
            if r["matched_skills"]:
                badges = "".join(f"<span class='skill-badge skill-badge-matched'>{s}</span>" for s in r["matched_skills"])
                st.markdown(badges, unsafe_allow_html=True)
            else:
                st.write("None found")

            st.markdown("**❌ Skill gaps**")
            if r["missing_skills"]:
                badges = "".join(f"<span class='skill-badge skill-badge-missing'>{s}</span>" for s in r["missing_skills"])
                st.markdown(badges, unsafe_allow_html=True)
                st.caption(
                    "To become a stronger fit, this candidate should gain experience or "
                    "training in the skills above."
                )
            else:
                st.write("None — this candidate covers every required skill.")

            with st.expander("📄 View resume with skills highlighted"):
                resume_skills = set(r["matched_skills"])
                st.markdown(
                    highlight_skills(r["text"], resume_skills),
                    unsafe_allow_html=True,
                )
