"""
Goniometer Properties Pop-up GUI to enable the user to set:
x,y,z, and rotation direction for Axis0 and Axis1

"""
import sys,os

from ui_GProps import *

#import PyQt modules
from PyQt4 import QtGui, QtCore, Qt

#include this try/except block to remap QString needed when using IPython
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

#import GUI components generated from Qt Designer .ui file
from ui_GProps import *

class SetGoniometerProperties(QtGui.QMainWindow):
    
    #initialize app
    def __init__(self, parent=None):
        #setup main window
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_GoniometerProperties() #defined in ui_GProps.py
        self.ui.setupUi(self)
        self.setWindowTitle("Goniometer Properties")
        self.ui.parent=parent
        self.ui.lineEditGPA0.setText(self.ui.parent.ui.ax0)
        self.ui.lineEditGPA1.setText(self.ui.parent.ui.ax1)
        
        #add signal/slot connection for pushbutton Reset
        self.connect(self.ui.pushButtonGPReset, QtCore.SIGNAL('clicked()'), self.Reset)    
        #add signal/slot connection for pushbutton Done request
        self.connect(self.ui.pushButtonGPDone, QtCore.SIGNAL('clicked()'), self.Done)
        self.show()
        
    def Reset(self):
        self.ui.lineEditGPA0.setText('0,1,0,1')
        self.ui.lineEditGPA1.setText('0,1,0,1')
        
    def Done(self):
        self.ui.parent.ui.ax0=str(self.ui.lineEditGPA0.text())
        self.ui.parent.ui.ax1=str(self.ui.lineEditGPA1.text())
        self.close()
