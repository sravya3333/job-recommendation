"""
Run this script once to populate the database with sample job listings.

Usage:
    python seed_data.py
"""

from app import app
from models import db, Job

SAMPLE_JOBS = [
    {
        "title": "Python Backend Developer",
        "company": "TechNova Solutions",
        "location": "Hyderabad",
        "job_type": "Full-time",
        "min_experience": 0,
        "required_skills": "Python, Flask, SQL, REST API, Git",
        "description": (
            "We are looking for a Python Backend Developer to design and build REST APIs "
            "using Flask, work with relational databases, and collaborate with the frontend "
            "team. Freshers with strong fundamentals in Python and SQL are welcome to apply."
        ),
    },
    {
        "title": "Machine Learning Engineer",
        "company": "DataWiz Analytics",
        "location": "Bangalore",
        "job_type": "Full-time",
        "min_experience": 1,
        "required_skills": "Python, Scikit-learn, Machine Learning, Pandas, NumPy, TensorFlow",
        "description": (
            "Join our AI team to build and deploy machine learning models. Experience with "
            "Scikit-learn, TensorFlow, data preprocessing, and model evaluation is required. "
            "You will work on recommendation systems and predictive analytics."
        ),
    },
    {
        "title": "Frontend Developer (React)",
        "company": "PixelCraft Studio",
        "location": "Pune",
        "job_type": "Full-time",
        "min_experience": 1,
        "required_skills": "JavaScript, React, HTML, CSS, Redux",
        "description": (
            "Build responsive and dynamic user interfaces using React.js. Strong understanding "
            "of HTML, CSS, JavaScript ES6, and component-based architecture required."
        ),
    },
    {
        "title": "Data Analyst",
        "company": "InsightEdge Corp",
        "location": "Hyderabad",
        "job_type": "Full-time",
        "min_experience": 0,
        "required_skills": "SQL, Excel, Python, Data Visualization, Power BI",
        "description": (
            "Analyze large datasets to generate business insights. Proficiency in SQL, Excel, "
            "and data visualization tools like Power BI or Tableau is essential. Python "
            "knowledge is a plus."
        ),
    },
    {
        "title": "Full Stack Developer",
        "company": "CloudBridge Technologies",
        "location": "Remote",
        "job_type": "Full-time",
        "min_experience": 2,
        "required_skills": "Python, Flask, JavaScript, React, SQL, HTML, CSS",
        "description": (
            "Work across the stack building web applications end-to-end using Flask for the "
            "backend and React for the frontend. Experience with SQL databases and REST APIs "
            "is required."
        ),
    },
    {
        "title": "AI Research Intern",
        "company": "NeuralWorks Labs",
        "location": "Bangalore",
        "job_type": "Internship",
        "min_experience": 0,
        "required_skills": "Python, Machine Learning, NLP, Scikit-learn, Deep Learning",
        "description": (
            "Assist the research team in developing NLP and recommendation algorithms. Ideal "
            "for students with coursework or projects in machine learning and natural language "
            "processing using Python and Scikit-learn."
        ),
    },
    {
        "title": "Java Backend Developer",
        "company": "Orion Systems",
        "location": "Chennai",
        "job_type": "Full-time",
        "min_experience": 2,
        "required_skills": "Java, Spring Boot, SQL, Microservices, REST API",
        "description": (
            "Design scalable backend services using Java and Spring Boot. Strong knowledge "
            "of microservices architecture, SQL databases, and REST API development required."
        ),
    },
    {
        "title": "DevOps Engineer",
        "company": "CloudBridge Technologies",
        "location": "Remote",
        "job_type": "Full-time",
        "min_experience": 2,
        "required_skills": "AWS, Docker, Kubernetes, CI/CD, Linux, Python",
        "description": (
            "Manage cloud infrastructure and deployment pipelines. Hands-on experience with "
            "AWS, Docker, Kubernetes, and CI/CD tools like Jenkins or GitHub Actions is required."
        ),
    },
    {
        "title": "Software Engineer - Backend",
        "company": "Techspire Pvt Ltd",
        "location": "Hyderabad",
        "job_type": "Full-time",
        "min_experience": 0,
        "required_skills": "Python, Django, SQL, REST API, Git, Linux",
        "description": (
            "Entry-level opportunity for a backend engineer to build and maintain server-side "
            "applications using Python and Django. Good understanding of databases and version "
            "control (Git) expected."
        ),
    },
    {
        "title": "Data Scientist",
        "company": "InsightEdge Corp",
        "location": "Bangalore",
        "job_type": "Full-time",
        "min_experience": 2,
        "required_skills": "Python, Machine Learning, Pandas, Scikit-learn, Statistics, SQL",
        "description": (
            "Build predictive models and statistical analyses to support business decisions. "
            "Strong background in Python, Scikit-learn, statistics, and SQL is required."
        ),
    },
    {
        "title": "UI/UX Designer",
        "company": "PixelCraft Studio",
        "location": "Pune",
        "job_type": "Full-time",
        "min_experience": 1,
        "required_skills": "Figma, Adobe XD, Wireframing, HTML, CSS",
        "description": (
            "Design intuitive and visually appealing interfaces for web and mobile apps. "
            "Proficiency in Figma or Adobe XD along with a solid understanding of HTML/CSS "
            "is expected."
        ),
    },
    {
        "title": "Mobile App Developer (Flutter)",
        "company": "AppVerse Technologies",
        "location": "Chennai",
        "job_type": "Full-time",
        "min_experience": 1,
        "required_skills": "Flutter, Dart, REST API, Firebase, Git",
        "description": (
            "Develop cross-platform mobile applications using Flutter and Dart. Experience "
            "integrating REST APIs and Firebase services is a plus."
        ),
    },
    {
        "title": "Cloud Support Engineer",
        "company": "NimbusTech",
        "location": "Remote",
        "job_type": "Full-time",
        "min_experience": 0,
        "required_skills": "AWS, Linux, Networking, Python, Troubleshooting",
        "description": (
            "Provide technical support for cloud infrastructure customers. Basic knowledge of "
            "AWS services, Linux administration, and scripting with Python is required."
        ),
    },
    {
        "title": "Business Analyst",
        "company": "Orion Systems",
        "location": "Hyderabad",
        "job_type": "Full-time",
        "min_experience": 1,
        "required_skills": "SQL, Excel, Communication, Data Analysis, Power BI",
        "description": (
            "Bridge the gap between business needs and technical teams. Strong analytical "
            "skills, SQL, and proficiency with Excel/Power BI required."
        ),
    },
    {
        "title": "Junior Python Developer (Fresher)",
        "company": "Techspire Pvt Ltd",
        "location": "Hyderabad",
        "job_type": "Full-time",
        "min_experience": 0,
        "required_skills": "Python, SQL, Git, Problem Solving",
        "description": (
            "Great opportunity for freshers to start their career in software development. "
            "Should have a good grasp of Python fundamentals, basic SQL, and version control."
        ),
    },
]


def seed():
    with app.app_context():
        db.create_all()

        if Job.query.count() > 0:
            print(f"Database already has {Job.query.count()} jobs. Skipping seed.")
            print("Delete database/jobs.db and re-run this script if you want to reseed.")
            return

        for data in SAMPLE_JOBS:
            job = Job(**data)
            db.session.add(job)

        db.session.commit()
        print(f"Seeded {len(SAMPLE_JOBS)} sample jobs successfully.")


if __name__ == "__main__":
    seed()
