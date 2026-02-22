SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "IRIS - Intelligent Resume Insight System API",
        "description": "API documentation for IRIS backend.",
        "version": "1.0.0",
    },
    "basePath": "/",
    "schemes": ["http"],
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT format: Bearer <token>",
        }
    },
}

AUTH_REGISTER_DOC = {
    "tags": ["Auth"],
    "summary": "Register a user",
    "parameters": [{
        "in": "body",
        "name": "body",
        "required": True,
        "schema": {
            "type": "object",
            "required": ["name", "email", "password", "role"],
            "properties": {
                "name": {"type": "string", "example": "Employer One"},
                "email": {"type": "string", "example": "employer@iris.com"},
                "password": {"type": "string", "example": "StrongPass@123"},
                "role": {"type": "string", "example": "employer"},
            },
        },
    }],
    "responses": {
        "201": {"description": "Registered", "examples": {"application/json": {"message": "User registered successfully"}}},
        "400": {"description": "Validation error"},
        "409": {"description": "Email already exists"},
    },
}

AUTH_LOGIN_DOC = {
    "tags": ["Auth"],
    "summary": "Login and obtain JWT",
    "parameters": [{
        "in": "body",
        "name": "body",
        "required": True,
        "schema": {
            "type": "object",
            "required": ["email", "password"],
            "properties": {
                "email": {"type": "string", "example": "employer@iris.com"},
                "password": {"type": "string", "example": "StrongPass@123"},
            },
        },
    }],
    "responses": {
        "200": {
            "description": "Login success",
            "examples": {
                "application/json": {
                    "message": "Login successful",
                    "access_token": "<JWT_TOKEN>",
                    "user": {
                        "id": 2,
                        "name": "Employer One",
                        "email": "employer@iris.com",
                        "role": "employer"
                    }
                }
            }
        },
        "401": {"description": "Invalid credentials"}
    }
}

JOB_CREATE_DOC = {
    "tags": ["Jobs"],
    "summary": "Create job (Employer)",
    "security": [{"BearerAuth": []}],
    "parameters": [{
        "in": "body",
        "name": "body",
        "required": True,
        "schema": {
            "type": "object",
            "required": ["title", "description", "location", "required_skills"],
            "properties": {
                "title": {"type": "string", "example": "Python Backend Developer"},
                "description": {"type": "string", "example": "Build Flask APIs and optimize SQL queries"},
                "location": {"type": "string", "example": "Bangalore"},
                "required_skills": {"type": "array", "items": {"type": "string"}, "example": ["python", "flask", "mysql", "sql"]}
            }
        }
    }],
    "responses": {
        "201": {"description": "Job created", "examples": {"application/json": {"message": "Job created successfully", "job_id": 1}}},
        "403": {"description": "Only employer can create jobs"}
    }
}

JOB_LIST_DOC = {
    "tags": ["Jobs"],
    "summary": "List jobs with optional search filters",
    "parameters": [
        {"in": "query", "name": "title", "type": "string", "required": False, "example": "Python"},
        {"in": "query", "name": "location", "type": "string", "required": False, "example": "Bangalore"}
    ],
    "responses": {
        "200": {
            "description": "Job list",
            "examples": {"application/json": [{"id": 1, "title": "Python Backend Developer", "description": "Build Flask APIs", "location": "Bangalore", "required_skills": ["flask", "python"], "employer_id": 2, "created_at": "2026-02-22T10:00:00"}]}
        }
    }
}

JOB_UPDATE_DOC = {
    "tags": ["Jobs"],
    "summary": "Update job (Employer)",
    "security": [{"BearerAuth": []}],
    "parameters": [
        {"in": "path", "name": "job_id", "type": "integer", "required": True},
        {"in": "body", "name": "body", "required": True, "schema": {"type": "object", "properties": {"title": {"type": "string"}, "description": {"type": "string"}, "location": {"type": "string"}, "required_skills": {"type": "array", "items": {"type": "string"}}}}}
    ],
    "responses": {
        "200": {"description": "Updated", "examples": {"application/json": {"message": "Job updated successfully"}}},
        "404": {"description": "Job not found"}
    }
}

JOB_DELETE_DOC = {
    "tags": ["Jobs"],
    "summary": "Delete job (Employer)",
    "security": [{"BearerAuth": []}],
    "parameters": [{"in": "path", "name": "job_id", "type": "integer", "required": True}],
    "responses": {
        "200": {"description": "Deleted", "examples": {"application/json": {"message": "Job deleted successfully"}}},
        "404": {"description": "Job not found"}
    }
}

