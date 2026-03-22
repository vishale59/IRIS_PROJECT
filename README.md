# IRIS — AI-Powered Job Portal

A full-stack Flask web application with AI resume analysis, smart categorization,
email notifications, and a modern Poppins-based UI.

---

## 🚀 Quick Start

### 1. Clone / unzip the project
```bash
cd IRIS
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your SMTP credentials (optional — app works without email)
```

### 5. Run the app
```bash
python app.py
```

Visit **http://localhost:5000**

---

## 🔑 Demo Accounts (auto-created on first run)

| Role     | Email               | Password      |
|----------|---------------------|---------------|
| Admin    | admin@iris.com      | Admin@1234    |
| Employer | employer@iris.com   | Employer@1234 |
| Jobseeker| Register new account| —             |

---

## 📁 Project Structure

```
IRIS/
├── app.py                  # App factory & seed data
├── config.py               # Dev / Prod configuration
├── models.py               # SQLAlchemy models
├── requirements.txt
├── .env.example
├── routes/
│   ├── auth.py             # Login, Register, Logout
│   ├── user.py             # Jobseeker: dashboard, resume, jobs, apply
│   ├── employer.py         # Employer: post jobs, manage applications
│   └── admin.py            # Admin: users, jobs, applications overview
├── services/
│   ├── ats_analyzer.py     # ATS keyword + TF-IDF scoring engine
│   ├── categorizer.py      # Smart degree + skill categorization ← NEW
│   ├── job_recommender.py  # Resume-to-job matching
│   ├── mailer.py           # SMTP email notifications
│   └── resume_parser.py    # PDF / DOCX text extraction
├── templates/
│   ├── base.html           # Sidebar layout shell
│   ├── auth/               # Login, Register
│   ├── user/               # Dashboard, Resume, Jobs, Applications, Profile
│   ├── employer/           # Dashboard, Post Job, Applications
│   ├── admin/              # Dashboard, Users, Jobs, Applications
│   └── errors/             # 404, 500, 413
└── static/
    ├── css/style.css       # Full design system (Poppins, #4f46e5)
    └── js/main.js          # Sidebar, drag-drop, alerts, progress bars
```

---

## ✨ Features

### Phase 1 — Clean Structure
- Invalid folders removed
- All imports and paths verified
- No duplicate files

### Phase 2 — Modern UI
- **Font:** Poppins
- **Primary color:** #4f46e5 (Indigo)
- **Background:** #f9fafb
- Sidebar navigation with role-based links
- Stat cards, job cards, modern tables
- Responsive (mobile-friendly)
- Hover animations & transitions
- Font Awesome icons throughout

### Phase 3 — Smart Categorization
```
Degree:  BCA → IT | BCom → Finance | BSc → Science | BA → Arts | MBA → Finance
Skills:  python/java → IT | accounting/tally → Finance | biology → Science

Logic:
  Same result  → return one category   (e.g. "IT")
  Different    → combine               (e.g. "IT + Finance")
```
- Runs on resume upload AND profile save
- Stored in `users.category` and `resumes.detected_category`
- Shown as colored badge in dashboard, job listings, admin

### Phase 4 — Email + Status System
**Emails sent on:**
- Job application submitted (to applicant)
- New application received (to employer)
- Application status changed (to applicant)

**Status flow:**
```
Applied → Reviewed → Selected → Rejected
                  ↘ Hired
```
- Employer selects status from dropdown in job applications view
- Applicant sees live colored status badge in My Applications

### Phase 5 — Reliability
- 404, 500, 413 error pages
- Form validation (required fields, email format, password length)
- Graceful email fallback (works without SMTP configured)
- ATS scoring with no external NLP model (pure scikit-learn)

---

## 📧 Email Setup (Gmail)

1. Enable 2FA on your Gmail account
2. Generate an **App Password**: Google Account → Security → App Passwords
3. Add to `.env`:
```
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx
MAIL_DEFAULT_SENDER=IRIS <your@gmail.com>
```

---

## 🧪 Full Flow

```
Register (jobseeker)
  ↓
Login → Dashboard
  ↓
Upload Resume (select degree → auto-categorized)
  ↓
View ATS Score + Skill Analysis
  ↓
Browse Jobs (filtered by category, type, location)
  ↓
Apply to Job (with resume + cover letter)
  ↓
Email sent to applicant + employer
  ↓
Employer reviews → updates status (Applied/Reviewed/Selected/Rejected)
  ↓
Email sent to applicant with new status
  ↓
Applicant sees colored status badge in My Applications
```

---

## 🛠 Tech Stack

- **Backend:** Python 3.11+, Flask 3.0
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **ORM:** Flask-SQLAlchemy
- **Auth:** Flask-Login + Werkzeug password hashing
- **Email:** Flask-Mail (SMTP)
- **AI / NLP:** scikit-learn TF-IDF + cosine similarity
- **PDF parsing:** PyMuPDF (fitz) / pdfminer fallback
- **DOCX:** python-docx
- **Frontend:** Vanilla HTML/CSS/JS + Poppins + Font Awesome

---

## 🎨 UI Design System (v2 — Premium SaaS Redesign)

### Color Tokens
| Token | Value | Usage |
|-------|-------|-------|
| `--clr-primary` | `#6366f1` | Buttons, links, active states |
| `--clr-secondary` | `#8b5cf6` | Gradients, accents |
| `--clr-accent` | `#06b6d4` | Highlights, cyan accents |
| `--bg-base` | `#0f0f1a` | Page background |
| `--bg-card` | `#1e1e32` | Card surfaces |

### Typography
- **Display font:** Plus Jakarta Sans (headings, stats, brand)
- **Body font:** Inter (all other text)

### Key Components
| Component | Class | Notes |
|-----------|-------|-------|
| Card | `.card` | Glass overlay, border, hover lift |
| Stat Card | `.stat-card` | Color variants: `.blue .green .orange .purple .cyan .red` |
| Button | `.btn` | Variants: `btn-primary btn-secondary btn-outline btn-danger btn-success btn-ghost` |
| Badge | `.badge` | `badge-primary badge-success badge-warning badge-danger badge-info badge-muted` |
| Status Pill | `.status-pill` | `sp-applied sp-reviewed sp-selected sp-rejected sp-hired` |
| Category Badge | `.cat-badge` | Gradient indigo, for career category display |
| Alert | `.alert` | `alert-success alert-danger alert-warning alert-info` |
| Progress Bar | `.progress-track` + `.progress-fill[data-pct]` | Auto-animates on scroll |
| Score Ring | `[data-score-ring="N"]` | SVG circular progress, auto-colored |
| Upload Zone | `#upload-zone` + `#file-input` | Drag & drop with visual feedback |
| Chip/Tag | `.chip` | `chip-primary chip-success chip-danger` |

### Animations
- `anim-fade-up` — fade + translateY on load
- `anim-scale` — scale from 0.95 on load
- `.d1`–`.d5` — staggered delay classes
- `.scroll-reveal` — IntersectionObserver fade-in on scroll
- `[data-count]` — animated counter on viewport entry
