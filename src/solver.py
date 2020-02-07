# from src.job import Step
from src.schedule import Schedule
from src.timeStep import idle_timeStep

last_schedules = list()

# how many schedules should be compared
# nur sinnvoll, wenn wir wissen, wir bewegen uns in die richtige Richtung.
# Ansonsten einfach alle behalten
# make it greater than iterations to keep all
stc = 20

# how many iterations should there be
iterations = 1000

# how deep should a path you want to look into be
path_deepness = 5

# how long should a moved step be blocked
block_time = 10


def solve(schedule: Schedule):
    for iteration in range(iterations):

        # Es fehlen weitere Abbruchbedingungen

        # if all jobs are perfectly fitted return the schedule
        if schedule.check_perfect():
            return schedule

        # if the length of schedules is going to be too long delete
        # first element
        if last_schedules is not None and len(last_schedules) >= stc:
            last_schedules.pop(0)
        # append the schedule to list of schedules to compare
        last_schedules.append(schedule.copy())

        # Vergleiche Längen der schedules
        shortest_schedule = min(last_schedules)
        if shortest_schedule.get_execute_time() <= schedule.min_time:
            return shortest_schedule

        # maybe unblock jobs
        schedule.reduce_block_count()

        # --------------- Begin of solving logic ---------------
        # block every first step
        # for job in schedule.jobs:
        #     first_step = job.steps[0]
        #     if first_step.start_time == 0 and not first_step.is_blocked:
        #         first_step.is_blocked = True
        #         first_step.time_blocked = 1

        # sort machines
        machine_to_take_index = 0
        sorted_machines = sorted(schedule.machines, reverse=True)

        search = True

        # search till you've got two viable steps to change or there're no more machines
        # to take the steps from
        # get longest job
        longest_job = max(schedule.machines).work[-1].job
        # find gap between two steps
        index = len(longest_job.steps)-1
        current_step = longest_job.steps[index]
        while index > 0:
            step_before = current_step.parent
            if step_before is not None and step_before.get_end_time() < current_step.start_time:
                # swap start
                current_machine = schedule.machines[current_step.machine_num]
                timeStep_of_current = current_machine.work[current_step.start_time]
                timeStep_before_current = current_machine.work[current_step.start_time-1]
                if timeStep_before_current is not idle_timeStep:
                    # versuche den gefundenen step zu tauschen
                    # switch steps
                    print("Steps to be switched:")
                    print("work: " + str(timeStep_of_current))
                    print("first: " + str(timeStep_before_current))
                    schedule.switch_steps(timeStep_before_current, timeStep_of_current,timeStep_of_current,1)
                    current_machine.remove_idle_at_end()
                    # block the swiched steps
                    for timeStep in [timeStep_before_current, timeStep_of_current]:
                        timeStep.step.is_blocked = True
                        timeStep.step.time_blocked = block_time
                    break
            elif step_before is None and step_before.start_time != 0:
                current_machine = schedule.machines[current_step.machine_num]
                timeStep_of_current = current_machine.work[current_step.start_time]
                timeStep_before_current = current_machine.work[current_step.start_time - 1]
                if timeStep_before_current is not idle_timeStep:
                    schedule.switch_steps(timeStep_before_current, timeStep_of_current, timeStep_of_current, 1)
                    current_machine.remove_idle_at_end()
                    # block the swiched steps

                    current_step.is_blocked = True
                    current_step.time_blocked = block_time
            current_step = step_before
            index -= 1
        # make schedule as condense as possible
        schedule.gapcheck()
