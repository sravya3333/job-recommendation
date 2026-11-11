"""
AI-based Job Recommendation Engine
------------------------------------
Uses Scikit-learn's TfidfVectorizer to convert the user's profile text and
job description text into vectors, then ranks jobs using Cosine Similarity.

Also computes a human-readable "why recommended" explanation by finding the
overlap between the user's skills and each job's required skills.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _normalize_skill(skill: str) -> str:
    return skill.strip().lower()


def compute_skill_overlap(user_skills, job_skills):
    """Return (matched_skills, missing_skills) preserving job's original casing."""
    user_set = {_normalize_skill(s) for s in user_skills}
    matched = []
    missing = []
    for job_skill in job_skills:
        if _normalize_skill(job_skill) in user_set:
            matched.append(job_skill)
        else:
            missing.append(job_skill)
    return matched, missing


def recommend_jobs(profile, jobs, top_n=None):
    """
    profile: a Profile model instance (the logged-in user's profile)
    jobs: list of Job model instances (candidate jobs)
    top_n: optionally limit to top N results

    Returns a list of dicts sorted by match score (highest first):
        {
            "job": Job instance,
            "score": float (0-100, rounded),
            "matched_skills": [...],
            "missing_skills": [...],
            "reason": str
        }
    """
    if not jobs:
        return []

    # Build the corpus: index 0 = user profile, rest = jobs
    documents = [profile.combined_text()] + [job.combined_text() for job in jobs]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    user_vector = tfidf_matrix[0:1]
    job_vectors = tfidf_matrix[1:]

    similarities = cosine_similarity(user_vector, job_vectors).flatten()

    user_skills = profile.skills_list()
    results = []

    for job, sim_score in zip(jobs, similarities):
        job_skills = job.skills_list()
        matched, missing = compute_skill_overlap(user_skills, job_skills)

        # Boost score slightly based on skill overlap ratio, then clip to 100
        skill_ratio = (len(matched) / len(job_skills)) if job_skills else 0
        combined_score = (0.7 * sim_score) + (0.3 * skill_ratio)
        percentage = round(min(combined_score, 1.0) * 100, 1)

        # Build explanation text
        reason_parts = []
        if matched:
            reason_parts.append(
                f"Matches {len(matched)} of your skills: {', '.join(matched[:6])}"
                + ("..." if len(matched) > 6 else "")
            )
        if profile.preferred_role and profile.preferred_role.strip().lower() in (job.title or "").lower():
            reason_parts.append(f"Matches your preferred role '{profile.preferred_role}'")
        if profile.experience_years is not None and job.min_experience is not None:
            if profile.experience_years >= job.min_experience:
                reason_parts.append("Your experience meets the job's requirement")
        if profile.location and job.location and profile.location.strip().lower() == job.location.strip().lower():
            reason_parts.append(f"Located in your preferred location ({job.location})")

        if not reason_parts:
            reason_parts.append("Related to your overall profile and interests")

        reason = ". ".join(reason_parts) + "."

        results.append({
            "job": job,
            "score": percentage,
            "matched_skills": matched,
            "missing_skills": missing,
            "reason": reason,
        })

    results.sort(key=lambda r: r["score"], reverse=True)

    if top_n:
        results = results[:top_n]

    return results
