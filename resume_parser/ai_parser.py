from openai import OpenAI

client = OpenAI()


def parse_resume_with_ai(resume_text):
    """
    Send extracted resume text to an AI model
    and return the AI's response.
    """

    response = client.responses.create(
        model="gpt-6-luna",
        instructions=(
            "You are a resume parsing assistant. "
            "Extract information only from the provided resume. "
            "Do not invent information that is not present."
        ),
        input=resume_text
    )

    return response.output_text