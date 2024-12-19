import os
import PyPDF2
from typing import Optional


def save_text_to_file(text: str, file_path: str) -> None:
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)
        print(f"Text extracted from PDF saved to txt file: {file_path}")

## PREPROCESSING INFO FROM PROJECTS
class TextExtractor:
    def __init__(self, max_chars: int = 100000):
        self.max_chars = max_chars

    def validate_file(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            print(f"Error: File not found at path: {file_path}")
            return False
        if not (file_path.lower().endswith('.pdf') or file_path.lower().endswith('.txt')):
            print("Error: File is not a PDF or text file")
            return False
        return True

    def extract_text(self, file_path: str) -> Optional[str]:
        """Extract text from either PDF or text file"""
        if not self.validate_file(file_path):
            return None

        try:
            if file_path.lower().endswith('.pdf'):
                return self._extract_from_pdf(file_path)
            else:
                return self._extract_from_text(file_path)
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return None

    def _extract_from_text(self, file_path: str) -> str:
        """Extract text from text file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read(self.max_chars)
            print(f"Processed text file with {len(text)} characters")
            return text

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            print(f"Processing PDF with {num_pages} pages...")

            extracted_text = []
            total_chars = 0

            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                if total_chars + len(text) > self.max_chars:
                    remaining_chars = self.max_chars - total_chars
                    extracted_text.append(text[:remaining_chars])
                    print(f"Reached {self.max_chars} character limit at page {page_num + 1}")
                    break

                extracted_text.append(text)
                total_chars += len(text)
                print(f"Processed page {page_num + 1}/{num_pages}")

            final_text = '\n'.join(extracted_text)
            print(f"\nExtraction complete! Total characters: {len(final_text)}")
            return final_text



# use:
if __name__ == "__main__":
    extractor = TextExtractor(max_chars=100000)
    text = extractor.extract_text("path/to/your/file.pdf")
