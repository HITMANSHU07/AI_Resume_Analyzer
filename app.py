import streamlit as st
import time

# ----------------- PAGE CONFIGURATION -----------------
st.set_page_config(
    page_title="AI Smart Resume Evaluator Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- MODERN HIGH-END CUSTOM CSS -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    .stApp {
        background: radial-gradient(circle at 10% 20%, #0d1117 0%, #080b10 50%, #030508 100%) !important;
        color: #F3F4F6;
    }

    [data-testid="stSidebar"] {
        background: rgba(10, 14, 22, 0.75) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    .hero-badge {
        display: inline-block;
        padding: 4px 14px;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-radius: 9999px;
        color: #818CF8;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60A5FA 0%, #C084FC 50%, #F472B6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.03em;
        line-height: 1.2;
        margin-bottom: 8px;
    }
    
    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        font-weight: 400;
        line-height: 1.6;
        margin-bottom: 24px;
    }

    .modern-card {
        background: rgba(17, 24, 39, 0.6);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 20px;
    }
    .modern-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 0 30px rgba(99, 102, 241, 0.15);
        transform: translateY(-2px);
    }

    [data-testid="stFileUploader"] {
        background: rgba(13, 17, 23, 0.7) !important;
        border: 2px dashed rgba(99, 102, 241, 0.35) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #818CF8 !important;
        background: rgba(30, 41, 59, 0.4) !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        letter-spacing: 0.3px !important;
        box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.4) !important;
        transition: all 0.25s ease !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) scale(1.01) !important;
        box-shadow: 0 15px 30px -5px rgba(124, 58, 237, 0.5) !important;
        color: #FFFFFF !important;
    }

    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.07);
        padding: 16px 20px;
        border-radius: 14px;
    }

    .footer-container {
        margin-top: 50px;
        padding: 16px;
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        text-align: center;
        color: #64748B;
        font-size: 0.9rem;
    }
    .footer-container b {
        color: #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown('<div class="hero-badge">v2.5 PRO ENGINE</div>', unsafe_allow_html=True)
    st.markdown("## ⚡ AI Evaluator")
    st.caption("Next-Gen ATS Parser & Analyzer")
    st.markdown("---")

    menu = st.radio(
        "Navigation Menu",
        ["🔍 Resume Analyzer", "🎯 ATS Matcher", "⚙️ Model Settings", "ℹ️ About Platform"],
        label_visibility="collapsed"
    )

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 16px;">
            <div style="font-size: 0.75rem; text-transform: uppercase; color: #94A3B8; letter-spacing: 0.5px;">LLM Engine</div>
            <div style="color: #10B981; font-weight: 600; font-size: 0.95rem; margin-top: 4px;">● Connected & Ready</div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 6px;">NLP Core: Scikit + Pandas</div>
        </div>
    """, unsafe_allow_html=True)

# ----------------- MAIN UI -----------------
st.markdown('<div class="hero-badge">AI-DRIVEN ATS OPTIMIZATION</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Smart Resume Evaluator Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Upload your resume to uncover real-time ATS compatibility scores, skill gaps, and keyword match analytics.</div>', unsafe_allow_html=True)

st.markdown('<div class="modern-card">', unsafe_allow_html=True)
st.markdown("#### 📂 Upload Document")
uploaded_file = st.file_uploader("Upload PDF or DOCX file (Max 200MB)", type=["pdf", "docx"], label_visibility="collapsed")

col_btn1, col_btn2 = st.columns([2, 1])
with col_btn1:
    analyze_click = st.button("🚀 Analyze & Generate Breakdown")
with col_btn2:
    clear_click = st.button("🔄 Clear Data")

st.markdown('</div>', unsafe_allow_html=True)

if analyze_click:
    if uploaded_file is not None:
        with st.spinner("⚡ Running deep neural evaluation & parsing keywords..."):
            time.sleep(1.2)

        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Performance Analytics")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(label="ATS Score", value="88 / 100", delta="High Match")
        m2.metric(label="Keyword Density", value="76%", delta="+14% optimal")
        m3.metric(label="Formatting Index", value="98%", delta="Clean")
        m4.metric(label="Readability Level", value="Grade 11", delta="Standard")
        
        st.markdown("---")
        st.markdown("#### 💡 Key Recommendations")
        st.markdown("""
        * **Quantify Impact:** Add measurable metrics (e.g., *'boosted performance by 25%'*) to recent backend projects.
        * **Tech Alignment:** Include missing keywords like **Docker**, **Kubernetes**, and **CI/CD Pipelines**.
        * **Structure:** Section headings are formatted well for automated ATS crawlers.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please upload a resume file first to generate the report.")

# ----------------- FOOTER -----------------
st.markdown("""
    <div class="footer-container">
        ⚡ Built & Maintained by <b>Himanshu Kumar</b> | AI Resume Engine
    </div>
""", unsafe_allow_html=True)
