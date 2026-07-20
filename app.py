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

import streamlit as st

# Page Config MUST be the very first Streamlit command
st.set_page_config(page_title="AIS Smart Resume Evaluator Pro", page_icon=":page_facing_up:")

import numpy as np
import plotly.express as px
import geocoder
import pymysql
from geopy.geocoders import Nominatim
from pdfminer.high_level import extract_text
from streamlit_tags import st_tags
from PIL import Image

import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import spacy
nlp = spacy.load('en_core_web_sm')

from Courses import ds_course, web_course, android_course, ios_course, uiux_course

skills_keywords = [
    "python", "java", "machine learning", "data analysis", "sql", "project management",
    "cloud computing", "aws", "azure", "docker", "react", "node.js", "deep learning"
]

nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('maxent_ne_chunker', quiet=True)
nltk.download('words', quiet=True)

def generate_session_token():
    return secrets.token_hex(16)

def get_geolocation():
    g = geocoder.ip('me')
    return g.latlng, g.city, g.state, g.country

def get_device_info():
    return {
        "ip_address": socket.gethostbyname(socket.gethostname()),
        "hostname": socket.gethostname(),
        "os": f"{platform.system()} {platform.release()}",
    }

def parse_resume(file_path):
    text = extract_text(file_path)
    lines = text.split('\n')
    
    parsed_data = {
        'name': lines[0] if lines else 'Not found',
        'email': next((line for line in lines if '@' in line), 'Not found'),
        'phone': next((line for line in lines if any(char.isdigit() for char in line)), 'Not found'),
        'skills': [word for line in lines for word in line.split() if len(word) > 2],
        'education': next((line for line in lines if any(edu in line.lower() for edu in ['bachelor', 'master', 'phd'])), 'Not found'),
    }
    return parsed_data

