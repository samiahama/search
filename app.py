from flask import Flask, request, jsonify
import json
import numpy as np
import math
from sentence_transformers import SentenceTransformer
from collections import Counter, defaultdict
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

# متغيرات عامة لتخزين الفهرسة المعكوسة وعدد الوثائق
inverted_index = {}
total_documents = 0
idf_cache = {}

def load_data(dataset):
    """تحميل البيانات وإنشاء الفهرسة المعكوسة"""
    global inverted_index, total_documents, idf_cache
    
    files = DATASETS[dataset]
    with open(files["processed"], encoding="utf-8") as f:
        text_data = json.load(f)
    with open(files["tfidf"], encoding="utf-8") as f:
        tfidf_data = json.load(f)
    with open(files["embeddings"], encoding="utf-8") as f:
        embeddings = json.load(f)
    
    # إنشاء الفهرسة المعكوسة
    inverted_index = defaultdict(set)
    total_documents = len(text_data)
    
    for doc in text_data:
        doc_id = doc["doc_id"]
        words = set(doc["text"].lower().split())
        for word in words:
            inverted_index[word].add(doc_id)
    
    # حساب IDF لكل كلمة
    for word in inverted_index:
        docs_with_word = len(inverted_index[word])
        idf_cache[word] = math.log(total_documents / (docs_with_word + 1))
    
    print(f"[DEBUG] Built inverted index with {len(inverted_index)} unique words")
    return text_data, tfidf_data, embeddings

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def cosine_similarity(vec1, vec2):
    """حساب التشابه باستخدام جيب التمام للمتجهات"""
    keys = set(vec1) | set(vec2)
    a = np.array([vec1.get(k, 0) for k in keys])
    b = np.array([vec2.get(k, 0) for k in keys])
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def cosine_similarity_vec(a, b):
    """حساب التشابه باستخدام جيب التمام للمتجهات العددية"""
    a = np.array(a)
    b = np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def calculate_query_tfidf(query):
    """
    حساب TF-IDF الحقيقي للاستعلام
    TF: عدد مرات ظهور الكلمة في الاستعلام
    IDF: log(إجمالي عدد الوثائق / عدد الوثائق التي تحتوي على الكلمة)
    """
    query_words = query.strip().lower().split()
    query_tfidf = {}
    
    for word in query_words:
        # حساب TF (Term Frequency) - عدد مرات ظهور الكلمة في الاستعلام
        tf = query_words.count(word)
        
        # حساب IDF (Inverse Document Frequency) - من الفهرسة المعكوسة
        if word in idf_cache:
            idf = idf_cache[word]
        else:
            # إذا لم توجد الكلمة في الفهرسة، استخدم IDF = 0
            idf = 0
        
        # TF-IDF = TF × IDF
        query_tfidf[word] = tf * idf
    
    return query_tfidf

@app.route('/api/search')
def search():
    query = request.args.get('query', '')
    dataset = request.args.get('dataset', 'miracl_ar')
    search_type = request.args.get('type', 'tfidf')
    
    # تحميل البيانات وإنشاء الفهرسة المعكوسة
    text_data, tfidf_data, embeddings = load_data(dataset)
    print(f"[DEBUG] Loaded {len(text_data)} docs for dataset {dataset}")
    
    docid_to_text = {doc["doc_id"]: doc["text"] for doc in text_data}
    docid_to_tfidf = {doc["doc_id"]: doc["tfidf"] for doc in tfidf_data}
    docid_to_emb = {doc["doc_id"]: doc["embedding"] for doc in embeddings}

    # حساب TF-IDF الحقيقي للاستعلام
    query_tfidf = calculate_query_tfidf(query)
    query_words = set(query.strip().lower().split())
    print(f"[DEBUG] Query: {query} | Query words: {query_words}")
    print(f"[DEBUG] Query TF-IDF: {query_tfidf}")

    results = []
    if search_type == "tfidf":
        # البحث باستخدام TF-IDF الحقيقي
        for doc_id, doc_tfidf in docid_to_tfidf.items():
            score = cosine_similarity(query_tfidf, doc_tfidf)
            doc_text = docid_to_text.get(doc_id, "")
            doc_words = set(doc_text.strip().lower().split())
            if score > 0.01 or query_words & doc_words:
                results.append({
                    "doc_id": doc_id,
                    "score": score,
                    "text": doc_text
                })
    elif search_type == "embedding":
        # البحث باستخدام Embeddings
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
        # البحث الهجين: دمج TF-IDF و Embeddings
        query_emb = model.encode(query).tolist()
        for doc_id in docid_to_text:
            tfidf_score = cosine_similarity(query_tfidf, docid_to_tfidf.get(doc_id, {}))
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
    """اقتراح الكلمات الأكثر شيوعًا"""
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