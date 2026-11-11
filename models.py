from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship("Profile", backref="user", uselist=False, cascade="all, delete-orphan")
    saved_jobs = db.relationship("SavedJob", backref="user", cascade="all, delete-orphan")
    applications = db.relationship("Application", backref="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    education = db.Column(db.String(255))          # e.g. "B.Tech in Computer Science"
    skills = db.Column(db.Text)                     # comma separated e.g. "Python, Flask, SQL"
    experience_years = db.Column(db.Float, default=0)
    experience_summary = db.Column(db.Text)          # short free-text about past experience
    preferred_role = db.Column(db.String(150))        # e.g. "Backend Developer"
    location = db.Column(db.String(150))
    interests = db.Column(db.Text)                    # comma separated interests/domains

    def skills_list(self):
        return [s.strip() for s in (self.skills or "").split(",") if s.strip()]

    def interests_list(self):
        return [s.strip() for s in (self.interests or "").split(",") if s.strip()]

    def combined_text(self):
        """Combine all profile fields into one text blob for TF-IDF matching."""
        parts = [
            self.education or "",
            (self.skills or "") + " " + (self.skills or ""),  # weight skills more
            self.experience_summary or "",
            self.preferred_role or "",
            self.interests or "",
        ]
        return " ".join(parts)


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150))
    job_type = db.Column(db.String(50), default="Full-time")   # Full-time, Internship, Remote...
    min_experience = db.Column(db.Float, default=0)
    description = db.Column(db.Text)
    required_skills = db.Column(db.Text)     # comma separated
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def skills_list(self):
        return [s.strip() for s in (self.required_skills or "").split(",") if s.strip()]

    def combined_text(self):
        parts = [
            self.title or "",
            (self.required_skills or "") + " " + (self.required_skills or ""),  # weight skills more
            self.description or "",
        ]
        return " ".join(parts)


class SavedJob(db.Model):
    __tablename__ = "saved_jobs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

    job = db.relationship("Job")

    __table_args__ = (db.UniqueConstraint("user_id", "job_id", name="uq_user_saved_job"),)


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Applied")   # Applied, Under Review, Rejected, Selected

    job = db.relationship("Job")

    __table_args__ = (db.UniqueConstraint("user_id", "job_id", name="uq_user_applied_job"),)
