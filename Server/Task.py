from threading import *
from time import sleep

class Task(Thread):
	@staticmethod
	def start_new(func,args=(),name=""):
		new_task=Task(func,args,name="")
		new_task.start()
		return new_task
	@staticmethod
	def delay(sec):
		return Task.start_new(lambda: sleep(sec),())
	@staticmethod
	def wait_all(tasks):
		for task in tasks:
			task.join()
	def __init__(self,func,args=(),name=""):
		Thread.__init__(self)
		self.name=name
		self.__func=func
		self.__args=args
		self.__result=None
		self.__work_done=False
	def run(self):
		self.__result=self.__func(*self.__args)
		self.__work_done=True
	def wait(self):
		self.join()
	@property
	def result(self):
		if not self.__work_done:self.join()
		return self.__result