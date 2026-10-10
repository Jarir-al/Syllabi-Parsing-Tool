import os
import io
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import your existing pipeline modules
from schema import CourseSyllabus
from extractor import extract_with_gemini
# Assuming your Stage 1 / Stage 2 cleaning logic lives in trimmer/cleaner
import pdfplumber
from trimmer import trim_syllabus_text  # adjust import to your cleaner function

load_dotenv()

app = FastAPI(title="Astrolabe Syllabus Parser API", version="1.0.0")

# Allow requests from your Next.js local dev or production URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_raw_pdf_text(file_bytes: bytes) -> str:
    """Extract raw text and table Markdown from PDF bytes."""
    extracted_chunks = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            # Extract plain text
            text = page.extract_text()
            if text:
                extracted_chunks.append(text)
            
            # Extract tables as markdown lines if available
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    clean_row = [str(cell).strip() if cell else "" for cell in row]
                    extracted_chunks.append(" | ".join(clean_row))
                    
    return "\n".join(extracted_chunks)

@app.post("/api/parse-syllabus", response_model=CourseSyllabus)
async def parse_syllabus_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        content = await file.read()
        
        # 1. Extract raw text from PDF
        raw_text = extract_raw_pdf_text(content)
        if not raw_text.strip():
            raise HTTPException(status_code=422, detail="No readable text found in PDF.")

        # 2. Stage 2: Heuristic trimming / boilerplate scrub
        cleaned_text = trim_syllabus_text(raw_text)

        # 3. Stage 3: Gemini Structured Extraction with Pydantic
        syllabus_data = extract_with_gemini(cleaned_text)
        
        return syllabus_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)