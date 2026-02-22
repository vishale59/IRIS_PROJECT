(function () {
  function setWelcome(user) {
    const target = document.getElementById("welcomeText");
    if (target) target.textContent = "Welcome, " + user.name;
  }

  function renderRoleDistribution(roleDistribution) {
    const container = document.getElementById("roleDistribution");
    if (!container) return;

    const entries = Object.entries(roleDistribution || {});
    if (!entries.length) {
      container.innerHTML = "<span class='muted'>No analytics available.</span>";
      return;
    }

    container.innerHTML = entries
      .map(function (entry) {
        return "<span class='tag'>" + entry[0] + ": " + entry[1] + "</span>";
      })
      .join("");
  }

  function renderUsers(users) {
    const body = document.getElementById("usersTableBody");
    if (!body) return;

    if (!users.length) {
      body.innerHTML = "<tr><td colspan='4' class='muted'>No users found.</td></tr>";
      return;
    }

    body.innerHTML = users.map(function (user) {
      return "<tr>"
        + "<td>" + user.name + "</td>"
        + "<td>" + user.email + "</td>"
        + "<td>" + user.role + "</td>"
        + "<td>" + new Date(user.created_at).toLocaleDateString() + "</td>"
        + "</tr>";
    }).join("");
  }

  async function loadDashboard() {
    const summary = await window.IRIS.apiRequest("/dashboard");
    const analytics = await window.IRIS.apiRequest("/dashboard/analytics");
    const users = await window.IRIS.apiRequest("/dashboard/users");

    document.getElementById("totalUsers").textContent = String(summary.total_users || 0);
    document.getElementById("totalJobs").textContent = String(summary.total_jobs || 0);
    document.getElementById("totalApplications").textContent = String(summary.total_applications || 0);
    document.getElementById("averageMatch").textContent = window.IRIS.formatPercent(summary.average_match_score || 0);

    renderRoleDistribution(analytics.role_distribution);
    renderUsers(users);

    if (window.IRISUI) {
      window.IRISUI.renderAdminCharts(summary, analytics.role_distribution || {});
    }
  }

  async function init() {
    const user = window.IRIS.requireAuth(["admin"]);
    if (!user) return;

    setWelcome(user);
    window.IRIS.bindLogout("logoutBtn");

    const message = document.getElementById("globalMessage");
    try {
      await loadDashboard();
    } catch (error) {
      window.IRIS.showMessage(message, error.message, "error");
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
