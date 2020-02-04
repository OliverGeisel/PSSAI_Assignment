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
            if len(self.work) <= start_time and self.work[start_time + i].step_num != -1:
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

    def switch_steps(self, timestep1: TimeStep, timestep2: TimeStep):
        self.removeStep(timestep1.step)
        self.removeStep(timestep2.step)
        start_time_cache = timestep1.step.start_time
        timestep1.step.start_time = timestep2.step.start_time
        timestep2.step.start_time = start_time_cache
        self.insert(timestep1.step.start_time, timestep1.step, timestep1.job)
        self.insert(timestep2.step.start_time, timestep2.step, timestep2.job)


class CollisionInScheduleException(Exception):

    def __init__(self, message):
        self.message = message
