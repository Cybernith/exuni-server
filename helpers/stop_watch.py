import time


class StopWatch:
    start_time = None
    time = None

    def start(self):
        self.start_time = time.time()
        self.time = self.start_time

    def print_elapsed(self):
        now = time.time()
        print("{}ms".format(round((now - self.time) * 1000, 2)))
