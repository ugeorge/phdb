"""
.. module:: phdb.interface.cli
   :platform: Unix, Windows
   :synopsis: Implmenents the core-line interface environment.

The core-line environment uses *docstrings* as in-context help. Check :mod:`cmd`
for details.

.. moduleauthor:: George Ungureanu <ugeorge@kth.se> 

"""

import os
import logging
import logging.config
import cmd
import pickle
import sys

try:
	confPath = os.path.join(os.getenv('PHDB_CFG_PATH'), "logger.conf")
	logging.config.fileConfig(confPath)
except AttributeError:
	print "PHDB_CFG_PATH was not set. Cannot continue execution."
	sys.exit(1)

log  = logging.getLogger('')

from phdb.backend import Backend
from phdb.frontend import Frontend
from phdb.dumper import DbDumper
import phdb.tools.utils as utils
import phdb.core.sqlite3cmd as dbapi


class ConsoleContext(object):
	''' Model class for storing console context.

	:param settings: settings object holding the run-time configuration.
	:type settings: :class:`phdb.tools.settings.Settings`

	This class is called by the main program before starting an interface. It initializes 
	the context based on the run-time configuration and it contains:
	
	 * useful paths
	 * core history
	 * active menu
	 * all the valid tags in the currently-loaded database (for auto-completion)/
	 * context setters/dumpers

	.. note::
	
	   The current state of the module is saved in PHDB_CFG_PATH using :mod:`pickle`.
	'''
	def __init__(self, settings):
		"""Default constructor.
		"""
		self.confPath = settings.configPath

		dbFile        = ''
		self.vTags    = []
		self.hist     = []
		self.active   = ''
		self.confFile = os.path.join(settings.configPath,"cliContext.pickle")

		try :
			with open(self.confFile) as f:
				dbFile, self.vTags, self.active = pickle.load(f)
		except Exception, e:
			log.debug(str(e.__class__) + " " + str(e.args))

		self.db = ''
		if (settings.db):
			self.use_db(settings.db)
		elif dbFile:
			self.use_db(dbFile)

	def use_db(self,args):
		"""Database setter. It sets all context (e.g. valid tags) according to the database. 

		:param args: database.
		:type args: str.
		"""
		if dbapi.isDatabase(args):
			self.db = args
			dbCon = dbapi.Connection(args)
			self.vTags = dbCon.getFrom('Tags')
		else:
			log.error("Database does not exist!")

	def dump(self):
		"""Dumps the context in PHDB_CFG_PATH using :mod:`pickle`

		:param args: database.
		:type args: str.
		"""
		with open(self.confFile, 'w') as f:
			pickle.dump([self.db, self.vTags, self.active], f)		
		

