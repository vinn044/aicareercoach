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

        # Stop when another section begins ***CHECK if this date/May August counts as the same "Section"
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
    educations = []

    if not lines:
        return educations

    current_education = None

    for index, line in enumerate(lines):

        # Look for a graduation date
        date_match = re.search(
            r'(Expected Graduation:\s*)?'
            r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|'
            r'May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|'
            r'Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
            r'\s+\d{4}',
            line,
            re.IGNORECASE
        )

        if date_match:
            education = Education()

            # Assume:
            # School
            # Degree
            # Graduation Date
            if index >= 2:
                education.school = lines[index - 2]
                education.degree = lines[index - 1]

            education.graduation_date = line

            educations.append(education)

    return educations

# Pares for Experience
def parse_experience(lines):
    experiences = []

    if not lines:
        return experiences

    current_experience = None

    for index, line in enumerate(lines):
        # Look for a date range such as:
        # May 2025 - August 2025
        # January 2024 - Present
        date_match = re.search(
            r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|'
            r'May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|'
            r'Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
            r'\s+\d{4}\s*[-–]\s*'
            r'(Present|Current|'
            r'Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|'
            r'May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|'
            r'Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
            r'(?:\s+\d{4})?',
            line,
            re.IGNORECASE
        )

        if date_match:
            # The two lines before the dates are assumed to be
            # job title and company.
            if current_experience:
                experiences.append(current_experience)

            current_experience = Experience()

            if index >= 2:
                current_experience.job_title = lines[index - 2]
                current_experience.company = lines[index - 1]

            dates = re.split(r'\s*[-–]\s*', line, maxsplit=1)

            if len(dates) == 2:
                current_experience.start_date = dates[0].strip()
                current_experience.end_date = dates[1].strip()

        elif current_experience:
            current_experience.description += line + " "

    if current_experience:
        current_experience.description = current_experience.description.strip()
        experiences.append(current_experience)

    return experiences

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