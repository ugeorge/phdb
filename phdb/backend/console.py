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
import phdb.core.sqlite3cmd as dbapi

try:
	confPath = os.path.join(os.getenv('PHDB_CFG_PATH'), "logger.conf")
	logging.config.fileConfig(confPath)
except AttributeError:
	print "+WARNING: PHDB_CFG_PATH was not set. Cannot continue execution."

logger = logging.getLogger('')

class ConsoleOut():
	"""Handler for console output.
	
	:parameter cols: Column headers.
	:type cols: [str,]
	:parameter rows: The rows returned by a database query
	:type rows: [(str,),]
	:parameter widths: Column widths.
	:type widths: [int,]
	"""
	def __init__(self, widths):
		if not widths:
			self._widths = [30]
		else:
			self._widths = widths
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
		
		data = map(lambda x: ['' if v is None else v for v in x], data)
		print wrap.indent([header]+data, hasHeader=True, separateRows=True,
		             prefix='| ', postfix=' |', 
		             wrapfunc=lambda (x,y): wrap.wrap_onspace_strict(x,y), 
			         widths = self._widths)

def reviews(variables):
	dbCon = dbapi.Connection(variables['db'])
	col_names, rows = dbCon.qGetSources(
		srcs      = variables['sources'])
	rows = map(list,rows)	
	return col_names, rows


def entries(variables):
	dbCon = dbapi.Connection(variables['db'])
	header, rows = dbCon.qGetEntries(
		filterExp = variables['filter'],
		srcs      = variables['sources'])	
	printdata = []
	for row in rows:
		row = list(row)
		del row[header.index('Crefs')]
		del row[header.index('Cites')]
		printdata.append(row)
	del header[header.index('Cites')]
	del header[header.index('Crefs')]
	return header, printdata
