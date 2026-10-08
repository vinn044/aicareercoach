# Imports the PyMuPDF library, which allows us to open and read PDF files.
import fitz


def extract_text_from_pdf(file_path):
    """
    Extracts all readable text from a PDF resume.

    Parameters:
        file_path: The location of the PDF file being uploaded.

    Returns:
        A string containing all text extracted from the PDF.
    """

    # Opens the PDF resume using the file path provided.
    document = fitz.open(file_path)

    # Creates an empty string to store the extracted text.
    text = ""

    # Loops through every page in the PDF document.
    for page in document:

        # Extracts the text from the current page and adds it
        # to the text collected from previous pages.
        text += page.get_text()

    # Closes the PDF document to free up system resources.
    document.close()

    # Returns the extracted text so it can be used by
    # the resume parser to identify skills, education,
    # work experience, and other candidate information.
    return text


# The code below was originally used to manually test the extractor.
# 

# if __name__ == "__main__":
#     from parser import parse_resume
#
#     resume_text = extract_text_from_pdf("test_resume.pdf")
#
#     candidate = parse_resume(resume_text)
#
#     print(candidate)
