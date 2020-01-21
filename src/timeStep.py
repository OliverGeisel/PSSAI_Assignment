from src.job import Step, Job


class TimeStep:

    def __init__(self, step: Step, step_number: int, job: Job, type: bool = False):
        self.type = type
        self.step = step
        self.step_number = step_number
        self.job = job
