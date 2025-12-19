from kernel.data import *
from kernel.ipc import *

class Proc:
    def __init__(self, func_text, prio, server=False):
        global pid_
        self.server = server
        self.pid = pid_
        self.func = func_text
        self.prio = prio
        self.pipes = {}
        self.state = CLOSED
        pid_ += 1
        if self.server:
            self.prio = 255