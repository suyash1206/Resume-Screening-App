"""
Text cleaning and skill extraction.

Skill matching uses word-boundary-aware substring search so that multi-word
skills like "machine learning" are matched as a phrase, and single-word
skills don't accidentally match inside unrelated words.
"""

import re

from utils.skills_data import SKILLS_LIST


def clean_text(text: str) -> str:
    """Lowercase and strip out anything that isn't alphanumeric/space/punctuation-lite."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\.\+\#\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_skills(text: str, skills_list: list = None) -> set:
    """Return the set of known skills found in the given text."""
    if skills_list is None:
        skills_list = SKILLS_LIST

    cleaned = clean_text(text)
    found = set()

    for skill in skills_list:
        skill_cleaned = skill.lower()
        # Build a regex that treats the skill as a whole phrase/word,
        # escaping special characters like "c++" or "c#".
        pattern = r"(?<![a-z0-9])" + re.escape(skill_cleaned) + r"(?![a-z0-9])"
        if re.search(pattern, cleaned):
            found.add(skill)

    return found
