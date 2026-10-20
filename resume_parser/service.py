# Imports our PDF text extraction function.
from .extractor import extract_text_from_pdf

# Imports our Gemini AI resume parsing function.
from .ai_parser import parse_resume_with_ai


def process_resume(file_path):
    """
    Processes a PDF resume and returns a CandidateProfile object.
    """

    # Step 1: Extract readable text from the uploaded PDF.
    resume_text = extract_text_from_pdf(file_path)

    # Step 2: Send the extracted text to Gemini AI.
    # Gemini analyzes the resume and creates a CandidateProfile.
    profile = parse_resume_with_ai(resume_text)

    # Step 3: Return the completed profile to the application.
    return profile


def process_resume_to_dict(file_path):
    """
    Processes a PDF resume and returns a dictionary
    that can be converted into JSON for the backend.
    """

    # Process the resume using our existing service.
    profile = process_resume(file_path)

    # Convert the CandidateProfile into a dictionary.
    # This makes the information easier for an API to return.
    return profile.to_dict()
