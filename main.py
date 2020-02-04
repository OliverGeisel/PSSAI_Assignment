import sys

from src.decoder import parse_tasks
from src.machine import Machine
from src.schedule import Schedule
from src.solver import solve


def run(*args):
    tasks = parse_tasks(args[1])
    for task in tasks:
        machines = list()
        for i in range(task.machine_count):
            machines.append(Machine(i))
        schedule = Schedule(task.jobs, machines)
        solve(schedule)
        print("Fertig")


if __name__ == "__main__":
    run(*sys.argv)
