# IRIS Job Portal

Flask full-stack job portal with role-based login, resume upload, ATS-style keyword analysis, employer job posting, and admin management.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create the MySQL database:
```sql
CREATE DATABASE IF NOT EXISTS iris_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

3. Set environment variables:
```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=iris_db
DB_USER=root
DB_PASSWORD=root123
SECRET_KEY=change-this-secret-key
```

4. Create tables:
```bash
python init_db.py
```

5. Run the app:
```bash
python app.py
```

## Active stack

- Backend: Flask
- ORM: Flask-SQLAlchemy
- Database: MySQL with PyMySQL
- Resume parsing: pypdf, python-docx
- ATS utilities: scikit-learn
- Mail: Flask-Mail

## Core routes

- `/auth/register`
- `/auth/login`
- `/user/dashboard`
- `/user/profile`
- `/user/resume/upload`
- `/user/jobs`
- `/user/applications`
- `/employer/dashboard`
- `/employer/jobs/new`
- `/admin/dashboard`
- `/admin/users`
- `/admin/jobs`
- `/admin/applications`
