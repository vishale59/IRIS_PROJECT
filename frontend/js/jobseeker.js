(function () {
  let cachedApplications = [];

  function setWelcome(user) {
    const target = document.getElementById("welcomeText");
    if (target) target.textContent = "Welcome, " + user.name;
  }

  function getApplicationsByJob() {
    const map = {};
    cachedApplications.forEach(function (item) {
      map[item.job_id] = item;
    });
    return map;
  }

  async function loadSummary() {
    const apps = await window.IRIS.apiRequest("/applications/me");
    cachedApplications = apps;

    const countEl = document.getElementById("applicationsCount");
    const avgEl = document.getElementById("avgMatch");
    if (countEl) countEl.textContent = String(apps.length);

    const avg = apps.length
      ? apps.reduce(function (sum, item) { return sum + Number(item.match_score || 0); }, 0) / apps.length
      : 0;
    if (avgEl) avgEl.textContent = window.IRIS.formatPercent(avg);

    if (window.IRISUI) {
      window.IRISUI.setScore("jobseekerScoreCircle", "jobseekerScoreText", avg);
      window.IRISUI.renderJobseekerCharts(cachedApplications);
    }

    const resumeStatusEl = document.getElementById("resumeStatus");
    try {
      await window.IRIS.apiRequest("/resumes/me");
      if (resumeStatusEl) resumeStatusEl.textContent = "Uploaded";
    } catch (error) {
      if (error.status === 404 && resumeStatusEl) resumeStatusEl.textContent = "Not Uploaded";
      else throw error;
    }
  }

  function renderJobs(jobs) {
    const container = document.getElementById("jobsContainer");
    if (!container) return;

    const appMap = getApplicationsByJob();

    if (!jobs.length) {
      container.innerHTML = "<article class='glass-card job-card'><p class='muted'>No jobs available.</p></article>";
      return;
    }

    container.innerHTML = jobs.map(function (job) {
      const app = appMap[job.id];
      const skills = Array.isArray(job.required_skills) ? job.required_skills.join(", ") : "";
      const score = app ? "<span class='score-badge'>Match: " + window.IRIS.formatPercent(app.match_score) + "</span>" : "<span class='score-badge'>Match will appear after applying</span>";
      const disabled = app ? "disabled" : "";
      const buttonLabel = app ? "Applied" : "Apply";

      return "<article class='glass-card job-card'>"
        + "<h3>" + job.title + "</h3>"
        + "<p class='muted'>" + job.description + "</p>"
        + "<div class='job-meta'><span>" + job.location + "</span><span>Required: " + skills + "</span></div>"
        + score
        + "<button class='btn btn-primary apply-btn' data-job-id='" + job.id + "' " + disabled + ">" + buttonLabel + "</button>"
        + "</article>";
    }).join("");

    Array.from(container.querySelectorAll(".apply-btn")).forEach(function (btn) {
      btn.addEventListener("click", function () {
        applyToJob(Number(btn.getAttribute("data-job-id")));
      });
    });
  }

  async function loadJobs() {
    const jobs = await window.IRIS.apiRequest("/jobs");
    renderJobs(jobs);
  }

  async function applyToJob(jobId) {
    const message = document.getElementById("globalMessage");
    window.IRIS.hideMessage(message);

    try {
      const result = await window.IRIS.apiRequest("/applications", {
        method: "POST",
        body: { job_id: jobId },
      });
      window.IRIS.showMessage(
        message,
        "Applied successfully. Match score: " + window.IRIS.formatPercent(result.match_score),
        "success"
      );
      await loadSummary();
      await loadJobs();
    } catch (error) {
      window.IRIS.showMessage(message, error.message, "error");
    }
  }

  async function uploadResume(event) {
    event.preventDefault();
    const message = document.getElementById("globalMessage");
    window.IRIS.hideMessage(message);

    const fileInput = document.getElementById("resumeFile");
    if (!fileInput || !fileInput.files || !fileInput.files.length) {
      window.IRIS.showMessage(message, "Please select a PDF file.", "error");
      return;
    }

    const fd = new FormData();
    fd.append("file", fileInput.files[0]);

    try {
      await window.IRIS.apiRequest("/resumes/upload", {
        method: "POST",
        body: fd,
        isFormData: true,
      });
      window.IRIS.showMessage(message, "Resume uploaded successfully.", "success");
      fileInput.value = "";
      await loadSummary();
    } catch (error) {
      window.IRIS.showMessage(message, error.message, "error");
    }
  }

  async function init() {
    const user = window.IRIS.requireAuth(["jobseeker"]);
    if (!user) return;

    setWelcome(user);
    window.IRIS.bindLogout("logoutBtn");

    const uploadForm = document.getElementById("resumeUploadForm");
    if (uploadForm) uploadForm.addEventListener("submit", uploadResume);

    const message = document.getElementById("globalMessage");
    try {
      await loadSummary();
      await loadJobs();
    } catch (error) {
      window.IRIS.showMessage(message, error.message, "error");
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
