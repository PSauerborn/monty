"""module containing helpers functions"""

import logging
from datetime import datetime, timedelta

import jwt
from pydantic import BaseModel

from config import JWT_SECRET, JWT_EXPIRY


LOGGER = logging.getLogger(__name__)

class TokenModel(BaseModel):
    """Dataclass contianing access token data model
    used to parse JWT claims"""
    uid: str
    expiry: datetime

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

def generate_jwt(user: str) -> str:
    """Function used to generate JWToken"""
    claims = {'uid': user, 'exp': datetime.utcnow() + timedelta(minutes=JWT_EXPIRY)}
    return jwt.encode(claims, JWT_SECRET, algorithm='HS256')