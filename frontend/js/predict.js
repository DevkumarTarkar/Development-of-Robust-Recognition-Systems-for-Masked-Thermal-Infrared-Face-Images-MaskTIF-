function setupDashboard() {
  const form =
    document.getElementById(
      "predict-form"
    );

  const fileInput =
    document.getElementById(
      "image-input"
    );

  const preview =
    document.getElementById(
      "image-preview"
    );

  const resultDiv =
    document.getElementById(
      "prediction-result"
    );

  const alertId =
    "dashboard-alert";

  if (
    !form ||
    !fileInput ||
    !preview ||
    !resultDiv
  ) {
    return;
  }


  /* ------------------------------------------
     image preview
  ------------------------------------------ */
  fileInput.addEventListener(
    "change",
    function () {

      const file =
        fileInput.files[0];

      if (!file) {
        preview.src = "";
        preview.classList.add(
          "d-none"
        );
        return;
      }

      const reader =
        new FileReader();

      reader.onload =
        function (event) {

          preview.src =
            event.target.result;

          preview.classList.remove(
            "d-none"
          );
        };

      reader.readAsDataURL(
        file
      );
    }
  );


  /* ------------------------------------------
     submit predict form
  ------------------------------------------ */
  form.addEventListener(
    "submit",
    async function (e) {

      e.preventDefault();

      const file =
        fileInput.files[0];

      if (!file) {
        showAlert(
          alertId,
          "Please choose an image first.",
          "warning"
        );
        return;
      }

      const token =
        getToken();

      if (!token) {

        showAlert(
          alertId,
          "Session expired. Please login again.",
          "danger"
        );

        setTimeout(() => {
          window.location.href =
            "index.html";
        }, 1000);

        return;
      }

      const submitBtn =
        form.querySelector(
          "button[type='submit']"
        );

      const oldBtnText =
        submitBtn.innerHTML;

      submitBtn.disabled =
        true;

      submitBtn.innerHTML =
        `<span class="spinner-border spinner-border-sm me-2"></span>Predicting...`;

      resultDiv.innerHTML = `
        <p class="text-muted">
          Running AI prediction...
        </p>
      `;

      const formData =
        new FormData();

      formData.append(
        "image",
        file
      );

      try {

        const response =
          await fetch(
            `${API_BASE_URL}/predict`,
            {
              method: "POST",

              headers: {
                Authorization:
                  `Bearer ${token}`
              },

              body: formData
            }
          );

        const data =
          await readJsonSafely(
            response
          );

        if (
          response.status === 401
        ) {

          showAlert(
            alertId,
            "Unauthorized. Please login again.",
            "danger"
          );

          setTimeout(() => {
            window.location.href =
              "index.html";
          }, 1000);

          return;
        }

        if (!response.ok) {

          showAlert(
            alertId,
            data?.message ||
              "Prediction failed.",
            "danger"
          );

          resultDiv.innerHTML = `
            <p class="text-danger">
              Failed to predict image.
            </p>
          `;

          return;
        }

        const person =
          data.predicted_person ||
          "Unknown";

        let confidence =
          data.confidence;

        if (
          confidence !== null &&
          confidence !== undefined
        ) {
          confidence =
            Math.round(
              confidence * 100
            );
        }

        let badgeClass =
          "bg-success";

        if (
          confidence < 70
        ) {
          badgeClass =
            "bg-warning text-dark";
        }

        if (
          confidence < 50
        ) {
          badgeClass =
            "bg-danger";
        }

        resultDiv.innerHTML = `
          <div class="text-center">

            <h4 class="mb-3">
              Prediction Result
            </h4>

            <h2 class="mb-3">
              ${person}
            </h2>

            <span class="badge ${badgeClass} fs-6 px-3 py-2">
              Confidence:
              ${
                confidence !==
                  null &&
                confidence !==
                  undefined
                  ? confidence +
                    "%"
                  : "N/A"
              }
            </span>

            <p class="mt-4 text-muted">
              File:
              ${
                data.image_name ||
                file.name
              }
            </p>

          </div>
        `;

        showAlert(
          alertId,
          "Prediction successful.",
          "success"
        );

      } catch (error) {

        console.error(
          error
        );

        showAlert(
          alertId,
          "Network error. Please try again.",
          "danger"
        );

        resultDiv.innerHTML = `
          <p class="text-danger">
            Network error occurred.
          </p>
        `;

      } finally {

        submitBtn.disabled =
          false;

        submitBtn.innerHTML =
          oldBtnText;
      }
    }
  );


  /* ------------------------------------------
     welcome username
  ------------------------------------------ */
  const navbarBrand =
    document.querySelector(
      ".navbar-brand"
    );

  const username =
    getUsername();

  if (
    username &&
    navbarBrand
  ) {
    navbarBrand.textContent =
      `MaskTIF | ${username}`;
  }
}