def get_database_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'resume_analyzer'),
        )
        return connection
    except Exception as e:
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

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS feedback (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        rating INT NOT NULL,
                        comments TEXT NOT NULL,
                        timestamp DATETIME NOT NULL
                    )
                """)
            connection.commit()
        except Exception as e:
            st.error(f"Error initializing database: {e}")
        finally:
            connection.close()

@st.cache_data
def analyze_resume(resume_text):
    from spacy.matcher import PhraseMatcher
    from collections import Counter

    resume_text = re.sub(r',+', ', ', resume_text)
    resume_text = re.sub(r'\s+', ' ', resume_text).strip()

    resume_doc = nlp(resume_text)

    name, email, phone = None, None, None
    for ent in resume_doc.ents:
        if ent.label_ == "PERSON" and not name:
            name = ent.text
        elif ent.label_ == "EMAIL" and not email:
            email = ent.text
        elif ent.label_ == "PHONE" and not phone:
            phone = ent.text

    if not email:
        email_pattern = re.compile(r'[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+')
        emails = re.findall(email_pattern, resume_text)
        email = emails[0] if emails else "Not found"

    if not phone:
        phone_pattern = re.compile(r'\+?\d[\d -]{8,12}\d')
        phones = re.findall(phone_pattern, resume_text)
        phone = phones[0] if phones else "Not found"

    education = []
    education_degrees = [
        "Bachelor", "Baccalaureate", "Undergraduate", "BA", "BS", "BSc",
        "Master", "Graduate", "MA", "MS", "MSc", "MBA",
        "Doctorate", "PhD", "Doctoral", "B.E", "B.Tech", "M.E", "M.Tech", "Information Science and Engineering"
    ]
    for sent in resume_doc.sents:
        for degree in education_degrees:
            if degree.lower() in sent.text.lower():
                education.append(sent.text.strip())
                break

    skills_list = [
        "Python", "Machine Learning", "Data Analysis", "Project Management",
        "Cloud Computing", "SQL", "Java", "C++", "AWS", "TensorFlow", "Keras",
        "Docker", "HTML", "CSS", "JavaScript", "Django", "MySQL", "Kali Linux",
        "Metasploit", "SEO", "pandas", "scikit-learn", "Gensim", "NLTK", "BeautifulSoup"
    ]

    matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
    patterns = [nlp.make_doc(skill.lower()) for skill in skills_list]
    matcher.add("SKILLS", patterns)

    matches = matcher(resume_doc)
    skills_found = {resume_doc[start:end].text for _, start, end in matches}

    personal_info = set()
    if name:
        personal_info.update(name.lower().split())
    if email and email != "Not found":
        personal_info.update(email.lower().split('@'))
    if phone and phone != "Not found":
        personal_info.update(phone.lower().split())
    skills_found = {skill for skill in skills_found if skill.lower() not in personal_info}

    experience = list({ent.text for ent in resume_doc.ents if ent.label_ == "ORG"})

    required_skills = {"Python", "Machine Learning", "Data Analysis", "Project Management", "Cloud Computing", "SQL"}
    matched_skills = required_skills.intersection(skills_found)
    resume_score = round(len(matched_skills) / len(required_skills) * 100, 2)

    return {
        "name": name if name else "Not found",
        "email": email,
        "mobile_number": phone,
        "skills": list(skills_found),
        "education": education,
        "experience": experience,
        "resume_score": resume_score
    }

def generate_pdf_report(resume_data, resume_score, score_breakdown, recommended_skills, recommended_field, recommended_courses):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from io import BytesIO

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Resume Analysis Report", styles['Title']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Basic Information", styles['Heading2']))
    basic_info = [
        ["Name", resume_data.get('name', 'Not found')],
        ["Email", resume_data.get('email', 'Not found')],
        ["Phone", resume_data.get('mobile_number', 'Not found')],
        ["Degree", resume_data.get('degree', 'Not found')]
    ]
    t = Table(basic_info)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Resume Score: {resume_score}/100", styles['Heading2']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Recommendations", styles['Heading2']))
    elements.append(Paragraph(f"Recommended Field: {recommended_field}", styles['Normal']))
    elements.append(Paragraph("Recommended Skills:", styles['Normal']))
    for skill in recommended_skills:
        elements.append(Paragraph(f"- {skill}", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def user_page():
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    st.title("AI Resume Analyzer")
    st.write("Upload your resume and get insights!")
    
    uploaded_file = st.file_uploader("Choose your resume (PDF)", type="pdf")
    
    if uploaded_file is not None:
        try:
            with st.spinner("Analyzing your resume..."):
                temp_directory = "temp"
                if not os.path.exists(temp_directory):
                    os.makedirs(temp_directory)  

                temp_file_path = os.path.join(temp_directory, f"resume_{st.session_state.session_id}.pdf")
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                resume_data = parse_resume(temp_file_path)
            
            display_resume_analysis(resume_data)
            offer_pdf_download(resume_data)
            display_additional_resources()

            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

        except Exception as e:
            st.error(f"An error occurred while processing your resume: {str(e)}")

    if st.button("Clear Session"):
        st.session_state.clear()
        st.experimental_rerun()

def display_resume_analysis(resume_data):
    st.subheader("Basic Information")
    st.write(f"Name: {resume_data.get('name', 'Not found')}")
    st.write(f"Email: {resume_data.get('email', 'Not found')}")
    st.write(f"Phone: {resume_data.get('mobile_number', 'Not found')}")
    
    skills = resume_data.get('skills', [])
    st.subheader("Skills")
    st.write(", ".join(skills) if skills else "No skills detected")
    
    st.subheader("Skills Recommendation")
    recommended_skills = recommend_skills(skills)
    st.write(", ".join(recommended_skills))

    st.subheader("Field Recommendation")
    recommended_field = recommend_field(skills)
    st.write(f"Recommended Field: {recommended_field}")

    st.subheader("Course Recommendation")
    recommended_courses = recommend_courses(recommended_field)
    for course in recommended_courses[:5]:
        st.write(f"- {course}")

    st.subheader("Resume Score")
    resume_score = calculate_resume_score(resume_data)
    st.write(f"Your resume score: {resume_score}/100")

def offer_pdf_download(resume_data):
    resume_score = calculate_resume_score(resume_data)
    score_breakdown = get_resume_score_breakdown(resume_data)
    recommended_skills = recommend_skills(resume_data.get('skills', []))
    recommended_field = recommend_field(resume_data.get('skills', []))
    recommended_courses = recommend_courses(recommended_field)

    pdf_buffer = generate_pdf_report(resume_data, resume_score, score_breakdown, recommended_skills, recommended_field, recommended_courses)
    st.download_button(
        label="Download Resume Analysis Report",
        data=pdf_buffer,
        file_name="resume_analysis_report.pdf",
        mime="application/pdf"
    )

def display_additional_resources():
    st.subheader("Resume Writing Tips")
    st.video("https://www.youtube.com/watch?v=y8YH0Qbu5h4")

def calculate_resume_score(resume_data):
    score_breakdown = get_resume_score_breakdown(resume_data)
    return sum(score_breakdown.values())

def get_resume_score_breakdown(resume_data):
    score_breakdown = {
        "Contact Information": 0,
        "Education": 0,
        "Skills": 0,
        "Experience": 0,
        "Formatting": 8,
        "Keywords": 7
    }
    if resume_data.get('name'): score_breakdown["Contact Information"] += 3
    if resume_data.get('email'): score_breakdown["Contact Information"] += 3
    if resume_data.get('mobile_number'): score_breakdown["Contact Information"] += 4
    
    skills = resume_data.get('skills', [])
    score_breakdown["Skills"] = min(len(skills), 10)
    return score_breakdown

def recommend_skills(skills):
    all_skills = {"Python", "Java", "C++", "JavaScript", "HTML", "CSS", "SQL", "Machine Learning", "Data Analysis", "React", "Node.js", "Docker", "AWS", "Git"}
    recommended = list(all_skills - set(skills))
    return random.sample(recommended, min(5, len(recommended)))

def recommend_field(skills):
    fields = {
        "Data Science": ["Python", "Machine Learning", "Data Analysis", "SQL"],
        "Web Development": ["JavaScript", "HTML", "CSS", "React", "Node.js"],
        "Android Development": ["Java", "Kotlin", "Android SDK"],
    }
    max_match = 0
    recommended_field = "General Software Development"
    for field, field_skills in fields.items():
        match = len(set(skills) & set(field_skills))
        if match > max_match:
            max_match = match
            recommended_field = field
    return recommended_field

def recommend_courses(field):
    courses = {
        "Data Science": ds_course,
        "Web Development": web_course,
        "Android Development": android_course,
    }
    return courses.get(field, ds_course)

def main():
    try:
        init_database()
        
        if 'session_token' not in st.session_state:
            st.session_state.session_token = generate_session_token()
        
        latlng, city, state, country = get_geolocation()
        
        st.sidebar.title("AI Resume Analyzer Pro")
        pages = ["User", "About"]
        page = st.sidebar.radio("Navigation", pages)

        st.sidebar.text(f"Session ID: {st.session_state.session_token[:8]}...")
        if city and country:
            st.sidebar.text(f"Location: {city}, {country}")
        
        if page == "User":
            user_page()
        elif page == "About":
            st.title("About AI Resume Analyzer")
            st.write("An intelligent ATS Resume Evaluation Tool designed for job seekers.")
        
        st.sidebar.markdown("---")
        st.sidebar.info("© 2024-2028 AI Resume Analyzer | Designed & Developed by Hitmanshu")

        st.markdown("---")
        st.caption("🚀 Developed by Hitmanshu | CSE Portfolio Project")
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()


    