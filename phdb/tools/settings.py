"""
.. module:: settings
   :platform: Unix, Windows
   :synopsis: Initializes the loggers and stores the run-time configuration.

.. moduleauthor:: George Ungureanu <ugeorge@kth.se> 

"""

import os
import sys
import shutil
import logging


class Settings:
	''' Model class for initializing and storing the run-time configuration.

	This class is called after parsing the.core-line arguments and before running 
	the main program.
	'''
	def __init__(self, args):
		"""Class constructor.

		:param args: parsed.core-line arguments.
		:type args: str.
		"""
		# set paths & names
		self.progPath = os.path.dirname(os.path.abspath(__file__))
		self.db = ''
		if args.database:
			self.db = args.database
		# the user path is either given as an environment variable, or the home folder
		configPath = os.getenv("PHDB_CFG_PATH",  os.path.join(os.path.expanduser("~"),".phdb"))
		if not os.path.exists(configPath):
			os.makedirs(configPath)
		self.configPath = configPath

		# write a logger configuration file, in the config path
		self.loggerConfFile = os.path.join(self.configPath, "logger.conf")
		confString  = "[loggers]\n" \
					+ "keys=root\n\n" \
					+ "[logger_root]\n"
		if args.log:
			confString  = confString + "handlers=screen,file\n"
		else:
			confString  = confString + "handlers=screen\n"
		
		confString = confString \
					+ "level=NOTSET\n\n" \
					+ "[formatters]\n" \
					+ "keys=simple,complex\n" \
					+ "\n" \
					+ "[formatter_simple]\n" \
					+ "format=+%(levelname)s : %(message)s\n" \
					+ "\n" \
					+ "[formatter_complex]\n" \
					+ "format=+%(levelname)s (%(module)s at %(lineno)d) : %(message)s\n" \
					+ "\n" \
					+ "[handlers]\n" \
					+ "keys=file,screen\n" \
					+ "\n" \
					+ "[handler_file]\n" \
					+ "class=handlers.TimedRotatingFileHandler\n" \
					+ "interval=midnight\n" \
					+ "backupCount=5\n" \
					+ "formatter=complex\n" \
					+ "level=DEBUG\n" \
					+ "args=('" + configPath + os.path.sep + "phdb.log',)\n" \
					+ "\n" \
					+ "[handler_screen]\n" \
					+ "class=StreamHandler\n"
		
		if args.debug:
			confString  = confString + "formatter=complex\n"
		else:
			confString  = confString + "formatter=simple\n"

		if args.debug:
			confString  = confString + "level=DEBUG\n"
		else:
			confString  = confString + "level=INFO\n"

		confString  = confString + "args=(sys.stdout,)\n"
		#print confString

		try:
			confFile = open(self.loggerConfFile, "w")
			confFile.write(confString)
		except Exception, e:
			log.debug(str(e.__class__) + " " + str(e.args))
			sys.exit(1)
		finally:
			confFile.close()
	

