from typing import List


class Step:

    def __init__(self, time: int, machine_num: int, parent: Step = None, idle: bool = False):
        self.parent = parent
        self.time = time
        self.machine_num = machine_num
        self.idle = idle


class Job:

    def __init__(self, steps: List[Step]):
        self.steps = list(steps)
        run = 0
        for step in self.steps:
            run += step.time
        self.min_time = run
