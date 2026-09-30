import re
from .models import CandidateProfile, Education, Experience

# Skills we currently know how to recognize
KNOWN_SKILLS = [
    "Python",
    "C",
    "C++",
    "C#",
    "Java",
    "JavaScript",
    "TypeScript",
    "SQL",
    "HTML",
    "CSS",
    "React",
    "Node.js",
    "Git",
    "GitHub",
    "Linux",
    "Docker",
    "AWS",
    "Azure",
    "MongoDB",
    "MySQL",
    "PostgreSQL",
    "Flask",
    "Django",
    "FastAPI"
]

# Common resume section headings
SECTION_ALIASES = {
    "education": [
        "education",
        "educational background",
        "academic background",
        "academic history"
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history"
    ],

    "skills": [
        "skills",
        "technical skills",
        "core skills",
        "competencies"
    ],

    "projects": [
        "projects",
        "relevant projects",
        "academic projects",
        "personal projects"
    ],

    "certifications": [
        "certifications",
        "certificates",
        "licenses and certifications"
    ]
}

def extract_section(text, section_type):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    section_content = []
    collecting = False

    # Get all possible headings
    all_headings = []

    for headings in SECTION_ALIASES.values():
        all_headings.extend(headings)

    # Get headings for the section we want
    target_headings = SECTION_ALIASES.get(section_type, [])

    for line in lines:
        normalized_line = line.lower().strip().rstrip(":")

        # Start collecting when we find the section
        if normalized_line in target_headings:
            collecting = True
            continue

        # Stop when another section begins
        if collecting and normalized_line in all_headings:
            break

        if collecting:
            section_content.append(line)

    return section_content

# Search resume for skills
def extract_skills(text):
    found_skills = []

    for skill in KNOWN_SKILLS:
        pattern = r'(?<!\w)' + re.escape(skill) + r'(?!\w)'

        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    return found_skills

# Parse for Education
def parse_education(lines):
    if not lines:
        return []

    education = Education()

    if len(lines) > 0:
        education.school = lines[0]

    if len(lines) > 1:
        education.degree = lines[1]

    if len(lines) > 2:
        education.graduation_date = lines[2]

    return [education]

# Pares for Experience
def parse_experience(lines):
    if not lines:
        return []

    experience = Experience()

    if len(lines) > 0:
        experience.job_title = lines[0]

    if len(lines) > 1:
        experience.company = lines[1]

    if len(lines) > 2:
        dates = lines[2]

        if " - " in dates:
            start_date, end_date = dates.split(" - ", 1)
            experience.start_date = start_date.strip()
            experience.end_date = end_date.strip()
        else:
            experience.start_date = dates

    if len(lines) > 3:
        experience.description = " ".join(lines[3:])

    return [experience]

# Parse for resume
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

    # Search resume for skills
    profile.skills = extract_skills(text)

    #Search resume for education, experience, projects, certifications, etc
    education_lines = extract_section(text, "education")
    experience_lines = extract_section(text, "experience")

    profile.education = parse_education(education_lines)
    profile.experience = parse_experience(experience_lines)

    profile.projects = extract_section(text, "projects")
    profile.certifications = extract_section(text, "certifications")

    return profile