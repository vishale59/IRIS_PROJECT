(function () {
  function log(...args) {
    console.log("[IRIS][applications]", ...args);
  }

  async function applyToJob(jobId) {
    if (!jobId) throw new Error("job_id is required");

    try {
      const response = await window.IRIS.apiRequest("/apply", {
        method: "POST",
        body: { job_id: jobId },
      });
      log("Applied via /apply", response);
      return response;
    } catch (error) {
      if (error.status === 404) {
        const fallback = await window.IRIS.apiRequest("/applications", {
          method: "POST",
          body: { job_id: jobId },
        });
        log("Applied via fallback /applications", fallback);
        return fallback;
      }
      throw error;
    }
  }

  async function fetchMyApplications() {
    try {
      const data = await window.IRIS.apiRequest("/applications");
      return Array.isArray(data) ? data : [];
    } catch (error) {
      if (error.status === 404) {
        const fallback = await window.IRIS.apiRequest("/applications/me");
        return Array.isArray(fallback) ? fallback : [];
      }
      throw error;
    }
  }

  async function fetchApplicantsByJob(jobId) {
    const data = await window.IRIS.apiRequest(`/jobs/${jobId}/applicants`);
    const applicants = Array.isArray(data?.applicants) ? data.applicants : [];
    applicants.sort((a, b) => Number(b.match_score || 0) - Number(a.match_score || 0));
    return applicants;
  }

  async function updateApplicationStatus(applicationId, status) {
    return window.IRIS.apiRequest(`/applications/${applicationId}/status`, {
      method: "PATCH",
      body: { status },
    });
  }

  function mapApplicationsByJob(applications) {
    return (applications || []).reduce((acc, item) => {
      acc[item.job_id] = item;
      return acc;
    }, {});
  }

  window.IRIS_APPLICATIONS = {
    applyToJob,
    fetchApplicantsByJob,
    fetchMyApplications,
    mapApplicationsByJob,
    updateApplicationStatus,
  };
})();
