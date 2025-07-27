import fitz
from collections import defaultdict

MAX_HEADING_CHAR_LENGTH = 120

def clean_text(text):
    return ' '.join(text.strip().split())

def detect_headers_footers(pdf_path, min_repeat=2):
    """Detect repeated header/footer lines to filter out."""
    doc = fitz.open(pdf_path)
    all_headers = defaultdict(int)
    all_footers = defaultdict(int)

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        page_height = page.rect.height
        for block in blocks:
            if "lines" not in block: 
                continue
            for line in block["lines"]:
                text = "".join(span["text"] for span in line["spans"]).strip()
                y = round(line["bbox"][1], 1)
                if y < 100:
                    all_headers[text] += 1
                if y > page_height - 100:
                    all_footers[text] += 1
    doc.close()
    return set([t for t, c in all_headers.items() if c >= min_repeat] +
               [t for t, c in all_footers.items() if c >= min_repeat])

def extract_outline(pdf_path, font_size_threshold=11):
    """Extract headings with bounding box y0 coordinate."""
    doc = fitz.open(pdf_path)
    outline = []
    for i, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    txt = span["text"].strip()
                    font_size = span["size"]
                    bbox = span["bbox"]
                    if len(txt) > 1 and font_size >= font_size_threshold and len(txt) <= MAX_HEADING_CHAR_LENGTH:
                        outline.append({
                            "page": i,
                            "text": txt,
                            "y0": bbox[1]
                        })
    doc.close()
    return outline
