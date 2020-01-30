from src.job import Step
from src.schedule import Schedule
from src.timeStep import TimeStep

last_schedules = None

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

# gives back the job with whom the collision appeared


def detect_collision(schedule: Schedule, step: Step) -> Step:
    for mw in schedule.machines[step.machine_num].work:
        if step.start_time <= mw.start_time:
            if mw.start_time < step.start_time + step.time:
                return mw
        elif step.start_time < mw.start_time + mw.time:
            if mw.start_time < step.start_time + step.time:
                return mw
    return None


# makes sure that all steps of one job are not starting before last one ended

# Methode wird nicht benötigt
# ------------------------------------------------------------------------------------
def make_consistent(schedule: Schedule):
    for j in schedule.jobs:
        for s in j.steps:
            next_step = j.steps[j.steps.index(s) + 1]
            if s.start_time + s.time > next_step.start_time:
                next_step.start_time = s.start_time + s.time
                collision_step = detect_collision(schedule, next_step)
                while collision_step:
                    # as long as there is a collision with a second step move the first behind
                    # not necessarily the wanted behaviour - to change later
                    s.start_time = collision_step.start_time + collision_step.time
                    collision_step = detect_collision(schedule, s)

# checkes if there is a gap and moves step if possible
# a gap is when the machine is idle for the time of the step and
# the step doesn't have a parent that is too close


def gapcheck(schedule: Schedule):
    for j in schedule.jobs:
        for s in j.steps:
            current_machine = schedule.machines[s.machine_num]
            slot_before_s = current_machine.work[current_machine.work.index(
                s) - 1]
            if slot_before_s.idle and s.parent.start_time + s.parent.time < s.start_time:
                if slot_before_s.start_time > s.parent.start_time + s.parent.time:
                    new_start = slot_before_s.start_time
                else:
                    new_start = s.parent.start_time + s.parent.time
                # TO-DO: find correct job
                current_machine.setStep(new_start, s, schedule.jobs.index(0))

    # for m in schedule.machines:
    #     for mw in m.work:
    #         workbefore = m.work[m.work.index(mw)-1]
    #         if workbefore.idle and mw.parent.start_time + mw.parent.time <= mw.start_time - mw.time and mw.time <= workbefore.time:
    #             # if there is a gap where the step fits in move it
    #             gapstep = workbefore if mw.parent.start_time + \
    #                 mw.parent.time < workbefore.start_time else mw.parent
    #             schedule.machines[mw.machine_num].setStep(m, gapstep.start_time, gapstep,  )# job vom step )


def solve(schedule: Schedule):

    for i in range(iterations):

        # Es fehlen weitere Abbruchbedingungen

        # if all jobs are perfectly fitted return the schedule
        if schedule.jobs.is_perfect():
            return schedule

        # Es fehlt die Tiefe eines Pfades; rekursion?

        # work with a new copy of the schedule
        origin_schedule = schedule.copy()

        # if the length of schedules is going to be too long delete first element
        if len(last_schedules) >= stc:
            last_schedules.pop(0)

        # Vergleiche Längen der schedules
        shortest_schedule = min(last_schedules)
        min_known_len = 0
        if shortest_schedule <= min_known_len:
            return shortest_schedule

        # append the schedule to list of schedules to compare
        last_schedules.append(origin_schedule)

        # maybe unblock jobs
        for x in schedule.machines:
            x.unblock_steps()

        # --------------- Begin of solving logic ---------------
        # block every first job
        for x in schedule.machines:
            if x.work[0].start_time == 0:
                x.block_step(x.work[0], 1)

        # find job that ends last
        latest_job = max(schedule.machines).work[-1].job

        # finde seinen ersten step der nicht am Anfang des schedules liegt
        step_number = 0
        first_step = latest_job.steps[step_number]

        # while first_step is a blocked one try another
        while schedule.machines[first_step.machine_num].is_blocked(first_step):
            step_number = step_number + 1
            first_step = latest_job.steps[step_number]
            # if you got to the end change strategie
            if first_step == latest_job.steps[latest_job.steps.len()]:
                # search for another step to change
                pass
            pass

        # versuche den ersten step zu tauschen

        machine_were_on = first_step.machine_num
        # search for step before first step of latest job
        index_of_step_to_change = schedule.machines.work.index(
            first_step) - 1
        step_to_change = schedule.machines[first_step.machine_num].work[index_of_step_to_change]

        # switch steps
        schedule.machines[machine_were_on].switch_steps(
            step_to_change.start_time, step_to_change.time, first_step.start_time, first_step.time)
        # remember the swiched steps
        schedule.machines[machine_were_on].block_step(
            step_to_change, block_time)
        schedule.machines[machine_were_on].block_step(
            first_step, block_time)

        # make schedule as condense as possible
        gapcheck(schedule)


# Methode wird nicht hier benötigt
# ------------------------------------------------------------------------------------
def initialize(schedule: Schedule):
    # Sort the jobs of the schedule to get longest first
    # Wie was genau ich sortieren muss weiß ich nicht
    schedule.jobs.sort(reverse=True)

    for j in schedule.jobs:
        for s in j.steps:
            # update start time
            # Kann es hier zum Fehler kommen, wenn es keinen parent gibt?
            s.start_time = s.parent.start_time + s.time
            # is there already a step
            col = detect_collision(schedule, s)
            while col:
                # as long as there is a collision with a second step move the first
                s.start_time = col.start_time + col.time
                col = detect_collision(schedule, s)
            # add step to schedule
            schedule.machines[s.machine_num].insert(
                s, s.start_time, j)  # ???
