from Sensor import Sensor

import threading


class MetaSensor(Sensor):

	"""
	A MetaSensor is a specialisation of a Sensor, that has efficient
	threaded behaviour built-in to it. Basically, your sensor provides
	3 things for the metasensor :

	- A fetcher method that fetchs data from some source
	- A displayer method that displays this data
	- A timer method that pauses between updates
	
	Once, you initialise a MetaSensor with these three parts,
	it will ensure that the datasource is polled at regular intervals,
	and that the display code is only called if there is something new
	to display.
	"""
	

	def __init__(self, retriever, rtimer, displayer):

		"""
		@retriever : function that retrieves data
		@type retriever: callable, returns True when new data
		available.

		@rtimer : function that return a sleep duration
		@type rtimer : callable. Returns int > 0.

		@displayer : function that displays data
		@type displayer : callable


		On config changed, only @displayer is called.
		@retriever lives is life, polling data and calling
		@displayer when needed.

		That's the best we can do with these old deprecated Sensor.
		
		"""
		
		Sensor.__init__(self)

		self.__retriever = retriever
		self.__rtimer    = rtimer
		self.__displayer = displayer

		self.__retriever_event = threading.Event()
		self.__displayer_event = threading.Event()
		
		self.watch_stop( self.__on_stop )
		self.watch_config( self.__on_update )


		def once():

			self.add_thread( self.__retriever_thread )
			self.add_thread( self.__displayer_thread )
			self._start = None

		self._start = once



	def watch_stop(self, callback):
		"""
		You can't override me :P
		"""
		pass


	def watch_config(self, callback):
		"""
		You can't override me :P
		"""
		pass


	def __on_stop(self):

		self.__retriever_event.set()
		self.__displayer_event.set()



	def __on_update(self, *dummy):

		self.__displayer_event.set()



	def __retriever_thread(self):

		while not self.is_stopped():

			if self.__retriever():
				self.__displayer_event.set()

			self.__retriever_event.wait( self.__rtimer() )




	def __displayer_thread(self):

		while not self.is_stopped():

			self.__displayer_event.wait()
			self.__displayer()
			self.__displayer_event.clear()
			
