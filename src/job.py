class Step:

    def __init__(self, machine_num: int, time: int, parent = None, idle: bool = False):
        self.parent = parent
        self.time = time
        self.machine_num = machine_num
        self.idle = idle


class Job:

    def __init__(self, job_info: str):
        self.steps = list()
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
            step = Step(int(machine), time, parent)
            self.steps.append(step)
            parent = step
            step_num += 2
        self.min_time = run_time
