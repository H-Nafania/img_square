from time import time

class Timer:
    def __init__(self):
        self.t1 = time()
        self.ti = time()

    def total_time(self):
        return f"{time()-self.t1:.2f}"

    def rely_time(self):
        t = time() - self.ti
        self.ti = time()
        return f"{t:.2f}"
