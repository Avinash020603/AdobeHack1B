# Adobe India Hackathon – Round 1B Solution

## Overview

This repository provides a **general-purpose, semantic extraction and summarization pipeline** for Challenge 1B of the Adobe India Hackathon.

- **Domain-agnostic:** Processes any PDF (travel, food, business, etc.)
- **Works fully offline with locally-stored pretrained models**
- **Input/output folder-based structure**
- **Portable, Dockerized (CPU-only, Linux/amd64)**

---

## Our Approach

### 1. Dynamic PDF Chunk Extraction
- Extracts meaningful text chunks from any PDF using adaptive heading/font-based segmentation.
- Removes repeated headers/footers via pattern analysis—no hardcoded PDF logic.

### 2. Semantic Embedding & Ranking
- Embeds each chunk as dense vectors with a sentence embedding model (BGE-micro or similar).
- Ranks chunks for relevance to a “job-to-be-done” via cosine similarity to the semantic query.

### 3. Balanced & Diverse Section Selection
- Selects top-ranked chunks from all PDFs, ensuring topical diversity and balanced document representation.

### 4. Summarization
- Chosen chunks are condensed into actionable, readable summaries using an offline abstractive model (e.g., FLAN-T5, DistilBART, T5, or PEGASUS).
- Summarization module is easily swappable according to size/performance needs.

### 5. Structured Output
- Saves output in JSON format: `{ "metadata", "extracted_sections", "subsection_analysis" }`.

---

## Models and Libraries Used

- **PyMuPDF (fitz):** For fast, robust PDF text and heading extraction.
- **Transformers (HuggingFace):**
  - *Embeddings:* e.g., `bge-small-en`
  - *Summarization:* `t5-base-finetuned-summarize-news`, `sshleifer/distilbart-cnn-12-6`, `google/flan-t5-small`, etc.
- **Scikit-learn:** For cosine similarity and chunk ranking.
- **NumPy, Sumy (TextRank):** Extractive scoring.
- **All dependencies local (no internet needed at runtime)**

---

## How to Build & Run

### Prerequisites

- **Docker** (recommended), or Python 3.8+ with `pip`
- Place input PDFs in the `input/` folder (project root)
- Models should be downloaded and saved in the `models/` folder

### Steps

1. **Place Input Files**
   - Copy your PDFs to the `input/` directory.

2. **Build the Docker Image**

docker build --platform linux/amd64 -t adobe_1b_solution:latest .

3. **Run the Pipeline**

docker run --rm --network none
-v $(pwd)/input:/app/input
-v $(pwd)/output:/app/output
adobe_1b_solution:latest

- Output will be found in the `output/` folder.

---

## File & Folder Structure

project_root/
├── main.py
├── input/ # Place all your PDFs here
├── output/ # Output JSONs generated here
├── models/ # All local huggingface model folders
├── utils/ # Summarization, chunking, utils scripts
├── requirements.txt
├── Dockerfile
└── README.md



---

## Configuration

- All models are loaded from the `models/` folder; **offline execution only**.
- No internet required at runtime; all dependencies are bundled in the Docker image.

---

## Troubleshooting

- **Missing PDFs:** The pipeline will warn and skip any filenames not present in `input/`.
- **Model loading errors:** Ensure proper model folders exist in `models/`.
- **Docker build too large/slow?** Add a `.dockerignore` to filter big files/directories you don’t need inside the image.

---
