"""
.. module:: backend
   :platform: Unix
   :synopsis: API for backend formatters.

This module contains all output formatters for the data returned by issued
database querries. They both format and write to their associated output device.

.. note::

   All new backeds go in here and they **MUST** comply with the API. Check 
   :class:`phdb.backend.Backend` for details.

.. moduleauthor:: George Ungureanu <ugeorge@kth.se> 

"""
#import plain
from console import ConsoleOut
from plain import PlainOut
from latex import LaTeXOut

class Backend():
	""" Formats and prints the results of a query. API class.

	:parameter parameters: The format parameters as a dictionary. 
	:type form: {key:data}
	:parameter outp: The output path (in case of a file).
	:type outp: str.
	:parameter rows: The rows returned by a database query
	:type rows: [(str,),]
	"""
	def __init__(self, parameters, outp):

		form   = parameters['format']
		if form == 'console':
			self._back = ConsoleOut(parameters['widths'])
		elif form == 'plain':
			self._back = PlainOut(parameters['widths'], outp)
		elif form == 'latex':
			self._back = LaTeXOut(parameters['widths'], parameters['flags'], outp)
	
	def writeout(self, msg, varDict=None):
		"""Start formatting, executing querries and printing

		:parameter msg: A message passed by the caller saying what to writeout.
		 Will be interpreted differently by different backends.
		:type msg: str.
		:parameter varDict: A dictionary containing relevant variables passed
		 by the caller.
		:type varDict: {str:str,}.
		"""
		return self._back.writeout(msg, varDict)




