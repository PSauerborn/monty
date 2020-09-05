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
def create_user_task(conn: object, cursor: object, uid: str, body: NewTaskRequest):
    """Function used to retrieve a single user details"""
    task_id, now = uuid.uuid4(), datetime.utcnow()
    args = (str(task_id), body.task_title, uid, body.content, body.priority, body.duration, body.duration, body.deadline, None, now)
    cursor.execute('INSERT INTO tasks(task_id,task_title,uid,content,priority,duration,hours_remaining,deadline,completion_date,created) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', args)
    conn.commit()
    return task_id

@database_function
def complete_task(conn: object, cursor: object, task_id: str, body):
    """Function used to retrieve a single user details"""
    cursor.execute('UPDATE tasks SET completion_date=%s WHERE task_id=%s', (datetime.utcnow(), task_id))
    conn.commit()

@database_function
def update_task_hours(conn: object, cursor: object, task_id: str, body):
    """Function used to retrieve a single user details"""
    if body.remaining_hours:
        LOGGER.debug('updating task with body %s', body)
        cursor.execute('UPDATE tasks SET hours_remaining=%s WHERE task_id=%s', (body.remaining_hours, task_id))
        conn.commit()
    else:
        LOGGER.warning('received no update hours')

@database_function
def get_user_tasks(conn: object, cursor: object, uid: str):
    """Function used to retrieve a single user details"""
    cursor.execute('SELECT task_id,task_title,content,priority,duration,deadline,completion_date,created,hours_remaining FROM tasks WHERE uid=%s', (uid,))
    return cursor.fetchall()

@database_function
def get_user_task(conn: object, cursor: object, uid: str, task_id: str):
    """Function used to retrieve a single task for
    a given user ID"""
    cursor.execute('SELECT task_id,task_title,content,priority,duration,deadline,completion_date,created,hours_remaining FROM tasks WHERE uid=%s AND task_id=%s', (uid, task_id))
    return cursor.fetchone()

@database_function
def get_user_tasks_in_range(conn: object, cursor: object, uid: str, start: datetime, end: datetime):
    """Function used to retrieve user tasks in time range"""
    cursor.execute('SELECT task_id,task_title,content,priority,duration,deadline,completion_date,created,hours_remaining FROM tasks WHERE uid=%s AND created > %s AND created < %s', (uid, start, end))
    return cursor.fetchall()

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