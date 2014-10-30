"""This module contains all the.core scripts and methods used by this program.
It makes the connection between the interface, frontend, backend and database. 

Since it is the only entity communicating with the database, porting the program to
another database type (for example MySQL, if decided in future revisions) should 
be transparent to all other modules except for this one. For convenience, the.cores
have been split into three categories:

 * *core.cores*: they have to share the same API and functionality, otherwise
   the program crashes when trying to load one instead of the other.
 * *optional.cores*: they might differ between revisions or database implementations,
   and failure of loading by the interface should end in a non-destructive warning. 
   The interface has to take care of handling the exceptions for calling non-existing 
   functions from this module
 * *internal.cores* : are used only by this module. for example 
   :mod:`phdb.core.filtergrammar`

.. moduleauthor:: George Ungureanu <ugeorge@kth.se> 

"""

