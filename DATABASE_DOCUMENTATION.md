# IRIS Database Documentation

## Database

This project now uses MySQL only.

Connection format:

```text
mysql+pymysql://<username>:<password>@localhost/<database_name>
```

## Tables

### `users`

- `id` INT primary key
- `username` VARCHAR(80) unique, not null
- `email` VARCHAR(120) unique, not null
- `password` VARCHAR(255) not null
- `role` VARCHAR(20) not null
- `created_at` DATETIME not null

### `jobs`

- `id` INT primary key
- `title` VARCHAR(150) not null
- `description` TEXT not null
- `employer_id` INT foreign key to `users.id`
- `created_at` DATETIME not null

### `applications`

- `id` INT primary key
- `user_id` INT foreign key to `users.id`
- `job_id` INT foreign key to `jobs.id`
- `resume_path` VARCHAR(255) not null
- `score` INT not null
- `applied_at` DATETIME not null

Constraint:

- Unique application per user per job via `uq_user_job_application`

### `resume_data`

- `id` INT primary key
- `user_id` INT foreign key to `users.id`
- `extracted_text` TEXT not null
- `file_name` VARCHAR(255) not null
- `original_name` VARCHAR(255) not null
- `score` INT not null
- `keywords` TEXT not null
- `uploaded_at` DATETIME not null

## Table creation

Run:

```bash
python init_db.py
```

That script connects to MySQL, runs `db.create_all()`, and seeds the baseline records used by the app.
