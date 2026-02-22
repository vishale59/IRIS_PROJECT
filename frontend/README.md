# IRIS Frontend

Vanilla HTML/CSS/JS frontend for IRIS.

## Structure
- `index.html`
- `login.html`
- `register.html`
- `dashboard-jobseeker.html`
- `dashboard-employer.html`
- `dashboard-admin.html`
- `css/style.css`
- `js/config.js`
- `js/auth.js`
- `js/jobseeker.js`
- `js/employer.js`
- `js/analytics.js`

## Configure Backend URL
Edit `js/config.js`:
```js
window.IRIS_CONFIG = {
  API_BASE: "http://localhost:5000/api",
};
```

## Run Locally
1. Start backend server from `backend/`:
```bash
python run.py
```
2. Start frontend static server from `frontend/`:
```bash
python -m http.server 5500
```
3. Open:
- `http://localhost:5500/index.html`

## Login Flow
1. Register a user from `register.html`.
2. Login from `login.html`.
3. JWT and user profile are stored in `localStorage` keys:
- `iris_token`
- `iris_user`

## Notes
- Frontend sends `Authorization: Bearer <token>` automatically for protected APIs.
- If API host/port changes, update `js/config.js` only.
- Ensure Flask CORS is enabled for frontend port.

## Basic Smoke Checklist
- Login works and redirects by role.
- Jobseeker can upload resume and apply.
- Employer can create job and view applicants.
- Admin can view dashboard analytics and users.