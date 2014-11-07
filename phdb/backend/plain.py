"""
.. module:: backend.console
   :platform: Unix
   :synopsis: Console handler for querry results.

.. moduleauthor:: George Ungureanu <ugeorge@kth.se> 

"""

import textwrap
import logging
import os

import plainformatter as wrap
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
	def __init__(self, widths, flags, out):
		if not widths:
			self._widths = [30]
		else:
			self._widths = widths
		self._output = out
		self._flags = flags
		logger.debug(str(self._widths))
	
	def writeout(self, msg, variables):
		"""Start formatting and printing"""
		if msg == 'reviews':
			reviews(variables, self._widths, self._output)
		elif msg == 'entries':
			entries(variables, self._widths, self._flags, self._output)
		elif msg == 'custom':
			custom(variables, self._widths, self._output)


def reviews(variables, widths, output):
	dbCon = dbapi.Connection(variables['db'])
	header, data = dbCon.qGetSources(
	srcs      = variables['sources'])	

	data = map(lambda x: ['' if v is None else v for v in list(x)], data)
	content = wrap.indent([header]+data, hasHeader=True, separateRows=True,
	             prefix='| ', postfix=' |', 
	             wrapfunc=lambda (x,y): wrap.wrap_onspace_strict(x,y), 
		         widths = widths)
	f = open(output, "w")
	f.write(content)
	f.close()


def entries(variables, widths, flags, output):
	dbCon = dbapi.Connection(variables['db'])
	header, rows = dbCon.qGetEntries(
		filterExp = variables['filter'],
		srcs      = variables['sources'])	
	printdata = []
	crefs = []
	for row in rows:
		row = ['' if v is None else v for v in list(row)]
		crossrefs = row[header.index('Crefs')]
		if crossrefs : 
			if ',' in crossrefs: crefs.append(','.split(crossrefs))
			else: crefs.append(crossrefs)
		del row[header.index('Crefs')]
		del row[header.index('Cites')]
		printdata.append(row)
	del header[header.index('Cites')]
	del header[header.index('Crefs')]

	content = wrap.indent([header]+printdata, hasHeader=True, separateRows=True,
	             prefix='| ', postfix=' |', 
	             wrapfunc=lambda (x,y): wrap.wrap_onspace_strict(x,y), 
		         widths = widths)
	f = open(output, "w")
	f.write(content)
	f.close()

	if not '-nocref' in flags:
		newsrcs = set([x.split('/')[0] for x in crefs])
		header, rows = dbCon.qGetCrefs(
			lables    = crefs,
			srcs      = newsrcs)
		content = wrap.indent([header]+rows, hasHeader=True, separateRows=True,
			         prefix='| ', postfix=' |', 
			         wrapfunc=lambda (x,y): wrap.wrap_onspace_strict(x,y), 
				     widths = widths)
		f = open(output, "a")
		f.write("\n\nReferenced entries:\n\n")
		f.write(content)
		f.close()


def custom(variables):
	pass

