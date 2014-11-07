"""
.. module:: textwrapper
   :synopsis: Formatter for plain-text tables. Based on Python Recipe 577615,
with slight modifications.

.. moduleauthor:: Jonathan Blakes (PSF license)

"""

import cStringIO,operator
import os
import re
import math
import logging

from itertools import izip_longest

try:
	confPath = os.path.join(os.getenv('PHDB_CFG_PATH'), "logger.conf")
	logging.config.fileConfig(confPath)
except AttributeError:
	print "+WARNING: PHDB_CFG_PATH was not set. Cannot continue execution."

logger = logging.getLogger(__name__)

def indent(rows, hasHeader=False, headerChar='-', delim=' | ', justify='left',
           separateRows=False, prefix='', postfix='', wrapfunc=lambda x:x, widths=[30]):
	"""Indents a table by column.
	   - rows: A sequence of sequences of items, one sequence per row.
	   - hasHeader: True if the first row consists of the columns' names.
	   - headerChar: Character to be used for the row separator line
		 (if hasHeader==True or separateRows==True).
	   - delim: The column delimiter.
	   - justify: Determines how are data justified in their column. 
		 Valid values are 'left','right' and 'center'.
	   - separateRows: True if rows are to be separated by a line
		 of 'headerChar's.
	   - prefix: A string prepended to each printed row.
	   - postfix: A string appended to each printed row.
	   - wrapfunc: A function f(text) for wrapping text; each element in
		 the table is first wrapped by this function."""
	# closure for breaking logical rows to physical, using wrapfunc
	def rowWrapper(row):
		if len(row) < 2:
			row = list(row) + ['']
		logger.debug(str(list(izip_longest(row, widths, fillvalue=widths[-1]))))
		newRows = [wrapfunc(item).split('\n') for item in list(izip_longest(row, widths, fillvalue=widths[-1]))]
		return [[substr or '' for substr in item] for item in map(None,*newRows)]
	# break each logical row into one or more physical ones
	logicalRows = [rowWrapper(row) for row in rows]
	# columns of physical rows
	columns = map(None,*reduce(operator.add,logicalRows))
	# get the maximum of each column by the string length of its items
	maxWidths = [max([len(str(item)) for item in column]) for column in columns]
	rowSeparator = headerChar * (len(prefix) + len(postfix) + sum(maxWidths) + \
		                         len(delim)*(len(maxWidths)-1))
	# select the appropriate justify method
	justify = {'center':str.center, 'right':str.rjust, 'left':str.ljust}[justify.lower()]
	output=cStringIO.StringIO()
	if separateRows: print >> output, rowSeparator
	for physicalRows in logicalRows:
		for row in physicalRows:
		    print >> output, \
		        prefix \
		        + delim.join([justify(str(item),width) for (item,width) in zip(row,maxWidths)]) \
		        + postfix
		if separateRows or hasHeader: print >> output, rowSeparator; hasHeader=False
	return output.getvalue()

def wrap_onspace(text, width):
	"""
	A word-wrap function that preserves existing line breaks
	and most spaces in the text. Expects that existing line
	breaks are posix newlines (\n).
	"""
	return reduce(lambda line, word, width=width: '%s%s%s' %
		          (line,
		           ' \n'[(len(line[line.rfind('\n')+1:])
		                 + len(word.split('\n',1)[0]
		                      ) >= width)],
		           word),
		          re.split(' |\r', text)
		         )
def wrap_onspace_strict(text, width):
	"""Similar to wrap_onspace, but enforces the width constraint:
	   words longer than width are split."""
	wordRegex = re.compile(r'\S{'+str(width)+r',}')
	return wrap_onspace(wordRegex.sub(lambda m: wrap_always(m.group(),width),text),width)

def wrap_always(text, width):
    """A simple word-wrap function that wraps text on exactly width characters.
       It doesn't split the text in words."""
    return '\n'.join([ text[width*i:width*(i+1)] \
                       for i in xrange(int(math.ceil(1.*len(text)/width))) ])
