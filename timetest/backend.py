#Abstract class for construct backend
from abc import ABCMeta, abstractmethod

class Backend(metaclass=ABCMeta):
	__metaclass__ = ABCMeta

	@abstractmethod
	def addTimeTestResult(self, title, info):
		raise NotImplementedError("Not implemented")
	@abstractmethod
	def getTimeTests(self, title, platform):
		raise NotImplementedError("Not implemented")
	@abstractmethod
	def getPlatformInfo(self, title):
		raise NotImplementedError("Not implemented")
	@abstractmethod
	def check(self):
		raise NotImplementedError("Not implemented")