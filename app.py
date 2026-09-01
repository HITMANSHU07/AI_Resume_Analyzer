import os
import io
import re
import uuid
import time
import random
import socket
import secrets
import datetime
import platform
import base64
import pandas as pd
import numpy as np
import streamlit as st

# Page Config MUST be the very first Streamlit command
st.set_page_config(
    page_title="AI Resume Analyzer & Job Gap Evaluator Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

import plotly.express as px
import plotly.graph_objects as go
import geocoder
import pymysql
from pdfminer.high_level import extract_text
from PIL import Image

import nltk
import spacy

try:
    nlp = spacy.load('en_core_web_sm')
except Exception:
    nlp = None

from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('words', quiet=True)

# ---------------------------------------------------------
# MASTER DATABASE OF SKILLS & JOB ROLES
# ---------------------------------------------------------
ALL_MASTER_SKILLS = [
    # Data Science & AI
    "Python", "R", "Machine Learning", "Deep Learning", "Data Analysis", "SQL", "TensorFlow", "PyTorch",
    "scikit-learn", "Pandas", "NumPy", "Keras", "NLTK", "Spacy", "OpenCV", "NLP", "Computer Vision",
    "MLOps", "Big Data", "Spark", "Hadoop", "Tableau", "Power BI", "Statistics", "Gensim",
    
    # Web & Full Stack
    "JavaScript", "TypeScript", "React", "Next.js", "Node.js", "Express", "HTML", "CSS", "Tailwind CSS",
    "Bootstrap", "Vue", "Angular", "Redux", "GraphQL", "REST API", "Django", "Flask", "FastAPI",
    "PHP", "Laravel", "Ruby on Rails", "ASP.NET",
    
    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD", "Git", "GitHub", "Linux", "Bash",
    "Terraform", "Ansible", "Jenkins", "Prometheus", "Grafana", "Nginx", "Microservices",
    
    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle", "Cassandra", "DynamoDB",
    
    # Mobile
    "Java", "Kotlin", "Android SDK", "Swift", "SwiftUI", "Flutter", "Dart", "React Native", "iOS SDK",
    
    # Cyber Security
    "Network Security", "Kali Linux", "Wireshark", "Metasploit", "Penetration Testing", "Ethical Hacking",
    "SIEM", "OWASP", "Cryptography", "Firewalls", "Incident Response",
    
    # Core CS & Tools
    "C", "C++", "C#", "Go", "Rust", "Data Structures", "Algorithms", "System Design", "Agile", "Scrum",
    "Jira", "Figma", "Adobe XD", "UI/UX"
]

JOB_ROLES_DATABASE = {
    "Data Scientist / AI Engineer": {
        "required_skills": ["Python", "Machine Learning", "Data Analysis", "SQL", "Deep Learning", "TensorFlow", "scikit-learn", "Pandas", "NumPy"],
        "optional_skills": ["AWS", "Docker", "NLP", "PyTorch", "MLOps", "Big Data", "Spark", "Tableau"],
        "key_phrases": ["model evaluation", "feature engineering", "predictive modeling", "neural networks", "hyperparameter tuning", "data pipeline"],
        "course_key": "Data Science",
        "sample_bullets": [
            "Developed predictive machine learning models using Python and scikit-learn, achieving 94% classification accuracy.",
            "Engineered end-to-end data pipelines with Pandas & SQL to process over 500k daily records for analytics."
        ]
    },
    "Full Stack Web Developer": {
        "required_skills": ["JavaScript", "React", "Node.js", "HTML", "CSS", "SQL", "Git", "REST API"],
        "optional_skills": ["TypeScript", "Next.js", "Docker", "MongoDB", "PostgreSQL", "Express", "Tailwind CSS", "AWS"],
        "key_phrases": ["responsive design", "state management", "frontend development", "backend development", "database schema", "API integration"],
        "course_key": "Web Development",
        "sample_bullets": [
            "Architected full-stack web applications using React, Node.js, and MongoDB, reducing page load time by 35%.",
            "Designed and consumed RESTful APIs with secure JWT authentication handling 10k+ active users."
        ]
    },
    "Frontend Engineer": {
        "required_skills": ["JavaScript", "TypeScript", "React", "HTML", "CSS", "Git", "REST API"],
        "optional_skills": ["Next.js", "Redux", "Tailwind CSS", "Vue", "Angular", "Webpack", "Vite", "UI/UX"],
        "key_phrases": ["responsive UI", "cross-browser compatibility", "component architecture", "performance optimization", "state management"],
        "course_key": "Web Development",
        "sample_bullets": [
            "Built responsive micro-frontend components using React and TypeScript, improving user engagement by 25%.",
            "Optimized frontend bundle size and web vitals, reducing initial load latency from 3.2s to 1.1s."
        ]
    },
    "Backend Engineer": {
        "required_skills": ["Python", "Java", "Node.js", "SQL", "REST API", "Git", "Microservices"],
        "optional_skills": ["Docker", "Kubernetes", "AWS", "PostgreSQL", "MongoDB", "Redis", "Kafka", "Django", "FastAPI"],
        "key_phrases": ["API design", "database query optimization", "system design", "authentication", "server performance", "scalable architecture"],
        "course_key": "Web Development",
        "sample_bullets": [
            "Engineered high-throughput microservices using Node.js & PostgreSQL, handling 2,000+ requests per second.",
            "Implemented Redis caching strategy that cut database query load by 45% during peak traffic hours."
        ]
    },
    "DevOps & Cloud Engineer": {
        "required_skills": ["Linux", "Docker", "Kubernetes", "AWS", "CI/CD", "Git", "Python", "Bash"],
        "optional_skills": ["Terraform", "Ansible", "Azure", "GCP", "Jenkins", "Prometheus", "Grafana", "Nginx"],
        "key_phrases": ["infrastructure as code", "deployment pipeline", "cloud infrastructure", "containerization", "monitoring and logging", "automation"],
        "course_key": "Web Development",
        "sample_bullets": [
            "Automated CI/CD deployment pipelines using GitHub Actions and Docker, cutting release cycles from hours to minutes.",
            "Managed multi-region AWS Kubernetes (EKS) clusters with Terraform, maintaining 99.99% uptime."
        ]
    },
    "Android Developer": {
        "required_skills": ["Java", "Kotlin", "Android SDK", "Git", "REST API", "SQLite"],
        "optional_skills": ["Jetpack Compose", "Flutter", "Firebase", "Room", "Coroutines", "MVVM"],
        "key_phrases": ["mobile app UI", "activity lifecycle", "push notifications", "asynchronous tasks", "app deployment"],
        "course_key": "Android Development",
        "sample_bullets": [
            "Developed native Android apps using Kotlin and Jetpack Compose, achieving 50,000+ downloads on Google Play Store.",
            "Integrated offline-first SQLite/Room database storage and background sync using WorkManager."
        ]
    },
    "iOS Developer": {
        "required_skills": ["Swift", "iOS SDK", "Xcode", "Git", "REST API", "Core Data"],
        "optional_skills": ["SwiftUI", "UIKit", "Combine", "Objective-C", "Firebase", "CocoaPods"],
        "key_phrases": ["iOS application", "SwiftUI views", "App Store submission", "autolayout", "mobile architecture"],
        "course_key": "iOS Development",
        "sample_bullets": [
            "Built intuitive iOS applications using Swift & SwiftUI adhering to Apple Human Interface Guidelines.",
            "Utilized Core Data for local caching and URLSession for smooth REST API network calls."
        ]
    },
    "Cyber Security Analyst": {
        "required_skills": ["Linux", "Network Security", "Kali Linux", "Wireshark", "Metasploit", "Python", "Ethical Hacking"],
        "optional_skills": ["SIEM", "Penetration Testing", "Cryptography", "OWASP", "Firewalls", "Incident Response"],
        "key_phrases": ["security assessment", "vulnerability scanning", "threat analysis", "network monitoring", "compliance"],
        "course_key": "Data Science",
        "sample_bullets": [
            "Conducted penetration testing and vulnerability assessments across corporate networks using Kali Linux and Wireshark.",
            "Mitigated high-risk OWASP Top 10 web security flaws and configured automated SIEM alert monitoring."
        ]
    },
    "Data Analyst": {
        "required_skills": ["SQL", "Excel", "Python", "Data Analysis", "Tableau", "Power BI"],
        "optional_skills": ["Pandas", "NumPy", "Statistics", "Data Visualization", "R", "ETL"],
        "key_phrases": ["data visualization", "dashboard creation", "business intelligence", "exploratory data analysis", "reporting"],
        "course_key": "Data Science",
        "sample_bullets": [
            "Designed executive Power BI & Tableau dashboards translating complex raw SQL datasets into actionable KPIs.",
            "Performed exploratory data analysis using Python Pandas, discovering revenue trends that boosted sales by 12%."
        ]
    },
    "UI/UX Designer": {
        "required_skills": ["Figma", "Adobe XD", "Wireframing", "Prototyping", "UI/UX", "User Research"],
        "optional_skills": ["HTML", "CSS", "Design Systems", "Usability Testing", "Photoshop", "Illustrator"],
        "key_phrases": ["user-centered design", "interactive prototypes", "user flow", "design system", "wireframes"],
        "course_key": "UI/UX Design",
        "sample_bullets": [
            "Designed high-fidelity interactive prototypes in Figma, conducting user testing with 30+ participants.",
            "Created comprehensive UI Design Systems that improved design-to-engineering handoff speed by 40%."
        ]
    }
}

COURSE_MAPPING = {
    "Data Science": ds_course,
    "Web Development": web_course,
    "Android Development": android_course,
    "iOS Development": ios_course,
    "UI/UX Design": uiux_course,
}

# ---------------------------------------------------------
# STYLING & HELPERS
# ---------------------------------------------------------
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Header Container */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 16px;
        padding: 28px;
        text-align: center;
        box-shadow: 0 12px 30px -5px rgba(0, 0, 0, 0.4);
        margin-bottom: 25px;
    }
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
    }
    
    /* Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px 15px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
    }
    .metric-val {
        font-size: 2.2rem;
        font-weight: 800;
        color: #818cf8;
    }
    .metric-lbl {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 4px;
        font-weight: 600;
    }
    
    /* Badges */
    .badge-matched {
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 4px;
    }
    .badge-missing {
        display: inline-block;
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.35);
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 4px;
    }
    .badge-optional {
        display: inline-block;
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.35);
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 4px;
    }
    
    /* Alert Cards */
    .alert-card-danger {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #fecdd3;
    }
    .alert-card-warning {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #fef3c7;
    }
    .alert-card-success {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #d1fae5;
    }
    
    /* Sample Bullet Box */
    .bullet-box {
        background: rgba(15, 23, 42, 0.8);
        border: 1px dashed rgba(129, 140, 248, 0.4);
        border-radius: 8px;
        padding: 12px 16px;
        font-family: monospace;
        font-size: 0.9rem;
        color: #c7d2fe;
        margin-top: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

def generate_session_token():
    return secrets.token_hex(16)

def get_geolocation():
    try:
        g = geocoder.ip('me')
        return g.latlng, g.city, g.state, g.country
    except Exception:
        return None, None, None, None

def get_database_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'resume_analyzer'),
        )
        return connection
    except Exception:
        return None

