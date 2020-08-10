"""module containing authentication plugin for monty application"""

import logging
from datetime import datetime

import jwt
from bottle import request, abort
from pydantic import BaseModel, ValidationError

from config import JWT_SECRET


LOGGER = logging.getLogger(__name__)


class TokenModel(BaseModel):
    """Dataclass contianing access token data model
    used to parse JWT claims"""
    uid: str
    exp: datetime

def extract_access_token() -> str:
    """Function used to extract the token value
    from the Authorization: Bearer <token> header
    format

    Returns:
        str containing token if present else None
    """
    token = request.headers.get('Authorization', None)
    if token and token.startswith('Bearer '):
        return token.split(' ')[1]
    LOGGER.warning('received invalid Authorization Header \'%s\'', token)

def parse_jwt_token(token: str) -> dict:
    """Helper function used to parse JWT tokens
    into claims"""
    return TokenModel(**jwt.decode(token, JWT_SECRET, algorithms=['HS256']))


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
            if (token := extract_access_token()) is not None:
                try:
                    # parse JWT token and inject into request headers
                    request.claims = parse_jwt_token(token)
                    LOGGER.debug('successfully parsed login token %s', request.claims)
                    return callback(*args, **kwargs)
                except (jwt.InvalidSignatureError, ValidationError):
                    LOGGER.exception('received invalid JWT')
                    abort(401, 'unauthorized')
                except jwt.ExpiredSignatureError:
                    LOGGER.exception('received expired JWT')
                    abort(401, 'access token expired')
            abort(401, 'missing access token')
        return wrapper



