# analyzer.py
# ─────────────────────────────────────────────────────────────────
# Core logic for the AI Resume Analyzer.
# Uses ONLY free/open-source tools — no paid APIs required.
# ─────────────────────────────────────────────────────────────────
import re
import pdfplumber
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Download required NLTK data (runs once, cached afterwards) ──
def download_nltk_data():
    packages = ["stopwords", "punkt", "wordnet", "omw-1.4", "punkt_tab"]
    for pkg in packages:
        try:
            nltk.download(pkg, quiet=True)
        except Exception:
            pass

download_nltk_data()


# ─────────────────────────────────────────────────────────────────
# STEP 1 — Extract text from a PDF file
# ─────────────────────────────────────────────────────────────────
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Opens a PDF file and extracts all text from every page.
    Returns a single string with all the content.
    """
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:                        # some pages may be blank
                text += page_text + "\n"
    return text.strip()


# ─────────────────────────────────────────────────────────────────
# STEP 2 — Clean and normalise raw text
# ─────────────────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    """
    Lowercase, remove punctuation/numbers, strip stopwords,
    and lemmatise every word so 'managing' → 'manage', etc.
    """
    lemmatizer = WordNetLemmatizer()
    stop_words  = set(stopwords.words("english"))

    # Lowercase
    text = text.lower()

    # Keep only alphabetic characters and spaces
    text = re.sub(r"[^a-z\s]", " ", text)

    # Tokenise (split into individual words)
    tokens = word_tokenize(text)

    # Remove stopwords and very short tokens, then lemmatise
    cleaned = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word not in stop_words and len(word) > 2
    ]

    return " ".join(cleaned)


# ─────────────────────────────────────────────────────────────────
# STEP 3 — Calculate match score using TF-IDF + Cosine Similarity
# ─────────────────────────────────────────────────────────────────
def calculate_match_score(resume_text: str, jd_text: str) -> float:
    """
    Converts both texts into TF-IDF vectors and measures how
    similar they are using cosine similarity (0 = no match,
    1 = perfect match).  Returns a 0-100 integer score.
    """
    # TF-IDF vectoriser — ignores very rare and very common words
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),   # consider single words AND 2-word phrases
        max_features=5000,
        sublinear_tf=True     # dampens the effect of very frequent terms
    )

    # Fit on both texts together, then transform each
    tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])

    # Cosine similarity between the two document vectors
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    # Convert 0-1 float → 0-100 integer
    return round(score * 100, 1)


# ─────────────────────────────────────────────────────────────────
# STEP 4 — Extract meaningful keywords from a piece of text
# ─────────────────────────────────────────────────────────────────
def extract_keywords(text: str, top_n: int = 30) -> set:
    """
    Uses TF-IDF to find the most important words in the text.
    Returns a set of keyword strings.
    """
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=200,
        stop_words="english",
        sublinear_tf=True
    )

    try:
        tfidf_matrix = vectorizer.fit_transform([text])
    except ValueError:
        # Happens when text is empty or has only stop-words
        return set()

    # Map each word/phrase → its TF-IDF score
    feature_names = vectorizer.get_feature_names_out()
    scores        = tfidf_matrix.toarray()[0]
    keyword_scores = sorted(
        zip(feature_names, scores),
        key=lambda x: x[1],
        reverse=True
    )

    # Return the top-N keywords as a set (lowercase)
    return {kw for kw, _ in keyword_scores[:top_n]}


# ─────────────────────────────────────────────────────────────────
# STEP 5 — Find matching and missing keywords
# ─────────────────────────────────────────────────────────────────
def find_keyword_gaps(resume_keywords: set, jd_keywords: set):
    """
    Compares the two keyword sets and returns:
      - matching : keywords present in BOTH (resume covers these)
      - missing  : keywords in the JD but NOT in the resume
    """
    matching = resume_keywords & jd_keywords     # set intersection
    missing  = jd_keywords - resume_keywords     # in JD, not in resume
    return sorted(matching), sorted(missing)


# ─────────────────────────────────────────────────────────────────
# STEP 6 — Generate human-readable improvement suggestions
# ─────────────────────────────────────────────────────────────────
def generate_suggestions(missing_keywords: list, score: float) -> list:
    """
    Produces actionable suggestions based on:
      - which keywords are missing from the resume
      - how low/high the overall match score is
    """
    suggestions = []

    # ── Score-based general advice ──────────────────────────────
    if score < 30:
        suggestions.append(
            "⚠️  Your resume matches less than 30% of the job description. "
            "Consider a major rewrite tailored to this specific role."
        )
    elif score < 50:
        suggestions.append(
            "📝  Moderate match. Add more role-specific language from the "
            "job description throughout your resume."
        )
    elif score < 70:
        suggestions.append(
            "👍  Good match! Fine-tune a few sections to push your score higher."
        )
    else:
        suggestions.append(
            "🌟  Excellent match! Your resume aligns well with this job description."
        )

    # ── Missing-keyword suggestions ─────────────────────────────
    if missing_keywords:
        # Group into manageable chunks for readability
        top_missing = missing_keywords[:10]
        suggestions.append(
            f"🔑  Add these important keywords to your resume: "
            f"{', '.join(top_missing)}."
        )

        # Heuristic: look for likely skill / tool names (short phrases)
        tech_terms = [kw for kw in missing_keywords if len(kw.split()) <= 2][:8]
        if tech_terms:
            suggestions.append(
                f"🛠️  Consider adding a dedicated 'Skills' section that includes: "
                f"{', '.join(tech_terms)}."
            )

    # ── Always-useful general tips ───────────────────────────────
    suggestions += [
        "📊  Quantify your achievements — use numbers and percentages "
        "wherever possible (e.g. 'Reduced load time by 40%').",
        "🎯  Mirror the exact phrasing from the job description in your "
        "bullet points — ATS systems are keyword-sensitive.",
        "📋  Ensure your resume has clear sections: Summary, Experience, "
        "Skills, Education.",
    ]

    return suggestions


# ─────────────────────────────────────────────────────────────────
# MAIN FUNCTION — runs the full analysis pipeline
# ─────────────────────────────────────────────────────────────────
def analyze_resume(pdf_path: str, job_description: str) -> dict:
    """
    Full pipeline:
      1. Extract text from PDF
      2. Clean both texts
      3. Calculate match score
      4. Extract keywords from each
      5. Find gaps
      6. Generate suggestions
    Returns a dictionary with all results.
    """
    # 1 — Extract raw text from the uploaded PDF
    raw_resume = extract_text_from_pdf(pdf_path)

    # 2 — Clean both texts for analysis
    clean_resume = clean_text(raw_resume)
    clean_jd     = clean_text(job_description)

    # 3 — Match score (0-100)
    score = calculate_match_score(clean_resume, clean_jd)

    # 4 — Keywords from each document
    resume_keywords = extract_keywords(clean_resume, top_n=40)
    jd_keywords     = extract_keywords(clean_jd,     top_n=40)

    # 5 — Matching vs missing keywords
    matching, missing = find_keyword_gaps(resume_keywords, jd_keywords)

    # 6 — Suggestions
    suggestions = generate_suggestions(missing, score)

    return {
        "score":           score,
        "resume_text":     raw_resume,
        "matching":        matching,
        "missing":         missing,
        "suggestions":     suggestions,
        "resume_keywords": sorted(resume_keywords),
        "jd_keywords":     sorted(jd_keywords),
    }
