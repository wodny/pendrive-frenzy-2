import Queue
from threading import Thread, Timer

##########
# Events #
##########

class Event:
    pass

class ProgressUpdate(Event):
    def __init__(self, gui, progress, total_progress, status = None):
        self.gui = gui
        self.progress = progress
        self.total_progress = total_progress
        self.status = status

    def handle(self, executor):
        self.gui.progress_update(self.progress, self.total_progress, self.status)

class StatusUpdate(Event):
    def __init__(self, gui, status):
        self.gui = gui
        self.status = status

    def handle(self, executor):
        self.gui.status_update(self.status)

class MainStatusUpdate(Event):
    def __init__(self, gui, status):
        self.gui = gui
        self.status = status

    def handle(self, executor):
        self.gui.mainstatus_update(self.status)

class ErrorsUpdate(Event):
    def __init__(self, gui, errors):
        self.gui = gui
        self.errors = errors

    def handle(self, executor):
        self.gui.errors_update(self.errors)

class ExpandErrors(Event):
    def __init__(self, gui, expand):
        self.gui = gui
        self.expand = expand

    def handle(self, executor):
        self.gui.expand_errors(self.expand)

class SetExitCode(Event):
    def __init__(self, exitcode):
        self.exitcode = exitcode

    def handle(self, executor):
        executor.exitcode = self.exitcode

class Quit(Event):
    def __init__(self):
        pass

    def handle(self, executor):
        executor.execute = False

class MakeSurprise(Event):
    def __init__(self, delay):
        self.delay = delay

    def handle(self, executor):
        if(self.delay >= 0):
            executor.surprise = Surprise(self.delay)


############
# Surprise #
############

class Surprise:
    def __init__(self, delay):
        self.timer = Timer(delay, self.wakeup)
        self.timer.start()

    def wakeup(self):
        EventQueue.instance().put(Quit())

    def cancel(self):
        self.timer.cancel()
        self.timer.join() 


####################
# Queue & Executor #
####################

class EventQueue(Queue.Queue):
    __single = None

    def __init__(self):
        if EventQueue.__single:
            raise EventQueue.__single

        Queue.Queue.__init__(self)
        EventQueue.__single = self

    @staticmethod
    def instance():
        return EventQueue.__single if EventQueue.__single else EventQueue()


class Executor(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.queue = EventQueue.instance()
        self.exitcode = 128
        self.execute = True
        self.surprise = None

    def run(self):
        while self.execute:
            order = self.queue.get()
            order.handle(self)

        if self.surprise:
            self.surprise.cancel()
