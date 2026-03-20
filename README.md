# AI Resume Analyzer
### 100% Free · No API Key · Runs Locally · Open Source

Analyze your resume against any job description using **TF-IDF cosine
similarity** and **NLP keyword extraction** — no internet required after
first install.

---

## 📁 Project Structure

```
ai_resume_analyzer/
│
├── app.py            ← Streamlit web UI  (recommended)
├── analyzer.py       ← Core analysis logic  (pure Python)
├── cli.py            ← Terminal/command-line version
├── requirements.txt  ← All dependencies
└── README.md         ← This file
```

---

## ⚡ Quick Start (5 steps)

### 1 — Make sure Python 3.8+ is installed
```bash
python --version    # should print Python 3.8 or higher
```
If not, download from https://www.python.org/downloads/

---

### 2 — Create a virtual environment (recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

---

### 3 — Install dependencies
```bash
pip install -r requirements.txt
```
This installs:
| Package | Purpose |
|---------|---------|
| `pdfplumber` | Extract text from PDF files |
| `scikit-learn` | TF-IDF vectorizer + cosine similarity |
| `nltk` | Tokenization, stopwords, lemmatization |
| `streamlit` | Browser-based UI |
| `pandas` | Data handling utilities |

---

### 4a — Run the Streamlit Web UI (recommended)
```bash
streamlit run app.py
```
Your browser opens automatically at **http://localhost:8501**

1. Upload your resume PDF
2. Paste the job description
3. Click **Analyze Resume**

---

### 4b — Run the Command-Line version
```bash
# With a job description text file:
python cli.py --resume your_resume.pdf --jd job_description.txt

# Without a JD file (you'll be prompted to paste it):
python cli.py --resume your_resume.pdf
```

---

### 5 — You're done!
The tool outputs:
- ✅ **Match Score** (0–100)
- ✅ **Matching Keywords** found in both resume and JD
- ❌ **Missing Keywords** present in JD but not your resume
- 💡 **Actionable Suggestions** to improve your resume

---

## 🔧 How it works

```
PDF Resume
    │
    ▼
pdfplumber ──► Extract raw text
    │
    ▼
NLTK ──────── Clean text
              (lowercase, remove stopwords, lemmatize)
    │
    ▼
scikit-learn ─ TF-IDF Vectorization
              (convert text → numerical vectors)
    │
    ▼
Cosine Similarity ── Match Score (0-100)
    │
    ▼
Keyword Extraction ── Matching & Missing Skills
    │
    ▼
Rule-based logic ──── Suggestions
```

---

## 🛠 Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| PDF text is empty | Your PDF may be image-based (scanned). Use a text-based PDF. |
| NLTK errors | Run `python -c "import nltk; nltk.download('all')"` |
| Port already in use | Run `streamlit run app.py --server.port 8502` |

---

## 📚 Tech Stack (all free & open source)

- **Python 3.8+** — https://python.org
- **pdfplumber** — https://github.com/jsvine/pdfplumber
- **scikit-learn** — https://scikit-learn.org
- **NLTK** — https://nltk.org
- **Streamlit** — https://streamlit.io

---

*No OpenAI. No paid APIs. No internet needed after install.*
