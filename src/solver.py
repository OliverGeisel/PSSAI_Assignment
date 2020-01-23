from src.schedule import Schedule
from src.job import Job

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


def solve(schedule: Schedule):
    # finde zuletzt endenden job
    # funktioniert garantiert nicht
    id_longest_machine = max(schedule.machines.end_time).id
    latest_job = id_longest_machine.work[id_longest_machine.end_time]

    # finde seinen ersten step
    first_step = latest_job.steps[0]

    # versuche den zu tauschen
    if first_step.start_time != 0:
        step_to_change = schedule.machines[first_step.machine_num].work[schedule.machines.work.index(
            first_step)-1]
        first_step.start_time = step_to_change.start_time
        step_to_change.start_time = first_step.start_time + first_step.time
        # Kopiere altes Schedule und speichere das neue

        # stelle konsistenz wieder her
        make_consistent(schedule)

    else:
        pass

    # speichere die zuletzt getauschten Steps (für)

    # schaue auch nach großen Lücken (vielleicht entstanden durch Konsistenz)


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
            schedule.machines[s.machine_num].append(s, s.start_time)  # ???
