import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from database import db
from limiter import limiter
from routes.auth_routes import auth_bp
from routes.predict import predict_bp

# ---------------------------------------------------
# basic logging setup
# ---------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------------------------------------------
# create flask app
# ---------------------------------------------------
app = Flask(__name__)
app.config.from_object(Config)

# ---------------------------------------------------
# create upload folder if not present
# ---------------------------------------------------
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ---------------------------------------------------
# initialize extensions
# ---------------------------------------------------
db.init_app(app)
JWTManager(app)

app.config.setdefault(
    "RATELIMIT_STORAGE_URI",
    Config.RATELIMIT_STORAGE_URI
)

limiter.init_app(app)

# ---------------------------------------------------
# allow frontend requests
# ---------------------------------------------------
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5500",
                "http://127.0.0.1:5500",
                "https://your-frontend-url.onrender.com"
            ]
        }
    }
)

# ---------------------------------------------------
# register routes
# ---------------------------------------------------
app.register_blueprint(auth_bp)
app.register_blueprint(predict_bp)

# ---------------------------------------------------
# home route
# ---------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "MaskTIF Backend Running"
    }), 200

# ---------------------------------------------------
# health route
# ---------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "database": "connected",
        "model": "lazy-load enabled"
    }), 200

# ---------------------------------------------------
# 404 error
# ---------------------------------------------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Route not found"
    }), 404

# ---------------------------------------------------
# 500 error
# ---------------------------------------------------
@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error"
    }), 500

# ---------------------------------------------------
# startup tasks
# ---------------------------------------------------
with app.app_context():
    db.create_all()
    logging.info("Database initialized")
    logging.info("ML model will load on first prediction request")

# ---------------------------------------------------
# run server
# ---------------------------------------------------
if __name__ == "__main__":
    logging.info("Server started on port 5001")

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=False
    )