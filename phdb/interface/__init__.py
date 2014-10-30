"""
.. module:: frontend.plain
   :platform: Unix
   :synopsis: Frontend parser for plain text formatted files.

This module contains all user interfaces implemented for this
project. The driver calls only the interface method with the run-time 
settings. Thus this module alone controls the user experience with 
*PhDB*, and imports the.cores as libraries.

The.cores ***cref*** have been split for convenience into *core.cores* and
*optional.cores*. Thus, to ensure legacy compatibility for new modules,
only the core.cores need to respect the current API for a minimal set of
functionality.

.. warning::

	The interface should crash if the core.cores are not available.

.. warning::

   The interface should continue execution if the optional.cores are not
   implemented, but the interface has to take care of handling the exceptions for
   calling non-existing functions.

.. note::

   All new user interfaces go in here. Check the existing ones for 
   implementation tips.

.. moduleauthor:: George Ungureanu <ugeorge@kth.se> 

"""
