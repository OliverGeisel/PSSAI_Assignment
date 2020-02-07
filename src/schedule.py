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
                interval_of_step = machine.work[
                                   start_of_interval:start_of_interval + step.time]
                occupied_steps = list(
                    filter(lambda x: x.job is not None, interval_of_step))
                if len(occupied_steps
                       ) > 0:  # check if there is an time_step occupied
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
        not_changed = False
        while not not_changed:
            not_changed = True
            for job in self.jobs:
                for step in job.steps:
                    current_machine = self.machines[step.machine_num]
                    if step.start_time == 0:
                        continue
                    start_of_idle = current_machine.get_start_of_idle(
                        step.start_time - 1)
                    if start_of_idle == -1:  # der "Bereich" davor ist kein idle
                        continue
                    end_time_parent = step.parent.get_end_time(
                    ) if step.parent is not None else 0
                    if step.start_time > end_time_parent:
                        diff = end_time_parent - start_of_idle
                        new_start = start_of_idle
                        if diff > 0:
                            new_start += diff
                        current_machine.removeStep(step)
                        current_machine.insert(new_start, step, job)
                        not_changed = False

    def switch_steps(self, timestep1: TimeStep, timestep2: TimeStep,
                     timestep_to_block: TimeStep, time_to_block: int) -> bool:
        """
        swap two steps and block one step
        :param timestep1: first step to swap
        :param timestep2: second step to swap
        :param timestep_to_block: step to block
        :param time_to_block: time the step will be blocked
        :return: nothing
        """
        # remove two steps from schedule
        if timestep2.step.is_blocked or timestep1.step.is_blocked:
            return False
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
        self.machines[timestep1.step.machine_num].insert(timestep1.step.start_time, timestep1.step, timestep1.job)
        self.machines[timestep2.step.machine_num].insert(timestep2.step.start_time, timestep2.step, timestep2.job)
        # update all steps
        self.__update_steps_from_swap(timestep1, timestep2)
        # block step
        timestep_to_block.step.is_blocked = True
        timestep_to_block.step.time_blocked = time_to_block
        return True

    def __update_steps_from_swap(self, timestep1: TimeStep,
                                 timestep2: TimeStep):
        for timestep in [timestep1, timestep2]:
            # 1. check ob coll mit vorher
            step_endtime = timestep.step.get_end_time()
            if timestep.job.steps.index(timestep.step) > 0:
                step_before = timestep.step.parent
                before_step_machine = self.machines[step_before.machine_num]
                time_step_before = before_step_machine.work[
                    step_before.start_time]

                if step_before.get_end_time() > timestep.step.start_time:
                    # print(f"Call move with arguments {timestep} and" +
                    #       f"time {time_step_before.step.get_end_time()}")
                    # verschiebe timestep soweit, dass er nicht mit seinem parent kollidiert
                    self.move(timestep, time_step_before.step.get_end_time())
            # 2. alle folgenden verschieben
            # es gibt einen nächsten step
            if timestep.job.steps.index(
                    timestep.step) < len(timestep.job.steps) - 1:
                # print(
                #     f"{timestep.job.steps.index(timestep.step)} < {len(timestep.job.steps)}"
                # )
                # finde timestep von nächstem Step
                t_next_step_index = timestep.job.steps.index(timestep.step) + 1
                next_step = timestep.job.steps[t_next_step_index]
                next_step_machine = self.machines[next_step.machine_num]
                # print(
                #     f"Work len: {len(next_step_machine.work)} startTime: {next_step.start_time}"
                # )
                next_time_step = next_step_machine.work[next_step.start_time]

                # print(f"Machine: {next_step_machine.id} \n"
                #       f"Start: {next_step.start_time}")

                # if endtime is after start_time of next  move following step
                if step_endtime > next_step.start_time:
                    self.move(next_time_step, step_endtime)

    def shift(self, t_step: TimeStep, start_time: int):
        """
        Shift timeStep to the right and all following steps,
        in same machine and update following steps of job
        :param t_step:
        :param start_time:
        :return:
        """
        current_machine = self.machines[t_step.step.machine_num]
        # remove step
        current_machine.removeStep(t_step.step)
        # shift all steps in target range and update siblings
        t_step.step.start_time = start_time
        self.__update_following_steps(current_machine, start_time, t_step)
        # insert step to new position
        current_machine.insert(start_time, t_step.step, t_step.job)

    def __update_following_steps(self, current_machine, start_time, t_step):
        """
        replace all following steps that collides with t_step. t_step will not be inserted
        :param current_machine:
        :param start_time:
        :param t_step:
        :return:
        """
        collision_block = self.__check_if_collision(current_machine, start_time, t_step)
        # if there is a step in target then this step must also be shifted
        step_before = t_step
        # insert all steps to new positions
        for following_time_step in collision_block:
            # calculate new start_time for step
            end_time_of_step_before = step_before.step.get_end_time()
            # remove step, thats collide
            current_machine.removeStep(following_time_step.step)
            new_start_for_following_step = max(end_time_of_step_before, following_time_step.step.start_time)
            following_time_step.step.start_time = new_start_for_following_step
            # update following
            self.__update_following_steps(current_machine, new_start_for_following_step, following_time_step)
            # insert all updated steps
            current_machine.insert(new_start_for_following_step, following_time_step.step, following_time_step.job)
            step_before = following_time_step
        # add t_step for updating following step
        collision_block = list(collision_block)
        collision_block.insert(0, t_step)
        # update all following steps of same job
        for time_step in collision_block:
            child_step_index = time_step.job.steps.index(time_step.step) + 1
            if child_step_index >= len(time_step.job.steps):
                continue
            child_step = time_step.job.steps[child_step_index]
            child_time_step = self.machines[child_step.machine_num].work[child_step.start_time]
            new_start_time = max(child_time_step.step.start_time, time_step.step.get_end_time())
            self.shift(child_time_step, new_start_time)
        return collision_block

    def __check_if_collision(self, current_machine, start_time, t_step):
        if len(current_machine.work) < start_time + t_step.step.time:
            current_machine.append_empty_timeSteps(start_time + t_step.step.time - len(current_machine.work))
        target_block = set(filter(
            lambda x: x != idle_timeStep,
            current_machine.work[start_time:start_time + t_step.step.time]))
        return target_block

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
            # if start is before end_time of before shift to end of step before
            if t_step.step.start_time < step_before.get_end_time():
                self.shift(t_step, step_before.get_end_time())
                return
        # print(
        #     f"{t_step.job.steps.index(t_step.step)} < {len(t_step.job.steps) - 1}"
        # )
        # check if not last job
        if t_step.job.steps.index(t_step.step) < len(t_step.job.steps) - 1:
            next_step_index = t_step.job.steps.index(t_step.step) + 1
            next_step = t_step.job.steps[next_step_index]
            next_step_machine = self.machines[next_step.machine_num]
            t_next_step = next_step_machine.work[next_step.start_time]
            # print(
            #     f"{t_step.step.get_end_time()} > {t_next_step.step.start_time}"
            # )
            # check if end time is after start of next step
            if t_step.step.get_end_time() > t_next_step.step.start_time:
                t_step.step.start_time = start_time
                self.move(t_next_step, t_step.step.get_end_time())
        # insert step to new position
        current_machine.insert(start_time, t_step.step, t_step.job)
