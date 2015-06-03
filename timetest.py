import datetime
import sys
import psutil
import redisbackend
from termcolor import colored


#Main Event object
class Event:
    def __init__(self, fn, title, *args, **kwargs):
        self.fn = fn
        self.title = title
        self.expected_delta = kwargs.get('expected_delta', 0)
        self.hardlimit = kwargs.get('hardlimit', 0)


class EventResult:
    def __init__(self, title, delta, platform_info):
        self.title = title
        self.delta = delta
        self.platform_info = platform_info

class PlatformInfo:
    def __init__(self, *args, **kwargs):
        self.platform = kwargs.get('platform')
        self.cpucount = kwargs.get('cpucount')
        self.pyversion = kwargs.get('pyversion')
        self.memory = kwargs.get('memory')

class TimeTest:
    def __init__(self, title, backend=None):
        self.events = []
        self.backend=backend
        self.title = title
        if backend == 'redis':
            try:
                import redisbackend
                self.backend = redisbackend.RedisBackend()
            except:
                self.backend = None


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
        return PlatformInfo(platform=sys.platform, cpucount=psutil.cpu_count(),pyversion=sys.version_info, memory=psutil.virtual_memory())

    def addTest(self, title, fn, *args, **kwargs):
        self._construct_event(fn,title, *args,**kwargs)

    def _analysis(self, event, delta):
        delta = delta.total_seconds()
        if event.hardlimit !=0 and event.hardlimit < delta:
            return "FAIL HARDLIMIT", "Hard limit was  {0}".format(event.hardlimit)
        if event.expected_delta!= 0 and event.expected_delta < delta:
            return "FAIL EXPECTED", "Expected was {0}".format(event.expected_delta)
        return "", None

    def _store_results(self, event_result):
        """ Store results of tests to backend store"""
        if self.backend == None:
            return
        else:
            self.backend.addTimeTestResult(self.title, event_result)

    def _getDataFromBackend(self):
        """ Getting past results from current test """
        pass

    def _info(self, text):
        return colored(text, 'white')

    def run(self):
        report = []
        platform_item = self._platform_info()
        print(colored("Platform information:", 'white', attrs=['bold']))
        print(self._info("OS: {0}".format(platform_item.platform)))
        print(self._info("CPU count: {0}".format(platform_item.cpucount)))
        pyversion = platform_item.pyversion
        print(self._info("Python version: {0}.{1}".format(pyversion.major, pyversion.minor)))
        memory = platform_item.memory
        print(self._info("Total virtual memory: {0}".format(memory.total)))
        print(self._info("Available virtual memory: {0}".format(memory.available)))
        print(self._info("Backend {0}\n".format(self.backend)))
        print("Time tests for {0}:".format(self.title))
        for event in self.events:
            eventstart = datetime.datetime.now()
            event.fn()
            eventend = datetime.datetime.now()
            delta = eventend - eventstart
            result = EventResult(event.title, delta, platform_item)
            self._store_results(result)
            msg, text = self._analysis(event, delta)
            if text == None:
                print(colored("COMPLETE: {0} - {1}".format(event.title, delta, platform_item), 'green', attrs=['blink']))
            else:
                print(colored("{0}: {1} - {2} ({3})".format(msg, event.title, delta, text), 'red'))
        return report
