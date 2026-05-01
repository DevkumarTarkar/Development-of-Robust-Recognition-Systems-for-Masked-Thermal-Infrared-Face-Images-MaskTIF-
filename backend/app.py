import logging
import os
from typing import Any

from flask import Flask, jsonify, request
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

def _cors_origins_from_env() -> list[str]:
    raw = os.environ.get("CORS_ORIGINS", "").strip()
    if not raw:
        return [
            "http://localhost:5500",
            "http://127.0.0.1:5500",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "https://masktif-face-recognition.vercel.app"
        ]
    return [o.strip() for o in raw.split(",") if o.strip()]


def _add_security_headers(resp):
    # Minimal baseline for an API + static frontend hosted separately.
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "DENY")
    resp.headers.setdefault("Referrer-Policy", "no-referrer")
    resp.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    # Tight CSP for API responses (no scripts/styles expected here).
    resp.headers.setdefault("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
    return resp


def create_app(config_object: Any = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    JWTManager(app)

    app.config.setdefault("RATELIMIT_STORAGE_URI", config_object.RATELIMIT_STORAGE_URI)
    limiter.init_app(app)

    CORS(app, resources={r"/*": {"origins": _cors_origins_from_env()}})

    app.after_request(_add_security_headers)

    @app.before_request
    def _log_request():
        if request.path in ("/health", "/"):
            return
        app.logger.info("%s %s", request.method, request.path)

    app.register_blueprint(auth_bp)
    app.register_blueprint(predict_bp)

    @app.route("/", methods=["GET"])
    def home():
        return jsonify({"message": "MaskTIF Backend Running"}), 200

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "database": "connected", "model": "lazy-load enabled"}), 200

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Route not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    with app.app_context():
        db.create_all()
        app.logger.info("Database initialized")
        app.logger.info("ML model will load on first prediction request")

    return app


app = create_app()

# ---------------------------------------------------
# run server
# ---------------------------------------------------
if __name__ == "__main__":
    app.logger.info("Server started on port 5001")
    app.run(host="0.0.0.0", port=5001, debug=False)