class Console(cmd.Cmd):
	''' Parent class for all consoles.

	:param context:  console context. 
	:type context: :class:`phdb.interface.cli.ConsoleContext`

	This class contains methods used by all classes. It inherits the :class:`cmd.Cmd`.
	Check the documentation for :mod:`cmd` for its usage. All methods starting with 
	`do_` are terminal.cores, and their docstrings are used as console help documentation.  
	'''
	def __init__(self, context):
		"""Class constructor."""
		cmd.Cmd.__init__(self)
		self.context  = context

	def do_hist(self, args):
		"""Print a list of.cores that have been entered"""
		print self.context.hist

	def do_exit(self, args):
		"""Exits from this console"""
		return -1

	def do_EOF(self, args):
		"""Exit on system end of file character"""
		print
		return self.do_exit(args)

	def do_shell(self, args):
		"""Pass core to a system shell when line begins with '!'"""
		os.system(args)

	def do_help(self, args):
		"""Get help on.cores
		'help' or '?' with no arguments prints a list of.cores for which help is available
		'help <core>' or '? <core>' gives help on <core>
		"""
		if not args:
			print self.menuHelp
		cmd.Cmd.do_help(self, args)

	def preloop(self):
		"""Initialization before prompting user for.cores.
		Despite the claims in the Cmd documentaion, Cmd.preloop() is not a stub.
		"""
		cmd.Cmd.preloop(self)   ## sets up core completion
		

	def postloop(self):
		"""Take care of any unfinished business.
		Despite the claims in the Cmd documentaion, Cmd.postloop() is not a stub.
		"""
		cmd.Cmd.postloop(self)   ## Clean up core completion


	def precmd(self, line):
		""" This method is called after the line has been input but before
		it has been interpreted. If you want to modifdy the input line
		before execution (for example, variable substitution) do it here.
		"""
		log.debug("--line input--: "+ line.strip())
		self.context.hist += [ line.strip() ]
		return line

	def postcmd(self, stop, line):
		"""If you want to stop the console, return something that evaluates to true.
		If you want to do some post core processing, do it here.
		"""
		return stop

	def emptyline(self):    
		"""Do nothing on empty input line"""
		pass


	def do_use_db(self,args):
		'''use_db <database_file> 
		Loads the given database.
		'''
		self.context.use_db(args)	

	# assumes that _format and formats are members of the child class.
	# the child class takes care to nullify this method otherwise
	def do_format(self, args):
		'''format <format> [options]
		Output format. May be followed by a set of menu-specific options.
		'''
		def __parseElement(string):
			val = string
			try:
				val = int(string)
			except ValueError:
				pass
			return val
		if args:
			args = args.split(' ')
			if args[0] in self.formats:
				self._format = {'format':args[0]}
				widths = [e for e in map(__parseElement, args[1:]) if isinstance(e, int)]
				flags  = [e for e in map(__parseElement, args[1:]) if isinstance(e, str)]
				self._format['widths'] = widths
				self._format['flags'] = flags
			else:
				log.error("Unrecognized format!")
		else:
			log.error("Unrecognized argument!")
	def complete_format(self, text, line, begidx, endidx):
		if not text:
			completions = self.formats[:]
		else:
			completions = [ f
							for f in self.formats
							if f.startswith(text)
							]
		return completions

	def default(self, line):       
		"""Called on an input line when the core prefix is not recognized.
		In that case we run the line as Python code.
		"""
		try:
			exec(line)
		except Exception, e:
			log.error(str(e.__class__) + " " + str(e.args))

class MainConsole(Console):
	''' Main menu console.

	:param context:  console context. 
	:type context: :class:`phdb.interface.cli.ConsoleContext`

	This class initializes all other (implemented) menus and contains the method
	for calling them.   

	.. note::
		
	   Needs to define context help string (`self.menuHelp`).

	'''
	def __init__(self, context):
		"""Class constructor."""
		Console.__init__(self, context)
		self.prompt   = "PhDB> "
		log.debug("Debugging enabled...")

		print 	"\n"\
				+ "      ----------------------------------------------\n" \
				+ "      PhD Personal Academic Database core console\n" \
				+ "      ----------------------------------------------\n" \
				+ "\n" \
				+ "        (c) 2014 George Ungureanu <ugeorge@kth.se>\n" \
				+ "\n" \
				+ "type 'help' for a list of all.cores in the current menu."

		self.menuHelp = "\nMain menu. You can access all other menus from here."
 

		# all implemented menus are initialised as a dictionary
		self.menu = dict()
		self.menu['entries']       = EntriesConsole(context)
		self.menu['reviews']       = ReviewsConsole(context)
		self.menu['custom-querry'] = CustomConsole(context)
		self.menu['db-admin']      = DbAdminConsole(context)

	def preloop(self):
		"""Overrides :func:`phdb.interface.cli.Console.preloop`"""
		Console.preloop(self)
		if self.context.active:
			self.do_menu(self.context.active)
		
	def postloop(self):
		"""Overrides :func:`phdb.interface.cli.Console.postloop`"""
		Console.postloop(self)
		print "Exiting PhDB console..."
		self.context.dump()
		
	def do_menu(self, arg):
		"""Enter a menu."""
		if arg and arg in self.menu.keys():
			self.context.active = arg
			self.menu[arg].cmdloop()
		else:
			log.error("Unrecognized menu!")
	def complete_menu(self, text, line, begidx, endidx):
		if not text:
			completions = self.menu.keys()[:]
		else:
			completions = [ f
							for f in self.menu.keys()
							if f.startswith(text)
							]
		return completions
	
	def do_format(self, arg):
		'''This core has no use in this prompt.'''
		pass

	def do__debug(self,args):
		log.debug("Environment vars:" +       \
			"\n * activ : " + str(self.context.active) +  \
			"\n * db    : " + str(self.context.db)     +  \
			"\n * vtags : " + str(self.context.vTags))

