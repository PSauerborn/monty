"""Module containing API functions"""

import logging
import json

from bottle import Bottle, request, response, abort

from config import LISTEN_ADDRESS, LISTEN_PORT
from data_models import dataclass_response, extract_request_body, HTTPResponse, NewUserRequest, \
    TokenRequest
from persistence import create_new_user
from helpers import email_in_use, username_in_use, is_authenticated_user
from token_helpers import generate_jwt


LOGGER = logging.getLogger(__name__)

def custom_error(error_details: str) -> dict: # pragma: no cover
    """Function used as custom error handler when
    uncaught exceptions are raised"""
    LOGGER.debug(error_details)
    # extract HTTP code and message from request body
    code, message = response.status_code, response.body
    response.content_type = 'application/json'
    return json.dumps({'success': False, 'http_code': code, 'message': message})

def cors(func: object) -> object: # pragma: no cover
    """Decorator used to apply CORS policy to a particular
    route. [GET, POST, PATCH, PUT, DELETE, OPTIONS] are all
    currently valid requests methods"""
    def wrapper(*args: tuple, **kwargs: dict) -> object:

        if 'Origin' in request.headers:
            response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
        else:
            response.headers['Access-Control-Allow-Origin'] = '*'
        # set allowed  methods and headers
        response.set_header("Access-Control-Allow-Methods", "GET, POST, PATCH, PUT, DELETE, OPTIONS")
        response.set_header("Access-Control-Allow-Headers", "Origin, Content-Type, Authorization, X-Authenticated-Userid")

        if request.method == 'OPTIONS':
            return

        return func(*args, **kwargs)
    return wrapper

APP = Bottle()
APP.default_error_handler = custom_error

@APP.route('/authenticate/health', method=['GET', 'OPTIONS'])
@cors
@dataclass_response
def health_check() -> HTTPResponse:
    """API route used to perform a health check
    operation

    Returns:
        HTTPResponse object contianing success message
    """
    return HTTPResponse(success=True, http_code=200, message='api running')

@APP.route('/authenticate/token', method=['POST', 'OPTIONS'])
@cors
@extract_request_body(TokenRequest, source='json', raise_on_error=True)
@dataclass_response
def get_token(body: TokenRequest) -> HTTPResponse:
    """API route used to perform a health check
    operation

    Returns:
        HTTPResponse object contianing success message
    """
    if not is_authenticated_user(body.uid, body.password):
        LOGGER.warning('received unauthorized request from user %s', body.uid)
        abort(400, 'invalid username or password')
    LOGGER.debug('successfully authenticated user %s', body.uid)
    token = generate_jwt(body.uid)
    return HTTPResponse(success=True, http_code=200, payload={'token': token.decode()})

@APP.route('/authenticate/signup', method=['POST', 'OPTIONS'])
@cors
@extract_request_body(NewUserRequest, source='json', raise_on_error=True)
@dataclass_response
def create_user(body: NewUserRequest) -> HTTPResponse:
    """API route used to perform a health check
    operation

    Returns:
        HTTPResponse object contianing success message
    """
    if email_in_use(body.email):
        LOGGER.error('email %s already in use', body.email)
        abort(400, 'email already in use')
    if username_in_use(body.uid):
        LOGGER.error('uid %s already in use', body.uid)
        abort(400, 'username already in use')

    LOGGER.debug('create new user %s', body.uid)
    user_id = create_new_user(body.uid, body.password, body.email)
    return HTTPResponse(success=True, http_code=200, payload={'userId': user_id})

if __name__ == '__main__':

    APP.run(host=LISTEN_ADDRESS, port=LISTEN_PORT, server='waitress')