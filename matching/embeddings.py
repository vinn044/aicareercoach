"""Create semantic job rankings from parsed candidate profiles.

Pipeline reference: PDF text -> CandidateProfile -> embedding vectors ->
cosine-similarity scores -> highest-to-lowest job ranking.
"""

import argparse
import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from resume_parser.models import CandidateProfile

from .sample_jobs import JobListing, SAMPLE_JOBS

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingModel(Protocol):
    """The small portion of a sentence-transformer model used here."""

    def encode(self, text: str) -> Sequence[float]: ...


@dataclass(frozen=True)
class RankedJob:
    job: JobListing
    score: float


def profile_to_embedding_text(profile: CandidateProfile) -> str:
    """Create a consistent semantic representation from parser output."""
    sections = []

    if profile.skills:
        sections.append(f"Skills: {', '.join(profile.skills)}")

    for experience in profile.experience:
        details = " ".join(
            value
            for value in (
                experience.job_title,
                f"at {experience.company}" if experience.company else "",
                f"({experience.start_date} to {experience.end_date})"
                if experience.start_date or experience.end_date
                else "",
                experience.description,
            )
            if value
        )
        if details:
            sections.append(f"Experience: {details}")

    for education in profile.education:
        details = " ".join(
            value
            for value in (
                education.degree,
                f"from {education.school}" if education.school else "",
                education.graduation_date,
            )
            if value
        )
        if details:
            sections.append(f"Education: {details}")

    if profile.projects:
        sections.append(f"Projects: {'; '.join(profile.projects)}")

    if profile.certifications:
        sections.append(f"Certifications: {', '.join(profile.certifications)}")

    return "\n".join(sections) or "Candidate profile contains no parsed details."


def job_to_embedding_text(job: JobListing) -> str:
    """Create a consistent semantic representation from a job listing."""
    parts = [f"Title: {job.title}", f"Description: {job.description}"]
    if job.company:
        parts.append(f"Company: {job.company}")
    if job.location:
        parts.append(f"Location: {job.location}")
    return "\n".join(parts)


def cosine_similarity(
    first_embedding: Iterable[float], second_embedding: Iterable[float]
) -> float:
    """Return cosine similarity for two vector embeddings."""
    first = [float(value) for value in first_embedding]
    second = [float(value) for value in second_embedding]

    if len(first) != len(second):
        raise ValueError("Embeddings must have the same number of dimensions.")

    first_magnitude = math.sqrt(sum(value * value for value in first))
    second_magnitude = math.sqrt(sum(value * value for value in second))
    if first_magnitude == 0 or second_magnitude == 0:
        raise ValueError("Cannot calculate similarity for a zero-length embedding.")

    dot_product = sum(
        first_value * second_value
        for first_value, second_value in zip(first, second, strict=True)
    )
    return dot_product / (first_magnitude * second_magnitude)


def rank_jobs(
    profile: CandidateProfile,
    jobs: Iterable[JobListing],
    model: EmbeddingModel,
) -> list[RankedJob]:
    """Rank job listings by semantic similarity to a parsed candidate profile."""
    # Encode the resume once, then compare that same vector with every job vector.
    resume_embedding = model.encode(profile_to_embedding_text(profile))
    ranked_jobs = [
        RankedJob(
            job=job,
            score=cosine_similarity(resume_embedding, model.encode(job_to_embedding_text(job))),
        )
        for job in jobs
    ]
    return sorted(ranked_jobs, key=lambda ranked_job: ranked_job.score, reverse=True)


def load_embedding_model(model_name: str = MODEL_NAME):
    """Load the model only when a real semantic matching run is requested."""
    try:
        from sentence_transformers import SentenceTransformer
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "Install the project dependencies with `pip install -r requirements.txt`."
        ) from error

    return SentenceTransformer(model_name)


def parse_pdf_resume(pdf_path: Path) -> CandidateProfile:
    """Run the existing PDF extraction and deterministic parser pipeline."""
    from resume_parser.extractor import extract_text_from_pdf
    from resume_parser.parser import parse_resume

    return parse_resume(extract_text_from_pdf(str(pdf_path)))


def print_rankings(label: str, profile: CandidateProfile, model: EmbeddingModel) -> None:
    print(f"\n{label}")
    print("=" * len(label))
    print(profile_to_embedding_text(profile))
    print("\nRanked jobs:")
    for position, ranked_job in enumerate(rank_jobs(profile, SAMPLE_JOBS, model), start=1):
        print(
            f"{position}. {ranked_job.job.title} at {ranked_job.job.company} "
            f"({ranked_job.score:.3f})"
        )


def main() -> None:
    # This is the entry point used by: python -m matching.embeddings --resume ...
    parser = argparse.ArgumentParser(
        description="Rank curated jobs against a parsed PDF resume."
    )
    parser.add_argument(
        "--resume",
        type=Path,
        required=True,
        help="Path to a local PDF resume.",
    )
    arguments = parser.parse_args()

    model = load_embedding_model()
    if not arguments.resume.is_file():
        parser.error(f"Resume PDF not found: {arguments.resume}")
    print_rankings("Parsed resume ranking", parse_pdf_resume(arguments.resume), model)


if __name__ == "__main__":
    main()
