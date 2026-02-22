(function () {
  let currentUser = null;
  const statuses = ["Applied", "Shortlisted", "Interview Scheduled", "Rejected", "Selected"];

  function setWelcome() {
    const target = document.getElementById("welcomeText");
    if (target && currentUser) target.textContent = "Welcome, " + currentUser.name;
  }

  function renderJobs(jobs) {
    const container = document.getElementById("employerJobsContainer");
    if (!container) return;

    const countEl = document.getElementById("employerJobCount");
    if (countEl) countEl.textContent = String(jobs.length);
    if (window.IRISUI) window.IRISUI.renderEmployerJobsChart(jobs);

    if (!jobs.length) {
      container.innerHTML = "<article class='glass-card job-card'><p class='muted'>No jobs created yet.</p></article>";
      return;
    }

    container.innerHTML = jobs.map(function (job) {
      return "<article class='glass-card job-card'>"
        + "<h3>" + job.title + "</h3>"
        + "<p class='muted'>" + job.description + "</p>"
        + "<div class='job-meta'><span>" + job.location + "</span><span>Skills: " + (job.required_skills || []).join(", ") + "</span></div>"
        + "<div class='job-meta'>"
        + "<button class='btn btn-secondary view-applicants' data-job-id='" + job.id + "' data-job-title='" + job.title + "'>View Applicants</button>"
        + "<button class='btn btn-danger delete-job' data-job-id='" + job.id + "'>Delete</button>"
        + "</div>"
        + "</article>";
    }).join("");

    Array.from(container.querySelectorAll(".view-applicants")).forEach(function (btn) {
      btn.addEventListener("click", function () {
        loadApplicants(Number(btn.getAttribute("data-job-id")), btn.getAttribute("data-job-title"));
      });
    });

    Array.from(container.querySelectorAll(".delete-job")).forEach(function (btn) {
      btn.addEventListener("click", function () {
        deleteJob(Number(btn.getAttribute("data-job-id")));
      });
    });
  }

  async function loadJobs() {
    const jobs = await window.IRIS.apiRequest("/jobs");
    const own = jobs.filter(function (job) {
      return Number(job.employer_id) === Number(currentUser.id);
    });
    renderJobs(own);
  }

  async function createJob(event) {
    event.preventDefault();
    const message = document.getElementById("globalMessage");
    window.IRIS.hideMessage(message);

    const title = document.getElementById("title").value.trim();
    const description = document.getElementById("description").value.trim();
    const location = document.getElementById("location").value.trim();
    const requiredSkills = document.getElementById("requiredSkills").value
      .split(",")
      .map(function (s) { return s.trim(); })
      .filter(Boolean);

    try {
      await window.IRIS.apiRequest("/jobs", {
        method: "POST",
        body: {
          title: title,
          description: description,
          location: location,
          required_skills: requiredSkills,
        },
      });
      event.target.reset();
      window.IRIS.showMessage(message, "Job created successfully.", "success");
      await loadJobs();
    } catch (error) {
      window.IRIS.showMessage(message, error.message, "error");
    }
  }

  async function deleteJob(jobId) {
    const message = document.getElementById("globalMessage");
    if (!window.confirm("Delete this job?")) return;

    try {
      await window.IRIS.apiRequest("/jobs/" + jobId, { method: "DELETE" });
      window.IRIS.showMessage(message, "Job deleted.", "success");
      await loadJobs();
      clearApplicants();
    } catch (error) {
      window.IRIS.showMessage(message, error.message, "error");
    }
  }

  function clearApplicants() {
    const body = document.getElementById("applicantsTableBody");
    if (body) body.innerHTML = "";
    const label = document.getElementById("selectedJobLabel");
    if (label) label.textContent = "Select a job to view applicants.";
    if (window.IRISUI) window.IRISUI.renderEmployerApplicantsChart([]);
  }

  function renderApplicants(rows, jobTitle) {
    const body = document.getElementById("applicantsTableBody");
    if (!body) return;

    const label = document.getElementById("selectedJobLabel");
    if (label) label.textContent = "Applicants for: " + jobTitle;

    if (window.IRISUI) window.IRISUI.renderEmployerApplicantsChart(rows);

    if (!rows.length) {
      body.innerHTML = "<tr><td colspan='5' class='muted'>No applicants yet.</td></tr>";
      return;
    }

    body.innerHTML = rows.map(function (row) {
      const options = statuses.map(function (status) {
        const selected = status === row.status ? "selected" : "";
        return "<option value='" + status + "' " + selected + ">" + status + "</option>";
      }).join("");

      return "<tr>"
        + "<td>" + row.name + "</td>"
        + "<td>" + row.email + "</td>"
        + "<td><span class='score-badge'>" + window.IRIS.formatPercent(row.match_score) + "</span></td>"
        + "<td>" + row.status + "</td>"
        + "<td><select class='table-select status-select' data-application-id='" + row.application_id + "'>" + options + "</select></td>"
        + "</tr>";
    }).join("");

    Array.from(body.querySelectorAll(".status-select")).forEach(function (select) {
      select.addEventListener("change", function () {
        updateStatus(Number(select.getAttribute("data-application-id")), select.value);
      });
    });
  }

  async function loadApplicants(jobId, jobTitle) {
    const message = document.getElementById("globalMessage");
    window.IRIS.hideMessage(message);

    try {
      const data = await window.IRIS.apiRequest("/jobs/" + jobId + "/applicants");
      renderApplicants(data.applicants || [], jobTitle);
    } catch (error) {
      window.IRIS.showMessage(message, error.message, "error");
    }
  }

  async function updateStatus(applicationId, status) {
    const message = document.getElementById("globalMessage");
    try {
      await window.IRIS.apiRequest("/applications/" + applicationId + "/status", {
        method: "PATCH",
        body: { status: status },
      });
      window.IRIS.showMessage(message, "Application status updated.", "success");
    } catch (error) {
      window.IRIS.showMessage(message, error.message, "error");
    }
  }

  async function init() {
    currentUser = window.IRIS.requireAuth(["employer"]);
    if (!currentUser) return;

    setWelcome();
    window.IRIS.bindLogout("logoutBtn");

    const form = document.getElementById("createJobForm");
    if (form) form.addEventListener("submit", createJob);

    const message = document.getElementById("globalMessage");
    try {
      await loadJobs();
      clearApplicants();
    } catch (error) {
      window.IRIS.showMessage(message, error.message, "error");
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
