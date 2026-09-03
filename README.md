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

## Status

Idea/planning stage. No code written yet.
