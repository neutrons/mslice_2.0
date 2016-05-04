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

"""
try:
    #for up to version 3.2 of Mantid
    from mantidplotpy.proxies import threadsafe_call
except:
    #new for mantid version 3.3
    #from mantidplot.proxies import threadsafe_call #would be the preferred way to call however not working for me...
    #so instead, do it this way:
    import mantidplot
    threadsafe_call=mantidplot.proxies.threadsafe_call
"""    
    
    
try:
    # When running inside Mantidplot, need to use threadsafe_call()
    from mantidplot import threadsafe_call
except ImportError:
    # However threadsafe_call() does not load when outside of Mantidplot
    # So in this case, just make a dummy threadsafe_call() 
    # Define a dummy threadsafe_call method
    def threadsafe_call(callable, *args, **kwargs):
        # forward
        return callable(*args, **kwargs)

    
import mantidqtpython


from PyQt4 import QtCore, QtGui

#app = QtGui.QApplication(sys.argv)

class SliceViewer(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        print "a"
        
    def LoadData(self,ws,label):
        print "b"
        print "label: ",label
        print "ws: ",ws,"  type(ws): ",type(ws)
        self.svw = threadsafe_call(mantidqtpython.MantidQt.Factory.WidgetFactory.Instance().createSliceViewerWindow, ws, label)

        print "b2"
    def SetParams(self,xydim,slicepoint,colormin,colormax,colorscalelog,limits, normalization):
        print "b3"
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
        print "b4"
        sv=threadsafe_call(self.svw.getSlicer)
        threadsafe_call(sv.setNormalization, normalization)
        print "b5"
        # --- Color scale ---
        if (not colormin is None) and (not colormax is None):
            threadsafe_call(sv.setColorScale, colormin, colormax, colorscalelog)
        else:
            if (not colormin is None): threadsafe_call(sv.setColorScaleMin, colormin)
            if (not colormax is None): threadsafe_call(sv.setColorScaleMax, colormax)
        print "b6"
        try:
            print "b7"
            threadsafe_call(sv.setColorScaleLog, colorscalelog)
            print "b8"
        except:
            print "Log color scale not possible."
        # --- XY limits ---
        if not limits is None:
            threadsafe_call(sv.setXYLimits, limits[0], limits[1], limits[2], limits[3])
        print "b9"
    def Show(self):
        print "c"
        wsNames=mtd.getObjectNames()
        print "WS Before SliceViewer: ",wsNames
        threadsafe_call(self.svw.show)

        
        
    def closeEvent(self,event):
        #case when 'X' selected to destroy widget
        print "Handling GUI Close"
        event.accept()
      
        
