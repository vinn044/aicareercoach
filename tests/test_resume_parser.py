from resume_parser.extractor import extract_text_from_pdf
from resume_parser.parser import parse_resume


resume_text = extract_text_from_pdf("test_resume.pdf")

candidate = parse_resume(resume_text)

print("----- EXTRACTED TEXT -----")
print(resume_text)

print("\n----- CANDIDATE PROFILE -----")
print(candidate)