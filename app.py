# app.py
# ─────────────────────────────────────────────────────────────────
# Streamlit UI for the AI Resume Analyzer
# Run with:  streamlit run app.py
# ─────────────────────────────────────────────────────────────────

import os
import tempfile
import streamlit as st
from analyzer import analyze_resume   # our core logic module

# ── Page configuration ───────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer By Dinesh",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS — clean, professional look ────────────────────────
st.markdown("""
<style>
/* Main background and font */
.stApp { background: #0f1117; color: #e8e4dc; }

/* Card-style containers */
.result-card {
    background: #1a1f2e;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}

/* Score circle */
.score-circle {
    width: 130px; height: 130px;
    border-radius: 50%;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    margin: 0 auto 1rem;
    font-weight: 700;
}

/* Keyword pills */
.pill-green {
    display: inline-block;
    background: rgba(78,203,141,0.15);
    border: 1px solid rgba(78,203,141,0.4);
    color: #4ecb8d;
    padding: 3px 12px; border-radius: 100px;
    font-size: 13px; margin: 3px;
}
.pill-red {
    display: inline-block;
    background: rgba(232,96,96,0.12);
    border: 1px solid rgba(232,96,96,0.35);
    color: #e86060;
    padding: 3px 12px; border-radius: 100px;
    font-size: 13px; margin: 3px;
}

/* Section headers */
.section-label {
    font-size: 11px; letter-spacing: 0.1em;
    text-transform: uppercase; color: rgba(232,228,220,0.5);
    margin-bottom: 0.75rem;
}
</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 2rem 0 1.5rem;'>
    <p style='color:#e8c96d; font-size:12px; letter-spacing:0.15em; text-transform:uppercase;
              border:1px solid rgba(232,201,109,0.3); display:inline-block;
              padding:4px 16px; border-radius:100px; margin-bottom:0.75rem;
              background:rgba(232,201,109,0.07);'>
        100% Free · No API Key · Runs Locally
    </p>
    <h1 style='font-size:2.6rem; font-weight:700; color:#f0ece4; margin:0;'>
        AI Resume Analyzer
    </h1>
    <p style='color:rgba(240,236,228,0.5); margin-top:0.4rem;'>
        Upload your resume PDF · Paste a job description · Get instant feedback
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Input columns ────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("#### 📄 Upload Resume (PDF)")
    uploaded_pdf = st.file_uploader(
        label="",
        type=["pdf"],
        help="Only PDF files are supported."
    )
    if uploaded_pdf:
        st.success(f"✓ Loaded: **{uploaded_pdf.name}**")

with col_right:
    st.markdown("#### 📋 Paste Job Description")
    job_description = st.text_area(
        label="",
        height=220,
        placeholder="Paste the full job description here…\n\nExample:\nWe are looking for a Python developer "
                    "with experience in machine learning, data pipelines, SQL, and cloud platforms (AWS/GCP)…"
    )

st.markdown("")

# ── Analyse button ────────────────────────────────────────────────
_, btn_col, _ = st.columns([2, 1, 2])
with btn_col:
    run = st.button("🔍  Analyze Resume", use_container_width=True, type="primary")

# ── Run analysis ──────────────────────────────────────────────────
if run:
    # Validate inputs
    if not uploaded_pdf:
        st.error("Please upload a resume PDF before analyzing.")
        st.stop()
    if not job_description.strip():
        st.error("Please paste a job description before analyzing.")
        st.stop()

    # Save uploaded PDF to a temp file so pdfplumber can read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_pdf.read())
        tmp_path = tmp.name

    # Run the core analysis pipeline
    with st.spinner("Analyzing your resume… this takes a few seconds."):
        try:
            results = analyze_resume(tmp_path, job_description)
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            os.unlink(tmp_path)
            st.stop()
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    score      = results["score"]
    matching   = results["matching"]
    missing    = results["missing"]
    suggestions = results["suggestions"]

    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    st.markdown("")

    # ── Row 1: Score + quick stats ────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    # Colour the score based on value
    if score >= 70:
        ring_color = "#4ecb8d"; ring_bg = "rgba(78,203,141,0.12)"
    elif score >= 50:
        ring_color = "#e8c96d"; ring_bg = "rgba(232,201,109,0.12)"
    elif score >= 30:
        ring_color = "#f0a553"; ring_bg = "rgba(240,165,83,0.12)"
    else:
        ring_color = "#e86060"; ring_bg = "rgba(232,96,96,0.12)"

    with c1:
        st.markdown(f"""
        <div class='result-card' style='text-align:center;'>
            <div class='score-circle' style='background:{ring_bg}; border: 3px solid {ring_color};'>
                <span style='font-size:2rem; color:{ring_color};'>{score}</span>
                <span style='font-size:11px; color:rgba(240,236,228,0.5); letter-spacing:0.06em;'>/ 100</span>
            </div>
            <div class='section-label' style='text-align:center;'>Match Score</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class='result-card' style='text-align:center; padding-top:2.2rem;'>
            <div style='font-size:2rem; font-weight:700; color:#4ecb8d;'>{len(matching)}</div>
            <div class='section-label'>Matching Keywords</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class='result-card' style='text-align:center; padding-top:2.2rem;'>
            <div style='font-size:2rem; font-weight:700; color:#e86060;'>{len(missing)}</div>
            <div class='section-label'>Missing Keywords</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        level = "Excellent" if score >= 70 else "Good" if score >= 50 else "Fair" if score >= 30 else "Weak"
        lcolor = ring_color
        st.markdown(f"""
        <div class='result-card' style='text-align:center; padding-top:2.2rem;'>
            <div style='font-size:1.8rem; font-weight:700; color:{lcolor};'>{level}</div>
            <div class='section-label'>Overall Verdict</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # ── Row 2: Matching + Missing keywords ───────────────────────
    kw_left, kw_right = st.columns(2, gap="large")

    with kw_left:
        st.markdown("#### ✅ Matching Skills Found")
        if matching:
            pills = "".join(f"<span class='pill-green'>{kw}</span>" for kw in matching)
            st.markdown(f"<div style='line-height:2.2;'>{pills}</div>", unsafe_allow_html=True)
        else:
            st.info("No strong keyword matches found.")

    with kw_right:
        st.markdown("#### ❌ Missing Skills (from Job Description)")
        if missing:
            pills = "".join(f"<span class='pill-red'>{kw}</span>" for kw in missing)
            st.markdown(f"<div style='line-height:2.2;'>{pills}</div>", unsafe_allow_html=True)
        else:
            st.success("No major missing keywords — great coverage!")

    st.markdown("")

    # ── Row 3: Suggestions ────────────────────────────────────────
    st.markdown("#### 💡 Suggestions to Improve Your Resume")
    for i, tip in enumerate(suggestions, 1):
        st.markdown(f"""
        <div class='result-card' style='border-left: 3px solid #e8c96d;'>
            <span style='color:rgba(240,236,228,0.4); font-size:12px;'>#{i}</span>
            <span style='margin-left:8px; font-size:14px;'>{tip}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # ── Expandable: raw resume text ───────────────────────────────
    with st.expander("📃 View Extracted Resume Text"):
        st.text_area(
            label="",
            value=results["resume_text"],
            height=300,
            disabled=True
        )

    st.success("✓ Analysis complete! Use the suggestions above to improve your resume.")
                    
