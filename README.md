# AI Career Coach

Senior project idea — an AI-assisted resume analyzer and job matcher.

## Planned Features

- Resume parsing into structured data (skills, experience, education) via a custom parser
- ATS/formatting feedback
- Job matching using semantic similarity search (embeddings), not just keywords
- AI-generated feedback explaining resume improvements and job match reasoning

## Planned Stack

- **Database:** PostgreSQL + `pgvector` (relational + vector search)
- **Job data source:** Job listings API (Indeed / LinkedIn / Adzuna — TBD)
- **Embeddings:** Pretrained embedding model for resume/job similarity matching (maybe sentence-transformers)
- **LLM:** Limited to the feedback/explanation layer, not parsing or matching — to avoid being a thin LLM wrapper

## Current Prototype

- PDF resume extraction and rule-based profile parsing
- Semantic matching demo using Sentence Transformers
- Curated sample job listings for repeatable local matching tests

## Local Setup

Use Python 3.11 through 3.13, create a virtual environment, and install the
project dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

To rank the included sample resumes against the curated job fixtures:

```bash
python -m matching.embeddings
```

To rank a local PDF resume, keep it in `local_resumes/` (which is ignored by
Git) and run:

```bash
python -m matching.embeddings --resume local_resumes/my_resume.pdf
```

The first matching run downloads the embedding model. Scores are useful for
ranking jobs relative to one another; they are not application-readiness
percentages.
