from resume_parser.extractor import extract_text_from_pdf
from resume_parser.parser import parse_resume

#One limitation: we're currently assuming the lines appear in a specific order.

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
assert len(candidate.education) == 2
assert len(candidate.experience) == 2
assert len(candidate.projects) > 0
assert len(candidate.certifications) > 0

# Test structured education
assert candidate.education[0].school == "University of Texas Rio Grande Valley"
assert candidate.education[0].degree == "Bachelor of Science in Computer Science"
assert candidate.education[0].graduation_date == "Expected Graduation: May 2027"

assert candidate.education[1].school == "South Texas College"
assert candidate.education[1].degree == "Associate of Science in Computer Science"
assert candidate.education[1].graduation_date == "May 2024"

# Test structured experience
assert candidate.experience[0].job_title == "Software Intern"
assert candidate.experience[0].company == "ABC Company"
assert candidate.experience[0].start_date == "May 2025"
assert candidate.experience[0].end_date == "August 2025"
#assert candidate.experience[0].description == "Developed and tested web applications."

assert candidate.experience[1].job_title == "IT Assistant"
assert candidate.experience[1].company == "XYZ Company"
assert candidate.experience[1].start_date == "January 2024"
assert candidate.experience[1].end_date == "April 2025"

# Test dictionary/JSON structure
candidate_dict = candidate.to_dict()

assert "name" in candidate_dict
assert "skills" in candidate_dict
assert "education" in candidate_dict
assert "experience" in candidate_dict
assert "projects" in candidate_dict
assert "certifications" in candidate_dict

# Test structured JSON data
assert candidate_dict["education"][0]["school"] == "University of Texas Rio Grande Valley"
assert candidate_dict["experience"][0]["job_title"] == "Software Intern"
assert candidate_dict["experience"][0]["company"] == "ABC Company"

assert candidate_dict["education"][0]["school"] == "University of Texas Rio Grande Valley"
assert candidate_dict["education"][1]["school"] == "South Texas College"

print("\nAll resume parser tests passed!")