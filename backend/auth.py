"""Authentication helpers for the MaskTIF backend.

This module is responsible for password hashing and verification utilities.
"""

from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(plain_password: str) -> str:
    """Return a secure password hash for the given plain text password."""

    return generate_password_hash(plain_password)


def verify_password(password_hash: str, candidate_password: str) -> bool:
    """Verify a plain text password against the stored password hash."""

    return check_password_hash(password_hash, candidate_password)

