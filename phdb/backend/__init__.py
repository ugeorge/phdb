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

	:parameter form: The format of the query output as list of two element. The
	                 first element is the format name and the second one is the
	                 passed parameters. 
	:type form: [str,[str,]]
	:parameter outp: The output path (in case of a file).
	:type outp: str.
	:parameter cols: Column headers.
	:type cols: [str,]
	:parameter rows: The rows returned by a database query
	:type rows: [(str,),]
	"""
	def __init__(self, form, outp):
		widths = [e for e in map(parseElement, form[1]) if isinstance(e, int)]
		flags  = [e for e in map(parseElement, form[1]) if isinstance(e, str)]
		form   = form[0]
		print widths
		print flags
		if form == 'console':
			self._back = ConsoleOut(widths)
		elif form == 'plain':
			self._back = plain(widths, out)
		elif form == 'latex':
			self._back = LaTeXOut(widths, flags, outp)
	
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


def parseElement(string):
	val = string
	try:
		val = int(string)
	except ValueError:
		pass
	return val

