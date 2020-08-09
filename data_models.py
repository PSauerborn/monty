"""Module containing data models"""

import logging
import json
import uuid
from datetime import datetime

from typing import Any, Optional
from pydantic import BaseModel

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

class HTTPResponse(BaseModel):
    """Dataclass containing HTTP response"""
    http_code: int
    success: bool
    message: Optional[str]
    payload: Optional[Any]

class Task(BaseModel):
    """Dataclass contining monte carlo task"""
    task_id: uuid.UUID
    content: str
    priority: int
    duration: int
    deadline: datetime
    completion_date: Optional[datetime]