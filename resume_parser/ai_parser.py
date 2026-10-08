import json
from google import genai
from .models import CandidateProfile, Education, Experience


# Creates a connection to Google's Gemini API.
client = genai.Client()


def parse_resume_with_ai(resume_text):
    """
    Sends resume text to Gemini AI and returns
    the extracted information as a Python dictionary.
    """

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

    # Convert Gemini's JSON response into a Python dictionary.
    data = json.loads(response.text)

    # Create a CandidateProfile using the AI-extracted information.
    profile = CandidateProfile(
        name=data.get("name", ""),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        skills=data.get("skills", []),

        # Convert education dictionaries into Education objects.
        education=[
            Education(**item)
            for item in data.get("education", [])
        ],

        # Convert experience dictionaries into Experience objects.
        experience=[
            Experience(**item)
            for item in data.get("experience", [])
        ],

        projects=data.get("projects", []),
        certifications=data.get("certifications", [])
    )

    return profile
