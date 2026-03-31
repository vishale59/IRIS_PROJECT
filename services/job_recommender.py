"""
IRIS Job Recommendation Engine
Ranks jobs based on resume-to-JD similarity.
"""
from services.ats_analyzer import analyze_resume, extract_skills_from_text, clean_text

JOB_ROLE_SKILL_MAP = {
    "Backend Developer": {
        "skills": {"python", "java", "sql", "flask", "django", "fastapi", "api", "nodejs", "spring"},
        "icon": "fa-server",
    },
    "Machine Learning Engineer": {
        "skills": {"python", "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "nlp"},
        "icon": "fa-brain",
    },
    "Data Scientist": {
        "skills": {"python", "sql", "pandas", "numpy", "data science", "statistics", "machine learning", "tableau", "power bi"},
        "icon": "fa-chart-line",
    },
    "Data Analyst": {
        "skills": {"sql", "excel", "power bi", "tableau", "data analysis", "data visualization", "python"},
        "icon": "fa-chart-column",
    },
    "Database Administrator": {
        "skills": {"sql", "mysql", "postgresql", "oracle", "mongodb", "redis"},
        "icon": "fa-database",
    },
    "Frontend Developer": {
        "skills": {"html", "css", "javascript", "typescript", "react", "angular", "vue", "bootstrap", "tailwind"},
        "icon": "fa-code",
    },
    "UI Designer": {
        "skills": {"html", "css", "figma", "sass", "less", "bootstrap", "tailwind"},
        "icon": "fa-palette",
    },
    "Software Engineer": {
        "skills": {"java", "python", "javascript", "c++", "c#", "go", "git", "api"},
        "icon": "fa-laptop-code",
    },
    "Android Developer": {
        "skills": {"java", "kotlin", "android", "android studio", "mobile development"},
        "icon": "fa-mobile-screen",
    },
    "Full Stack Developer": {
        "skills": {"html", "css", "javascript", "typescript", "react", "nodejs", "python", "sql", "api"},
        "icon": "fa-layer-group",
    },
    "DevOps Engineer": {
        "skills": {"docker", "kubernetes", "aws", "azure", "gcp", "terraform", "jenkins", "linux", "ci/cd"},
        "icon": "fa-gears",
    },
    "Business Analyst": {
        "skills": {"excel", "sql", "tableau", "power bi", "data analysis", "communication", "presentation"},
        "icon": "fa-briefcase",
    },
}


def recommend_jobs(resume_text: str, jobs: list, top_n: int = 6) -> list[dict]:
    """
    Score every job against the resume and return top_n ranked results.
    Each item: { job, score, matched_skills, missing_skills }
    """
    if not resume_text or not jobs:
        return []

    resume_clean = clean_text(resume_text)
    resume_skills = extract_skills_from_text(resume_clean)
    scored = []

    for job in jobs:
        if not getattr(job, "is_active", True):
            continue

        jd_text = (
            f"{job.title} {job.description or ''} "
            f"{getattr(job, 'skills_required', '') or ''} "
            f"{getattr(job, 'requirements', '') or ''}"
        )
        result = analyze_resume(resume_text, jd_text)
        scored.append({
            "job": job,
            "score": result["ats_score"],
            "matched_skills": result["matched_skills"][:8],
            "missing_skills": result["missing_skills"][:5],
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]


def get_skill_gap(resume_text: str, job) -> dict:
    """Detailed skill gap analysis for a specific job."""
    jd_text = (
        f"{job.title} {job.description or ''} "
        f"{getattr(job, 'skills_required', '') or ''} "
        f"{getattr(job, 'requirements', '') or ''}"
    )
    return analyze_resume(resume_text, jd_text)


def suggest_jobs(skills: list[str]) -> dict:
    """
    Suggest primary and alternative job roles from extracted skills.
    Returns:
        {
            "recommended": [role_name, ...],
            "alternative": [role_name, ...],
            "primary": [role_name, ...],  # compatibility alias
            "details": [{"role": ..., "score": ..., "matched_skills": [...], "icon": ...}, ...],
            "best_match": "Role Name" | None,
        }
    """
    if not skills:
        return {
            "recommended": [],
            "alternative": [],
            "primary": [],
            "details": [],
            "best_match": None,
        }

    normalized_skills = {skill.strip().lower() for skill in skills if skill and skill.strip()}
    ranked_roles = []

    for role, config in JOB_ROLE_SKILL_MAP.items():
        matched_skills = sorted(normalized_skills.intersection(config["skills"]))
        if not matched_skills:
            continue

        role_skill_count = len(config["skills"])
        coverage = len(matched_skills) / role_skill_count
        skill_weight = len(matched_skills) * 10
        score = round((coverage * 100) + skill_weight, 1)

        ranked_roles.append({
            "role": role,
            "score": score,
            "matched_skills": matched_skills,
            "icon": config["icon"],
        })

    ranked_roles.sort(key=lambda item: (-item["score"], item["role"]))

    ordered_roles = [item["role"] for item in ranked_roles]
    primary = ordered_roles[:3]
    alternative = ordered_roles[3:7]

    recommended = list(dict.fromkeys(primary))
    alternative = [role for role in dict.fromkeys(alternative) if role not in recommended]

    return {
        "recommended": recommended,
        "alternative": alternative,
        "primary": recommended,
        "details": ranked_roles,
        "best_match": recommended[0] if recommended else None,
    }


def suggest_jobs_from_resume_text(resume_text: str) -> dict:
    """Convenience wrapper to extract skills first, then suggest roles."""
    if not resume_text:
        return {
            "recommended": [],
            "alternative": [],
            "primary": [],
            "details": [],
            "best_match": None,
        }

    extracted_skills = extract_skills_from_text(clean_text(resume_text))
    return suggest_jobs(extracted_skills)
