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

    def remove_idle_at_end(self):
        while len(self.work) != 0 and self.work[-1] == idle_timeStep:
            self.work.pop()
        self.end_time = len(self.work)

    def append_empty_timeSteps(self, timeSteps):
        for i in range(timeSteps):
            self.work.append(idle_timeStep)
        self.end_time = len(self.work)

    def setStep(self, start_time: int, step: Step, job: Job):
        step_num = job.steps.index(step) + 1
        time_step = TimeStep(step, step_num, job)
        for i in range(step.time):
            # Check ob bereits ein Job an der Stelle ist
            if len(self.work) <= start_time or self.work[start_time + i] != idle_timeStep:
                raise CollisionInScheduleException(
                    f"An Error occurred! The step {start_time + i} in machine {self.id}"
                    f" is already placed! Job {self.work[start_time + i]} is there but"
                    f" {job} is wanted.")
            self.work[start_time + i] = time_step
        step.start_time = start_time

    def __remove_step(self, start_time, time):
        if len(self.work) < start_time + time:
            return
        for i in range(time):
            self.work[start_time + i] = idle_timeStep
        self.remove_idle_at_end()

    def removeStep(self, step: Step):
        self.__remove_step(step.start_time, step.time)

    def get_start_of_idle(self, index: int) -> int:
        if index > len(self.work)-1 or self.work[index] != idle_timeStep:
            return -1
        while index > 0 and self.work[index-1] == idle_timeStep:
            index -= 1
        return index

    def get_start_of_step(self, step: Step):
        for index, time_step in enumerate(self.work):
            if time_step.step is step:
                return index

    def __lt__(self, other):
        return other.end_time > self.end_time

    def find_t_step_of_next_step(self, t_step: TimeStep):
        if len(self.work) == t_step.step.get_end_time():
            return t_step

        i = t_step.step.get_end_time()
        first_t_step_after = self.work[i]
        while first_t_step_after == idle_timeStep:
            i += 1
            first_t_step_after = self.work[i]
        return first_t_step_after

    def find_t_step_of_step_before(self, t_step: TimeStep):
        if t_step.step.start_time == 0:
            return t_step

        i = t_step.step.start_time
        first_t_step_after = self.work[i]
        while first_t_step_after == idle_timeStep:
            i -= 1
            first_t_step_after = self.work[i]
        return first_t_step_after


class CollisionInScheduleException(Exception):
    def __init__(self, message):
        self.message = message
