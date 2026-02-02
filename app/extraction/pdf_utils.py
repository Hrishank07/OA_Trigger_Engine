import os
from pydantic import BaseModel

class PdfUtils:
    @staticmethod
    def extract_text(filepath: str) -> str:
        """
        Extracts text from a PDF file using pypdf.
        """
        import pypdf
        text = ""
        try:
            reader = pypdf.PdfReader(filepath)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading PDF {filepath}: {e}")
            return ""
        return text
