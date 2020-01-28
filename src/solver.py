from src.schedule import Schedule
from src.job import Job

last_schedules = None

# how many schedules should be compared
stc = 20

# gives back the job with whom the collision appeared


def detect_collision(schedule: Schedule, step: schedule.jobs.steps) -> schedule.jobs.steps:

    for mw in schedule.machines[step.machine_num].work:
        if step.start_time <= mw.start_time:
            if mw.start_time < step.start_time + step.time:
                return mw
        elif step.start_time < mw.start_time + mw.time:
            if mw.start_time < step.start_time + step.time:
                return mw
    return None

# makes sure that all steps of one job are not starting before last one ended


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

# check if there is a gap
# a gap is when the machine is idle for the time of the step and
# the step doesn't have a parent that is too close


def gapcheck(schedule: Schedule):
    for m in schedule.machines:
        for mw in m.work:
            workbefore = m.work[m.work.index(mw)-1]
            if workbefore.idle and mw.parent.start_time + mw.parent.time <= mw.start_time - mw.time and mw.time <= workbefore.time:
                # if there is a gap where the step fits in move it
                if mw:
                    gapstep_start = workbefore.start_time if mw.parent.start_time + \
                        mw.parent.time < workbefore.start_time else mw.parent.start_time + mw.parent.time
                    # insert, setStep??
                    schedule.machines[mw.machine_num].insert(mw, gapstep_start)


def solve(schedule: Schedule):
    # Es fehlen weitere Abbruchbedingungen

    # if all jobs are perfectly fitted return the schedule
    if schedule.jobs.isperfect():
        return schedule

    # Es fehlt die Tiefe eines Pfades

    # if the list of schedules is going to be too long delete first element
    if len(last_schedules) >= stc:
        last_schedules.pop(0)

    # Vergleiche Längen der schedules

    # append the schedule to list of schedules to compare
    last_schedules.append(schedule)
    # work with a new copy of the schedule
    schedule = schedule.copy()

    # finde zuletzt endenden job
    # funktioniert garantiert nicht
    id_longest_machine = max(schedule.machines.end_time).id
    latest_job = id_longest_machine.work[id_longest_machine.end_time]

    # finde seinen ersten step der nicht am Anfang des schedules liegt
    first_step = latest_job.steps[0]

    if first_step.start_time == 0:
        first_step = latest_job.steps[1]

    # versuche passenden step zu tauschen
    # merke die getauschten steps
    # setStep??
    step_to_change = schedule.machines[first_step.machine_num].work[schedule.machines.work.index(
        first_step)-1]
    first_step.start_time = step_to_change.start_time
    step_to_change.start_time = first_step.start_time + first_step.time
    # stelle konsistenz wieder her
    make_consistent(schedule)
    # schaue auch nach großen Lücken (vielleicht entstanden durch Konsistenz)
    gapcheck(schedule)
    # vergleiche länge von schedules


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
            schedule.machines[s.machine_num].append(s)  # ???, s.start_time
