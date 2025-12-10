import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import random

# ======================================================
# OFFICIAL LINKS BASED ON SECTION CATEGORY
# ======================================================
category_links = {
    "MCA Overview": "https://moderncoe.edu.in/master-in-computer-applications-mca-college-in-pune",
    "Academic Calendar": "https://moderncoe.edu.in/master-of-computer-application-mca",
    "Curriculum": "https://moderncoe.edu.in/mca-curriculum-new",
    "Faculty": "https://moderncoe.edu.in/mca-faculty-new",
    "Placements": "https://moderncoe.edu.in/training-placement-cell",
    "Facilities": "https://moderncoe.edu.in/",
    "Admissions & Fees": "https://moderncoe.edu.in/",
    "Rules & Policies": "https://moderncoe.edu.in/",
    "Student Routine": "",
    "Activities & Events": "https://moderncoe.edu.in/"
}

# ======================================================
# LOAD CSV
# ======================================================
@st.cache_data
def load_faq(csv_path="faq.csv"):
    df = pd.read_csv(csv_path)
    df["question"] = df["question"].fillna("")
    df["answer"] = df["answer"].fillna("")
    df["category"] = df["category"].fillna("General")
    return df

faq = load_faq("faq.csv")

# ======================================================
# STUDY TOPICS LIBRARY
# ======================================================
subject_topics = {
    "Artificial Intelligence": [
        "Basics of AI & ML overview",
        "Supervised vs Unsupervised Learning",
        "Neural Networks & Deep Learning intro",
        "Mini coding activity on model building"
    ],
    "Internet of Things": [
        "IoT architecture, sensors & actuators",
        "MQTT, REST and IoT communication protocols",
        "Edge computing & IoT data handling",
        "Mini simulation activity"
    ],
    "DMBI": [
        "Data preprocessing & cleaning",
        "Clustering and Classification",
        "Data Warehousing & BI fundamentals",
        "Case study or mini analytics"
    ],
    "Python Programming": [
        "Syntax, Variables, Data types",
        "OOP, files & exception handling",
        "pandas, numpy crash practice",
        "Small assignment"
    ],
    "Java Programming": [
        "JDK vs JVM vs JRE",
        "Collections, Generics & File I/O",
        "Exception handling & multi-threading",
        "Lab assignment"
    ],
    "C++ Programming": [
        "OOP principles: Abstraction, Encapsulation",
        "Pointers, memory, STL",
        "File handling & projects",
        "Mini coding assignment"
    ],
    "Operating Systems": [
        "Process scheduling & CPU management",
        "Memory management & segmentation",
        "File systems & OS internals",
        "Case study"
    ],
    "Computer Networks": [
        "OSI & TCP/IP models",
        "Routing vs Switching",
        "Network security basics",
        "Simulation practice"
    ],
    "Data Structures & Algorithms": [
        "Arrays & Linked Lists",
        "Trees, Graphs",
        "Sorting & Searching",
        "Time complexity practice"
    ],
    "Software Development Methodology": [
        "SDLC models",
        "Agile & Scrum",
        "UML & Requirements",
        "Testing basics"
    ]
}

# ======================================================
# NEW SMART PLANNER (NO REPETITION UNTIL TOPICS FINISH)
# ======================================================
def create_plan(subjects, days, hrs_per_day):
    plan = []
    topic_cache = {}

    # When topics get exhausted, use HIGH-VALUE academic slots:
    extra_slots = [
        "Revision & recap of previous topics",
        "Hands-on coding practice",
        "MCQ solving and test preparation",
        "Debugging & error resolution",
        "Mini project milestone work",
        "Documentation & viva preparation"
    ]

    for day in range(1, days + 1):
        idx = (day - 1) % len(subjects)
        subject = subjects[idx]
        all_topics = subject_topics.get(subject, ["Topic"])

        if subject not in topic_cache:
            topic_cache[subject] = []

        # Remaining unused topics
        remaining_topics = [
            t for t in all_topics if t not in topic_cache[subject]
        ]

        if remaining_topics:
            topic = remaining_topics[0]
            topic_cache[subject].append(topic)
        else:
            # When subject topics finish → use academic slots
            topic = extra_slots[(day - 1) % len(extra_slots)]

        plan.append({
            "Day": f"Day {day}",
            "Subject": subject,
            "Key Topics": topic,
            "Study Hours": f"{hrs_per_day} hrs"
        })

    return pd.DataFrame(plan)

# ======================================================
# PDF EXPORT
# ======================================================
def export_pdf(df):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica", 10)
    y = 770

    pdf.drawString(230, 800, "MCA Study Plan")

    for _, row in df.iterrows():
        pdf.drawString(
            40, y,
            f"{row['Day']} | {row['Subject']} | {row['Key Topics']} | {row['Study Hours']}"
        )
        y -= 15
        if y < 60:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = 770

    pdf.save()
    buffer.seek(0)
    return buffer

# ======================================================
# APP UI
# ======================================================
st.set_page_config(page_title="MCA Agent", layout="wide")
st.title("🎓 MCA Academic Assistant – Modern College of Engineering")

tab1, tab2 = st.tabs(["📖 College FAQ", "🗓 Study Planner"])

# ======================================================
# TAB 1 — FAQ SYSTEM
# ======================================================
with tab1:
    st.subheader("📁 Choose Category")
    available_sections = sorted(list(set(faq['category'].tolist())))
    section = st.selectbox("Select Category:", available_sections)

    st.subheader("📜 Select Question")
    questions = faq[faq['category'] == section]["question"].tolist()
    question = st.selectbox("Select Question:", questions)

    if st.button("Show Answer"):
        row = faq[(faq["category"] == section) & (faq["question"] == question)].iloc[0]
        st.markdown("### 🟢 Answer")
        st.write(row["answer"])
        link = category_links.get(section, "")
        if link:
            st.markdown(f"[🔗 Visit Official Page]({link})")

    st.markdown("---")
    st.markdown("### 📊 Dataset Statistics")
    st.write("Total Questions Loaded:", len(faq))
    st.table(faq['category'].value_counts())

# ======================================================
# TAB 2 — STUDY PLANNER
# ======================================================
with tab2:
    st.subheader("🧠 Create Smart Study Plan")

    subjects_list = list(subject_topics.keys())
    selected_subjects = st.multiselect("Select Subjects:", subjects_list, default=["Python Programming"])
    days = st.slider("Total Days:", 3, 30, 7)
    hours = st.slider("Daily Study Hours:", 1, 8, 3)

    if st.button("Generate Plan"):
        df = create_plan(selected_subjects, days, hours)
        st.table(df)

        pdf_file = export_pdf(df)
        st.download_button(
            label="⬇️ Download Study Plan as PDF",
            data=pdf_file,
            file_name="mca_study_plan.pdf",
            mime="application/pdf"
        )
