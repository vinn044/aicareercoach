from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from resume_parser.models import (
    CandidateProfile,
    Education,
    Experience,
)

from resume_parser.recommender import recommend_resume_improvements


# Create a standalone router for AI resume recommendations.
router = APIRouter(
    prefix="/api/resume",
    tags=["Resume Recommendations"],
)


# ==========================================
# API REQUEST MODELS
# ==========================================

# Represents the candidate's education.
class EducationRequest(BaseModel):
    school: str = ""
    degree: str = ""
    graduation_date: str = ""


# Represents the candidate's work experience.
class ExperienceRequest(BaseModel):
    job_title: str = ""
    company: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""


# Represents the candidate's parsed resume.
class CandidateProfileRequest(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    skills: list[str] = []
    education: list[EducationRequest] = []
    experience: list[ExperienceRequest] = []
    projects: list[str] = []
    certifications: list[str] = []


# Represents the complete recommendation request.
class RecommendationRequest(BaseModel):
    profile: CandidateProfileRequest
    job_description: str


# ==========================================
# API RESPONSE MODELS
# ==========================================

# Represents the four categories of AI recommendations.
class RecommendationResult(BaseModel):
    matching_qualifications: list[str]
    missing_qualifications: list[str]
    resume_improvements: list[str]
    skills_to_develop: list[str]


# Represents the complete API response.
class RecommendationResponse(BaseModel):
    recommendations: RecommendationResult


# ==========================================
# CANDIDATE PROFILE CONVERSION
# ==========================================

def convert_to_candidate_profile(
    profile: CandidateProfileRequest
) -> CandidateProfile:
    """Convert validated API data into a CandidateProfile object."""

    return CandidateProfile(
        name=profile.name,
        email=profile.email,
        phone=profile.phone,
        skills=profile.skills,
        education=[
            Education(**education.model_dump())
            for education in profile.education
        ],
        experience=[
            Experience(**experience.model_dump())
            for experience in profile.experience
        ],
        projects=profile.projects,
        certifications=profile.certifications,
    )


# ==========================================
# AI RECOMMENDATION ENDPOINT
# ==========================================

@router.post(
    "/recommend",
    response_model=RecommendationResponse
)
def recommend_resume(request: RecommendationRequest):
    """Generate AI resume recommendations for a selected job."""

    # Make sure the job description is not empty.
    if not request.job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )

    # Convert the incoming API data into our existing CandidateProfile.
    profile = convert_to_candidate_profile(request.profile)

    # Remove unnecessary personal information before sending to Gemini.
    profile.name = ""
    profile.email = ""
    profile.phone = ""

    try:
        # Generate personalized recommendations using Gemini.
        recommendations = recommend_resume_improvements(
            profile,
            request.job_description
        )

    except RuntimeError as error:
        # Handle Gemini API failures.
        raise HTTPException(
            status_code=503,
            detail="AI recommendations are temporarily unavailable."
        ) from error

    except ValueError as error:
        # Handle invalid AI responses.
        raise HTTPException(
            status_code=502,
            detail="AI returned an invalid recommendation response."
        ) from error

    # Return the recommendations to the frontend.
    return {
        "recommendations": recommendations
    }