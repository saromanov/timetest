import datetime
import sys
import psutil
import redisbackend
import logging
from termcolor import colored
from enum import Enum


#Main Event object
class Event:
    """ Inner class for representation timetest
    arguments:
       fn(function): test function, getting from user
       title (string): title of test function. Usual this is name of function
       **kwargs:
       expected_delta(int) - expected time for running test
       hardlimit (int) - if current test is greather then this param, show FAIL
    """
    def __init__(self, fn, title, *args, **kwargs):
        self.fn = fn
        self.title = title
        self.expected_delta = kwargs.get('expected_delta', 0)
        self.hardlimit = kwargs.get('hardlimit', 0)
        self.expected = kwargs.get('expected')


class EventResult:
    """ Inner class for representation result of timetest """
    def __init__(self, title, delta, platform_info):
        self.title = title
        self.delta = delta
        self.platform_info = platform_info

class PlatformInfo:
    """ Inner class for platform information, where test was running """
    def __init__(self, *args, **kwargs):
        self.platform = kwargs.get('platform')
        self.cpucount = kwargs.get('cpucount')
        self.pyversion = kwargs.get('pyversion')
        self.memory = kwargs.get('memory')

class Expected(Enum):
    ''' This class provides expected results on time test
        HIGHEST - current result must be better than previous results
        AVERAGE - current result must be average compare to previous results
        This works only with backend
    '''
    HIGHEST = 1
    AVERAGE = 2

class TimeTest:
    def __init__(self, title, backend=None, show_past_results=0, *args, **kwargs):
        """ backend - backend for store results of tests
            show_past_results - show n best results from the previous
        """
        self.events = []
        self.backend=backend
        self.backend_name = None
        self.title = title
        self.backend_start= False
        self.show_past_results = show_past_results
        if backend == 'redis':
            try:
                import redisbackend
                self.backend = redisbackend.RedisBackend()
                self.backend_name = 'redis'
                #Backend contains at the moment of starting
                self.backend_start = True
            except:
                self.backend = None
                print(colored("Redis is not ready", 'red'))


    def __call__(self, fn, *args, **kwargs):
        self._construct_event(fn, fn.__name__)
        def inner(*args, **kwargs):
            pass
        return inner

    def _construct_event(self, fn, name, *args,**kwargs):
        expected_time_sec = kwargs.get('expected_time_sec',0)
        hardlimit = kwargs.get('hardlimit',0)
        expected = kwargs.get('expected')
        self.events.append(Event(fn, name, expected_delta=expected_time_sec, hardlimit=hardlimit, expected=expected))

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

    def _checkBackend(self):
        """ Before read or write, check availability of backend """
        try:
            self.backend.check()
            return True
        except:
            return False

    def _getDataFromBackend(self, title, platform):
        """ Getting past results from current test """
        if self.backend_start and not self._checkBackend():
            # If backend is not available, set None to backend value
            self.backend = None
            print(colored("Backend in not available", "red"))
        if self.backend == None or self.show_past_results == 0:
            return
        results = self.backend.getTimeTests(title, platform)
        return results if self.show_past_results > len(results) else results[:self.show_past_results]

    def _getPlatformInfoFromBackend(self, title):
        if self.backend == None:
            return
        backend_result = self.backend.getPlatformInfo(title)
        if all(res is None for (plat, res) in backend_result):
            logging.info("Can't get information about plarform from backend")
            return
        return backend_result

    def _getExpected(self, past_results, delta, event):
        if event.expected == Expected.HIGHEST:
            if delta.total_seconds() >= past_results[0][1]:
                return 0, colored("FAIL Expected. Current result is not highest", 'red')
            else:
                return 1, colored("PASSED Expected. Current results is highest", 'green')
        if event.expected == Expected.AVERAGE:
            #Not implemented yet
            return 1,""
        else:
            logging.info("Found error in expected parameter")
            return 0,""


    def _info(self, text):
        return colored(text, 'white')

    def compare(self, title1, title2):
        ''' This method provides compare of results between two tests'''
        platform_info = self._platform_info()
        result1 = self._getDataFromBackend(title1, platform_info)
        if result1 == None or len(result1) == 0:
            print(colored("Can't find information about {0}".format(title1), 'red'))
            return False
        result1 = float(result1[0][1])
        result2 = self._getDataFromBackend(title2, platform_info)
        if result2 == None or len(result2) == 0:
             print(colored("Can't find information about {0}".format(title2), 'red'))
             return
        result2 = float(result2[0][1])
        print(colored("{0} - {1}".format(title1, result1), "blue"))
        print(colored("{0} - {1}".format(title2, result2), "blue"))

    def _show_system_info(self, platform_item):
        print(colored("Platform information:", 'white', attrs=['bold']))
        print(self._info("OS: {0}".format(platform_item.platform)))
        print(self._info("CPU count: {0}".format(platform_item.cpucount)))
        pyversion = platform_item.pyversion
        print(self._info("Python version: {0}.{1}".format(pyversion.major, pyversion.minor)))
        memory = platform_item.memory
        print(self._info("Total virtual memory: {0}".format(memory.total)))
        print(self._info("Available virtual memory: {0}".format(memory.available)))
        print(self._info("Backend: {0}\n".format(self.backend_name)))
        print("Time tests for {0}:".format(self.title))

    def run(self):
        report = []
        platform_item = self._platform_info()
        self._show_system_info(platform_item)
        num_completed = 0
        num_failures = 0
        num_time_tests = len(self.events)
        for event in self.events:
            eventstart = datetime.datetime.now()
            event.fn()
            eventend = datetime.datetime.now()
            delta = eventend - eventstart
            result = EventResult(event.title, delta, platform_item)
            past_results = self._getDataFromBackend(event.title, None)
            if event.expected != None and self.backend != None:
                status, expmsg = self._getExpected(past_results, delta, event)
                num_failures += status
                num_completed -= status
                print(expmsg)
            backend_result = self._getPlatformInfoFromBackend(event.title)
            self._store_results(result)
            msg, text = self._analysis(event, delta)
            if text == None:
                num_completed += 1
                print(colored("COMPLETE: {0} - {1}".format(event.title, delta, platform_item), 'green', attrs=['blink']))
            else:
                num_failures += 1
                print(colored("{0}: {1} - {2} ({3})".format(msg, event.title, delta, text), 'red'))

            if past_results != None and past_results != []:
                print("Past results: ")
                for result in past_results:
                    print("{0} {1}".format(result[0],result[1]))
            if num_completed == num_time_tests:
                print("\nAll time tests was completed!")
        print(" ")
        if num_failures > 0:
            print("Number of failures: {0}".format(num_failures))
        return report
