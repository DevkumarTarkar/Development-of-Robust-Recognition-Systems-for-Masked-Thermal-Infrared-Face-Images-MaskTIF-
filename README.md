# MaskTIF – Masked Thermal Infrared Face Recognition
![CI Pipeline](https://github.com/DevkumarTarkar/Development-of-Robust-Recognition-Systems-for-Masked-Thermal-Infrared-Face-Images-MaskTIF-/actions/workflows/ci.yml/badge.svg)
## Overview

MaskTIF is an end‑to‑end system for recognizing individuals from **thermal infrared face images**, even when faces are partially occluded by masks.  
The project includes:

- Dataset preprocessing and face cropping
- Synthetic mask generation and dataset organization
- Deep learning model training and evaluation with ResNet50 (PyTorch)
- A **Flask backend API** with JWT authentication and SQLite storage
- A **Bootstrap‑based frontend** for login, registration, and image‑based prediction

This repository can be used as a reference for research demos and small‑scale deployments of masked thermal face recognition.

---

## Core Features

- **Thermal face preprocessing**
  - Face cropping from raw images
  - Identity‑based directory organization
  - Train/validation/test splits
- **Synthetic mask generation**
  - Masks applied to thermal faces to simulate real‑world occlusions
- **Model training & evaluation**
  - ResNet50 backbone with 224×224 input
  - Accuracy, precision, recall, F1‑score, confusion matrix
- **Production‑style backend**
  - JWT‑secured `/predict` endpoint
  - Prediction history stored per user
- **Web frontend**
  - Login and registration
  - Dashboard with image upload, preview, and prediction result display

---

## High‑Level Architecture

- **Model layer**
  - ResNet50 trained on masked thermal infrared images
  - Weights stored in `models/masktif_model.pth`

- **Backend (Flask, PyTorch, SQLite)**
  - Loads the model once at startup
  - REST endpoints for `/register`, `/login`, and `/predict`
  - SQLite database (`masktif.db`) via SQLAlchemy with `users` and `predictions` tables

- **Frontend (HTML, Bootstrap, JavaScript)**
  - Auth pages (`index.html`, `register.html`)
  - Protected dashboard (`dashboard.html`) that calls the backend using Fetch API

---

## Project Structure

```text
MaskTIF_Project/
├── backend/
│   ├── app.py                # Flask app entrypoint
│   ├── auth.py               # Password hashing helpers
│   ├── config.py             # Backend configuration
│   ├── database.py           # SQLAlchemy models (User, Prediction)
│   ├── model_loader.py       # Load ResNet50 + run inference
│   ├── routes/
│   │   ├── auth_routes.py    # /register, /login
│   │   └── predict.py        # /predict (JWT‑protected)
│   └── uploads/              # Saved uploaded images
├── frontend/
│   ├── index.html            # Login page
│   ├── register.html         # Registration page
│   ├── dashboard.html        # Prediction dashboard
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── auth.js           # Auth + token handling
│       └── predict.js        # Image upload + predict
├── data/
│   ├── raw/                  # Original thermal dataset
│   └── masked/
│       ├── train/
│       ├── val/
│       └── test/
├── models/
│   └── masktif_model.pth     # Trained ResNet50 weights
├── src/
│   ├── crop_faces.py
│   ├── preprocess_images.py
│   ├── generate_masks.py
│   ├── train_model.py
│   ├── evaluate_model.py
│   └── export_model.py
├── config.py                  # Re‑exports backend.Config for tooling
├── README.md
└── requirements.txt           # Core training/runtime dependencies
```

---

## Backend API

### Tech Stack

- Flask
- Flask‑JWT‑Extended
- Flask‑SQLAlchemy / SQLAlchemy
- PyTorch, Torchvision
- Pillow

### Base URL

```text
http://127.0.0.1:5001
```

### `POST /register`

Registers a new user.

**Request JSON:**

```json
{
  "username": "dev_rajput",
  "email": "user@example.com",
  "password": "strongpassword"
}
```

### `POST /login`

Authenticates a user and returns a JWT token.

**Request JSON:**

```json
{
  "username": "dev_rajput",
  "password": "strongpassword"
}
```

**Response:**

```json
{
  "access_token": "<JWT_TOKEN_HERE>"
}
```

### `POST /predict` (JWT‑protected)

Runs inference on an uploaded thermal face image.

- Headers: `Authorization: Bearer <JWT_TOKEN_HERE>`
- Body: `multipart/form-data` with field `image` (file)

**Response:**

```json
{
  "predicted_person": "person_5",
  "confidence": 0.87
}
```

Each call also inserts a row into the `predictions` table with:

- `user_id`
- `image_path`
- `predicted_person`
- `confidence`
- `timestamp`

---

## Frontend

The frontend is a static web app (no framework) using **HTML, CSS, Bootstrap 5, and vanilla JavaScript**.

- `index.html` – login page (username, password)
- `register.html` – registration page (username, email, password)
- `dashboard.html` – protected page:
  - Upload image, preview it, send to `/predict`
  - Show predicted person + confidence

JWT tokens are stored in `localStorage` and automatically attached to `/predict` requests. If no token is found, the dashboard redirects back to the login page.

Frontend files are served with Python’s built‑in HTTP server.

---

## Installation & Setup

From the project root (`MaskTIF_Project/`):

```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows PowerShell
pip install -r requirements.txt
```

### Start the backend API

```bash
cd backend
python app.py
```

Server will run on `http://127.0.0.1:5001`.

### Start the frontend server

Open a second terminal:

```bash
cd frontend
python -m http.server 8000
```

Open the login page in your browser:

```text
http://127.0.0.1:8000/index.html
```

### Typical usage flow

1. Open the frontend and go to **Register**.
2. Register a new account.
3. Log in with the same username/password.
4. On successful login, you are redirected to `dashboard.html`.
5. Upload a thermal face image and click **Predict Face**.
6. View **Predicted Person** and **Confidence**; the prediction is stored in the database.

---

## Training & Evaluation

Training and evaluation scripts are under `src/`.

### Train the model

```bash
python src/train_model.py
```

### Evaluate the model

```bash
python src/evaluate_model.py
```

The evaluation script computes:

- Accuracy
- Precision
- Recall
- F1‑score
- Confusion matrix

Example results:

- Accuracy: **62.5%**
- Precision: **0.67**
- Recall: **0.63**
- F1‑score: **0.63**

### Export model for deployment

Export the trained model to PyTorch (.pth) and ONNX (.onnx) formats:

```bash
python src/export_model.py
```

Output:

- `models/masktif_model.pth` – PyTorch state dict (used by backend)
- `models/masktif_model.onnx` – ONNX format for other runtimes (TensorFlow, mobile, etc.)

---

## Security

- **Rate limiting** – Flask-Limiter: 10 req/min for `/register`, `/login`; 30 req/min for `/predict`
- **Security headers** – `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Strict-Transport-Security`
- **Input validation** – Email format, username (3–30 chars, alphanumeric), password (min 8 chars, letter + digit), allowed image types for upload
- **CORS** – Configured for frontend on a different port
- **Password hashing** – Werkzeug; no plain-text passwords
- **SQL injection** – SQLAlchemy ORM (parameterized queries)

---

## Dataset Overview

The dataset consists of thermal infrared face images for multiple identities. Each identity contains at least ~100 images to provide sufficient training data.

Raw layout:

```text
data/raw/
├── person_1/
├── person_2/
├── person_3/
├── person_4/
├── person_5/
├── person_6/
├── person_7/
└── person_8/
```

After preprocessing and mask generation:

```text
data/masked/
├── train/
├── val/
└── test/
```

---

## Future Improvements

- Larger and more diverse thermal datasets
- Real‑time webcam inference pipeline
- Role‑based access control and richer user management
- Deployment using a production WSGI server (Gunicorn/Uvicorn) behind Nginx
- Model optimization for edge devices (quantization, pruning)

---

## License

This project is licensed under the **MIT License**.  
See the [`LICENSE`](LICENSE) file for details.

---

## Author

**Dev Kumar Tarkar**

--- 

