import datetime
class timer(object):
	def __init__(self):
		self.begin = datetime.datetime.now()
	def interval(self):
		#return (datetime.datetime.now() - self.begin).seconds
		delta = datetime.datetime.now() - self.begin
		delta = float(delta.seconds) + float(delta.microseconds)/1000000
		return delta