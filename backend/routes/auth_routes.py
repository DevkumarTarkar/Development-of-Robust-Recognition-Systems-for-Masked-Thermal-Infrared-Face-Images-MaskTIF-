import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from auth import hash_password, verify_password
from database import User, db
from limiter import limiter

auth_bp = Blueprint("auth", __name__)

# ------------------------------------------
# register user
# ------------------------------------------
@auth_bp.route("/register", methods=["POST"])
@limiter.limit("10 per minute")
def register():

    data = request.get_json() or {}

    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", "")).strip()

    # validate empty fields
    if not username or not email or not password:
        return jsonify({
            "message": "Username, email and password are required"
        }), 400

    # email validation
    email_pattern = r"^[^@]+@[^@]+\.[^@]+$"

    if not re.match(email_pattern, email):
        return jsonify({
            "message": "Invalid email format"
        }), 400

    # password length check
    if len(password) < 6:
        return jsonify({
            "message": "Password must be at least 6 characters"
        }), 400

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

    print(f"New user registered: {username}")

    return jsonify({
        "message": "User registered successfully"
    }), 201


# ------------------------------------------
# login user
# ------------------------------------------
@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():

    data = request.get_json() or {}

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    if not username or not password:
        return jsonify({
            "message": "Username and password are required"
        }), 400

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

    print(f"User logged in: {username}")

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "username": user.username
    }), 200