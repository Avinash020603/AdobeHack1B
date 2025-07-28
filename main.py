import os
import json
import time
import numpy as np
import torch
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity

from utils.extract_chunks import extract_chunks_with_outline
from utils.rank_chunks import load_bge_model, calc_score
from utils.extractive import textrank_extract
from utils.summarize import summarize_text
from utils.output_format import save_output_json
from utils.text_utils import clean_repetitive_prefix

INPUT_DIR ="input"
OUTPUT_DIR ="output"
INPUT_FILE ="challenge1b_input.json"
OUTPUT_FILE ="challenge1b_output.json"

DIM = 384
MAX_SELECTED = 5

def load_input(path):
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    persona = cfg.get("persona", {}).get("role", "Travel Planner")
    job = cfg.get("job_to_be_done", {}).get("task", "")
    pdfs = [d["filename"] for d in cfg.get("documents", [])]
    return persona, job, pdfs

def is_diverse(candidate_text, seen_texts, threshold=0.85):
    for t in seen_texts:
        overlap = len(set(candidate_text.lower().split()) & set(t.lower().split())) / max(len(set(candidate_text.split())), 1)
        if overlap > threshold:
            return False
    return True

def main():
    start_time = time.perf_counter()
    persona, job, pdfs = load_input(os.path.join(INPUT_DIR, INPUT_FILE))

    print(f"Persona: {persona}")
    print(f"Job: {job}")
    print(f"Processing {len(pdfs)} PDFs\n")

    query = (
        "You are a travel planner organizing a 4-day trip for 10 college friends. "
        "The trip should focus on fun, culture, local cuisine, and budget-friendly activities. "
        f"{job}"
    )

    bge_tok, bge_mdl = load_bge_model()
    print("Extracting chunks and embedding...")

    all_chunks = []
    embeddings = []
    metadata = []

    for pdf in pdfs:
        pdf_path = os.path.join(INPUT_DIR, pdf)
        chunks = extract_chunks_with_outline(pdf_path)
        for c in chunks:
            c["document"] = pdf
        all_chunks.extend(chunks)

    for c in all_chunks:
        inputs = bge_tok(
            c["text"],
            return_tensors="pt",
            truncation=True,
            padding="longest",
            max_length=512,
        )
        with torch.no_grad():
            out = bge_mdl(**inputs)
            vec = out.last_hidden_state.mean(dim=1).squeeze(0).cpu().numpy().astype("float32")
        embeddings.append(vec)
        metadata.append({
            "document": c["document"],
            "page": c["page"],
            "section_title": c["section_title"],
            "text": c["text"]
        })

    embeddings_np = np.vstack(embeddings)
    assert embeddings_np.shape[1] == DIM

    q_inputs = bge_tok(
        query,
        return_tensors="pt",
        truncation=True,
        padding="longest",
        max_length=512,
    )
    with torch.no_grad():
        q_out = bge_mdl(**q_inputs)
        q_vec = q_out.last_hidden_state.mean(dim=1).cpu().numpy().astype("float32")

    print("Computing cosine similarity to query")
    sim_scores = cosine_similarity(q_vec, embeddings_np)[0]

    candidates = []
    for idx, score in enumerate(sim_scores):
        m = metadata[idx]
        candidates.append({**m, "score": float(score)})

    
    for c in candidates:
        c["score"] = calc_score(query, c["text"], bge_mdl, bge_tok)

    candidates.sort(key=lambda x: x["score"], reverse=True)

    scores = [c["score"] for c in candidates]
    if scores:
        t80, t60, t40, t20 = np.percentile(scores, [80, 60, 40, 20])
        for c in candidates:
            s = c["score"]
            c["importance_rank"] = (
                1 if s >= t80 else 2 if s >= t60 else 3 if s >= t40 else 4 if s >= t20 else 5
            )
    else:
        for c in candidates:
            c["importance_rank"] = 5

    candidates_by_pdf = defaultdict(list)
    for c in candidates:
        candidates_by_pdf[c["document"]].append(c)

    selected = []
    seen_texts = []

   
    for pdf in pdfs:
        pdf_chunks = candidates_by_pdf.get(pdf, [])
        if pdf_chunks:
            top_chunk = max(pdf_chunks, key=lambda x: x["score"])
            if is_diverse(top_chunk["text"], seen_texts):
                selected.append(top_chunk)
                seen_texts.append(top_chunk["text"])

    
    for c in candidates:
        if len(selected) >= MAX_SELECTED:
            break
        if c in selected:
            continue
        if is_diverse(c["text"], seen_texts):
            selected.append(c)
            seen_texts.append(c["text"])

    print(f"Selected {len(selected)} diverse chunks for summarization.")

    print("Summarizing chunks...")
    results = []

    for c in selected:
        excerpt = textrank_extract(c["text"], num_sentences=6)
        raw_summary = summarize_text(excerpt, max_len=150)
        clean_summary = clean_repetitive_prefix(raw_summary)
        results.append({
            "document": c["document"],
            "section_title": c["section_title"],
            "page_number": c["page"],
            "importance_rank": c["importance_rank"],
            "refined_text": clean_summary
        })
        print(f"Summarized chunk from {c['document']} | Section: {c['section_title']} → Rank {c['importance_rank']}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    elapsed = time.perf_counter() - start_time

    save_output_json(
        results,
        os.path.join(OUTPUT_DIR, OUTPUT_FILE),
        persona, job, pdfs,
        exec_time=elapsed
    )

    print(f"\nPipeline completed in {elapsed:.2f} seconds. Output saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
