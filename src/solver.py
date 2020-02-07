import random

# from src.job import Step
from src.schedule import Schedule
from src.timeStep import idle_timeStep


def solve(schedule: Schedule, iterations: int, block_time: int):
    shortest_schedule = schedule.copy()
    for iteration in range(iterations):
        # print(f"Start Iteration {iteration}")
        # if all jobs are perfectly fitted return the schedule
        if schedule.check_perfect():
            return schedule

        if schedule < shortest_schedule:
            shortest_schedule = schedule.copy()

        # unblock jobs
        schedule.reduce_block_count()

        # --------------- Begin of solving logic ---------------

        # print(schedule)
        # For the first time try switching steps of longest job
        if iteration < 0.2 * iterations:
            longest_job = max(schedule.machines).work[-1].job
            index = len(longest_job.steps) - 1
            current_step = longest_job.steps[index]
            # try new step for a better schedule
            try_new_step(current_step, index, schedule, block_time)
        # then switch random steps
        else:
            job_index = random.randint(0, len(schedule.jobs) - 1)
            random_job = schedule.jobs[job_index]
            step_index = random.randint(0, len(random_job.steps) - 1)
            random_step = random_job.steps[step_index]
            try_new_step(random_step, step_index, schedule, block_time)

        # make schedule as condense as possible
        schedule.gapcheck()
        # print(schedule)

    return shortest_schedule


def try_new_step(current_step, index, schedule, block_time: int):
    # search till you've got two viable steps to change or there're no more machines (steps?)
    while index >= 0:
        step_before = current_step.parent
        if step_before is not None and step_before.get_end_time(
        ) < current_step.start_time:
            # swap start
            current_machine = schedule.machines[current_step.machine_num]
            timeStep_of_current = current_machine.work[current_step.start_time]
            timeStep_before_current = current_machine.work[
                current_step.start_time - 1]
            if timeStep_before_current != idle_timeStep:
                # versuche den gefundenen step zu tauschen
                # switch steps
                # print("Steps to be switched:")
                # print("work: " + str(timeStep_of_current))
                # print("first: " + str(timeStep_before_current))
                if schedule.switch_steps(timeStep_before_current,
                                         timeStep_of_current,
                                         timeStep_before_current, block_time):
                    current_machine.remove_idle_at_end()
                    break
        elif step_before is None and current_step.start_time != 0:
            current_machine = schedule.machines[current_step.machine_num]
            timeStep_of_current = current_machine.work[current_step.start_time]
            timeStep_before_current = current_machine.work[
                current_step.start_time - 1]
            if timeStep_before_current != idle_timeStep:
                schedule.switch_steps(timeStep_before_current,
                                      timeStep_of_current, timeStep_of_current,
                                      block_time)
                current_machine.remove_idle_at_end()
        current_step = step_before
        index -= 1
