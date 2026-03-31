"""
IRIS ATS Analyzer Service
Combines keyword matching + TF-IDF semantic similarity for robust scoring.
No spaCy model download required — pure scikit-learn approach.
"""
import re
import json
import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ── Master skill taxonomy ────────────────────────────────────────────────────
SKILL_TAXONOMY = {
    "programming": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
        "kotlin", "swift", "ruby", "php", "scala", "r", "matlab", "perl",
        "dart", "lua", "shell", "bash", "powershell",
    ],
    "web": [
        "html", "css", "react", "angular", "vue", "nextjs", "nuxtjs", "svelte",
        "jquery", "bootstrap", "tailwind", "sass", "less", "webpack", "vite",
        "nodejs", "express", "fastapi", "django", "flask", "spring", "laravel",
        "graphql", "rest", "api", "soap", "websocket",
    ],
    "data": [
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "oracle", "cassandra", "dynamodb", "firebase",
        "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
        "tableau", "power bi", "excel", "data analysis", "data visualization",
    ],
    "ml_ai": [
        "machine learning", "deep learning", "nlp", "computer vision",
        "tensorflow", "pytorch", "keras", "scikit-learn", "huggingface",
        "llm", "gpt", "bert", "transformer", "neural network",
        "data science", "statistics", "regression", "classification",
        "clustering", "reinforcement learning", "feature engineering",
    ],
    "devops": [
        "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ansible",
        "jenkins", "github actions", "ci/cd", "linux", "nginx", "apache",
        "monitoring", "prometheus", "grafana", "elk stack", "microservices",
    ],
    "soft": [
        "leadership", "communication", "teamwork", "problem solving",
        "agile", "scrum", "kanban", "project management", "critical thinking",
        "time management", "collaboration", "mentoring", "presentation",
    ],
    "tools": [
        "git", "github", "gitlab", "jira", "confluence", "slack", "figma",
        "postman", "vs code", "intellij", "eclipse", "xcode", "android studio",
    ],
    "mobile": [
        "android", "ios", "react native", "flutter", "ionic", "xamarin",
        "mobile development", "app development",
    ],
    "security": [
        "cybersecurity", "ethical hacking", "penetration testing", "owasp",
        "ssl", "tls", "encryption", "oauth", "jwt", "authentication",
    ],
}

ALL_SKILLS = [s for skills in SKILL_TAXONOMY.values() for s in skills]


# ── Text utilities ────────────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^\w\s\+\#\.]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_skills_from_text(text: str) -> list[str]:
    """Return deduplicated list of skills found in text."""
    text_lower = text.lower()
    found = []
    for skill in ALL_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)
    return list(dict.fromkeys(found))  # preserve order, dedupe


# ── Scoring ───────────────────────────────────────────────────────────────────
def keyword_score(resume_skills: list[str], jd_skills: list[str]) -> tuple[float, list, list]:
    """Hard keyword overlap score."""
    if not jd_skills:
        return 50.0, resume_skills, []
    matched = [s for s in jd_skills if s in resume_skills]
    missing = [s for s in jd_skills if s not in resume_skills]
    score = (len(matched) / len(jd_skills)) * 100
    return round(score, 1), matched, missing


def semantic_score(resume_text: str, jd_text: str) -> float:
    """TF-IDF cosine similarity between resume and JD."""
    try:
        vec = TfidfVectorizer(stop_words='english', max_features=5000)
        tfidf = vec.fit_transform([resume_text, jd_text])
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return round(float(sim) * 100, 1)
    except Exception:
        return 0.0


def section_bonus(resume_text: str) -> float:
    """Award bonus points for having key resume sections."""
    sections = {
        'education': 5,
        'experience': 5,
        'skills': 5,
        'projects': 3,
        'certifications': 2,
        'summary': 2,
        'achievements': 3,
    }
    text_lower = resume_text.lower()
    bonus = 0.0
    for section, pts in sections.items():
        if section in text_lower:
            bonus += pts
    return min(bonus, 20.0)  # cap at 20


