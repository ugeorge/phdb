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

import phdb.core.sqlite3cmd as test

class TestSettings(unittest.TestCase):
	
	def setUp(self):
		if not os.path.isdir('.temp'):
			os.makedirs('.temp')
		test.createDb('test', '.temp', os.path.join('tests','resources'))
		self.db = os.path.join('.temp', 'test.db')

	def tearDown(self):
		shutil.rmtree('.temp')

	def test_createDb(self):
		self.assertTrue(test.isDatabase(self.db))

	def test_simpleInsertAndRemove(self):
		conn = test.Connection(self.db)
		conn.insert('Tags','(Tag)',[('foo',), ('bar',)])
		conn.insertOrIgnore('Tags','(Tag)',[('bar',), ('baz',)])
		conn.insertOrReplace('Tags','(Tag)',[('baz',), ('spam',)])
		ident = conn.insertUnique('Tags', '(Tag)', ('egg',))
		conn.commit()
		cols, rows = conn.getFrom('Tags')
		self.assertEqual(len(rows), 5)
		self.assertEqual(ident, 6)
		conn.removeFrom('Tags', 'Tag', 'foo | bar')
		cols, rows = conn.getFrom('Tags')
		self.assertEqual(len(rows), 3)


if __name__ == '__main__':
    unittest.main()
