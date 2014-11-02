"""
.. module:: phdbcommand.sqlite3core
   :platform: Unix
   :synopsis: Implmenents the corecommands for working with SQLite3.

.. moduleauthor:: George Ungureanu <ugeorge@kth.se> 

"""

import os
import re
import logging
import difflib
import sys
import sqlite3 as lite

from names import *
from filtergrammar import getExpTree
import phdb.tools.utils as utils

try:
	confPath = os.path.join(os.getenv('PHDB_CFG_PATH'), "logger.conf")
	logging.config.fileConfig(confPath)
except AttributeError:
	pass
logger = logging.getLogger('')

def isDatabase(filename):
	"""Checks if a given file is of SQLite3 format.

	:parameter filename: the path to the file.
	:type filename: str.
	:returns: bool -- `True` if the file is SQLite3.
	"""
	from os.path import isfile, getsize
	
	if not isfile(filename):
		return False
	if getsize(filename) < 100: # SQLite database file header is 100 bytes
		return False
	else:
		fd = open(filename, 'rb')
		Header = fd.read(100)
		fd.close()

		if Header[0:16] == 'SQLite format 3\000':
		    return True
		else:
		    return False


def createDb(name, loc, resources):
	"""Creates an SQLite3 :ref:idb from a chosen frontend.

	:parameter name: The name of the new database.
	:type name: str.
	:parameter loc: The location of the new database.
	:type loc: str.
	:parameter resources: The location of the new database.
	:type resources: str.
	:parameter ftype: The type of the frontend container. Check :mod:`phdb.fontend.api`
	  for available types.
	:type ftype: str.
	:parameter inp: The location of the frontend container folder.
	:type inp: str.
	"""    
	connection = lite.connect(os.path.join(loc,name+'.db'))
	with connection:
		cursor = connection.cursor()
		cursor.execute('SELECT SQLITE_VERSION()')
		data = cursor.fetchone()
		logger.info("SQLite version: %s" % data)

		#create database tables
		cursor.execute("pragma foreign_keys=ON")
		cursor.execute("DROP TABLE IF EXISTS Xrefs")
		cursor.execute("DROP TABLE IF EXISTS Source")
		cursor.execute("DROP TABLE IF EXISTS Entries")
		cursor.execute("DROP TABLE IF EXISTS Tags")
		cursor.execute("DROP TABLE IF EXISTS Tags__Entries")
		cursor.execute("DROP TABLE IF EXISTS Resources")
		cursor.execute("CREATE TABLE Source( \
			BibRef TEXT UNIQUE NOT NULL PRIMARY KEY, \
			Link TEXT, \
			About TEXT)")
		cursor.execute("CREATE TABLE Entries(\
			Id INTEGER PRIMARY KEY AUTOINCREMENT, \
			Source TEXT,\
			At TEXT,    \
			Info TEXT,  \
			Label TEXT, \
			Cites TEXT, \
			Crefs TEXT)")
		cursor.execute("CREATE TABLE Tags(\
			Tag TEXT UNIQUE NOT NULL PRIMARY KEY)")
		cursor.execute("CREATE TABLE Xrefs(\
			RefBy TEXT,\
			RefTo TEXT,\
			FOREIGN KEY(RefBy) REFERENCES Source(BibRef) ,\
			FOREIGN KEY(RefTo) REFERENCES Source(BibRef) )")
		cursor.execute("CREATE TABLE Tags__Entries(\
			Entry INT,\
			Tag TEXT)")
		cursor.execute("CREATE TABLE resources(Path TEXT)")
		cursor.execute("INSERT INTO resources VALUES('" + resources + "')")
	return

class SqLite3FilterParser():
	def __init__ (self, base):
		self.base = base

	def parseNode (self, op, l, r = None):
		if op == 'TAG':
			return self.base + "='" + l + "' "
		elif op == 'WILDB':
			return self.base + "LIKE '%" + l + "' "
		elif op == 'WILDA':
			return self.base + "LIKE '" + l + "%' "
		elif op == '/':
			return 'NOT ' + self.parseNode(*l);
		elif op == '()':
			return '(' + self.parseNode(*l) + ') ';
		elif op == '&':
			return self.parseNode(*l) + ' AND ' + self.parseNode(*r)
		elif op == '|':
			return self.parseNode(*l) + ' OR ' + self.parseNode(*r)

	

