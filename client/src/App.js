import React, { useState, useEffect } from "react";
import { FaSearch } from "react-icons/fa";

const DATASETS = [
  { value: "miracl_ar", label: "MIRACL Arabic" },
  { value: "msmarco", label: "MSMARCO" },
];

function smartRepType(query) {
  return "tfidf";
}

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dataset, setDataset] = useState("miracl_ar");
  const [expanded, setExpanded] = useState({});

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError("");
    setResults([]);
    const repType = smartRepType(query);
    try {
      const res = await fetch(
        `http://localhost:5000/api/search?query=${encodeURIComponent(
          query
        )}&type=${repType}&dataset=${dataset}`
      );
      if (!res.ok) throw new Error("فشل الاتصال بالسيرفر");
      const data = await res.json();
      setResults(data);
    } catch (err) {
      setError("حدث خطأ أثناء البحث");
    } finally {
      setLoading(false);
    }
  };

  const handleExpand = (docId) => {
    setExpanded((prev) => ({ ...prev, [docId]: !prev[docId] }));
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #e3f0ff 0%, #f8fafc 100%)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "flex-start",
      }}
    >
      <div
        style={{
          marginTop: 100,
          width: "100%",
          maxWidth: 600,
          textAlign: "center",
        }}
      >
        <h1
          style={{
            fontFamily: "Product Sans, Arial",
            fontWeight: 700,
            fontSize: 38,
            color: "#4285f4",
            marginBottom: 30,
            letterSpacing: -2,
            textShadow: "0 2px 8px #e3f0ff",
          }}
        >
          نظام استرجاع المعلومات
        </h1>
        <form
          onSubmit={handleSearch}
          style={{
            position: "relative",
            marginBottom: 18,
            display: "flex",
            justifyContent: "center",
          }}
          autoComplete="off"
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              background: "#fff",
              borderRadius: 32,
              boxShadow: "0 2px 16px rgba(66,133,244,0.08)",
              border: "1.5px solid #e3eafc",
              width: "100%",
              maxWidth: 520,
              padding: "4px 12px 4px 4px",
              margin: "0 auto",
              flexDirection: "row-reverse",
            }}
          >
            <input
              id="search-input"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="ابحث في الوثائق..."
              style={{
                width: "100%",
                padding: "14px 18px 14px 44px",
                fontSize: 20,
                borderRadius: 32,
                border: "none",
                outline: "none",
                direction: "rtl",
                background: "#fff",
                boxShadow: "none",
                color: "#222",
                fontFamily: "inherit",
              }}
              autoFocus
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              type="submit"
              style={{
                background: "#e3f0ff",
                color: "#4285f4",
                border: "none",
                borderRadius: "50%",
                width: 40,
                height: 40,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 20,
                marginLeft: -44,
                marginRight: 8,
                boxShadow: loading ? "0 0 0 2px #bcdcff" : "none",
                cursor: loading ? "not-allowed" : "pointer",
                transition: "background 0.2s, box-shadow 0.2s",
                position: "relative",
                zIndex: 2,
              }}
            >
              <FaSearch />
            </button>
          </div>
        </form>
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            marginBottom: 30,
          }}
        >
          <select
            value={dataset}
            onChange={(e) => setDataset(e.target.value)}
            style={{
              fontSize: 17,
              padding: "10px 28px",
              borderRadius: 20,
              border: "1.5px solid #e3eafc",
              background: "#f8fafc",
              color: "#4285f4",
              fontWeight: 600,
              boxShadow: "0 1px 4px #e3f0ff",
              margin: "0 auto",
              outline: "none",
              minWidth: 180,
              textAlign: "center",
            }}
          >
            {DATASETS.map((d) => (
              <option key={d.value} value={d.value}>
                {d.label}
              </option>
            ))}
          </select>
        </div>
        {error && (
          <div style={{ color: "#e53935", marginBottom: 10, fontWeight: 600 }}>
            {error}
          </div>
        )}
      </div>
      <div
        style={{
          width: "100%",
          maxWidth: 700,
          margin: "0 auto",
          marginBottom: 40,
        }}
      >
        {results.length > 0 && (
          <div style={{ marginTop: 10 }}>
            {results.map((r, i) => {
              const isExpanded = expanded[r.doc_id];
              const lines = r.text.split("\n").join(" ").split(" ");
              const previewText =
                lines.slice(0, 30).join(" ") +
                (lines.length > 30 ? " ..." : "");
              return (
                <div
                  key={r.doc_id}
                  style={{
                    background: "#fff",
                    borderRadius: 18,
                    boxShadow: "0 2px 12px rgba(66,133,244,0.10)",
                    padding: 28,
                    marginBottom: 26,
                    textAlign: "right",
                    borderRight: "4px solid #4285f4",
                    direction: "rtl",
                    position: "relative",
                    minHeight: 90,
                    maxWidth: 650,
                    transition: "box-shadow 0.2s",
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      fontSize: 15,
                      color: "#7baaf7",
                      marginBottom: 6,
                      fontWeight: 600,
                    }}
                  >
                    معرّف الوثيقة: {r.doc_id}
                  </div>
                  <div
                    style={{
                      fontSize: 20,
                      color: "#222",
                      marginBottom: 8,
                      lineHeight: 1.7,
                      maxHeight: isExpanded ? "none" : 3 * 1.7 * 20 + "px", // 3 أسطر فقط
                      overflow: isExpanded ? "visible" : "hidden",
                      textOverflow: "ellipsis",
                      display: "-webkit-box",
                      WebkitLineClamp: isExpanded ? "none" : 3,
                      WebkitBoxOrient: "vertical",
                      whiteSpace: isExpanded ? "normal" : "pre-line",
                    }}
                  >
                    {isExpanded ? r.text : previewText}
                  </div>
                  <div
                    style={{
                      position: "absolute",
                      left: 24,
                      top: 24,
                      color: "#4285f4",
                      fontWeight: 700,
                      fontSize: 18,
                    }}
                  >
                    {(r.score || 0).toFixed(4)}
                  </div>
                  {r.text.split(" ").length > 30 && (
                    <button
                      onClick={() => handleExpand(r.doc_id)}
                      style={{
                        background: isExpanded ? "#e3eafc" : "#f1f3f4",
                        color: "#4285f4",
                        border: "none",
                        borderRadius: 12,
                        padding: "6px 18px",
                        fontSize: 15,
                        fontWeight: 600,
                        cursor: "pointer",
                        marginTop: 8,
                        float: "left",
                        boxShadow: "0 1px 4px #e3f0ff",
                      }}
                    >
                      {isExpanded ? "إخفاء" : "قراءة المزيد"}
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
