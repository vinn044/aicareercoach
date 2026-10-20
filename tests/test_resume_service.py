# Import our resume processing service.
from resume_parser.service import process_resume

# Import our CandidateProfile model.
from resume_parser.models import CandidateProfile


# Test the complete resume processing pipeline.
def test_resume_service():

    # Process our existing test PDF.
    # This extracts text and sends it to Gemini AI.
    profile = process_resume("test_resume.pdf")

    # Verify that the result is a CandidateProfile object.
    assert isinstance(profile, CandidateProfile)

    # Verify that the profile contains the expected data types.
    assert isinstance(profile.name, str)
    assert isinstance(profile.skills, list)
    assert isinstance(profile.education, list)
    assert isinstance(profile.experience, list)

    # Print the extracted information.
    print("\n----- PROCESSED RESUME -----")
    print(profile.to_json())

    print("\nResume service test passed!")


# Run the test when this file is executed.
if __name__ == "__main__":
    test_resume_service()


# Import the tools needed for our new test.
from unittest.mock import patch
from resume_parser.service import process_resume_to_dict
from resume_parser.models import CandidateProfile


# Create a fake CandidateProfile for testing.
fake_profile = CandidateProfile(
    name="John Smith",
    email="john@example.com",
    phone="",
    skills=["Python", "Java", "SQL"],
    education=[],
    experience=[],
    projects=["AI Career Coach"],
    certifications=[]
)


# Replace the real resume processing function with our fake result.
# This prevents the test from contacting Gemini.
with patch(
    "resume_parser.service.process_resume",
    return_value=fake_profile
):
    # Call our new function using a fictional PDF filename.
    result = process_resume_to_dict("fake_resume.pdf")

    # Verify that the result is a dictionary.
    assert isinstance(result, dict)

    # Verify that the dictionary contains the expected information.
    assert result["name"] == "John Smith"
    assert result["skills"] == ["Python", "Java", "SQL"]
    assert result["projects"] == ["AI Career Coach"]

    print("Resume dictionary service test passed!")
