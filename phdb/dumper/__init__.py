"""
.. module:: dumper
   :platform: Unix
   :synopsis: API for database dumpers.

This module contains all dumper classes defined for this project. A dumper
defines methods to export all the content of the database in another format for
different purpose (reading, conversion between databases, etc).

.. note::

   All new dumpers go in here and they **MUST** comply with the API. Check 
   :class:`phdb.dumper.api` for details.

.. moduleauthor:: George Ungureanu <ugeorge@kth.se> 

"""

from phdb.dumper import plain

class DbDumper():
	"""Dumps the contents of a database. API class."""

	def __init__(self, parameters, outp):
		"""Default constructor. It initializes a different dumper according to 
		the *format* parameter.
		
		:parameter parameters: dumper parameters. Initializes one of the available dumpers.
		:type parameters: {key:}
		:parameter outp: dump path.
		:type outp: str
		"""
		if parameters['format'] == 'plain':
			self._dumper = plain.PlainDumper(outp)
	
	def dumpNewSource(self,data):
		"""Initializes the container for a new source."""
		self._dumper.dumpNewSource(data)

	def dumpHeader(self,data):
		"""Dumps the header."""
		self._dumper.dumpHeader(data)

	def dumpEntry(self, data):
		"""Dumps an entry field."""
		self._dumper.dumpEntry(data)


