import sys
import time

from src.decoder import parse_tasks
from src.machine import Machine
from src.schedule import Schedule
from src.solver import solve

# how many iterations should there be
from_iteration = 0
to_iterations = 100

# how long should a moved step be blocked
from_block_time = 0
to_block_time = 10

time_list = list()
schedule_list = list()
iter_param = list()
block_param = list()


def run(*args):
    tasks = parse_tasks(args[1])
    for task in tasks:
        start = time.time()
        machines = list()
        for i in range(task.machine_count):
            machines.append(Machine(i))
        schedule = Schedule(task.jobs, machines)

        # try some parameters to compare wich is faster
        for i in range(from_iteration, to_iterations):
            for block in range(from_block_time, to_block_time):
                start = time.time()
                schedule_list.append(solve(schedule, i, block))
                end = time.time()
                time_list.append(end - start)
                iter_param.append(i)
                block_param.append(block)
            # print(f"Iteration with {i} Iterations is over")

        shortest_schedule = min(schedule_list)
        shortest_schedule_indizes = list()
        # search for all the schedules that have same (minimal) length
        for x in schedule_list:
            if shortest_schedule == x:
                shortest_schedule_indizes.append(schedule_list.index(x))

        # list the times that the shortest schedules needed to compute
        shortest_times = list()
        for i in range(0, len(time_list) - 1):
            if i in shortest_schedule_indizes:
                shortest_times.append(time_list[i])

        # get shortest needed time
        shortest_time = min(shortest_times)
        # get shortest schedule with smallest time needed
        fastest_schedule_index = time_list.index(shortest_time)
        stop = time.time()
        print(f"finisch task {task.name} in {stop-start}s")
        print(f"Fastest Schedule drawn took {shortest_time}s " +
              f"to calculate and had follwoing params:")
        print(f"Iterations: {iter_param[fastest_schedule_index]}")
        print(f"Block length: {block_param[fastest_schedule_index]}")
        print(schedule_list[fastest_schedule_index])


if __name__ == "__main__":
    run(*sys.argv)
