"""Module containing monte carlo simulation functions"""

import logging
import json
import copy

from datetime import datetime, timedelta
from typing import List

import matplotlib.pyplot as plt
import numpy as np

from config import TASK_PRIORITY_THRESHOLD
from data_models import Task
from helpers import get_tasks, create_tasks

LOGGER = logging.getLogger(__name__)


def get_important_tasks(tasks: List[Task]) -> List[Task]:
    """Function used to determine if a is considered a
    priority task based on percentils"""
    percentile = round(TASK_PRIORITY_THRESHOLD * len(tasks))
    return sorted(tasks, key=lambda task: task.priority)[percentile:len(tasks)]

def get_completed_tasks(tasks: List[Task]) -> List[Task]:
    """Function used to return all completed tasks"""
    return [task for task in tasks if task.completion_date is not None]

def get_in_time_tasks(tasks: List[Task]) -> List[Task]:
    """Function used to get all tasks completed in time"""
    return [task for task in tasks if task.completion_date < task.deadline]

def tally_tasks(tasks: List[Task]) -> tuple:
    """Function used to tally tasks and
    return aggregated results"""
    total_tasks = len(tasks)

    completed = get_completed_tasks(tasks)
    important = len(get_important_tasks(completed)) / total_tasks
    in_time = len(get_in_time_tasks(completed)) / total_tasks

    return len(completed) / total_tasks, important, in_time

SORTING_FUNCTIONS = {
    'as_they_come': lambda tasks: tasks,
    'due_first': lambda tasks: sorted(tasks, key=lambda task: task.deadline),
    'due_last': lambda tasks: sorted(tasks, key=lambda task: task.deadline, reverse=True),
    'important_first': lambda tasks: sorted(tasks, key=lambda task: task.priority, reverse=True),
    'easier_first': lambda tasks: sorted(tasks, key=lambda task: task.duration),
    'easier_important_first': lambda tasks: sorted(tasks, key=lambda task: (task.duration, 100 - task.priority), reverse=True),
    'easier_due_first': lambda tasks: sorted(tasks, key=lambda task: (task.duration, task.deadline), reverse=True)
}

def run_simulation(hours_per_day: int, tasks: List[Task], sim_type: str = 'as_they_come',):
    """Function used to run Simulation on list of tasks"""
    # evaluate total time available for task and end time of simulation
    total_time = sum([task.duration for task in tasks]) * (hours_per_day / 24)
    end = datetime.utcnow() + timedelta(hours=total_time)
    sorter = SORTING_FUNCTIONS.get(sim_type, None)
    if sorter is None:
        raise
    # sort tasks according to simulation type
    sorted_tasks, task_finish = sorter(tasks), datetime.utcnow()
    completed = []
    for i, task in enumerate(sorted_tasks):
        # evaluate end time of task given duration
        task_finish += timedelta(task.duration)
        # end simulation if total time has exceeded limit
        if task_finish > end:
            LOGGER.info('finished running simulation type %s. completed tasks (%s) / (%s)', sim_type, i + 1, len(tasks))
            break
        # else complete task
        task.completion_date = task_finish
        completed.append(task)
    return tally_tasks(completed + sorted_tasks[len(completed):])

def analyse_task_set(hours_per_day: int, tasks: List[Task]) -> dict:
    """Function used to analyse a particular
    task set"""
    results = {}
    for sim_type in SORTING_FUNCTIONS:
        completed, important_completed, completed_in_time = run_simulation(hours_per_day, copy.deepcopy(tasks), sim_type=sim_type)
        results[sim_type] = {
            'completed': completed,
            'important_completed': important_completed,
            'completed_in_time': completed_in_time
        }
        LOGGER.info('completed: %s important completed: %s completed in time: %s', completed, important_completed, completed_in_time)
    return results

def plot_simulation_results(results: dict):
    """Function used to plot results obtained from
    running simulations"""

    x = np.arange(len(results))
    fig, ax = plt.subplots()

    bar_width = 0.3
    completed = ax.bar(x, [sim['completed'] for sim in results.values()], width=bar_width, label='completed')
    important_completed = ax.bar(x - bar_width, [sim['important_completed'] for sim in results.values()], width=bar_width, label='important completed')
    completed_in_time = ax.bar(x + bar_width, [sim['completed_in_time'] for sim in results.values()], width=bar_width, label='completed in time')

    ax.legend()
    ax.set_xticklabels([0] + list(results.keys()))

    plt.show()

if __name__ == '__main__':

    tasks = get_tasks()
    plot_simulation_results(analyse_task_set(8, tasks))









