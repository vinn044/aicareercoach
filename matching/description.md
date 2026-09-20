# Job Matching

This is my current work for the job matching part of our Career Coach platform.

Right now I'm using Sentence Transformers with the `all-MiniLM-L6-v2` model to turn resumes and job listings into embeddings. Each one gets converted into a 384 dimensional vector.

For testing, I made two fake resumes and one fake job listing. One resume has skills that match the job pretty well (Python, SQL, Pandas, Machine Learning), while the other is intentionally unrelated work experience.

I'm using cosine similarity to compare each resume embedding to the job embedding. it's measuring the angle/direction between the vectors. Conceptually though, you will see that resumeone is semantically "closer" to jobone, than resumetwo and jobone is.

## Files

- `embeddings.py` - creates the embeddings and compares them
- `resumeone.py` - fake CS resume
- `resumetwo.py` - fake unrelated resume
- `jobone.py` - fake data science job

## So far

- Set up Sentence Transformers
- Created embeddings for resumes
- Created embeddings for job listings
- Compared resume/job embeddings using cosine similarity
- Tested relevant vs unrelated resumes

## Next

## Next

The next step is to find a job listings API so I can start working with real job data instead of fake listings/manually writing each one. The job descriptions will be converted into embeddings and stored in a vector database.

After that, the goal is to use the resume embedding to search the vector database and return the jobs that are most similar to the user's resume.

Eventually the fake resume data will also be replaced with the actual output from our resume parser.