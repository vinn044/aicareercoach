
"""
Tests our AI-powered resume recommendation system.

Uses a sample candidate and job description
to check whether Gemini generates recommendations.
"""

from resume_parser.models import CandidateProfile
from resume_parser.recommender import recommend_resume_improvements


def test_resume_recommendations():
    """
    Test Gemini's job-specific resume recommendations.
    """

    # Step 1: Create a sample candidate.
    sample_profile = CandidateProfile(
        name="John Smith",
        email="john@example.com",
        phone="123-456-7890",
        skills=["Python", "SQL", "Java"],
        education=[],
        experience=[],
        projects=[],
        certifications=[]
    )

    # Step 2: Create a sample job description.
    sample_job = """
    Junior Software Developer

    Requirements:
    - Experience with Python programming
    - Knowledge of SQL databases
    - Familiarity with REST APIs
    - Experience with Docker
    - Basic understanding of AWS
    """

    # Step 3: Ask Gemini to compare the resume
    # against the selected job.
    recommendations = recommend_resume_improvements(
        sample_profile,
        sample_job
    )

    # Step 4: Verify Gemini returned a dictionary.
    assert isinstance(recommendations, dict)

    # Step 5: Verify all expected categories exist.
    expected_fields = [
        "matching_qualifications",
        "missing_qualifications",
        "resume_improvements",
        "skills_to_develop"
    ]

    for field in expected_fields:
        assert field in recommendations
        assert isinstance(recommendations[field], list)

        # Every recommendation should be a string.
        for item in recommendations[field]:
            assert isinstance(item, str)

    # Step 6: Display Gemini's recommendations.
    print("\n=== AI RESUME RECOMMENDATIONS ===")

    for category, items in recommendations.items():
        print(f"\n{category.replace('_', ' ').title()}:")

        for item in items:
            print(f"  - {item}")

    print("\nAI recommendation test passed!")


# Run our test.
test_resume_recommendations()


from unittest.mock import patch
from types import SimpleNamespace


def test_invalid_recommendations():
    """
    Tests whether our recommender correctly
    rejects invalid responses from Gemini.
    """

    # Create a sample candidate.
    sample_profile = CandidateProfile(
        name="John Smith",
        email="john@example.com",
        phone="123-456-7890",
        skills=["Python", "SQL"],
        education=[],
        experience=[],
        projects=[],
        certifications=[]
    )

    sample_job = "Python Developer requiring Python and SQL."

    # Test different invalid Gemini responses.
    invalid_responses = [
        "This is not valid JSON",

        '{"matching_qualifications": []}',

        '{"matching_qualifications": "Python", '
        '"missing_qualifications": [], '
        '"resume_improvements": [], '
        '"skills_to_develop": []}',

        '{"matching_qualifications": [123], '
        '"missing_qualifications": [], '
        '"resume_improvements": [], '
        '"skills_to_develop": []}'
    ]

    for invalid_response in invalid_responses:

        # Simulate Gemini returning invalid data.
        with patch("resume_parser.recommender.genai.Client") as mock_client:

            mock_client.return_value.models.generate_content.return_value = (
                SimpleNamespace(text=invalid_response)
            )

            # Verify our code rejects the response.
            try:
                recommend_resume_improvements(
                    sample_profile,
                    sample_job
                )

            except ValueError:
                print("Invalid AI response correctly rejected!")

            else:
                raise AssertionError(
                    "Invalid AI response was accepted!"
                )

    print("\nAll invalid recommendation tests passed!")


# Run our new test.
test_invalid_recommendations()



from google.genai import errors


def test_gemini_api_failure():
    """
    Tests whether our recommender handles
    Gemini API failures correctly.
    """

    # Step 1: Create a sample candidate.
    sample_profile = CandidateProfile(
        name="John Smith",
        email="john@example.com",
        phone="123-456-7890",
        skills=["Python", "SQL"],
        education=[],
        experience=[],
        projects=[],
        certifications=[]
    )

    # Step 2: Create a sample job description.
    sample_job = "Python Developer requiring Python and SQL."

    # Step 3: Simulate a Gemini API failure.
    fake_error = errors.ClientError(
        503,
        {"error": {"message": "Service unavailable"}}
    )

    with patch("resume_parser.recommender.genai.Client") as mock_client:

        mock_client.return_value.models.generate_content.side_effect = (
            fake_error
        )

        # Step 4: Verify our recommender handles the error.
        try:
            recommend_resume_improvements(
                sample_profile,
                sample_job
            )

        except RuntimeError as error:
            assert (
                "AI resume recommendations are temporarily unavailable"
                in str(error)
            )

            print("Gemini API failure handled correctly!")

        else:
            raise AssertionError(
                "Gemini API failure was not handled!"
            )


# Run our API failure test.
test_gemini_api_failure()
