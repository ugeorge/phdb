import os
import shutil
import unittest

class DummyArgs:
	def __init__(self):
		self.database = ''
		self.log = False
		self.debug = True

import phdb.tools.settings as settings

dargs = DummyArgs()
settings = settings.Settings(dargs)
os.environ["PHDB_CFG_PATH"] = settings.configPath

class TestStandaloneCase1(unittest.TestCase):
	
	def setUp(self):
		if not os.path.isdir('.temp1'):
			os.makedirs('.temp1')
		self.db = os.path.join('.temp1', 'test.db')

	#def tearDown(self):
	#	shutil.rmtree('.temp1')

	def test_1_frontend_parse(self):
		import phdb.core.sqlite3cmd as dbapi
		from phdb.frontend import Frontend

		dbapi.createDb(name = 'test', 
						loc = '.temp1', 
						resources = os.path.join('tests','resources'))
		self.assertTrue(dbapi.isDatabase(self.db))
		dbCon = dbapi.Connection(self.db)
		parser = Frontend(dbCon, 'plain', os.path.join('tests','resources'))
		parser.harvest()
		cols, tags = dbCon.getFrom('Tags')
		self.assertEqual(len(tags),6)
		cols, assoc = dbCon.getFrom('Tags__Entries')
		self.assertEqual(len(assoc),12)
		cols, xrefs = dbCon.getFrom('Xrefs')
		self.assertEqual(len(xrefs),1)
		cols, src = dbCon.getFrom('Source')
		self.assertEqual(len(src),2)

	def test_2_basic_querries(self):
		import phdb.core.sqlite3cmd as dbapi

		dbCon = dbapi.Connection(self.db)
		col_names, rows = dbCon.qGetSources()
		print col_names
		self.assertEqual(len(rows), 2)
		col_names, rows = dbCon.qGetEntries()
		self.assertEqual(len(rows), 5)
		col_names, rows = dbCon.qGetEntries(filterExp = '(catchphrase & /motivation) | plea')
		print col_names
		print "\n".join(map(str,rows))
