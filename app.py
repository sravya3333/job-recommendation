from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from sqlalchemy import or_

from config import Config
from models import db, User, Profile, Job, SavedJob, Application
from recommender import recommend_jobs

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    total_jobs = Job.query.count()
    return render_template("index.html", total_jobs=total_jobs)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("register"))

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Create an empty profile right away
        profile = Profile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.name}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    profile = current_user.profile
    if profile is None:
        profile = Profile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()

    if request.method == "POST":
        profile.education = request.form.get("education", "").strip()
        profile.skills = request.form.get("skills", "").strip()
        profile.experience_years = float(request.form.get("experience_years") or 0)
        profile.experience_summary = request.form.get("experience_summary", "").strip()
        profile.preferred_role = request.form.get("preferred_role", "").strip()
        profile.location = request.form.get("location", "").strip()
        profile.interests = request.form.get("interests", "").strip()

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", profile=profile)


# ---------------------------------------------------------------------------
# Jobs: browse / search
# ---------------------------------------------------------------------------

@app.route("/jobs")
def jobs():
    query = request.args.get("q", "").strip()
    location = request.args.get("location", "").strip()

    jobs_query = Job.query

    if query:
        like = f"%{query}%"
        jobs_query = jobs_query.filter(
            or_(
                Job.title.ilike(like),
                Job.company.ilike(like),
                Job.required_skills.ilike(like),
                Job.description.ilike(like),
            )
        )

    if location:
        jobs_query = jobs_query.filter(Job.location.ilike(f"%{location}%"))

    all_jobs = jobs_query.order_by(Job.posted_at.desc()).all()

    saved_ids, applied_ids = set(), set()
    if current_user.is_authenticated:
        saved_ids = {sj.job_id for sj in current_user.saved_jobs}
        applied_ids = {ap.job_id for ap in current_user.applications}

    return render_template(
        "jobs.html",
        jobs=all_jobs,
        query=query,
        location=location,
        saved_ids=saved_ids,
        applied_ids=applied_ids,
    )


@app.route("/jobs/<int:job_id>")
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)

    is_saved = False
    is_applied = False
    match = None

    if current_user.is_authenticated:
        is_saved = SavedJob.query.filter_by(user_id=current_user.id, job_id=job.id).first() is not None
        is_applied = Application.query.filter_by(user_id=current_user.id, job_id=job.id).first() is not None

        if current_user.profile and current_user.profile.skills:
            result = recommend_jobs(current_user.profile, [job])
            if result:
                match = result[0]

    return render_template("job_detail.html", job=job, is_saved=is_saved, is_applied=is_applied, match=match)


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------

@app.route("/recommendations")
@login_required
def recommendations():
    profile = current_user.profile

    if not profile or not profile.skills:
        flash("Please complete your profile (especially skills) to get personalized recommendations.", "warning")
        return redirect(url_for("profile"))

    all_jobs = Job.query.all()
    results = recommend_jobs(profile, all_jobs)

    return render_template("recommendations.html", results=results)


# ---------------------------------------------------------------------------
# Save / Apply actions
# ---------------------------------------------------------------------------

@app.route("/jobs/<int:job_id>/save", methods=["POST"])
@login_required
def save_job(job_id):
    job = Job.query.get_or_404(job_id)
    existing = SavedJob.query.filter_by(user_id=current_user.id, job_id=job.id).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash("Removed from saved jobs.", "info")
    else:
        saved = SavedJob(user_id=current_user.id, job_id=job.id)
        db.session.add(saved)
        db.session.commit()
        flash("Job saved!", "success")

    return redirect(request.referrer or url_for("jobs"))


@app.route("/jobs/<int:job_id>/apply", methods=["POST"])
@login_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)
    existing = Application.query.filter_by(user_id=current_user.id, job_id=job.id).first()

    if existing:
        flash("You have already applied for this job.", "info")
    else:
        application = Application(user_id=current_user.id, job_id=job.id)
        db.session.add(application)
        db.session.commit()
        flash(f"Successfully applied for {job.title} at {job.company}!", "success")

    return redirect(request.referrer or url_for("jobs"))


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    profile = current_user.profile

    recommended = []
    if profile and profile.skills:
        all_jobs = Job.query.all()
        recommended = recommend_jobs(profile, all_jobs, top_n=5)

    saved = SavedJob.query.filter_by(user_id=current_user.id).order_by(SavedJob.saved_at.desc()).all()
    applied = Application.query.filter_by(user_id=current_user.id).order_by(Application.applied_at.desc()).all()

    profile_complete = bool(profile and profile.skills and profile.education and profile.preferred_role)

    return render_template(
        "dashboard.html",
        recommended=recommended,
        saved=saved,
        applied=applied,
        profile_complete=profile_complete,
        total_jobs=Job.query.count(),
    )


# ---------------------------------------------------------------------------
# CLI helper: initialize DB
# ---------------------------------------------------------------------------

@app.cli.command("init-db")
def init_db():
    """Create all database tables."""
    db.create_all()
    print("Database initialized.")

with app.app_context():
    db.create_all()
    if Job.query.count() == 0:
        import seed_data
        if hasattr(seed_data, "seed"):
            seed_data.seed()
if __name__ == "__main__":
    import os
    with app.app_context():
        db.create_all()
    # host="0.0.0.0" makes the server reachable from other devices/hosting platforms,
    # not just 127.0.0.1 (localhost-only).
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
