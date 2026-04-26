import os
from datetime import datetime

from flask import (
    Blueprint,
    request,
    jsonify,
    current_app
)

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from werkzeug.utils import secure_filename

from config import Config
from database import db, User, Prediction
from limiter import limiter
from model_loader import predict_image


# ------------------------------------------
# blueprint
# ------------------------------------------
predict_bp = Blueprint(
    "predict",
    __name__
)

ALLOWED_EXTENSIONS = (
    Config.ALLOWED_EXTENSIONS
)


# ------------------------------------------
# validate file extension
# ------------------------------------------
def allowed_file(filename):

    return (
        "." in filename and
        filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ------------------------------------------
# predict route
# ------------------------------------------
@predict_bp.route(
    "/predict",
    methods=["POST"]
)
@jwt_required()
@limiter.limit("30 per minute")
def predict():

    try:

        # check image field
        if "image" not in request.files:

            return jsonify({
                "message":
                "Image file is required"
            }), 400

        file = request.files["image"]

        # empty filename
        if file.filename == "":

            return jsonify({
                "message":
                "No file selected"
            }), 400

        # file extension check
        if not allowed_file(
            file.filename
        ):

            return jsonify({
                "message":
                "Invalid file type"
            }), 400

        # max file size 5 MB
        if (
            request.content_length and
            request.content_length >
            5 * 1024 * 1024
        ):

            return jsonify({
                "message":
                "File too large"
            }), 400

        # current user
        user_id = get_jwt_identity()

        user = db.session.get(
            User,
            int(user_id)
        )

        if not user:

            return jsonify({
                "message":
                "User not found"
            }), 404

        # upload folder
        upload_folder = (
            current_app.config[
                "UPLOAD_FOLDER"
            ]
        )

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        # secure filename
        filename = secure_filename(
            file.filename
        )

        if not filename:
            filename = "image.jpg"

        # unique name
        timestamp = (
            datetime.utcnow()
            .strftime(
                "%Y%m%d%H%M%S%f"
            )
        )

        name, ext = os.path.splitext(
            filename
        )

        final_filename = (
            f"{name}_{timestamp}{ext}"
        )

        file_path = os.path.join(
            upload_folder,
            final_filename
        )

        # save file
        file.save(file_path)

        # run model
        predicted_person, confidence = (
            predict_image(file_path)
        )

        # save database history
        new_prediction = Prediction(
            user_id=user.id,
            image_path=file_path,
            predicted_person=(
                predicted_person
            ),
            confidence=float(
                confidence
            )
        )

        db.session.add(
            new_prediction
        )

        db.session.commit()

        # success response
        return jsonify({

            "message":
            "Prediction successful",

            "predicted_person":
            predicted_person,

            "confidence":
            round(
                float(confidence),
                2
            ),

            "image_name":
            final_filename

        }), 200

    except Exception as error:

        current_app.logger.error(
            f"Prediction error: "
            f"{str(error)}"
        )

        return jsonify({
            "message":
            "Internal server error"
        }), 500