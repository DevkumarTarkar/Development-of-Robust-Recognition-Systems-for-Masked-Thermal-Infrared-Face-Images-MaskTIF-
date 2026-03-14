const API_BASE_URL = 'https://masktif-api.onrender.com';
const TOKEN_KEY = 'masktif_jwt_token';

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function logout() {
  localStorage.removeItem(TOKEN_KEY);
  window.location.href = 'index.html';
}

function requireAuth() {
  const token = getToken();
  if (!token) {
    window.location.href = 'index.html';
  }
}

function showAlert(elementId, message, type = 'danger') {
  const el = document.getElementById(elementId);
  if (!el) return;

  el.className = `alert alert-${type}`;
  el.textContent = message;
  el.classList.remove('d-none');
}

function setupLoginPage() {
  const form = document.getElementById('login-form');
  const alertId = 'login-alert';

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value.trim();

    if (!username || !password) {
      showAlert(alertId, 'Please enter username and password.', 'warning');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (!response.ok) {
        showAlert(alertId, data.message || 'Login failed.', 'danger');
        return;
      }

      if (!data.access_token) {
        showAlert(alertId, 'No token received from server.', 'danger');
        return;
      }

      setToken(data.access_token);
      window.location.href = 'dashboard.html';
    } catch (error) {
      console.error(error);
      showAlert(alertId, 'Network error. Please try again.', 'danger');
    }
  });
}

function setupRegisterPage() {
  const form = document.getElementById('register-form');
  const alertId = 'register-alert';

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    const username = document.getElementById('reg-username').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value.trim();

    if (!username || !email || !password) {
      showAlert(alertId, 'Please fill all fields.', 'warning');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
      });

      const data = await response.json();

      if (!response.ok) {
        showAlert(alertId, data.message || 'Registration failed.', 'danger');
        return;
      }

      showAlert(alertId, 'Registration successful. Redirecting to login...', 'success');

      setTimeout(() => {
        window.location.href = 'index.html';
      }, 1500);
    } catch (error) {
      console.error(error);
      showAlert(alertId, 'Network error. Please try again.', 'danger');
    }
  });
}

document.addEventListener('DOMContentLoaded', function () {
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }
});

