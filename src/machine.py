from src.job import Step, Job
from src.timeStep import TimeStep


class Machine:
    idle_timeStep = TimeStep(None, -1, None)

    def __init__(self, id: int):
        self.work = list()
        self.id = id
        self.end_time = 0  # time the machine complete last step of all jobs
        self.blocked_steps = list(list(Step, int))

    @DeprecationWarning
    def append(self, step: Step, gap: int = 0) -> None:
        if not gap:
            idle = Step(gap, self.id, idle=True)
            self.work.append(idle)
        self.work.append(step)
        self.end_time += gap + step.time
        self.remove_double_idle()

    def insert(self, step: Step, start_time: int, job: Job) -> None:
        if self.end_time < start_time + step.time:
            self.append_empty_timeSteps(start_time + step.time - self.end_time)
        self.setStep(start_time, step.time, job)
        self.end_time = len(self.work)

    def __remove_idle_at_end(self):
        while self.work[-1] is self.idle_timeStep:
            self.work.pop()

    @DeprecationWarning
    def remove_double_idle(self):
        for index, step in enumerate(self.work):
            if step.idle and self.work[index + 1].idle:
                new_idle = Step(step.time + self.work[index + 1].time, self.id, idle=True)
                self.work.pop(index)
                self.work.pop(index)
                self.work.insert(index, new_idle)
                break

    def split_None(self):
        pass

    def append_empty_timeSteps(self, timeSteps):
        for i in range(timeSteps):
            self.work.append(self.idle_timeStep)

    def setStep(self, start_time, step: Step, job: Job):
        step_num = job.steps.index(step)
        time_step = TimeStep(step, step_num, job)
        for i in range(step.time):
            # Check ob bereits ein Job an der Stelle ist
            if len(self.work) <= start_time and self.work[start_time + i].step_num != -1:
                raise CollisionInScheduleException(f"An Error occurred! The step {start_time + i} in machine {self.id}"
                                                   f" is already placed! Job {self.work[start_time + i]} is there but"
                                                   f" {job} is wanted.")
            self.work[start_time + i] = time_step

    def removeStep(self, start_time, time):
        for i in range(time):
            self.work[start_time + i] = self.idle_timeStep

    def __lt__(self, other):
        return other.end_time - self.end_time

    def switch_steps(self, start_time1, time1, start_time2, time2):
        self.removeStep(self,start_time1, time1)
        self.removeStep(self,start_time2, time2)
        self.setStep(self, start_time1,time1)
        self.setStep(self, start_time2,time2)
        pass

                    
    def block_step(self, step: Step, time):
        self.blocked_steps.append([job, time])

    def unblock_steps(self):
        for x in self.blocked_steps:
            x[1] = x[1] -1
            if x[1] == 0:
                self.blocked_steps.remove(x)

    def is_blocked(self, step: Step):
        for x in self.blocked_steps:
            if x[0] == step:
                return True

class CollisionInScheduleException(Exception):

    def __init__(self, message):
        self.message = message
