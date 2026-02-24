(function () {
  function log(...args) {
    console.log("[IRIS][resume]", ...args);
  }

  async function analyzeResume(file) {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const result = await window.IRIS.apiRequest("/resume/analyze", {
        method: "POST",
        body: formData,
        isFormData: true,
      });
      log("Resume analyzed using /resume/analyze");
      return result;
    } catch (error) {
      console.warn("[IRIS][resume] /resume/analyze not available, falling back to /resumes/upload", error.message);
      const fallbackResult = await window.IRIS.apiRequest("/resumes/upload", {
        method: "POST",
        body: formData,
        isFormData: true,
      });
      log("Resume uploaded using /resumes/upload");
      return fallbackResult;
    }
  }

  async function uploadAndAnalyzeResume(file) {
    if (!file) throw new Error("Please select a PDF file.");
    return analyzeResume(file);
  }

  function renderResumeAnalysis(data, options = {}) {
    const {
      scoreId = "avgMatch",
      matchedSkillsId,
      missingSkillsId,
      messageId = "globalMessage",
    } = options;

    const scoreEl = document.getElementById(scoreId);
    if (scoreEl && typeof data.match_score !== "undefined") {
      scoreEl.textContent = window.IRIS.formatPercent(data.match_score);
    }

    if (matchedSkillsId) {
      const matchedEl = document.getElementById(matchedSkillsId);
      if (matchedEl) {
        const matched = Array.isArray(data.matched_skills) ? data.matched_skills : [];
        matchedEl.textContent = matched.length ? matched.join(", ") : "None";
      }
    }

    if (missingSkillsId) {
      const missingEl = document.getElementById(missingSkillsId);
      if (missingEl) {
        const missing = Array.isArray(data.missing_skills) ? data.missing_skills : [];
        missingEl.textContent = missing.length ? missing.join(", ") : "None";
      }
    }

    const messageEl = document.getElementById(messageId);
    if (messageEl) {
      const scoreInfo = typeof data.match_score !== "undefined"
        ? ` Match score: ${window.IRIS.formatPercent(data.match_score)}.`
        : "";
      window.IRIS.showMessage(messageEl, `Resume processed successfully.${scoreInfo}`, "success");
    }
  }

  window.IRIS_RESUME = {
    renderResumeAnalysis,
    uploadAndAnalyzeResume,
  };
})();
