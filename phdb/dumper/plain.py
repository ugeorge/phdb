"""
.. module:: dumper.plain
   :platform: Unix
   :synopsis: Plain text database dumper.

.. moduleauthor:: George Ungureanu <ugeorge@kth.se> 

"""

import logging
import os

logger = logging.getLogger('phdb.backend.plain')

class PlainDumper():
	"""Plain text file dumper. Dumps the passed content into a text file for 
	each source in the database.
	
	:parameter outp: output folder
	:type outp: str"""
	def __init__(self, outp):
		if not os.path.exists(outp):
			os.makedirs(outp)
		self._path = outp
		self._f = open(os.path.join(self._path,".cfg"), 'w+')

	def __exit__(self, type, value, traceback):
		self._f.close()

	def dumpNewSource(self, ref):
		self._f.close()
		self._f = open(os.path.join(self._path,ref), 'w+')
		self._f.write("#!phdb\n\n")

	def dumpRef(self,text):
		content = "BIBREF: " + text + "\n\n"
		self._f.write(content)

	def dumpAbout(self,text):
		content = "ABOUT: " + text + "\n\n"
		self._f.write(content)

	def dumpConcl(self,text):
		content = "CONCLUSION: " + text + "\n\n"
		self._f.write(content)

	def dumpXrefs(self,text):
		content = "REFERENCES: " + text + "\n\n"
		self._f.write(content)

	def dumpGTags(self,text):
		content = "TAGS: " + text + "\n\nEntries\n-------\n\n"
		self._f.write(content)

	def dumpEntry(self,tags = '', at = '' , info = ''):
		content = "TAG: " + tags + "\n"\
				+ "AT: " + at + "\n"\
				+ info + "\n\n"
		self._f.write(content)

