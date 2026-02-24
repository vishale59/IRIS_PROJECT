(function () {
  const API_BASE = (window.IRIS_CONFIG && window.IRIS_CONFIG.API_BASE) || "http://127.0.0.1:5000/api";

  const STORAGE_KEYS = {
    token: "iris_token",
    role: "iris_role",
    user: "iris_user",
  };

  const ROLE_DASHBOARD = {
    jobseeker: "dashboard-jobseeker.html",
    employer: "dashboard-employer.html",
    admin: "dashboard-admin.html",
  };

  function log(...args) {
    console.log("[IRIS][auth]", ...args);
  }

  function getToken() {
    return localStorage.getItem(STORAGE_KEYS.token) || "";
  }

  function getRole() {
    return localStorage.getItem(STORAGE_KEYS.role) || "";
  }

  function getUser() {
    const raw = localStorage.getItem(STORAGE_KEYS.user);
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch (error) {
      console.error("[IRIS][auth] Failed to parse stored user", error);
      return null;
    }
  }

  function saveSession(accessToken, role, user) {
    localStorage.setItem(STORAGE_KEYS.token, accessToken || "");
    localStorage.setItem(STORAGE_KEYS.role, role || "");
    if (user) localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(user));
    log("Session saved", { role: role || "unknown" });
  }

  function clearSession() {
    localStorage.removeItem(STORAGE_KEYS.token);
    localStorage.removeItem(STORAGE_KEYS.role);
    localStorage.removeItem(STORAGE_KEYS.user);
    log("Session cleared");
  }

  function redirectByRole(role) {
    const path = ROLE_DASHBOARD[role] || "login.html";
    window.location.href = path;
  }

  function logout() {
    clearSession();
    window.location.href = "login.html";
  }

  function bindLogout(buttonId = "logoutBtn") {
    const btn = document.getElementById(buttonId);
    if (!btn) return;
    btn.addEventListener("click", logout);
  }

  function showMessage(el, message, type = "error") {
    if (!el) return;
    el.className = "alert";
    el.classList.add(type === "success" ? "alert-success" : "alert-error");
    el.textContent = message;
    el.classList.remove("hidden");
  }

  function hideMessage(el) {
    if (!el) return;
    el.textContent = "";
    el.classList.add("hidden");
  }

  function formatPercent(value) {
    const num = Number(value || 0);
    return `${num.toFixed(2)}%`;
  }

  function getAuthHeaders(extraHeaders) {
    const token = getToken();
    const headers = Object.assign({}, extraHeaders || {});
    if (token) headers.Authorization = `Bearer ${token}`;
    return headers;
  }

  async function apiRequest(path, options = {}) {
    const {
      method = "GET",
      body,
      headers = {},
      auth = true,
      isFormData = false,
    } = options;

    const requestHeaders = Object.assign({}, headers);
    if (!isFormData && body !== undefined && !requestHeaders["Content-Type"]) {
      requestHeaders["Content-Type"] = "application/json";
    }

    const finalHeaders = auth ? getAuthHeaders(requestHeaders) : requestHeaders;

    let response;
    try {
      response = await fetch(`${API_BASE}${path}`, {
        method,
        headers: finalHeaders,
        body: body === undefined ? undefined : (isFormData ? body : JSON.stringify(body)),
      });
    } catch (networkError) {
      console.error("[IRIS][auth] Network error", networkError);
      throw new Error("Unable to connect to server. Please try again.");
    }

    let data = null;
    const text = await response.text();
    if (text) {
      try {
        data = JSON.parse(text);
      } catch (_parseError) {
        data = { message: text };
      }
    }

    if (response.status === 401 && auth) {
      console.warn("[IRIS][auth] Unauthorized response, logging out");
      logout();
      throw new Error("Session expired. Please login again.");
    }

    if (!response.ok) {
      const message = (data && (data.error || data.message)) || `Request failed (${response.status})`;
      const error = new Error(message);
      error.status = response.status;
      error.payload = data;
      throw error;
    }

    return data || {};
  }

  function requireAuth(expectedRoles) {
    const token = getToken();
    const role = getRole() || (getUser() && getUser().role) || "";

    if (!token) {
      window.location.href = "login.html";
      return null;
    }

    if (Array.isArray(expectedRoles) && expectedRoles.length && !expectedRoles.includes(role)) {
      redirectByRole(role);
      return null;
    }

    return {
      token,
      role,
      user: getUser(),
    };
  }

  async function handleLoginSubmit(event) {
    event.preventDefault();

    const messageEl = document.getElementById("authMessage");
    hideMessage(messageEl);

    const email = document.getElementById("email")?.value.trim();
    const password = document.getElementById("password")?.value || "";
    const selectedRole = document.getElementById("role")?.value || "";

    if (!email || !password) {
      showMessage(messageEl, "Email and password are required.", "error");
      return;
    }

    try {
      const response = await apiRequest("/auth/login", {
        method: "POST",
        auth: false,
        body: { email, password },
      });

      const role = response.role || (response.user && response.user.role) || "";
      const token = response.access_token;

      if (!token || !role) {
        throw new Error("Invalid login response from server.");
      }

      if (selectedRole && role !== selectedRole) {
        showMessage(messageEl, "Selected role does not match this account.", "error");
        return;
      }

      saveSession(token, role, response.user || null);
      redirectByRole(role);
    } catch (error) {
      console.error("[IRIS][auth] Login failed", error);
      showMessage(messageEl, error.message || "Login failed.", "error");
    }
  }

  async function handleRegisterSubmit(event) {
    event.preventDefault();

    const messageEl = document.getElementById("authMessage");
    hideMessage(messageEl);

    const name = document.getElementById("name")?.value.trim();
    const email = document.getElementById("email")?.value.trim();
    const password = document.getElementById("password")?.value || "";
    const role = document.getElementById("role")?.value || "";

    if (!name || !email || !password || !role) {
      showMessage(messageEl, "All fields are required.", "error");
      return;
    }

    try {
      const response = await apiRequest("/auth/register", {
        method: "POST",
        auth: false,
        body: { name, email, password, role },
      });

      console.log("[IRIS][auth] Register success", response);
      showMessage(messageEl, "Registration successful. Redirecting to login...", "success");
      setTimeout(() => {
        window.location.href = "login.html";
      }, 900);
    } catch (error) {
      console.error("[IRIS][auth] Register failed", error);
      showMessage(messageEl, error.message || "Registration failed.", "error");
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
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
    getAuthHeaders,
    getRole,
    getToken,
    getUser,
    hideMessage,
    logout,
    redirectByRole,
    requireAuth,
    saveSession,
    showMessage,
  };
})();
