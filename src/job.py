class Step:

    def __init__(self, machine_num: int, time: int, parent=None, start_time: int = 0, idle: bool = False, is_blocked: bool = False):
        self.parent = parent
        self.time = time
        self.machine_num = machine_num
        self.idle = idle
        if parent is not None and start_time == 0:
            self.start_time = parent.start_time + parent.time
        else:
            self.start_time = start_time

        self.is_blocked = is_blocked
        self.time_blocked = 0
    def __str__(self):
        return f"Step for machine {self.machine_num} with time {self.time}"




class Job:

    def __init__(self, job_info: str, id):
        self.steps = list()
        self.id = id
        run_time = 0
        parent = None
        job_info = job_info.strip().split(" ")
        while " " in job_info:
            job_info.remove(" ")
        while "" in job_info:
            job_info.remove("")
        step_num = 0

        while step_num < len(job_info):
            machine = int(job_info[step_num])
            time = int(job_info[step_num + 1])
            run_time += time
            step = Step(machine, time, parent)
            self.steps.append(step)
            parent = step
            step_num += 2
        self.min_time = run_time

    def is_perfect(self) -> bool:
        return self.min_time == self.get_work_time()

    def is_continuous(self) -> bool:
        offset = self.steps[0].start_time
        for step in self.steps:
            if step.parent is None or \
                    step.parent.time + step.start_time + offset == step.start_time:
                offset += step.time
                continue
            return False
        return True

    def get_work_time(self):
        last_step = self.steps[-1]
        return last_step.start_time + last_step.time

    def __lt__(self, other):
        return other.min_time > self.min_time

    def __str__(self):
        return f"Job with min_time {self.min_time} and a work_time of {self.get_work_time()}"

