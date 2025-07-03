# Information Retrieval System (محرك بحث نصي متعدد اللغات)

نظام استرجاع معلومات متكامل يدعم البحث في مجموعات بيانات ضخمة (مثل MIRACL Arabic وMSMARCO English) باستخدام نماذج TF-IDF وEmbeddings، مع واجهة ويب عصرية تشبه Google Search.

---

## 💡 **المزايا الرئيسية**

- بحث نصي سريع وذكي (TF-IDF، Embedding، Hybrid)
- دعم العربية والإنجليزية
- واجهة React عصرية مع دعم RTL
- اختيار مجموعة البيانات من الواجهة
- عرض النتائج بشكل بطاقات مع زر "قراءة المزيد"
- تصميم شبيه بمحرك Google

---

## 🛠 **المتطلبات**

- Python 3.8+
- Node.js 16+
- npm

### مكتبات بايثون:

```bash
pip install flask flask-cors numpy scikit-learn sentence-transformers
```

### مكتبات React:

```bash
cd client
npm install
npm install react-icons
```

---

## 🚀 **خطوات التحميل والتشغيل**

### 1. تحميل المشروع من GitHub

```bash
git clone <رابط_المستودع>
cd search
```

### 2. تجهيز البيانات (ضع ملفات البيانات في مجلد data كما هو موضح)

### 3. بناء تمثيلات TF-IDF وEmbeddings

```bash
python build_tfidf.py --input data/miracl_ar_processed.json --output data/miracl_ar_tfidf.json
python build_tfidf.py --input data/msmarco_processed.json --output data/msmarco_tfidf.json

python build_embed.py --input data/miracl_ar_processed.json --output data/miracl_ar_embeddings.json
python build_embed.py --input data/msmarco_processed.json --output data/msmarco_embeddings.json
```

### 4. تشغيل خادم البحث (Flask)

```bash
python app.py
```

### 5. تشغيل الواجهة الأمامية (React)

```bash
cd client
npm start
```

---

## 🖥 **طريقة الاستخدام**

- افتح المتصفح على: [http://localhost:3000](http://localhost:3000)
- اختر مجموعة البيانات (MIRACL Arabic أو MSMARCO)
- اكتب استعلامك واضغط زر البحث (أو Enter)
- ستظهر النتائج في بطاقات أنيقة مع إمكانية قراءة المزيد

---

## ⚙️ **ملاحظات التطوير والتخصيص**

- يمكنك إضافة مجموعات بيانات جديدة بتعديل ملفات data وبناء التمثيلات لها.
- يمكن تعديل منطق البحث أو تحسين التطبيع/الفلترة من خلال كود Flask.
- الواجهة قابلة للتخصيص بالكامل عبر React/JSX وCSS.

---

## 📂 **هيكلية المشروع**

- `app.py` : خادم Flask (API)
- `build_tfidf.py` : بناء تمثيل TF-IDF
- `build_embed.py` : بناء Embeddings
- `client/` : واجهة React
- `data/` : ملفات البيانات

---

## 📞 **الدعم والمساهمة**

لأي استفسار أو مساهمة، يمكنك فتح Issue أو Pull Request على GitHub.
