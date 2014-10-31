"""
.. module:: utils
   :platform: Unix, Windows
   :synopsis: A collection of general-purpose functions.

.. moduleauthor:: George Ungureanu <ugeorge@kth.se> 

"""

import re
import logging
from tempfile import mkstemp
from os import remove, close
from shutil import move

logger = logging.getLogger('phdb.utils')

def getFileName(fname):
	"""Function that returns the name of a file, used for conveninence

	:param fname:
	:type fname: str.
	:returns: str -- The file name.

	"""
	match = re.search('.',fname)
	if match:
		befor_keyowrd, keyword, after_keyword = fname.partition('.')
		return befor_keyowrd
	else:
		return fname

def strAfter(line,pattern):
	"""Returns the string after a keyword.

	:param line: the input string.
	:type line: str.
	:param pattern: the keyword.
	:type pattern: str.
	:returns: str -- The string after the keyword.

	"""
	match = re.search(pattern,line)
	if match:
		befor_keyowrd, keyword, after_keyword = line.partition(pattern)
		return after_keyword

def strAfterF( f, key ):
	"""Searches for the first occurrence of a keyword in a text file and
	returns all text after it, until the first empty `newline` (equivalent of
	`\\n\\n`).

	Args:
	   f (file)  : the file being parsed.
	   key (str) : the keyword.

	Returns:
	   str, file.  Two arguments:
	   * the first argument is the matching string
	   * the second argument is the file object with the updated read pointer.

	"""
	tmp = f
	string = ''
	inside = False
	while True:
		line = f.readline()
		if not line:
			return '',tmp
		if inside:
			string = string + line
			if line.strip() == "":
				return string.strip(),f
		if line.startswith(key):
			inside = True
			string = strAfter(line,key)

def replaceAfter(file, pattern, subst):
	"""Per-line replacement of strings after a matching keyword.

	Args:
	   file (str)    : path to the file that needs to be modified.
	   pattern (str) : the keyword.
	   subst (str)   : the substring replacing the matching strings.

	"""
	fh, abs_path = mkstemp()
	new_file = open(abs_path,'w')
	old_file = open(file)
	for line in old_file:
		theline = strAfter(line,pattern)
		if not theline == None:
			new_file.write(re.sub(theline,subst,line))
	new_file.close()
	close(fh)
	old_file.close()
	remove(file)
	move(abs_path, file)

def find_between( s, first, last ):
	"""Returns the string between two keywords.

	Args:
	   s (str)      : input string.
	   first (str)  : the first keyword.
	   last (str)   : the second keyword.

	Returns:
	   str.  The string between the two keywords.

	"""
	try:
		start = s.index( first ) + len( first )
		allstart = s.index (first)
		end = s.index( last, start )
		new_s = s[:allstart] + s[end:]
		return s[start:end].strip(), new_s
	except ValueError:
		return "", s

def treatStr(val):
	"""Beautifies by adding spaces after commas in strings from lists.

	Args:
	   val (_) : A list-like value which can be converted to string

	Returns:
	   str.  Beautified string.

	.. warning::
	
		ALWAYS pass values that can be converted to string. Otherwise it will
		end up in crashing the program since there is no defined exception handling.

	"""
	string = ''
	if val:
		string = str(val)
	return ', '.join([x.strip() for x in string.split(',')])

def intersectRows(rows, tags, place):
	"""Returns only the rows of data returned by an sql query which contain
	a tag from a given set.

	Args:
	   rows (list(tup)) : list of data returned from an SQL query
	   tags (list)      : the set of tags
	   place (int)      : the position in the tuple where the tags should be found

	Returns:
	   list(tup).  Only the rows with matching tags.

	"""
	outRows = []
	for row in rows:
		keep_it = all([tag in row[place] for tag in tags])
		if keep_it:
			outRows.append(row)
	return outRows

## Splits a string by a given character and returns it as a list of substrings
# @param str $string The input string
# @param str $char The character to split against
# @return List of strings
def splitBy(string,char):
	l_str = [x.strip() for x in string.split(char)]
	return l_str
