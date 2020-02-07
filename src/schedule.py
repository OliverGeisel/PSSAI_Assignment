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
                start_of_update = job.steps.index(step) + 1
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
                count += 1
        return count == len(self.jobs)

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
        """
        swap two steps and block one step
        :param timestep1: first step to swap
        :param timestep2: second step to swap
        :param timestep_to_block: step to block
        :param time_to_block: time the step will be blocked
        :return: nothing
        """
        # remove two steps from schedule
        self.machines[timestep1.step.machine_num].removeStep(timestep1.step)
        self.machines[timestep2.step.machine_num].removeStep(timestep2.step)
        # decide which is the earlier step
        if timestep1.step.start_time < timestep2.step.start_time:
            start_time_cache = timestep1.step.start_time
            timestep1.step.start_time = timestep1.step.start_time + timestep2.step.time
            timestep2.step.start_time = start_time_cache
        else:
            start_time_cache = timestep2.step.start_time
            timestep2.step.start_time = timestep2.step.start_time + timestep1.step.time
            timestep1.step.start_time = start_time_cache
        # set new step positions
        self.machines[timestep1.step.machine_num].insert(
            timestep1.step.start_time, timestep1.step, timestep1.job)
        self.machines[timestep2.step.machine_num].insert(
            timestep2.step.start_time, timestep2.step, timestep2.job)
        # update all steps
        self.__update_steps_from_swap(timestep1, timestep2)
        # block step
        timestep_to_block.step.is_blocked = True
        timestep_to_block.step.time_blocked = time_to_block

    def __update_steps_from_swap(self, timestep1: TimeStep, timestep2: TimeStep):
        for timestep in [timestep1, timestep2]:
            # 1. check ob coll mit vorher
            step_endtime = timestep.step.get_end_time()
            if timestep.job.steps.index(timestep.step) > 0:
                step_before = timestep.step.parent
                before_step_machine = self.machines[step_before.machine_num]
                time_step_before = before_step_machine.work[step_before.start_time]

                if step_before.get_end_time() > timestep.step.start_time:
                    print(f"Call move with arguments {timestep} and time {time_step_before.step.get_end_time()}")
                    # verschiebe timestep soweit, dass er nicht mit seinem parent kollidiert
                    self.move(timestep, time_step_before.step.get_end_time())
            # 2. alle folgenden verschieben
            # es gibt einen nächsten step
            if timestep.job.steps.index(timestep.step) < len(timestep.job.steps) - 1:
                print(f"{timestep.job.steps.index(timestep.step)} < {len(timestep.job.steps)}")
                # finde timestep von nächstem Step
                t_next_step_index = timestep.job.steps.index(timestep.step) + 1
                next_step = timestep.job.steps[t_next_step_index]
                next_step_machine = self.machines[next_step.machine_num]
                print(f"Work len: {len(next_step_machine.work)} startTime: {next_step.start_time}")
                next_time_step = next_step_machine.work[next_step.start_time]

                print(f"Machine: {next_step_machine.id} \n"
                      f"Start: {next_step.start_time}")

                # if endtime is after start_time of next  move following step
                if step_endtime > next_step.start_time:
                    self.move(next_time_step, step_endtime)
        print(self)

    def shift(self, t_step: TimeStep, start_time: int):
        current_machine = self.machines[t_step.step.machine_num]
        # remove step
        current_machine.removeStep(t_step.step)
        # shift all steps in in target range
        if len(current_machine.work) < start_time + t_step.step.time:
            current_machine.append_empty_timeSteps(start_time + t_step.step.time - len(current_machine.work))
        target_block = set(filter(lambda x: x is not idle_timeStep,
                                  current_machine.work[start_time: start_time + t_step.step.time]))
        shift_offset = t_step.step.time
        t_step.step.start_time = start_time
        for time_step in target_block:
            current_machine.removeStep(time_step.step)
            time_step.step.start_time = start_time + shift_offset
            self.move(time_step, start_time + shift_offset)
            shift_offset += time_step.step.time
        current_machine.insert(start_time, t_step.step, t_step.job)

    def move(self, t_step: TimeStep, start_time: int):
        """
        Move one timeStep/ Step to new Position and check collision
        :param t_step: step to move
        :param start_time: point of new start
        :return: nothing
        """
        current_machine = self.machines[t_step.step.machine_num]
        # if not first step
        if t_step.job.steps.index(t_step.step) > 0:
            t_step_before_index = t_step.job.steps.index(t_step.step.parent)
            step_before = t_step.job.steps[t_step_before_index]
            if t_step.step.start_time < step_before.get_end_time():
                self.shift(t_step, step_before.get_end_time())
                return
        print(f"{t_step.job.steps.index(t_step.step)} < {len(t_step.job.steps) - 1}")
        # check if not last job
        if t_step.job.steps.index(t_step.step) < len(t_step.job.steps) - 1:
            next_step_index = t_step.job.steps.index(t_step.step) + 1
            next_step = t_step.job.steps[next_step_index]
            next_step_machine = self.machines[next_step.machine_num]
            t_next_step = next_step_machine.work[next_step.start_time]
            print(f"{t_step.step.get_end_time()} > {t_next_step.step.start_time}")
            # check if end time is after start of next step
            if t_step.step.get_end_time() > t_next_step.step.start_time:
                t_step.step.start_time = start_time
                self.shift(t_next_step, t_step.step.get_end_time())
        current_machine.insert(start_time, t_step.step, t_step.job)
