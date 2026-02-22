(function () {
  const BASE_API = (window.IRIS_CONFIG && window.IRIS_CONFIG.API_BASE) || window.IRIS_API_BASE || "http://localhost:5000/api";

  function getToken() {
    return localStorage.getItem("iris_token");
  }

  function getUser() {
    const raw = localStorage.getItem("iris_user");
    return raw ? JSON.parse(raw) : null;
  }

  function saveSession(token, user) {
    localStorage.setItem("iris_token", token);
    localStorage.setItem("iris_user", JSON.stringify(user));
  }

  function clearSession() {
    localStorage.removeItem("iris_token");
    localStorage.removeItem("iris_user");
  }

  function redirectByRole(role) {
    if (role === "jobseeker") window.location.href = "dashboard-jobseeker.html";
    else if (role === "employer") window.location.href = "dashboard-employer.html";
    else if (role === "admin") window.location.href = "dashboard-admin.html";
    else window.location.href = "login.html";
  }

  async function apiRequest(path, options) {
    const opts = options || {};
    const method = opts.method || "GET";
    const body = opts.body;
    const auth = opts.auth !== false;
    const isFormData = opts.isFormData === true;
    const headers = Object.assign({}, opts.headers || {});

    if (!isFormData) headers["Content-Type"] = "application/json";
    if (auth && getToken()) headers.Authorization = "Bearer " + getToken();

    const response = await fetch(BASE_API + path, {
      method,
      headers,
      body: body ? (isFormData ? body : JSON.stringify(body)) : undefined,
    });

    const text = await response.text();
    let data = {};
    if (text) {
      try {
        data = JSON.parse(text);
      } catch (_err) {
        data = { message: text };
      }
    }

    if (!response.ok) {
      const message = data.error || data.message || "Request failed";
      const err = new Error(message);
      err.status = response.status;
      throw err;
    }

    return data;
  }

  function showMessage(el, message, type) {
    if (!el) return;
    el.className = "alert";
    el.classList.add(type === "success" ? "alert-success" : "alert-error");
    el.textContent = message;
    el.classList.remove("hidden");
  }

  function hideMessage(el) {
    if (!el) return;
    el.classList.add("hidden");
    el.textContent = "";
  }

  function formatPercent(value) {
    const n = Number(value || 0);
    return n.toFixed(2) + "%";
  }

  function requireAuth(expectedRoles) {
    const user = getUser();
    const token = getToken();
    if (!user || !token) {
      window.location.href = "login.html";
      return null;
    }

    if (Array.isArray(expectedRoles) && expectedRoles.length && !expectedRoles.includes(user.role)) {
      redirectByRole(user.role);
      return null;
    }

    return user;
  }

  function bindLogout(buttonId) {
    const btn = document.getElementById(buttonId || "logoutBtn");
    if (!btn) return;
    btn.addEventListener("click", function () {
      clearSession();
      window.location.href = "login.html";
    });
  }

  async function handleLoginSubmit(event) {
    event.preventDefault();
    const msg = document.getElementById("authMessage");
    hideMessage(msg);

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const selectedRole = document.getElementById("role").value;

    try {
      const data = await apiRequest("/auth/login", {
        method: "POST",
        body: { email, password },
        auth: false,
      });

      if (data.user.role !== selectedRole) {
        showMessage(msg, "Selected role does not match account role.", "error");
        return;
      }

      saveSession(data.access_token, data.user);
      redirectByRole(data.user.role);
    } catch (error) {
      showMessage(msg, error.message, "error");
    }
  }

  async function handleRegisterSubmit(event) {
    event.preventDefault();
    const msg = document.getElementById("authMessage");
    hideMessage(msg);

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const role = document.getElementById("role").value;

    try {
      await apiRequest("/auth/register", {
        method: "POST",
        body: { name, email, password, role },
        auth: false,
      });

      showMessage(msg, "Registration successful. Redirecting to login.", "success");
      setTimeout(function () {
        window.location.href = "login.html";
      }, 900);
    } catch (error) {
      showMessage(msg, error.message, "error");
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");

    if (loginForm) loginForm.addEventListener("submit", handleLoginSubmit);
    if (registerForm) registerForm.addEventListener("submit", handleRegisterSubmit);
  });

  window.IRIS = {
    apiRequest,
    bindLogout,
    clearSession,
    formatPercent,
    getToken,
    getUser,
    hideMessage,
    redirectByRole,
    requireAuth,
    saveSession,
    showMessage,
  };
})();