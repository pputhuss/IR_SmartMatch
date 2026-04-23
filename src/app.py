from flask import Flask, request, jsonify
from flask_cors import CORS
from matcher import rank_companies
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)

def load_companies():
    path = Path(__file__).parent.parent / "data" / "companies.json"
    with open(path) as f:
        return json.load(f)

def extract_pdf_text(file_bytes):
    try:
        import fitz  # pymupdf
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        return " ".join(page.get_text() for page in doc).strip()
    except Exception as e:
        return None

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    text = extract_pdf_text(file.read())
    if not text or len(text) < 50:
        return jsonify({"error": "Could not extract text from PDF"}), 400
    return jsonify({"text": text})

@app.route("/match", methods=["POST"])
def match():
    data = request.get_json()
    resume_text = data.get("resume_text", "").strip()

    if not resume_text or len(resume_text) < 50:
        return jsonify({"error": "Resume text too short"}), 400

    companies = load_companies()

    # ── Filter by major if one was specified ──
    major = data.get("major", "all")
    if major and major != "all":
        filtered = [c for c in companies if c.get("major", "").lower() == major.lower()]
        # Fall back to all companies if the filter returns nothing
        if filtered:
            companies = filtered

    company_lookup = {c["company"]: c for c in companies}
    ranked = rank_companies(resume_text, companies)

    top_n = data.get("top_n", 5)
    results = []
    for name, score in ranked[:top_n]:
        c = company_lookup.get(name, {})
        results.append({
            "company": name,
            "score": round(score, 4),
            "description": c.get("description", ""),
            "tags": c.get("tags", []),
            "major": c.get("major", ""),
        })

    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(debug=True, port=5000)