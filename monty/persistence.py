"""Module containing persistence functions used to connect
to postgres server"""

import logging
import uuid

from datetime import timedelta, datetime
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

from config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
from data_models import NewTaskRequest

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

@database_function
def create_user(conn: object, cursor: object, uid: str):
    """Function used to create user in postgres"""
    user_id = uuid.uui4()
    cursor.execute('INSERT INTO users(user_id, username) VALUES(%s, %s)', (str(user_id), uid))
    conn.commit()
    return user_id

@database_function
def get_all_users(conn: object, cursor: object):
    """Function used to retreive all users"""
    cursor.execute('SELECT user_id, username FROM users')
    return cursor.fetchall()

@database_function
def get_user_details(conn: object, cursor: object, uid: str):
    """Function used to retrieve a single user details"""
    cursor.execute('SELECT user_id, username FROM users WHERE username=%s', (uid,))
    return cursor.fetchone()

@database_function
def create_user_task(conn: object, cursor: object, user_id: uuid.UUID, body: NewTaskRequest):
    """Function used to retrieve a single user details"""
    task_id, now = uuid.uuid4(), datetime.utcnow()
    args = (str(task_id), body.task_title, str(user_id), body.content, body.priority, body.duration, body.duration, body.deadline, None, now)
    cursor.execute('INSERT INTO tasks(task_id,task_title,user_id,content,priority,duration,hours_remaining,deadline,completion_date,created) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', args)
    conn.commit()
    return task_id

@database_function
def complete_task(conn: object, cursor: object, task_id: str):
    """Function used to retrieve a single user details"""
    cursor.execute('UPDATE tasks SET completion_date=%s WHERE task_id=%s', (datetime.utcnow(), task_id))
    conn.commit()

@database_function
def get_user_tasks(conn: object, cursor: object, uid: str):
    """Function used to retrieve a single user details"""
    cursor.execute('SELECT task_id,task_title,content,priority,duration,deadline,completion_date,created,hours_remaining FROM tasks INNER JOIN users ON (tasks.user_id = users.user_id) WHERE username=%s', (uid,))
    return cursor.fetchall()

@database_function
def get_user_task(conn: object, cursor: object, uid: str, task_id: str):
    """Function used to retrieve a single task for
    a given user ID"""
    cursor.execute('SELECT task_id,task_title,content,priority,duration,deadline,completion_date,created,hours_remaining FROM tasks INNER JOIN users ON (tasks.user_id = users.user_id) WHERE username=%s AND task_id=%s', (uid, task_id))
    return cursor.fetchone()

@database_function
def get_task(conn: object, cursor: object, task_id: uuid.UUID):
    """Function used to retrieve a single user details"""
    cursor.execute('SELECT task_id,task_title,content,priority,duration,deadline,completion_date,created,hours_remaining FROM tasks WHERE task_id=%s', (task_id,))
    return cursor.fetchone()

@database_function
def delete_task(conn: object, cursor: object, task_id: uuid.UUID):
    """Function used to retrieve a single user details"""
    cursor.execute('DELETE FROM tasks WHERE task_id=%s', (task_id,))
    conn.commit()


if __name__ == '__main__':


    # task = NewTaskRequest(content='testing task', priority=45, duration=6, deadline=datetime.utcnow() + timedelta(hours=12))

    task = get_task('46649e01-0fb3-47a1-a974-e62021216319')
    print(dict(task))