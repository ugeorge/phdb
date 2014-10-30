"""
.. module:: backend.console
   :platform: Unix
   :synopsis: Console handler for querry results.

.. moduleauthor:: George Ungureanu <ugeorge@kth.se> 

"""
import logging
import os
import re

import phdb.core.sqlite3cmd as dbapi
import phdb.core.filter as filterparse
from phdb.core.names import *

try:
	confPath = os.path.join(os.getenv('PHDB_CFG_PATH'), "logger.conf")
	logging.config.fileConfig(confPath)
except AttributeError:
	print "+WARNING: PHDB_CFG_PATH was not set. Cannot continue execution."

logger = logging.getLogger('')


class LaTeXOut():
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
		self._flags = flags
		self._output = out
		logger.debug(str(self._widths))
	
	def writeout(self, msg, variables):
		"""Start formatting and printing"""
		if msg == 'reviews':
			self.reviews(variables)
		elif msg == 'entries':
			self.entries(variables)
		else:
			header = variables["header"]
			data   = variables["data"]

	def reviews(self, var):
		f = open(self._output, "w")
		writeheader(f)
		f.write("\section{Query results}\n")
		col_names, rows = self.getReviews(var)
		writeTable(f, col_names, rows, "Tab01")
		writefooter(f)
		f.close()
	def entries(self, var):
		f = open(self._output, "w")
		writeheader(f)
		f.write("\section{Query results}\n")
		col_names, rows, lables = self.getEntries(var)
		writeTable(f, col_names, rows, "Tab01")
		f.write("\n\section{Indirect references}")
		while lables:
			col_names, rows, lables = self.getCref(lables, var)
			writeTable(f, col_names, rows, "Tab02")
		writefooter(f)
		f.close()

	def getReviews(self, variables):
		dbCon = dbapi.Connection(variables['db'])
		col_names, rows = dbCon.qGetSources(
			srcs      = variables['sources'],
			cols      = variables['columns'])	
		rows = self.alterRows_cite(rows, [col_names.index('BibRef'), col_names.index(REFERS)])
		return col_names, rows


	def getEntries(self, variables):
		dbCon = dbapi.Connection(variables['db'])
		col_names, rows = dbCon.qGetEntriesWLabels(
			filterExp = variables['filter'],
			srcs      = variables['sources'],
			cols      = variables['columns'])	
		parser = filterparse.FilterParser(rows, len(col_names)-1)
		fRows = parser.parse(variables['filter'])
		rows = self.alterRows_cite(fRows, [col_names.index(BIBREFSOURCE)])
		rows, labels = self.alterRows_cref(rows, col_names.index('Id'), col_names.index('Label'))
		del col_names[col_names.index('Label')]
		rows, reqLables = self.alterRows_info(rows, col_names.index('Info'), labels)
		
		return col_names, rows, reqLables

	def getCref(self, lables, variables):
		dbCon = dbapi.Connection(variables['db'])
		col_names, rows = dbCon.qGetCrefs(
			lables    = lables,
			srcs      = variables['sources'],
			cols      = variables['columns'])	
		rows = self.alterRows_cite(rows, [col_names.index(BIBREFSOURCE)])
		rows, labels = self.alterRows_cref(rows, col_names.index('Id'), col_names.index('Label'))
		del col_names[col_names.index('Label')]
		rows, reqLables = self.alterRows_info(rows, col_names.index('Info'), labels)
		return col_names, rows, reqLables

	def alterRows_cite(self, rows, indexes):
		if not '-nocite' in self._flags:
			for index in indexes:
				for rownum, row in enumerate(rows):
					rows[rownum] = alter_addRawCitation(row, index)
		return rows

	def alterRows_cref(self, rows, idIndex, labelIndex):
		labels = []
		noCrefFlag = False
		if '-nocref' in self._flags:
			noCrefFlag = True
		for rownum, row in enumerate(rows):
			newrow, label = alter_addCref(row, idIndex, labelIndex, noCrefFlag)
			rows[rownum] = tuple(newrow)
			if label:
				labels.append(label)
		return rows, labels

	def alterRows_info(self, rows, index, labels):
		reqLabels = []
		for rownum, row in enumerate(rows):
			if not '-noformat' in self._flags:
				row = alter_format(row, index)
			if not '-noimg' in self._flags:
				row = alter_addImgs(row, index)
			if not '-nocite' in self._flags:
				row = alter_addInfoCitation(row, index)
			if not '-nocref' in self._flags:
				row,label = alter_addInfoCref(row, index, labels)
				reqLabels += label
			rows[rownum] = row
		return rows, reqLabels

