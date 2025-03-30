import os
import mammoth
import PyPDF2
import textract
from typing import Optional
import re


class FileReader:
    @staticmethod
    def read_file(file_path: str) -> Optional[str]:
        """Read resume files with robust DOCX/DOC support using mammoth"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            extension = os.path.splitext(file_path)[1].lower()

            if extension == '.pdf':
                return FileReader._read_pdf(file_path)
            elif extension == '.docx':
                # Try mammoth first for best DOCX handling
                text = FileReader._read_docx_with_mammoth(file_path)
                if not text or len(text.strip()) < 50:
                    text = FileReader._read_docx_standard(file_path)
                return text
            elif extension == '.doc':
                return FileReader._read_doc(file_path)
            else:
                return FileReader._read_via_textract(file_path)

        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
            return None

    @staticmethod
    def _read_pdf(file_path: str) -> str:
        """Read PDF using PyPDF2"""
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return " ".join(page.extract_text() for page in reader.pages)
        except Exception as e:
            print(f"PDF read error: {str(e)}")
            return ""

    @staticmethod
    def _read_docx_with_mammoth(file_path: str) -> str:
        """Read DOCX using mammoth for best formatting handling"""
        try:
            with open(file_path, "rb") as f:
                result = mammoth.extract_raw_text(f)
                text = result.value

                # Clean up mammoth's output
                text = re.sub(r'\n\s*\n', '\n', text)  # Remove excessive newlines
                text = text.strip()

                # Handle any mammoth messages (warnings/errors)
                if result.messages:
                    print(f"Mammoth messages for {file_path}:")
                    for message in result.messages:
                        print(f"- {message}")

                return text if text else ""
        except Exception as e:
            print(f"Mammoth DOCX read failed: {str(e)}")
            return ""

    @staticmethod
    def _read_docx_standard(file_path: str) -> str:
        """Fallback DOCX reader using python-docx"""
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
        except Exception as e:
            print(f"Standard DOCX read failed: {str(e)}")
            return ""

    @staticmethod
    def _read_doc(file_path: str) -> str:
        """Read .doc using textract"""
        try:
            text = textract.process(file_path).decode('utf-8')
            # Clean non-ASCII characters
            return text.encode('ascii', errors='ignore').decode('ascii')
        except Exception as e:
            print(f"DOC read failed: {str(e)}")
            return ""

    @staticmethod
    def _read_via_textract(file_path: str) -> str:
        """Fallback method using textract"""
        try:
            text = textract.process(file_path).decode('utf-8')
            # Basic cleaning
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        except Exception as e:
            print(f"Textract read failed: {str(e)}")
            return ""