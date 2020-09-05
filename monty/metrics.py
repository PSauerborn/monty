"""Module containing metrics functions"""

import logging
from datetime import datetime

from persistence import get_user_tasks_in_range
from data_models import UserMetrics

LOGGER = logging.getLogger(__name__)


METRIC_FUNCTIONS = {
    'total_tasks': lambda tasks: len(tasks),
    'completed_tasks': lambda : len([task for task in tasks if task.completion_date]),
    'completed_in_time': lambda : len([task for task in tasks if task.completion_date and task.completion_date < task.deadline])
}

def get_user_metrics(uid : str, start: datetime, end: datetime) -> UserMetrics:
    """Function used to retrieve user metrics"""
    tasks = get_user_tasks_in_range(uid, start, end)
    metrics = {metric: func(tasks) for metric, func in METRIC_FUNCTIONS.items()}
    return UserMetrics(**metrics.update('uid', uid))

