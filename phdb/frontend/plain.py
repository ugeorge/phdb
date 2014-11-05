"""
.. module:: frontend.plain
   :platform: Unix
   :synopsis: Frontend parser for plain text formatted files.

.. moduleauthor:: George Ungureanu <ugeorge@kth.se> 

"""

import os
import re
import logging

try:
	confPath = os.path.join(os.getenv('PHDB_CFG_PATH'), "logger.conf")
	logging.config.fileConfig(confPath)
except AttributeError:
	log.warn("PHDB_CFG_PATH was not set. Cannot log events.")
logger = logging.getLogger(__name__)

import phdb.tools.utils as utils

#TODO: entry post-analysis
class TextParser():
	"""Plain text frontend parser.

	:parameter context: check :class:`phdb.frontend.api.Frontend` 
	:type context: defined in :mod:`phdb.core`
	:parameter path: Input path.
	:type path: str.

	"""
	def __init__(self, connection, path):
		self.logger = logging.getLogger('phdb.frontend.text')
		self.path = path
		self.con = connection
		self.bibref = ''
		self._genTags = []

	def harvest(self):
		'''Start parsing all PhDB files from a folder'''
		self.logger.debug("Searching folder: " + self.path)
		for filename in os.listdir (self.path):
			self.logger.debug("Checking file: " + filename)
			self.harvestFile(os.path.join(self.path,filename))

	def harvestFile(self, filename):
		'''Parse a PhDB text file'''
		if os.path.isfile(filename) and '~' not in filename and '#' not in filename:
			with open(filename, 'r') as f:
				if "#!phdb" in f.readline():
					self.logger.debug("Found phdb file: " + filename)
					self.__parse_header(f)
					self.__parse_entries(f)
					self.con.commit()

	def __parse_header(self, f):
		'''Add the source info'''
		header              = _strHeaderF(f)
		self.bibref, header = _strBetween(header, 'BIBREF:', '\n')
		about, header       = _strBetween(header, 'ABOUT:', '\n')
		self.con.insertOrReplace(  "Source", "(BibRef, About)", [(self.bibref, about),])
		self.logger.debug("Added source: " + self.bibref)

		xrefs, header = _strBetween(header, 'REFERENCES:', '\n')
		if xrefs.strip():
			newXrefs = [(self.bibref, x.strip(),) for x in utils.splitBy(xrefs,',')]
			self.con.insert( "Xrefs", "(RefBy, RefTo)", newXrefs)
		
		gTags, header = _strBetween(header, 'TAGS:', '\n')
		self.genTags = map(str.strip, utils.splitBy(gTags,','))
		if gTags.strip():
			generalTags = [(x.strip(),) for x in self.genTags]
			self.con.insertOrIgnore( "Tags", "(Tag)", generalTags)
		self.logger.debug("Found general tags: " + str(self.genTags))

	def __parse_entries(self, f):
		'''Add the entries for a source'''
		entry,f = _strAfterF(f, 'TAG:')
		while entry:
			self.logger.debug("New entry found:")
			self.__add_new_entry(entry)
			entry,f = _strAfterF(f, 'TAG:')

	def __add_new_entry(self, entry):
		'''Add a new entry to this source'''
		tags, entry  = _strBetween(entry, '', '\n')
		at, entry    = _strBetween(entry, 'AT:', '\n')
		label, entry = _strBetween(entry, 'LABEL:', '\n')
		self.logger.debug(str(tags))

		stripped_tags = []
		for tag in utils.splitBy(tags,','):
			self.con.insertOrIgnore( "Tags", "(Tag)", [(tag.strip(),),])
			stripped_tags.append(tag.strip())

		label = self.bibref + '/' + label

		refs = re.findall(r'\[\[(.+?)\]\]', entry) #find in-text references of type [[foo]]
		cites = []
		crefs = []
		for ref in refs:
			if ref.startswith('Ref:'):
				newref = _strAfter(ref,'Ref:')
				cites.append(newref)
				self.con.insertOrIgnore( "Xrefs", "(RefBy, RefTo)", [(self.bibref, newref),])
				self.logger.debug("Added new reference to: " + newref)
			elif ref.startswith('Cref:'):
				cref = _strAfter(ref,'Cref:')
				if  '/' in cref:
					newref = utils.splitBy(cref,'/')[0]
					self.con.insertOrIgnore( "Xrefs", "(RefBy, RefTo)", [(self.bibref, newref),])
					self.logger.debug("Added new reference to: " + newref)
				else:
					tmp = cref
					cref = self.bibref + '/' + cref 
					entry.replace('Cref:'+tmp, 'Cref:'+cref)
				crefs.append(cref)
		citestr = ','.join(cites)
		crefstr = ','.join(crefs)
		

		entryId = str(self.con.insertUnique( "Entries", "(Source, At, Info, Label, Cites, Crefs)", 
					(self.bibref, at, entry, label, citestr, crefstr)))
		self.logger.debug("Created entry #" + entryId)
		for tag in stripped_tags:
			self.con.insert( "Tags__Entries", "(Entry, Tag)", [(entryId, tag),])
		for tag in self.genTags:
			self.con.insert( "Tags__Entries", "(Entry, Tag)", [(entryId, tag),])


def _strAfterF( f, key ):
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
	for line in f:
		if not '%%' in line:
			if line.startswith(key):
				inside = True
				string = utils.strAfter(line,key)
			if inside:
				string = string + line
				if line.strip() == "":
					return string.strip(),f
	return '', tmp

def _strHeaderF( f ):
	tmp = f
	string = ''
	inside = False
	for line in f:
		if line.startswith('%%'):
			inside = True
			string += line[2:]
		else:
			if inside: return string
	return string


def _strAfter(line,pattern):
	"""Returns the string after a keyword."""
	match = re.search(pattern,line)
	if match:
		befor_keyowrd, keyword, after_keyword = line.partition(pattern)
		return after_keyword

def _strBetween( s, first, last ):
	try:
		start = s.index( first ) + len( first )
		allstart = s.index (first)
		end = s.index( last, start )
		new_s = s[:allstart] + s[end:]
		return s[start:end].strip(), new_s
	except ValueError:
		return "", s
