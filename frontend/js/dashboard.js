(function () {
  const STATUSES = ["Applied", "Shortlisted", "Interview Scheduled", "Rejected", "Selected"];

  function log(...args) {
    console.log("[IRIS][dashboard]", ...args);
  }

  function setWelcome(user) {
    const welcome = document.getElementById("welcomeText");
    if (welcome) welcome.textContent = `Welcome, ${(user && user.name) || "User"}`;
  }

  function getMessageEl() {
    return document.getElementById("globalMessage");
  }

  async function getAnalytics() {
    try {
      return await window.IRIS.apiRequest("/analytics");
    } catch (error) {
      if (error.status === 404) {
        return window.IRIS.apiRequest("/dashboard/analytics");
      }
      throw error;
    }
  }

  async function loadAdminDashboard() {
    const summary = await window.IRIS.apiRequest("/dashboard");
    const analytics = await getAnalytics();
    const users = await window.IRIS.apiRequest("/dashboard/users");

    const totalUsers = document.getElementById("totalUsers");
    const totalJobs = document.getElementById("totalJobs");
    const totalApplications = document.getElementById("totalApplications");
    const averageMatch = document.getElementById("averageMatch");

    if (totalUsers) totalUsers.textContent = String(summary.total_users || 0);
    if (totalJobs) totalJobs.textContent = String(summary.total_jobs || 0);
    if (totalApplications) totalApplications.textContent = String(summary.total_applications || 0);
    if (averageMatch) averageMatch.textContent = window.IRIS.formatPercent(summary.average_match_score || 0);

    const roleDistributionEl = document.getElementById("roleDistribution");
    const roleDistribution = analytics.role_distribution || {};
    if (roleDistributionEl) {
      const entries = Object.entries(roleDistribution);
      roleDistributionEl.innerHTML = entries.length
        ? entries.map(([role, count]) => `<span class='tag'>${role}: ${count}</span>`).join("")
        : "<span class='muted'>No analytics available.</span>";
    }

    const usersBody = document.getElementById("usersTableBody");
    if (usersBody) {
      if (!users.length) {
        usersBody.innerHTML = "<tr><td colspan='4' class='muted'>No users found.</td></tr>";
      } else {
        usersBody.innerHTML = users.map((u) => `
          <tr>
            <td>${u.name}</td>
            <td>${u.email}</td>
            <td>${u.role}</td>
            <td>${new Date(u.created_at).toLocaleDateString()}</td>
          </tr>
        `).join("");
      }
    }

    if (window.IRISUI) {
      window.IRISUI.renderAdminCharts(summary, roleDistribution);
    }
  }

  async function initAdmin() {
    const auth = window.IRIS.requireAuth(["admin"]);
    if (!auth) return;

    setWelcome(auth.user || { role: auth.role });
    window.IRIS.bindLogout("logoutBtn");

    try {
      await loadAdminDashboard();
      log("Admin dashboard loaded");
    } catch (error) {
      window.IRIS.showMessage(getMessageEl(), error.message, "error");
    }
  }

  async function loadJobseekerSummary() {
    const applications = await window.IRIS_APPLICATIONS.fetchMyApplications();
    const appsCount = document.getElementById("applicationsCount");
    const avgMatch = document.getElementById("avgMatch");

    if (appsCount) appsCount.textContent = String(applications.length);

    const average = applications.length
      ? applications.reduce((sum, app) => sum + Number(app.match_score || 0), 0) / applications.length
      : 0;

    if (avgMatch) avgMatch.textContent = window.IRIS.formatPercent(average);

    if (window.IRISUI) {
      window.IRISUI.setScore("jobseekerScoreCircle", "jobseekerScoreText", average);
      window.IRISUI.renderJobseekerCharts(applications);
    }

    const resumeStatus = document.getElementById("resumeStatus");
    try {
      await window.IRIS.apiRequest("/resumes/me");
      if (resumeStatus) resumeStatus.textContent = "Uploaded";
    } catch (error) {
      if (resumeStatus) resumeStatus.textContent = error.status === 404 ? "Not Uploaded" : "Unknown";
    }

    return applications;
  }

  async function loadJobseekerJobs(existingApplications) {
    const jobs = await window.IRIS_JOBS.fetchJobs();
    const applicationsByJob = window.IRIS_APPLICATIONS.mapApplicationsByJob(existingApplications || []);

    window.IRIS_JOBS.renderJobs(jobs, {
      containerId: "jobsContainer",
      applicationsByJob,
      onApply: async (jobId) => {
        const messageEl = getMessageEl();
        window.IRIS.hideMessage(messageEl);

        if (applicationsByJob[jobId]) {
          window.IRIS.showMessage(messageEl, "You already applied to this job.", "error");
          return;
        }

        try {
          const applyResult = await window.IRIS_APPLICATIONS.applyToJob(jobId);
          const score = applyResult && typeof applyResult.match_score !== "undefined"
            ? ` Match score: ${window.IRIS.formatPercent(applyResult.match_score)}.`
            : "";
          window.IRIS.showMessage(messageEl, `Application submitted successfully.${score}`, "success");

          const updatedApps = await loadJobseekerSummary();
          await loadJobseekerJobs(updatedApps);
        } catch (error) {
          if (error.status === 409) {
            window.IRIS.showMessage(messageEl, "You have already applied to this job.", "error");
            const refreshedApps = await loadJobseekerSummary();
            await loadJobseekerJobs(refreshedApps);
            return;
          }
          window.IRIS.showMessage(messageEl, error.message, "error");
        }
      },
    });
  }

  async function handleResumeUpload(event) {
    event.preventDefault();

    const messageEl = getMessageEl();
    window.IRIS.hideMessage(messageEl);

    const fileInput = document.getElementById("resumeFile");
    const file = fileInput && fileInput.files && fileInput.files[0];
    if (!file) {
      window.IRIS.showMessage(messageEl, "Please select a PDF file.", "error");
      return;
    }

    try {
      const result = await window.IRIS_RESUME.uploadAndAnalyzeResume(file);
      window.IRIS_RESUME.renderResumeAnalysis(result, { messageId: "globalMessage" });
      if (fileInput) fileInput.value = "";

      const updatedApps = await loadJobseekerSummary();
      await loadJobseekerJobs(updatedApps);
    } catch (error) {
      window.IRIS.showMessage(messageEl, error.message, "error");
    }
  }

  async function initJobseeker() {
    const auth = window.IRIS.requireAuth(["jobseeker"]);
    if (!auth) return;

    setWelcome(auth.user || { role: auth.role });
    window.IRIS.bindLogout("logoutBtn");

    const uploadForm = document.getElementById("resumeUploadForm");
    if (uploadForm) uploadForm.addEventListener("submit", handleResumeUpload);

    try {
      const apps = await loadJobseekerSummary();
      await loadJobseekerJobs(apps);
      log("Jobseeker dashboard loaded");
    } catch (error) {
      window.IRIS.showMessage(getMessageEl(), error.message, "error");
    }
  }

  function renderEmployerApplicants(applicants, selectedJobTitle) {
    const applicantsBody = document.getElementById("applicantsTableBody");
    if (!applicantsBody) return;

    const selectedJobLabel = document.getElementById("selectedJobLabel");
    if (selectedJobLabel) selectedJobLabel.textContent = selectedJobTitle
      ? `Applicants for: ${selectedJobTitle}`
      : "Select a job to view applicants.";

    if (window.IRISUI) {
      window.IRISUI.renderEmployerApplicantsChart(applicants);
    }

    if (!applicants.length) {
      applicantsBody.innerHTML = "<tr><td colspan='5' class='muted'>No applicants yet.</td></tr>";
      return;
    }

    applicantsBody.innerHTML = applicants.map((row) => {
      const options = STATUSES.map((status) => {
        const selected = row.status === status ? "selected" : "";
        return `<option value='${status}' ${selected}>${status}</option>`;
      }).join("");

      return `
        <tr>
          <td>${row.name}</td>
          <td>${row.email}</td>
          <td><span class='score-badge'>${window.IRIS.formatPercent(row.match_score)}</span></td>
          <td>${row.status}</td>
          <td><select class='table-select status-select' data-application-id='${row.application_id}'>${options}</select></td>
        </tr>
      `;
    }).join("");

    const statusSelects = Array.from(applicantsBody.querySelectorAll(".status-select"));
    statusSelects.forEach((select) => {
      select.addEventListener("change", async () => {
        const applicationId = Number(select.getAttribute("data-application-id"));
        const nextStatus = select.value;
        try {
          await window.IRIS_APPLICATIONS.updateApplicationStatus(applicationId, nextStatus);
          window.IRIS.showMessage(getMessageEl(), "Application status updated.", "success");
        } catch (error) {
          window.IRIS.showMessage(getMessageEl(), error.message, "error");
        }
      });
    });
  }
  async function loadEmployerAnalytics() {
    try {
      const analytics = await getAnalytics();
      const applicantCount = document.getElementById("employerApplicantCount");
      const avgMatch = document.getElementById("employerAvgMatch");

      if (applicantCount && Number(applicantCount.textContent || 0) === 0) {
        applicantCount.textContent = String(analytics.total_applications || 0);
      }

      if (avgMatch && (avgMatch.textContent || "0%").startsWith("0")) {
        avgMatch.textContent = window.IRIS.formatPercent(analytics.average_match_score || 0);
      }
    } catch (error) {
      console.warn("[IRIS][dashboard] Employer analytics unavailable", error.message);
    }
  }

  async function loadEmployerJobs(currentUser) {
    const allJobs = await window.IRIS_JOBS.fetchJobs();
    const ownJobs = allJobs.filter((job) => Number(job.employer_id) === Number(currentUser.id));

    const count = document.getElementById("employerJobCount");
    if (count) count.textContent = String(ownJobs.length);

    if (window.IRISUI) {
      window.IRISUI.renderEmployerJobsChart(ownJobs);
    }

    const container = document.getElementById("employerJobsContainer");
    if (!container) return ownJobs;

    if (!ownJobs.length) {
      container.innerHTML = "<article class='glass-card job-card'><p class='muted'>No jobs created yet.</p></article>";
      return ownJobs;
    }

    container.innerHTML = ownJobs.map((job) => `
      <article class='glass-card job-card'>
        <h3>${job.title}</h3>
        <p class='muted'>${job.description}</p>
        <div class='job-meta'>
          <span>${job.location}</span>
          <span>Skills: ${(job.required_skills || []).join(", ")}</span>
        </div>
        <div class='job-meta'>
          <button class='btn btn-secondary view-applicants' data-job-id='${job.id}' data-job-title='${job.title}'>View Applicants</button>
          <button class='btn btn-danger delete-job' data-job-id='${job.id}'>Delete</button>
        </div>
      </article>
    `).join("");

    const applicantsButtons = Array.from(container.querySelectorAll(".view-applicants"));
    applicantsButtons.forEach((btn) => {
      btn.addEventListener("click", async () => {
        const jobId = Number(btn.getAttribute("data-job-id"));
        const jobTitle = btn.getAttribute("data-job-title") || "Selected Job";
        try {
          const applicants = await window.IRIS_APPLICATIONS.fetchApplicantsByJob(jobId);
          renderEmployerApplicants(applicants, jobTitle);
        } catch (error) {
          window.IRIS.showMessage(getMessageEl(), error.message, "error");
        }
      });
    });

    const deleteButtons = Array.from(container.querySelectorAll(".delete-job"));
    deleteButtons.forEach((btn) => {
      btn.addEventListener("click", async () => {
        const jobId = Number(btn.getAttribute("data-job-id"));
        if (!window.confirm("Delete this job?")) return;

        try {
          await window.IRIS_JOBS.deleteJob(jobId);
          window.IRIS.showMessage(getMessageEl(), "Job deleted successfully.", "success");
          await loadEmployerJobs(currentUser);
          renderEmployerApplicants([], "");
        } catch (error) {
          window.IRIS.showMessage(getMessageEl(), error.message, "error");
        }
      });
    });

    return ownJobs;
  }

  async function handleCreateJob(event, currentUser) {
    event.preventDefault();

    const title = document.getElementById("title")?.value.trim();
    const description = document.getElementById("description")?.value.trim();
    const location = document.getElementById("location")?.value.trim();
    const requiredSkills = (document.getElementById("requiredSkills")?.value || "")
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    if (!title || !description || !location || !requiredSkills.length) {
      window.IRIS.showMessage(getMessageEl(), "All fields are required.", "error");
      return;
    }

    try {
      await window.IRIS_JOBS.createJob({
        title,
        description,
        location,
        required_skills: requiredSkills,
      });
      event.target.reset();
      window.IRIS.showMessage(getMessageEl(), "Job created successfully.", "success");
      await loadEmployerJobs(currentUser);
    } catch (error) {
      window.IRIS.showMessage(getMessageEl(), error.message, "error");
    }
  }

  async function initEmployer() {
    const auth = window.IRIS.requireAuth(["employer"]);
    if (!auth) return;

    const user = auth.user || {};
    setWelcome(user);
    window.IRIS.bindLogout("logoutBtn");

    const createForm = document.getElementById("createJobForm");
    if (createForm) {
      createForm.addEventListener("submit", (event) => handleCreateJob(event, user));
    }

    try {
      await loadEmployerAnalytics();
      await loadEmployerJobs(user);
      renderEmployerApplicants([], "");
      log("Employer dashboard loaded");
    } catch (error) {
      window.IRIS.showMessage(getMessageEl(), error.message, "error");
    }
  }

  document.addEventListener("DOMContentLoaded", async () => {
    const path = (window.location.pathname || "").toLowerCase();

    if (path.endsWith("dashboard-jobseeker.html")) {
      await initJobseeker();
      return;
    }

    if (path.endsWith("dashboard-employer.html")) {
      await initEmployer();
      return;
    }

    if (path.endsWith("dashboard-admin.html")) {
      await initAdmin();
    }
  });
})();

