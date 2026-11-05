
"""
Job-Specific AI Resume Recommendation System.

Uses Gemini AI to compare a candidate's resume
against a selected job description and provide
personalized recommendations.
"""
import json
from google import genai
from google.genai import errors


def recommend_resume_improvements(profile, job_description):
    """
    Generates job-specific resume recommendations.

    Parameters:
        profile: CandidateProfile object containing
                 the user's resume information.

        job_description: String containing the
                         selected job's requirements.

    Returns:
        Dictionary containing the AI recommendations.
    """

    # Step 1: Make sure the job description is valid.
    if not isinstance(job_description, str) or not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    # Step 2: Convert the CandidateProfile into JSON.
    resume_json = profile.to_json()

    # Step 3: Create our Gemini client.
    # Uses the GEMINI_API_KEY environment variable.
    client = genai.Client()

    # Step 4: Tell Gemini how to compare the resume
    # against the selected job description.
    prompt = f"""
    You are an AI career coach helping a job applicant
    improve their resume for a specific position.

    Compare the candidate's resume with the job
    description provided below.

    Identify:
    1. Skills and qualifications the candidate already has.
    2. Required skills and qualifications not demonstrated
       in the resume.
    3. Ways to improve how existing experience is described.
    4. Skills, certifications, or projects the candidate
       could develop to become more qualified.

    IMPORTANT RULES:
    - Only use information actually found in the resume.
    - Never invent qualifications or work experience.
    - Do not suggest adding skills the candidate
      has not actually learned.
    - Distinguish missing resume evidence from
      genuinely missing qualifications.
    - Make recommendations specific and actionable.
    - Do not calculate a match percentage.
      Our existing job matching system handles scoring.

    Return a JSON object with exactly these fields:

    {{
        "matching_qualifications": [],
        "missing_qualifications": [],
        "resume_improvements": [],
        "skills_to_develop": []
    }}

    Each field must contain a list of strings.

    CANDIDATE RESUME:
    {resume_json}

    JOB DESCRIPTION:
    {job_description}
    """

     # Step 5: Ask Gemini to analyze the resume.
    # Handle API failures without exposing technical details.

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )

    except errors.APIError as error:
        raise RuntimeError(
            "AI resume recommendations are temporarily "
            "unavailable. Please try again later."
        ) from error

    # Step 6: Make sure Gemini returned valid JSON.
    try:
        recommendations = json.loads(response.text)

    except (json.JSONDecodeError, TypeError):
        raise ValueError(
            "Gemini returned an invalid recommendation response."
        )

    # Step 7: Make sure the response is a dictionary.
    if not isinstance(recommendations, dict):
        raise ValueError(
            "AI recommendations must be a dictionary."
        )

    # Step 8: Define the fields we expect from Gemini.
    required_fields = [
        "matching_qualifications",
        "missing_qualifications",
        "resume_improvements",
        "skills_to_develop"
    ]

    # Step 9: Validate each recommendation category.
    for field in required_fields:

        # Every required field must contain a list.
        if field not in recommendations or not isinstance(
            recommendations[field], list
        ):
            raise ValueError(
                f"Invalid or missing recommendation field: {field}"
            )

        # Every item in the list must be a string.
        for item in recommendations[field]:
            if not isinstance(item, str):
                raise ValueError(
                    f"Invalid recommendation item in: {field}"
                )

    # Step 10: Return the validated recommendations.
    return recommendations

