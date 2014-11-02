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


import phdb.core.sqlite3cmd as dbapi
import phdb.interface.cli as cli

class TestStandaloneCase1(unittest.TestCase):
	
	def setUp(self):
		if not os.path.isdir('.temp1'):
			os.makedirs('.temp1')
		self.db = os.path.join('.temp1', 'test.db')

	#def tearDown(self):
	#	shutil.rmtree('.temp1')

	def test_frontend_parse(self):
		from phdb.frontend import Frontend

		dbapi.createDb(name = 'test', 
						loc = '.temp1', 
						resources = os.path.join('tests','resources'))
		self.assertTrue(dbapi.isDatabase(self.db))
		dbCon = dbapi.Connection(self.db)
		parser = Frontend(dbCon, 'plain', os.path.join('tests','resources'))
		parser.harvest()
