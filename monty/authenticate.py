"""module containing authentication plugin for monty application"""

import logging
from datetime import datetime

import jwt
from bottle import request, response, abort
from pydantic import BaseModel, ValidationError

from config import JWT_SECRET


LOGGER = logging.getLogger(__name__)


class AuthenticationPlugin:
    """Bottle plugin used to check token authentication
    on API routes. Tokens are parsed and injected into
    the request headers"""

    def setup(self, app: object):
        """Function used to check that plugin has not been
        added to bottle application twice"""
        for plugin in app.plugins:
            if isinstance(plugin, AuthenticationPlugin):
                raise RuntimeError('authentication plugin already applied to application')

    def apply(self, callback: object, context: object):
        """Function used to apply authorization decorator
        to bottle application"""
        def wrapper(*args: tuple, **kwargs: dict):
            if (user := request.headers.get('X-Authenticated-Userid')) is not None:
                request.uid = user
            else:
                abort(401, 'unauthorized')
            return callback(*args, **kwargs)
        return wrapper




