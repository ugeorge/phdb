import os
import re
import shutil
import unittest
import phdb.tools.utils as utils

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
		self.assertEqual(len(tags),7)
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
		self.assertEqual(len(rows), 2)
		col_names, rows = dbCon.qGetEntries()
		self.assertEqual(len(rows), 5)
		col_names, rows = dbCon.qGetEntries(filterExp = '(catchphrase & /motivation) | plea', 
							srcs = ['ugeorge14',])
		self.assertEqual(len(rows), 1)
		col_names, rows = dbCon.qGetEntries(filterExp = '(catchphrase & /motivation) | plea')
		self.assertEqual(len(rows), 2)
		for row in rows:
			info = row[col_names.index("Info")]
			cite = row[col_names.index("Cites")]
			cref = row[col_names.index("Crefs")]
			refs = re.findall(r'\[\[(.+?)\]\]', info)
			for ref in refs:
				if ref.startswith('Ref:'):
					testref = utils.strAfter(ref,'Ref:')
					self.assertTrue(testref in cite)
				if ref.startswith('Cref:'):
					testcref = utils.strAfter(ref,'Cref:')
					self.assertTrue(testcref in cref)

	def test_3_database_manipulation(self):
		import phdb.core.sqlite3cmd as dbapi

		dbCon = dbapi.Connection(self.db)
		typos = dbCon.evaluateDb_typos(0.8)
		self.assertEqual(len(typos),1)
		inval = dbCon.evaluateDb_validTag(2)
		self.assertEqual(len(inval),3)
		dbCon.replaceLinks(('Tags','Tag'), ('Tags__Entries', 'Tag'), 
						[(typos[0][1][0],typos[0][0][0]),] )
		inval = dbCon.evaluateDb_validTag(2)
		self.assertEqual(len(inval),2)
		dbCon.removeLinks(('Tags','Tag'), ('Tags__Entries', 'Tag'), 
						["marshmallow",] )
		cols, tags = dbCon.getFrom('Tags')
		tagstr = [x[0] for x in tags]
		self.assertFalse("marshmallow" in tagstr)

	def test_4_database_dump(self):
		import phdb.core.sqlite3cmd as dbapi
		import phdb.dumper as dump

		dbCon = dbapi.Connection(self.db)
		dumper = dump.DbDumper(parameters = {'format':'plain',}, outp = '.temp1')
		dbCon.executeDumpDb(dumper);
		self.assertTrue(os.path.isfile(os.path.join('.temp1','ugeorge14')))
		self.assertTrue(os.path.isfile(os.path.join('.temp1','haddaway93')))

	"""def test_5_database_format(self):
		import phdb.core.sqlite3cmd as dbapi"""
