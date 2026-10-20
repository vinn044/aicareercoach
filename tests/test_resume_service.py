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



# Import patch to simulate an API failure.
from unittest.mock import patch

# Import our resume processing service.
from resume_parser.service import process_resume

# Import our CandidateProfile model.
from resume_parser.models import CandidateProfile


def test_gemini_fallback():
    """
    Tests whether the original rule-based parser
    takes over when Gemini AI is unavailable.
    """

    # Create a fake resume containing basic information.
    fake_resume_text = (
        "John Smith\n"
        "Email: john@example.com\n"
        "Skills\n"
        "Python, Java, SQL\n"
    )

    # Simulate PDF extraction without opening a real PDF.
    with patch(
        "resume_parser.service.extract_text_from_pdf",
        return_value=fake_resume_text
    ):

        # Simulate Gemini AI being unavailable.
        with patch(
            "resume_parser.service.parse_resume_with_ai",
            side_effect=RuntimeError("Gemini API unavailable")
        ):

            # Process the resume using our service.
            profile = process_resume("fake_resume.pdf")

            # Verify that we received a CandidateProfile object.
            assert isinstance(profile, CandidateProfile)

            # Verify that the fallback extracted the skills.
            assert "Python" in profile.skills

            print("Gemini fallback test passed!")


# Run our fallback test.
test_gemini_fallback()


def test_gemini_success():
    """
    Verify that Gemini's result is used when
    the AI parser works successfully.
    """

    # Create a fake resume.
    fake_resume_text = "John Smith\nSkills: Python, Java"

    # Create a fake successful AI result.
    fake_profile = CandidateProfile(
        name="John Smith",
        email="john@example.com",
        phone="",
        skills=["Python", "Java"],
        education=[],
        experience=[],
        projects=[],
        certifications=[]
    )

    # Simulate extracting text from a PDF.
    with patch(
        "resume_parser.service.extract_text_from_pdf",
        return_value=fake_resume_text
    ):

        # Simulate Gemini successfully parsing the resume.
        with patch(
            "resume_parser.service.parse_resume_with_ai",
            return_value=fake_profile
        ) as mock_ai:

            # Process the resume.
            profile = process_resume("fake_resume.pdf")

            # Verify Gemini was called.
            mock_ai.assert_called_once_with(fake_resume_text)

            # Verify the returned profile is Gemini's result.
            assert profile is fake_profile

            print("Gemini success test passed!")


# Run the success test.
test_gemini_success()
