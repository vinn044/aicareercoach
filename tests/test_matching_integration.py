import unittest

from matching.embeddings import (
    cosine_similarity,
    profile_to_embedding_text,
    rank_jobs,
)
from matching.sample_jobs import JobListing
from resume_parser.models import CandidateProfile, Education, Experience


class KeywordEmbeddingModel:
    """A dependency-free model used only to test ranking plumbing."""

    KEYWORDS = ("python", "sql", "react", "cashier")

    def encode(self, text):
        normalized_text = text.lower()
        return [float(normalized_text.count(keyword)) for keyword in self.KEYWORDS]


class MatchingIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.profile = CandidateProfile(
            skills=["Python", "SQL"],
            education=[Education(school="UTRGV", degree="BS Computer Science")],
            experience=[
                Experience(
                    job_title="Software Intern",
                    company="Example Co.",
                    description="Built Python data tools.",
                )
            ],
            projects=["Created a SQL dashboard"],
        )

    def test_profile_text_preserves_parsed_sections(self):
        profile_text = profile_to_embedding_text(self.profile)

        self.assertIn("Skills: Python, SQL", profile_text)
        self.assertIn("Experience: Software Intern at Example Co.", profile_text)
        self.assertIn("Education: BS Computer Science from UTRGV", profile_text)
        self.assertIn("Projects: Created a SQL dashboard", profile_text)

    def test_relevant_job_ranks_above_unrelated_job(self):
        jobs = [
            JobListing(
                title="Retail Cashier",
                company="Market",
                location="Local",
                description="Handle cash and assist customers as a cashier.",
            ),
            JobListing(
                title="Python Data Intern",
                company="Analytics Co.",
                location="Remote",
                description="Use Python and SQL to analyze data.",
            ),
        ]

        rankings = rank_jobs(self.profile, jobs, KeywordEmbeddingModel())

        self.assertEqual(rankings[0].job.title, "Python Data Intern")
        self.assertGreater(rankings[0].score, rankings[1].score)

    def test_cosine_similarity_rejects_zero_vector(self):
        with self.assertRaises(ValueError):
            cosine_similarity([0, 0], [1, 0])


if __name__ == "__main__":
    unittest.main()
