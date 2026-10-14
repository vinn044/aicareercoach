from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from matching.embeddings import load_embedding_model, rank_jobs
from matching.sample_jobs import JobListing, SAMPLE_JOBS
from resume_parser.extractor import extract_text_from_pdf
from resume_parser.parser import extract_skills, parse_resume

app = FastAPI(title="AI Career Coach API")

# Allow the local React development server to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


def job_payload(job: JobListing, score: float | None = None) -> dict:
    payload = asdict(job)
    if score is not None:
        payload["score"] = score
    return payload


@lru_cache(maxsize=1)
def matching_model():
    # Loading model weights is expensive; reuse one model for every request.
    return load_embedding_model()


def parse_uploaded_resume(file: UploadFile):
    """Validate an uploaded PDF and return the existing parsed profile."""
    try:
        if not (file.filename or "").lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Please upload a PDF resume.",
            )

        # Read at most 10 MB plus one byte to detect oversized files.
        contents = file.file.read(10 * 1024 * 1024 + 1)

        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="The PDF must be 10 MB or smaller.",
            )

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        # Use a fixed filename and delete the temporary file afterward.
        with TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "resume.pdf"
            pdf_path.write_bytes(contents)

            try:
                text = extract_text_from_pdf(str(pdf_path))
            except Exception as exc:
                raise HTTPException(
                    status_code=400,
                    detail="Could not read this PDF. Try an unencrypted PDF.",
                ) from exc

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found. Upload a text-based PDF.",
            )

        return parse_resume(text)

    finally:
        file.file.close()


@app.get("/api/jobs")
def list_jobs():
    """Expose the same sample jobs the ranking endpoint uses."""
    return {"jobs": [job_payload(job) for job in SAMPLE_JOBS]}


@app.post("/api/resume/parse")
def parse_resume_endpoint(file: UploadFile):
    """Keep the original parser-only endpoint available for the current UI."""
    return parse_uploaded_resume(file).to_dict()


@app.post("/api/resume/match")
def match_uploaded_resume(file: UploadFile):
    profile = parse_uploaded_resume(file)
    ranked_jobs = rank_jobs(profile, SAMPLE_JOBS, matching_model())
    top_match = ranked_jobs[0]

    # Compare recognized skill names, not embedding values, for an explainable card.
    top_job_text = f"{top_match.job.title}\n{top_match.job.description}"
    top_job_skills = {skill.casefold() for skill in extract_skills(top_job_text)}
    matching_skills = [
        skill for skill in profile.skills if skill.casefold() in top_job_skills
    ]

    return {
        "profile": profile.to_dict(),
        "top_match": job_payload(top_match.job, top_match.score),
        "matching_skills": matching_skills,
        "ranked_jobs": [
            job_payload(ranked.job, ranked.score) for ranked in ranked_jobs
        ],
    }
