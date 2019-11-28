from typing import List

from src.job import Job
from src.machine import Machine


class Schedule:

    def __int__(self, jobs: List[Job], machines: List[Machine]):
        self.num_of_machines = len(machines)
        self.machines = machines
        self.jobs = jobs
        temp = [x.min_time for x in jobs]
        self.min_time = min(temp)
        self.max_time = sum(temp)
