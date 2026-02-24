(function () {
  function log(...args) {
    console.log("[IRIS][jobs]", ...args);
  }

  async function fetchJobs() {
    const jobs = await window.IRIS.apiRequest("/jobs");
    return Array.isArray(jobs) ? jobs : [];
  }

  function renderJobs(jobs, options = {}) {
    const { containerId = "jobsContainer", applicationsByJob = {}, onApply } = options;
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!Array.isArray(jobs) || jobs.length === 0) {
      container.innerHTML = "<article class='glass-card job-card'><p class='muted'>No jobs available.</p></article>";
      return;
    }

    container.innerHTML = jobs.map((job) => {
      const app = applicationsByJob[job.id];
      const skills = Array.isArray(job.required_skills) ? job.required_skills.join(", ") : "";
      const buttonDisabled = app ? "disabled" : "";
      const buttonLabel = app ? "Applied" : "Apply";
      const scoreLabel = app
        ? `<span class='score-badge'>Match: ${window.IRIS.formatPercent(app.match_score)}</span>`
        : "<span class='score-badge'>Match will appear after applying</span>";

      return `
        <article class='glass-card job-card'>
          <h3>${job.title || "Untitled"}</h3>
          <p class='muted'>${job.description || "No description"}</p>
          <div class='job-meta'>
            <span>${job.location || "N/A"}</span>
            <span>Required: ${skills || "N/A"}</span>
          </div>
          ${scoreLabel}
          <button class='btn btn-primary apply-btn' data-job-id='${job.id}' ${buttonDisabled}>${buttonLabel}</button>
        </article>
      `;
    }).join("");

    const applyButtons = Array.from(container.querySelectorAll(".apply-btn"));
    applyButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const jobId = Number(btn.getAttribute("data-job-id"));
        if (typeof onApply === "function") onApply(jobId);
      });
    });
  }

  async function createJob(payload) {
    const response = await window.IRIS.apiRequest("/jobs", {
      method: "POST",
      body: payload,
    });
    log("Job created", response);
    return response;
  }

  async function deleteJob(jobId) {
    const response = await window.IRIS.apiRequest(`/jobs/${jobId}`, { method: "DELETE" });
    log("Job deleted", { jobId, response });
    return response;
  }

  window.IRIS_JOBS = {
    createJob,
    deleteJob,
    fetchJobs,
    renderJobs,
  };
})();
