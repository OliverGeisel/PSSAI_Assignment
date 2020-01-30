import copy
from typing import List

from src.job import Job, Step
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
        temp_job_list = copy.copy(self.jobs)
        temp_job_list.sort()
        longest_job = temp_job_list.pop()
        self.__insert_job_in_plan(longest_job)
        for job in self.jobs:
            if job is longest_job:
                continue
            # nicht insert -> wird kollidieren
            # self.__insert_job_in_plan(job)
            self.__add_new_job(job)

    def copy(self):
        return copy.deepcopy(self)

    def __insert_job_in_plan(self, job: Job) -> None:
        """Only for first step in plan"""
        for step in job.steps:
            self.machines[step.machine_num].insert(step, step.start_time, job)

    def __add_new_job(self, job: Job):
        for step in job.steps:
            machine = self.machines[step.machine_num]
            match = False
            start_of_interval = step.start_time
            original_start_time = start_of_interval
            while not match:
                if machine.end_time < step.start_time + step.time:
                    machine.append_empty_timeSteps(step.start_time + step.time - machine.end_time)
                interval_of_step = machine.work[start_of_interval: start_of_interval + step.time]
                used_steps = [x for x in interval_of_step if x.job is not None]
                if len(used_steps) > 0:
                    last_step = used_steps[-1].step
                    start_of_interval = last_step.start_time + last_step.time
                    continue
                machine.insert(step, start_of_interval, job)
                match = True
                # update start_time of all following steps
                start_of_update = job.steps.index(step)
                offset = start_of_interval - original_start_time
                for update_step in job.steps[start_of_update:]:
                    update_step.start_time += offset

    def __str__(self):
        schedule = list()
        for machine in self.machines:
            for timeStep in machine.work:
                if timeStep.step_number == -1:
                    schedule.append("O ")
                else:
                    schedule.append(f"{timeStep.job.id} ")
            schedule.append("\n")
        return f"The schedule for task looks like:\n" \
               f"{''.join(schedule)}"