def alter_addCref(row, idIdx, labelIdx, noCrefFlag):
	newrow = list(row)
	label = newrow[labelIdx]
	if label and not noCrefFlag:
		newrow[idIdx] += "\label{" + label + "}"
	del newrow[labelIdx] 
	return newrow, label

def alter_addRawCitation(row, index):
	refs = re.findall(r'[a-zA-Z0-9_-]+',row[index])
	citeRef = ['\cite{' + ref + '}' for ref in refs]
	newrow = list(row)
	newrow[index] = ', '.join(citeRef)
	return tuple(newrow)


def alter_addInfoCref(row, index, lables):
	reqrefs = []
	refs = re.findall(r'\[\[Cref:(.+)\]\]',row[index])
	newrow = list(row)
	for ref in refs:
		citeRef = '\href{' + ref + '}'
		newrow[index] = newrow[index].replace('[[Cref:' + ref + ']]', citeRef)
		if not ref in lables:
			reqrefs.append(ref)
	return tuple(newrow), reqrefs

def alter_addInfoCitation(row, index):
	refs = re.findall(r'\[\[Ref:(.+)\]\]',row[index])
	newrow = list(row)
	for ref in refs:
		citeRef = '\cite{' + ref + '}'
		newrow[index] = newrow[index].replace('[[Ref:' + ref + ']]', citeRef)
	return tuple(newrow)

def alter_addImgs(row, index):
	imgs = re.findall(r'\[\[Img:(.+)\]\]',row[index])
	newrow = list(row)
	for img in imgs:
		inclImg = '\includegraphics[width=.6/textwidth]{' + img + '}'
		newrow[index] = newrow[index].replace('[[Img:' + img + ']]', inclImg)
	return tuple(newrow)

def alter_format(row, index):
	info = row[index].split('\n')
	formatted = ''
	inside = False
	currDepth = 0
	for line in info:
		if re.search(r'^[ \t\v\r]*(\*|\-)', line):
			depth = len(line) - len(line.lstrip())
			if depth > currDepth:
				currDepth = depth
				formatted += "\t\\begin{itemize}\n"
			elif depth < currDepth:
				currDepth = depth
				formatted += "\n\t\\end{itemize}\n"
			formatted += '\t\t\item' + line
		else:
			if currDepth > 0:
				currDepth = 0
				formatted += "\n\t\\end{itemize}\n"
			formatted += '\t' + line + '\n\n'
	if currDepth > 0:
		currDepth = 0
		formatted += "\n\t\\end{itemize}\n"
	newrow = list(row)
	newrow[index] = formatted
	return tuple(newrow)


def writeheader(f):
	text = '''%Generated by PhDB. Modify as you see fit.
\documentclass{article}

\usepackage{booktabs}
\usepackage{longtable}
\usepackage{hyperref}

\\begin{document}

'''
	f.write(text)

def writeTable(f, headers, rows, tabname):
	text = '''

\\begin{longtable}
\\begin{tabular}{''' + 'l ' * len(headers) + '''}
\\toprule

'''
	text += " " + ''.join([x + " & " for x in headers[:-1]])
	text += headers[-1] + " \\\\\n\midrule\n"
	f.write(text)
	for row in rows:
		text = " " + ''.join([x + "\n\t& " for x in row[:-1]])
		text += row[-1] + " \\\\\n"
		f.write(text)

	text = '''\\bottomrule
\end{tabular}
\caption{'''+ tabname +'''}
\end{longtable}
'''
	f.write(text)

def writefooter(f):
	text = '\end{document}\n'
	f.write(text)

