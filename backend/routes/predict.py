"""Prediction endpoint for the MaskTIF backend."""

import logging
import os
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename

from database import Prediction, User, db
from model_loader import predict_image


logger = logging.getLogger(__name__)

predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/predict", methods=["POST"])
@jwt_required()
def predict():
    """Run model inference on an uploaded image and persist the result."""

    try:
        if "image" not in request.files:
            return jsonify({"message": "Missing file field 'image'"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"message": "No file selected"}), 400

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

