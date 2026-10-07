from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from resume_parser.extractor import extract_text_from_pdf
from resume_parser.parser import parse_resume

app = FastAPI(title="AI Career Coach API")

# Allow the local React development server to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/resume/parse")
def parse_uploaded_resume(file: UploadFile):
    try:
        if not (file.filename or "").lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Please upload a PDF resume.",
            )

        # Read at most 10 MB plus one byte to detect oversized files.
        contents = file.file.read(10 * 1024 * 1024 + 1)

        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="The PDF must be 10 MB or smaller.",
            )

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        # Use a fixed filename and delete the temporary file afterward.
        with TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "resume.pdf"
            pdf_path.write_bytes(contents)

            try:
                text = extract_text_from_pdf(str(pdf_path))
            except Exception as exc:
                raise HTTPException(
                    status_code=400,
                    detail="Could not read this PDF. Try an unencrypted PDF.",
                ) from exc

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found. Upload a text-based PDF.",
            )

        profile = parse_resume(text)
        return profile.to_dict()

    finally:
        file.file.close()