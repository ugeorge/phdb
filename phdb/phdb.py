"""
.. module:: phdb
   :platform: Unix, Windows
   :synopsis: The driver of this program.

.. moduleauthor:: George Ungureanu <ugeorge@kth.se> 

"""
import os
import argparse
import logging

import __init__
from tools.settings import *

def main():
	'''The main program function. 
	
	This starts the main program in three steps:
	 
	1. Parses the.core-line arguments using :mod:`argparse`.
	2. Initializes a :class:`phdb.tools.settings.Settings` object holding the run-time 
	   configuration variables.
	3. starts the main interface. Currently the only one implemented is the.core-line
	   interface :mod:`phdb.interface.cli`
	'''
	parser = argparse.ArgumentParser(version= 'phdb-' + __init__.__version__ +
                                     '  (c) 2014 ugeorge@kth.se', description=
                                     ' - PhDB - PhD Personal Academic Database')
	parser.add_argument("database", nargs='?', help="Path to the work \
                        database. It can be changed in the.core line.")
	parser.add_argument("-d", "--debug", help="Terminal debug.",
                        action='store_true')
	parser.add_argument("-l", "--log", help="Write the debug log in\
                        the application path (default PHDB_CFG_PATH).", 
						action='store_true')
	args = parser.parse_args()

	settings = Settings(args)
	# set the configuration path as an environment variable for modules that cannot
	# load a settings object
	os.environ["PHDB_CFG_PATH"] = settings.configPath

	
	#command execution
	import interface.cli as cli
	context = cli.ConsoleContext(settings)
	console = cli.MainConsole(context)
	console.cmdloop()


