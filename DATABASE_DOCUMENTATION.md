# IRIS Project - Database Documentation

## 📊 Overview
The IRIS (AI-Powered Job Portal) database consists of 4 main tables managing users, resumes, job postings, and job applications with role-based access control.

---

## 🗄️ Database Tables

### 1. USERS Table
Stores all user accounts with role-based authentication and profile information.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| full_name | VARCHAR(120) | NOT NULL | User's full name |
| email | VARCHAR(120) | UNIQUE, NOT NULL | User's email address |
| password_hash | VARCHAR(256) | NOT NULL | Hashed password (Werkzeug security) |
| role | VARCHAR(20) | DEFAULT: 'jobseeker' | User role: jobseeker, employer, admin |
| phone | VARCHAR(20) | NULLABLE | User's phone number |
| location | VARCHAR(100) | NULLABLE | User's location |
| bio | TEXT | NULLABLE | User biography/profile description |
| degree | VARCHAR(100) | NULLABLE | Educational degree (NEW) |
| category | VARCHAR(100) | NULLABLE | Auto-detected professional category |
| profile_pic | VARCHAR(200) | DEFAULT: 'default.png' | Profile picture filename |
| is_active | BOOLEAN | DEFAULT: True | Account activation status |
| created_at | DATETIME | DEFAULT: UTC NOW | Account creation timestamp |

**Key Relationships:**
- 1 User → Many Resumes (cascade delete)
- 1 User → Many Applications (cascade delete)
- 1 User (employer) → Many Jobs (cascade delete)

**Indexes:** email (unique), created_at

---

### 2. RESUMES Table
Stores resume files and AI-powered analysis results.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique resume identifier |
| user_id | INTEGER | FOREIGN KEY → users.id, NOT NULL | Owner of the resume |
| filename | VARCHAR(200) | NOT NULL | Stored filename on server |
| original_name | VARCHAR(200) | NULLABLE | Original uploaded filename |
| file_path | VARCHAR(500) | NULLABLE | Full file path in uploads folder |
| extracted_text | TEXT | NULLABLE | Full text extracted from PDF/DOCX |
| ats_score | FLOAT | DEFAULT: 0.0 | ATS (Applicant Tracking System) score (0-100) |
| matched_skills | TEXT | NULLABLE | JSON array of matched skills |
| missing_skills | TEXT | NULLABLE | JSON array of missing skills |
| suggestions | TEXT | NULLABLE | JSON array of improvement suggestions |
| detected_category | VARCHAR(100) | NULLABLE | AI-detected job category |
| uploaded_at | DATETIME | DEFAULT: UTC NOW | Upload timestamp |
| is_primary | BOOLEAN | DEFAULT: False | Whether this is primary resume |

**Key Relationships:**
- Many Resumes → 1 User (foreign key)
- 1 Resume → Many Applications (cascade delete)

**Indexes:** user_id, uploaded_at, ats_score

---

### 3. JOBS Table
Stores job postings from employers.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique job identifier |
| employer_id | INTEGER | FOREIGN KEY → users.id, NOT NULL | Employer who posted the job |
| title | VARCHAR(200) | NOT NULL | Job title (e.g., "Senior Developer") |
| company | VARCHAR(200) | NOT NULL | Company name |
| location | VARCHAR(100) | NULLABLE | Job location |
| job_type | VARCHAR(50) | DEFAULT: 'Full-time' | Full-time, Part-time, Contract, etc. |
| salary_min | INTEGER | NULLABLE | Minimum salary in base currency |
| salary_max | INTEGER | NULLABLE | Maximum salary in base currency |
| description | TEXT | NOT NULL | Full job description |
| requirements | TEXT | NULLABLE | Job requirements text |
| skills_required | TEXT | NULLABLE | Comma-separated required skills |
| experience_level | VARCHAR(50) | DEFAULT: 'Entry' | Entry, Mid, Senior, Executive |
| category | VARCHAR(100) | NULLABLE | Job category (e.g., IT, HR, Finance) |
| is_active | BOOLEAN | DEFAULT: True | Job posting active status |
| created_at | DATETIME | DEFAULT: UTC NOW | Job posting timestamp |
| deadline | DATETIME | NULLABLE | Application deadline |

