# from src.job import Step
from src.schedule import Schedule
from src.timeStep import idle_timeStep

# from src.timeStep import TimeStep

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

        # Es fehlt die Tiefe eines Pfades; rekursion?

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
        for job in schedule.jobs:
            first_step = job.steps[0]
            if first_step.start_time == 0 and not first_step.is_blocked:
                first_step.is_blocked = True
                first_step.time_blocked = 1

        # sort machines
        machine_to_take_index = 0
        sorted_machines = sorted(schedule.machines, reverse=True)

        search = True

        # search till you've got two viable steps to change or there're no more machines
        # to take the steps from
        while search:
            end_of_job = False
            step_number = 0
            # find first step of longest job
            latest_job = sorted_machines[machine_to_take_index].work[-1].job
            first_step = latest_job.steps[step_number]

            # while first_step is a blocked one or this or the step before is IdleStep try another
            current_machine_work = schedule.machines[first_step.machine_num].work
            timeStep_step_blocked = current_machine_work[first_step.start_time].step.is_blocked
            current_timeStep = current_machine_work[first_step.start_time]
            timeStep_before = current_machine_work[first_step.start_time - 1]

            while (idle_timeStep in [timeStep_before, current_timeStep] or timeStep_step_blocked) \
                    and not end_of_job:
                step_number += 1
                first_step = latest_job.steps[step_number]
                # if you got to the end of job take machine next longest
                if first_step == latest_job.steps[len(latest_job.steps) - 1]:
                    end_of_job = True
                    machine_to_take_index = machine_to_take_index + 1
                    if machine_to_take_index >= len(schedule.machines) + 1:
                        # It seems that every step is blocked
                        return min(last_schedules)
            if not end_of_job:
                search = False

        # versuche den gefundenen step zu tauschen

        machine_were_on = first_step.machine_num
        first_time_step = schedule.machines[machine_were_on].work[
            first_step.start_time]
        # search for step before first step of latest job
        work_to_change = schedule.machines[first_step.machine_num].work[
            first_step.start_time - 1]

        # switch steps
        print("Steps to be switched:")
        print("work: " + str(work_to_change))
        print("first: " + str(first_time_step))
        if work_to_change.job is not None and first_time_step.job is not None:
            schedule.machines[machine_were_on].switch_steps(
                work_to_change, first_time_step)
            # block the swiched steps
            for job in [first_time_step, work_to_change]:
                job.step.is_blocked = True
                job.step.time_blocked = block_time
        else:
            print(
                "Uh oh, there is a step that is Idle. How could that happen?")

        # make schedule as condense as possible
        schedule.gapcheck()
