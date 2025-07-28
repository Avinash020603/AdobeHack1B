# Adobe India Hackathon - Round 1B

1. Overview
This repository contains our general-purpose semantic extraction and summarization pipeline for Challenge 1B of the Adobe India Hackathon.
It processes any set of text-based PDF files to select, rank, and summarize the most relevant content according to a persona and job-to-be-done.

Domain-Agnostic: Works with any PDFs (travel, food, business, etc.).

Pretrained models used locally and fully offline.

Flexible input/output folder structure.

Dockerized for portability (CPU-only, Linux/amd64 compliant).

2. Our Approach
a.Dynamic PDF Chunk Extraction

->For each input PDF (from /input or as listed in a config JSON), extract meaningful text chunks using heading/font-based segmentation.

->Remove repeated headers and footers automatically via pattern analysis.

b.Semantic Embedding & Ranking

->Each chunk is converted into a dense vector using a sentence embedding model (e.g., BGE-micro or similar).

->All chunks are scored for relevance to the user-defined "job-to-be-done" via cosine similarity.

c.Balanced & Diverse Section Selection

->Top-ranked chunks are selected with a filter to maximize topical diversity and ensure representation from all input documents.

d.Summarization

->Selected chunks are condensed into concise actionable summaries using a locally hosted pretrained abstractive model, depending on disk constraints.

->The code is easily switched between models like FLAN-T5 (see summarizer module).

e.Output Formatting

->Results are saved in the specified output JSON structure, including metadata, extracted_sections, and subsection_analysis arrays.

3.Models and Libraries Used
a.PyMuPDF (fitz): For robust text extraction and heading detection from PDFs.

Transformers (HuggingFace):

For semantic embeddings and summarization:

bge-small-en

t5-base-finetuned-summarize-news 

Scikit-learn: For vector similarity (cosine) operations.

NumPy and Python standard libraries: Array operations, file management, JSON, etc.


4.How to Build & Run the Solution
Prerequisites
Docker installed (recommended) OR Python 3.8+ with pip for local runs.

All PDFs to process should be placed in input/ folder.

1. Place input files
Place your PDFs in the input/ directory (at project root).

Optionally, ensure a config JSON (e.g. challenge1b_input.json) is provided if used by your pipeline.

2. Build Docker image
   docker build --platform linux/amd64 -t adobe_1b_solution:latest .

3. Run the pipeline
   docker run --rm --network none \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  adobe_1b_solution:latest

Output JSON files will be written to the output/ directory.

The pipeline will automatically process all PDFs found in /app/input or as configured.

4.Configuration
Models are loaded from the models/ folder for fully offline execution.
No internet required at runtime. All dependencies are handled within the Docker image.
