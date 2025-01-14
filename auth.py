# Relevant documentation:
# Werkzeug Security: https://werkzeug.palletsprojects.com/en/2.0.x/utils/#module-werkzeug.security

# File to handle authentication of users

from werkzeug.security import generate_password_hash, check_password_hash
from models import add_user, get_user

def create_user(username, password, role):
    """Create a new user with a hashed password."""
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    add_user(username, hashed_password, role)

def authenticate_user(username, password):
    """Authenticate a user by username and password."""
    user = get_user(username)
    if user and check_password_hash(user.password, password):
        return user
    return None
