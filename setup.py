from distutils.core import setup

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
#files = ["things/*"]

setup(name = "phdb",
	version = "0.1.0.0",
	description = "PhD Personal Academic Database",
	author = "George Ungureanu",
	author_email = "ugeorge@kth.se",
	url = "-",
	#Name the folder where your packages live:
	#(If you have other packages (dirs) or modules (py files) then
	#put them into the package directory - they will be found 
	#recursively.)
	packages = ['phdb'],
	#package_data = {'package' : files },
	#'runner' is in the root.
	scripts = ["runner"],
	long_description = """Really long text here.""" 
	#
	#This next part it for the Cheese Shop, look a little down the page.
	#classifiers = []     
) 
