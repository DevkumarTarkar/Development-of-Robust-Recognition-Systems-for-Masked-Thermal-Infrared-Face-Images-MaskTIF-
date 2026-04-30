import re
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token

from auth import hash_password, verify_password
from database import User, db
from limiter import limiter

auth_bp = Blueprint("auth", __name__)


def _is_json_request() -> bool:
    ct = (request.headers.get("Content-Type") or "").lower()
    return "application/json" in ct


def _validate_username(username: str) -> str | None:
    # 3-32 chars; letters, numbers, underscore, dot only.
    if not (3 <= len(username) <= 32):
        return "Username must be 3 to 32 characters long"
    if not re.fullmatch(r"[a-zA-Z0-9_.]+", username):
        return "Username may contain letters, numbers, underscore, and dot only"
    return None


def _validate_email(email: str) -> str | None:
    if len(email) > 120:
        return "Email is too long"
    email_pattern = r"^[^@]+@[^@]+\.[^@]+$"
    if not re.match(email_pattern, email):
        return "Invalid email format"
    return None


def _validate_password(password: str) -> str | None:
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if len(password) > 128:
        return "Password is too long"
    # Basic strength: at least 1 letter and 1 number
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return "Password must include at least one letter and one number"
    return None


# ------------------------------------------
# register user
# ------------------------------------------
@auth_bp.route("/register", methods=["POST"])
@limiter.limit("10 per minute")
def register():

    if not _is_json_request():
        return jsonify({"message": "Content-Type must be application/json"}), 415

    data = request.get_json() or {}

    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", "")).strip()

    # validate empty fields
    if not username or not email or not password:
        return jsonify({
            "message": "Username, email and password are required"
        }), 400

    u_err = _validate_username(username)
    if u_err:
        return jsonify({"message": u_err}), 400

    e_err = _validate_email(email)
    if e_err:
        return jsonify({"message": e_err}), 400

    p_err = _validate_password(password)
    if p_err:
        return jsonify({"message": p_err}), 400

    # duplicate checks
    if User.query.filter_by(username=username).first():
        return jsonify({
            "message": "Username already exists"
        }), 400

    if User.query.filter_by(email=email).first():
        return jsonify({
            "message": "Email already exists"
        }), 400

    # create user
    new_user = User(
        username=username,
        email=email,
        password_hash=hash_password(password)
    )

    db.session.add(new_user)
    db.session.commit()

    current_app.logger.info("New user registered: %s", username)

    return jsonify({
        "message": "User registered successfully"
    }), 201


# ------------------------------------------
# login user
# ------------------------------------------
@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():

    if not _is_json_request():
        return jsonify({"message": "Content-Type must be application/json"}), 415

    data = request.get_json() or {}

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    if not username or not password:
        return jsonify({
            "message": "Username and password are required"
        }), 400

    u_err = _validate_username(username)
    if u_err:
        # Keep generic so we don't leak exact validation rules on login
        return jsonify({"message": "Invalid username or password"}), 401

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({
            "message": "Invalid username or password"
        }), 401

    if not verify_password(user.password_hash, password):
        return jsonify({
            "message": "Invalid username or password"
        }), 401

    access_token = create_access_token(
        identity=str(user.id)
    )

    current_app.logger.info("User logged in: %s", username)

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "username": user.username
    }), 200