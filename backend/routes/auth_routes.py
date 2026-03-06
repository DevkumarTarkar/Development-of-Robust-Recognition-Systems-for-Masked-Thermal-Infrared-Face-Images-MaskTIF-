"""Authentication routes for the MaskTIF backend."""

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from auth import hash_password, verify_password
from database import User, db


logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
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

