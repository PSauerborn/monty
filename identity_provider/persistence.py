"""Module containing persistence functions used to connect
to postgres server"""

import logging
import uuid
import hashlib

from datetime import timedelta, datetime
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

from config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

LOGGER = logging.getLogger(__name__)

@contextmanager
def persistence():
    """Function used to create postgres persistence
    connection. Persistence connections are returned
    as conext managers"""
    connection = None
    try:
        LOGGER.debug('connecting to postgres at %s:%s', POSTGRES_HOST, POSTGRES_PORT)
        connection = psycopg2.connect(f'host={POSTGRES_HOST} port={POSTGRES_PORT} '
                               f'dbname={POSTGRES_DB} user={POSTGRES_USER} '
                               f'password={POSTGRES_PASSWORD}')
        yield connection
    except Exception:
        LOGGER.exception('unable to connect to postgres server')
        raise
    finally:
        if connection is not None:
            connection.close()

def database_function(func: object):
    """Wrapper used to insert database connection
    and cursor into function call arguments"""
    def wrapper(*args: tuple, **kwargs: dict):
        with persistence() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            return func(conn, cursor, *args, **kwargs)
    return wrapper

def hash_password(password: str) -> str:
    """Function used to hash password with a
    UID salt

    Arguments:
        password: str password to hash
    Returns:
        string containing hashed password
    """
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

@database_function
def get_user_credentials(conn: object, cursor: object, uid: str):
    """Function used to retrieve password
    from database"""
    cursor.execute('SELECT user_id, username, password FROM user_credentials WHERE username=%s', (uid,))
    return cursor.fetchone()

@database_function
def create_new_user(conn: object, cursor: object, uid: str, password: str, email: str):
    """Function used to create new user in database"""
    # generate user ID and hash password
    user_id, password = uuid.uuid4(), hash_password(password)

    # insert values into relevant tables
    cursor.execute('INSERT INTO user_credentials(user_id, username, password) VALUES(%s,%s,%s)', (str(user_id), uid, password))
    cursor.execute('INSERT INTO users(user_id, username) VALUES(%s, %s)', (str(user_id), uid))
    cursor.execute('INSERT INTO user_details(user_id, email, signup_timestamp) VALUES(%s,%s,%s)', (str(user_id), email, datetime.utcnow()))

    conn.commit()
    return user_id

@database_function
def get_email_entry(conn: object, cursor: object, email: str):
    """Function used to retrieve an email entry from
    the database"""
    cursor.execute('SELECT email FROM user_details WHERE email=%s', (email,))
    return cursor.fetchone()

@database_function
def get_username_entry(conn: object, cursor: object, username: str):
    """Function used to retrieve an email entry from
    the database"""
    cursor.execute('SELECT user_id FROM users WHERE username=%s', (username,))
    return cursor.fetchone()

