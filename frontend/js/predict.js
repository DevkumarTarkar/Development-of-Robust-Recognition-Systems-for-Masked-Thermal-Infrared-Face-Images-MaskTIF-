function setupDashboard() {
  const form = document.getElementById('predict-form');
  const fileInput = document.getElementById('image-input');
  const preview = document.getElementById('image-preview');
  const resultDiv = document.getElementById('prediction-result');
  const alertId = 'dashboard-alert';

  fileInput.addEventListener('change', function () {
    const file = fileInput.files[0];
    if (!file) {
      preview.classList.add('d-none');
      preview.src = '';
      return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
      preview.src = e.target.result;
      preview.classList.remove('d-none');
    };
    reader.readAsDataURL(file);
  });

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    const file = fileInput.files[0];
    if (!file) {
      showAlert(alertId, 'Please choose an image first.', 'warning');
      return;
    }

    const token = getToken();
    if (!token) {
      showAlert(alertId, 'Session expired. Please log in again.', 'danger');
      setTimeout(() => (window.location.href = 'index.html'), 1000);
      return;
    }

    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: formData
      });

      const data = await response.json();

      if (response.status === 401) {
        showAlert(alertId, data.message || 'Unauthorized. Please log in again.', 'danger');
        setTimeout(() => (window.location.href = 'index.html'), 1000);
        return;
      }

      if (!response.ok) {
        showAlert(alertId, data.message || 'Prediction failed.', 'danger');
        return;
      }

      const person = data.predicted_person || 'Unknown';
      const confidence = data.confidence != null
        ? Math.round(data.confidence * 100)
        : null;

      resultDiv.innerHTML = `
        <h4 class="mb-3">Result</h4>
        <p class="fs-5"><strong>Predicted Person:</strong> ${person}</p>
        <p class="fs-5">
          <strong>Confidence:</strong> ${
            confidence !== null ? confidence + '%' : 'N/A'
          }
        </p>
      `;

      showAlert(alertId, 'Prediction successful.', 'success');
    } catch (error) {
      console.error(error);
      showAlert(alertId, 'Network error. Please try again.', 'danger');
    }
  });
}

