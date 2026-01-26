import os
import fitz
import requests
from io import BytesIO

# def load_pdf(source: str) -> list:
#     """Load PDF and return list of pages with content and page number"""
#     if source.startswith("http"):
#         r = requests.get(source)
#         doc = fitz.open(stream=BytesIO(r.content), filetype="pdf")
#     else:
#         doc = fitz.open(source)

#     pages = []
#     for page_num, page in enumerate(doc, 1):
#         text = page.get_text()
#         pages.append({
#             "page_number": page_num,
#             "text": text.strip()
#         })
    
#     total_chars = sum(len(p["text"]) for p in pages)
#     print(f"Extracted {total_chars} characters from PDF with {len(pages)} pages.")
#     return pages


def load_pdf(source: str) -> list:
    """Load PDF and return list of pages with content and page number"""
    print(f"Loading data from {source}...")
    if source.startswith("http"):
        response = requests.get(source, timeout=20)
        response.raise_for_status()
        file_stream = BytesIO(response.content)
        doc = fitz.open(stream=file_stream, filetype="pdf")
    else:
        if not os.path.exists(source):
            raise FileNotFoundError(f"{source} not found")
        doc = fitz.open(source)

    pages = []
    for page_num, page in enumerate(doc, 1):
        text = page.get_text()
        pages.append({
            "page_number": page_num,
            "text": text.strip()
        })
    
    total_chars = sum(len(p["text"]) for p in pages)
    print(f"TOTAL EXTRACTED CHARS: {total_chars} from {len(pages)} pages")
    return pages
