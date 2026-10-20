from resume_parser.extractor import extract_text_from_pdf
from resume_parser.ai_parser import parse_resume_with_ai
from resume_parser.models import CandidateProfile, Education, Experience
import json

resume_text = extract_text_from_pdf("test_resume.pdf")

print("----- RESUME TEXT -----")
print(resume_text)

print("\n----- AI RESPONSE -----")

result = parse_resume_with_ai(resume_text)

print(result)

assert isinstance(result, CandidateProfile)
assert isinstance(result.skills, list)
assert all(isinstance(item, Education) for item in result.education)
assert all(isinstance(item, Experience) for item in result.experience)
assert isinstance(result.to_json(), str)

print("\nAll Gemini AI parser tests passed!")


# Test what happens when an empty resume is submitted.
# The parser should reject it before contacting Gemini.

try:
    # Attempt to parse an empty resume.
    parse_resume_with_ai("")

    # If no error occurs, the test should fail.
    raise AssertionError("Empty resume was not rejected!")

except ValueError as error:
    # Verify that the expected error message was returned.
    assert str(error) == (
        "Resume text is empty. Please upload a valid resume."
    )

    print("Empty resume test passed!")


# Imports tools for creating a fake API error during testing.
from unittest.mock import patch
from google.genai import errors


# Simulates Gemini returning an API error.
# This allows us to test error handling without contacting Google.
fake_error = errors.ClientError(
    429,
    {
        "error": {
            "code": 429,
            "message": "Rate limit exceeded",
            "status": "RESOURCE_EXHAUSTED"
        }
    }
)

# Temporarily replaces Gemini's generate_content function
# with one that raises our fake error.
with patch(
    "resume_parser.ai_parser.client.models.generate_content",
    side_effect=fake_error
):
    try:
        # Attempts to process a fictional resume.
        parse_resume_with_ai("John Smith\nPython Developer")

    except RuntimeError as error:
        # Checks that our parser returned the expected error message.
        assert str(error) == (
            "Gemini AI request failed. Please try again later."
        )

        print("Gemini API error handling test passed!")

    else:
        # Fail the test if our parser did not raise RuntimeError.
        raise AssertionError("Gemini API error was not handled!")

    
# Imports SimpleNamespace to create a fake Gemini response.
from types import SimpleNamespace
from unittest.mock import patch


# Creates a fake response containing invalid JSON.
fake_response = SimpleNamespace(
    text="This is not valid JSON!"
)


# Temporarily replaces Gemini's response with our fake response.
# This test does not make a real API request.
with patch(
    "resume_parser.ai_parser.client.models.generate_content",
    return_value=fake_response
):
    try:
        # Attempts to parse a fictional resume.
        parse_resume_with_ai("John Smith\nPython Developer")

    except ValueError as error:
        # Checks that our parser returns the correct error message.
        assert str(error) == (
            "Gemini returned an invalid JSON response."
        )

        print("Invalid JSON test passed!")

    else:
        # Fails the test if invalid JSON was accepted.
        raise AssertionError("Invalid JSON was not rejected!")

    # Create a fake Gemini response with an invalid skills field.
# Skills should be a list, but here we intentionally use a string.
fake_skills_response = SimpleNamespace(
    text=json.dumps({
        "name": "John Smith",
        "email": "",
        "phone": "",
        "skills": "Python, Java, SQL",
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": []
    })
)


# Replace Gemini's real response with our fake response.
# This test does not contact the Gemini API.
with patch(
    "resume_parser.ai_parser.client.models.generate_content",
    return_value=fake_skills_response
):
    try:
        # Attempt to parse a fictional resume.
        parse_resume_with_ai("John Smith\nSoftware Developer")

    except ValueError as error:
        # Verify that our skills validation catches the mistake.
        assert str(error) == (
            "Gemini returned an invalid skills format. Expected a list."
        )

        print("Invalid skills format test passed!")

    else:
        # Fail if our parser accepts the invalid skills format.
        raise AssertionError("Invalid skills format was not rejected!")


    
