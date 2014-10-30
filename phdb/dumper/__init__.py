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

	def __init__(self, form, outp):
		"""Default constructor. It initializes a different dumper according to 
		the *form* parameter.
		
		:parameter form: dump format. Initializes one of the available dumpers.
		:type format: str
		:parameter outp: dump path.
		:type outp: str
		"""
		if form[0] == 'plain':
			self._dumper = plain.PlainDumper(outp)
	
	def dumpNewSource(self,data):
		"""Initializes the container for a new source."""
		self._dumper.dumpNewSource(data)

	def dumpRef(self,data):
		"""Dumps the *References* field."""
		self._dumper.dumpRef(data)

	def dumpAbout(self,data):
		"""Dumps the *About* field."""
		self._dumper.dumpAbout(data)

	def dumpConcl(self,data):
		"""Dumps the *Conclusion* field."""
		self._dumper.dumpConcl(data)

	def dumpXrefs(self,data):
		"""Dumps the *Cross-references* field."""
		self._dumper.dumpXrefs(data)

	def dumpGTags(self,data):
		"""Dumps the *Global tags* field."""
		self._dumper.dumpGTags(data)

	def dumpEntry(self, tags, at, info):
		"""Dumps an entry field."""
		self._dumper.dumpEntry(tags, at, info)


