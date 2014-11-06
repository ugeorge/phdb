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

	def dumpHeader(self,data):
		content = "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n%%\n"
		content += "%% BIBREF: " + data['BIBREF'] + "\n%%\n"
		content += "%% ABOUT: " + data['ABOUT'] + "\n%%\n"
		content += "%% REFERENCES: " + data['REFERENCES'] + "\n%%\n"
		content += "%% TAGS: " + data['TAGS'] + "\n%%\n"
		content += "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n"
		self._f.write(content)

	def dumpEntry(self, data):
		content = "TAG: " + data['TAG'] + "\n"\
				+ "AT: " + data['AT'] + "\n"\
				+ "LABEL: " + data['LABEL'] + "\n"\
				+ data['INFO'] + "\n\n"
		self._f.write(content)

