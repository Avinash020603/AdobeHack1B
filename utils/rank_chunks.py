import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_bge_model(path="./models/bge-small-en"):
    tok = AutoTokenizer.from_pretrained(path)
    mdl = AutoModel.from_pretrained(path).eval()
    return tok, mdl

def calc_score(query, text, model, tokenizer):
    qi = tokenizer(query, return_tensors="pt", truncation=True,
                   padding=True, max_length=512)
    ti = tokenizer(text, return_tensors="pt", truncation=True,
                   padding=True, max_length=512)
    with torch.no_grad():
        qv = model(**qi).last_hidden_state.mean(1)
        tv = model(**ti).last_hidden_state.mean(1)
    qn = torch.nn.functional.normalize(qv, p=2, dim=1).cpu().numpy()[0]
    tn = torch.nn.functional.normalize(tv, p=2, dim=1).cpu().numpy()[0]
    sem = float(np.dot(qn, tn))
    try:
        v = TfidfVectorizer(stop_words="english", max_features=500)
        m = v.fit_transform([query, text])
        tf = float(cosine_similarity(m[0:1], m[1:2])[0][0])
    except:
        tf = 0.0
    qc, tc = set(query.lower().split()), set(text.lower().split())
    cov = len(qc & tc) / max(len(qc), 1)
    return 0.6*sem + 0.3*tf + 0.1*cov

def normalize_strict_ranks(chunks):
    
    top5 = sorted(chunks, key=lambda x: x["score"], reverse=True)[:5]
    for i, c in enumerate(top5, 1):
        c["importance_rank"] = i
    return chunks

def rank_chunks(query, chunks, model, tokenizer):
    for c in chunks:
        c["score"] = calc_score(query, c["text"], model, tokenizer)
    sorted_chunks = sorted(chunks, key=lambda x: x["score"], reverse=True)
    return normalize_strict_ranks(sorted_chunks)