class ReviewsConsole(Console):
	''' Reviews menu console.

	:param context:  console context. 
	:type context: :class:`phdb.interface.cli.ConsoleContext`

	This class contains methods for building and executing queries for returning
	document reviews.

	.. note::
	
	   The current state of the module is saved in PHDB_CFG_PATH using :mod:`pickle`.
	'''
	def __init__(self,context):
		"""Class constructor.

		.. note::
		
		Needs to define accepted output formats (`self.formats`) and menu help string
		(`self.menuHelp`).

		:param context:  console context. 
		:type context: :class:`interface.cli.ConsoleContext`.
		"""
		Console.__init__(self, context)
		self.prompt   = 'PhDB - reviews> '
		self.menuHelp = "\nReviews menu. You can build and execute queries for "\
						+ "returning document reviews."
		self.confFile = os.path.join(self.context.confPath,"cliReviews.pickle")
		self.formats  = ['plain', 'console', 'latex']
		log.debug("Reviews menu initialized...")

	def preloop(self):
		"""Overrides :func:`phdb.interface.cli.Console.preloop`"""
		Console.preloop(self)
		log.debug("Entering the reviews console...")

		self._sources = []
		self._columns = []
		self._format  = ['console',['30']]
		self._outfile = utils.getFileName(self.context.db) + '.out'
		self._valid   = False
		try :
			with open(self.confFile) as f:
				self._sources, \
				self._columns, \
				self._format,  \
				self._outfile, \
				self._valid    = pickle.load(f)
		except Exception, e:
			log.debug(str(e.__class__) + " " + str(e.args))
		self.do__debug('')


	def postloop(self):
		"""Overrides :func:`phdb.interface.cli.Console.postloop`"""
		Console.postloop(self)
		log.debug("Exiting the reviews console...")
		with open(self.confFile, 'w') as f:
			pickle.dump([ self._sources, \
						  self._columns, \
						  self._format,  \
						  self._outfile, \
						  self._valid], f)

	def do_sources(self, arg):
		"""sources [ref1 [ref2...]]
		Restrict the sources for the query. The sources are referenced by their 
		BibRef. If either no argument or 'all' or '*' ar passed, all sources are 
		targeted by the query.
		"""
		if arg in ['all', '', '*']:
			self._sources = []
		else:
			self._sources = utils.splitBy(arg, ' ')

	def do_columns(self, arg):
		'''columns [col1 [col2...]]
		Returns only specified columns. The user needs to know the column names,
		as defined by the database.
		'''
		self._columns = utils.splitBy(arg, ' ')

	def do_outfile(self,arg):
		'''outfile <file>
		Output file to store the query results.
		'''
		self._outfile = os.path.abspath(arg)

	def do_show_query(self, opt):
		'''Show query built up to this point'''
		db      = self.context.db
		sources = self._sources
		columns = self._columns
		form    = self._format
		outfile = self._outfile

		if not db:
			db = '!missing!'
		if not sources:
			sources = 'all'
		if not columns:
			columns = 'all'
		if form == 'latex':
			form = 'LaTeX markup file'
		elif form == 'plain':
			form = 'plain text'
		if not outfile:
			outfile = '!missing!'

		print '              GET: reviews'
		print '[use_db]      FROM', db			
		print '[sources]     FOR SOURCES:', sources
		print '[columns]     SHOWING COLUMNS:', columns
		print '[format]      PRINTING INFO AS:', form
		print '[outfile]     INTO FILE:', outfile

		self._validate()
		if self._valid:
			log.info("Ready to be executed.")
		else:
			log.warn("Not a valid query. There is still missing information!")

	def _validate(self):
		"""Check if a query is valid."""
		self._valid = True
		if not dbapi.isDatabase(self.context.db):
			self._valid = False
		if not self._outfile:
			self._valid = False

	def do__debug(self,args):
		log.debug("Environment vars:" +    \
			"\n * srcs : " + str(self._sources) +  \
			"\n * frmt : " + str(self._format) +   \
			"\n * cols : " + str(self._columns) +  \
			"\n * outf : " + str(self._outfile) +   \
			"\n * val  : " + str(self._valid))

	def do_run(self, arg):
		'''Executes a valid query. Verify if query is valid with 'show_query' '''

		self._validate()
		if not self._valid:
			log.warn("Query is not valid. Check what is missing with 'show_query' ")
			return

		backend = Backend(form = self._format, outp = self._outfile)
		backend.writeout(msg = 'reviews', 
		                 varDict  = {'db'      : self.context.db, 
		                             'sources' : self._sources,
		                             'columns' : self._columns})


