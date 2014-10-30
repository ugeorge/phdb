.. PhDB documentation master file, created by
   sphinx-quickstart on Thu Sep 18 12:55:50 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PhDB -- PhD personal academic Database
======================================

Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Main
====

.. automodule:: phdb

.. automodule:: phdb.phdb
   :members:


Interfaces
==========

.. automodule:: phdb.interface

.. automodule:: phdb.interface.cli
   :members:

Commands
========

.. automodule:: phdb.command.sqlite3core
   :members:

.. automodule:: phdb.command.sqlite3opt
   :members:

Backends
========

.. automodule:: phdb.backend
   :members:

Implemented submodules
**********************

.. warning::
   These classes **SHOULD NOT BE CALLED** directly from other modules, and should
   be accessed only through the :class:`phdb.backend.Backend` API class.

.. automodule:: phdb.backend.console
   :members:

.. automodule:: phdb.backend.plain
   :members:

Frontends
=========

.. automodule:: phdb.frontend
   :members:

Implemented submodules
**********************

.. warning::
   These classes **SHOULD NOT BE CALLED** directly from other modules, and should
   be accessed only through the :class:`phdb.frontend.Frontend` API class.

.. automodule:: phdb.frontend.plain
   :members:

Database dumpers
================

.. automodule:: phdb.dumper
   :members:

Implemented submodules
**********************

.. warning::
   These classes **SHOULD NOT BE CALLED** directly from other modules, and should
   be accessed only through the :class:`phdb.dumper.DbDumper` API class.

.. automodule:: phdb.dumper.plain
   :members:

Tools
=====

Settings
********

This is something I want to say that is not in the docstring.

.. automodule:: phdb.tools.settings
   :members:

Utils
*****

This is something I want to say that is not in the docstring.

.. automodule:: phdb.tools.utils
   :members:

Text Wrapper
************

This is something I want to say that is not in the docstring.

.. automodule:: phdb.tools.textwrapper
   :members:
