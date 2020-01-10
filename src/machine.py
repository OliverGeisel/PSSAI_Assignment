from src.job import Step


class Machine:

    def __init__(self, id: int):
        self.work = list()
        self.id = id
        self.end_time = 0  # time the machine complete last step of all jobs

    def append(self, step: Step, gap: int = 0) -> None:
        if not gap:
            idle = Step(gap, self.id, idle=True)
            self.work.append(idle)
        self.work.append(step)
        self.end_time += gap + step.time
        self.remove_double_idle()

    def insert(self, step, duration: int) -> None:
        # Todo insert a step and add idle plus merge to one
        pass

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
