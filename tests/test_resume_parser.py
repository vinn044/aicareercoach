from resume_parser.extractor import extract_text_from_pdf
from resume_parser.parser import parse_resume


resume_text = extract_text_from_pdf("test_resume.pdf")

candidate = parse_resume(resume_text)

print("----- EXTRACTED TEXT -----")
print(resume_text)

print("\n----- CANDIDATE PROFILE -----")
print(candidate)
print("\n----- JSON OUTPUT -----")
print(candidate.to_json())

# Automated tests
assert candidate.name == "Christopher Kegley"
assert "Python" in candidate.skills
assert len(candidate.education) > 0
assert len(candidate.experience) > 0
assert len(candidate.projects) > 0
assert len(candidate.certifications) > 0

print("\nAll resume parser tests passed!")