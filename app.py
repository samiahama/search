from flask import Flask, request, jsonify
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from collections import Counter
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# تحميل البيانات
DATASETS = {
    "miracl_ar": {
        "processed": "data/miracl_ar_processed.json",
        "tfidf": "data/miracl_ar_tfidf.json",
        "embeddings": "data/miracl_ar_embeddings.json"
    },
    "msmarco": {
        "processed": "data/msmarco_processed.json",
        "tfidf": "data/msmarco_tfidf.json",
        "embeddings": "data/msmarco_embeddings.json"
    }
}

def load_data(dataset):
    files = DATASETS[dataset]
    with open(files["processed"], encoding="utf-8") as f:
        text_data = json.load(f)
    with open(files["tfidf"], encoding="utf-8") as f:
        tfidf_data = json.load(f)
    with open(files["embeddings"], encoding="utf-8") as f:
        embeddings = json.load(f)
    return text_data, tfidf_data, embeddings

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def cosine_similarity(vec1, vec2):
    keys = set(vec1) | set(vec2)
    a = np.array([vec1.get(k, 0) for k in keys])
    b = np.array([vec2.get(k, 0) for k in keys])
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def cosine_similarity_vec(a, b):
    a = np.array(a)
    b = np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def text_to_tfidf(text):
    words = text.strip().lower().split()
    return dict(Counter(words))

@app.route('/api/search')
def search():
    query = request.args.get('query', '')
    dataset = request.args.get('dataset', 'miracl_ar')
    search_type = request.args.get('type', 'tfidf')
    text_data, tfidf_data, embeddings = load_data(dataset)
    print(f"[DEBUG] Loaded {len(text_data)} docs for dataset {dataset}")
    docid_to_text = {doc["doc_id"]: doc["text"] for doc in text_data}
    docid_to_tfidf = {doc["doc_id"]: doc["tfidf"] for doc in tfidf_data}
    docid_to_emb = {doc["doc_id"]: doc["embedding"] for doc in embeddings}

    # تمثيل الاستعلام كـ bag-of-words
    query_vec = text_to_tfidf(query)
    query_words = set(query.strip().lower().split())
    print(f"[DEBUG] Query: {query} | Query words: {query_words}")

    results = []
    if search_type == "tfidf":
        for doc_id, tfidf in docid_to_tfidf.items():
            score = cosine_similarity(query_vec, tfidf)
            doc_text = docid_to_text.get(doc_id, "")
            doc_words = set(doc_text.strip().lower().split())
            if score > 0.01 or query_words & doc_words:
                results.append({
                    "doc_id": doc_id,
                    "score": score,
                    "text": doc_text
                })
    elif search_type == "embedding":
        query_emb = model.encode(query).tolist()
        for doc_id, emb in docid_to_emb.items():
            score = cosine_similarity_vec(query_emb, emb)
            doc_text = docid_to_text.get(doc_id, "")
            if score > 0.1 or any(word in doc_text for word in query_words):
                results.append({
                    "doc_id": doc_id,
                    "score": score,
                    "text": doc_text
                })
    elif search_type == "hybrid":
        query_emb = model.encode(query).tolist()
        for doc_id in docid_to_text:
            tfidf_score = cosine_similarity(query_vec, docid_to_tfidf.get(doc_id, {}))
            emb_score = cosine_similarity_vec(query_emb, docid_to_emb.get(doc_id, []))
            score = 0.5 * tfidf_score + 0.5 * emb_score
            doc_text = docid_to_text.get(doc_id, "")
            if score > 0.05 or any(word in doc_text for word in query_words):
                results.append({
                    "doc_id": doc_id,
                    "score": score,
                    "text": doc_text
                })
    print(f"[DEBUG] Results found: {len(results)}")
    results = sorted(results, key=lambda x: x["score"], reverse=True)[:10]
    if not results:
        print("[DEBUG] No results found, returning empty list []")
        return jsonify([])
    return jsonify(results)

@app.route('/api/suggestions')
def suggestions():
    dataset = request.args.get('dataset', 'miracl_ar')
    with open(DATASETS[dataset]["processed"], encoding="utf-8") as f:
        text_data = json.load(f)
    freq = {}
    for doc in text_data:
        for word in doc["text"].split():
            if len(word) > 2:
                freq[word] = freq.get(word, 0) + 1
    top = sorted(freq, key=lambda w: freq[w], reverse=True)[:100]
    return jsonify(top)

if __name__ == '__main__':
    app.run(port=5000) 