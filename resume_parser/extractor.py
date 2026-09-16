import fitz


def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF resume.
    """
    # opens the resume 
    document = fitz.open(file_path) 

    text = ""

    # goes through ever page of the document 
    for page in document:
        text += page.get_text() #extracts the text from each page

    document.close()

    return text # returns the text to whatever part of the application called the function

if __name__ == "__main__":
    resume_text = extract_text_from_pdf("test_resume.pdf")
    print(resume_text)