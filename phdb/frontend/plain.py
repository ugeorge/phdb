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
		self._bibref = ''
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
					self.__add_source_info(f)
					self.__add_general_refs(f)
					self.__add_general_tags(f)
					self.__add_entries(f)
					self.con.commit()

	def __add_source_info(self, f):
		'''Add the source info'''
		self._bibref,f = utils.strAfterF(f, 'BIBREF:')
		about,       f = utils.strAfterF(f, 'ABOUT:')
		concl,       f = utils.strAfterF(f, 'CONCLUSION:')
		self.con.insertOrReplace(                  \
								"Source",                      \
								"(BibRef, About, Conclusion)", \
								[(self._bibref, about, concl),])
		self.logger.debug("Added source: " + self._bibref)

	def __add_general_refs(self, f):
		'''Add the pre-defined references'''
		xrefs,f = utils.strAfterF(f, 'REFERENCES:')
		if xrefs.strip():
			newSources = []
			newXrefs = []
			for ref in utils.splitBy(xrefs,','):
				ref = ref.strip()
				newSources.append((ref,))
				newXrefs.append((self._bibref, ref))
				self.logger.debug("Found reference: " + str((self._bibref, ref)))
			self.con.insertOrIgnore( "Source", "(BibRef)", newSources)
			self.con.insert( "Xrefs", "(RefBy, RefTo)", newXrefs)

	def __add_general_tags(self, f):
		'''Add the pre-defined tags for this source'''
		gTags,f = utils.strAfterF(f, 'TAGS:')
		generalTags = []
		if gTags.strip():
			generalTags = [(x.strip(),) for x in utils.splitBy(gTags,',')]
			self.con.insertOrIgnore( "Tags", "(Tag)", generalTags)


	def __add_entries(self, f):
		'''Add the entries for a source'''
		entry,f = utils.strAfterF(f, 'TAG:')
		while entry:
			self.logger.debug("New entry found:")
			self.__add_new_entry(entry)
			entry,f = utils.strAfterF(f, 'TAG:')

	def __add_new_reference(self, newref):
		'''Add a new reference discovered in-line in the entries'''
		self.con.insertOrIgnore( "Source", "(BibRef)", [(newref,),])
		self.con.insertOrIgnore( "Xrefs", "(RefBy, RefTo)", [(self._bibref, newref),])
		self.logger.debug("Added new reference to: " + newref)

	def __add_new_entry(self, entry):
		'''Add a new entry to this source'''
		tags, entry = utils.find_between(entry, '', '\n')
		self.logger.debug(str(tags))
		at, entry = utils.find_between(entry, 'AT:', '\n')
		label, entry = utils.find_between(entry, 'LABEL:', '\n')

		stripped_tags = []
		for tag in utils.splitBy(tags,','):
			self.con.insertOrIgnore( "Tags", "(Tag)", [(tag.strip(),),])
			stripped_tags.append(tag.strip())

		self.__entry_post_analysis(entry)
		entryId = str(self.con.insertUnique( "Entries", "(Source, At, Info, Label)", (self._bibref, at, entry, label)))
		self.logger.debug("Created entry #" + entryId)

		for tag in stripped_tags:
			self.con.insert( "Tags__Entries", "(Entry, Tag)", [(entryId, tag),])
		for tag in self._genTags:
			self.con.insert( "Tags__Entries", "(Entry, Tag)", [(entryId, tag),])

	def __entry_post_analysis(self,entry):
		'''Post-analysis of the entry text. It identifies entry or source cross-references and acts accordingy.'''
		newrefs = re.findall(r'\[\[(.+?)\]\]', entry) #find in-text references of type [[foo]]
		for newref in newrefs:
			if newref.startswith('Ref:'):
				self.__add_new_reference(utils.strAfter(newref,'Ref:'))