def generate_suggestions(matched: list, missing: list, resume_text: str, semantic: float) -> list[str]:
    suggestions = []

    if len(missing) > 0:
        top_missing = missing[:5]
        suggestions.append(
            f"Add these in-demand skills to your resume: {', '.join(top_missing)}."
        )

    if semantic < 40:
        suggestions.append(
            "Tailor your resume summary/objective to mirror the job description language."
        )

    resume_lower = resume_text.lower()
    if 'project' not in resume_lower and 'portfolio' not in resume_lower:
        suggestions.append(
            "Include a Projects section with 2–3 relevant projects to demonstrate hands-on experience."
        )

    if 'certification' not in resume_lower and 'certified' not in resume_lower:
        suggestions.append(
            "Add relevant certifications (AWS, Google, Microsoft, etc.) to boost credibility."
        )

    quantifiers = re.findall(r'\d+\s*%|\d+\s+\w+|\$\d+', resume_text)
    if len(quantifiers) < 3:
        suggestions.append(
            "Quantify your achievements — use numbers, percentages, and metrics (e.g., 'Reduced load time by 40%')."
        )

    if len(resume_text.split()) < 300:
        suggestions.append(
            "Your resume appears thin. Expand experience descriptions with specific responsibilities and outcomes."
        )

    if not suggestions:
        suggestions.append("Your resume is well-aligned. Keep it concise and ATS-friendly.")

    return suggestions


# ── Main entry point ──────────────────────────────────────────────────────────
def analyze_resume(resume_text: str, job_description: str = "") -> dict:
    """
    Full ATS analysis.
    Returns a dict with score, matched_skills, missing_skills, suggestions.
    """
    if not resume_text or len(resume_text.strip()) < 50:
        return {
            "ats_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "suggestions": ["Could not extract meaningful content from the resume."],
            "semantic_score": 0,
            "keyword_score": 0,
            "skill_categories": {},
        }

    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(job_description) if job_description else ""

    resume_skills = extract_skills_from_text(resume_clean)

    if jd_clean:
        jd_skills = extract_skills_from_text(jd_clean)
    else:
        # Generic scoring against full taxonomy when no JD provided
        jd_skills = ALL_SKILLS[:60]

    kw_score, matched, missing = keyword_score(resume_skills, jd_skills)
    sem_score = semantic_score(resume_clean, jd_clean) if jd_clean else 50.0
    bonus = section_bonus(resume_text)

    # Weighted final score: 50% keyword, 30% semantic, 20% section bonus
    if jd_clean:
        final = (kw_score * 0.50) + (sem_score * 0.30) + (bonus * 1.0)
    else:
        # No JD: score based on resume completeness only
        completeness = min((len(resume_skills) / 15) * 60, 60)
        final = completeness + bonus

    final = min(round(final, 1), 100.0)

    # Categorise matched skills
    skill_categories = {}
    for cat, skills in SKILL_TAXONOMY.items():
        cat_matched = [s for s in matched if s in skills]
        if cat_matched:
            skill_categories[cat] = cat_matched

    suggestions = generate_suggestions(matched, missing, resume_text, sem_score)

    return {
        "ats_score": final,
        "matched_skills": matched,
        "missing_skills": missing[:20],
        "suggestions": suggestions,
        "semantic_score": sem_score,
        "keyword_score": kw_score,
        "skill_categories": skill_categories,
    }


def compute_job_match(resume_text: str, job: object) -> float:
    """Quick match score between a resume and a Job model instance."""
    jd_text = (
        f"{job.title} {job.description or ''} "
        f"{getattr(job, 'skills_required', '') or ''} "
        f"{getattr(job, 'requirements', '') or ''}"
    )
    result = analyze_resume(resume_text, jd_text)
    return result["ats_score"]
