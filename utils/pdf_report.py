"""
Generates a PDF summary report of the screening results — ranked candidates,
their scores, matched skills, and a gap-analysis of what each candidate
would need to become a stronger fit.
"""

import io
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)


def build_pdf_report(jd_text: str, results: list, skill_weight: float) -> bytes:
    """
    results: the ranked list returned by matcher.rank_candidates
    Returns the PDF file content as bytes, ready for a Streamlit download button.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        topMargin=0.6 * inch, bottomMargin=0.6 * inch,
        leftMargin=0.6 * inch, rightMargin=0.6 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom", parent=styles["Title"], fontSize=20, spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"], fontSize=10, textColor=colors.grey,
        spaceAfter=16,
    )
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6)
    h3 = ParagraphStyle("H3", parent=styles["Heading3"], spaceBefore=10, spaceAfter=4,
                         textColor=colors.HexColor("#1f4e79"))
    body = styles["Normal"]
    small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=9, textColor=colors.grey)

    story = []

    # --- Header ---
    story.append(Paragraph("Resume Screening Report", title_style))
    story.append(Paragraph(
        f"Generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')} · "
        f"Skill-match weighting: {int(skill_weight * 100)}%",
        subtitle_style
    ))

    # --- Job description summary ---
    story.append(Paragraph("Job Description", h2))
    jd_preview = jd_text.strip().replace("\n", "<br/>")
    story.append(Paragraph(jd_preview, body))
    story.append(Spacer(1, 12))

    # --- Ranked summary table ---
    story.append(Paragraph("Candidate Ranking", h2))
    table_data = [["Rank", "Candidate", "Final Score", "Skill Match", "Content Similarity"]]
    for i, r in enumerate(results, 1):
        table_data.append([
            str(i), r["name"], f"{r['final_score']}%",
            f"{r['skill_match_score']}%", f"{r['content_similarity']}%",
        ])

    t = Table(table_data, colWidths=[0.5*inch, 2.2*inch, 1*inch, 1*inch, 1.3*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f6fa")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(PageBreak())

    # --- Per-candidate detail ---
    story.append(Paragraph("Candidate Details", h2))
    for i, r in enumerate(results, 1):
        story.append(Paragraph(f"{i}. {r['name']} — {r['final_score']}% overall fit", h3))
        story.append(Paragraph(f"Email: {r.get('email', 'N/A')} &nbsp;&nbsp; Phone: {r.get('phone', 'N/A')}", small))
        story.append(Spacer(1, 4))

        matched = ", ".join(r["matched_skills"]) if r["matched_skills"] else "None found"
        missing = ", ".join(r["missing_skills"]) if r["missing_skills"] else "None — full match"

        story.append(Paragraph(f"<b>Matched skills:</b> {matched}", body))
        story.append(Paragraph(f"<b>Skill gaps:</b> {missing}", body))

        if r["missing_skills"]:
            story.append(Paragraph(
                f"<i>To become a stronger fit for this role, this candidate should "
                f"gain experience or training in: {missing}.</i>",
                small
            ))
        else:
            story.append(Paragraph(
                "<i>This candidate covers every skill listed in the job description.</i>",
                small
            ))
        story.append(Spacer(1, 10))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
