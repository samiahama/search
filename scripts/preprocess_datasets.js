const fs = require("fs");

// دالة تنظيف النصوص (lowercase، إزالة الرموز، التشكيل، إلخ)
function cleanText(text) {
  if (!text) return "";
  // إزالة التشكيل العربي
  let cleaned = text.replace(/[\u064B-\u0652]/g, "");
  // إزالة الرموز غير الحروف والأرقام
  cleaned = cleaned.replace(/[^\p{L}\p{N}\s]/gu, "");
  // تحويل إلى lowercase
  cleaned = cleaned.toLowerCase();
  // إزالة المسافات الزائدة
  cleaned = cleaned.replace(/\s+/g, " ").trim();
  return cleaned;
}

function preprocessFile(inputPath, outputPath, textField) {
  const raw = fs.readFileSync(inputPath, "utf-8");
  const data = JSON.parse(raw);
  const processed = data.map((doc) => ({
    doc_id: doc.doc_id,
    text: cleanText(doc[textField]),
  }));
  fs.writeFileSync(outputPath, JSON.stringify(processed, null, 2), "utf-8");
  console.log(`تمت معالجة ${inputPath} → ${outputPath}`);
}

// معالجة MSMARCO (body)
preprocessFile(
  "data/msmarco_sample.json",
  "data/msmarco_processed.json",
  "text"
);
// معالجة MIRACL Arabic (text)
preprocessFile(
  "data/miracl_ar_sample.json",
  "data/miracl_ar_processed.json",
  "text"
);
