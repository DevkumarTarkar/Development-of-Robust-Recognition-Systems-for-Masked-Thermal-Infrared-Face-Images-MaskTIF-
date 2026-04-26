const API_BASE_URL = "http://127.0.0.1:5001";
const TOKEN_KEY = "masktif_jwt_token";
const USERNAME_KEY = "masktif_username";

/* ------------------------------------------
   token management
------------------------------------------ */
function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function removeToken() {
  localStorage.removeItem(TOKEN_KEY);
}

/* ------------------------------------------
   username management
------------------------------------------ */
function setUsername(username) {
  localStorage.setItem(USERNAME_KEY, username);
}

function getUsername() {
  return localStorage.getItem(USERNAME_KEY);
}

function removeUsername() {
  localStorage.removeItem(USERNAME_KEY);
}

/* ------------------------------------------
   logout
------------------------------------------ */
function logout() {
  removeToken();
  removeUsername();
  window.location.href = "index.html";
}

/* ------------------------------------------
   require auth
------------------------------------------ */
function requireAuth() {
  const token = getToken();

  if (!token) {
    window.location.href = "index.html";
  }
}

/* ------------------------------------------
   alert helper
------------------------------------------ */
function showAlert(elementId, message, type = "danger") {
  const alertBox = document.getElementById(elementId);

  if (!alertBox) return;

  alertBox.className = `alert alert-${type}`;
  alertBox.textContent = message;
  alertBox.classList.remove("d-none");
}

/* ------------------------------------------
   hide alert
------------------------------------------ */
function hideAlert(elementId) {
  const alertBox = document.getElementById(elementId);

  if (!alertBox) return;

  alertBox.classList.add("d-none");
}

/* ------------------------------------------
   safe json parse
------------------------------------------ */
async function readJsonSafely(response) {
  try {
    return await response.json();
  } catch (error) {
    return null;
  }
}

/* ------------------------------------------
   readable api errors
------------------------------------------ */
function getApiErrorMessage(response, data, fallback) {
  if (data && data.message && typeof data.message === "string") {
    return data.message;
  }

  if (response.status === 401) return "Invalid credentials.";
  if (response.status === 404) return "API route not found.";
  if (response.status >= 500) return "Server error. Try again.";

  return fallback;
}

/* ------------------------------------------
   loading button
------------------------------------------ */
function setButtonLoading(button, text) {
  button.disabled = true;
  button.dataset.oldText = button.innerHTML;

  button.innerHTML =
    `<span class="spinner-border spinner-border-sm me-2"></span>${text}`;
}

function resetButton(button) {
  button.disabled = false;

  if (button.dataset.oldText) {
    button.innerHTML = button.dataset.oldText;
  }
}

/* ------------------------------------------
   login page
------------------------------------------ */
function setupLoginPage() {
  const form = document.getElementById("login-form");

  if (!form) return;

  const alertId = "login-alert";

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    hideAlert(alertId);

    const username = document
      .getElementById("login-username")
      .value.trim();

    const password = document
      .getElementById("login-password")
      .value.trim();

    const button = form.querySelector("button[type='submit']");

    if (!username || !password) {
      showAlert(alertId, "Please enter username and password.", "warning");
      return;
    }

    try {
      setButtonLoading(button, "Logging in...");

      const response = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          username,
          password
        })
      });

      const data = await readJsonSafely(response);

      if (!response.ok) {
        showAlert(
          alertId,
          getApiErrorMessage(response, data, "Login failed."),
          "danger"
        );
        resetButton(button);
        return;
      }

      if (!data || !data.access_token) {
        showAlert(alertId, "No token received.", "danger");
        resetButton(button);
        return;
      }

      setToken(data.access_token);
      setUsername(data.username || username);

      showAlert(alertId, "Login successful!", "success");

      // 🔥 FINAL FIX
      resetButton(button);
      window.location.href = "dashboard.html";

    } catch (error) {
      console.error(error);

      showAlert(alertId, "Network error. Try again.", "danger");
      resetButton(button);
    }
  });
}

/* ------------------------------------------
   register page
------------------------------------------ */
function setupRegisterPage() {
  const form = document.getElementById("register-form");

  if (!form) return;

  const alertId = "register-alert";

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    hideAlert(alertId);

    const username = document
      .getElementById("reg-username")
      .value.trim();

    const email = document
      .getElementById("reg-email")
      .value.trim();

    const password = document
      .getElementById("reg-password")
      .value.trim();

    const button = form.querySelector("button[type='submit']");

    if (!username || !email || !password) {
      showAlert(alertId, "Please fill all fields.", "warning");
      return;
    }

    if (password.length < 6) {
      showAlert(
        alertId,
        "Password must be at least 6 characters.",
        "warning"
      );
      return;
    }

    try {
      setButtonLoading(button, "Creating...");

      const response = await fetch(`${API_BASE_URL}/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          username,
          email,
          password
        })
      });

      const data = await readJsonSafely(response);

      if (!response.ok) {
        showAlert(
          alertId,
          getApiErrorMessage(response, data, "Registration failed."),
          "danger"
        );
        resetButton(button);
        return;
      }

      showAlert(
        alertId,
        "Registration successful! Redirecting...",
        "success"
      );

      resetButton(button);

      setTimeout(() => {
        window.location.href = "index.html";
      }, 1200);

    } catch (error) {
      console.error(error);

      showAlert(alertId, "Network error. Try again.", "danger");
      resetButton(button);
    }
  });
}

/* ------------------------------------------
   page load
------------------------------------------ */
document.addEventListener("DOMContentLoaded", function () {
  setupLoginPage();
  setupRegisterPage();

  const logoutBtn = document.getElementById("logout-btn");

  if (logoutBtn) {
    logoutBtn.addEventListener("click", logout);
  }
});