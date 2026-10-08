from resume_parser.extractor import extract_text_from_pdf
from resume_parser.ai_parser import parse_resume_with_ai
from resume_parser.models import CandidateProfile, Education, Experience

resume_text = extract_text_from_pdf("test_resume.pdf")

print("----- RESUME TEXT -----")
print(resume_text)

print("\n----- AI RESPONSE -----")

result = parse_resume_with_ai(resume_text)

print(result)

assert isinstance(result, CandidateProfile)
assert isinstance(result.skills, list)
assert all(isinstance(item, Education) for item in result.education)
assert all(isinstance(item, Experience) for item in result.experience)
assert isinstance(result.to_json(), str)

print("\nAll Gemini AI parser tests passed!")