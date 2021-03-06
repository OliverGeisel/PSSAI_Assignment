from src.job import Step, Job


class TimeStep:

    def __init__(self, step: Step, step_number: int, job: Job, type: bool = False):
        self.type = type
        self.step = step
        self.step_number = step_number
        self.job = job

    def __str__(self):
        if self.job is None:
            return "Idle Step"
        return f"TimeStep for {self.job} and step_num {self.step_number}"

    def __eq__(self, other):
        if self is other:
            return True

        return self.job == other.job and \
               self.step == other.step and \
               self.step_number == other.step_number and \
               self.type == other.type

    def __hash__(self):
        return self.step.__hash__()


idle_timeStep = TimeStep(None, -1, None)
