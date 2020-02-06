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

    def find_t_step_of_next_step(self, t_step: TimeStep):
        if len(self.work) == t_step.step.get_end_time():
            return t_step

        i = t_step.step.get_end_time()
        first_t_step_after = self.work[i]
        while first_t_step_after is idle_timeStep:
            i += 1
            first_t_step_after = self.work[i]
        return first_t_step_after

    def find_t_step_of_step_before(self, t_step: TimeStep):
        if t_step.step.start_time == 0:
            return t_step

        i = t_step.step.start_time
        first_t_step_after = self.work[i]
        while first_t_step_after is idle_timeStep:
            i -= 1
            first_t_step_after = self.work[i]
        return first_t_step_after

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
                    timestep.step) < len(timestep.job.steps)-1:

                next_time_step = self.find_t_step_of_next_step(timestep)

                if step_endtime > next_time_step.step.start_time:
                    self.move(next_time_step, step_endtime)

                if timestep.job.steps.index(timestep.step) > 0:

                    time_step_before = self.find_t_step_of_step_before(
                        timestep)

                    if time_step_before.step.get_end_time() > step_endtime:
                        print("Call __move__ with arguments " + str(timestep) +
                              " and time " +
                              str(time_step_before.get_end_time()))
                        self.move(timestep, time_step_before.get_end_time())

        timestep_to_block.step.is_blocked = True
        timestep_to_block.step.time_blocked = time_to_block

    def move(self, t_step: TimeStep, start_time: int):
        # this loop handels all moving on one machine
        for count, length in enumerate(self.work[start_time: start_time + t_step.step.time + 1],
                                       start_time):
            print(count, length)
            no_coll = True
            if self.work[count] is not idle_timeStep and no_coll:
                self.move(self.work[count], t_step.step.time + start_time + 1)
                no_coll = False
        self.removeStep(t_step.step)
        self.insert(start_time, t_step.step, t_step.job)

        t_step = self.work[start_time]
        # those ifs handle the consistency and out of range
        print(str(t_step.job.steps.index(t_step.step)) +
              " < " + str(len(t_step.job.steps) - 1))
        if t_step.job.steps.index(t_step.step) < len(t_step.job.steps) - 1:

            # the next step of same job
            t_next_step = self.find_t_step_of_next_step(t_step)
            t_next_step_index = t_step.job.steps.index(t_step.step) + 1
            next_step = t_step.job.steps[t_next_step_index]
            next_step_machine = next_step.machine_num
            t_next_step = 1 + next_step_machine  # Quatsch Zeile
            print(str(t_step.step.get_end_time()) +
                  " > " + str(t_next_step.step.start_time))
            if t_step.step.get_end_time() >= t_next_step.step.start_time:
                self.move(t_next_step, t_step.step.get_end_time() + 1)

            if t_step.job.steps.index(t_step.step) > 0:

                t_step_before = self.find_t_step_of_step_before(t_step)
                if t_step.step.start_time < t_step_before.get_end_time():
                    self.move(t_step_before,
                              t_step_before.step.get_end_time() + 1)


class CollisionInScheduleException(Exception):
    def __init__(self, message):
        self.message = message
