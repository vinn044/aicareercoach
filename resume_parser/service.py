
# Import our PDF text extraction function.
from .extractor import extract_text_from_pdf

# Import our Gemini AI resume parsing function.
from .ai_parser import parse_resume_with_ai

# Import our original rule-based parser.
# This will be used as a backup if Gemini's API fails.
from .parser import parse_resume


def process_resume(file_path):
    """
    Processes a PDF resume using Gemini AI.

    If Gemini's API fails, the original rule-based
    parser is used as a backup.

    Returns a CandidateProfile object.
    """

    # Step 1: Extract readable text from the PDF.
    resume_text = extract_text_from_pdf(file_path)

    # Step 2: Make sure the resume contains readable text.
    if not resume_text or not resume_text.strip():
        raise ValueError(
            "Resume text is empty. Please upload a valid resume."
        )

    # Step 3: Try processing the resume with Gemini AI.
    try:
        profile = parse_resume_with_ai(resume_text)

    # Step 4: If Gemini's API fails, use the original parser.
    except RuntimeError:
        print("Gemini unavailable. Using rule-based parser instead.")

        profile = parse_resume(resume_text)

    # Step 5: Return the completed CandidateProfile object.
    return profile


def process_resume_to_dict(file_path):
    """
    Processes a PDF resume and returns a dictionary
    that can be converted into JSON for the backend.
    """

    # Process the resume using our existing service.
    # This includes the automatic fallback system.
    profile = process_resume(file_path)

    # Convert the CandidateProfile into a dictionary.
    return profile.to_dict()
