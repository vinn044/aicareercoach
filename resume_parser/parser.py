
# Imports Python's regular expression library.
# Regex allows us to search text for patterns such as email addresses, phone numbers, dates, and skills.
import re

# Imports the classes we created in models.py. CandidateProfile stores the entire resume. Education stores information about one school or degree.
# Experience stores information about one previous job.
from .models import CandidateProfile, Education, Experience


# A list of technical skills our parser currently recognizes. The parser searches the resume for these skills.
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


# Different resumes may use different names for the same section.
# This dictionary groups common headings into five categories.
#
# For example, "Academic Background" and "Education" will both be recognized as the education section.
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
    """
    Extracts the lines belonging to a specific resume section.

    Parameters:
        text: The complete text extracted from the resume.
        section_type: The section we want, such as "education".

    Returns:
        A list containing the lines found in that section.
    """

    # Splits the resume into separate lines.
    # strip() removes extra spaces at the beginning and end.
    # The if statement removes empty lines.
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Stores the lines found inside the requested section.
    section_content = []

    # Keeps track of whether we have reached the section.
    # False means we have not started collecting information yet.
    collecting = False

    # Creates a list containing every known section heading.
    # This helps us recognize when one section ends
    # and another section begins.
    all_headings = []

    for headings in SECTION_ALIASES.values():
        all_headings.extend(headings)

    # Gets the possible headings for the section we want.
    # For example, "education" has four recognized headings.
    # If the section does not exist, return an empty list.
    target_headings = SECTION_ALIASES.get(section_type, [])

    # Goes through the resume one line at a time.
    for line in lines:

        # Converts the line to lowercase and removes
        # extra spaces and a trailing colon.
        #
        # Example: "ACADEMIC BACKGROUND:"
        # becomes "academic background".
        normalized_line = line.lower().strip().rstrip(":")

        # If the line matches the section we want,
        # start collecting information.
        if normalized_line in target_headings:
            collecting = True
            continue

        # If we are collecting information and encounter
        # another recognized heading, stop collecting.
        #
        # Dates such as "May 2025 - August 2025" do not
        # count as headings because they are not listed
        # in SECTION_ALIASES.
        if collecting and normalized_line in all_headings:
            break

        # Add the current line to our section if
        # we are currently collecting information.
        if collecting:
            section_content.append(line)

    # Returns all lines found in the requested section.
    return section_content


def extract_skills(text):
    """
    Searches the resume for technical skills.

    Returns:
        A list containing all recognized skills.
    """

    # Creates an empty list to store matching skills.
    found_skills = []

    # Checks each skill in our known skills list.
    for skill in KNOWN_SKILLS:

        # Creates a regex pattern for the current skill.
        #
        # re.escape(skill) handles special characters
        # such as the + signs in C++.
        #
        # (?<!\w) ensures the skill does not start
        # in the middle of another word.
        #
        # (?!\w) ensures the skill does not end
        # in the middle of another word.
        #
        # This prevents "C" from being detected inside
        # a word such as "Computer".
        pattern = r'(?<!\w)' + re.escape(skill) + r'(?!\w)'

        # Searches the entire resume for the skill.
        # re.IGNORECASE allows "python" and "Python"
        # to be treated as the same skill.
        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    # Returns all recognized skills.
    return found_skills


def parse_education(lines):
    """
    Extracts education information from the resume.

    Supports multiple education entries by searching
    for graduation dates.

    Expected format:
        School
        Degree
        Graduation Date

    Returns:
        A list of Education objects.
    """

    # Creates an empty list to store education entries.
    educations = []

    # If the education section is empty, return an empty list.
    if not lines:
        return educations

    # Loops through each line in the education section.
    # enumerate() provides both the line number (index)
    # and the actual text (line).
    for index, line in enumerate(lines):

        # Searches for a month followed by a year.
        #
        # Examples:
        # "Expected Graduation: May 2027"
        # "May 2024"
        #
        # The regex supports full month names and
        # common abbreviations such as Jan and Feb.
        #
        # \s+ means one or more spaces.
        # \d{4} means exactly four digits (a year).
        date_match = re.search(
            r'(Expected Graduation:\s*)?'
            r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|'
            r'May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|'
            r'Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
            r'\s+\d{4}',
            line,
            re.IGNORECASE
        )

        # If a graduation date is found, create
        # a new Education object.
        if date_match:
            education = Education()

            # Our current parser assumes the school and
            # degree appear directly before the date.
            #
            # index - 2 = School
            # index - 1 = Degree
            # index     = Graduation Date
            if index >= 2:
                education.school = lines[index - 2]
                education.degree = lines[index - 1]

            # Stores the graduation date.
            education.graduation_date = line

            # Adds the completed education entry to our list.
            educations.append(education)

    # Returns all education entries found in the resume.
    return educations


