"""Prediction endpoint for the MaskTIF backend."""

import logging
import os
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename

from config import Config
from database import Prediction, User, db
from limiter import limiter
from model_loader import predict_image


logger = logging.getLogger(__name__)

predict_bp = Blueprint("predict", __name__)

ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@predict_bp.route("/predict", methods=["POST"])
@jwt_required()
@limiter.limit("30 per minute")
def predict():
    """Run model inference on an uploaded image and persist the result."""

    try:
        if "image" not in request.files:
            return jsonify({"message": "Missing file field 'image'"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"message": "No file selected"}), 400

        # Input validation: allow only image files
        if not _allowed_file(file.filename):
            return jsonify(
                {"message": "Invalid file type. Allowed: png, jpg, jpeg, bmp, gif, webp"}
            ), 400

        # Ensure the user exists for the current JWT identity.
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user is None:
            return jsonify({"message": "User associated with token not found"}), 404

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        filename = secure_filename(file.filename) or "uploaded_image.png"
        # Add timestamp to avoid collisions.
        timestamp_str = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        name, ext = os.path.splitext(filename)
        final_filename = f"{name}_{timestamp_str}{ext or '.png'}"

        file_path = os.path.join(upload_folder, final_filename)
        file.save(file_path)

        predicted_person, confidence = predict_image(file_path)

        prediction = Prediction(
            user_id=user.id,
            image_path=file_path,
            predicted_person=predicted_person,
            confidence=confidence,
        )
        db.session.add(prediction)
        db.session.commit()

        return (
            jsonify(
                {
                    "predicted_person": predicted_person,
                    "confidence": confidence,
                }
            ),
            200,
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error while processing /predict request: %s", exc)
        return jsonify({"message": "Internal server error"}), 500

