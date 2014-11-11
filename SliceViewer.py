#Some notes for using this program:
#
#To run, need to make sure that modules and packages are all compatible with the versions that mantid expects
#Here I'm running the python within the MantidInstall\bin subdirectory
#
#Then from the python command line I run the following:
#execfile(r'C:\Users\mid\Documents\PyQt\MSlice\check-in\man_sv_2.py')

import sys
import os
import imp

sys.path.append(os.environ['MANTIDPATH'])
import PyQt4
from mantid.simpleapi import *
from mantidplotpy.proxies import threadsafe_call
import mantidqtpython


from PyQt4 import QtCore, QtGui

#app = QtGui.QApplication(sys.argv)

class SliceViewer(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        print "a"
        
    def LoadData(self,ws,label):
        print "b"
        self.svw = threadsafe_call(mantidqtpython.MantidQt.Factory.WidgetFactory.Instance().createSliceViewerWindow, ws, label)
        print "b2"
    def SetParams(self,xydim,slicepoint,colormin,colormax,colorscalelog,limits, normalization):
        # --- X/Y Dimensions ---
        if (not xydim is None):
            if len(xydim) != 2:
                raise Exception("You need to specify two values in the 'xydim' parameter")
            else:
                threadsafe_call(sv.setXYDim, xydim[0], xydim[1])
        # --- Slice point ---
        if not slicepoint is None:
            for d in xrange(len(slicepoint)): 
                try:
                    val = float(slicepoint[d])
                except ValueError:
                    raise ValueError("Could not convert item %d of slicepoint parameter to float (got '%s'" % (d, slicepoint[d]))
                sv.setSlicePoint(d, val)  
        # Set the normalization before the color scale
        sv=threadsafe_call(self.svw.getSlicer)
        threadsafe_call(sv.setNormalization, normalization)
        # --- Color scale ---
        if (not colormin is None) and (not colormax is None):
            threadsafe_call(sv.setColorScale, colormin, colormax, colorscalelog)
        else:
            if (not colormin is None): threadsafe_call(sv.setColorScaleMin, colormin)
            if (not colormax is None): threadsafe_call(sv.setColorScaleMax, colormax)
        try:
            threadsafe_call(sv.setColorScaleLog, colorscalelog)
        except:
            print "Log color scale not possible."
        # --- XY limits ---
        if not limits is None:
            threadsafe_call(sv.setXYLimits, limits[0], limits[1], limits[2], limits[3])
        
    def Show(self):
        print "c"
        wsNames=mtd.getObjectNames()
        print "WS Before SliceViewer: ",wsNames
        threadsafe_call(self.svw.show)

        
        
    def closeEvent(self,event):
        #case when 'X' selected to destroy widget
        print "Handling GUI Close"
        event.accept()
      
        