def parse_experience(lines):
    """
    Extracts previous work experience from the resume.

    Supports multiple jobs by identifying date ranges.

    Expected format:
        Job Title
        Company
        Start Date - End Date
        Description

    Returns:
        A list of Experience objects.
    """

    # Creates an empty list to store previous jobs.
    experiences = []

    # If no experience information exists,
    # return the empty list.
    if not lines:
        return experiences

    # Stores the job currently being processed.
    # None means we have not found a job yet.
    current_experience = None

    # Loops through every line in the experience section.
    for index, line in enumerate(lines):

        # Searches for employment date ranges.
        #
        # Examples:
        # "May 2025 - August 2025"
        # "January 2024 - Present"
        #
        # [-–] allows a normal hyphen or an en dash.
        # \s* allows zero or more spaces.
        # re.IGNORECASE ignores capitalization.
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

        # If a date range is found, we assume
        # we have discovered a new job entry.
        if date_match:

            # If a previous job was being processed,
            # save it before starting the next job.
            if current_experience:
                experiences.append(current_experience)

            # Creates a new Experience object.
            current_experience = Experience()

            # Assumes the two lines before the dates
            # contain the job title and company name.
            if index >= 2:
                current_experience.job_title = lines[index - 2]
                current_experience.company = lines[index - 1]

            # Splits the date range into two parts.
            #
            # Example:
            # "May 2025 - August 2025"
            #
            # Becomes:
            # ["May 2025", "August 2025"]
            dates = re.split(r'\s*[-–]\s*', line, maxsplit=1)

            # If both dates were found, store them.
            if len(dates) == 2:
                current_experience.start_date = dates[0].strip()
                current_experience.end_date = dates[1].strip()

        # If the line is not a date range but we have
        # already found a job, add the line to its description.
        elif current_experience:
            current_experience.description += line + " "

    # After the loop, save the final job.
    # Without this, the last job would not be added.
    if current_experience:

        # Removes extra spaces from the description.
        current_experience.description = current_experience.description.strip()

        # Adds the last job to our experience list.
        experiences.append(current_experience)

    # Returns all jobs found in the resume.
    return experiences


def parse_resume(text):
    """
    Main function responsible for parsing a resume.

    Takes the raw text extracted from a PDF and
    converts it into a structured CandidateProfile.

    Returns:
        A CandidateProfile containing the extracted information.
    """

    # Splits the resume into lines and removes
    # empty lines and unnecessary spaces.
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Creates an empty CandidateProfile object.
    # We will fill it with information from the resume.
    profile = CandidateProfile()

    # Assumes the first non-empty line contains the candidate's name.
    if lines:
        profile.name = lines[0]

    # Searches for an email address using regex.
    #
    # [\w.-]+ matches letters, numbers, underscores,
    # periods, and hyphens.
    # @ matches the @ symbol.
    # \. matches a literal period.
    # \w+ matches the final part of the domain.
    email_match = re.search(
        r'[\w\.-]+@[\w\.-]+\.\w+',
        text
    )

    # If an email was found, store it in the profile.
    if email_match:
        profile.email = email_match.group()

    # Searches for a phone number.
    #
    # Supports formats such as:
    # 956-555-1234
    # (956) 555-1234
    # +1 956-555-1234
    #
    # \d{3} matches three digits.
    # \d{4} matches four digits.
    # ? makes the preceding part optional.
    phone_match = re.search(
        r'(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}',
        text
    )

    # If a phone number was found, store it.
    if phone_match:
        profile.phone = phone_match.group()

    # Searches the entire resume for recognized skills.
    profile.skills = extract_skills(text)

    # Extracts the raw lines belonging to the
    # education and experience sections.
    education_lines = extract_section(text, "education")
    experience_lines = extract_section(text, "experience")

    # Converts those lines into structured
    # Education and Experience objects.
    profile.education = parse_education(education_lines)
    profile.experience = parse_experience(experience_lines)

    # Extracts projects and certifications.
    # These are currently stored as lists of strings.
    profile.projects = extract_section(text, "projects")
    profile.certifications = extract_section(text, "certifications")

    # Returns the completed CandidateProfile.
    # The profile can then be converted to JSON
    # and passed to the backend or job matching module.
    return profile
