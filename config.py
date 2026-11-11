import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # SQLite by default. To use MySQL instead, set the DATABASE_URL env variable, e.g.:
    # mysql+pymysql://username:password@localhost/job_recommendation_db
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "database", "jobs.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
