"""
IRIS Email Notification Service
"""
from flask import current_app
from flask_mail import Mail, Message

mail = Mail()


def _send(subject: str, recipients: list, html: str):
    """Internal helper that skips delivery when mail is not configured."""
    try:
        if not current_app.config.get("MAIL_USERNAME"):
            return
        msg = Message(subject=subject, recipients=recipients, html=html)
        mail.send(msg)
    except Exception as exc:
        current_app.logger.warning(f"[MAIL] Failed to send email: {exc}")


_BASE = """
<div style="font-family:Poppins,sans-serif;max-width:600px;margin:auto;background:#f9fafb;border-radius:12px;overflow:hidden">
  <div style="background:linear-gradient(135deg,#2563eb,#7c3aed);padding:32px;text-align:center">
    <h1 style="color:#fff;margin:0;font-size:24px;letter-spacing:1px">IRIS</h1>
    <p style="color:#bfdbfe;margin:4px 0 0;font-size:13px">AI-Powered Job Portal</p>
  </div>
  <div style="padding:32px;background:#fff">
    {body}
  </div>
  <div style="padding:16px;text-align:center;background:#f1f5f9;font-size:12px;color:#94a3b8">
    &copy; 2024 IRIS Job Portal. All rights reserved.
  </div>
</div>
"""


def _display_name(user) -> str:
    return getattr(user, "full_name", None) or getattr(user, "username", "User")


def _job_company(job) -> str:
    employer = getattr(job, "employer", None)
    return getattr(job, "company", None) or getattr(employer, "username", "Employer")


def _job_meta(job) -> str:
    parts = [getattr(job, "location", None), getattr(job, "job_type", None)]
    return " | ".join(part for part in parts if part)


def notify_application_received(applicant, job, employer_email: str):
    applicant_name = _display_name(applicant)
    company = _job_company(job)
    meta = _job_meta(job) or "IRIS Job Portal"
    body = f"""
      <h2 style="color:#1e293b">New Application Received</h2>
      <p style="color:#475569">Hi <strong>{company}</strong>,</p>
      <p style="color:#475569">
        <strong>{applicant_name}</strong> has applied for your job posting:
      </p>
      <div style="background:#f0f9ff;border-left:4px solid #2563eb;padding:16px;border-radius:8px;margin:16px 0">
        <strong style="color:#1e293b">{job.title}</strong><br>
        <span style="color:#64748b">{meta}</span>
      </div>
      <p style="color:#475569">Log in to your employer dashboard to review the application.</p>
    """
    _send(
        subject=f"New Application: {job.title} - {applicant_name}",
        recipients=[employer_email],
        html=_BASE.format(body=body),
    )


def notify_application_submitted(applicant_email: str, applicant_name: str, job):
    company = _job_company(job)
    meta = _job_meta(job)
    details = company if not meta else f"{company} | {meta}"
    body = f"""
      <h2 style="color:#1e293b">Application Submitted</h2>
      <p style="color:#475569">Hi <strong>{applicant_name}</strong>,</p>
      <p style="color:#475569">Your application has been successfully submitted.</p>
      <div style="background:#f0fdf4;border-left:4px solid #16a34a;padding:16px;border-radius:8px;margin:16px 0">
        <strong style="color:#1e293b">{job.title}</strong><br>
        <span style="color:#64748b">{details}</span>
      </div>
    """
    _send(
        subject=f"Application Submitted - {job.title} at {company}",
        recipients=[applicant_email],
        html=_BASE.format(body=body),
    )


def notify_status_change(applicant_email: str, applicant_name: str, job, new_status: str):
    company = _job_company(job)
    status_styles = {
        "shortlisted": ("#f0fdf4", "#16a34a", "Shortlisted"),
        "rejected": ("#fff1f2", "#dc2626", "Application Update"),
        "hired": ("#fefce8", "#d97706", "Offer Extended"),
        "reviewed": ("#eff6ff", "#2563eb", "Application Reviewed"),
    }
    bg, border, label = status_styles.get(new_status, ("#f8fafc", "#64748b", "Status Update"))

    body = f"""
      <h2 style="color:#1e293b">{label}</h2>
      <p style="color:#475569">Hi <strong>{applicant_name}</strong>,</p>
      <p style="color:#475569">Your application status has been updated:</p>
      <div style="background:{bg};border-left:4px solid {border};padding:16px;border-radius:8px;margin:16px 0">
        <strong style="color:#1e293b">{job.title}</strong> at <strong>{company}</strong><br>
        <span style="color:{border};font-weight:600;text-transform:capitalize">Status: {new_status}</span>
      </div>
    """
    _send(
        subject=f"Application Update - {job.title} at {company}",
        recipients=[applicant_email],
        html=_BASE.format(body=body),
    )
