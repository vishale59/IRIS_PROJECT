(function () {
  var charts = {};

  function ensureChart(id, config) {
    if (typeof window.Chart === "undefined") return null;
    var canvas = document.getElementById(id);
    if (!canvas) return null;

    if (charts[id]) charts[id].destroy();
    var ctx = canvas.getContext("2d");
    charts[id] = new window.Chart(ctx, config);
    return charts[id];
  }

  function setScore(circleId, textId, score) {
    var value = Number(score || 0);
    var circle = document.getElementById(circleId);
    if (circle) circle.style.setProperty("--score", String(Math.max(0, Math.min(100, value))));

    var text = document.getElementById(textId);
    if (text) text.textContent = value.toFixed(2) + "%";
  }

  function renderJobseekerCharts(applications) {
    var apps = Array.isArray(applications) ? applications : [];
    var labels = apps.map(function (_, i) { return "A" + (i + 1); });
    var scores = apps.map(function (a) { return Number(a.match_score || 0); });

    ensureChart("jobseekerTrendChart", {
      type: "line",
      data: {
        labels: labels.length ? labels : ["No Data"],
        datasets: [{
          label: "Match Score",
          data: scores.length ? scores : [0],
          borderColor: "#818cf8",
          backgroundColor: "rgba(129,140,248,0.2)",
          tension: 0.35,
          fill: true,
          pointRadius: 2,
        }],
      },
      options: chartOptions(0, 100),
    });

    var statusMap = {};
    apps.forEach(function (a) {
      var key = a.status || "Applied";
      statusMap[key] = (statusMap[key] || 0) + 1;
    });

    var tableBody = document.getElementById("jobseekerStatusTableBody");
    if (tableBody) {
      var entries = Object.entries(statusMap);
      if (!entries.length) {
        tableBody.innerHTML = "<tr><td class='muted' colspan='2'>Application data will appear here after job applications.</td></tr>";
      } else {
        tableBody.innerHTML = entries.map(function (item) {
          return "<tr><td>" + item[0] + "</td><td>" + item[1] + "</td></tr>";
        }).join("");
      }
    }
  }

  function renderEmployerJobsChart(jobs) {
    var list = Array.isArray(jobs) ? jobs : [];
    ensureChart("employerJobsChart", {
      type: "bar",
      data: {
        labels: list.length ? list.map(function (_, i) { return "Job " + (i + 1); }) : ["No Jobs"],
        datasets: [{
          label: "Required Skills Count",
          data: list.length ? list.map(function (j) { return (j.required_skills || []).length; }) : [0],
          backgroundColor: "rgba(99,102,241,0.45)",
          borderColor: "#818cf8",
          borderWidth: 1,
        }],
      },
      options: chartOptions(0),
    });
  }

  function renderEmployerApplicantsChart(applicants) {
    var rows = Array.isArray(applicants) ? applicants : [];
    var statusMap = {};
    rows.forEach(function (row) {
      var key = row.status || "Applied";
      statusMap[key] = (statusMap[key] || 0) + 1;
    });

    var labels = Object.keys(statusMap);
    var values = labels.map(function (k) { return statusMap[k]; });
    ensureChart("employerApplicantsChart", {
      type: "doughnut",
      data: {
        labels: labels.length ? labels : ["No Applicants"],
        datasets: [{
          data: values.length ? values : [1],
          backgroundColor: ["#818cf8", "#38bdf8", "#34d399", "#fb7185", "#fbbf24"],
          borderColor: "rgba(15,23,42,0.9)",
          borderWidth: 2,
        }],
      },
      options: {
        plugins: {
          legend: { labels: { color: "#cbd5e1" } },
        },
      },
    });

    var countEl = document.getElementById("employerApplicantCount");
    var avgEl = document.getElementById("employerAvgMatch");
    if (countEl) countEl.textContent = String(rows.length);

    var avg = rows.length
      ? rows.reduce(function (sum, row) { return sum + Number(row.match_score || 0); }, 0) / rows.length
      : 0;
    if (avgEl) avgEl.textContent = avg.toFixed(2) + "%";
  }

  function renderAdminCharts(summary, roleDistribution) {
    ensureChart("adminOverviewChart", {
      type: "bar",
      data: {
        labels: ["Users", "Jobs", "Applications"],
        datasets: [{
          label: "Total",
          data: [
            Number(summary.total_users || 0),
            Number(summary.total_jobs || 0),
            Number(summary.total_applications || 0),
          ],
          backgroundColor: ["rgba(99,102,241,0.6)", "rgba(56,189,248,0.6)", "rgba(34,197,94,0.6)"],
          borderWidth: 1,
        }],
      },
      options: chartOptions(0),
    });

    var labels = Object.keys(roleDistribution || {});
    var values = labels.map(function (key) { return roleDistribution[key]; });

    ensureChart("adminRolesChart", {
      type: "pie",
      data: {
        labels: labels.length ? labels : ["No Data"],
        datasets: [{
          data: values.length ? values : [1],
          backgroundColor: ["#6366f1", "#06b6d4", "#22c55e", "#f97316"],
          borderColor: "rgba(15,23,42,0.9)",
          borderWidth: 2,
        }],
      },
      options: {
        plugins: {
          legend: { labels: { color: "#cbd5e1" } },
        },
      },
    });
  }

  function chartOptions(min, max) {
    return {
      maintainAspectRatio: false,
      scales: {
        x: {
          ticks: { color: "#cbd5e1" },
          grid: { color: "rgba(148,163,184,0.14)" },
        },
        y: {
          min: typeof min === "number" ? min : undefined,
          max: typeof max === "number" ? max : undefined,
          ticks: { color: "#cbd5e1" },
          grid: { color: "rgba(148,163,184,0.14)" },
        },
      },
      plugins: {
        legend: { labels: { color: "#cbd5e1" } },
      },
    };
  }

  window.IRISUI = {
    setScore: setScore,
    renderJobseekerCharts: renderJobseekerCharts,
    renderEmployerJobsChart: renderEmployerJobsChart,
    renderEmployerApplicantsChart: renderEmployerApplicantsChart,
    renderAdminCharts: renderAdminCharts,
  };
})();
