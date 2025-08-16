import re

def verify_username(username: str) -> bool:
    """
    Verifies that the username:
    - Is between 3 and 20 characters
    - Contains only letters, numbers, underscores, or dots
    - Starts with a letter
    """
    if not isinstance(username, str):
        return False
    if not (3 <= len(username) <= 20):
        return False
    if not re.match(r'^[A-Za-z][A-Za-z0-9_.]*$', username):
        return False
    return True

def verify_password(password: str) -> bool:
    """
    Verifies that the password:
    - Is at least 8 characters
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    """
    if not isinstance(password, str):
        return False
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

