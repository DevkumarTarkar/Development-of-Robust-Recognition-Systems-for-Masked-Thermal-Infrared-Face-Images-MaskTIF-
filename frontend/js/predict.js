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

  const historyLoading =
    document.getElementById(
      "history-loading"
    );

  const historyEmpty =
    document.getElementById(
      "history-empty"
    );

  const historyTable =
    document.getElementById(
      "history-table"
    );

  const historyTbody =
    document.getElementById(
      "history-tbody"
    );

  const refreshBtn =
    document.getElementById(
      "refresh-history-btn"
    );

  if (
    !form ||
    !fileInput ||
    !preview ||
    !resultDiv
  ) {
    return;
  }

  function formatTime(iso) {
    if (!iso) return "-";
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    return d.toLocaleString();
  }

  function fileNameFromPath(path) {
    if (!path) return "-";
    const normalized = String(path).replaceAll("\\", "/");
    const parts = normalized.split("/");
    return parts[parts.length - 1] || normalized;
  }

  function setHistoryState(state) {
    // state: "loading" | "empty" | "table"
    if (historyLoading) {
      historyLoading.classList.toggle(
        "d-none",
        state !== "loading"
      );
    }
    if (historyEmpty) {
      historyEmpty.classList.toggle(
        "d-none",
        state !== "empty"
      );
    }
    if (historyTable) {
      historyTable.classList.toggle(
        "d-none",
        state !== "table"
      );
    }
  }

  function renderHistory(items) {
    if (!historyTbody) return;
    historyTbody.textContent = "";

    if (!items || items.length === 0) {
      setHistoryState("empty");
      return;
    }

    for (const p of items) {
      const tr = document.createElement("tr");

      const tdTime = document.createElement("td");
      tdTime.className = "text-warning";
      tdTime.textContent = formatTime(p.timestamp);

      const tdPerson = document.createElement("td");
      tdPerson.textContent = p.predicted_person || "Unknown";

      const tdConf = document.createElement("td");
      const conf =
        p.confidence !== null &&
        p.confidence !== undefined
          ? Math.round(p.confidence * 100)
          : null;

      const badge = document.createElement("span");
      badge.className = "badge";
      if (conf === null) {
        badge.classList.add("bg-secondary");
        badge.textContent = "N/A";
      } else if (conf >= 70) {
        badge.classList.add("bg-success");
        badge.textContent = `${conf}%`;
      } else if (conf >= 50) {
        badge.classList.add("bg-warning", "text-dark");
        badge.textContent = `${conf}%`;
      } else {
        badge.classList.add("bg-danger");
        badge.textContent = `${conf}%`;
      }
      tdConf.appendChild(badge);

      const tdFile = document.createElement("td");
      tdFile.className = "text-warning";
      tdFile.textContent = fileNameFromPath(p.image_path);

      tr.appendChild(tdTime);
      tr.appendChild(tdPerson);
      tr.appendChild(tdConf);
      tr.appendChild(tdFile);
      historyTbody.appendChild(tr);
    }

    setHistoryState("table");
  }

  async function loadHistory() {
    const token = getToken();
    if (!token) return;

    setHistoryState("loading");
    try {
      const resp = await fetch(
        `${API_BASE_URL}/predictions?limit=10`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      const data = await readJsonSafely(
        resp
      );

      if (resp.status === 401) {
        setHistoryState("empty");
        return;
      }

      if (!resp.ok) {
        setHistoryState("empty");
        showAlert(
          alertId,
          data?.message ||
            "Failed to load prediction history.",
          "warning"
        );
        return;
      }

      renderHistory(data?.items || []);
    } catch (e) {
      console.error(e);
      setHistoryState("empty");
    }
  }

  if (refreshBtn) {
    refreshBtn.addEventListener(
      "click",
      function () {
        loadHistory();
      }
    );
  }

  // Initial history load
  loadHistory();


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

      resultDiv.textContent = "";
      const runningP = document.createElement("p");
      runningP.className = "text-warning";
      runningP.textContent = "Running AI prediction...";
      resultDiv.appendChild(runningP);

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

        resultDiv.textContent = "";
        const wrap = document.createElement("div");
        wrap.className = "text-center";

        const h4 = document.createElement("h4");
        h4.className = "mb-3";
        h4.textContent = "Prediction Result";

        const h2 = document.createElement("h2");
        h2.className = "mb-3";
        h2.textContent = person;

        const badge = document.createElement("span");
        badge.className = `badge ${badgeClass} fs-6 px-3 py-2`;
        const confText =
          confidence !== null &&
          confidence !== undefined
            ? `${confidence}%`
            : "N/A";
        badge.textContent = `Confidence: ${confText}`;

        const fileP = document.createElement("p");
        fileP.className = "mt-4 text-warning";
        fileP.textContent = `File: ${data?.image_name || file.name}`;

        wrap.appendChild(h4);
        wrap.appendChild(h2);
        wrap.appendChild(badge);
        wrap.appendChild(fileP);
        resultDiv.appendChild(wrap);

        showAlert(
          alertId,
          "Prediction successful.",
          "success"
        );

        // Refresh history so UI shows DB storage -> display flow
        loadHistory();

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