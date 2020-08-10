"""module containing helpers functions"""

import logging
import hashlib
import uuid

from persistence import get_user_credentials, get_email_entry, get_username_entry, hash_password

LOGGER = logging.getLogger(__name__)


def is_authenticated_user(user: str, password: str) -> bool:
    """Helper function used to determine is user
    is authenticated"""
    credentials = get_user_credentials(user)
    if not credentials:
        return False
    hashed_password = dict(credentials)['password']
    return check_password(hashed_password, password)

def email_in_use(email: str) -> bool:
    """Helper function used to check if a particular email
    address is already in use"""
    return bool(get_email_entry(email))

def username_in_use(username: str) -> bool:
    """Helper function used to check if a username is already
    in use"""
    return bool(get_username_entry(username))

def check_password(hashed_password: str, user_password: str) -> bool: # pragma: no cover
    """Function used to check that password hash
    matches user password

    Arguments:
        hashed_password: str hashed password
        user_password: user password from database
    Returns:
        true if passwords match else false
    """

    try:
        password, salt = hashed_password.split(':')
        return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()
    except (KeyError, AttributeError):
        return False