**Key Relationships:**
- Many Jobs → 1 User (employer) (foreign key)
- 1 Job → Many Applications (cascade delete)

**Indexes:** employer_id, is_active, created_at, deadline

---

### 4. APPLICATIONS Table
Stores job applications from users with ATS matching scores.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique application identifier |
| user_id | INTEGER | FOREIGN KEY → users.id, NOT NULL | Applicant user ID |
| job_id | INTEGER | FOREIGN KEY → jobs.id, NOT NULL | Applied job ID |
| resume_id | INTEGER | FOREIGN KEY → resumes.id, NULLABLE | Primary resume used in application |
| cover_letter | TEXT | NULLABLE | Application cover letter |
| status | VARCHAR(30) | DEFAULT: 'Applied' | Applied, Reviewed, Shortlisted, Selected, Rejected, Hired |
| ats_match_score | FLOAT | DEFAULT: 0.0 | ATS match percentage (0-100) |
| applied_at | DATETIME | DEFAULT: UTC NOW | Application submission timestamp |
| updated_at | DATETIME | DEFAULT: UTC NOW, AUTO UPDATE | Last status update timestamp |
| employer_notes | TEXT | NULLABLE | Employer's internal notes on candidate |

**Key Relationships:**
- Many Applications → 1 User (applicant) (foreign key)
- Many Applications → 1 Job (foreign key)
- Many Applications → 1 Resume (foreign key)

**Indexes:** user_id, job_id, resume_id, status, applied_at, ats_match_score

---

## 📈 Entity-Relationship Diagram (ERD)

```
                            ┌─────────────────┐
                            │     USERS       │
                            ├─────────────────┤
                            │ id (PK)         │
                            │ full_name       │
                            │ email (UQ)      │
                            │ password_hash   │
                            │ role            │
                            │ phone           │
                            │ location        │
                            │ bio             │
                            │ degree          │
                            │ category        │
                            │ profile_pic     │
                            │ is_active       │
                            │ created_at      │
                            └────────┬────────┘
                      ●●●(employer)●●●(jobseeker)
                     /        │              \
         (employer posts)     │        (jobseeker applies)
                 /            │                \
    ┌───────────────────┐     │    ┌─────────────────────┐
    │       JOBS        │     │    │  APPLICATIONS       │
    ├───────────────────┤     │    ├─────────────────────┤
    │ id (PK)           │     │    │ id (PK)             │
    │ employer_id (FK)──┼─────┘    │ user_id (FK)────────┼──┐
    │ title             │          │ job_id (FK) ────────┼─┐│
    │ company           │          │   (references JOBS) │ ││
    │ location          │          │ resume_id (FK)──┐   │ ││
    │ job_type          │          │ cover_letter    │   │ ││
    │ salary_min        │          │ status          │   │ ││
    │ salary_max        │          │ ats_match_score │   │ ││
    │ description       │          │ applied_at      │   │ ││
    │ requirements      │          │ updated_at      │   │ ││
    │ skills_required   │          │ employer_notes  │   │ ││
    │ experience_level  │          └─────────────────┘   │ ││
    │ category          │                                │ ││
    │ is_active         │                                │ ││
    │ created_at        │                ┌───────────────┘ ││
    │ deadline          │                │                 ││
    └───────────────────┘    ┌──────────────────┐           ││
                             │     RESUMES      │           ││
                             ├──────────────────┤           ││
                             │ id (PK)          │           ││
                             │ user_id (FK) ────┼───────────┼┘
                             │ filename         │           │
                             │ original_name    │           │
                             │ file_path        │           │
                             │ extracted_text   │◄──────────┘
                             │ ats_score        │
                             │ matched_skills   │
                             │ missing_skills   │
                             │ suggestions      │
                             │ detected_category│
                             │ uploaded_at      │
                             │ is_primary       │
                             └──────────────────┘

Legend:
PK   = Primary Key
FK   = Foreign Key
UQ   = Unique
●●●  = One-to-Many Relationship
```

