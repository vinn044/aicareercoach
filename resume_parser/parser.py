import re
from .models import CandidateProfile

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

    #Search resume for education and experience
    profile.education = extract_section(text, "education")
    profile.experience = extract_section(text, "experience")
    profile.projects = extract_section(text, "projects")
    profile.certifications = extract_section(text, "certifications")

    return profile