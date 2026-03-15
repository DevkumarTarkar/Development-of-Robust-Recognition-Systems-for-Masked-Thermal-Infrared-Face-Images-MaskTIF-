"""Flask application entry point for the MaskTIF backend API."""

import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from database import db
from limiter import limiter
from model_loader import load_model


def configure_logging(app: Flask) -> None:
    """Configure application-wide logging with a rotating file handler."""

    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "app.log")

    handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)


def create_app() -> Flask:
    """Application factory to create and configure the Flask app."""

    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Configure logging before other components so they can log during init
    configure_logging(app)

    # Initialize database, JWT, and rate limiter
    db.init_app(app)
    JWTManager(app)
    app.config.setdefault("RATELIMIT_STORAGE_URI", Config.RATELIMIT_STORAGE_URI)
    limiter.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Import and register blueprints
    from routes.auth_routes import auth_bp
    from routes.predict import predict_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(predict_bp)

    @app.after_request
    def add_headers(response):
        """Security headers."""

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response

    @app.route("/health", methods=["GET"])
    def health():
        """Simple health check endpoint."""

        return jsonify({"status": "ok"}), 200

    # Error handlers for cleaner error responses
    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning("404 error: %s", error)
        return jsonify({"message": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error("500 error: %s", error)
        return jsonify({"message": "Internal server error"}), 500

    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        # Load the model once at startup
        load_model()
        app.logger.info("Application startup complete; model loaded.")

    return app


app = create_app()


if __name__ == "__main__":
    # Running with debug=False avoids duplicate startup when using the reloader.
    # Use port 5001 to avoid conflicts with any other service on 5000.
    app.run(host="0.0.0.0", port=5001, debug=False)

