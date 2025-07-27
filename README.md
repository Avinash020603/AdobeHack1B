# Adobe India Hackathon - Round 1B

## 📌 Objective
Given a persona and job-to-be-done, this system ranks relevant sections of PDFs and provides refined summaries.

## 🔧 How to Build

```bash
docker build --platform linux/amd64 -t adobe1b .
```

## 🚀 How to Run

```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none adobe1b
```

## 📂 Directory Structure

- `/app/input` - Place PDFs here
- `/app/output` - Output JSONs will be saved here

## ✅ Features
- PDF chunk extraction
- Semantic ranking with SentenceTransformers
- Text summarization using TextRank
