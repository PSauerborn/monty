"""Module containing API functions"""

import logging
import json

from bottle import Bottle, request, response, abort
from dateutil import parser
from dateutil.parser._parser import ParserError

from config import LISTEN_ADDRESS, LISTEN_PORT
from persistence import get_user_tasks, create_user_task, complete_task, \
    get_task, get_user_task, delete_task, update_task_hours
from data_models import dataclass_response, extract_request_body, HTTPResponse, NewTaskRequest, \
    Task, TaskUpdateRequest
from simulation import analyse_task_set
from authenticate import AuthenticationPlugin
from helpers import get_user_details
from metrics import get_user_metrics


LOGGER = logging.getLogger(__name__)

def custom_error(error_details: str) -> dict: # pragma: no cover
    """Function used as custom error handler when
    uncaught exceptions are raised"""
    LOGGER.debug(error_details)
    # extract HTTP code and message from request body
    code, message = response.status_code, response.body
    response.content_type = 'application/json'
    return json.dumps({'success': False, 'http_code': code, 'message': message})

APP = Bottle()
APP.default_error_handler = custom_error

@APP.route('/monty/health', method=['GET', 'OPTIONS'])
@dataclass_response
def health_check() -> HTTPResponse:
    """API route used to perform a health check
    operation

    Returns:
        HTTPResponse object contianing success message
    """
    return HTTPResponse(success=True, http_code=200, message='api running')

@APP.route('/monty/task', method=['POST', 'OPTIONS'])
@extract_request_body(NewTaskRequest, source='json', raise_on_error=True)
@dataclass_response
def create_task(body: NewTaskRequest) -> HTTPResponse:
    """API route used to create new task
    objects in the postgres database

    Arguments:
        body: task containing request body
    Returns:
        HTTPResponse containing response
    """
    LOGGER.debug('received request to create new task %s for user %s', body, request.uid)
    # create task in database and return task ID
    task_id = create_user_task(request.uid, body)
    return HTTPResponse(success=True, http_code=200, payload={'task_id': str(task_id)})

@APP.route('/monty/tasks', method=['GET', 'OPTIONS'])
@dataclass_response
def get_tasks() -> HTTPResponse:
    """API route used to create new task
    objects in the postgres database

    Arguments:
        body: task containing request body
    Returns:
        HTTPResponse containing response
    """
    LOGGER.debug('received request to retrieve tasks for user %s', request.uid)
    fetch_completed = request.query.fetch_completed if request.query.fetch_completed else 'false'
    fetch_completed = fetch_completed.lower() in ['true', 't']

    tasks = [Task(**row) for row in get_user_tasks(request.uid)]
    if not fetch_completed:
        tasks = [task for task in tasks if not task.completion_date]
    return HTTPResponse(success=True, http_code=200, payload=tasks)

TASK_PATCH_OPERATIONS = {
    'COMPLETE': complete_task,
    'UPDATE': update_task_hours
}

@APP.route('/monty/task/<task_id>', method=['PATCH', 'OPTIONS'])
@extract_request_body(TaskUpdateRequest, source='json', raise_on_error=True)
@dataclass_response
def update_task(body: TaskUpdateRequest, task_id: str) -> HTTPResponse:
    """API route used to create new task
    objects in the postgres database

    Arguments:
        body: task containing request body
    Returns:
        HTTPResponse containing response
    """
    LOGGER.debug('received request to update task %s', task_id)
    operation = request.query.operation if request.query.operation else ''
    task = get_task(task_id)
    if not task:
        abort(400, 'invalid task id ' + task_id)
    if (handler := TASK_PATCH_OPERATIONS.get(operation, None)) is not None:
        handler(task_id, body)
        return HTTPResponse(success=True, http_code=200, message='successfully update task ' + task_id)
    abort(400, 'invalid operation')

@APP.route('/monty/task/<task_id>', method=['DELETE', 'OPTIONS'])
@dataclass_response
def delete_user_task(task_id: str):
    """API Route used to delete tasks

    Arguments:
        task_id: ID of task to delete
    Returns:
        HTTPResponse containing response
    """
    if (task := get_user_task(request.uid, task_id)):
        LOGGER.info('deleting task %s', task)
        delete_task(task_id)
        return HTTPResponse(success=True, http_code=200, message='successfully deleted task ' + task_id)
    else:
        LOGGER.warning('user %s attempted to delete task %s', request.uid, task_id)
        return abort(404, 'invalid task ID ' + task_id)

@APP.route('/monty/simulation', method=['GET', 'OPTIONS'])
@dataclass_response
def run_user_simulation() -> HTTPResponse:
    """API route used to create new task
    objects in the postgres database

    Arguments:
        body: task containing request body
    Returns:
        HTTPResponse containing response
    """
    LOGGER.debug('received request to run simulations for user %s', request.uid)
    tasks = [Task(**dict(row)) for row in get_user_tasks(request.uid)]
    LOGGER.info('running simulation for %s tasks', len(tasks))
    return HTTPResponse(success=True, http_code=200, payload=analyse_task_set(8, tasks))

@APP.route('/monty/metrics/<start>/<end>', method=['GET', 'OPTIONS'])
@dataclass_response
def get_metrics(start: str, end: str) -> HTTPResponse:
    """API route used to retrieve user metrics
    from database

    Returns:
        HTTPResponse containing response
    """
    LOGGER.debug('received request to get metrics for user %s', request.uid)
    try:
        start, end = parser.parse(start), parser.parse(end)
        if start > end:
            raise ParserError
        return HTTPResponse(success=True, http_code=200, payload=get_user_metrics(request.uid, start, end))
    except ParserError:
        LOGGER.error('received invalid timestamps %s and %s', start, end)
        return HTTPResponse(success=False, http_code=400, message='invalid time range')


if __name__ == '__main__':

    APP.install(AuthenticationPlugin())
    APP.run(host=LISTEN_ADDRESS, port=LISTEN_PORT, server='waitress')