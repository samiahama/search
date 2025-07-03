import json
import argparse
from sentence_transformers import SentenceTransformer

parser = argparse.ArgumentParser(description="Build Embeddings for a dataset.")
parser.add_argument('--input', required=True, help='Path to processed.json')
parser.add_argument('--output', required=True, help='Path to output embeddings.json')
args = parser.parse_args()

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

with open(args.input, encoding="utf-8") as f:
    docs = json.load(f)

embeddings = []
for doc in docs:
    emb = model.encode(doc["text"]).tolist()
    embeddings.append({"doc_id": doc["doc_id"], "embedding": emb})

with open(args.output, "w", encoding="utf-8") as f:
    json.dump(embeddings, f, ensure_ascii=False)

print(f"تم بناء ملف {args.output} بنجاح!") 