from werkzeug.security import generate_password_hash, check_password_hash


# ------------------------------------------
# create hashed password before storing
# ------------------------------------------
def hash_password(password):
    return generate_password_hash(password)


# ------------------------------------------
# verify password during login
# ------------------------------------------
def verify_password(stored_hash, password):
    return check_password_hash(stored_hash, password)
