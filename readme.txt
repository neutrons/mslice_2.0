################################################################################

April 16, 2014

README.TXT file pertaining to the MSlice PyQt development effort.

This README is intended to assist with understanding the organizational
structure of the MSlice family of software.  

Main program: MSlice.pyw
GUI constructor import for main: MSlice.py
GUI construction file: MSlice.ui

Child main program: WorkspaceComposerMain.py
GUI constructor import: WorkspaceComposer.py
GUI construction file: WorkspaceComposer.ui

Subtle note that the pattern of using .pyw was not used for WorkspaceComposer 
as at this point it wasn't clear to the developer how to import a .pyw file as
this seemed a minor issue easy to circumvent.

Qt Designer has been used to produce the .ui files.  The python utility 
pyuic4 is used to convert the .ui file to a .py file.  Though main programs 
have been created from scratch without any sort of builder or converter 
basically following the pattern for how to import then customize GUIs initially
constructed via Qt Designer.

Following python convention, the above mentioned .py and .pyw files 
should be co-located within the same directory, then from a terminal
command prompt type the following command to launch the MSlice application:
python MSlice.pyw 

The current version of MSlice has been built based upon python 2.7 and PyQt4

Running the main program often creates corresponding .pyc files which are
in 'Compiled Python' format.  Subsequent runs of the main program can utilize
these .pyc files thus shortening the initialization time for running the
application.  Largely, these .pyc files can be ignored.

As of this writing, user beware as many features remain to be implemented.