"""
IRIS Smart Categorization Service
Degree-based + Skill-based auto-categorization
"""

DEGREE_MAP = {
    'bca':        'IT',
    'mca':        'IT',
    'b.tech':     'IT',
    'm.tech':     'IT',
    'bsc it':     'IT',
    'msc it':     'IT',
    'bcom':       'Finance',
    'b.com':      'Finance',
    'mcom':       'Finance',
    'm.com':      'Finance',
    'bba':        'Finance',
    'mba':        'Finance',
    'bsc':        'Science',
    'b.sc':       'Science',
    'msc':        'Science',
    'm.sc':       'Science',
    'ba':         'Arts',
    'b.a':        'Arts',
    'ma':         'Arts',
    'm.a':        'Arts',
    'llb':        'Law',
    'mbbs':       'Medical',
    'bpharm':     'Medical',
    'pharm':      'Medical',
    'bdes':       'Design',
    'b.des':      'Design',
    'barch':      'Engineering',
    'b.arch':     'Engineering',
}

SKILL_KEYWORDS = {
    'IT': [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
        'react', 'angular', 'vue', 'nodejs', 'flask', 'django', 'spring',
        'html', 'css', 'php', 'ruby', 'swift', 'kotlin', 'android', 'ios',
        'sql', 'mysql', 'mongodb', 'postgresql', 'redis', 'docker', 'kubernetes',
        'aws', 'azure', 'gcp', 'machine learning', 'deep learning', 'nlp',
        'tensorflow', 'pytorch', 'data science', 'programming', 'software',
        'developer', 'engineer', 'backend', 'frontend', 'fullstack', 'devops',
        'git', 'api', 'microservices', 'cloud', 'linux', 'networking',
    ],
    'Finance': [
        'accounting', 'finance', 'taxation', 'audit', 'tally', 'gst',
        'financial analysis', 'balance sheet', 'budgeting', 'forecasting',
        'investment', 'banking', 'insurance', 'risk management', 'compliance',
        'excel', 'financial modeling', 'valuation', 'equity', 'portfolio',
        'payroll', 'accounts', 'bookkeeping', 'cost accounting', 'sap fico',
        'chartered', 'ca', 'cpa', 'cfa', 'acca',
    ],
    'Science': [
        'biology', 'chemistry', 'physics', 'laboratory', 'research',
        'biochemistry', 'microbiology', 'genetics', 'ecology', 'biotechnology',
        'clinical', 'pharmaceutical', 'spectroscopy', 'chromatography',
        'data analysis', 'statistics', 'r programming', 'matlab', 'spss',
        'environmental', 'geology', 'astronomy', 'zoology', 'botany',
    ],
    'Arts': [
        'communication', 'media', 'journalism', 'content', 'writing',
        'social media', 'marketing', 'advertising', 'public relations',
        'graphic design', 'photography', 'videography', 'editing',
        'teaching', 'education', 'counseling', 'human resources', 'hr',
        'psychology', 'sociology', 'literature', 'history', 'philosophy',
        'political science', 'event management', 'hospitality',
    ],
    'Design': [
        'figma', 'sketch', 'adobe', 'photoshop', 'illustrator', 'indesign',
        'ui', 'ux', 'user experience', 'user interface', 'wireframe',
        'prototype', 'typography', 'branding', 'logo', 'animation',
        'motion graphics', 'video editing', 'premiere', 'after effects',
        '3d', 'autocad', 'solidworks',
    ],
    'Medical': [
        'clinical', 'patient', 'diagnosis', 'treatment', 'surgery',
        'medicine', 'pharmacy', 'nursing', 'healthcare', 'hospital',
        'medical', 'anatomy', 'physiology', 'pathology', 'radiology',
        'ophthalmology', 'cardiology', 'neurology', 'pediatrics',
    ],
    'Law': [
        'legal', 'law', 'litigation', 'contracts', 'compliance', 'regulatory',
        'corporate law', 'intellectual property', 'arbitration', 'mediation',
        'criminal law', 'civil law', 'constitutional', 'court',
    ],
}


def detect_degree_category(text: str) -> str | None:
    """Detect category based on degree keywords in text."""
    text_lower = text.lower()
    for degree, category in DEGREE_MAP.items():
        if degree in text_lower:
            return category
    return None


def detect_skill_category(text: str) -> str | None:
    """Detect category based on skill keyword frequency."""
    text_lower = text.lower()
    scores = {}
    for category, keywords in SKILL_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[category] = score
    if not scores:
        return None
    return max(scores, key=scores.get)


def final_category(degree: str, resume_text: str) -> str:
    """
    Combine degree-based and skill-based detection.
    Returns final category string.
    """
    deg_cat   = detect_degree_category(degree) if degree else None
    skill_cat = detect_skill_category(resume_text) if resume_text else None

    if deg_cat and skill_cat:
        if deg_cat == skill_cat:
            return deg_cat
        return f"{deg_cat} + {skill_cat}"
    if deg_cat:
        return deg_cat
    if skill_cat:
        return skill_cat
    return 'General'
