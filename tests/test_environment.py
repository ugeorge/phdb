import os
import unittest
import phdb.tools.settings as test

class DummyArgs:
	def __init__(self):
		self.database = ''
		self.log = False
		self.debug = False

class TestSettings(unittest.TestCase):
	
	def setUp(self):
		dargs = DummyArgs()
		self.settings = test.Settings(dargs)

	def test_cfgPath(self):
		self.assertTrue(os.path.exists(self.settings.configPath))

	def test_cfgLogFile(self):
		self.assertTrue(os.path.exists(self.settings.loggerConfFile))

if __name__ == '__main__':
    unittest.main()
