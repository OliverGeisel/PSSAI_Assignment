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
            self.machines[step.machine_num].insert(step.start_time, step, job)

    def __add_new_job(self, job: Job):
        for step in job.steps:
            machine = self.machines[step.machine_num]
            match = False
            start_of_interval = step.start_time
            original_start_time = start_of_interval
            # as long the step dosen't fit on the machine
            while not match:
                interval_of_step = machine.work[start_of_interval: start_of_interval + step.time]
                occupied_steps = list(filter(lambda x: x.job is not None, interval_of_step))
                if len(occupied_steps) > 0:  # check if there is an time_step occupied
                    last_step = occupied_steps[-1].step
                    start_of_interval = last_step.start_time + last_step.time
                    continue
                machine.insert(start_of_interval, step, job)
                match = True
                # update start_time of all following steps
                start_of_update = job.steps.index(step)
                offset = start_of_interval - original_start_time
                for update_step in job.steps[start_of_update:]:
                    update_step.start_time += offset

    def reduce_block_count(self, amount=1):
        for j in self.jobs:
            for s in j.steps:
                if s.is_blocked:
                    s.time_blocked -= amount
                    if s.time_blocked <= 0:
                        s.is_blocked = False
                        s.time_blocked = 0

    def get_execute_time(self):
        return max(self.machines).end_time

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
               f"{''.join(schedule)} \n Time: {self.get_execute_time()}"

    def __lt__(self, other):
        return min(self.machines) < min(other.machines)  # TODO warum min?

    def check_perfect(self) -> bool:
        for job in self.jobs:
            count = 0
            if job.is_perfect():
                count = count + 1
            if count == len(self.jobs):
                return True
        return False

    def gapcheck(self):
        # checkes if there is a gap and moves step if possible
        # a gap is when the machine is idle for the time of the step and
        # the step doesn't have a parent that is too close
        for job in self.jobs:
            for step in job.steps:
                current_machine = self.machines[step.machine_num]
                if step.start_time == 0:
                    continue
                start_of_idle = current_machine.get_start_of_idle(step.start_time - 1)
                if start_of_idle == -1:  # der "Bereich" davor ist kein idle
                    continue
                end_time_parent = step.parent.get_end_time()
                if step.start_time > end_time_parent:
                    diff = end_time_parent - start_of_idle
                    new_start = start_of_idle
                    if diff > 0:
                        new_start += diff
                    current_machine.removeStep(step)
                    current_machine.insert(new_start, step, job)
