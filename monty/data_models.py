"""Module containing data models"""

import logging
import json
import uuid

from datetime import datetime, date
from typing import Any, Optional

from bottle import request, abort
from pydantic import BaseModel, ValidationError, Field


LOGGER = logging.getLogger(__name__)

def dataclass_response(func: object):
    """Wrapper used to convert pydantic models into
    JSON format before returning"""
    def wrapper(*args: tuple, **kwargs: dict):
        response = func(*args, **kwargs)
        if isinstance(response, BaseModel):
            return json.loads(response.json(exclude_unset=True))
        LOGGER.warning('received non-dataclass response %s', response)
        return response
    return wrapper


REQUEST_BODY_SOURCES = {
    'json': lambda: request.json
}

def extract_request_body(model: BaseModel, source='json', raise_on_error: bool = True) -> object:
    """Wrapper function used to extract and inject
    request bodies using Pydantic"""
    def make_wrapper(func: object):
        def wrapper(*args: tuple, **kwargs: dict):
            body_source = REQUEST_BODY_SOURCES.get(source, None)
            if body_source is None:
                LOGGER.error('invalid request body source %s', body_source)
                raise
            try:
                keys = model.__fields__.keys()
                result = func(model(**{key: body_source().get(key, None) for key in keys}), *args, **kwargs)
            except ValidationError as err:
                LOGGER.exception('unable to parse request body')
                if raise_on_error:
                    abort(400, 'invalid request body')
                result = func(None, *args, **kwargs)
            return result
        return wrapper
    return make_wrapper

class HTTPResponse(BaseModel):
    """Dataclass containing HTTP response"""
    http_code: int
    success: bool
    message: Optional[str]
    payload: Optional[Any]

class NewTaskRequest(BaseModel):
    """Dataclass contianing request for new task"""
    task_title: str
    content: str
    priority: int
    duration: int
    deadline: date

class TaskUpdateRequest(BaseModel):
    """Dataclass containing request for updating tasks"""
    remaining_hours: Optional[int]

class Task(BaseModel):
    """Dataclass contining monte carlo task"""
    task_id: uuid.UUID
    task_title: str
    content: str
    priority: int
    duration: int
    hours_remaining: int
    created: datetime
    deadline: datetime
    completion_date: Optional[datetime]

