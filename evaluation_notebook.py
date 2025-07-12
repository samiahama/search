# كود التقييم المحسن - يمكن نسخه إلى Jupyter Notebook
import json
import requests
import time

def precision_at_k(retrieved, relevant, k):
    """حساب الدقة عند k نتيجة"""
    retrieved_k = retrieved[:k]
    return len(set(retrieved_k) & set(relevant)) / max(len(retrieved_k), 1)

def recall_at_k(retrieved, relevant, k):
    """حساب الاسترجاع عند k نتيجة"""
    retrieved_k = retrieved[:k]
    return len(set(retrieved_k) & set(relevant)) / max(len(relevant), 1)

def average_precision(retrieved, relevant):
    """حساب متوسط الدقة"""
    hits = 0
    sum_precisions = 0
    for i, doc_id in enumerate(retrieved, 1):
        if doc_id in relevant:
            hits += 1
            sum_precisions += hits / i
    return sum_precisions / max(len(relevant), 1)

def evaluate_search_system(dataset_name, search_type="tfidf", k=10):
    """
    تقييم نظام البحث
    
    Args:
        dataset_name: اسم الداتاست ("miracl_ar" أو "msmarco")
        search_type: نوع البحث ("tfidf", "embedding", "hybrid")
        k: عدد النتائج المراد تقييمها
    """
    
    # تحميل الاستعلامات المناسبة للـ dataset
    query_file = f"data/queries_{dataset_name}.json"
    try:
        with open(query_file, encoding='utf-8') as f:
            ground_truth = json.load(f)
        print(f"✅ تم تحميل {len(ground_truth)} استعلام من {query_file}")
    except FileNotFoundError:
        print(f"❌ لم يتم العثور على ملف {query_file}")
        return
    
    # جلب نتائج البحث من الخادم
    results = {}
    print(f"🔄 جاري جلب النتائج من الخادم...")
    
    for i, item in enumerate(ground_truth):
        query = item["query"]
        print(f"  البحث {i+1}/{len(ground_truth)}: {query}")
        
        params = {
            "query": query,
            "type": search_type,
            "dataset": dataset_name
        }
        
        try:
            response = requests.get("http://localhost:5000/api/search", params=params)
            docs = response.json()
            results[query] = [doc["doc_id"] for doc in docs]
            time.sleep(0.1)  # تأخير بسيط لتجنب إرهاق الخادم
        except Exception as e:
            print(f"  ❌ خطأ في البحث: {e}")
            results[query] = []
    
    # حساب معايير التقييم
    precisions = []
    recalls = []
    aps = []
    
    print(f"\n📊 حساب معايير التقييم...")
    
    for item in ground_truth:
        query = item["query"]
        relevant = item["relevant_docs"]
        retrieved = results.get(query, [])
        
        prec = precision_at_k(retrieved, relevant, k)
        rec = recall_at_k(retrieved, relevant, k)
        ap = average_precision(retrieved, relevant)
        
        precisions.append(prec)
        recalls.append(rec)
        aps.append(ap)
        
        print(f"  {query}:")
        print(f"    Precision@{k}: {prec:.4f}")
        print(f"    Recall@{k}: {rec:.4f}")
        print(f"    AP: {ap:.4f}")
    
    # حساب المتوسطات
    avg_precision = sum(precisions) / len(precisions)
    avg_recall = sum(recalls) / len(recalls)
    map_score = sum(aps) / len(aps)
    
    # عرض النتائج النهائية
    print(f"\n" + "="*50)
    print(f"📈 نتائج التقييم النهائية")
    print(f"="*50)
    print(f"Dataset: {dataset_name}")
    print(f"Search Type: {search_type}")
    print(f"Number of Queries: {len(ground_truth)}")
    print(f"k: {k}")
    print(f"-"*50)
    print(f"متوسط الدقة (Precision@{k}): {avg_precision:.4f}")
    print(f"متوسط الاسترجاع (Recall@{k}): {avg_recall:.4f}")
    print(f"متوسط متوسط الدقة (MAP): {map_score:.4f}")
    print(f"="*50)
    
    return {
        "precision": avg_precision,
        "recall": avg_recall,
        "map": map_score,
        "results": results
    }

# مثال على الاستخدام:
# تقييم النظام على MIRACL Arabic مع TF-IDF
print("🔍 تقييم نظام البحث")
print("="*50)

# يمكنك تغيير هذه المعاملات حسب ما تريد
dataset = "miracl_ar"  # أو "msmarco"
search_type = "tfidf"  # أو "embedding" أو "hybrid"
k = 10

results = evaluate_search_system(dataset, search_type, k) 