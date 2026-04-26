from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# ------------------------------------------
# database object
# ------------------------------------------
db = SQLAlchemy()


# ------------------------------------------
# user table
# ------------------------------------------
class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    predictions = db.relationship(
        "Prediction",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def as_dict(self):

        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat()
        }


# ------------------------------------------
# prediction history table
# ------------------------------------------
class Prediction(db.Model):

    __tablename__ = "predictions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    image_path = db.Column(
        db.String(255),
        nullable=False
    )

    predicted_person = db.Column(
        db.String(120),
        nullable=False
    )

    confidence = db.Column(
        db.Float,
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def as_dict(self):

        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_path": self.image_path,
            "predicted_person": self.predicted_person,
            "confidence": round(
                float(self.confidence), 2
            ),
            "timestamp": self.timestamp.isoformat()
        }