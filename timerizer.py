from time import time

class Timer:
    def __init__(self, max_time:float) -> None:
        self.max_time = max_time
        self.start_time = 0
        self.atual_time = 0
        self.run = False

    def active(self) -> None:
        self.run = True
        self.start_time = time()
    
    def change_max_time(self, max_time:float) -> None:
        self.max_time = max_time

    def update(self) -> None:
        self.atual_time = time()
        if self.atual_time - self.start_time >= self.max_time:
            self.run = False