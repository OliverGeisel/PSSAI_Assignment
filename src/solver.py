from src.job import Step
from src.schedule import Schedule
from src.timeStep import TimeStep

last_schedules = list()

# how many schedules should be compared
# nur sinnvoll, wenn wir wissen, wir bewegen uns in die richtige Richtung. Ansonsten einfach alle behalten
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
            if slot_before_s.step.idle and s.step.parent.start_time + s.step.parent.time < s.start_time:
                if slot_before_s.step.start_time > s.step.parent.start_time + s.step.parent.time:
                    new_start = slot_before_s.step.start_time
                else:
                    new_start = s.step.parent.start_time + s.step.parent.time

                current_machine.insert(new_start, s.step, s.job)

    # for m in schedule.machines:
    #     for mw in m.work:
    #         workbefore = m.work[m.work.index(mw)-1]
    #         if workbefore.idle and mw.parent.start_time + mw.parent.time <= mw.start_time - mw.time and mw.time <= workbefore.time:
    #             # if there is a gap where the step fits in move it
    #             gapstep = workbefore if mw.parent.start_time + \
    #                 mw.parent.time < workbefore.start_time else mw.parent
    #             schedule.machines[mw.machine_num].insert(m, gapstep.start_time, gapstep,  )# job vom step )


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

        # if the length of schedules is going to be too long delete first element
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

        # find job that ends last
        latest_job = max(schedule.machines).work[-1].job

        # finde seinen ersten step der nicht am Anfang des schedules liegt
        step_number = 0
        first_step = latest_job.steps[step_number]

        # while first_step is a blocked one try another
        while schedule.machines[first_step.machine_num].work[first_step.start_time].step.is_blocked:
            step_number = step_number + 1
            first_step = latest_job.steps[step_number]
            # if you got to the end of job change strategie
            if first_step == latest_job.steps[len(latest_job.steps)-1]:
                # search for another step to change
                pass

        # versuche den gefundenen step zu tauschen

        machine_were_on = first_step.machine_num
        first_time_step = schedule.machines[machine_were_on].work[first_step.start_time]
        # search for step before first step of latest job
        work_to_change = schedule.machines[first_step.machine_num].work[first_step.start_time - 1]

        # switch steps
        schedule.machines[machine_were_on].switch_steps(
            work_to_change, first_time_step)
        # remember the swiched steps
        for x in [first_time_step, work_to_change]:
            x.step.is_blocked = True
            x.step.time_blocked = block_time

        # make schedule as condense as possible
        gapcheck(schedule)
