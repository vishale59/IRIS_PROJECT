"""
IRIS Email Notification Service
"""
from flask import current_app, render_template_string
from flask_mail import Mail, Message

mail = Mail()


def _send(subject: str, recipients: list, html: str):
    """Internal helper — silently fails if mail not configured."""
    try:
        if not current_app.config.get('MAIL_USERNAME'):
            return  # mail not configured; skip silently
        msg = Message(subject=subject, recipients=recipients, html=html)
        mail.send(msg)
    except Exception as e:
        current_app.logger.warning(f"[MAIL] Failed to send email: {e}")


# ── Email Templates ───────────────────────────────────────────────────────────
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


def notify_application_received(applicant, job, employer_email: str):
    body = f"""
      <h2 style="color:#1e293b">New Application Received 📬</h2>
      <p style="color:#475569">Hi <strong>{job.company}</strong>,</p>
      <p style="color:#475569">
        <strong>{applicant.full_name}</strong> has applied for your job posting:
      </p>
      <div style="background:#f0f9ff;border-left:4px solid #2563eb;padding:16px;border-radius:8px;margin:16px 0">
        <strong style="color:#1e293b">{job.title}</strong><br>
        <span style="color:#64748b">{job.location} · {job.job_type}</span>
      </div>
      <p style="color:#475569">Log in to your employer dashboard to review the application.</p>
      <a href="#" style="display:inline-block;background:#2563eb;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:8px">View Application</a>
    """
    _send(
        subject=f"New Application: {job.title} — {applicant.full_name}",
        recipients=[employer_email],
        html=_BASE.format(body=body),
    )


def notify_application_submitted(applicant_email: str, applicant_name: str, job):
    body = f"""
      <h2 style="color:#1e293b">Application Submitted ✅</h2>
      <p style="color:#475569">Hi <strong>{applicant_name}</strong>,</p>
      <p style="color:#475569">Your application has been successfully submitted!</p>
      <div style="background:#f0fdf4;border-left:4px solid #16a34a;padding:16px;border-radius:8px;margin:16px 0">
        <strong style="color:#1e293b">{job.title}</strong><br>
        <span style="color:#64748b">{job.company} · {job.location}</span>
      </div>
      <p style="color:#475569">We'll notify you when the employer reviews your application. Good luck! 🤞</p>
    """
    _send(
        subject=f"Application Submitted — {job.title} at {job.company}",
        recipients=[applicant_email],
        html=_BASE.format(body=body),
    )


def notify_status_change(applicant_email: str, applicant_name: str, job, new_status: str):
    status_styles = {
        'shortlisted': ('#f0fdf4', '#16a34a', '🎉 Shortlisted!'),
        'rejected':    ('#fff1f2', '#dc2626', 'Application Update'),
        'hired':       ('#fefce8', '#d97706', '🎊 Offer Extended!'),
        'reviewed':    ('#eff6ff', '#2563eb', 'Application Reviewed'),
    }
    bg, border, label = status_styles.get(new_status, ('#f8fafc', '#64748b', 'Status Update'))

    body = f"""
      <h2 style="color:#1e293b">{label}</h2>
      <p style="color:#475569">Hi <strong>{applicant_name}</strong>,</p>
      <p style="color:#475569">Your application status has been updated:</p>
      <div style="background:{bg};border-left:4px solid {border};padding:16px;border-radius:8px;margin:16px 0">
        <strong style="color:#1e293b">{job.title}</strong> at <strong>{job.company}</strong><br>
        <span style="color:{border};font-weight:600;text-transform:capitalize">Status: {new_status}</span>
      </div>
      <p style="color:#475569">Log in to your dashboard to view details.</p>
    """
    _send(
        subject=f"Application Update — {job.title} at {job.company}",
        recipients=[applicant_email],
        html=_BASE.format(body=body),
    )
