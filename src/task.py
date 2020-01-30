from typing import List

from src.job import Job


class Task:

    def __init__(self, infos: List[str]):
        self.name = infos.pop(0)
        self.komplete_info = infos.pop(0)
        jobs_and_machines = infos.pop(0).split(" ")
        self.job_count = int(jobs_and_machines[1])
        self.machine_count = int(jobs_and_machines[2])
        self.jobs = list()
        for job_id, job_info in enumerate(infos):
            self.jobs.append(Job(job_info, job_id + 1))
