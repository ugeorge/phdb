"""
.. module:: frontend
   :platform: Unix
   :synopsis: API for frontend parsers.

This module contains all frontend parser classes defined for this project. 
A frontend parser harvests data from an input file having a defined format 
and fills a database with the extracted data.

.. note::

   All new frontends go in here and they **MUST** comply with the API. Check 
   :class:`phdb.frontend.api` for details.

.. moduleauthor:: George Ungureanu <ugeorge@kth.se> 

"""

import plain
import phdb.core.sqlite3cmd as dbapi

class Frontend():
	"""API class for all implemented frontend parsers.

	:parameter connection: Floating connection with basic input methods.
	:type connection: defined in :mod:`phdb.core`
	:parameter form: Format (just `plain` at the moment)
	:type form: str.
	:parameter path: Input path.
	:type path: str.

	.. note::
	   All new frontends have to comply with this API.
	"""
	def __init__(self, connection, form, path):
		self._front = plain.TextParser(connection, path)
	
	def harvest(self):
		'''Start parsing'''
		self._front.harvest()	

	def harvestFile(self, filename, db):
		'''Start parsing file'''
		self._front.harvestFile(filename)

