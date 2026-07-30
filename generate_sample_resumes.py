"""
Generates 5 sample resume PDFs into sample_data/resumes/ for demo purposes.
These are fictional candidates with a deliberate spread of skill overlap
against sample_data/job_description.txt — two strong matches, two medium,
and one clear mismatch — so a demo shows the ranking clearly differentiating
candidates.

Run once with:  python generate_sample_resumes.py
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "sample_data", "resumes")

RESUMES = {
    "priya_sharma.pdf": [
        "Priya Sharma",
        "priya.sharma@email.com | +91-98765-43210",
        "",
        "SUMMARY",
        "Data Scientist with 2 years of experience building predictive models",
        "and delivering data-driven insights to business stakeholders.",
        "",
        "SKILLS",
        "Python, SQL, Machine Learning, Pandas, Statistics, AWS, Tableau,",
        "Communication, Problem Solving",
        "",
        "EXPERIENCE",
        "Data Scientist, XYZ Analytics (2023 - Present)",
        "- Built machine learning models to predict customer churn",
        "- Used Pandas and SQL to clean and analyze large datasets",
        "- Presented insights to stakeholders using Tableau dashboards",
        "- Deployed models on AWS for production use",
        "",
        "EDUCATION",
        "B.Tech in Computer Science, 2022",
    ],
    "karan_mehta.pdf": [
        "Karan Mehta",
        "karan.mehta@email.com | +91-91234-56780",
        "",
        "SUMMARY",
        "Machine Learning enthusiast with hands-on experience in deep",
        "learning and statistical modeling from internships and coursework.",
        "",
        "SKILLS",
        "Python, Machine Learning, Deep Learning, TensorFlow, Statistics,",
        "Problem Solving, Communication",
        "",
        "EXPERIENCE",
        "ML Engineer Intern, DataVision Labs (2024)",
        "- Trained deep learning models for image classification using TensorFlow",
        "- Applied statistical methods to validate model performance",
        "- Collaborated with senior engineers to improve model accuracy",
        "",
        "EDUCATION",
        "B.Tech in Information Technology, 2024",
    ],
    "sneha_patel.pdf": [
        "Sneha Patel",
        "sneha.patel@email.com | +91-99887-76655",
        "",
        "SUMMARY",
        "Business analyst with a strong background in reporting and",
        "dashboarding, transitioning into data analytics.",
        "",
        "SKILLS",
        "Python, Data Analysis, Excel, Power BI, Communication, Teamwork",
        "",
        "EXPERIENCE",
        "Business Analyst, Retail Insights Co. (2022 - Present)",
        "- Built Power BI dashboards for sales performance tracking",
        "- Performed data analysis in Excel and Python for monthly reports",
        "- Worked closely with sales and marketing teams",
        "",
        "EDUCATION",
        "B.Com in Business Analytics, 2021",
    ],
    "rahul_verma.pdf": [
        "Rahul Verma",
        "rahul.verma@email.com | +91-90000-11122",
        "",
        "SUMMARY",
        "Junior data analyst with foundational reporting experience,",
        "looking to grow into a data science role.",
        "",
        "SKILLS",
        "SQL, Excel, Communication, Problem Solving, Project Management",
        "",
        "EXPERIENCE",
        "Junior Data Analyst, Metro Retail (2023 - Present)",
        "- Wrote SQL queries to extract data for weekly reports",
        "- Maintained Excel-based tracking sheets for inventory",
        "- Coordinated with store managers on data requests",
        "",
        "EDUCATION",
        "B.Sc in Statistics, 2023",
    ],
    "amit_singh.pdf": [
        "Amit Singh",
        "amit.singh@email.com | +91-93333-22211",
        "",
        "SUMMARY",
        "Backend software engineer specializing in scalable microservices",
        "and cloud infrastructure.",
        "",
        "SKILLS",
        "Java, Spring Boot, Docker, Kubernetes, AWS, Leadership, Teamwork",
        "",
        "EXPERIENCE",
        "Backend Engineer, CloudCore Systems (2021 - Present)",
        "- Designed microservices using Java and Spring Boot",
        "- Managed containerized deployments with Docker and Kubernetes",
        "- Led a team of 3 junior engineers",
        "",
        "EDUCATION",
        "B.Tech in Computer Science, 2020",
    ],
}


def make_pdf(filename, lines):
    path = os.path.join(OUTPUT_DIR, filename)
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - 60
    for line in lines:
        if line.isupper() and line.strip():
            c.setFont("Helvetica-Bold", 12)
        else:
            c.setFont("Helvetica", 11)
        c.drawString(60, y, line)
        y -= 18
    c.save()
    print(f"Created {path}")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for filename, lines in RESUMES.items():
        make_pdf(filename, lines)
    print(f"\nDone. {len(RESUMES)} sample resumes created in {OUTPUT_DIR}")