JOB_APPLICANTS_DOC = {
    "tags": ["Jobs"],
    "summary": "View applicants by job sorted by match score",
    "security": [{"BearerAuth": []}],
    "parameters": [{"in": "path", "name": "job_id", "type": "integer", "required": True}],
    "responses": {
        "200": {
            "description": "Applicants list",
            "examples": {"application/json": {"job_id": 1, "applicants": [{"application_id": 5, "user_id": 7, "name": "John", "email": "john@x.com", "match_score": 88.4, "status": "Applied", "applied_at": "2026-02-22T12:00:00"}]}}
        }
    }
}

RESUME_UPLOAD_DOC = {
    "tags": ["Resume"],
    "summary": "Upload resume PDF",
    "security": [{"BearerAuth": []}],
    "consumes": ["multipart/form-data"],
    "parameters": [
        {"in": "formData", "name": "file", "type": "file", "required": True, "description": "PDF resume"}
    ],
    "responses": {
        "201": {
            "description": "Uploaded",
            "examples": {"application/json": {"message": "Resume uploaded successfully", "resume_id": 3, "extracted_skills": ["flask", "python"]}}
        },
        "400": {"description": "Invalid file"}
    }
}

RESUME_ME_DOC = {
    "tags": ["Resume"],
    "summary": "Get latest resume of logged-in jobseeker",
    "security": [{"BearerAuth": []}],
    "responses": {
        "200": {
            "description": "Resume details",
            "examples": {"application/json": {"id": 3, "filename": "resume.pdf", "uploaded_at": "2026-02-22T12:30:00", "extracted_skills": ["flask", "python"]}}
        },
        "404": {"description": "No resume found"}
    }
}

APP_CREATE_DOC = {
    "tags": ["Applications"],
    "summary": "Apply to a job",
    "security": [{"BearerAuth": []}],
    "parameters": [{
        "in": "body",
        "name": "body",
        "required": True,
        "schema": {
            "type": "object",
            "required": ["job_id"],
            "properties": {"job_id": {"type": "integer", "example": 1}}
        }
    }],
    "responses": {
        "201": {
            "description": "Application created",
            "examples": {"application/json": {"message": "Applied successfully", "application_id": 5, "match_score": 78.42, "matched_skills": ["python"], "missing_skills": ["mysql"]}}
        },
        "409": {"description": "Duplicate application"}
    }
}

APP_STATUS_DOC = {
    "tags": ["Applications"],
    "summary": "Update application status (Employer)",
    "security": [{"BearerAuth": []}],
    "parameters": [
        {"in": "path", "name": "application_id", "type": "integer", "required": True},
        {"in": "body", "name": "body", "required": True, "schema": {"type": "object", "required": ["status"], "properties": {"status": {"type": "string", "example": "Shortlisted"}}}}
    ],
    "responses": {
        "200": {"description": "Status updated", "examples": {"application/json": {"message": "Application status updated", "status": "Shortlisted"}}}
    }
}

APP_ME_DOC = {
    "tags": ["Applications"],
    "summary": "List my applications",
    "security": [{"BearerAuth": []}],
    "responses": {
        "200": {
            "description": "My applications",
            "examples": {"application/json": [{"application_id": 5, "job_id": 1, "job_title": "Python Backend Developer", "location": "Bangalore", "match_score": 78.42, "status": "Applied", "created_at": "2026-02-22T12:35:00"}]}
        }
    }
}

DASH_SUMMARY_DOC = {
    "tags": ["Dashboard"],
    "summary": "Admin dashboard summary",
    "security": [{"BearerAuth": []}],
    "responses": {
        "200": {
            "description": "Summary",
            "examples": {"application/json": {"total_users": 10, "total_jobs": 6, "total_applications": 19, "average_match_score": 74.2}}
        }
    }
}

DASH_USERS_DOC = {
    "tags": ["Dashboard"],
    "summary": "List all users (Admin)",
    "security": [{"BearerAuth": []}],
    "responses": {
        "200": {
            "description": "Users",
            "examples": {"application/json": [{"id": 1, "name": "Admin", "email": "admin@iris.com", "role": "admin", "created_at": "2026-02-22T09:00:00"}]}
        }
    }
}

DASH_DELETE_USER_DOC = {
    "tags": ["Dashboard"],
    "summary": "Delete user (Admin)",
    "security": [{"BearerAuth": []}],
    "parameters": [{"in": "path", "name": "user_id", "type": "integer", "required": True}],
    "responses": {
        "200": {"description": "Deleted", "examples": {"application/json": {"message": "User deleted successfully"}}},
        "404": {"description": "User not found"}
    }
}

DASH_ANALYTICS_DOC = {
    "tags": ["Dashboard"],
    "summary": "System analytics (Admin)",
    "security": [{"BearerAuth": []}],
    "responses": {
        "200": {
            "description": "Analytics",
            "examples": {"application/json": {"total_users": 10, "total_jobs": 6, "total_applications": 19, "average_match_score": 74.2, "role_distribution": {"admin": 1, "employer": 3, "jobseeker": 6}}}
        }
    }
}