from resume_parser.extractor import extract_text_from_pdf
from resume_parser.ai_parser import parse_resume_with_ai


resume_text = extract_text_from_pdf("test_resume.pdf")

print("----- RESUME TEXT -----")
print(resume_text)

print("\n----- AI RESPONSE -----")

result = parse_resume_with_ai(resume_text)

print(result)