"""
.. module:: backend.console
   :platform: Unix
   :synopsis: Console handler for querry results.

.. moduleauthor:: George Ungureanu <ugeorge@kth.se> 

"""

import textwrap
import logging
import os

import phdb.tools.textwrapper as wrap
import phdb.core.filter as filterparse
import phdb.core.sqlite3cmd as dbapi

try:
	confPath = os.path.join(os.getenv('PHDB_CFG_PATH'), "logger.conf")
	logging.config.fileConfig(confPath)
except AttributeError:
	print "+WARNING: PHDB_CFG_PATH was not set. Cannot continue execution."

logger = logging.getLogger('')


class PlainOut():
	"""Handler for plain text output.
	
	:parameter cols: Column headers.
	:type cols: [str,]
	:parameter rows: The rows returned by a database query
	:type rows: [(str,),]
	:parameter widths: Column widths.
	:type widths: [int,]
	"""
	def __init__(self, widths, out):
		if not widths:
			self._widths = [30]
		else:
			self._widths = widths
		self._output = out
		logger.debug(str(self._widths))
	
	def writeout(self, msg, variables):
		"""Start formatting and printing"""
		if msg == 'reviews':
			header, data = reviews(variables)
		elif msg == 'entries':
			header, data = entries(variables)
		elif msg == 'custom':
			header = variables["header"]
			data   = variables["data"]

		content = wrap.indent([header]+data, hasHeader=True, separateRows=True,
		             prefix='| ', postfix=' |', 
		             wrapfunc=lambda (x,y): wrap.wrap_onspace_strict(x,y), 
			         widths = self._widths)
		f = open(self._output, "w")
		f.write(content)
		f.close()

def reviews(variables):
	dbCon = dbapi.Connection(variables['db'])
	col_names, rows = dbCon.qGetSources(
		srcs      = variables['sources'],
		cols      = variables['columns'])	
	return col_names, rows


def entries(variables):
	dbCon = dbapi.Connection(variables['db'])
	col_names, rows = dbCon.qGetEntries(
		filterExp = variables['filter'],
		srcs      = variables['sources'],
		cols      = variables['columns'])	
	parser = filterparse.FilterParser(rows, len(col_names)-1)
	fRows = parser.parse(variables['filter'])
	return col_names, fRows