# Create a fake Gemini response with invalid education data.
# The graduation_date field is intentionally missing.
fake_education_response = SimpleNamespace(
    text=json.dumps({
        "name": "John Smith",
        "email": "",
        "phone": "",
        "skills": ["Python", "Java"],
        "education": [
            {
                "school": "University of Texas",
                "degree": "Computer Science"
            }
        ],
        "experience": [],
        "projects": [],
        "certifications": []
    })
)


# Replace Gemini's response with our fake response.
# This test does not make a real API request.
with patch(
    "resume_parser.ai_parser.client.models.generate_content",
    return_value=fake_education_response
):
    try:
        # Attempt to parse a fictional resume.
        parse_resume_with_ai("John Smith\nComputer Science Student")

    except ValueError as error:
        # Verify that the missing graduation_date was detected.
        assert str(error) == (
            "Gemini returned an invalid education field: graduation_date"
        )

        print("Invalid education test passed!")

    else:
        # Fail if the parser accepts incomplete education data.
        raise AssertionError("Invalid education data was not rejected!")


    
# Create a fake Gemini response with invalid experience data.
# The company field is intentionally missing.
fake_experience_response = SimpleNamespace(
    text=json.dumps({
        "name": "John Smith",
        "email": "",
        "phone": "",
        "skills": ["Python", "Java"],
        "education": [],
        "experience": [
            {
                "job_title": "Software Developer",
                "start_date": "2024",
                "end_date": "2025",
                "description": "Developed software applications."
            }
        ],
        "projects": [],
        "certifications": []
    })
)


# Replace Gemini's real response with our fake response.
# This test does not contact the Gemini API.
with patch(
    "resume_parser.ai_parser.client.models.generate_content",
    return_value=fake_experience_response
):
    try:
        # Attempt to parse a fictional resume.
        parse_resume_with_ai("John Smith\nSoftware Developer")

    except ValueError as error:
        # Verify that the missing company field was detected.
        assert str(error) == (
            "Gemini returned an invalid experience field: company"
        )

        print("Invalid experience test passed!")

    else:
        # Fail if the parser accepts incomplete experience data.
        raise AssertionError("Invalid experience data was not rejected!")


    
# Test that the parser rejects invalid projects data.
# Projects should be a list, not a string.
fake_projects_response = SimpleNamespace(
    text=json.dumps({
        "name": "John Smith",
        "email": "",
        "phone": "",
        "skills": ["Python"],
        "education": [],
        "experience": [],
        "projects": "AI Career Coach",
        "certifications": []
    })
)

# Replace Gemini's real response with our fake response.
with patch(
    "resume_parser.ai_parser.client.models.generate_content",
    return_value=fake_projects_response
):
    try:
        parse_resume_with_ai("John Smith\nSoftware Developer")

    except ValueError as error:
        assert str(error) == (
            "Gemini returned an invalid projects format. Expected a list."
        )
        print("Invalid projects test passed!")

    else:
        raise AssertionError("Invalid projects data was not rejected!")


# Test that the parser rejects invalid certifications data.
# Certifications should be a list, not a string.
fake_certifications_response = SimpleNamespace(
    text=json.dumps({
        "name": "John Smith",
        "email": "",
        "phone": "",
        "skills": ["Python"],
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": "AWS Certification"
    })
)

# Replace Gemini's real response with our fake response.
with patch(
    "resume_parser.ai_parser.client.models.generate_content",
    return_value=fake_certifications_response
):
    try:
        parse_resume_with_ai("John Smith\nSoftware Developer")

    except ValueError as error:
        assert str(error) == (
            "Gemini returned an invalid certifications format. Expected a list."
        )
        print("Invalid certifications test passed!")

    else:
        raise AssertionError(
            "Invalid certifications data was not rejected!"
        )