class EntriesConsole(Console):
	''' Entries menu console.

	:param context:  console context. 
	:type context: :class:`phdb.interface.cli.ConsoleContext`

	This class contains methods for building and executing queries for returning
	*'ideas'* or information entries.
	'''
	def __init__(self,context):
		"""Class constructor.

		.. note::
		
		Needs to define accepted output formats (`self.formats`) and menu help string
		(`self.menuHelp`).

		:param context:  console context. 
		:type context: :class:`interface.cli.ConsoleContext`.
		"""
		Console.__init__(self, context)
		self.prompt   = 'PhDB - entries> '
		self.menuHelp = "\nEntries menu. You can build and execute queries for "\
						+ "returning tagged information."
		self.formats  = ['plain', 'console', 'latex']
		self.confFile = os.path.join(self.context.confPath,"cliEntries.pickle")
		log.debug("Initialized entries console...")


	def preloop(self):
		"""Overrides :func:`phdb.interface.cli.Console.preloop`"""
		Console.preloop(self)
		log.debug("Entering the entries console...")

		self._sources  = []
		self._columns  = []
		self._filterExp = []
		self._exclTags = []
		self._format  = ['console',['30']]
		self._outfile = utils.getFileName(self.context.db) + '.out'
		self._valid   = False
		try :
			with open(self.confFile) as f:
				self._sources, \
				self._columns, \
				self._filterExp,\
				self._exclTags,\
				self._format,  \
				self._outfile, \
				self._valid    = pickle.load(f)
		except Exception, e:
			log.debug(str(e.__class__) + " " + str(e.args))
		self.do__debug('')

	def postloop(self):
		"""Overrides :func:`phdb.interface.cli.Console.postloop`"""
		Console.postloop(self)
		log.debug("Exiting the entries console...")
		with open(self.confFile, 'w') as f:
			pickle.dump([ self._sources, \
						  self._columns, \
					      self._filterExp,\
					      self._exclTags,\
						  self._format,  \
						  self._outfile, \
						  self._valid], f)

	def do_sources(self, arg):
		"""sources [ref1 [ref2...]]
		Restrict the sources for the query. The sources are referenced by their 
		BibRef. If either no argument or 'all' or '*' ar passed, all sources are 
		targeted by the query.
		"""
		if arg in ['all', '', '*']:
			self._sources = []
		else:
			self._sources = utils.splitBy(arg, ' ')

	def do_filter_by(self, arg):
		'''filter_by <E>
		Filters output information by specific tags. <E> is a logical expression 
		that has the following operations having tag names as operands:

		+---------+-------------------------------------------------+
		| Operator| Comment                                         |
		+=========+=================================================+
		|  ( E )  | group a set of operations for higher precedence |
		+----------+------------------------------------------------+
		|    &    | logical 'and'                                   |
		+------------+----------------------------------------------+
		|    |    | logical 'or'                                    |
		+---------+-------------------------------------------------+
		|    /    | logical 'not'                                   |
		+------------+----------------------------------------------+

		For example, getting all entries tagged either as 'optimization' or 'speculative' 
		but exclude the ones tagged 'technical', you can build the following filtering
		expression:::

			filter_by (optimization | speculative) & /technical

		For more on creating query filters check the documentation.'''
		self._filterExp=arg
	def complete_filter_by(self, text, line, begidx, endidx):
		if not text:
			completions = self.context.vTags[:]
		else:
			completions = [ f
							for f in self.context.vTags
							if f.startswith(text)
							]
		return completions

	def do_outfile(self,arg):
		'''outfile <file>
		Output file to store the query results.
		'''
		self._outfile = os.path.abspath(arg)

	def do_show_query(self, opt):
		'''Show query built up to this point'''
		db        = self.context.db
		sources   = self._sources
		filterExp = self._filterExp
		columns   = self._columns
		form      = self._format
		outfile   = self._outfile

		if not db:
			db = '!missing!'
		if not filterExp:
			filterExp = '!missing!'
		if not sources:
			sources = 'all'
		if not columns:
			columns = 'all'
		if form == 'latex':
			form = 'LaTeX markup file'
		elif form == 'plain':
			form = 'plain text'
		if not outfile:
			outfile = '!missing!'

		print '              GET: entries'	
		print '[use_db]      FROM', db		
		print '[sources]     FROM SOURCES:', sources
		print '[filter_by]   FILTERED BY:', filterExp
		print '[columns]     SHOWING COLUMNS:', columns
		print '[format]      PRINTING INFO AS:', form
		print '[outfile]     INTO FILE:', outfile

		self._validate()
		if self._valid:
			log.info("Ready to be executed.")
		else:
			log.warn("Not a valid query. There is still missing information!")

	def _validate(self):
		"""Check if a query is valid."""
		self._valid = True
		if not dbapi.isDatabase(self.context.db):
			self._valid = False
		if not self._outfile:
			self._valid = False

	def do__debug(self,args):
		log.debug("Environment vars:" +    \
			"\n * srcs : " + str(self._sources) +   \
			"\n * cols : " + str(self._columns) +   \
			"\n * fexp : " + str(self._filterExp) + \
			"\n * frmt : " + str(self._format) +    \
			"\n * outf : " + str(self._outfile) +   \
			"\n * val  : " + str(self._valid))

	def do_run(self, arg):
		'''Executes a valid query. Verify if query is valid with 'show_query' '''

		self._validate()
		if not self._valid:
			log.warn("Query is not valid. Check what is missing with 'show_query' ")
			return

		backend = Backend(form = self._format, outp = self._outfile)
		backend.writeout(msg = 'entries', 
		                 varDict  = {'db'      : self.context.db, 
		                             'sources' : self._sources,
		                             'columns' : self._columns,
		                             'filter'  : self._filterExp})

		

