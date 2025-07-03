import json
import argparse
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix

parser = argparse.ArgumentParser(description="Build TF-IDF for a dataset.")
parser.add_argument('--input', required=True, help='Path to processed.json')
parser.add_argument('--output', required=True, help='Path to output tfidf.json')
args = parser.parse_args()

with open(args.input, encoding="utf-8") as f:
    docs = json.load(f)
texts = [doc["text"] for doc in docs]
doc_ids = [doc["doc_id"] for doc in docs]

vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
tfidf_matrix = vectorizer.fit_transform(texts)
tfidf_matrix = csr_matrix(tfidf_matrix)  # Ensure correct type for linter/runtime
terms = vectorizer.get_feature_names_out()

tfidf_data = []
for i, doc_id in enumerate(doc_ids):
    row = tfidf_matrix.getrow(i)
    tfidf_vec = {terms[j]: float(row[0, j]) for j in row.nonzero()[1]}
    tfidf_data.append({"doc_id": doc_id, "tfidf": tfidf_vec})

with open(args.output, "w", encoding="utf-8") as f:
    json.dump(tfidf_data, f, ensure_ascii=False, indent=2)

print(f"تم بناء ملف {args.output} بنجاح!")