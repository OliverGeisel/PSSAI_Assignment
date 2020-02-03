# from src.job import Step
from src.schedule import Schedule
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

# checkes if there is a gap and moves step if possible
# a gap is when the machine is idle for the time of the step and
# the step doesn't have a parent that is too close


def gapcheck(schedule: Schedule):
    for j in schedule.jobs:
        for s in j.steps:
            current_machine = schedule.machines[s.machine_num]
            slot_before_s = current_machine.work[s.start_time - 1]
            print(slot_before_s)
            # Ich hoffe, das ist dann auch ein Idle
            if not slot_before_s and s.step.parent.start_time +\
                    s.step.parent.time < s.start_time:
                # TO-DO Wie finde ich denn den Anfang eines Idle raus?
                if slot_before_s.step.start_time > s.step.parent.start_time +\
                        s.step.parent.time:
                    new_start = slot_before_s.step.start_time
                else:
                    new_start = s.step.parent.start_time + s.step.parent.time

                current_machine.insert(new_start, s.step, s.job)


def solve(schedule: Schedule):

    for i in range(iterations):

        # Es fehlen weitere Abbruchbedingungen

        # if all jobs are perfectly fitted return the schedule
        for x in schedule.jobs:
            count = 0
            if x.is_perfect:
                count = count + 1
            if count == len(schedule.jobs):
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
        for j in schedule.jobs:
            for s in j.steps:
                if s.is_blocked:
                    s.time_blocked = s.time_blocked - 1
                if s.time_blocked == 0:
                    s.is_blocked = False

        # --------------- Begin of solving logic ---------------
        # block every first job
        for j in schedule.jobs:
            first_step = j.steps[0]
            if first_step.start_time == 0 and not first_step.is_blocked:
                first_step.is_blocked = True
                first_step.time_blocked = 1

        # sort machines
        machine_to_take_index = 0
        sortet_machines = sorted(schedule.machines, reverse=True)

        search = True

        # search till you've got two viable steps to change or there're no more machines
        # to take the steps from
        while search:
            end_of_job = False
            step_number = 0
            # find first step of longest job
            latest_job = sortet_machines[machine_to_take_index].work[-1].job
            first_step = latest_job.steps[step_number]

            # while first_step is a blocked one or this or the step before is IdleStep try another
            while not schedule.machines[first_step.machine_num].work[
                    first_step.start_time].job and not schedule.machines[
                        first_step.machine_num].work[
                            first_step.start_time -
                            1].job and not schedule.machines[
                                first_step.machine_num].work[
                                    first_step.
                                    start_time].step.is_block and not end_of_job:
                step_number = step_number + 1
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
            for x in [first_time_step, work_to_change]:
                x.step.is_blocked = True
                x.step.time_blocked = block_time
        else:
            print(
                "Uh oh, there is a step that is Idle. How could that happen?")

        # make schedule as condense as possible
        gapcheck(schedule)
