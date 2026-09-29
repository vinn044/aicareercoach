import re
from .models import CandidateProfile

def extract_section(text, section_name, possible_sections):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    section_content = []
    collecting = False

    for line in lines:

        # Start collecting after finding our section
        if line.lower() == section_name.lower():
            collecting = True
            continue

        # Stop when we reach another section
        if collecting and line.lower() in [s.lower() for s in possible_sections]:
            break

        if collecting:
            section_content.append(line)

    return section_content


def parse_resume(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    profile = CandidateProfile()

    # Assume first non-empty line is the candidate's name
    if lines:
        profile.name = lines[0]

    # Find email address
    email_match = re.search(
        r'[\w\.-]+@[\w\.-]+\.\w+',
        text
    )

    if email_match:
        profile.email = email_match.group()

    # Find phone number
    phone_match = re.search(
        r'(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}',
        text
    )

    if phone_match:
        profile.phone = phone_match.group()

    # Skills we currently know how to recognize
    known_skills = [
        "Python",
        "C++",
        "Java",
        "JavaScript",
        "SQL",
        "HTML",
        "CSS",
        "Git",
        "React",
        "Node.js"
    ]

    # Search resume for skills
    for skill in known_skills:
        if skill.lower() in text.lower():
            profile.skills.append(skill)

    # Common resume section headings
    sections = [
        "education",
        "experience",
        "work experience",
        "skills",
        "projects",
        "certifications"
    ]

    # Extract education
    profile.education = extract_section(
        text,
        "education",
        sections
    )

    # Extract experience
    profile.experience = extract_section(
        text,
        "experience",
        sections
    )

    # Some resumes use "Work Experience" instead
    if not profile.experience:
        profile.experience = extract_section(
            text,
            "work experience",
            sections
        )

    return profile