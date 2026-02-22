import re

SKILL_KEYWORDS = {
    "python",
    "flask",
    "django",
    "fastapi",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "pandas",
    "numpy",
    "scikit-learn",
    "machine learning",
    "data analysis",
    "java",
    "spring",
    "javascript",
    "typescript",
    "react",
    "node.js",
    "html",
    "css",
    "git",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "rest api",
    "microservices",
}


def extract_skills(text):
    if not text:
        return []

    found = set()
    lowered = text.lower()

    for skill in SKILL_KEYWORDS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, lowered):
            found.add(skill)

    return sorted(found)


def parse_skills(skills_value):
    if not skills_value:
        return []

    if isinstance(skills_value, list):
        return sorted({s.strip().lower() for s in skills_value if str(s).strip()})

    return sorted({s.strip().lower() for s in str(skills_value).split(",") if s.strip()})
