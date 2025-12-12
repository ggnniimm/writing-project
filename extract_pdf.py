
import sys
try:
    from pypdf import PdfReader
except ImportError:
    try:
        import PyPDF2 as PdfReader # Fallback
    except ImportError:
        print("Error: pypdf or PyPDF2 not installed.")
        sys.exit(1)

def extract_text(filepath):
    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_pdf.py <pdf_file>")
        sys.exit(1)
    
    content = extract_text(sys.argv[1])
    if content:
        print(content)