class Connection():
	"""Creates a floating connection instance to a given database that can be passed
	without loading the whole core module. It contains basic database operations.

	:parameter db: Path to the database.
	:type db: str.
	"""
	def __init__(self, db): 
		self.connection = lite.connect(db)
		self.cursor = self.connection.cursor() 
		
	def __del__(self):
		self.connection.close()

	def commit(self):
		"""Overloads :func:`sqlite3.Connection.commit function`"""
		self.connection.commit()

	def lastrowid(self):
		return self.cursor.lastrowid

	def insertOrIgnore(self, table, columns, data):
		"""`INSERT OR IGNORE` SQLite statement for introducing multiple rows.

		:parameter table: The table in the :ref:idb
		:type table: str.
		:parameter columns: Columns written as `(col1,col2,...)`.
		:type columns: str.
		:parameter data: Data to be introduced as list of tuples.
		:type data: [(str,),]
		"""
		command   =	"INSERT OR IGNORE " + completeCommand(table, columns)
		self.cursor.executemany(command, data)

	def insertOrReplace(self, table, columns, data):
		"""`INSERT OR REPLACE` SQLite statement for introducing multiple rows.

		:parameter table: The table in the :ref:idb
		:type table: str.
		:parameter columns: Columns written as `(col1,col2,...)`.
		:type columns: str.
		:parameter data: Data to be introduced as list of tuples.
		:type data: [(str,),]
		"""
		command   =	"INSERT OR REPLACE " + completeCommand(table, columns)
		self.cursor.executemany(command, data)

	def insert(self, table, columns, data):
		"""`INSERT` SQLite statement for introducing multiple rows.

		:parameter table: The table in the :ref:idb
		:type table: str.
		:parameter columns: Columns written as `(col1,col2,...)`.
		:type columns: str.
		:parameter data: Data to be introduced as list of tuples.
		:type data: [(str,),]
		"""
		command   =	"INSERT " + completeCommand(table, columns)
		self.cursor.executemany(command, data)

	def insertUnique(self, table, columns, data):
		"""`INSERT` SQLite statement for introducing multiple rows.

		:parameter table: The table in the :ref:idb
		:type table: str.
		:parameter columns: Columns written as `(col1,col2,...)`.
		:type columns: str.
		:parameter data: Data to be introduced as list of tuples.
		:type data: (str,)
		"""
		command   =	"INSERT " + completeCommand(table, columns)
		self.cursor.execute(command, data)
		return self.cursor.lastrowid

	def getFrom(self, table, cols=None, groupBy=None):
		"""Simple SQLite3 querry. Returns the colums from a table in an :ref:idb.

		:parameter db: Path to the database.
		:type db: str.
		:parameter table: Path to the database.
		:type table: str.
		:parameter cols: Columns.
		:type cols: [str,].
		:returns: [str,] -- List with all tags.
		"""
		command = ''
		if groupBy:
			command = "GROUP BY" + groupBy
		command = "SELECT "	+ _colsListToStr("", cols, "*") +" FROM " + table \
					+ command + ";"
		self.cursor.execute(command)        
		self.connection.commit()
		col_names = [cn[0] for cn in self.cursor.description]
		rows = self.cursor.fetchall()
		return [x[0] for x in rows]

	def removeFrom(self, table, col, exp):
		"""Simple SQLite3 remove statement.

		:parameter db: Path to the database.
		:type db: str.
		:parameter table: Path to the database.
		:type table: str.
		:parameter col: Column.
		:type col: str.
		:parameter exp: Filter expression based on the previous column.
		:type exp: str.
		"""
		filterTree = getExpTree(exp)
		parser     = SqLite3FilterParser(col)
		condition  = parser.parseNode(*filterTree)
		command = 'DELETE FROM ' + table + " WHERE " + condition + ';'
		
		self.cursor.execute(command)        
		self.connection.commit()
		

	def replaceLinks(self, original, link, replacePairs):
		"""Replaces a set of linked data in an :ref:idb and takes care of relinking.

		:parameter db: Path to the database.
		:type db: str.
		:parameter original: Pair of table name and column name that points to the place
		 of the original data, which needs to be replaced.
		:type original: (str,str)
		:parameter link: Pair of table name and column name that points to the place
		 of the link that needs to be updated.
		:type link: (str,str)
		:parameter listOfTags: List with pairs of data (to be replaced, replace with).
		:type listOfTags: [(str,str),]
		"""
		origTab = original[0]
		origCol = original[1]
		linkTab = link[0]
		linkCol = link[1]
		for data in replacePairs: 
			logger.info("Replacing '" +data[0]+ "' with '" + data[1])
			self.cursor.execute("INSERT OR IGNORE INTO " + origTab + " (" + origCol \
					+ ") VALUES (?)", (data[1],) )
			self.connection.commit()
			command = "UPDATE " + linkTab + " SET " + linkCol + "='" + data[1] \
					+ "' WHERE " + linkCol + "='" + data[0] + "';"
			self.cursor.execute(command)    
			self.connection.commit()
			command = "DELETE FROM " + origTab + " WHERE " + origCol + " = '" \
					+ data[0] + "';"
			self.cursor.execute(command)  
			self.connection.commit()  
		return

	def removeLinks(self, original, link, removeList):
		"""Removes a set of linked data in an :ref:idb and takes care of removing the links.

		:parameter db: Path to the database.
		:type db: str.
		:parameter listOfTags: The database.
		:type listOfTags: [str,].
		"""
		origTab = original[0]
		origCol = original[1]
		linkTab = link[0]
		linkCol = link[1]
		for data in removeList:
			logger.info("Removing '" + data + "'")
			command = "DELETE FROM " + linkTab + " WHERE " + linkCol + " = '" + data + "';"
			self.cursor.execute(command)    
			self.connection.commit()
			command = "DELETE FROM " + origTab + " WHERE " + origCol + " = '" + data + "';"
			self.cursor.execute(command)  
			self.connection.commit()    
		return

	def qGetCustom(self, q):
		"""Executes a custom SQLite3 query. The user needs to know the architecture of
		the :ref:idb.

		:parameter db: Path to the database.
		:type db: str.
		:parameter q: The query.
		:type q: str.
		"""
		col_names = []
		rows = []
		try:
			self.cursor.execute(q)        
			self.connection.commit()
			col_names = [cn[0] for cn in self.cursor.description]
			rows = self.cursor.fetchall()
			logger.debug(str(rows))
		except Exception as e:
			logger.error(str(e.__class__) + " " + ', '.join(e.args))
		return col_names, rows

	def qGetSources(self, srcs):
		"""Executes a pre-defined query which returns information about sources and
		writes it to a chosen backend.

		:parameter db: Path to the database.
		:type db: str.
		:parameter srcs: List of sources, if specified. Otherwise all sources will be returned.
		:type srcs: [str,]
		:returns: [str,] , [(str,),] -- column headers and data rows
		"""
		col_names = []
		rows = []
		command = "\n" \
			+ "\tSELECT *, GROUP_CONCAT(distinct x.RefTo) AS " + REFERS + ", \n"\
			+ "\t          GROUP_CONCAT(distinct t.Tag) AS " + TAGS + ", \n"\
			+ "\tFROM Source AS s \n"\
			+ "\tLEFT JOIN Entries AS e ON e.Source = s.BibRef \n"\
			+ "\tLEFT JOIN Tags__Entries AS te ON te.Entry = e.Id \n"\
			+ "\tLEFT JOIN Tags AS t ON t.Tag = te.Tag \n"\
			+ "\tLEFT JOIN Xrefs AS x ON x.RefBy = s.BibRef \n"\
			+ "\t"+ _srcListToStr("s.BibRef", srcs) +" \n"\
			+ "\tGROUP BY s.BibRef; "
		logger.debug(command)
		self.cursor.execute(command)        
		self.connection.commit()

		col_names = [cn[0] for cn in self.cursor.description]
		rows = self.cursor.fetchall()
		logger.debug(str(rows))
		return col_names, rows


	def qGetEntries(self, srcs, filterExp):
		"""Executes a pre-defined query which returns (idea) entries and
		writes it to a chosen backend. Includes lable column.

		:parameter db: Path to the database.
		:type db: str.
		:parameter srcs: List of sources, if specified. Otherwise all sources will be returned.
		:type srcs: [str,].
		:parameter filterExp: Filter expression. Will be parsed according 
		  to :mod:`phdbcommand.filterparse`
		:type filterExp: str.
		:returns: [str,] , [(str,),] -- column headers and data rows
		"""

		tags = ''
		if filterExp:
			filterTree = getExpTree(filterExp)
			parser     = Sqlite3FilterParser('te.Tag')
			tags       = 'WHERE ' + parser.parseNode(*filterTree)

		command = " \n"\
			+ "\tSELECT *, GROUP_CONCAT(distinct t.Tag) AS " + TAGGED + "\n"\
			+ "\t	FROM Entries AS e\n"\
			+ "\tLEFT JOIN Tags__Entries AS te ON te.Entry = e.Id \n"\
			+ "\tLEFT JOIN Tags AS t ON t.Tag = te.Tag \n"\
			+ "\t" + tags +" \n"\
			+ "\t" + _srcListToStr("e.Source", srcs) +" \n"\
			+ "\tGROUP BY e.Id; "
		logger.debug(command)
		self.cursor.execute(command)        
		self.connection.commit()

		col_names = [cn[0] for cn in self.cursor.description]
		rows = self.cursor.fetchall()
		rows = [tuple(map(utils.treatStr, x)) for x in rows]
		return col_names, rows

	def qGetCrefs(self, srcs, lables):
		"""Executes a pre-defined query which returns entries associated with a label.

		:parameter db: Path to the database.
		:type db: str.
		:parameter srcs: List of sources, if specified. Otherwise all sources will be returned.
		:type srcs: [str,].
		:parameter labels: List of lables associated with the needed entries
		:type labels: [str,]
		:returns: [str,] , [(str,),] -- column headers and data rows
		"""
		col_names = []
		rows = []

		command = " \n"\
			+ "\tSELECT *, GROUP_CONCAT(distinct t.Tag) AS " + TAGGED + "\n"\
			+ "\t	FROM Entries AS e\n"\
			+ "\tLEFT JOIN Tags__Entries AS te ON te.Entry = e.Id \n"\
			+ "\tLEFT JOIN Tags AS t ON t.Tag = te.Tag \n"\
			+ "\tWHERE e.Label in ("+ _tagsListToStr(lables) +") \n"\
			+ "\tGROUP BY e.Id; "
		logger.debug(command)
		self.cursor.execute(command)        
		self.connection.commit()

		col_names = [cn[0] for cn in self.cursor.description]
		rows = self.cursor.fetchall()
		rows = [tuple(map(utils.treatStr, x)) for x in rows]
		return col_names, rows


	def executeDumpDb(self, dumper):
		"""Dumps the contents of a database in a chosen format, specified in :mod:`phdb.dumper.api`

		:parameter db: Path to the database.
		:type db: str.
		:parameter dumper: An initialized dumper.
		:type outp: :class:`phdb.dumper.api.DbDumper`.
		"""
		command = "SELECT BibRef FROM Source;"
		self.cursor.execute(command)    
		rows = self.cursor.fetchall()
		logger.debug("All sources in DB: " + str(rows))

		for source in rows:
			src = source[0]
			dumper.dumpNewSource(src)

			command = "\n"\
				+ "\tSELECT s.BibRef, s.About, s.Conclusion, GROUP_CONCAT(distinct x.RefTo) \n"\
				+ "\t	FROM Source AS s \n"\
				+ "\tLEFT JOIN Xrefs AS x ON x.RefBy = s.BibRef \n"\
				+ "\tWHERE s.BibRef = '"+ src +"' \n"\
				+ "\tGROUP BY s.BibRef; "
			self.cursor.execute(command)    
			data = self.cursor.fetchall()
			data = map(utils.treatStr, list(data[0]))
			logger.debug(str(data))		
			dumper.dumpRef(data[0]) 
			dumper.dumpAbout(data[1])
			dumper.dumpConcl(data[2])
			dumper.dumpXrefs(data[3])
			dumper.dumpGTags('')

			command = " \n"\
				+ "\tSELECT e.Info, e.At, GROUP_CONCAT(distinct t.Tag)\n"\
				+ "\tFROM Entries AS e\n"\
				+ "\t	LEFT JOIN Tags__Entries AS te ON te.Entry = e.Id \n"\
				+ "\t	LEFT JOIN Tags AS t ON t.Tag = te.Tag \n"\
				+ "\tWHERE e.Source = '"+ src +"' \n"\
				+ "\tGROUP BY e.Id;"	
			self.cursor.execute(command)    
			data = self.cursor.fetchall()
			for entry in data:
				entry = map(utils.treatStr, list(entry))
				logger.debug(str(entry))	
				dumper.dumpEntry(tags = entry[2], at = entry[1], info = entry[0])
		return


	def evaluateDb_typos (self, tolerance):
		"""Evaluates an :ref:idb for typos in the tags.

		:parameter db: Path to the database.
		:type db: str.
		:parameter tolerance: the percentage of similarity between two tags to 
		  be considered a typo.
		:type tolerance: int.
		"""
		command = "SELECT Tag, Count(*) FROM Tags__Entries GROUP BY Tag;"
		self.cursor.execute(command)        
		self.connection.commit()
		col_names = [cn[0] for cn in self.cursor.description]

		rows = self.cursor.fetchall()
		typoList = []
		for row in rows:
			if not rows:
				break
			rows.pop(0)
			currentTypos = [row]
			for potential in rows:
				similarity = 1
				s = difflib.SequenceMatcher(None, row[0], potential[0])
				similarity = s.ratio() if s.ratio() < similarity else similarity
				if similarity >= tolerance:
					currentTypos.append(potential)
			if len(currentTypos) > 1:
				typoList.append(currentTypos)
			rows = [ x for x in rows if not x in currentTypos ]
		return typoList 

	def evaluateDb_validTag (self, threshold):
		"""Evaluates an :ref:idb for inconsistent tags (have too few entries associated).

		:parameter db: Path to the database.
		:type db: str.
		:parameter threshold: the number of minimum tag occurrences to be considered 
		  a valid tag
		:type threshold: int.
		"""
		command = "SELECT Tag, Count(*) FROM Tags__Entries GROUP BY Tag;"
		self.cursor.execute(command)        
		self.connection.commit()
		col_names = [cn[0] for cn in self.cursor.description]
		rows = self.cursor.fetchall()
		invalidTags = []
		for row in rows:
			if row[1] < threshold:
				invalidTags.append(row)
		return invalidTags

def _colsListToStr(prefix, colLst, default):
	"""Helper. Column list to string for query."""
	string = ''
	if colLst:
		for col in colLst:
			string = string + prefix + col + ', '
		string = string[:-2]
	else:
		string = default
	return string

def _tagsListToStr(tagLst):
	"""Helper. Tag list to string for query."""
	string = ''
	for tag in tagLst:
		string = string + "'" + tag + "', "
	string = string[:-2]
	return string

def _srcListToStr(column, srcList):
	"""Helper. Sources list to string for query."""
	string = ''
	if srcList:
		string = "AND "+column+" IN ('"
		for src in srcList:
			string = string + src + "','"
		string = string[:-2] + ")"
	return string

def completeCommand(table, columns):
	"""Helper for completing SQL statements"""
	wildcards = "?," * (columns.count(',') + 1)
	return "INTO " + table + " " + columns \
			+ " VALUES (" +  wildcards[:-1] + ")"


