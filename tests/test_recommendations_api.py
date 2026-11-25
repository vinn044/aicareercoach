from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.test_server import app


# Create a client for testing our FastAPI application.
client = TestClient(app)


# Simulated Gemini response.
MOCK_RECOMMENDATIONS = {
    "matching_qualifications": ["Python", "SQL"],
    "missing_qualifications": ["Docker"],
    "resume_improvements": ["Expand Python project descriptions."],
    "skills_to_develop": ["Learn Docker."]
}


# Test a successful recommendation request.
def test_successful_recommendation():
    with patch(
        "backend.recommendations.recommend_resume_improvements",
        return_value=MOCK_RECOMMENDATIONS
    ):
        response = client.post(
            "/api/resume/recommend",
            json={
                "profile": {
                    "name": "John Smith",
                    "skills": ["Python", "SQL"]
                },
                "job_description": "Python developer with Docker experience."
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            "recommendations": MOCK_RECOMMENDATIONS
        }

        print("Successful recommendation API test passed!")



# Test an empty job description.
def test_empty_job_description():
    response = client.post(
        "/api/resume/recommend",
        json={
            "profile": {
                "skills": ["Python", "SQL"]
            },
            "job_description": ""
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Job description cannot be empty."

    print("Empty job description test passed!")


# Test an invalid candidate profile.
def test_invalid_profile():
    response = client.post(
        "/api/resume/recommend",
        json={
            "profile": {
                "skills": "Python"
            },
            "job_description": "Software Engineer"
        }
    )

    assert response.status_code == 422

    print("Invalid candidate profile test passed!")


# Test an invalid Gemini response.
def test_invalid_ai_response():
    with patch(
        "backend.recommendations.recommend_resume_improvements",
        side_effect=ValueError("Invalid AI response")
    ):
        response = client.post(
            "/api/resume/recommend",
            json={
                "profile": {
                    "skills": ["Python"]
                },
                "job_description": "Software Engineer"
            }
        )

        assert response.status_code == 502
        assert response.json()["detail"] == (
            "AI returned an invalid recommendation response."
        )

        print("Invalid AI response test passed!")


# Test Gemini service unavailability.
def test_ai_service_failure():
    with patch(
        "backend.recommendations.recommend_resume_improvements",
        side_effect=RuntimeError("Gemini unavailable")
    ):
        response = client.post(
            "/api/resume/recommend",
            json={
                "profile": {
                    "skills": ["Python"]
                },
                "job_description": "Software Engineer"
            }
        )

        assert response.status_code == 503
        assert response.json()["detail"] == (
            "AI recommendations are temporarily unavailable."
        )

        print("AI service failure test passed!")


# Verify that personal information is removed before calling Gemini.
def test_personal_information_removal():
    with patch(
        "backend.recommendations.recommend_resume_improvements",
        return_value=MOCK_RECOMMENDATIONS
    ) as mock_recommender:

        response = client.post(
            "/api/resume/recommend",
            json={
                "profile": {
                    "name": "John Smith",
                    "email": "john@example.com",
                    "phone": "555-0100",
                    "skills": ["Python", "SQL"]
                },
                "job_description": "Python Developer"
            }
        )

        assert response.status_code == 200

        # Retrieve the profile passed to our AI recommender.
        mock_recommender.assert_called_once()
        sent_profile = mock_recommender.call_args.args[0]

        # Verify that personal information was removed.
        assert sent_profile.name == ""
        assert sent_profile.email == ""
        assert sent_profile.phone == ""

        # Verify that useful qualifications were preserved.
        assert sent_profile.skills == ["Python", "SQL"]

        print("Personal information removal test passed!")

# Verify that nested education and experience are converted correctly.
def test_nested_profile_conversion():
    with patch(
        "backend.recommendations.recommend_resume_improvements",
        return_value=MOCK_RECOMMENDATIONS
    ) as mock_recommender:

        response = client.post(
            "/api/resume/recommend",
            json={
                "profile": {
                    "skills": ["Python", "SQL"],
                    "education": [
                        {
                            "school": "UTRGV",
                            "degree": "Computer Science",
                            "graduation_date": "May 2027"
                        }
                    ],
                    "experience": [
                        {
                            "job_title": "Software Intern",
                            "company": "ABC Company",
                            "start_date": "May 2025",
                            "end_date": "August 2025",
                            "description": "Developed Python applications."
                        }
                    ],
                    "projects": ["Python data analysis application"],
                    "certifications": ["AWS Cloud Practitioner"]
                },
                "job_description": "Software Engineer"
            }
        )

        assert response.status_code == 200

        mock_recommender.assert_called_once()
        sent_profile = mock_recommender.call_args.args[0]

        # Verify education conversion.
        assert len(sent_profile.education) == 1
        assert sent_profile.education[0].school == "UTRGV"
        assert sent_profile.education[0].degree == "Computer Science"
        assert sent_profile.education[0].graduation_date == "May 2027"

        # Verify experience conversion.
        assert len(sent_profile.experience) == 1
        assert sent_profile.experience[0].job_title == "Software Intern"
        assert sent_profile.experience[0].company == "ABC Company"
        assert sent_profile.experience[0].start_date == "May 2025"
        assert sent_profile.experience[0].end_date == "August 2025"
        assert sent_profile.experience[0].description == (
            "Developed Python applications."
        )

        # Verify projects and certifications.
        assert sent_profile.projects == [
            "Python data analysis application"
        ]
        assert sent_profile.certifications == [
            "AWS Cloud Practitioner"
        ]

        print("Nested profile conversion test passed!")

if __name__ == "__main__":
    test_successful_recommendation()
    test_empty_job_description()
    test_invalid_profile()
    test_invalid_ai_response()
    test_ai_service_failure()
    test_personal_information_removal()
    test_nested_profile_conversion()

    print("\nAll recommendation API tests passed!")