"""Module containing configuration settings for the enerlytics Identity Provider"""

import logging
import os

from typing import Any

LOGGER = logging.getLogger(__name__)


TRUE_CONVERSIONS = ['true', 't', '1']

def override_value(key: str, default: Any, secret: bool = False) -> Any:
    """Helper function used to override local configuration
    settings with values set in environment variables

    Arguments:
        key: str name of environment variable to override
        default: Any default value to use if not set
        secret: bool hide value from logs if True
    Returns:
        default value if not set in environs, else value from
            environment variables
    """
    value = os.environ.get(key.upper(), None)

    if value is not None:
        LOGGER.info('overriding variable %s with value %s', key, value if not secret else '*' * len(value))
        # cast to boolean if default is of instance boolean
        if isinstance(default, bool):
            LOGGER.info('default value for %s is boolean. casting to boolean', key)
            value = value.lower() in TRUE_CONVERSIONS
    else:
        value = default
    return type(default)(value)

LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARN,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

LOG_LEVEL = LOG_LEVELS.get(override_value('log_level', 'DEBUG'), logging.DEBUG)
logging.basicConfig(level=LOG_LEVEL)

logging.getLogger('matplotlib').setLevel(level=logging.WARN)

LISTEN_ADDRESS = override_value('LISTEN_ADDRESS', '0.0.0.0')
LISTEN_PORT = override_value('LISTEN_PORT', 10999)

TASK_PRIORITY_THRESHOLD = override_value('task_priority_threshold', 0.75)

POSTGRES_PORT = override_value('postgres_port', 5432)
POSTGRES_HOST = override_value('postgres_host', 'localhost')
POSTGRES_USER = override_value('postgres_user', 'postgres')
POSTGRES_PASSWORD = override_value('postgres_password', '')
POSTGRES_DB = override_value('postgres_db', 'monty')

def get_postgres_connection_string() -> str:
    """Function used go generate the postgres
    connection string"""
    return f'postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

DB_CONNECTION_STRING = get_postgres_connection_string()

JWT_SECRET = override_value('jwt_secret', '')