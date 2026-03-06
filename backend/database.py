"""Database models and SQLAlchemy instance for the MaskTIF backend."""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

# Global SQLAlchemy instance to be initialized by the application factory.
db = SQLAlchemy()


class User(db.Model):
    """User account model for authentication."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    predictions = db.relationship("Prediction", backref="user", lazy=True)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class Prediction(db.Model):
    """Stores each model inference request and its result."""

    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    predicted_person = db.Column(db.String(120), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Prediction user_id={self.user_id} label={self.predicted_person}>"