#TODO: make use of context history
class CustomConsole(Console):
	''' Custom query menu console.

	:param context:  console context. 
	:type context: :class:`phdb.interface.cli.ConsoleContext`

	This class contains methods for inputting and running user-defined queries.
	'''
	def __init__(self,context):
		"""Class constructor.

		.. note::
		
		   Needs to define accepted output formats (`self.formats`) and menu help string
		   (`self.menuHelp`).
		"""
		Console.__init__(self, context)
		self.formats  = ['plain', 'console']
		self.menuHelp = "\nCustom query menu. You can build and execute your own queries."
		self.confFile = os.path.join(self.context.confPath,"cliCustom.pickle")
		self.prompt   = 'PhDB - custom> '
		log.debug("Initialized custom console...")

	def preloop(self):
		Console.preloop(self)
		log.debug("Entering the custom console...")
		self._query   = ''
		self._format  = ['console',['30']]
		self._outfile = utils.getFileName(self.context.db) + '.out'
		try :
			with open(self.confFile) as f:
				self._query,  \
				self._format, \
				self._outfile = pickle.load(f)
		except Exception, e:
			log.debug(str(e.__class__) + " " + str(e.args))
		self.do__debug('')
	
	def postloop(self):
		Console.postloop(self)
		log.debug("Exiting the custom console...")
		with open(self.confFile, 'w') as f:
			pickle.dump([ self._query,  \
						  self._format, \
						  self._outfile], f)

	def do__debug(self,args):
		log.debug("Environment vars:" +    \
			"\n * db   : " + str(self.context.db) +  \
			"\n * cqry : " + str(self._query) +  \
			"\n * frmt : " + str(self._format) +   \
			"\n * outf : " + str(self._outfile))


	def default(self, line):       
		if line.strip().endswith(';'):
			self._query = self._query + line.strip()
			dbCon = dbapi.Connection(self.context.db)
			col_names, rows = dbCon.qGetCustom(self._query)
			backend = Backend(self._format, self._outfile)
			backend.writeout(msg      = 'custom', 
					         varDict  = {'header' : col_names, 
					                     'data'   : rows})
			self._query = ''
		else:
			self._query = self._query + " " + line.strip()

	def do_outfile(self,arg):
		'''outfile <file>
		Output file to store the query results
		'''
		self._outfile = os.path.abspath(arg)