def init_database():
    connection = get_database_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        resume_score INT NOT NULL,
                        recommended_field VARCHAR(255),
                        experience_level VARCHAR(50),
                        timestamp DATETIME NOT NULL
                    )
                """)
            connection.commit()
        except Exception:
            pass
        finally:
            connection.close()

# ---------------------------------------------------------
# RESUME PARSER & EVALUATOR ENGINE
# ---------------------------------------------------------
def parse_resume_full(file_path):
    try:
        text = extract_text(file_path)
    except Exception:
        text = ""

    if not text:
        text = ""

    text_clean = re.sub(r'\s+', ' ', text).strip()
    
    # Extract Email
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    email = email_match.group(0) if email_match else "Not found"

    # Extract Phone
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    phone = phone_match.group(0) if phone_match else "Not found"

    # Extract Links
    linkedin_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+', text, re.IGNORECASE)
    linkedin = linkedin_match.group(0) if linkedin_match else None

    github_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+', text, re.IGNORECASE)
    github = github_match.group(0) if github_match else None

    portfolio_match = re.search(r'(?:https?://)?(?:www\.)?[a-zA-Z0-9_-]+\.(?:dev|io|me|portfolio)', text, re.IGNORECASE)
    portfolio = portfolio_match.group(0) if portfolio_match else None

    # Name Extraction
    name = "Not found"
    if nlp:
        doc = nlp(text[:1000])
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text
                break
    if name == "Not found":
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            name = lines[0]

    # Skills detection using master list
    detected_skills = []
    text_lower = text.lower()
    for skill in ALL_MASTER_SKILLS:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            detected_skills.append(skill)
            
    # Section Presence Check
    sections = {
        "summary": bool(re.search(r'\b(summary|objective|profile|about me)\b', text, re.IGNORECASE)),
        "education": bool(re.search(r'\b(education|academic|qualification|degree|university|college|b\.tech|bachelor|master|phd)\b', text, re.IGNORECASE)),
        "experience": bool(re.search(r'\b(experience|employment|work history|internship|worked|work experience)\b', text, re.IGNORECASE)),
        "projects": bool(re.search(r'\b(projects|portfolio|key projects|personal projects)\b', text, re.IGNORECASE)),
        "certifications": bool(re.search(r'\b(certifications|certificates|licenses|courses)\b', text, re.IGNORECASE)),
        "skills_section": bool(re.search(r'\b(skills|technical skills|technologies|tools|competencies)\b', text, re.IGNORECASE))
    }

    # Quantified Metrics Check (numbers with %, $, k, M, etc.)
    metrics = re.findall(r'(\d+%\s*|\$\d+\s*|\b\d+\+\s*|\b\d+\s*(?:users|clients|percent|percentile|million|thousand|k|x|fps|ms|hrs|days|weeks|months)\b)', text, re.IGNORECASE)

    # Action Verbs Check
    action_verbs_list = ["developed", "built", "designed", "architected", "implemented", "optimized", "managed", "led", "created", "spearheaded", "engineered", "reduced", "increased", "automated", "deployed", "scaled", "analyzed", "delivered"]
    found_action_verbs = [verb for verb in action_verbs_list if re.search(r'\b' + verb + r'\b', text_lower)]

    return {
        "raw_text": text,
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "portfolio": portfolio,
        "skills": detected_skills,
        "sections": sections,
        "metrics_count": len(metrics),
        "metrics_samples": list(set(metrics))[:5],
        "action_verbs": found_action_verbs
    }

def evaluate_gap_analysis(resume_data, target_role, custom_jd=""):
    detected_skills = resume_data.get("skills", [])
    text_lower = resume_data.get("raw_text", "").lower()
    
    if target_role == "Custom Job Description":
        jd_lower = custom_jd.lower()
        required_skills = [skill for skill in ALL_MASTER_SKILLS if re.search(r'\b' + re.escape(skill.lower()) + r'\b', jd_lower)]
        if not required_skills:
            required_skills = ["Python", "JavaScript", "SQL", "Git", "REST API"]
        optional_skills = ["Docker", "AWS", "CI/CD", "TypeScript"]
        key_phrases = ["project management", "team collaboration", "problem solving", "scalable architecture"]
        course_key = "Web Development"
        sample_bullets = [
            "Tailor project accomplishments directly using key technical skills from your target Job Description."
        ]
    else:
        role_data = JOB_ROLES_DATABASE.get(target_role, JOB_ROLES_DATABASE["Full Stack Web Developer"])
        required_skills = role_data["required_skills"]
        optional_skills = role_data["optional_skills"]
        key_phrases = role_data["key_phrases"]
        course_key = role_data["course_key"]
        sample_bullets = role_data["sample_bullets"]

    # Skill matching
    matched_skills = [s for s in required_skills if s.lower() in [ds.lower() for ds in detected_skills] or s.lower() in text_lower]
    missing_required_skills = [s for s in required_skills if s not in matched_skills]
    
    matched_optional = [s for s in optional_skills if s.lower() in [ds.lower() for ds in detected_skills] or s.lower() in text_lower]
    missing_optional_skills = [s for s in optional_skills if s not in matched_optional]

    # Phrase matching
    matched_phrases = [p for p in key_phrases if p.lower() in text_lower]
    missing_phrases = [p for p in key_phrases if p not in matched_phrases]

    # Scores
    skill_score = round((len(matched_skills) / max(len(required_skills), 1)) * 100, 1)

    # Structure & Content Scoring
    struct_score = 0
    missing_sections = []
    
    if resume_data["email"] != "Not found" and resume_data["phone"] != "Not found":
        struct_score += 15
    else:
        missing_sections.append("Complete Contact Info (Email & Phone Number)")

    if resume_data["linkedin"] or resume_data["github"] or resume_data["portfolio"]:
        struct_score += 15
    else:
        missing_sections.append("Professional Portfolio Links (LinkedIn / GitHub URL)")

    if resume_data["sections"]["summary"]:
        struct_score += 15
    else:
        missing_sections.append("Professional Summary / Objective Section")

    if resume_data["sections"]["experience"] or resume_data["sections"]["projects"]:
        struct_score += 25
    else:
        missing_sections.append("Detailed Experience or Projects Section")

    if resume_data["metrics_count"] >= 3:
        struct_score += 15
    elif resume_data["metrics_count"] > 0:
        struct_score += 8
    else:
        missing_sections.append("Quantifiable Impact Metrics (e.g. percentages %, numbers, performance results)")

    if len(resume_data["action_verbs"]) >= 4:
        struct_score += 15
    else:
        missing_sections.append("Strong Action Verbs (Developed, Architected, Reduced, Automated, etc.)")

    overall_fit_score = round((0.65 * skill_score) + (0.35 * struct_score), 1)

    return {
        "target_role": target_role,
        "skill_score": skill_score,
        "struct_score": struct_score,
        "overall_fit_score": overall_fit_score,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_required_skills": missing_required_skills,
        "optional_skills": optional_skills,
        "matched_optional": matched_optional,
        "missing_optional_skills": missing_optional_skills,
        "key_phrases": key_phrases,
        "matched_phrases": matched_phrases,
        "missing_phrases": missing_phrases,
        "missing_sections": missing_sections,
        "course_key": course_key,
        "sample_bullets": sample_bullets
    }

# ---------------------------------------------------------
# VISUALIZATION & PDF REPORT ENGINE
# ---------------------------------------------------------
def create_score_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Job Fit Match Score", 'font': {'size': 18, 'color': "#f3f4f6"}},
        number={'suffix': "%", 'font': {'size': 36, 'color': "#818cf8", 'family': "Plus Jakarta Sans"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#9ca3af"},
            'bar': {'color': "#6366f1"},
            'bgcolor': "rgba(30, 41, 59, 0.5)",
            'borderwidth': 1,
            'bordercolor': "#334155",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.3)'},
                {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.3)'},
                {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.3)'}
            ],
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#f3f4f6"},
        height=240,
        margin=dict(l=20, r=20, t=35, b=20)
    )
    return fig

def create_skill_breakdown_chart(matched_count, missing_count, optional_matched):
    fig = px.bar(
        x=["Matched Required", "Missing Required", "Matched Bonus"],
        y=[matched_count, missing_count, optional_matched],
        color=["Matched Required", "Missing Required", "Matched Bonus"],
        color_discrete_map={
            "Matched Required": "#10b981",
            "Missing Required": "#ef4444",
            "Matched Bonus": "#f59e0b"
        },
        labels={'x': 'Category', 'y': 'Count'},
        title="Skills Breakdown vs Role Requirements"
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#f3f4f6"},
        showlegend=False,
        height=240,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def generate_pdf_report(resume_data, gap_data):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from io import BytesIO

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e1b4b'),
        alignment=0
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#4338ca'),
        spaceBefore=10,
        spaceAfter=6
    )
    normal_style = ParagraphStyle(
        'DocNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#1f2937')
    )

    elements = []

    # Title & Header
    elements.append(Paragraph("AI Resume Evaluation & Role Gap Analysis", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%B %d, %Y')}", normal_style))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#6366f1'), spaceAfter=12))

    # Candidate Summary Table
    elements.append(Paragraph("1. Candidate Profile & Target Role", h2_style))
    candidate_table_data = [
        [Paragraph("<b>Candidate Name:</b>", normal_style), Paragraph(resume_data.get('name', 'Not found'), normal_style)],
        [Paragraph("<b>Email:</b>", normal_style), Paragraph(resume_data.get('email', 'Not found'), normal_style)],
        [Paragraph("<b>Phone:</b>", normal_style), Paragraph(resume_data.get('phone', 'Not found'), normal_style)],
        [Paragraph("<b>Target Job Role:</b>", normal_style), Paragraph(gap_data.get('target_role', 'N/A'), normal_style)],
        [Paragraph("<b>Role Fit Score:</b>", normal_style), Paragraph(f"<b>{gap_data.get('overall_fit_score', 0)}%</b>", normal_style)]
    ]
    t_candidate = Table(candidate_table_data, colWidths=[150, 370])
    t_candidate.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 5)
    ]))
    elements.append(t_candidate)
    elements.append(Spacer(1, 12))

    # Skill Gap Summary Table
    elements.append(Paragraph("2. Skill Gap Analysis", h2_style))
    matched_str = ", ".join(gap_data.get('matched_skills', [])) if gap_data.get('matched_skills') else "None detected"
    missing_str = ", ".join(gap_data.get('missing_required_skills', [])) if gap_data.get('missing_required_skills') else "All required skills present!"
    
    gap_table_data = [
        [Paragraph("<b>Skill Status</b>", normal_style), Paragraph("<b>Skills List</b>", normal_style)],
        [Paragraph("<b>Matched Skills:</b>", normal_style), Paragraph(f"<font color='#059669'>{matched_str}</font>", normal_style)],
        [Paragraph("<b>Missing Required Skills:</b>", normal_style), Paragraph(f"<font color='#dc2626'>{missing_str}</font>", normal_style)]
    ]
    t_gap = Table(gap_table_data, colWidths=[150, 370])
    t_gap.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e0e7ff')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#c7d2fe')),
        ('PADDING', (0,0), (-1,-1), 5)
    ]))
    elements.append(t_gap)
    elements.append(Spacer(1, 12))

    # Missing Content & Recommendations
    elements.append(Paragraph("3. Missing Resume Elements & Recommendations", h2_style))
    missing_sections = gap_data.get('missing_sections', [])
    if missing_sections:
        for item in missing_sections:
            elements.append(Paragraph(f"• <b>{item}</b>: Highly recommended to add in your resume.", normal_style))
    else:
        elements.append(Paragraph("Great job! Your resume contains all essential sections and metrics.", normal_style))

    elements.append(Spacer(1, 8))
    elements.append(Paragraph("<b>Recommended Bullet Point Improvements:</b>", normal_style))
    for sample in gap_data.get('sample_bullets', []):
        elements.append(Paragraph(f"<i>\"{sample}\"</i>", normal_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------------------------------------------------------
# MAIN APP FLOW
# ---------------------------------------------------------
def main():
    inject_custom_css()
    init_database()

    if 'session_token' not in st.session_state:
        st.session_state.session_token = generate_session_token()

    latlng, city, state, country = get_geolocation()

    # Sidebar Navigation
    st.sidebar.markdown("## ⚙️ Navigation")
    pages = ["📊 Resume & Role Analyzer", "ℹ️ About & System Info"]
    page = st.sidebar.radio("Go to", pages)

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Session ID:** `{st.session_state.session_token[:8]}...`")
    if city and country:
        st.sidebar.markdown(f"📍 **Location:** {city}, {country}")
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Tip:** Target a specific Job Role or paste a custom Job Description to see missing skills & recommended resume additions!")

    if page == "📊 Resume & Role Analyzer":
        render_analyzer_page()
    else:
        render_about_page()

    st.markdown("---")
    st.caption("🚀 AI Resume Analyzer Pro | Powered by Python, Streamlit, SpaCy & NLTK")

def render_analyzer_page():
    # Hero Title Card
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">AI Smart Resume & Job Gap Evaluator</div>
        <div class="hero-subtitle">Upload your resume, analyze skill gaps, and discover exactly what content to add to match your target job role.</div>
    </div>
    """, unsafe_allow_html=True)

    col_upload, col_role = st.columns([1, 1])

    with col_upload:
        st.markdown("### 📤 Step 1: Upload Resume")
        uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])

    with col_role:
        st.markdown("### 🎯 Step 2: Choose Target Job Role")
        role_options = list(JOB_ROLES_DATABASE.keys()) + ["Custom Job Description"]
        selected_role = st.selectbox("Select Target Role", role_options, index=1)
        
        custom_jd_text = ""
        if selected_role == "Custom Job Description":
            custom_jd_text = st.text_area("Paste Target Job Description (JD) here", height=120, placeholder="Paste the job requirements and description...")

    if uploaded_file is not None:
        try:
            with st.spinner("Analyzing resume content, extracting skills & evaluating role fit..."):
                temp_dir = "temp"
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)

                temp_path = os.path.join(temp_dir, f"resume_{st.session_state.session_token}.pdf")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                resume_data = parse_resume_full(temp_path)
                gap_data = evaluate_gap_analysis(resume_data, selected_role, custom_jd_text)

                if os.path.exists(temp_path):
                    os.remove(temp_path)

            # Top Metrics Bar
            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
            with mcol1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val">{gap_data['overall_fit_score']}%</div>
                    <div class="metric-lbl">Role Match Score</div>
                </div>
                """, unsafe_allow_html=True)

            with mcol2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val" style="color: #34d399;">{len(gap_data['matched_skills'])}</div>
                    <div class="metric-lbl">Matched Skills</div>
                </div>
                """, unsafe_allow_html=True)

            with mcol3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val" style="color: #f87171;">{len(gap_data['missing_required_skills'])}</div>
                    <div class="metric-lbl">Missing Skills</div>
                </div>
                """, unsafe_allow_html=True)

            with mcol4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val" style="color: #fbbf24;">{len(gap_data['missing_sections'])}</div>
                    <div class="metric-lbl">Content Alerts</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Tabbed View
            tab1, tab2, tab3, tab4 = st.tabs([
                "📄 Resume Overview",
                "🎯 Job Gap & Skill Matrix",
                "💡 Missing Content & Recommendations",
                "📚 Learning Courses"
            ])

            with tab1:
                st.subheader("Basic Contact & Profile Details")
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"👤 **Name:** {resume_data['name']}")
                    st.write(f"📧 **Email:** {resume_data['email']}")
                    st.write(f"📞 **Phone:** {resume_data['phone']}")
                with c2:
                    st.write(f"🔗 **LinkedIn:** {resume_data['linkedin'] if resume_data['linkedin'] else '⚠️ Missing Link'}")
                    st.write(f"💻 **GitHub:** {resume_data['github'] if resume_data['github'] else '⚠️ Missing Link'}")
                    st.write(f"🌐 **Portfolio:** {resume_data['portfolio'] if resume_data['portfolio'] else '⚠️ Missing Link'}")

                st.markdown("---")
                st.subheader("Extracted Skills from Resume")
                if resume_data["skills"]:
                    badge_html = "".join([f'<span class="badge-matched">{s}</span>' for s in resume_data["skills"]])
                    st.markdown(badge_html, unsafe_allow_html=True)
                else:
                    st.info("No standard skills auto-detected from resume text.")

                st.markdown("---")
                st.subheader("PDF Export Report")
                pdf_bytes = generate_pdf_report(resume_data, gap_data)
                st.download_button(
                    label="📥 Download Detailed Resume & Gap Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"resume_gap_report_{selected_role.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            with tab2:
                gcol1, gcol2 = st.columns([1, 1])
                with gcol1:
                    st.plotly_chart(create_score_gauge(gap_data['overall_fit_score']), use_container_width=True)
                with gcol2:
                    st.plotly_chart(create_skill_breakdown_chart(
                        len(gap_data['matched_skills']),
                        len(gap_data['missing_required_skills']),
                        len(gap_data['matched_optional'])
                    ), use_container_width=True)

                st.markdown("### 🔍 Required Skills Comparison Matrix")
                
                col_m, col_u = st.columns(2)
                with col_m:
                    st.markdown("#### ✅ Matched Role Skills")
                    if gap_data['matched_skills']:
                        m_html = "".join([f'<span class="badge-matched">✓ {s}</span>' for s in gap_data['matched_skills']])
                        st.markdown(m_html, unsafe_allow_html=True)
                    else:
                        st.write("No matched required skills found.")

                with col_u:
                    st.markdown("#### ❌ Missing Required Skills")
                    if gap_data['missing_required_skills']:
                        u_html = "".join([f'<span class="badge-missing">✗ {s}</span>' for s in gap_data['missing_required_skills']])
                        st.markdown(u_html, unsafe_allow_html=True)
                    else:
                        st.success("Awesome! You possess all essential technical skills for this role!")

                st.markdown("---")
                st.markdown("#### 🌟 Bonus / Optional Role Skills")
                opt_html = ""
                for s in gap_data['optional_skills']:
                    if s in gap_data['matched_optional']:
                        opt_html += f'<span class="badge-matched">✓ {s}</span>'
                    else:
                        opt_html += f'<span class="badge-optional">+ {s}</span>'
                st.markdown(opt_html, unsafe_allow_html=True)

            with tab3:
                st.subheader("📌 What is Missing in Your Resume?")
                st.markdown(f"Here are the specific missing items and recommendations to optimize your resume for **{selected_role}**:")

                if gap_data['missing_sections']:
                    for sec in gap_data['missing_sections']:
                        st.markdown(f"""
                        <div class="alert-card-danger">
                            ⚠️ <b>Missing Item: {sec}</b><br>
                            Adding this section/content will boost your ATS resume score and make your profile stand out to recruiters.
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="alert-card-success">
                        🎉 <b>Great Structure!</b> Your resume includes all primary structural sections, links, and quantifiable impact metrics.
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")
                st.subheader("✍️ Copyable Project Bullet Point Recommendations")
                st.write("Use these metric-driven sample bullet points as inspiration to describe your project experience:")
                for bullet in gap_data['sample_bullets']:
                    st.markdown(f'<div class="bullet-box">• {bullet}</div>', unsafe_allow_html=True)

                st.markdown("---")
                st.subheader("🔑 Missing Role Keywords & Phrases")
                if gap_data['missing_phrases']:
                    phrases_html = "".join([f'<span class="badge-optional">{p}</span>' for p in gap_data['missing_phrases']])
                    st.markdown(phrases_html, unsafe_allow_html=True)
                else:
                    st.write("Your resume covers all standard role phrases.")

            with tab4:
                st.subheader(f"📚 Recommended Courses for {gap_data['target_role']}")
                c_key = gap_data['course_key']
                courses = COURSE_MAPPING.get(c_key, ds_course)

                for course_title, course_url in courses[:8]:
                    st.markdown(f"- 🎓 [{course_title}]({course_url})")

                st.markdown("---")
                st.subheader("🎥 Helpful Resume & Interview Videos")
                vcol1, vcol2 = st.columns(2)
                with vcol1:
                    st.markdown("#### Resume Tips")
                    st.video(resume_videos[0])
                with vcol2:
                    st.markdown("#### Interview Prep")
                    st.video(interview_videos[0])

        except Exception as e:
            st.error(f"Error processing resume: {str(e)}")

def render_about_page():
    st.title("About AI Resume Analyzer Pro")
    st.markdown("""
    **AI Resume Analyzer Pro** is an intelligent resume parsing & job gap evaluation platform designed to help job seekers tailor their resumes for ATS screening.
    
    ### Features:
    - 🔍 **ATS Resume Parsing**: Automatically extracts candidate contact information, skills, and structural sections.
    - 🎯 **Job Role Gap Analysis**: Compares candidate skills against job role expectations or custom pasted JDs.
    - 🚨 **Missing Content Detection**: Alerts candidates about missing links (LinkedIn/GitHub), missing metrics, and missing skills.
    - 📊 **Visual Analytics**: Interactive Plotly score gauge and skill match breakdown graphs.
    - 📥 **PDF Export**: Downloadable evaluation report summarizing gaps and recommendations.
    """)

if __name__ == "__main__":
    main()