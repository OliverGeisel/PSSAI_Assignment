import sys
from typing import List

from src.info.JobInfo import JobInfo
from src.task import Task


def build_tasks(parts) -> List[Task]:
    back = list()
    part_number = 0
    while part_number < len(parts):
        task_head = parts[part_number].split("\n")[2]
        task_body = parts[part_number + 1].split("\n")
        task_body.pop(0)
        task_body.pop()
        task_body.insert(0, task_head)
        back.append(Task(task_body))
        part_number += 2
    return back


def parse_tasks(path_of_file: str) -> List[Task]:
    with open(path_of_file, "r") as source:
        content = source.read()
    parts = content.split("+++++++++++++++++++++++++++++")
    del content
    # remove info part of file
    for i in range(3):
        parts.pop(0)
    parts.pop()
    parts[-1] = parts[-1].split("+")[0].strip()
    # build tasks
    tasks = build_tasks(parts)
    return tasks


parse_tasks(sys.argv[1])
