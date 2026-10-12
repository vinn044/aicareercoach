# Semantic Matching

This package ranks job listings by semantic similarity to a parsed
`CandidateProfile`. It intentionally keeps a small set of fake jobs and
resumes so ranking behavior remains repeatable while the team adds a real job
data source.

## Try a personal resume safely

Put a PDF in `local_resumes/`, which Git ignores, then run:

```bash
python -m matching.embeddings --resume local_resumes/my_resume.pdf
```

The command uses the existing `resume_parser` extraction pipeline and prints
the text that was generated from the resulting profile before showing rankings.
Do not commit personal resumes.

## Next integration points

- Replace `SAMPLE_JOBS` with records from an approved job-listings API.
- Store each job's metadata, embedding, and application URL in PostgreSQL with
  `pgvector`.
- Keep `profile_to_embedding_text()` and `job_to_embedding_text()` stable so
  stored and query embeddings share the same format.
