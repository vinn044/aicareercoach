"""Curated job fixtures used for local semantic-matching evaluation.

Each listing below is converted to an embedding and compared with the imported
resume; these are test data, not live job postings.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class JobListing:
    """The job details used to create one job embedding."""
    title: str
    company: str
    location: str
    description: str
    application_url: str = ""


SAMPLE_JOBS = [
    JobListing(
        title="Junior Data Scientist",
        company="Insight Labs",
        location="Remote",
        description=(
            "Analyze datasets with Python, SQL, Pandas, and machine learning. "
            "Build reports and collaborate with product teams."
        ),
        application_url="https://example.com/jobs/junior-data-scientist",
    ),
    JobListing(
        title="Pediatric Nurse",
        company="Cloud Harbor",
        location="Austin, TX",
        description=(
            "Provide compassionate care to pediatric patients in a hospital setting. "
            "Assist with medical procedures, document patient information, and collaborate with healthcare teams."
        ),
        application_url="https://example.com/jobs/pediatric-nurse",
    ),
    JobListing(
        title="Wendys Crew Member",
        company="Wendy's",
        location="McAllen, TX",
        description=(
            "Prepare food, take orders, and provide excellent customer service in a fast-paced restaurant environment."
        ),
        application_url="https://example.com/jobs/frontend-intern",
    ),
    JobListing(
        title="IT Support Assistant",
        company="Campus Technology Services",
        location="Edinburg, TX",
        description=(
            "Troubleshoot Windows and Linux devices, document support requests, "
            "and assist users with software and network issues."
        ),
        application_url="https://example.com/jobs/it-support-assistant",
    ),
    JobListing(
        title="Psychology Research Assistant",
        company="Northstar Systems",
        location="Dallas, TX",
        description=(
            "Assist with psychological research studies, collect and analyze data, "
        ),
        application_url="https://example.com/jobs/cloud-operations-intern",
    ),
    JobListing(
        title="Retail Cashier",
        company="Neighborhood Market",
        location="McAllen, TX",
        description=(
            "Process customer purchases, handle cash, stock merchandise, and "
            "provide friendly customer service in a busy retail store."
        ),
        application_url="https://example.com/jobs/retail-cashier",
    ),
    JobListing(
        title="Restaurant Shift Supervisor",
        company="Community Kitchen",
        location="McAllen, TX",
        description=(
            "Lead front-of-house and kitchen operations, train team members, "
            "handle food safety procedures, and support customer service."
        ),
        application_url="https://example.com/jobs/restaurant-supervisor",
    ),
    JobListing(
        title="Quant Research Intern",
        company="Ledger Partners",
        location="Remote",
        description=(
            "Assist with quantitative research, data analysis, and financial modeling. "
        ),
        application_url="https://example.com/jobs/quant-research-intern",
    ),
]
