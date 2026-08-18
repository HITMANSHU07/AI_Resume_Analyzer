import streamlit as st
import time
import re
import io

st.set_page_config(
    page_title="AI Smart Resume Evaluator Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }
    .stApp { background: radial-gradient(circle at 10% 20%, #0d1117 0%, #080b10 50%, #030508 100%) !important; color: #F3F4F6; }
    [data-testid="stSidebar"] { background: rgba(10, 14, 22, 0.75) !important; backdrop-filter: blur(20px) !important; border-right: 1px solid rgba(255, 255, 255, 0.08) !important; }
    .hero-badge { display: inline-block; padding: 4px 14px; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 9999px; color: #818CF8; font-size: 0.8rem; font-weight: 600; margin-bottom: 12px; }
    .hero-title { font-size: 2.7rem; font-weight: 800; background: linear-gradient(135deg, #60A5FA 0%, #C084FC 50%, #F472B6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; }
    .hero-subtitle { color: #94A3B8; font-size: 1.05rem; margin-bottom: 24px; }
    .modern-card { background: rgba(17, 24, 39, 0.6); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 18px; padding: 24px; margin-bottom: 20px; }
    [data-testid="stFileUploader"] { background: rgba(13, 17, 23, 0.7) !important; border: 2px dashed rgba(99, 102, 241, 0.35) !important; border-radius: 16px !important; padding: 20px !important; }
    .stButton > button { background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important; color: #FFFFFF !important; font-weight: 600 !important; border-radius: 12px !important; padding: 12px 28px !important; width: 100% !important; }
    div[data-testid="metric-container"] { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.07); padding: 16px 20px; border-radius: 14px; }
    .skill-tag { display: inline-block; background: rgba(96, 165, 250, 0.15); color: #93C5FD; border: 1px solid rgba(96, 165, 250, 0.3); padding: 4px 10px; border-radius: 8px; margin: 4px 2px; font-size: 0.85rem; }
    .missing-tag { display: inline-block; background: rgba(239, 68, 68, 0.15); color: #FCA5A5; border: 1px solid rgba(239, 68, 68, 0.3); padding: 4px 10px; border-radius: 8px; margin: 4px 2px; font-size: 0.85rem; }
    .footer-container { margin-top: 50px; padding: 16px; border-radius: 14px; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.06); text-align: center; color: #64748B; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

def extract_text_robust(uploaded_file):
    text = ""
    file_bytes = uploaded_file.getvalue()
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception:
        pass

    if not text.strip():
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        except Exception:
            pass

    if not text.strip():
        text = file_bytes.decode('utf-8', errors='ignore')

    return text

TECH_SKILLS_DB = [
    "python", "java", "c++", "c#", "javascript", "typescript", "react", "next.js", 
    "angular", "vue", "node.js", "express", "spring boot", "django", "flask", "fastapi",
    "sql", "mysql", "postgresql", "mongodb", "redis", "firebase", "docker", "kubernetes",
    "aws", "azure", "gcp", "git", "github", "ci/cd", "rest api", "graphql", "html", "css",
    "tailwind", "bootstrap", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "machine learning", "nlp", "data structures", "algorithms", "microservices"
]

def evaluate_resume_accurately(raw_text):
    clean_text = raw_text.lower()
    total_words = len(re.findall(r'\b[a-zA-Z0-9+#.-]+\b', clean_text))
    
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text))
    has_phone = bool(re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', raw_text))
    has_linkedin = "linkedin.com" in clean_text
    has_github = "github.com" in clean_text
    
    contact_score = sum([has_email * 6, has_phone * 4, has_linkedin * 5, has_github * 5])

    sections = {
        "Education": ["education", "academic", "degree", "b.tech", "btech", "university", "college"],
        "Experience": ["experience", "internship", "employment", "work history"],
        "Projects": ["projects", "personal projects", "academic projects"],
        "Skills": ["skills", "technical skills", "tech stack", "technologies"],
        "Certifications": ["certifications", "certificates", "courses", "achievements"]
    }
    
    detected_sections = [sec for sec, keywords in sections.items() if any(kw in clean_text for kw in keywords)]
    section_score = len(detected_sections) * 6

    found_skills = [skill for skill in TECH_SKILLS_DB if re.search(r'\b' + re.escape(skill) + r'\b', clean_text)]
    found_skills = list(dict.fromkeys(found_skills))
    skill_score = min(len(found_skills) * 2.8, 35)

    if 250 <= total_words <= 900:
        length_score = 15
    elif 120 <= total_words < 250 or 900 < total_words <= 1300:
        length_score = 10
    else:
        length_score = 5

    final_score = int(contact_score + section_score + skill_score + length_score)
    final_score = min(max(final_score, 25), 98)

    suggested_missing = [s.title() for s in ["Docker", "Kubernetes", "AWS", "CI/CD", "PostgreSQL", "Microservices"] if s.lower() not in clean_text][:4]

    return {
        "ats_score": final_score,
        "word_count": total_words,
        "skills_count": len(found_skills),
        "found_skills": [s.title() for s in found_skills],
        "missing_skills": suggested_missing,
        "sections": detected_sections,
        "has_contact": has_email and has_phone
    }

with st.sidebar:
    st.markdown('<div class="hero-badge">v3.0 ATS ENGINE</div>', unsafe_allow_html=True)
    st.markdown("## ⚡ AI Evaluator")
    st.caption("Deep Parsing & Candidate Rating")
    st.markdown("---")
    st.radio("Navigation", ["🔍 Full Resume Audit", "ℹ️ About Engine"], label_visibility="collapsed")
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 16px;">
            <div style="font-size: 0.75rem; text-transform: uppercase; color: #94A3B8;">Extractor Status</div>
            <div style="color: #10B981; font-weight: 600; font-size: 0.92rem; margin-top: 4px;">● PDF Text Engine Ready</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="hero-badge">DYNAMIC RESUME AUDITOR</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Smart Resume Evaluator Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Upload any candidate resume to get exact extracted text insights, detected skills, and an authentic ATS rating.</div>', unsafe_allow_html=True)

st.markdown('<div class="modern-card">', unsafe_allow_html=True)
st.markdown("#### 📂 Upload Candidate Resume")
uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"], label_visibility="collapsed")

col_btn1, col_btn2 = st.columns([2, 1])
with col_btn1:
    analyze_click = st.button("🚀 Run Deep Candidate Evaluation")
with col_btn2:
    clear_click = st.button("🔄 Reset Analysis")
st.markdown('</div>', unsafe_allow_html=True)

if analyze_click:
    if uploaded_file is not None:
        with st.spinner(f"🔍 Reading and analyzing {uploaded_file.name}..."):
            resume_text = extract_text_robust(uploaded_file)
            metrics = evaluate_resume_accurately(resume_text)
            time.sleep(0.5)

        if metrics["word_count"] < 30:
            st.error("⚠️ Could not extract readable text from this PDF. Please upload a text-readable PDF.")
        else:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown(f"### 📊 Evaluation Report: `{uploaded_file.name}`")
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(label="ATS Score", value=f"{metrics['ats_score']}/100", delta=f"{metrics['ats_score'] - 50:+d} vs Base")
            m2.metric(label="Total Words", value=metrics["word_count"], delta="Scanned")
            m3.metric(label="Skills Detected", value=metrics["skills_count"], delta="Extracted")
            m4.metric(label="Sections Found", value=f"{len(metrics['sections'])} / 5", delta="Structured")

            st.markdown("---")
            
            col_sk1, col_sk2 = st.columns(2)
            with col_sk1:
                st.markdown("#### 🎯 Identified Skills")
                if metrics["found_skills"]:
                    tags_html = "".join([f'<span class="skill-tag">{skill}</span>' for skill in metrics["found_skills"]])
                    st.markdown(tags_html, unsafe_allow_html=True)
                else:
                    st.write("No matching technical skills found.")
                    
            with col_sk2:
                st.markdown("#### ⚡ Recommended Additions")
                if metrics["missing_skills"]:
                    missing_html = "".join([f'<span class="missing-tag">{skill}</span>' for skill in metrics["missing_skills"]])
                    st.markdown(missing_html, unsafe_allow_html=True)
                else:
                    st.write("Skill coverage looks complete!")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 📑 Structural Checklist")
            st.markdown(f"""
            * **Sections Present:** `{', '.join(metrics['sections']) if metrics['sections'] else 'None'}`
            * **Contact Information:** {'✅ Found Email & Phone' if metrics['has_contact'] else '⚠️ Incomplete Contact Info'}
            * **Word Count Quality:** {'✅ Optimal Length' if 250 <= metrics['word_count'] <= 900 else '⚠️ Refine word count'}
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please select and upload a PDF resume first.")

st.markdown("""
    <div class="footer-container">
        ⚡ Built & Maintained by <b>Himanshu Kumar</b> | AI Resume Engine
    </div>
""", unsafe_allow_html=True)
