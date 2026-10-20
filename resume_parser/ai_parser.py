import json
from google import genai
from google.genai import errors
from .models import CandidateProfile, Education, Experience


# Creates a connection to Google's Gemini API.
client = genai.Client()


def parse_resume_with_ai(resume_text):
    """
    Sends resume text to Gemini AI and returns
    the extracted information as a CandidateProfile object.
    """

    # Check whether the resume contains any readable text.
    # This prevents us from sending empty resumes to Gemini.
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty. Please upload a valid resume.")

    # Try sending the resume text to Gemini AI.
    try:
        # Ask Gemini to extract the information in JSON format.
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=(
                "Extract information from the following resume.\n"
                "Return ONLY a valid JSON object with these fields:\n"
                "name, email, phone, skills, education, experience, "
                "projects, certifications.\n\n"
                "Use these formats:\n"
                "skills: list of strings\n"
                "education: list of objects with school, degree, graduation_date\n"
                "experience: list of objects with job_title, company, "
                "start_date, end_date, description\n"
                "projects: list of strings\n"
                "certifications: list of strings\n\n"
                "Use empty strings or empty lists for missing information.\n"
                "Do not invent missing information.\n\n"
                "Resume:\n"
                + resume_text
            ),
            config={
                # Requests JSON rather than normal conversational text.
                "response_mime_type": "application/json"
            }
        )

    # Catch errors returned by Google's Gemini API.
    except errors.APIError as error:
        # Provide a clearer error message to our application.
        # "from error" preserves the original error for debugging.
        raise RuntimeError(
            "Gemini AI request failed. Please try again later."
        ) from error

    # Convert Gemini's JSON response into a Python dictionary.
    
    # Try converting Gemini's JSON response into a Python dictionary.
    try:
        data = json.loads(response.text)

    # Catch errors if Gemini returns invalid JSON.
    except (json.JSONDecodeError, TypeError) as error:
        raise ValueError(
            "Gemini returned an invalid JSON response."
        ) from error

    # Make sure Gemini returned a dictionary, not a list or string.
    if not isinstance(data, dict):
        raise ValueError(
            "Gemini returned an unexpected JSON structure."
        )

    # Check that the skills field contains a list.
    # Gemini should return something like ["Python", "Java"].
    skills = data.get("skills", [])

    if not isinstance(skills, list):
        raise ValueError(
            "Gemini returned an invalid skills format. Expected a list."
        )

    # Check that every item in the skills list is a string.
    # This prevents numbers, dictionaries, or other data types
    # from being treated as technical skills.
    if not all(isinstance(skill, str) for skill in skills):
        raise ValueError(
            "Gemini returned an invalid skill. Expected text."
        )

    
    # Check that education is a list.
    # Each entry should contain school, degree, and graduation_date.
    education = data.get("education", [])

    if not isinstance(education, list):
        raise ValueError(
            "Gemini returned an invalid education format. Expected a list."
        )

    # Check every education entry.
    for item in education:

        # Each entry must be a dictionary.
        if not isinstance(item, dict):
            raise ValueError(
                "Gemini returned an invalid education entry."
            )

        # Check that all required fields exist and contain text.
        required_fields = [
            "school",
            "degree",
            "graduation_date"
        ]

        for field in required_fields:
            if field not in item or not isinstance(item[field], str):
                raise ValueError(
                    f"Gemini returned an invalid education field: {field}"
                )

    # Check that experience is a list.
    # Each entry should contain information about a previous job.
    experience = data.get("experience", [])

    if not isinstance(experience, list):
        raise ValueError(
            "Gemini returned an invalid experience format. Expected a list."
        )

    # Check each work experience entry.
    for item in experience:

        # Each experience entry must be a dictionary.
        if not isinstance(item, dict):
            raise ValueError(
                "Gemini returned an invalid experience entry."
            )

        # These fields are required by our Experience model.
        required_fields = [
            "job_title",
            "company",
            "start_date",
            "end_date",
            "description"
        ]

        # Make sure every required field exists and contains text.
        for field in required_fields:
            if field not in item or not isinstance(item[field], str):
                raise ValueError(
                    f"Gemini returned an invalid experience field: {field}"
                )

    # Check that projects is a list.
    # Each project should be represented as a string.
    projects = data.get("projects", [])

    if not isinstance(projects, list):
        raise ValueError(
            "Gemini returned an invalid projects format. Expected a list."
        )

    # Check that every project is a string.
    if not all(isinstance(project, str) for project in projects):
        raise ValueError(
            "Gemini returned an invalid project. Expected text."
        )

    # Check that certifications is a list.
    # Each certification should be represented as a string.
    certifications = data.get("certifications", [])

    if not isinstance(certifications, list):
        raise ValueError(
            "Gemini returned an invalid certifications format. Expected a list."
        )

    # Check that every certification is a string.
    if not all(
        isinstance(certification, str)
        for certification in certifications
    ):
        raise ValueError(
            "Gemini returned an invalid certification. Expected text."
        )

    # Create a CandidateProfile using the AI-extracted information.
    profile = CandidateProfile(
        name=data.get("name", ""),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        skills=skills,

        # Convert education dictionaries into Education objects.
        education=[
            Education(**item)
            for item in education
            ],

        # Convert experience dictionaries into Experience objects.
        experience=[
            Experience(**item)
            for item in experience
            ],

        projects=projects,
        certifications=certifications
    )

    # Return the completed CandidateProfile object.
    return profile
