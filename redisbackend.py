import redis
import datetime
import logging
import json

class RedisBackend:
    def __init__(self,host='localhost', port=6379):
        self.client = redis.Redis(host=host, port=port)
        self.client.ping()

    def getTimeTests(self, title, platform):
        return self.client.zrange(title, 0,-1, withscores=True)

    def checkExist(self, title):
        return title in self.client.hkeys("timetest")

    def _getNumberOfTests(self, title):
        return self.client.zcount(title,float("-inf"),float("inf"))

    def _storePlatformInfo(self, title, platforminfo):
        return self.client.hmset("meminfo_" + title, {'platform': platforminfo.platform, 'cpucount': platforminfo.cpucount, \
                'pyversion': platforminfo.pyversion, 'memory': platforminfo.memory})

    def getPlatformInfo(self, title):
        params = ['platform', 'cpucount', 'pyversion', 'memory']
        values = self.client.hmget("meminfo_" + title, params)
        return list(zip(params, values))

    def addTimeTestResult(self, title, info):
        if not self.checkExist(title):
            self.client.hset("timetest", title, title + "_results")
        if not isinstance(info.delta, datetime.timedelta):
            raise Exception("Delta must be in the timedelta format")
        num_tests = self._getNumberOfTests(info.title)
        total_seconds = info.delta.total_seconds()
        now = datetime.datetime.now()
        strnow = now.strftime('%Y-%m-%d %H:%M:%S')
        result = self.client.zadd(info.title, strnow, total_seconds)
        platform_result = self._storePlatformInfo(info.title + "_" + strnow, info.platform_info)
        if not platform_result:
            logging.info("Information about platform was not added to redis")
        if result == 0:
            logging.info("Element {0} already exist".format(info.title))
