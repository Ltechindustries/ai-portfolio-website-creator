import pdfplumber
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_stream):
    """
    Extracts all text from a PDF file stream.
    Accepts a file-like object (e.g. BytesIO or Flask FileStorage).
    """
    try:
        text_content = []
        with pdfplumber.open(file_stream) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
                else:
                    logger.warning(f"Could not extract text from page {page_num}")
        
        full_text = "\n\n".join(text_content)
        if not full_text.strip():
            raise ValueError("No text could be extracted from the PDF. The PDF may be empty or scanned as an image.")
            
        return full_text
    except Exception as e:
        logger.error(f"Error extracting PDF: {str(e)}")
        raise e
