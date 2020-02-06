import copy
from typing import List

from src.job import Job
from src.machine import Machine
from src.timeStep import TimeStep, idle_timeStep


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
                occupied_steps = list(
                    filter(lambda x: x.job is not None, interval_of_step))
                if len(occupied_steps) > 0:  # check if there is an time_step occupied
                    last_step = occupied_steps[-1].step
                    start_of_interval = last_step.get_end_time()
                    continue
                machine.insert(start_of_interval, step, job)
                match = True
                # update start_time of all following steps
                start_of_update = job.steps.index(step)+1
                if start_of_update >= len(job.steps):
                    continue
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
        return max(self.machines) < max(other.machines)

    def check_perfect(self) -> bool:
        count = 0
        for job in self.jobs:
            if job.is_perfect():
                count = count + 1
        if count == len(self.jobs):
            return True
        else:
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
                start_of_idle = current_machine.get_start_of_idle(
                    step.start_time - 1)
                if start_of_idle == -1:  # der "Bereich" davor ist kein idle
                    continue
                end_time_parent = step.parent.get_end_time() if step.parent is not None else 0
                if step.start_time > end_time_parent:
                    diff = end_time_parent - start_of_idle
                    new_start = start_of_idle
                    if diff > 0:
                        new_start += diff
                    current_machine.removeStep(step)
                    current_machine.insert(new_start, step, job)

    def switch_steps(self, timestep1: TimeStep, timestep2: TimeStep,
                     timestep_to_block: TimeStep, time_to_block: int):
        self.machines[timestep1.step.machine_num].removeStep(timestep1.step)
        self.machines[timestep2.step.machine_num].removeStep(timestep2.step)
        if timestep1.step.start_time < timestep2.step.start_time:
            start_time_cache = timestep1.step.start_time
            timestep1.step.start_time = timestep1.step.start_time + timestep2.step.time
            timestep2.step.start_time = start_time_cache
        else:
            start_time_cache = timestep2.step.start_time
            timestep2.step.start_time = timestep2.step.start_time + timestep1.step.time
            timestep1.step.start_time = start_time_cache

        self.machines[timestep1.step.machine_num].insert(
            timestep1.step.start_time, timestep1.step, timestep1.job)
        self.machines[timestep2.step.machine_num].insert(
            timestep2.step.start_time, timestep2.step, timestep2.job)

        for timestep in [timestep1, timestep2]:
            step_endtime = timestep.step.get_end_time()
            # if step's endtime exceeds the upcoming step's start time or its start time comes
            # before parents end time

            # out of range test before
            # es gibt einen nächsten step
            if timestep.job.steps.index(
                    timestep.step) < len(timestep.job.steps)-1:
                print(str(timestep.job.steps.index(timestep.step)) +
                      " < " + str(len(timestep.job.steps)))

                # finde timestep von nächstem Step
                t_next_step_index = timestep.job.steps.index(timestep.step) + 1
                next_step = timestep.job.steps[t_next_step_index]
                next_step_machine = next_step.machine_num
                print("Work len: " + str(len(self.machines[next_step_machine].work)
                                         ) + " startTime: " + str(next_step.start_time))
                next_time_step = self.machines[next_step_machine].work[next_step.start_time]

                print("Machine: " + str(next_step_machine) +
                      " Start: " + str(next_step.start_time))
                print(self.__str__())

                if step_endtime > next_time_step.step.start_time:
                    self.move(next_time_step, step_endtime)

                if timestep.job.steps.index(timestep.step) > 0:

                    t_step_before_index = timestep.job.steps.index(
                        timestep.step) - 1
                    step_before = timestep.job.steps[t_step_before_index]
                    before_step_machine = step_before.machine_num
                    time_step_before = self.machines[before_step_machine].work[
                        step_before.start_time - 1]

                    if time_step_before.step.get_end_time() > step_endtime:
                        print("Call __move__ with arguments " + str(timestep) +
                              " and time " +
                              str(time_step_before.step.get_end_time()))
                        self.move(
                            timestep, time_step_before.step.get_end_time())

        timestep_to_block.step.is_blocked = True
        timestep_to_block.step.time_blocked = time_to_block

    def move(self, t_step: TimeStep, start_time: int):
        # this loop handels all moving on one machine
        for count, length in enumerate(self.machines[t_step.step.machine_num].work[
                start_time: start_time + t_step.step.time + 1], start_time):
            print(count, length)
            no_coll = True
            if self.machines[t_step.step.machine_num].work[count] is not idle_timeStep and no_coll:
                self.move(self.machines[t_step.step.machine_num].work[count],
                          t_step.step.time + start_time + 1)
                no_coll = False
        self.machines[t_step.step.machine_num].removeStep(t_step.step)
        self.machines[t_step.step.machine_num].insert(
            start_time, t_step.step, t_step.job)

        t_step = self.machines[t_step.step.machine_num].work[start_time]
        # those ifs handle the consistency and out of range
        print(str(t_step.job.steps.index(t_step.step)) +
              " < " + str(len(t_step.job.steps) - 1))
        if t_step.job.steps.index(t_step.step) < len(t_step.job.steps) - 1:

            # the next step of same job
            # t_next_step = self.find_t_step_of_next_step(t_step)
            t_next_step_index = t_step.job.steps.index(t_step.step) + 1
            next_step = t_step.job.steps[t_next_step_index]
            next_step_machine = next_step.machine_num
            t_next_step = self.machines[next_step_machine].work[next_step.start_time - 1]
            print(str(t_step.step.get_end_time()) +
                  " > " + str(t_next_step.step.start_time))
            if t_step.step.get_end_time() >= t_next_step.step.start_time:
                self.move(t_next_step, t_step.step.get_end_time() + 1)

            if t_step.job.steps.index(t_step.step) > 0:

                # t_step_before = self.find_t_step_of_step_before(t_step)
                t_step_before_index = t_step.job.steps.index(t_step.step) - 1
                step_before = t_step.job.steps[t_step_before_index]
                before_step_machine = step_before.machine_num
                t_step_before = self.machines[before_step_machine].work[step_before.start_time - 1]
                if t_step.step.start_time < t_step_before.step.get_end_time():
                    self.move(t_step, t_step_before.step.get_end_time() + 1)
