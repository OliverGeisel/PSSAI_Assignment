from src.job import Step, Job
from src.timeStep import TimeStep, idle_timeStep


class Machine:
    def __init__(self, id: int):
        self.work = list()
        self.id = id
        self.end_time = 0  # time the machine complete last step of all jobs

    def insert(self, start_time: int, step: Step, job: Job) -> None:
        if self.end_time < start_time + step.time:
            self.append_empty_timeSteps(start_time + step.time - self.end_time)
        self.setStep(start_time, step, job)
        self.end_time = len(self.work)

    def __remove_idle_at_end(self):
        while self.work[-1] is idle_timeStep:
            self.work.pop()
        self.end_time = len(self.work)

    def append_empty_timeSteps(self, timeSteps):
        for i in range(timeSteps):
            self.work.append(idle_timeStep)

    def setStep(self, start_time: int, step: Step, job: Job):
        step_num = job.steps.index(step) + 1
        time_step = TimeStep(step, step_num, job)
        for i in range(step.time):
            # Check ob bereits ein Job an der Stelle ist
            if len(self.work) <= start_time and self.work[start_time +
                                                          i].step_num != -1:
                raise CollisionInScheduleException(
                    f"An Error occurred! The step {start_time + i} in machine {self.id}"
                    f" is already placed! Job {self.work[start_time + i]} is there but"
                    f" {job} is wanted.")
            self.work[start_time + i] = time_step
        step.start_time = start_time

    def __remove_step(self, start_time, time):
        for i in range(time):
            self.work[start_time + i] = idle_timeStep
        self.__remove_idle_at_end()

    def removeStep(self, step: Step):
        self.__remove_step(step.start_time, step.time)

    def get_start_of_idle(self, index: int) -> int:
        if self.work[index] is not idle_timeStep:
            return -1
        while self.work[index] is idle_timeStep and index > 0:
            index -= 1
        return index

    def get_start_of_step(self, step: Step):
        for index, time_step in enumerate(self.work):
            if time_step.step is step:
                return index

    def __lt__(self, other):
        return other.end_time > self.end_time

    def switch_steps(self, timestep1: TimeStep, timestep2: TimeStep,
                     timestep_to_block: TimeStep, time_to_block: int):
        self.removeStep(timestep1.step)
        self.removeStep(timestep2.step)
        if timestep1.step.start_time < timestep2.step.start_time:
            start_time_cache = timestep1.step.start_time
            timestep1.step.start_time = timestep1.step.start_time + timestep2.step.time
            timestep2.step.start_time = start_time_cache
        else:
            start_time_cache = timestep2.step.start_time
            timestep2.step.start_time = timestep2.step.start_time + timestep1.step.time
            timestep1.step.start_time = start_time_cache

        self.insert(timestep1.step.start_time, timestep1.step, timestep1.job)
        self.insert(timestep2.step.start_time, timestep2.step, timestep2.job)

        for timestep in [timestep1, timestep2]:
            step_endtime = timestep.step.get_end_time()
            # if step's endtime exceeds the upcoming step's start time or its start time comes
            # before parents end time

            # out of range test before
            if timestep.job.steps.index(
                    timestep.step) < len(timestep.job.steps) - 1:

                next_time_step = timestep.job.steps[
                    timestep.job.steps.index(timestep.step) + 1]
                if step_endtime > next_time_step.start_time:
                    __move__(next_time_step, step_endtime)

            elif timestep.job.steps.index(timestep.step) > 0:

                time_step_before = timestep.job.steps[
                    timestep.job.steps.index(timestep.step) - 1]
                time_step_before_end_time = time_step_before.get_end_time()
                if time_step_before.get_end_time() > step_endtime:
                    print("Call __move__ with arguments " + str(timestep) +
                          " and time " + str(time_step_before_end_time))
                    __move__(timestep, time_step_before_end_time)

        timestep_to_block.step.is_blocked = True
        timestep_to_block.step.time_blocked = time_to_block


def __move__(self, t_step: TimeStep, start_time: int):
    # this loop handels all moving on one machine
    for len in [start_time, start_time + t_step.step.time]:
        no_coll = True
        if self.work[len] is not idle_timeStep and no_coll:
            __move__(self.work.step, t_step.step.get_end_time())
            no_coll = False
    self.insert(start_time, t_step.step, t_step)

    # those ifs handle the consistency and out of range
    if t_step.job.steps.index(t_step.step) < len(t_step.job.steps) - 1:

        t_next_step = t_step.job.steps[t_step.job.steps.index(t_step.step) + 1]
        if t_step.step.get_end_time() > t_next_step.start_time:
            __move__(t_next_step, t_step.step.get_end_time())

    elif t_step.job.steps.index(t_step.step) > 0:

        t_step_before = t_step.job.steps[t_step.job.steps.index(t_step.step) -
                                         1]
        if t_step.step.start_time < t_step_before:
            __move__(t_step_before, t_step_before)


class CollisionInScheduleException(Exception):
    def __init__(self, message):
        self.message = message
