import copy
from typing import List

from src.job import Job
from src.machine import Machine


class Schedule:

    def __init__(self, jobs: List[Job], machines: List[Machine]):
        self.num_of_machines = len(machines)
        self.machines = machines
        self.jobs = jobs
        time_list = [x.min_time for x in jobs]
        self.min_time = min(time_list)
        self.max_time = sum(time_list)
        # längsten job zuerst
        # idee sortiere jobs und gehe das durch
        # self.jobs.sort(reverse=True)
        longest_job = max(self.jobs)
        self.__insert_job_in_plan(longest_job)
        for job in self.jobs:
            if job == longest_job:
                continue
            # nicht insert -> wird kollidieren
            # self.__insert_job_in_plan(job)
            self.__add_new_job(job)

    def copy(self):
        return copy.deepcopy(self)

    def __insert_job_in_plan(self, job: Job) -> None:
        for step in job.steps:
            self.machines[step.machine_num].insert(step, step.start_time, job)

    def __add_new_job(self, job: Job):
        for step in job.steps:
            machine = self.machines[step.machine_num]
            # solange es belegt ist 
            interval_of_step= machine.work[step.start_time: step.start_time + step.time]
            if len([x for x in interval_of_step if x.job is not None]):
                pass
                
