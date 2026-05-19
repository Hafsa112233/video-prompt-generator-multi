import pypdf
from pathlib import Path


def read_pdf(file_path: str) -> dict:
    """
    Read a PDF file and extract all text from it.

    Args:
        file_path: The path to the PDF file

    Returns:
        Dictionary containing the extracted text and status
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return {"error": f"File not found: {file_path}", "status": "error"}

        if not str(file_path).endswith(".pdf"):
            return {"error": "File must be a PDF", "status": "error"}

        reader = pypdf.PdfReader(file_path)

        text = ""
        for page in reader.pages:
            text += page.extract_text()

        return {
            "text": text,
            "pages": len(reader.pages),
            "status": "success",
        }

    except Exception as e:
        return {"error": str(e), "status": "error"}