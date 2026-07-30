"""
Renders resume text as HTML with matched skills highlighted, so a reader can
see exactly where in the resume each skill was found.
"""

import re
import html


def highlight_skills(text: str, skills: set) -> str:
    """
    Return HTML-escaped resume text with each occurrence of a skill wrapped
    in a highlighted <span>. Longer skill phrases are highlighted before
    shorter ones so e.g. "machine learning" doesn't get partially matched
    by some other shorter overlapping term first.
    """
    if not skills:
        return f"<div class='resume-text'>{html.escape(text)}</div>"

    # Escape the raw text first so we don't fight HTML special characters,
    # then insert highlight markers using placeholder tokens.
    escaped = html.escape(text)

    # Sort skills longest-first so multi-word phrases are matched before
    # any shorter skill that might be a substring of them.
    sorted_skills = sorted(skills, key=len, reverse=True)

    for skill in sorted_skills:
        skill_escaped = html.escape(skill)
        pattern = r"(?<![a-zA-Z0-9])(" + re.escape(skill_escaped) + r")(?![a-zA-Z0-9])"
        escaped = re.sub(
            pattern,
            r"<span class='skill-highlight'>\1</span>",
            escaped,
            flags=re.IGNORECASE,
        )

    # Preserve line breaks
    escaped = escaped.replace("\n", "<br>")

    return f"<div class='resume-text'>{escaped}</div>"
