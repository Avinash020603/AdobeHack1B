import fitz
from collections import defaultdict
from utils.pdf_structure_utils import extract_outline, detect_headers_footers, clean_text
from utils.text_utils import clean_section_title

def extract_chunks_with_outline(pdf_path):
    """
    Extract text chunks grouped by headings bounded by y coordinate.
    Remove header/footer repeated lines.
    Returns list of dicts with keys: text, page, section_title.
    """
    doc = fitz.open(pdf_path)
    outline = extract_outline(pdf_path)
    outline_by_page = defaultdict(list)
    for h in outline:
        outline_by_page[h["page"]].append(h)

    hf_strings = detect_headers_footers(pdf_path)

    chunks = []

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: b[1])  

        headings = sorted(outline_by_page.get(page_num, []), key=lambda h: h["y0"])

        if not headings:
            lines = page.get_text().split('\n')
            filtered_lines = [line for line in lines if line.strip() and line.strip() not in hf_strings]
            text = " ".join(filtered_lines).strip()
            if text:
                chunks.append({
                    "text": text,
                    "page": page_num + 1,
                    "section_title": f"Page {page_num + 1}"
                })
            continue

        for i, heading in enumerate(headings):
            y_start = heading["y0"]
            y_end = headings[i+1]["y0"] if i+1 < len(headings) else float('inf')
            chunk_blocks = [b for b in blocks if y_start <= b[1] < y_end]
            if not chunk_blocks:
                continue
            chunk_text = " ".join(b[4] for b in chunk_blocks).strip()
            lines = chunk_text.split('\n')
            filtered_lines = [line for line in lines if line.strip() and line.strip() not in hf_strings]
            cleaned_text = " ".join(filtered_lines).strip()
            if cleaned_text:
                chunks.append({
                    "text": cleaned_text,
                    "page": page_num + 1,
                    "section_title": clean_section_title(heading["text"])
                })

    doc.close()
    return chunks
