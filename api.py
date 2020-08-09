"""Module containing API functions"""

import logging
import json

from bottle import Bottle, request, response, abort

from config import LISTEN_ADDRESS, LISTEN_PORT
from persistence import get_user_tasks, get_user_details, create_user_task, complete_task, \
    get_task
from data_models import dataclass_response, extract_request_body, HTTPResponse, NewTaskRequest, \
    Task
from simulation import analyse_task_set


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

@APP.route('/health', method=['GET', 'OPTIONS'])
@dataclass_response
def health_check() -> HTTPResponse:
    """API route used to perform a health check
    operation

    Returns:
        HTTPResponse object contianing success message
    """
    return HTTPResponse(success=True, http_code=200, message='api running')

@APP.route('/task/<uid>', method=['POST', 'OPTIONS'])
@extract_request_body(NewTaskRequest, source='json', raise_on_error=True)
@dataclass_response
def create_task(body: NewTaskRequest, uid: str) -> HTTPResponse:
    """API route used to create new task
    objects in the postgres database

    Arguments:
        body: task containing request body
    Returns:
        HTTPResponse containing response
    """
    LOGGER.debug('received request to create new task %s for user %s', body, uid)
    user = get_user_details(uid)
    if not user:
        return HTTPResponse(success=False, http_code=404, message='invalid user ' + uid)
    else:
        user = dict(user)
    # create task in database and return task ID
    task_id = create_user_task(user['user_id'], body)
    return HTTPResponse(success=True, http_code=200, payload={'task_id': str(task_id)})

@APP.route('/task/<uid>', method=['GET', 'OPTIONS'])
@dataclass_response
def get_tasks(uid: str) -> HTTPResponse:
    """API route used to create new task
    objects in the postgres database

    Arguments:
        body: task containing request body
    Returns:
        HTTPResponse containing response
    """
    LOGGER.debug('received request to retrieve tasks for user %s', uid)
    return HTTPResponse(success=True, http_code=200, payload=get_user_tasks(uid))

TASK_PATCH_OPERATIONS = {
    'COMPLETE': complete_task
}

@APP.route('/task/<task_id>', method=['PATCH', 'OPTIONS'])
@dataclass_response
def update_task(task_id: str) -> HTTPResponse:
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
        handler(task_id)
        return HTTPResponse(success=True, http_code=200, message='successfully update task ' + task_id)
    abort(400, 'invalid operation')


@APP.route('/simulation/<uid>', method=['GET', 'OPTIONS'])
@dataclass_response
def run_user_simulation(uid: str) -> HTTPResponse:
    """API route used to create new task
    objects in the postgres database

    Arguments:
        body: task containing request body
    Returns:
        HTTPResponse containing response
    """
    LOGGER.debug('received request to run simulations for user %s', uid)
    user = get_user_details(uid)
    if not user:
        return HTTPResponse(success=False, http_code=404, message='invalid user ' + uid)
    else:
        user = dict(user)
    tasks = [Task(**dict(row)) for row in get_user_tasks(uid)]
    return HTTPResponse(success=True, http_code=200, payload=analyse_task_set(8, tasks))

if __name__ == '__main__':

    APP.run(host=LISTEN_ADDRESS, port=LISTEN_PORT, server='waitress')