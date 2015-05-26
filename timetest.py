import datetime
import sys
import psutil

#Main Event object
class Event:
    def __init__(self, fn, title, *args, **kwargs):
        self.fn = fn
        self.title = title
        self.expected_delta = kwargs.get('expected_delta', 0)
        self.hardlimit = kwargs.get('hardlimit', 0)


class EventResult:
    def __init__(self, title, delta):
        self.title = title
        self.delta = delta

class TimeTest:
    def __init__(self, backend=None):
        self.events = []


    def __call__(self, fn, *args, **kwargs):
        self._construct_event(fn, fn.__name__)
        def inner(*args, **kwargs):
            pass
        return inner

    def _construct_event(self, fn, name, *args,**kwargs):
        expected = kwargs.get('expected',0)
        hardlimit = kwargs.get('hardlimit',0)
        self.events.append(Event(fn, name, expected_delta=expected, hardlimit=hardlimit))

    def _platform_info(self):
        return {'platform': sys.platform, 'cpucount': psutil.cpu_count(), 'pyversion': sys.version_info, 'memory': psutil.virtual_memory()}

    def addTest(self, title, fn, *args, **kwargs):
        self._construct_event(fn,title, *args,**kwargs)

    def _analysis(self, event, delta):
        if event.expected_delta < delta:
            print("This event takes more time")
        if event.hardlimit < delta:
            print("It takes much more time")

    def run(self):
        report = []
        platform_item = self._platform_info()
        print("Platform information:\n")
        print("OS: {0}".format(platform_item['platform']))
        print("CPU count: {0}".format(platform_item['cpucount']))
        pyversion = platform_item['pyversion']
        print("Python version: {0}.{1}".format(pyversion.major, pyversion.minor))
        memory = platform_item['memory']
        print("Total virtual memory: {0}".format(memory.total))
        print("Available virtual memory: {0}\n".format(memory.available))

        for event in self.events:
            eventstart = datetime.datetime.now()
            event.fn()
            eventend = datetime.datetime.now()
            print("{0} : {1}".format(event.title, eventend - eventstart))
        return report
