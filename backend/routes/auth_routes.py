"""Authentication routes for the MaskTIF backend."""

import logging
import re

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from auth import hash_password, verify_password
from database import User, db
from limiter import limiter


logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

# Validation helpers
EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,30}$")


def _validate_password(password: str) -> str | None:
    """Return error message if invalid, else None."""
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if not re.search(r"[a-zA-Z]", password):
        return "Password must contain at least one letter"
    if not re.search(r"\d", password):
        return "Password must contain at least one digit"
    return None


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("10 per minute")
def register():
    """Register a new user account."""

    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return (
            jsonify({"message": "username, email and password are required"}),
            400,
        )

    # Input validation
    username = str(username).strip()
    email = str(email).strip().lower()
    if not USERNAME_RE.match(username):
        return jsonify({"message": "Username: 3-30 chars, alphanumeric and underscore only"}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"message": "Invalid email format"}), 400
    err = _validate_password(password)
    if err:
        return jsonify({"message": err}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
    )
    db.session.add(user)
    db.session.commit()

    logger.info("Registered new user: %s", username)
    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    """Authenticate a user and return a JWT token."""

    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not verify_password(user.password_hash, password):
        logger.warning("Failed login attempt for user: %s", username)
        return jsonify({"message": "Invalid username or password"}), 401

    access_token = create_access_token(identity=user.id)
    logger.info("User %s logged in successfully", username)
    return jsonify({"access_token": access_token}), 200

