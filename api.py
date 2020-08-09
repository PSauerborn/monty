"""Module containing API functions"""

import logging
import json

from bottle import Bottle, request, response, abort

from config import LISTEN_ADDRESS, LISTEN_PORT
from data_models import dataclass_response, extract_request_body, HTTPResponse, NewTaskRequest


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

@APP.route('/task', method=['POST', 'OPTIONS'])
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
    LOGGER.debug('received request to create new task %s', body)
    return HTTPResponse(success=False, http_code=502, message='feature not yet implemented')

@APP.route('/task', method=['GET', 'OPTIONS'])
@dataclass_response
def get_user_tasks() -> HTTPResponse:
    """API route used to create new task
    objects in the postgres database

    Arguments:
        body: task containing request body
    Returns:
        HTTPResponse containing response
    """
    LOGGER.debug('received request to retrieve tasks %s', body)
    return HTTPResponse(success=False, http_code=502, message='feature not yet implemented')

TASK_PATCH_OPERATIONS = {
    'COMPLETE': lambda: HTTPResponse(success=False, http_code=502, message='feature not yet implemented')
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
    if (handler := TASK_PATCH_OPERATIONS.get(operation, None)) is not None:
        return handler()
    abort(400, 'invalid operation')

if __name__ == '__main__':

    APP.run(host=LISTEN_ADDRESS, port=LISTEN_PORT, server='waitress')