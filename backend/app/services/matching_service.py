from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_match(resume_text, job_description, resume_skills, required_skills):
    base_resume_text = resume_text or ""
    base_job_text = job_description or ""

    tfidf_score = 0.0
    if base_resume_text.strip() and base_job_text.strip():
        vectorizer = TfidfVectorizer(stop_words="english")
        vectors = vectorizer.fit_transform([base_resume_text, base_job_text])
        tfidf_score = float(cosine_similarity(vectors[0:1], vectors[1:2])[0][0]) * 100

    resume_set = {s.strip().lower() for s in (resume_skills or []) if str(s).strip()}
    required_set = {s.strip().lower() for s in (required_skills or []) if str(s).strip()}

    matched_skills = sorted(resume_set.intersection(required_set))
    missing_skills = sorted(required_set.difference(resume_set))

    skill_score = 0.0
    if required_set:
        skill_score = (len(matched_skills) / len(required_set)) * 100

    combined_score = (0.7 * tfidf_score) + (0.3 * skill_score)

    return {
        "match_score": round(combined_score, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }
