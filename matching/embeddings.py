from sentence_transformers import SentenceTransformer

from jobone import job

from resumeone import resume_one
from resumetwo import resume_two

# 1. Load a pretrained Sentence Transformer model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


resume_one_text = f"""
Skills: {", ".join(resume_one["skills"])}
Experience: {resume_one["experience"]}
Education: {resume_one["education"]}
"""

print(resume_one_text)

resume_two_text = f"""
Skills: {", ".join(resume_two["skills"])}
Experience: {resume_two["experience"]}
Education: {resume_two["education"]}
"""

print(resume_two_text)

job_text = f"""
Title: {job["title"]}
Description: {job["description"]}
"""

print(job_text)

#create embeddings for the two resume texts

resume_one_embedding = model.encode(resume_one_text)

print(resume_one_embedding.shape)

resume_two_embedding = model.encode(resume_two_text)

print(resume_two_embedding.shape)

# Create embeddings for the job text

job_embedding = model.encode(job_text)

print(job_embedding.shape)

# compare the embeddings from both resumes using cosine similarity

similarity_one = model.similarity(resume_one_embedding, job_embedding)
similarity_two = model.similarity(resume_two_embedding, job_embedding)

print(similarity_one)
print(similarity_two)