---

## 🔗 Relationship Summary

### One-to-Many Relationships

| From | To | Cardinality | Cascade | Description |
|---|---|---|---|---|
| User | Resume | 1 : N | Delete | One user can upload multiple resumes |
| User | Application | 1 : N | Delete | One user can apply to multiple jobs |
| User (Employer) | Job | 1 : N | Delete | One employer can post multiple jobs |
| Job | Application | 1 : N | Delete | One job can receive multiple applications |

### Many-to-One Relationships

| From | To | Description |
|---|---|---|
| Resume | User | Each resume belongs to one user |
| Application | User | Each application is from one user |
| Application | Job | Each application is for one job |
| Application | Resume | Each application references one resume |
| Job | User | Each job is posted by one employer |

---

## 🔐 Data Integrity Rules

1. **Referential Integrity:**
   - All foreign key constraints are enforced at the database level
   - Cascade delete enabled on all relationships to maintain data consistency

2. **Unique Constraints:**
   - Email addresses must be unique across all users
   - One primary resume per user

3. **Data Validation:**
   - Role values: `jobseeker`, `employer`, `admin`
   - Job Type: Full-time, Part-time, Contract, etc.
   - Application Status: Applied, Reviewed, Shortlisted, Selected, Rejected, Hired
   - Experience Level: Entry, Mid, Senior, Executive

4. **Timestamp Management:**
   - `created_at`: Set on record creation, never updated
   - `updated_at`: Set on creation, auto-updates on modification (Applications only)

---

## 📊 Key Queries Examples

### Count applications per job
```sql
SELECT j.id, j.title, COUNT(a.id) as application_count
FROM jobs j
LEFT JOIN applications a ON j.id = a.job_id
GROUP BY j.id, j.title;
```

### Find jobs matching user's resume skills
```sql
SELECT j.id, j.title, r.ats_score
FROM jobs j
JOIN applications a ON j.id = a.job_id
JOIN resumes r ON a.resume_id = r.id
WHERE a.user_id = ? AND a.status != 'Rejected';
```

### Employer's application statistics
```sql
SELECT 
    u.full_name,
    COUNT(CASE WHEN a.status = 'Rejected' THEN 1 END) as rejected,
    COUNT(CASE WHEN a.status = 'Shortlisted' THEN 1 END) as shortlisted,
    COUNT(CASE WHEN a.status = 'Hired' THEN 1 END) as hired
FROM users u
LEFT JOIN jobs j ON u.id = j.employer_id
LEFT JOIN applications a ON j.id = a.job_id
WHERE u.role = 'employer'
GROUP BY u.id, u.full_name;
```

---

## 🔄 Data Flow Diagram

```
1. User Registration
   └─ Create User record (role: jobseeker/employer/admin)

2. Resume Upload (Jobseeker)
   └─ Create Resume record
   └─ Extract text using resume_parser
   └─ Run ATS analyzer → ats_score, matched_skills, missing_skills
   └─ Run categorizer → detected_category

3. Job Posting (Employer)
   └─ Create Job record with requirements and skills

4. Job Application (Jobseeker)
   └─ Create Application record
   └─ Run job_recommender for matching
   └─ Assign ats_match_score

5. Application Updates
   └─ Employer updates Application status
   └─ Send email notification (if configured)
```

---

## 📝 Database Statistics

- **Total Tables:** 4
- **Total Columns:** 59
- **Foreign Keys:** 7
- **Unique Constraints:** 1 (email)
- **Default Cascade Deletes:** 4 relationships

---

**Generated:** March 2026  
**Project:** IRIS v2 Premium - AI-Powered Job Portal  
**Database:** SQLite (Development) / PostgreSQL (Production)
