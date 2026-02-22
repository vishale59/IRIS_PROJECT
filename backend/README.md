# IRIS - Intelligent Resume Insight System

Production-ready Flask backend for resume analysis and smart job matching using TF-IDF + cosine similarity.

## Tech Stack
- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- MySQL (PyMySQL driver)
- PyPDF2
- scikit-learn (TF-IDF + Cosine Similarity)
- Flask-CORS
- python-dotenv
- logging

## Project Structure
```
backend/
  app/
    __init__.py
    models/
      user_model.py
      job_model.py
      resume_model.py
      application_model.py
    routes/
      auth_routes.py
      job_routes.py
      resume_routes.py
      application_routes.py
      dashboard_routes.py
    services/
      matching_service.py
    utils/
      file_handler.py
      skill_extractor.py
    middleware/
      role_required.py
  config.py
  run.py
  requirements.txt
  .env.example
```

## Database Setup
Run this in MySQL:
```sql
CREATE DATABASE iris_db;
```

## Environment Setup
1. Create virtual environment and activate it.
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Create `.env` from `.env.example` and update secrets.

Example `.env`:
```env
FLASK_DEBUG=True
DATABASE_URL=mysql+pymysql://root:root123@localhost:3306/iris_db
JWT_SECRET_KEY=replace-with-a-strong-secret
MAX_CONTENT_LENGTH=5242880
UPLOAD_FOLDER=uploads/resumes
LOG_FILE=logs/app.log
```

## Run Server
```bash
python run.py
```

Server starts at `http://localhost:5000`.

## API Overview
Base path: `/api`

### 1. Register
`POST /api/auth/register`

Request:
```json
{
  "name": "Employer One",
  "email": "employer@iris.com",
  "password": "StrongPass@123",
  "role": "employer"
}
```

Response:
```json
{
  "message": "User registered successfully"
}
```

### 2. Login
`POST /api/auth/login`

Request:
```json
{
  "email": "employer@iris.com",
  "password": "StrongPass@123"
}
```

Response:
```json
{
  "message": "Login successful",
  "access_token": "<JWT_TOKEN>",
  "user": {
    "id": 2,
    "name": "Employer One",
    "email": "employer@iris.com",
    "role": "employer"
  }
}
```

### 3. Create Job (Employer)
`POST /api/jobs`

Headers:
`Authorization: Bearer <JWT_TOKEN>`

Request:
```json
{
  "title": "Python Backend Developer",
  "description": "Build Flask APIs and optimize SQL queries",
  "location": "Bangalore",
  "required_skills": ["python", "flask", "mysql", "sql"]
}
```

### 4. Upload Resume (Jobseeker)
`POST /api/resumes/upload` (form-data)

Fields:
- `file`: PDF

### 5. Apply to Job (Jobseeker)
`POST /api/applications`

Request:
```json
{
  "job_id": 1
}
```

Response:
```json
{
  "message": "Applied successfully",
  "application_id": 5,
  "match_score": 78.42,
  "matched_skills": ["flask", "python"],
  "missing_skills": ["mysql", "sql"]
}
```

### 6. Employer Views Applicants Sorted by Match
`GET /api/jobs/<job_id>/applicants`

### 7. Employer Updates Application Status
`PATCH /api/applications/<application_id>/status`

Request:
```json
{
  "status": "Shortlisted"
}
```

### 8. Admin Dashboard Summary
`GET /api/dashboard`

Returns:
- `total_users`
- `total_jobs`
- `total_applications`
- `average_match_score`

## Logging
The system logs key events to `logs/app.log`:
- Login attempts
- Job creation
- Resume upload
- Application creation

## Notes
- Passwords are hashed with Werkzeug.
- Credentials are loaded from environment variables.
- Duplicate job applications are prevented.
- Matching uses only TF-IDF + cosine similarity (no deep learning).

## Swagger / OpenAPI
- Swagger UI: /docs (or /docs/)
- OpenAPI spec endpoint: /openapi.json`n- Generated OpenAPI file: openapi.json`n
## Postman Collection
- Import postman_collection.json into Postman.
- Set collection variables: aseUrl, 	oken, and IDs.

