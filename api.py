"""Module containing API functions"""

import logging

from bottle import Bottle, run

from config import LISTEN_ADDRESS, LISTEN_PORT
from data_models import dataclass_response, HTTPResponse

LOGGER = logging.getLogger(__name__)

APP = Bottle()


@APP.route('/health', methods=['GET', 'OPTIONS'])
@dataclass_response
def health_check() -> HTTPResponse:
    """Health check route"""
    return HTTPResponse(success=True, http_code=200, message='api running')


if __name__ == '__main__':

    APP.run(host=LISTEN_ADDRESS, port=LISTEN_PORT, server='waitress')