class DbAdminConsole(Console):
	''' Database administration menu console.

	:param context:  console context. 
	:type context: :class:`phdb.interface.cli.ConsoleContext`

	This class contains methods for general administration.cores.
	'''
	def __init__(self,context):
		"""Class constructor.

		.. note::
		
		   Needs to define accepted output formats (`self.formats`) and menu help string
		   (`self.menuHelp`).
		"""
		Console.__init__(self, context)
		self.formats  = ['plain']
		self.menuHelp = "\nDatabase administration menu. You can administer your database "\
						+ "from here."
		self.confFile = os.path.join(self.context.confPath,"cliDbAdmin.pickle")
		self.prompt   = 'PhDB - db-admin> '
		log.debug("Initialized db-admin console...")

	def preloop(self):
		Console.preloop(self)
		log.debug("Entering the db-admin console...")
		self._format  = ['plain']
		self._outpath = utils.getFileName(self.context.db)
		try :
			with open(self.confFile) as f:
				self._format, \
				self._outpath = pickle.load(f)
		except Exception, e:
			log.debug(str(e.__class__) + " " + str(e.args))
		self.do__debug('')
	
	def postloop(self):
		Console.postloop(self)
		log.debug("Exiting the custom console...")
		with open(self.confFile, 'w') as f:
			pickle.dump([ self._format, \
						  self._outpath], f)

	def do__debug(self,args):
		log.debug("Environment vars:" +    \
			"\n * frmt : " + str(self._format) +   \
			"\n * outp : " + str(self._outpath))

	def do_format(self,args):
		'''format <format>
		Output format for database dumper. Implemented formats: `plain`
		'''
		Console.do_format(self,args)

	def do_outpath(self,arg):
		'''outpath <path>
		Output path to dump database
		'''
		self._outpath = os.path.abspath(arg)

	def do_dump_db(self, arg):
		"""dump_db [path]
		Dumps the database as [format] in the <path> directory."""
		if arg:
			self.do_outpath(arg)
		dbCon = dbapi.Connection(self.context.db)
		dumper = DbDumper(self._format, self._outpath)
		dbCon.executeDumpDb(dumper);

	def do_create_db(self,args):
		'''Opens up dialog for creating a database'''

		dbname = raw_input('Database name [default academic]:')
		if not dbname:
			dbname = 'academic'
		dbloc = raw_input('Database location [default '+os.getcwd()+']:')
		if dbloc:
			dbloc = os.path.abspath(dbloc)
		else:
			dbloc = os.getcwd()
		dbres = raw_input('Resource folder (e.g.images) [default '+os.getcwd()+']:')
		if dbres:
			dbres = os.path.abspath(dbloc)
		else:
			dbres = os.getcwd()
		dbin = raw_input('Path to input files [default '+os.getcwd()+']:')
		if dbin:
			dbin = os.path.abspath(dbin)
		else:
			dbin = os.getcwd()

		#try:
		dbapi.createDb(name = dbname, loc = dbloc, resources = dbres)
		self.context.use_db(os.path.join(dbloc,dbname+'.db'))
		dbCon = dbapi.Connection(self.context.db)
		parser = Frontend(dbCon, 'plain', dbin)
		parser.harvest()
		#except Exception as e:
		#	log.error(str(e.__class__) + " " + ', '.join(e.args))
		#return 


	# Evaluate database
	def do_evaluate_db(self, args):
		'''evaluate_db [threshold] [typo_tolerance]

		Evaluates a database  for consistency. 

		 * <threshold> determines the number of minimum tag occurrences to be considered 
		   a valid tag (default is 2).
		 * <typo_tolerance> determines the percentage of similarity between two tags to 
		   be considered a typo (default is 0.75).
		'''
		dbCon = dbapi.Connection(self.context.db)
		threshold = 2
		tolerance = 0.75
		msg = filter(None,args.split(' '))
		if len(msg) > 1:
			threshold = int(msg[0])
			tolerance = float(msg[1])
		elif len(msg) == 1:
			threshold = int(msg[0])
		typoTags = dbCon.evaluateDb_typos(tolerance)
		log.debug(str(typoTags))
		tagsToModify = []
		for t in typoTags:
			text = ''
			mostFrequent = ''
			frequency = 0
			for i in t:
				if i[1] > frequency:
					frequency = i[1]
					mostFrequent = i[0]
				text = text + " '" + i[0] + "' (" + str(i[1]) + " entries),"
			answer = raw_input("The following tags seem to be typos from the same word:" \
				+ text[:-1] + ". Is it true? (y/N)")
			if answer in ['y', 'Y', 'yes', 'YES']:
				for i in t:
					answer = raw_input("Replace '" + i[0] + "' with '" + mostFrequent \
						+ "'? (y/N/correct)")
					if answer.strip() in ['y', 'Y', 'yes', 'YES']:
						tagsToModify.append((i[0], mostFrequent))
					elif not answer.strip() in ['n', 'N', 'no', 'NO', '']:
						tagsToModify.append((i[0], answer))
		dbCon.replaceLinks(('Tags','Tag'), ('Tags__Entries', 'Tag'), tagsToModify)

		invTags = dbCon.evaluateDb_validTag(threshold)
		log.debug(str(invTags))
		tagsToRemove = []
		for i in invTags:
			answer = raw_input("Only " + str(i[1]) + " entries were found for '" \
				+ i[0] + "'. Do you want to remove this tag? (y/N) ")
			if answer.strip() in ['y', 'Y', 'yes', 'YES']:
				tagsToRemove.append(i[0])
		dbCon.removeLinks(('Tags','Tag'), ('Tags__Entries', 'Tag') , tagsToRemove)

		self.context.vTags = dbCon.getFrom('Tags')
		log.debug(str(self.context.vTags))

	def do_show_tags(self, args):
		"""Prints all tags available in the loaded database"""
		for tag in self.context.vTags:
			print tag

	def do_remove_tag(self, arg):
		"""remove_tag <tag1>
		Removes a set of tags from the database (and all its links)."""
		if arg in self.context.vTags:
			dbCon = dbapi.Connection(self.context.db)
			dbCon.removeLinks(('Tags','Tag'), ('Tags__Entries', 'Tag'), [arg])
			self.context.vTags = dbCon.getFrom('Tags')
		else:
			print "Tag does not exist!"
	def complete_remove_tag(self, text, line, begidx, endidx):
		if not text:
			completions = self.context.vTags[:]
		else:
			completions = [ f
							for f in self.context.vTags
							if f.startswith(text)
							]
		return completions

	def do_rename_tag(self, arg):
		"""rename_tag <old_tag> <new_tag>
		Renames a set of tags and takes care of all dependencies in the database.
		"""
		modify = tuple(arg.split(' '))
		if modify[0] in self.context.vTags:
			dbCon = dbapi.Connection(self.context.db)
			dbCon.replaceLinks(('Tags','Tag'), ('Tags__Entries', 'Tag'), [modify])
			self.context.vTags = dbCon.getFrom('Tags')
		else:
			print "Tag does not exist!"
	def complete_rename_tag(self, text, line, begidx, endidx):
		if not text:
			completions = self.context.vTags[:]
		else:
			completions = [ f
							for f in self.context.vTags
							if f.startswith(text)
							]
		return completions
			
