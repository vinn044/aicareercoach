"""Curated job fixtures used for local semantic-matching evaluation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class JobListing:
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
        title="Backend Software Engineering Intern",
        company="Cloud Harbor",
        location="Austin, TX",
        description=(
            "Help develop Python and FastAPI services. Work with PostgreSQL, "
            "REST APIs, Git, Docker, and automated tests."
        ),
        application_url="https://example.com/jobs/backend-intern",
    ),
    JobListing(
        title="Frontend Developer Intern",
        company="Bright Web Studio",
        location="Remote",
        description=(
            "Build responsive React and JavaScript interfaces with HTML and CSS. "
            "Collaborate through GitHub pull requests."
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
        title="Cloud Operations Intern",
        company="Northstar Systems",
        location="Dallas, TX",
        description=(
            "Support AWS infrastructure, Docker deployments, Linux operations, "
            "and monitoring for web applications."
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
        title="Accounting Intern",
        company="Ledger Partners",
        location="Remote",
        description=(
            "Assist with invoices, account reconciliation, Excel reports, and "
            "financial record keeping under the direction of staff accountants."
        ),
        application_url="https://example.com/jobs/accounting-intern",
    ),
]
