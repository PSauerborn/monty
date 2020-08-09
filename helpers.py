"""module containing helpers functions"""

import logging
import json
import uuid
from math import floor

from typing import List
from datetime import datetime, timedelta
from random import randint, choice, uniform

import numpy as np

from data_models import Task

LOGGER = logging.getLogger(__name__)


def get_tasks(input_file: str = './tasks.json') -> list:
    """Helper function used to import tasks from
    local JSON file and convert into Task Models"""
    with open(input_file, 'r') as f:
        data = json.load(f)
    return [Task(**task) for task in data['tasks']]

def create_tasks(count: int, output: str = './tasks.json', save: bool = False) -> List[Task]:
    """Function used to create tasks that are saved
    to a local JSON file to use for testing

    Arguments:
        count: int number of tasks to create
        output: str output path of task JSON file
        save: bool save to local disk if True
    Returns:
        list of Task objects
    """
    tasks = []
    now = datetime(2020, 8, 9)
    deadline_dist, duration_dist = np.round(np.random.exponential(5, 10000)), np.round(np.random.exponential(7, 10000))
    for i in range(count):
        deadline = choice(deadline_dist) + 1
        # only include durations that are less than the deadline
        valid_durations = np.where(duration_dist < deadline * 24)
        duration = choice(duration_dist[valid_durations]) + 1
        task = {
            'task_id': str(uuid.uuid4()),
            'content': 'testing task ' + str(i),
            'priority': randint(1, 100),
            'deadline': (now + timedelta(days=deadline)).isoformat(),
            'duration': int(duration),
            'completion_date': None
        }
        tasks.append(task)
    if save:
        with open(output, 'w') as f:
            json.dump({'tasks': tasks}, f)
    return tasks

if __name__ == '__main__':

    create_tasks(1000, save=True)