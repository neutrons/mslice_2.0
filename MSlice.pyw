"""
################################################################################
#
# MSlice.pyw
#
# April 16, 2014 - original check-in
#
# This program has been inspired by the IDL DAVE MSLICE and Matlab MSLICE 
# applications.  This version developed using PyQt leverages the work done by
# the Mantid Project developing workspaces and algorithms supporting neutron
# scattering research with the intent to provide significant performance 
# improvements thus reducing the time and complexity for producing results.
#
# Utilizing Mantid Workspaces is a significant difference from the MSLICE 
# predecessors.  These workspaces can be grouped for convenience and 
# intermediate workspaces produced in using MSlice can be saved and loaded for 
# later use rather than having to start from the beginning each time - this
# feature yet to be added as of this writing
#
# This program imports the GUI produced via QtDesigner from MSlice.py
#   MSlice.ui --> pyuic4 --> MSlice.py --> imported into MSlice.pyw
#
# The WorkspaceComposer is a child main application which MSlice.pyw can call.
# This application enables a user to select a number of workspaces and group or
# add these together.  The WorkSpaceComposer also enables editing of the 
# workspace groups (add or remove workspaces).  MSlice.pyw imports 
# WorkspaceComposerMain which in turn imports WorkspaceComposerMain.py 
# developed from WorkspaceComposerMain.ui.
#
# At the time of inital check-in, algorithms for calculating projections and
# for data display are outstanding tasks to be done.
#
################################################################################
"""
import sys, os, time
from os.path import expanduser
from PyQt4 import Qt, QtCore, QtGui
from MSlice import *  # .py file created from the .ui file produced by PyQt corresponding to the .pyw file used to instantiate the GUI

import psutil
import numpy as np
import matplotlib
#need to make sure that the QT backend is being used for matplotlib else things won't work...
if matplotlib.get_backend() != 'QT4Agg':
    matplotlib.use('QT4Agg')
from pylab import *

#import custom develped helpers
from MSliceHelpers import *  #getReduceAlgFromWorkspace, getWorkspaceMemSize
#import h5py 
from WorkspaceComposerMain import *
from MPLPowderCutMain import *


#import SliceViewer (here it assumes local module as a Mantid produced module for this does not exist)
from SliceViewer import *
from GProps import *

from utils_dict_xml import *

import config  #bring in configuration parameters and constants

class MSlice(QtGui.QMainWindow):
    
    
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle("Mantid MSlice")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #define things needed for later
        self.ui.numActiveWorkspaces=0  #number of workspaces loaded into memory
        self.ui.activeWSNames=[]       #names of these workspaces
        self.ui.activeWSVarsList=[]    #this is where these workspaces are loaded
        self.ui.activePowderCalcWS=[]  #list for holding projection data for powder sample
        self.ui.activeSCCalcWS=[]      #list for holding projection data for single crystal sample
        self.ui.rememberDataPath=''        #retain path where user selects data
                
        #set global font style by system type as point size seems different on different platforms.
        if os.sys.platform == 'win32':
            #set for windows
            self.setStyleSheet('font-size: 10pt; font-family: Ariel;')
        elif os.sys.platform == 'linux2':
            #set for Linux
            self.setStyleSheet('font-size: 11pt; font-family: Ariel;')
        elif os.sys.platform == 'darwin':
            #mac
            self.setStyleSheet('font-size: 12pt; font-family: Ariel;')
        else:
            #otherwise...
            self.setStyleSheet('font-size: 11pt; font-family: Ariel;')
        
        #const=constants()

        #define actions and callbacks
#        self.connect(self.ui.actionLoad_Workspace_s, QtCore.SIGNAL('triggered()'), self.WorkspaceManagerPageSelect) #make workspace stack page available to user
#        self.connect(self.ui.actionCreateWorkspace, QtCore.SIGNAL('triggered()'), self.CreateWorkspacePageSelect) #define function to call to select files
        self.connect(self.ui.actionExit, QtCore.SIGNAL('triggered()'), self.confirmExit) #define function to confirm and perform exit
        self.connect(self.ui.actionDeleteSelected, QtCore.SIGNAL('triggered()'), self.deleteSelected) #define function to confirm and perform exit
        self.connect(self.ui.actionDeleteAll, QtCore.SIGNAL('triggered()'), self.deleteAll) #define function to confirm and perform exit

#        QtCore.QObject.connect(self.ui.pushButtonPerformActions, QtCore.SIGNAL('clicked(bool)'),self.performWorkspaceActions) #define the function to call to create workspaces from file selection page
        QtCore.QObject.connect(self.ui.pushButtonUpdate, QtCore.SIGNAL('clicked(bool)'),self.Update) #define the function to call to create workspaces from file selection page

        #For some reason GUI tool disables one of these headers so here we're forcing both sets to be enabled
        self.ui.tableWidgetWorkspaces.horizontalHeader().setVisible(True)
        self.ui.tableWidgetWorkspaces.verticalHeader().setVisible(True)

        #Save Log setup
        QtCore.QObject.connect(self.ui.pushButtonSaveLog, QtCore.SIGNAL('clicked(bool)'),self.SaveLogSelect) 

        #setup Calc Proj section
        QtCore.QObject.connect(self.ui.pushButtonPowderCalcProj, QtCore.SIGNAL('clicked(bool)'),self.PowderCalcProjSelect)
        QtCore.QObject.connect(self.ui.pushButtonSCCalcProj, QtCore.SIGNAL('clicked(bool)'),self.SCCalcProjSelect)
        self.ui.pushButtonPowderCalcProj.setEnabled(True) 
        self.ui.pushButtonSCCalcProj.setEnabled(False) 
        self.ui.comboBoxPowderu1.setCurrentIndex(1) #set initial index for powder Calc Projections 
        self.ui.comboBoxPowderu2.setCurrentIndex(1) #set initial index for powder Calc Projections
        self.ui.comboBoxPowderu2.setCurrentIndex(0) #set initial index for powder Calc Projections - seem to need to toggle index 0 to get label to appear initially in GUI
        #setup Single Crystal Calculate Projections
        self.ui.comboBoxSCVAu1Direction.setCurrentIndex(1)
        self.ui.comboBoxSCVAu2Direction.setCurrentIndex(1)
        self.ui.comboBoxSCVAu3Direction.setCurrentIndex(1)
        
        #need to set the Greek characters using unicode format as the global style sheet seems to be overriding setting the font for these labels.
        SYMBOLIC_BASE = 880  #offset into the unicode font set to the Symbolic, or in this case, Greek alphabet - see here: http://www.alanwood.net/unicode/fontsbyrange.html 
        self.ui.labelSCUCalpha.setText(unichr(SYMBOLIC_BASE + 65)+"(*)")
        self.ui.labelSCUCbeta.setText(unichr(SYMBOLIC_BASE + 66)+"(*)")
        self.ui.labelSCUCgamma.setText(unichr(SYMBOLIC_BASE + 67)+"(*)")
        #tried the set the font, but doing this seemed to be ignored.
#        self.ui.labelSCUCalpha.setFont(QtGui.QFont('Symbol',10))
#        self.ui.labelSCUCbeta.setFont(QtGui.QFont('Symbol',10))
#        self.ui.labelSCUCgamma.setFont(QtGui.QFont('Symbol',10))


        #setup workspaces table
        NrowsWS=self.ui.tableWidgetWorkspaces.rowCount()
        print "NrowsWS: ",NrowsWS

#        col=config.WSM_SelectCol
#        for i in range(NrowsWS):
#            addCheckboxToWSTCell(self.ui.tableWidgetWorkspaces,i,col,True)

        #setup timer to enable periodic events such as status update checks
        self.ctimer = QtCore.QTimer()
        self.ctimer.start(5000)
        QtCore.QObject.connect(self.ctimer, QtCore.SIGNAL("timeout()"), self.constantUpdate)

        #setup application elapsed timer
        self.etimer = QtCore.QTimer()
        self.etimer.start(60000)
        self.etimer.minutecntr=0L
        QtCore.QObject.connect(self.etimer, QtCore.SIGNAL("timeout()"), self.elapsedUpdate)		
        
        #select Workspace Manager as the default tab
        self.ui.tabWidgetFilesWorkspaces.setCurrentIndex(0)
        
        #setup progress bars to look nicer than defaults :-)
        self.ui.progressBarStatusMemory.setStyleSheet("QProgressBar {width: 25px;border: 1px solid black; border-radius: 3px; background: white;text-align: center;padding: 0px;}" 
                               +"QProgressBar::chunk:horizontal {background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00CCEE, stop: 0.3 #00DDEE, stop: 0.6 #00EEEE, stop:1 #00FFEE);}")
        self.ui.progressBarStatusCPU.setStyleSheet("QProgressBar {width: 25px;border: 1px solid black; border-radius: 3px; background: white;text-align: center;padding: 0px;}" 
                               +"QProgressBar::chunk:horizontal {background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00CCEE, stop: 0.3 #00DDEE, stop: 0.6 #00EEEE, stop:1 #00FFEE);}")
        self.ui.progressBarStatusProgress.setStyleSheet("QProgressBar {width: 25px;border: 1px solid black; border-radius: 3px; background: white;text-align: center;padding: 0px;}" 
                               +"QProgressBar::chunk:horizontal {background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00CCEE, stop: 0.3 #00DDEE, stop: 0.6 #00EEEE, stop:1 #00FFEE);}")
        #make sure that initial value is zero
        self.ui.progressBarStatusProgress.setValue(0)

        #enable saving of info that has been logged
        QtCore.QObject.connect(self.ui.pushButtonSaveLog, QtCore.SIGNAL('clicked(bool)'), self.pushButtonSaveLogSelect)

        #setup signal and call back for Sample Tab Widget selection
        QtCore.QObject.connect(self.ui.SampleTabWidget, QtCore.SIGNAL('currentChanged(int)'), self.SampleTabWidgetSelect)
        
        #Enable SC Calc Projections button
        self.ui.pushButtonSCCalcProj.setEnabled(True) 

        #setup callbacks for Single Crystal Volume push buttons - Plot, Oplot, and Surface Slice
        QtCore.QObject.connect(self.ui.pushButtonSCVolSlices, QtCore.SIGNAL('clicked(bool)'), self.pushButtonSCVolSlicesSelect)
        QtCore.QObject.connect(self.ui.pushButtonSCVShowParams, QtCore.SIGNAL('clicked(bool)'), self.pushButtonSCVShowParamsSelect)
                 
        #setup SC Volume tab
        #first setup combo boxes
        self.ui.comboBoxSCVolX.setCurrentIndex(1)
        self.ui.comboBoxSCVolX.setCurrentIndex(0)  # seem to need to toggle index 0 to get label to appear initially in GUI
        self.ui.comboBoxSCVolY.setCurrentIndex(1)		
        self.ui.comboBoxSCVolZ.setCurrentIndex(2)	
        self.ui.comboBoxSCVolE.setCurrentIndex(3)			

        #setup callbacks for SC Cut push buttons - Plot and Oplot 
        QtCore.QObject.connect(self.ui.pushButtonSCCutPlot, QtCore.SIGNAL('clicked(bool)'), self.pushButtonSCCutPlotSelect)
        QtCore.QObject.connect(self.ui.pushButtonSCCutOplot, QtCore.SIGNAL('clicked(bool)'), self.pushButtonSCCutOplotSelect)

        #setup SC Cut comboBox initial values
        self.ui.comboBoxSCCutAlong.setCurrentIndex(1)
        self.ui.comboBoxSCCutAlong.setCurrentIndex(0) # seem to need to toggle index 0 to get label to appear initially in GUI
        self.ui.comboBoxSCCutThick1.setCurrentIndex(1)
        self.ui.comboBoxSCCutThick1_2.setCurrentIndex(2)
        self.ui.comboBoxSCCutThick2.setCurrentIndex(3)
        self.ui.comboBoxSCCutY.setCurrentIndex(1)
        self.ui.comboBoxSCCutY.setCurrentIndex(0) # seem to need to toggle index 0 to get label to appear initially in GUI


        #setup callbacks for Powder Cut push buttons - Plot and Oplot 
        QtCore.QObject.connect(self.ui.pushButtonPowderCutPlot, QtCore.SIGNAL('clicked(bool)'), self.pushButtonPowderCutPlotSelect)

        #setup Powder Cut comboBox initial values
        self.ui.comboBoxPowderCutAlong.setCurrentIndex(1)
        self.ui.comboBoxPowderCutAlong.setCurrentIndex(0) # seem to need to toggle index 0 to get label to appear initially in GUI
        self.ui.comboBoxPowderCutThick.setCurrentIndex(1)
        self.ui.comboBoxPowderCutAlong.setCurrentIndex(1)
        self.ui.comboBoxPowderCutAlong.setCurrentIndex(0) # seem to need to toggle index 0 to get label to appear initially in GUI

        #setup callbacks for Single Crystal Slice push buttons - Show Params and Surface Slice
        QtCore.QObject.connect(self.ui.pushButtonSCShowParams, QtCore.SIGNAL('clicked(bool)'), self.pushButtonSCShowParamsSelect)
        QtCore.QObject.connect(self.ui.pushButtonSCSliceSurfaceSlice, QtCore.SIGNAL('clicked(bool)'), self.pushButtonSCSSurfaceSelect) 

        #setup signal/slot for from/to/step changes to recalculate number of points - for X
        QtCore.QObject.connect(self.ui.lineEditSCSliceXFrom, QtCore.SIGNAL('editingFinished()'), self.calcXNpts)
        QtCore.QObject.connect(self.ui.lineEditSCSliceXTo, QtCore.SIGNAL('editingFinished()'), self.calcXNpts)
        QtCore.QObject.connect(self.ui.lineEditSCSliceXStep, QtCore.SIGNAL('editingFinished()'), self.calcXNpts)
        QtCore.QObject.connect(self.ui.comboBoxSCSliceX, QtCore.SIGNAL('currentIndexChanged(int)'), self.calcXNpts)
        #setup signal/slot for from/to/step changes to recalculate number of points - for Y
        QtCore.QObject.connect(self.ui.lineEditSCSliceYFrom, QtCore.SIGNAL('editingFinished()'), self.calcYNpts)
        QtCore.QObject.connect(self.ui.lineEditSCSliceYTo, QtCore.SIGNAL('editingFinished()'), self.calcYNpts)
        QtCore.QObject.connect(self.ui.lineEditSCSliceYStep, QtCore.SIGNAL('editingFinished()'), self.calcYNpts)
        QtCore.QObject.connect(self.ui.comboBoxSCSliceY, QtCore.SIGNAL('currentIndexChanged(int)'), self.calcYNpts)        
                
        #setup SC Slice tab
        #first setup combo boxes
        self.ui.comboBoxSCSliceX.setCurrentIndex(1)
        self.ui.comboBoxSCSliceX.setCurrentIndex(0)  # seem to need to toggle index 0 to get label to appear initially in GUI
        self.ui.comboBoxSCSliceY.setCurrentIndex(1)		
        self.ui.comboBoxSCSliceZ.setCurrentIndex(2)		
        self.ui.comboBoxSCSliceE.setCurrentIndex(3)				

        #setup callbacks for Powder Slice push buttons - Plot, Oplot, and Surface Slice
        QtCore.QObject.connect(self.ui.pushButtonPowderSlicePlotSlice, QtCore.SIGNAL('clicked(bool)'), self.pushButtonPowderSlicePlotSliceSelect)
        QtCore.QObject.connect(self.ui.pushButtonPowderSliceSurfaceSlice, QtCore.SIGNAL('clicked(bool)'), self.pushButtonPowderSliceSurfaceSliceSelect)

        #setup Powder Slice tab
        #first setup combo boxes
        self.ui.comboBoxPowderSliceX.setCurrentIndex(1)
        self.ui.comboBoxPowderSliceY.setCurrentIndex(1)		
        self.ui.comboBoxPowderSliceY.setCurrentIndex(0)		# seem to need to toggle index 0 to get label to appear initially in GUI

        #setup view tabs once the application has been initialized
        self.ui.ViewTabWidget.setCurrentIndex(0)	
        #set Powder Calculate Projections Tab as default on startup
        self.ui.SampleTabWidget.setCurrentIndex(0)  

        #Initialize Status area
        self.ui.statusText="Status Updates"
        datetimestr=time.strftime("%a %b %d %Y %H:%M:%S")+" - Application Start: "
        self.ui.StatusText.append(datetimestr)

        #setup for integrating with workspace group editor
        self.ui.WSMIndex=[]   #WorkSpaceManager Index gives the row number of that table.  -1 indicates new group to be created
        self.ui.GWSName=[]
        self.ui.GWSType=[]
        self.ui.GWSSize=[]
        self.ui.returnName=''
        self.ui.returnType=''
        self.ui.returnSize=''
        
        #setup for saving and restoring single crystal calc proj params
        #set defaults
        #get parameters from GUI:
        #Unit Cell Parameters:
        self.ui.SCUCa=str(self.ui.lineEditUCa.text())
        self.ui.SCUCb=str(self.ui.lineEditUCb.text())
        self.ui.SCUCc=str(self.ui.lineEditUCc.text())
        self.ui.SCUCalpha=str(self.ui.lineEditUCalpha.text())
        self.ui.SCUCbeta=str(self.ui.lineEditUCbeta.text())
        self.ui.SCUCgamma=str(self.ui.lineEditUCgamma.text())
        
        #Crystal Orientations:
        self.ui.SCCOux=str(self.ui.lineEditSCCOux.text())
        self.ui.SCCOuy=str(self.ui.lineEditSCCOuy.text())
        self.ui.SCCOuz=str(self.ui.lineEditSCCOuz.text())
        self.ui.SCCOvx=str(self.ui.lineEditSCCOvx.text())
        self.ui.SCCOvy=str(self.ui.lineEditSCCOvy.text())
        self.ui.SCCOvz=str(self.ui.lineEditSCCOvz.text())
        self.ui.SCCOPsi=str(self.ui.lineEditSCCOPsi.text())
        self.ui.SCCOMN=str(self.ui.lineEditSCCOName.text())		
        
        #Viewing Angle
        self.ui.SCVAu1a=str(self.ui.lineEditSCVAu1a.text())
        self.ui.SCVAu1b=str(self.ui.lineEditSCVAu1b.text())
        self.ui.SCVAu1c=str(self.ui.lineEditSCVAu1c.text())
        self.ui.SCVAu1Label=str(self.ui.lineEditSCVAu1Label.text())
        self.ui.SCVAu2a=str(self.ui.lineEditSCVAu2a.text())
        self.ui.SCVAu2b=str(self.ui.lineEditSCVAu2b.text())
        self.ui.SCVAu2c=str(self.ui.lineEditSCVAu2c.text())
        self.ui.SCVAu2Label=str(self.ui.lineEditSCVAu2Label.text())
        self.ui.SCVAu3a=str(self.ui.lineEditSCVAu3a.text())
        self.ui.SCVAu3b=str(self.ui.lineEditSCVAu3b.text())
        self.ui.SCVAu3c=str(self.ui.lineEditSCVAu3c.text())
        self.ui.SCVAu3Label=str(self.ui.lineEditSCVAu3Label.text())
        
        #Set Default Goniometer Settings - not on MSlice GUI but available via ui_GPrpos GUI
        self.ui.ax0='0,1,0,1'
        self.ui.ax1='0,1,0,1'
        self.connect(self.ui.actionGoniometer_Properties, QtCore.SIGNAL('triggered()'), self.setGProps) 
        
        #enable parameters reset button
        QtCore.QObject.connect(self.ui.pushButtonDefaultSCParams, QtCore.SIGNAL('clicked(bool)'),self.DefaultSCParams)
        #now setup signals and slots for saving and loading parameters
        QtCore.QObject.connect(self.ui.pushButtonSaveSCParams, QtCore.SIGNAL('clicked(bool)'),self.SaveSCParams)
        QtCore.QObject.connect(self.ui.pushButtonLoadSCParams, QtCore.SIGNAL('clicked(bool)'),self.LoadSCParams)
        QtCore.QObject.connect(self.ui.pushButtonCheckSCWorkspace, QtCore.SIGNAL('clicked(bool)'),self.CheckWorkspace)
        
        #Define Slice Single Crystal dictionary used for creating data to view
        ViewSCDict={}

        ViewSCDict.setdefault('u1',{})['index']='0'
        ViewSCDict.setdefault('u1',{})['label']='[H,0,0]'+config.XYZUnits
        ViewSCDict.setdefault('u1',{})['from']=''
        ViewSCDict.setdefault('u1',{})['to']=''
        ViewSCDict.setdefault('u1',{})['Intensity']=''
        
        ViewSCDict.setdefault('u2',{})['index']='1'
        ViewSCDict.setdefault('u2',{})['label']='[0,K,0]'+config.XYZUnits
        ViewSCDict.setdefault('u2',{})['from']=''
        ViewSCDict.setdefault('u2',{})['to']=''
        ViewSCDict.setdefault('u2',{})['Intensity']=''
        
        ViewSCDict.setdefault('u3',{})['index']='2'
        ViewSCDict.setdefault('u3',{})['label']='[0,0,L]'+config.XYZUnits
        ViewSCDict.setdefault('u3',{})['from']=''
        ViewSCDict.setdefault('u3',{})['to']=''
        ViewSCDict.setdefault('u3',{})['Intensity']=''
        
        ViewSCDict.setdefault('E',{})['index']='3'
        ViewSCDict.setdefault('E',{})['label']='E (meV)'
        ViewSCDict.setdefault('E',{})['from']=''
        ViewSCDict.setdefault('E',{})['to']=''
        ViewSCDict.setdefault('E',{})['Intensity']=''
        #make dictionary available to MSlice
        self.ui.ViewSCDict=ViewSCDict
        
        #Define signal/slot for when Viewing Axes change - need a connection for each line edit field in 'Viewing Axes'
        QtCore.QObject.connect(self.ui.lineEditSCVAu1a, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu1b, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu1c, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCDict)        
        QtCore.QObject.connect(self.ui.lineEditSCVAu2a, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu2b, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu2c, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu3a, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu3b, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu3c, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu1Label, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu2Label, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu3Label, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCDict)
        
        #Define signal/slot for changing View Data combo box selections
        QtCore.QObject.connect(self.ui.comboBoxSCSliceX, QtCore.SIGNAL('currentIndexChanged(int)'),self.UpdateComboSCX)
        QtCore.QObject.connect(self.ui.comboBoxSCSliceY, QtCore.SIGNAL('currentIndexChanged(int)'),self.UpdateComboSCY)
        QtCore.QObject.connect(self.ui.comboBoxSCSliceZ, QtCore.SIGNAL('currentIndexChanged(int)'),self.UpdateComboSCZ)
        QtCore.QObject.connect(self.ui.comboBoxSCSliceE, QtCore.SIGNAL('currentIndexChanged(int)'),self.UpdateComboSCE)
        self.ui.ViewSCDataDeBounce=False #need a debouncing flag since we're generating two index changed events: one for using the mouse to select the combobox item, 
        #and a second for programmatically changing the current index when updating the ViewSCDict.  Skip the second update...

        #Define signal/slot for handling SCXNpts and SCYNpts calculations upon value changes
        QtCore.QObject.connect(self.ui.lineEditSCSliceXFrom, QtCore.SIGNAL('textChanged(QString)'),self.updateSCNpts)
        QtCore.QObject.connect(self.ui.lineEditSCSliceXTo, QtCore.SIGNAL('textChanged(QString)'),self.updateSCNpts)
        QtCore.QObject.connect(self.ui.lineEditSCSliceXStep, QtCore.SIGNAL('textChanged(QString)'),self.updateSCNpts)
        QtCore.QObject.connect(self.ui.lineEditSCSliceYFrom, QtCore.SIGNAL('textChanged(QString)'),self.updateSCNpts)
        QtCore.QObject.connect(self.ui.lineEditSCSliceYTo, QtCore.SIGNAL('textChanged(QString)'),self.updateSCNpts)
        QtCore.QObject.connect(self.ui.lineEditSCSliceYStep, QtCore.SIGNAL('textChanged(QString)'),self.updateSCNpts)
        
        
        #Define Volume Single Crystal dictionary used for creating data to view
        ViewSCVDict={}

        ViewSCVDict.setdefault('u1',{})['index']='0'
        ViewSCVDict.setdefault('u1',{})['label']='[H,0,0]'+config.XYZUnits
        ViewSCVDict.setdefault('u1',{})['from']=''
        ViewSCVDict.setdefault('u1',{})['to']=''
        ViewSCVDict.setdefault('u1',{})['Intensity']=''
        
        ViewSCVDict.setdefault('u2',{})['index']='1'
        ViewSCVDict.setdefault('u2',{})['label']='[0,K,0]'+config.XYZUnits
        ViewSCVDict.setdefault('u2',{})['from']=''
        ViewSCVDict.setdefault('u2',{})['to']=''
        ViewSCVDict.setdefault('u2',{})['Intensity']=''
        
        ViewSCVDict.setdefault('u3',{})['index']='2'
        ViewSCVDict.setdefault('u3',{})['label']='[0,0,L]'+config.XYZUnits
        ViewSCVDict.setdefault('u3',{})['from']=''
        ViewSCVDict.setdefault('u3',{})['to']=''
        ViewSCVDict.setdefault('u3',{})['Intensity']=''
        
        ViewSCVDict.setdefault('E',{})['index']='3'
        ViewSCVDict.setdefault('E',{})['label']='E (meV)'
        ViewSCVDict.setdefault('E',{})['from']=''
        ViewSCVDict.setdefault('E',{})['to']=''
        ViewSCVDict.setdefault('E',{})['Intensity']=''
        #make dictionary available to MSlice
        self.ui.ViewSCVDict=ViewSCVDict
        
        #Define signal/slot for when Viewing Axes change - need a connection for each line edit field in 'Viewing Axes'
        QtCore.QObject.connect(self.ui.lineEditSCVAu1a, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCVDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu1b, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCVDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu1c, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCVDict)        
        QtCore.QObject.connect(self.ui.lineEditSCVAu2a, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCVDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu2b, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCVDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu2c, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCVDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu3a, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCVDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu3b, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCVDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu3c, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCVDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu1Label, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCVDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu2Label, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCVDict)
        QtCore.QObject.connect(self.ui.lineEditSCVAu3Label, QtCore.SIGNAL('textChanged(QString)'),self.UpdateViewSCVDict)
        
        #Define signal/slot for changing View Data combo box selections
        QtCore.QObject.connect(self.ui.comboBoxSCVolX, QtCore.SIGNAL('currentIndexChanged(int)'),self.UpdateComboSCVX)
        QtCore.QObject.connect(self.ui.comboBoxSCVolY, QtCore.SIGNAL('currentIndexChanged(int)'),self.UpdateComboSCVY)
        QtCore.QObject.connect(self.ui.comboBoxSCVolZ, QtCore.SIGNAL('currentIndexChanged(int)'),self.UpdateComboSCVZ)
        QtCore.QObject.connect(self.ui.comboBoxSCVolE, QtCore.SIGNAL('currentIndexChanged(int)'),self.UpdateComboSCVE)
        self.ui.ViewSCVDataDeBounce=False #need a debouncing flag since we're generating two index changed events: one for using the mouse to select the combobox item, 
        #and a second for programmatically changing the current index when updating the ViewSCDict.  Skip the second update...

        #Define signal/slot for handling SCXNpts and SCYNpts calculations upon value changes
        QtCore.QObject.connect(self.ui.lineEditSCVolXFrom, QtCore.SIGNAL('textChanged(QString)'),self.updateSCVNpts)
        QtCore.QObject.connect(self.ui.lineEditSCVolXTo, QtCore.SIGNAL('textChanged(QString)'),self.updateSCVNpts)
        QtCore.QObject.connect(self.ui.lineEditSCVolXStep, QtCore.SIGNAL('textChanged(QString)'),self.updateSCVNpts)
        QtCore.QObject.connect(self.ui.lineEditSCVolYFrom, QtCore.SIGNAL('textChanged(QString)'),self.updateSCVNpts)
        QtCore.QObject.connect(self.ui.lineEditSCVolYTo, QtCore.SIGNAL('textChanged(QString)'),self.updateSCVNpts)
        QtCore.QObject.connect(self.ui.lineEditSCVolYStep, QtCore.SIGNAL('textChanged(QString)'),self.updateSCVNpts)
        QtCore.QObject.connect(self.ui.lineEditSCVolZFrom, QtCore.SIGNAL('textChanged(QString)'),self.updateSCVNpts)
        QtCore.QObject.connect(self.ui.lineEditSCVolZTo, QtCore.SIGNAL('textChanged(QString)'),self.updateSCVNpts)
        QtCore.QObject.connect(self.ui.lineEditSCVolZStep, QtCore.SIGNAL('textChanged(QString)'),self.updateSCVNpts)        
        
        
        

    #add slot for workspace group editor to connect to
    @QtCore.pyqtSlot(int)
    def on_button_clicked(self,val):       #signal for this function defined in WorkspaceComposerMain.py
        #val can be used to let this methold know who called it should that be desired
        
        #get constants
        #const=constants()
        
        print "on_button_clicked - val: ",val
        self.ui.pushButtonUpdate.setEnabled(True)
        #now add new group workspace to Workspace Manager table
        table=self.ui.tableWidgetWorkspaces
        GWSName=self.ui.GWSName
        wsname=self.ui.returnName
        wstype=self.ui.returnType
        wssize=self.ui.returnSize
        
        if wsname in GWSName:
            print "** name within the list of names - case to overwrite workspace"
            #case where the resultant workspace already existed
            #overwrite the existing workspace in this case
            val=config.mySigOverwrite
        
        Nrows=table.rowCount()
        if val == config.mySigNorm:
            wsindex=Nrows
            #in case that the workspace name was originally created by the workspace composer, need to add this new name to the GWSName list
            if wsname not in GWSName:
                self.ui.GWSName.append(wsname)
                
        elif val == config.mySigOverwrite:
            #case where we have one workspace with same name in Workspace Mgr and Workspace Composer - overwrite in this case
            for row in range(Nrows):
                #find which row to overwrite
                if wsname == str(table.item(row,config.WSM_WorkspaceCol).text()):
                    wsindex=row
        print "Slot WSMIndex: ",wsindex
        addmemWStoTable(table,wsname,wstype,wssize,wsindex)
        #reset WSM info
#        self.ui.WSMIndex=[]  #learned that clearing this fails re-running an open Workspace Composer
#        self.ui.GWSName=[]
        self.ui.GWSType=[]
        self.ui.GWSSize=[]
        
    def SaveLogSelect(self):
        #save content in the log window to file
        filter='*.txt'
        home=getHomeDir()
        logpathname = str(QtGui.QFileDialog.getSaveFileName(self, 'Save Log', home,filter))
        if logpathname != '':
            fileObj=open(logpathname,'w')
            log=self.ui.StatusText.document().toPlainText()
            fileObj.write(log)
            fileObj.close()

    def PowderCalcProjSelect(self):

        #get constants
        #const=constants()

        #disable Powder Calc Proj until calculations complete
        self.ui.pushButtonPowderCalcProj.setEnabled(False)      	
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Powder Calculate Projections Initiated")		

        #get workspace table to work with
        table=self.ui.tableWidgetWorkspaces

        #get values from combo boxes 
        CBPU1=self.ui.comboBoxPowderu1.currentIndex()
        CBPU1txt=self.ui.comboBoxPowderu1.currentText()
        print "CBPU1: ",str(CBPU1)," ",CBPU1txt
        CBPU2=self.ui.comboBoxPowderu2.currentIndex()
        CBPU2txt=self.ui.comboBoxPowderu2.currentText()
        print "CBPU2: ",str(CBPU2)," ",CBPU2txt

        #now get values from the labels
        LESCu1Label=self.ui.lineEditPowderu1.text()
        print "LESCu1Label: ",LESCu1Label
        LESCu2Label=self.ui.lineEditPowderu2.text()
        print "LESCu2Label: ",LESCu2Label

        NumActiveWorkspaces=self.ui.numActiveWorkspaces
        print "NumActiveWorkspaces: ",NumActiveWorkspaces
        
        #need to determine which workspaces are selected 
        Nrows=table.rowCount()
        pwsSuffix=str(self.ui.lineEditPowderWorkspaceSuffix.text())
        self.ui.progressBarStatusProgress.setValue(0) #clear progress bar
        addcntr=0
        for row in range(Nrows):
            percentbusy=int(100*(row+1)/Nrows)
            self.ui.progressBarStatusProgress.setValue(percentbusy)
            cw=table.cellWidget(row,config.WSM_SelectCol) 
            print "cw: ",cw
            print "type(cw): ",type(cw)
            print "config.WSM_SelectCol: ",config.WSM_SelectCol
            print "config.WSM_SavedCol: ",config.WSM_SavedCol
            cbstat=cw.isChecked()
            if cbstat:
                
                #case to attempt to run calculate projections
                #FIXME - skipped for now, but will need to verify workspace type before running calc proj
                #but for now, we'll assume that it's a powder workspace
                pws=str(table.item(row,config.WSM_WorkspaceCol).text())
                self.ui.StatusText.append(time.strftime('  Input Workspace: '+pws))	
                print "  pws: ",pws
                pws_out=pws+pwsSuffix
                self.ui.StatusText.append(time.strftime('  Output Workspace: '+pws_out))	
                pws=mtd.retrieve(pws)
                if pws.id() == 'Workspace2D':
                    ConvertToMD(pws,'|Q|','Direct',Outputworkspace=pws_out,PreprocDetectorsWS='')
                elif pws.id() == 'WorkspaceGroup':
                    #FIXME - eventually need to check inside group to determine each ws is a Workspace2D type
                    ConvertToMD(pws,'|Q|','Direct',Outputworkspace=pws_out,PreprocDetectorsWS='')
                elif pws.id() == 'MDEventWorkspace<MDEvent,2>':
                    #case convert to MD has already been done 
                    #so employ some mantid workspace handlers...
                    mtd.addOrReplace(pws_out,pws)                
                else:
                    #unhandled case for now
                    pass
                placeholderws=mtd.retrieve(pws_out)
                #once outputworkspace exists, add it back to the table
                pws_type='Powder Calc Proj'
                pws_size=str(float(int(float(placeholderws.getMemorySize())/float(1024*1024)*10))/10)+' MB'
                pws_indx=Nrows+addcntr
                print "pws_out: ",pws_out
                print "pws_type: ",pws_type
                print "pws_size: ",pws_size
                print "table: ",table
                print "config.WSM_SelectCol: ",config.WSM_SelectCol
                table.insertRow(pws_indx)
                addmemWStoTable(table,pws_out,pws_type,pws_size,pws_indx)
                addCheckboxToWSTCell(table,row,config.WSM_SelectCol,False) #row was: pws_indx-1
                addcntr +=1 #increment row counter for where to add a workspace
        table.resizeColumnsToContents();
        time.sleep(0.2) #give some time since processing before clearing progress bar
        self.ui.progressBarStatusProgress.setValue(0) #clear progress bar
        #upon successful completion enable Powder Calc Proj button
        self.ui.pushButtonPowderCalcProj.setEnabled(True)      
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Powder Calculate Projections Complete")	
        print "Powder Calc Workspaces Processed: "

    def SCCalcProjSelect(self):

        try:
            #to avoid various pilot erros from hanging the interface, 
            #catch excpetions here and handle them gracefulle for this method
            #disable Powder Calc Proj until calculations complete
            self.ui.pushButtonSCCalcProj.setEnabled(False)      
            self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Single Crystal Calculate Projections Initiated")		
            
            #get workspace table to work with
            table=self.ui.tableWidgetWorkspaces
    
            #extract values from the line text boxes
            #Unit Cell Parameters:
            SCUCa=str(self.ui.lineEditUCa.text())
            SCUCb=str(self.ui.lineEditUCb.text())
            SCUCc=str(self.ui.lineEditUCc.text())
            SCUCalpha=str(self.ui.lineEditUCalpha.text())
            SCUCbeta=str(self.ui.lineEditUCbeta.text())
            SCUCgamma=str(self.ui.lineEditUCgamma.text())
            print "UC values: ",SCUCa,SCUCb,SCUCc,SCUCalpha,SCUCbeta,SCUCgamma
            
            #Crystal Orientations:
            SCCOux=self.ui.lineEditSCCOux.text()
            SCCOuy=self.ui.lineEditSCCOuy.text()
            SCCOuz=self.ui.lineEditSCCOuz.text()
            SCCOvx=self.ui.lineEditSCCOvx.text()
            SCCOvy=self.ui.lineEditSCCOvy.text()
            SCCOvz=self.ui.lineEditSCCOvz.text()
            SCCOPsi=self.ui.lineEditSCCOPsi.text()	
            SCCOMN=self.ui.lineEditSCCOName.text()	
            print "CO values: ",SCCOux,SCCOuy,SCCOuz,SCCOvx,SCCOvy,SCCOvz,SCCOPsi
    
            #Viewing Angle
            SCVAu1a=self.ui.lineEditSCVAu1a.text()
            SCVAu1b=self.ui.lineEditSCVAu1b.text()
            SCVAu1c=self.ui.lineEditSCVAu1c.text()
            SCVAu1Label=self.ui.lineEditSCVAu1Label.text()
            SCVAu2a=self.ui.lineEditSCVAu2a.text()
            SCVAu2b=self.ui.lineEditSCVAu2b.text()
            SCVAu2c=self.ui.lineEditSCVAu2c.text()
            SCVAu2Label=self.ui.lineEditSCVAu2Label.text()
            SCVAu3a=self.ui.lineEditSCVAu3a.text()
            SCVAu3b=self.ui.lineEditSCVAu3b.text()
            SCVAu3c=self.ui.lineEditSCVAu3c.text()
            SCVAu3Label=self.ui.lineEditSCVAu3Label.text()
            print "VA values: ",SCVAu1a,SCVAu1b,SCVAu1c,SCVAu1Label,SCVAu2a,SCVAu2b,SCVAu2c,SCVAu2Label,SCVAu3a,SCVAu3b,SCVAu3c,SCVAu3Label
    
            #Not doing this portion yet as the functionality is not yet supported in Mantid
            #Viewing Angle - fold
            SCVAu1Fold=self.ui.checkBoxSCVAu1Fold.checkState()
            SCVAu1Center=self.ui.lineEditSCVAu1Center.text()
            SCVAu1Direction=self.ui.comboBoxSCVAu1Direction.currentIndex()
            SCVAu1Directiontxt=self.ui.comboBoxSCVAu1Direction.currentText()
            SCVAu2Fold=self.ui.checkBoxSCVAu2Fold.checkState()
            SCVAu2Center=self.ui.lineEditSCVAu2Center.text()
            SCVAu2Direction=self.ui.comboBoxSCVAu2Direction.currentIndex()
            SCVAu2Directiontxt=self.ui.comboBoxSCVAu2Direction.currentText()
            SCVAu3Fold=self.ui.checkBoxSCVAu2Fold.checkState()
            SCVAu3Center=self.ui.lineEditSCVAu2Center.text()
            SCVAu3Direction=self.ui.comboBoxSCVAu2Direction.currentIndex()
            SCVAu3Directiontxt=self.ui.comboBoxSCVAu2Direction.currentText()
            #print "VA - fold u1: ",SCVAu1Fold,SCVAu1Center,SCVAu1Direction,SCVAu1Directiontxt
            #print "VA - fold u2: ",SCVAu2Fold,SCVAu2Center,SCVAu2Direction,SCVAu2Directiontxt
            #print "VA - fold u3: ",SCVAu3Fold,SCVAu3Center,SCVAu3Direction,SCVAu3Directiontxt
    
            #need to determine which workspaces are selected 
            Nrows=table.rowCount()
            cwsSuffix=str(self.ui.lineEditSCWorkspaceSuffix.text()) #get workspace suffix to append to resultant workspace from GUI
            self.ui.progressBarStatusProgress.setValue(0) #clear progress bar
            addcntr=0
            NumSelWorkspaces=0
            for row in range(Nrows):
                percentbusy=int(100*(row+1)/Nrows)
                self.ui.progressBarStatusProgress.setValue(percentbusy)
                cw=table.cellWidget(row,config.WSM_SelectCol) 
                print "cw: ",cw
                print "type(cw): ",type(cw)
                cbstat=cw.isChecked()
                if cbstat:
                    NumSelWorkspaces+=1
                    cws=str(table.item(row,config.WSM_WorkspaceCol).text())
                    self.ui.StatusText.append(time.strftime('  Input Workspace: '+cws))	
                    
    
            #**************************************************************************
            #
            #Initial implementation of SC expects a single group workspace
            
            if NumSelWorkspaces != 1:
                #case where we have more or less than one (group) workspace
                dialog=QtGui.QMessageBox(self)
                dialog.setText("Need a single workspace or a group workspace - returning")
                dialog.exec_()  
                return
            #print a warning if the workspace is not a group workspace
            cwsName=cws
            cws=mtd.retrieve(cws) #now retrieve cws using it's string name to have a Mantid workspace
            if cws.id() != 'WorkspaceGroup':
                print "Notice: single workspace is not a group workspace"
                
            #update Ei and S1
            try:
                #using try in case S1 is not the correct motor name
                Ei=cws.run().getProperty('Ei').value
                self.ui.labelSCEi.setText("Ei: "+"%.3f" % Ei)
                S1=cws.run().getProperty('S1').firstValue()
                self.ui.labelSCS1.setText("Start Angle: "+"%.3f" % S1)
            except:
                pass
            
            cws_out=cwsName+cwsSuffix
            
            self.ui.StatusText.append(time.strftime('  Output Workspace: '+cws_out))	
            
            #
            #place variables into Mantid Algorithms
            #FIXME - need a generic way to determine Axis0 name
            # From Mantid Documentation: Axis0: name, x,y,z, 1/-1 (1 for ccw, -1 for cw rotation). A number of degrees can be used instead of name. Leave blank for no axis
            motorName=str(self.ui.lineEditSCCOName.text())
            #check if motor name given - if not, request 
            if motorName=='':
                #case where we need to send the user back to fill in the value
                motorName,ok = QtGui.QInputDialog.getText(self,"Set Goniometer","Input Motor Name")
                if motorName == "" or motorName == None:
                    #we tried to be nice and ask again, just send the user back to the GUI
                    return
            motorName=str(motorName) #if we get here, we should have a motor name
            self.ui.lineEditSCCOName.setText(motorName)
            print "Motor Name: ",motorName
        
            Psi=str(self.ui.lineEditSCCOPsi.text())
            #check if Psi angle given - if not, request 
            if Psi=='':
                #case where we need to send the user back to fill in the value
                Psi,ok = QtGui.QInputDialog.getText(self,"Set Goniometer","Input Psi")
                if Psi == "" or Psi == None:
                    #we tried to be nice and ask again, just send the user back to the GUI
                    return
            Psi=str(Psi) #if we get here, we should have a Psi angle
            self.ui.lineEditSCCOPsi.setText(Psi)
            print "Psi: ",Psi
            ax0=str(self.ui.ax0)
            ax1=str(self.ui.ax1)
            print "ax0: ",ax0,"  ax1: ",ax1
            #SetGoniometer(Workspace=cws,Axis0='s1,0,1,0,1',Axis1='7.5,0,1,0,1') 
            SetGoniometer(Workspace=cws,Axis0=motorName+','+ax0,Axis1=Psi+','+ax1) 
            u=str(SCCOux)+','+str(SCCOuy)+','+str(SCCOuz)
            v=str(SCCOvx)+','+str(SCCOvy)+','+str(SCCOvz)
            SetUB(Workspace=cws,a=SCUCa,b=SCUCb,c=SCUCc,alpha=SCUCalpha,beta=SCUCbeta,gamma=SCUCgamma,u=u,v=v)
            #FIXME - note in ConvertToMD may want to support additional modes that direct some point into the future but hard coded for now
            #Some notes:
            # - ConvertToMDMinMaxGlobal requires a single workspace, not a group workspace to give results
            # - As long as Ei is the same for all workspaces in the group, minn and maxx will be the same for all workspaces in that group
            # - Since ConvertToMDMinMaxGlobal will sense the UB workspace, Autoselect will automatically select HKL mode for Q3DFrames
            if cws.id() != 'WorkspaceGroup':
                # single workspace case - no index on cws
                minn,maxx = ConvertToMDMinMaxGlobal(InputWorkspace=cws,QDimensions='Q3D',dEAnalysisMode='Direct')
            else:
                # group workspace - use index on cws
                minn,maxx = ConvertToMDMinMaxGlobal(InputWorkspace=cws[0],QDimensions='Q3D',dEAnalysisMode='Direct')
            Uproj=str(SCVAu1a)+','+str(SCVAu1b)+','+str(SCVAu1c)
            Vproj=str(SCVAu2a)+','+str(SCVAu2b)+','+str(SCVAu2c)
            Wproj=str(SCVAu3a)+','+str(SCVAu3b)+','+str(SCVAu3c)
            ConvertToMD(InputWorkspace=cws,OutputWorkspace=cws_out,QDimensions='Q3D',QConversionScales='HKL',MinValues=minn,MaxValues=maxx,Uproj=Uproj,Vproj=Vproj,Wproj=Wproj,PreprocDetectorsWS='')
            #
            #**************************************************************************
    
            #once outputworkspace exists, add it back to the table
            placeholderws=mtd.retrieve(cws_out)
            cws_type='Single Crystal Calc Proj'
            
            #to determine memory size, must add sizes of each workspace in the group as the group workspace itself does not provide the composite size
            #also note that memory size can differ from disk size - will consider if/how to address this later
            if cws.id() != 'WorkspaceGroup':
                # single workspace case 
                Nws=1
                sz=float(placeholderws.getMemorySize())
            else:
                # group workspace case
                Nws=len(placeholderws)
                sz=0.0
                for i in range(Nws):
                    sz+=float(placeholderws[i].getMemorySize())
            cws_size=str(float(int(sz/float(1024*1024)*10))/10)+' MB'
            cws_indx=Nrows#+NumSelWorkspaces #here this should be equivalent to Nrows+1
            print "cws_out: ",cws_out
            print "cws_type: ",cws_type
            print "cws_size: ",cws_size
            table.insertRow(cws_indx)
            addmemWStoTable(table,cws_out,cws_type,cws_size,cws_indx)
            addCheckboxToWSTCell(table,row,config.WSM_SelectCol,False) #row was: pws_indx-1
            
            #update ViewSCDict with minn and maxx values calculated above
            ViewSCDict=self.ui.ViewSCDict
            ViewSCDict['u1']['from']=minn[0]
            ViewSCDict['u1']['to']=maxx[0]            
            ViewSCDict['u2']['from']=minn[1]
            ViewSCDict['u2']['to']=maxx[1] 
            ViewSCDict['u3']['from']=minn[2]
            ViewSCDict['u3']['to']=maxx[2] 
            ViewSCDict['E']['from']=minn[3]
            ViewSCDict['E']['to']=maxx[3] 

            #update ViewSCVDict with minn and maxx values calculated above
            ViewSCVDict=self.ui.ViewSCVDict
            ViewSCVDict['u1']['from']=minn[0]
            ViewSCVDict['u1']['to']=maxx[0]            
            ViewSCVDict['u2']['from']=minn[1]
            ViewSCVDict['u2']['to']=maxx[1] 
            ViewSCVDict['u3']['from']=minn[2]
            ViewSCVDict['u3']['to']=maxx[2] 
            ViewSCVDict['E']['from']=minn[3]
            ViewSCVDict['E']['to']=maxx[3]             
            
            
        except Exception as e:
            #parse error messages and provide info to user
            etype=e.__class__.__name__
            #exception types found here: https://docs.python.org/3/library/exceptions.html 
            
            #add handling specific to cases discovered in using the code
            msg0=''
            #retrieve error message info and interpret this for the user
            if e.args[0] == "'NoneType' object has no attribute 'isChecked'":
                msg0='No files selected'
            #can add additional elif clauses here as more error types are handled
            elif etype == 'ValueError':
                msg0='Wrong file type selected'
            else:
                msg0='Non-fatal error encountered'
                
            #also check if there are any system errors
            syserr=sys.stderr.errors
            if syserr==None:
                syserr=''
                
            #retrieve exception error message and write to log - this info useful for programmer but not user...
            msg1=e.args[0]
            self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+msg1)	
            
            #Compile the entire message from substrings created above and present it to the user
            msg="Type: "+etype+" - "+msg0+" - "+syserr
            dialog=QtGui.QMessageBox(self)
            dialog.setText("Non-Fatal Error: "+msg)
            dialog.exec_()  

            
        else:
            #case where try completes successfully and we want to know specifically that it has
            self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Single Crystal Calculate Projections Complete")	
            
        finally:
            #this code executed for either case for try/except conditions occuring
            #upon completion enable Powder Calc Proj button
            self.ui.pushButtonSCCalcProj.setEnabled(True)      
            self.ui.progressBarStatusProgress.setValue(0) #clear progress bar
        
    def Update(self):
        print "** Update "
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Updating Workspace Manager")
        #const=constants()

        self.ui.tableWidgetWorkspaces.setEnabled(False)
        self.ui.pushButtonPowderCalcProj.setEnabled(True) 
        self.ui.pushButtonSCCalcProj.setEnabled(True) 
        self.ui.activeWSNames=[]
        table=self.ui.tableWidgetWorkspaces
        #first let's clean up empty rows
        Nrows=table.rowCount()
        roff=0
        for row in range(Nrows):
            item=table.item(row,config.WSM_WorkspaceCol) #need to convert item from Qstring to string for comparison to work
            itemStr=str(item)
            print "itemStr: ",itemStr
            if itemStr == 'None':
                table.removeRow(row-roff)
                roff=roff+1	
        #now let's determine which action to take
        
        if self.ui.radioButtonLoadSingleWorkspace.isChecked():  
            #Load workspaces or groups from files
            
            #open dialog box to select files
            if self.ui.rememberDataPath=='':
                curdir=os.curdir
            else:
                curdir=self.ui.rememberDataPath
            filter="NXS (*.nxs);;All files (*.*)"
            wsFiles = QtGui.QFileDialog.getOpenFileNames(self, 'Open Workspace(s)', curdir,filter)
            self.ui.rememberDataPath=os.path.dirname(str(wsFiles[0]))
        
            #for each file selected:
            #  - load mantid workspace
            #  - populate workspace manager table
            Nfiles=len(wsFiles)
            
            table=self.ui.tableWidgetWorkspaces
            
            print "Number of files selected: ",Nfiles
            cntr=1 #used for calculating progress bar % complete...
            gotOne=0
            for wsfile in wsFiles:
                basename=os.path.basename(str(wsfile))
                fileparts=os.path.splitext(basename)
                wsName=fileparts[0]
                Load(Filename=str(wsfile),OutputWorkspace=wsName)
                #make sure workspaces are available at the python level
                __ws=mtd.retrieve(wsName)
                print "** type(__ws): ",type(__ws)
                #check if the workspace just loaded is a single crystal CalcProj workspace
                #need to check workspace history to determine this
                histDictTmp=histToDict(__ws)
                #check if workspace history has entries for:
                # - SetGoniometer
                # - SetUB
                # - ConvertToMD
                #as each of these contain params needed for the GUI
                    
                try:
                    #check if the needed settings are present
                    Goniometer=histDictTmp['SetGoniometer']
                    UB=histDictTmp['SetUB']
                    MD=histDictTmp['ConvertToMD']
                    histDict=histDictTmp
                    wsfiletmp=wsfile
                    gotOne +=1
                except:
                    #case where the needed parameters for SC CalcProj not available in the workspace
                    #skip this workspace and check next one if there are more.
                    pass
                
                #check if we found more than one SC Calc Proj workspace
                
                print "gotOne: ",gotOne
                
                if gotOne > 1:
                    #inform user that multiple SCCalcProj workspaces discovered
                    #and using the last one found
                    msg='Multiple SC Calc Proj workspaces discovered - using parameters from : '+__ws.name()
                    dialog=QtGui.QMessageBox(self)
                    dialog.setText(msg)
                    dialog.exec_()  
                    
                #case we have parameters for latest SC Calc Proj workspace
                #put params into GUI
                if gotOne >= 1:
                    #case to update parameters on GUI
                    updateSCParms(self,histDict,['Slice'])
                    updateSCParms(self,histDict,['Volume'])
                    #make corresponding SC tabs on top
                    self.ui.SampleTabWidget.setCurrentIndex(1) 
                    self.ui.ViewTabWidget.setCurrentIndex(1)	
                    
                    
                
                percentbusy=int(float(cntr)/float(Nfiles)*100)
                self.ui.progressBarStatusProgress.setValue(percentbusy) #adjust progress bar according to % busy
                time.sleep(0.01)  #seem to need a small delay to ensure that status updates
                cntr += 1
                #now populate table
                self.ui.StatusText.append("  Loading workspace:"+str(wsName))
                addWStoTable(table,wsName,wsfile)
                #update table with memory size rather than file size in the Size column of the Workspace Manager
                
            #in case for loading single crystal CalcProj workspace, also
            #need to fill-in parameters section of GUI
            #first need to determine how many files are selected as the params
            #from only one file can be placed in the GUI.  At this point we are
            #not checking to see if the params are the same for all selected
            #SC CalcProj workspaces - leaving it to the user to ensure selected
            #files have compatible parameters.
            if Nfiles > 0:
                #case to begin sorting out single crystal parameters.
                __ws=mtd.retrieve(wsName)
                histDict=histToDict(__ws)
                
            table.resizeColumnsToContents();
            self.ui.progressBarStatusProgress.setValue(0) #adjust progress bar according to % busy
            
        elif self.ui.radioButtonComposeSelected.isChecked():  
            #edit existing workspace group using the workspace group editor
            self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Calling Workspace Composer Edit Workspace")
            #first need to determine which workspace selected in the workspace manager
            table=self.ui.tableWidgetWorkspaces
            #first let's clean up empty rows
            Nrows=table.rowCount()
            selrow=[]
            for row in range(Nrows):
                #get checkbox status            
                cw=table.cellWidget(row,config.WSM_SelectCol) 
                try:
                    cbstat=cw.isChecked()
                    print "row: ",row," cbstat: ",cbstat
                    if cbstat == True:
                        #case to identify selected row number
                        selrow.append(row)
                except AttributeError:
                    #case where rows have been deleted and nothing do check or do
                    print "unexpected case"

            #once done checking selects, determine:
            # if none were selected
            # if more than one were selected
            # or just one was selected
            if len(selrow) >= 0:
                #preferred case - just do it
                print "type WSMIndex: ",type(self.ui.WSMIndex)
                for row in selrow:
                    self.ui.WSMIndex.append(row)   #WorkSpaceManager Index gives the row number of that table.  -1 indicates new group to be created
                    self.ui.GWSName.append(str(table.item(row,config.WSM_WorkspaceCol).text()))
                self.child_win = WorkspaceComposer(self)
                self.child_win.show()                    
                
            else:
                print "this case not anticipated...doing nothing"        
            
        elif self.ui.radioButtonSelectAll.isChecked():  
            #set all checkboxes in the workspace manager table
            #first check if there are any rows to update selection
            item=table.item(0,config.WSM_WorkspaceCol) #need to convert item from Qstring to string for comparison to work
            itemStr=str(item)
#            print "itemStr: ",itemStr
            #then only update the rows if rows with content are discovered.
            if itemStr != 'None':
                Nrows=table.rowCount()
                for row in range(Nrows):
                    addCheckboxToWSTCell(table,row,config.WSM_SelectCol,True)            

        elif self.ui.radioButtonClearAll.isChecked():  
            #clear all checkboxes in the workspace manager table
            #first check if there are any rows to update selection
            item=table.item(0,config.WSM_WorkspaceCol) #need to convert item from Qstring to string for comparison to work
            itemStr=str(item)
#            print "itemStr: ",itemStr
            #then only update the rows if rows with content are discovered.
            if itemStr != 'None':
                Nrows=table.rowCount()
                for row in range(Nrows):
                    addCheckboxToWSTCell(table,row,config.WSM_SelectCol,False)          
            
        elif self.ui.radioButtonSaveSelected.isChecked():  
            #save selected workspaces
            table=self.ui.tableWidgetWorkspaces
            #first let's clean up empty rows
            Nrows=table.rowCount()
            selrow=[]
            for row in range(Nrows):
                #get checkbox status            
                cw=table.cellWidget(row-roff,config.WSM_SelectCol) 
                try:
                    cbstat=cw.isChecked()
                    print "row: ",row," cbstat: ",cbstat
                    if cbstat == True:
                        #case to identify selected row number
                        selrow.append(row)
                except AttributeError:
                    #case where rows have been deleted and nothing do check or do
                    pass
            #once done checking selects, determine:
            # if none were selected
            # if more than one were selected
            # or just one was selected
            if len(selrow) == 0:
                #warn that no rows were selected

                dialog=QtGui.QMessageBox(self)
                dialog.setText("No workspaces selected to save")
                dialog.exec_()  
            elif len(selrow) == 1:
                #when saving one file, user specifies filename and directory to save
                row=selrow[0]
                if row != -1:
                    wsname=str(table.item(row,config.WSM_WorkspaceCol).text())
                    
                if self.ui.rememberDataPath=='':
                    curdir=os.curdir
                else:
                    curdir=self.ui.rememberDataPath
                    
                filter=".nxs"
                wsnamext=wsname+filter
                filter="NXS (*.nxs);;All files (*.*)"
                wspathname = str(QtGui.QFileDialog.getSaveFileName(self, 'Save Workspace', curdir+'/'+wsnamext,filter))
                print "Workspace Save: ",wspathname
                
                if wspathname != '':
                    #now save workspace to nexus file
                    self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Saving Workspace: "+str(wsname))
                    stws=str(type(mtd.retrieve(wsname))) #get the type of workspace, convert to string
                    print "stws: ",stws
                    if (('MatrixWorkspace' in stws) or ('IEventWorkspace' in stws)):
                        #case for "standard" 2D workspace
                        SaveNexus(wsname,wspathname)
                    else:
                        #case for MD workspace
                        SaveMD(wsname,wspathname)
                    table.item(row,config.WSM_SavedCol).setText('Yes')
                    
                    
            elif len(selrow) > 1:
                #when saving more than one file, user selects directory and filenames are automatically generated.

                dialog=QtGui.QMessageBox(self)
                dialog.setText("Multiple files selected to save - user selects the directory to save the files and filenames will be automatically generated")
                dialog.exec_()
                             
                filter="NXS (*.nxs);;All files (*.*)"
#                wsnamext=wsname+filter
#                wspathname = str(QtGui.QFileDialog.getSaveFileName(self, 'Save Workspace', wsnamext,filter))
                home=getHomeDir()
                wspathname = str(QtGui.QFileDialog.getExistingDirectory(self,'Save Workspaces Directory',home))
                print "Workspace Save: ",wspathname
                
                #check if files already exist
                fcnt=0
                fstat=False
                for row in selrow:
                    wsname=str(str(table.item(row,config.WSM_WorkspaceCol).text()))
                    wspathname1 = wspathname + os.sep + wsname + '.nxs'
                    tmp=os.path.isfile(wspathname1)
                    if tmp:
                        fcnt += 1
                        fstat=True

                print " fstat: ",fstat                
                
                if fstat:
                    print "one or more files already exist - overwrite?"
                    reply = QtGui.QMessageBox.question(self, 'Warning', "One or more files already exist - overwrite all existing files?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
                    print "Button pressed: ",reply
                else:
                    reply = QtGui.QMessageBox.Yes
                    
                if reply == QtGui.QMessageBox.Yes:
                    #case to (over)write files
                    if wspathname != '':
                        #wspathname will be empty if the cancel button was selected on the path dialog.
                        cntr=1
                        for row in selrow:
                            wsname=str(str(table.item(row,config.WSM_WorkspaceCol).text()))
                            #since wspathname contains a directory, need to add filename and extension to it
                            wspathname1 = wspathname + os.sep + wsname + '.nxs'
                            print "save wsname: ",wsname
                            print "wspathname1: ",wspathname1
                            
                            percentbusy=int(float(cntr)/float(len(selrow))*100)
                            self.ui.progressBarStatusProgress.setValue(percentbusy) 
                            #now save workspace to nexus file
                            self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Saving Workspace: "+str(wsname))
                            stws=str(type(mtd.retrieve(wsname))) #get the type of workspace, convert to string
                            print "stws: ",stws
                            if (('MatrixWorkspace' in stws) or ('IEventWorkspace' in stws)):
                                #case for "standard" 2D workspace
                                SaveNexus(wsname,wspathname1)
                            else:
                                #case for MD workspace
                                SaveMD(wsname,wspathname1)
                            table.item(row,config.WSM_SavedCol).setText('Yes')
                            cntr += 1

                time.sleep(0.2)
                self.ui.progressBarStatusProgress.setValue(0) 

            else:
                print "this case not anticipated...doing nothing"
            

            
        elif self.ui.radioButtonRemoveSelected.isChecked(): 
            #remove selected workspaces from the application
            
            print "Remove Selected Selected"
            #first check if there are any rows to update selection
            item=table.item(0,config.WSM_WorkspaceCol) #need to convert item from Qstring to string for comparison to work
            itemStr=str(item)
            print "itemStr: ",itemStr
            #then only update the rows if rows with content are discovered.
            if itemStr != 'None':
                Nrows=table.rowCount()
                roff=0
                rcntr=0
                for row in range(Nrows):
                    item=table.item(row-roff,config.WSM_WorkspaceCol)
                    itemStr=str(item)
                    print "itemStr: ",itemStr
                    #then only update the rows if rows with content are discovered.
                    if itemStr != 'None':
                        #get checkbox status            
                        cw=table.cellWidget(row-roff,config.WSM_SelectCol) 
    #                    try:
                        cbstat=cw.isChecked()
                        print "row: ",row," roff: ",roff," rcntr: ",rcntr," cbstat: ",cbstat
                        if cbstat == True:
                            #case to remove a row
                            rcntr=row-roff
                            if rcntr < 0:
                                rcntr=0
                            print "   rcntr: ",rcntr
                            #remove workspace from memory before removing the row from the table
                            #get workspace name to be removed
                            print "Available workspaces: ",mtd.getObjectNames()
                            wsname=str(table.item(row-roff,config.WSM_WorkspaceCol).text())
                            print "wsname: ",wsname
                            self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Removing Workspace: "+str(wsname))
                            percentbusy=int(float(row+1)/float(Nrows))*100
                            self.ui.progressBarStatusProgress.setValue(percentbusy)
                            mtd.remove(wsname)
                            #now check to see which workspaces remain
                            print "Remaining workspaces: ",mtd.getObjectNames()
                            table.removeRow(rcntr)
                            roff += 1
    #                    except AttributeError:
    #                        #case where rows have been deleted and nothing do check or do
    #                        print "remove row attribute Error exception"
    #                        pass            
            
            
            self.ui.progressBarStatusProgress.setValue(0)
            pass 
        else:
            print "unsupported radiobutton option...doing nothing"
        self.ui.tableWidgetWorkspaces.setEnabled(True)
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Workspace Manager Update Complete")

    def performWorkspaceActions(self):
        print "performWorkspaceActions"
        #const=constants()
        self.ui.pushButtonPerformActions.setEnabled(False) 
        self.ui.tableWidgetWorkspaces.setEnabled(False)
        self.ui.pushButtonPowderCalcProj.setEnabled(False) 
        self.ui.pushButtonSCCalcProj.setEnabled(False) 
        self.ui.activeWSNames=[]
        table=self.ui.tableWidgetWorkspaces
        #first let's clean up empty rows
        Nrows=table.rowCount()
        roff=0
        for row in range(Nrows):
            item=table.item(row,config.WSM_WorkspaceCol) #need to convert item from Qstring to string for comparison to work
            itemStr=str(item)
            print "itemStr: ",itemStr
            if itemStr == 'None':
                table.removeRow(row-roff)
                roff=roff+1		
        #now let's process the empty row cleaned table
        Nrows=table.rowCount()
        roff=0
        NumActiveRows=0
        calcProjFlag=0
        roff=0
        for irow in range(Nrows):
            row=irow-roff
            percentbusy=100*(irow+1)/Nrows #determine % busy
            print "percentbusy: ",percentbusy
            self.ui.progressBarStatusProgress.setValue(percentbusy) #adjust progress bar according to % busy
            time.sleep(0.01)  #seem to need a small delay to ensure that status updates
            #determine if row has content to process
            item=table.item(row,config.WSM_WorkspaceCol) #need to convert item from Qstring to string for comparison to work
            itemStr=str(item)
            print "itemStr: ",itemStr
            if itemStr != 'None':
                itemText=str(table.item(row,config.WSM_WorkspaceCol).text())
                print "row: ",row
                rowComboboxIndex=table.cellWidget(row,config.WSM_ActionCol).currentIndex()
                print "rowAction: ",rowComboboxIndex
                if rowComboboxIndex == 0:
                    print "Load case"
                    NumActiveRows +=1 #increment active workspaces counter
                    #add names of active workspaces to the list - since list is cleared each time this function is called, need to add items each time
                    self.ui.activeWSNames.append(itemText)
                    print "itemText: ",itemText," self.ui.activeWSNames: ",self.ui.activeWSNames
                    #determine if data already loaded, if so, skip load
                    loadStat=str(table.item(row,config.WSM_StatusCol).text())
                    if loadStat != 'Loaded':
                        print "Case to load data"
                        #get filename
                        #open file and read data
                        #set status action to Loaded
                        #for now, just generate random number np arrays
                        Ndim=5000+irow
                        mockWSData=np.random.rand(Ndim,Ndim)
                        self.ui.activeWSVarsList.append(mockWSData)
                    status="Loaded"
                    table.setItem(row,config.WSM_StatusCol,QtGui.QTableWidgetItem(status)) #Status col=5
                    #if any data are loaded, set cal proj buttons active
                    calcProjFlag +=1

                elif rowComboboxIndex == 1:
                    print "Unload case"
                    loadStat=str(table.item(row,config.WSM_StatusCol).text())
                    if loadStat == 'Loaded':
                        #case to unload data
                        print "case to unload data"
                        self.ui.activeWSVarsList[row]=[] #replace whatever list item is there with an empty list - this deletes the data		
                    status="Not Loaded"
                    table.setItem(row,5,QtGui.QTableWidgetItem(status)) #Status col=5

                elif rowComboboxIndex == 2:
                    print "Remove case"
                    #remove this row
                    #first determine the current state of this workspace
                    wkspc=str(table.item(row,config.WSM_WorkspaceCol).text())
                    print "Removing Workspace: ",wkspc
                    loadStat=str(table.item(row,config.WSM_StatusCol).text())
                    if loadStat == 'Loaded':    
                        self.ui.activeWSVarsList[row]=[] #replace whatever list item is there with an empty list - this deletes the data	
#                        NumActiveRows -=1 #decrement active workspaces counter if the row to be deleted already has data
                        roff +=1
                    table.removeRow(row)
                    row=row-1
 #                   Nrows=Nrows-1
                elif rowComboboxIndex == 3:
                    print "No Action case"
                    #do nothing to status
                else:
                    print "Undefined case - should not get here..."
            else:
                print "Skipping case - no content discovered to process - row: ",row
                #remove this row
                table.removeRow(row-roff)
                roff=roff+1
            constantUpdateActor(self) #update memory/CPU status each time through the loop
            #cleanup the lists which may have had elements removed leaving null list placeholders
            #note that .remove() errors out if the element to delete is not present in the list - so put one in...
            self.ui.activeWSVarsList.append([]) #dummy null list to give our friend .remove() something to do...
            self.ui.activeWSVarsList.remove([])

        if calcProjFlag > 0:
            self.ui.pushButtonPowderCalcProj.setEnabled(True) 
            self.ui.pushButtonSCCalcProj.setEnabled(True) 
        else:
            self.ui.pushButtonPowderCalcProj.setEnabled(False) 
            self.ui.pushButtonSCCalcProj.setEnabled(False) 

        self.ui.progressBarStatusProgress.setValue(0) #clear progress bar
        self.ui.numActiveWorkspaces=NumActiveRows
        cnt=0
        for row in range(NumActiveRows):
            itemText=str(table.item(row,config.WSM_LastAlgCol).text())
            print "row: ",row,"  itemText: ",itemText
            if itemText == "DgsReduction":
                cnt +=1
        
        label='Available Workspaces: '+str(cnt)
        self.ui.labelSCWorkspaces.setText(label)
        self.ui.labelPowderWorkspaces.setText(label)
        self.ui.pushButtonPerformActions.setEnabled(True) 
        self.ui.tableWidgetWorkspaces.setEnabled(True)

    def WorkspaceManagerPageSelect(self):
        self.ui.stackedWidgetFilesWorkspaces.setCurrentIndex(1) #Show workspace manager stacked widget page

    def CreateWorkspacePageSelect(self):
        self.ui.stackedWidgetFilesWorkspaces.setCurrentIndex(0) #Show create workspace from files stacked widget page 

    def elapsedUpdate(self):
        #update the elapsed time since the application has been running.
        self.etimer.minutecntr = self.etimer.minutecntr + 1L #increment counter with timer timeout each 60 seconds
        thisCnt=self.etimer.minutecntr
#        print "Updating Elapsed Time - thisCnt: ",thisCnt
        hours=int(thisCnt/60)
        minutes=thisCnt % 60
        label="Elapsed Time: "+str(hours)+" H  "+str(minutes)+" M"
        self.ui.labelElapsedTime.setText(label)
        
    def constantUpdate(self): 
        #redirct to global function
        constantUpdateActor(self)


    def pushButtonSaveLogSelect(self):
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Save Log")			

    def pushButtonSCCutPlotSelect(self):
        print "SC Cut Plot Callback"
        SCCAIndex=self.ui.comboBoxSCCutAlong.currentIndex()
        SCCAFrom=self.ui.lineEditSCCutAlongFrom.text()
        SCCATo=self.ui.lineEditSCCutAlongTo.text()		
        SCCAStep=self.ui.lineEditSCCutAlongStep.text()
        SCCT1Index=self.ui.comboBoxSCCutThick1.currentIndex()
        SCCT1From=self.ui.lineEditSCCutThick1From.text()
        SCCT1To=self.ui.lineEditSCCutThick1To.text()
        SCCT1_2Index=self.ui.comboBoxSCCutThick1_2.currentIndex()
        SCCT1_2From=self.ui.lineEditSCCutThick1From_2.text()
        SCCT1_2To=self.ui.lineEditSCCutThick1To_2.text()
        SCCT2Index=self.ui.comboBoxSCCutThick2.currentIndex()
        SCCT2From=self.ui.lineEditSCCutThick2From.text()
        SCCT2To=self.ui.lineEditSCCutThick2To.text()
        SCCYIndex=self.ui.comboBoxSCCutY.currentIndex()
        SCCYFrom=self.ui.lineEditSCCutYFrom.text()
        SCCYTo=self.ui.lineEditSCCutYTo.text()
        print "SC Cut Plot Values: ",SCCAIndex,SCCAFrom,SCCATo,SCCAStep,SCCT1Index,SCCT1From,SCCT1To,SCCT1_2Index,SCCT1_2From,SCCT1_2To,SCCT2Index,SCCT2From,SCCT2To,SCCYIndex,SCCYFrom,SCCYTo
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Single Crystal Sample: Plot Cut")				

    def pushButtonSCCutOplotSelect(self):
        print "SC Cut Oplot Callback"
        SCCAIndex=self.ui.comboBoxSCCutAlong.currentIndex()
        SCCAFrom=self.ui.lineEditSCCutAlongFrom.text()
        SCCATo=self.ui.lineEditSCCutAlongTo.text()		
        SCCAStep=self.ui.lineEditSCCutAlongStep.text()
        SCCT1Index=self.ui.comboBoxSCCutThick1.currentIndex()
        SCCT1From=self.ui.lineEditSCCutThick1From.text()
        SCCT1To=self.ui.lineEditSCCutThick1To.text()
        SCCT2Index=self.ui.comboBoxSCCutThick2.currentIndex()
        SCCT2From=self.ui.lineEditSCCutThick2From.text()
        SCCT2To=self.ui.lineEditSCCutThick2To.text()
        SCCYIndex=self.ui.comboBoxSCCutY.currentIndex()
        SCCYFrom=self.ui.lineEditSCCutYFrom.text()
        SCCYTo=self.ui.lineEditSCCutYTo.text()
        print "SC Cut Oplot Values: ",SCCAIndex,SCCAFrom,SCCATo,SCCAStep,SCCT1Index,SCCT1From,SCCT1To,SCCT2Index,SCCT2From,SCCT2To,SCCYIndex,SCCYFrom,SCCYTo
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Single Crystal Sample: Oplot Cut")				


    def pushButtonPowderCutPlotSelect(self):
        #const=constants()
        print "Powder Cut Plot Callback"
        PCAIndex=self.ui.comboBoxPowderCutAlong.currentIndex()
        PCAFrom=self.ui.lineEditPowderCutAlongFrom.text()
        PCATo=self.ui.lineEditPowderCutAlongTo.text()		
        PCAStep=self.ui.lineEditPowderCutAlongStep.text()
        PCTIndex=self.ui.comboBoxPowderCutThick.currentIndex()
        PCTFrom=self.ui.lineEditPowderCutThickFrom.text()
        PCTTo=self.ui.lineEditPowderCutThickTo.text()
        PCYIndex=self.ui.comboBoxPowderCutY.currentIndex()
        PCYFrom=self.ui.lineEditPowderCutYFrom.text()
        PCYTo=self.ui.lineEditPowderCutYTo.text()
        print "Powder Cut Plot Values: ",PCAIndex,PCAFrom,PCATo,PCAStep,PCTIndex,PCTFrom,PCTTo,PCYIndex,PCYFrom,PCYTo
        #**** code to extract data and perform plot placed here
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Powder Sample: Plot Cut")		
        print "Calling MPLPC"
        #get list of selected workspaces from the workspace manager
        table=self.ui.tableWidgetWorkspaces
        Nrows=table.rowCount()
        EmptyRows=0
        wslist=[]
        for row in range(Nrows):
            try:
                #using try here to check if user forgot to load data then we'd have a table with empty rows...
                cw=table.cellWidget(row,config.WSM_SelectCol) 
                cbstat=cw.isChecked()
                #check if this workspace is selected for display
                if cbstat == True:
                    #case where it is selected
                    #get workspace
                    wsitem=str(table.item(row,config.WSM_WorkspaceCol).text())
                    print " wsitem:",wsitem
                    print " mtd.getObjectNames():",mtd.getObjectNames()
                    ws=mtd.retrieve(wsitem)      
                    wslist.append(wsitem)
            except:
                #case where a table row is empty - can't use this one
                EmptyRows += 1
                
        print "Number of empty rows: ",EmptyRows
#        self.ui.wslist=['Hello','World']  #for debugging use...
        self.ui.wslist=wslist
        
        self.MPLPC_win = MPLPowderCut(self)				
        self.MPLPC_win.show() 
        """
        if wslist != []:
            self.MPLPC_win = MPLPowderCut(self)				
            self.MPLPC_win.show()    
        else:
            self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - No workspaces selected for powder cut plots...returning")		
        """

    def pushButtonSCShowParamsSelect(self):
        #Utility function to transfer values from ViewSCDict into the 
        #corresponding view fields in the Slice GUI
        ViewSCDict=self.ui.ViewSCDict
        
        label=convertIndexToLabel(self,'X','Slice')    
        if ViewSCDict[label]['from'] != '':                
            SCSXFrom = str("%.3f" % ViewSCDict[label]['from'])
            self.ui.lineEditSCSliceXFrom.setText(SCSXFrom)

        label=convertIndexToLabel(self,'X','Slice')   
        if ViewSCDict[label]['to'] != '':      
            SCSXTo = str("%.3f" % ViewSCDict[label]['to'])
            self.ui.lineEditSCSliceXTo.setText(SCSXTo)
        
        label=convertIndexToLabel(self,'Y','Slice')    
        if ViewSCDict[label]['from'] != '':
            SCSYFrom = str("%.3f" % ViewSCDict[label]['from'])
            self.ui.lineEditSCSliceYFrom.setText(SCSYFrom)
        
        label=convertIndexToLabel(self,'Y','Slice')
        if ViewSCDict[label]['to'] != '':
            SCSYTo = str("%.3f" % ViewSCDict[label]['to'])
            self.ui.lineEditSCSliceYTo.setText(SCSYTo)
        
        label=convertIndexToLabel(self,'Z','Slice')     
        if ViewSCDict[label]['from'] != '':
            SCSZFrom = str("%.3f" % ViewSCDict[label]['from'])
            self.ui.lineEditSCSliceZFrom.setText(SCSZFrom)
        
        label=convertIndexToLabel(self,'Z','Slice')
        if ViewSCDict[label]['to'] != '':
            SCSZTo = str("%.3f" % ViewSCDict[label]['to'])  
            self.ui.lineEditSCSliceZTo.setText(SCSZTo)
        
        label=convertIndexToLabel(self,'E','Slice')                    
        if ViewSCDict[label]['from'] != '':
            SCSEFrom = str("%.3f" % ViewSCDict[label]['from'])    
            self.ui.lineEditSCSliceEFrom.setText(SCSEFrom)
        
        label=convertIndexToLabel(self,'E','Slice')  
        if ViewSCDict[label]['to'] != '':
            SCSETo = str("%.3f" % ViewSCDict[label]['to'])       
            self.ui.lineEditSCSliceETo.setText(SCSETo)

    def pushButtonSCVShowParamsSelect(self):
        #Utility function to transfer values from ViewSCVDict into the 
        #corresponding view fields in the Slice GUI
        ViewSCVDict=self.ui.ViewSCVDict
        
        label=convertIndexToLabel(self,'X','Volume')    
        if ViewSCVDict[label]['from'] != '':                
            SCSXFrom = str("%.3f" % ViewSCVDict[label]['from'])
            self.ui.lineEditSCVolXFrom.setText(SCSXFrom)

        label=convertIndexToLabel(self,'X','Volume')   
        if ViewSCVDict[label]['to'] != '':      
            SCSXTo = str("%.3f" % ViewSCVDict[label]['to'])
            self.ui.lineEditSCVolXTo.setText(SCSXTo)
        
        label=convertIndexToLabel(self,'Y','Volume')    
        if ViewSCVDict[label]['from'] != '':
            SCSYFrom = str("%.3f" % ViewSCVDict[label]['from'])
            self.ui.lineEditSCVolYFrom.setText(SCSYFrom)
        
        label=convertIndexToLabel(self,'Y','Volume')
        if ViewSCVDict[label]['to'] != '':
            SCSYTo = str("%.3f" % ViewSCVDict[label]['to'])
            self.ui.lineEditSCVolYTo.setText(SCSYTo)
        
        label=convertIndexToLabel(self,'Z','Volume')     
        if ViewSCVDict[label]['from'] != '':
            SCSZFrom = str("%.3f" % ViewSCVDict[label]['from'])
            self.ui.lineEditSCVolZFrom.setText(SCSZFrom)
        
        label=convertIndexToLabel(self,'Z','Volume')
        if ViewSCVDict[label]['to'] != '':
            SCSZTo = str("%.3f" % ViewSCVDict[label]['to'])  
            self.ui.lineEditSCVolZTo.setText(SCSZTo)
        
        label=convertIndexToLabel(self,'E','Volume')                    
        if ViewSCVDict[label]['from'] != '':
            SCSEFrom = str("%.3f" % ViewSCVDict[label]['from'])    
            self.ui.lineEditSCVolEFrom.setText(SCSEFrom)
        
        label=convertIndexToLabel(self,'E','Volume')  
        if ViewSCVDict[label]['to'] != '':
            SCSETo = str("%.3f" % ViewSCVDict[label]['to'])       
            self.ui.lineEditSCVolETo.setText(SCSETo)


    def pushButtonSCVolSlicesSelect(self):
        #method to call the sliceviewer to visualize the data volume
        
        print "Single Crystal Surface Slice Button pressed"
        #now extract values from this tab
        SCSXcomboIndex=self.ui.comboBoxSCVolX.currentIndex()
        SCSXFrom=self.ui.lineEditSCVolXFrom.text()
        SCSXTo=self.ui.lineEditSCVolXTo.text()
        SCSXStep=self.ui.lineEditSCVolXStep.text()
        SCSYcomboIndex=self.ui.comboBoxSCVolY.currentIndex()
        SCSYFrom=self.ui.lineEditSCVolYFrom.text()
        SCSYTo=self.ui.lineEditSCVolYTo.text()
        SCSYStep=self.ui.lineEditSCVolYStep.text()
        SCSZcomboIndex=self.ui.comboBoxSCVolZ.currentIndex()
        SCSZFrom=self.ui.lineEditSCVolZFrom.text()
        SCSZTo=self.ui.lineEditSCVolZTo.text()
        SCSZStep=self.ui.lineEditSCVolZStep.text()
        SCSEcomboIndex=self.ui.comboBoxSCVolE.currentIndex()
        SCSEFrom=self.ui.lineEditSCVolEFrom.text()
        SCSETo=self.ui.lineEditSCVolETo.text()
        SCSIntensityFrom=self.ui.lineEditSCVolIntensityFrom.text()
        SCSIntensityTo=self.ui.lineEditSCVolIntensityTo.text()
        SCSSmoothing=self.ui.lineEditSCVolSmoothing.text()
        SCSEcomboIndex=self.ui.comboBoxSCVolE.currentIndex()
        SCSThickFrom=self.ui.lineEditSCVolEFrom.text()
        SCSThickTo=self.ui.lineEditSCVolETo.text()

        #**** code to extract data and perform plot placed here
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Single Crystal Sample: Surface Slice")				

        #determine which workspaces have been selected
        table=self.ui.tableWidgetWorkspaces
        #first let's clean up empty rows
        Nrows=table.rowCount()
        Nws=0
        for row in range(Nrows):
            cw=table.cellWidget(row,config.WSM_SelectCol) 
            cbstat=cw.isChecked()
            #check if this workspace is selected for display
            if cbstat == True:
                #case where it is selected
                Nws+=1 #increment selected workspace counter
                #get workspace
                wsitem=str(table.item(row,config.WSM_WorkspaceCol).text())
                print " wsitem:",wsitem
                print " mtd.getObjectNames():",mtd.getObjectNames()
                __ws=mtd.retrieve(wsitem)
                
                #need to determine if this is a single or group workspace to obtain min/max values
                #get min & max range values for the MD workspace
                wsType=__ws.id()
                if wsType == 'WorkspaceGroup':
                    minn=[__ws[0].getXDimension().getMinimum(),__ws[0].getYDimension().getMinimum(),__ws[0].getZDimension().getMinimum(),__ws[0].getTDimension().getMinimum()]
                    maxx=[__ws[0].getXDimension().getMaximum(),__ws[0].getYDimension().getMaximum(),__ws[0].getZDimension().getMaximum(),__ws[0].getTDimension().getMaximum()]
                    NEntries=__ws.getNumberOfEntries()
                else:
                    # single workspace case
                    minn=[__ws.getXDimension().getMinimum(),__ws.getYDimension().getMinimum(),__ws.getZDimension().getMinimum(),__ws.getTDimension().getMinimum()]
                    maxx=[__ws.getXDimension().getMaximum(),__ws.getYDimension().getMaximum(),__ws.getZDimension().getMaximum(),__ws.getTDimension().getMaximum()]
                    NEntries=1
                    
                #get values from GUI and ViewSCDict
                ViewSCDict=self.ui.ViewSCDict
                print "ViewSCDict: ",ViewSCDict
                if SCSXFrom =='':
                    #SCSXFrom=minn[0]
                    label=convertIndexToLabel(self,'X','Volume')   
                    print "  label: ",label                 
                    SCSXFrom = float(ViewSCDict[label]['from'])
                else:
                    SCSXFrom=float(SCSXFrom)
                if SCSXTo =='':
                    #SCSXTo=maxx[0]
                    label=convertIndexToLabel(self,'X','Volume')                    
                    SCSXTo = float(ViewSCDict[label]['to'])
                else:
                    SCSXTo=float(SCSXTo)
                Nscx=int(round((SCSXTo-SCSXFrom)/float(SCSXStep)))
                
                if SCSYFrom =='':
                    #SCSYFrom=minn[1]
                    label=convertIndexToLabel(self,'Y','Volume')                    
                    SCSYFrom = float(ViewSCDict[label]['from'])
                else:
                    SCSYFrom=float(SCSYFrom)
                if SCSYTo =='':
                    #SCSYTo=maxx[1]
                    label=convertIndexToLabel(self,'Y','Volume')                    
                    SCSYTo = float(ViewSCDict[label]['to'])
                else:
                    SCSYTo=float(SCSYTo)
                Nscy=int(round((SCSYTo-SCSYFrom)/float(SCSYStep)))                    
                    
                if SCSZFrom =='':
                    #SCSZFrom=minn[2]
                    label=convertIndexToLabel(self,'Z','Volume')                    
                    SCSZFrom = float(ViewSCDict[label]['from'])
                else:
                    SCSZFrom=float(SCSZFrom)
                if SCSZTo =='':
                    #SCSZTo=maxx[2]
                    label=convertIndexToLabel(self,'Z','Volume')                    
                    SCSZTo = float(ViewSCDict[label]['to'])
                else:
                    SCSZTo=float(SCSZTo)   
                Nscz=int(round((SCSZTo-SCSZFrom)/float(SCSZStep)))  
                    
                if SCSEFrom =='':
                    #SCSEFrom=minn[3]
                    label=convertIndexToLabel(self,'E','Volume')                    
                    SCSEFrom = float(ViewSCDict[label]['from'])
                else:
                    SCSEFrom=float(SCSEFrom)
                if SCSETo =='':
                    #SCSETo=maxx[3]
                    label=convertIndexToLabel(self,'E','Volume')                    
                    SCSETo = float(ViewSCDict[label]['to'])
                else:
                    SCSETo=float(SCSETo)
                    
                #Derive names from Viewing Axes u and label fields
                #nameLst=makeSCNames(self)
                #Extract names from Slice View combo boxes
                nameLst=[]
                nameLst.append(self.ui.comboBoxSCSliceX.currentText())
                nameLst.append(self.ui.comboBoxSCSliceY.currentText())
                nameLst.append(self.ui.comboBoxSCSliceZ.currentText())
                nameLst.append(self.ui.comboBoxSCSliceE.currentText())
                #note that the comboBox label and that label needed by MDNormDirectSC are different - search for the case and replace with what's needed
                nameLst=['DeltaE' if x=='E (meV)' else x for x in nameLst]
                                                                    
                #Format: 'name,minimum,maximum,number_of_bins'
                print "Nscx: ",Nscx,"  Nscy: ",Nscy
                AD0=str(nameLst[0])+','+str(SCSXFrom)+','+str(SCSXTo)+','+str(Nscx)
                AD0=AD0.replace(config.XYZUnits,'')
                AD1=str(nameLst[1])+','+str(SCSYFrom)+','+str(SCSYTo)+','+str(Nscy)
                AD1=AD1.replace(config.XYZUnits,'')
                AD2=str(nameLst[2])+','+str(SCSZFrom)+','+str(SCSZTo)+','+str(Nscz)
                AD2=AD2.replace(config.XYZUnits,'')
                AD3=str(nameLst[3])+','+str(SCSEFrom)+','+str(SCSETo)+','+str(1)
                AD3=AD3.replace(config.XYZUnits,'')
                
                print "AD0: ",AD0,'  type: ',type(AD0)
                print "AD1: ",AD1,'  type: ',type(AD1)
                print "AD2: ",AD2,'  type: ',type(AD2)
                print "AD3: ",AD3,'  type: ',type(AD3)
                print "type(__ws): ",type(__ws)
                print "__ws: ",__ws.name
                histoData,histoNorm=MDNormDirectSC(__ws,AlignedDim0=AD0,AlignedDim1=AD1,AlignedDim2=AD2,AlignedDim3=AD3)
                print "histoNorm Complete"
                if wsType == 'WorkspaceGroup':
                    print "histoData.getNumberOfEntries(): ",histoData.getNumberOfEntries()
                    print "histoNorm.getNumberOfEntries(): ",histoNorm.getNumberOfEntries()
                    #Loop thru each workspace in a group and calculate the data and norm for the requested parameters
                    for k in range(NEntries):
                        print "Sum Loop: ",k," of ",NEntries
                        
                        if k == 0:
                            histoDataSum=histoData[k]
                            histoNormSum=histoNorm[k]
                        else:
                            histoDataSum+=histoData[k]
                            histoNormSum+=histoNorm[k]
                else:
                    # case for a single workspace - just pass thru to sum workspaces
                    histoDataSum=histoData
                    histoNormSum=histoNorm
                    
                #upon summing coresponding data and norm data, produce eht normalized result
                print "histoDataSum.id(): ",histoDataSum.id()
                print "histoNormSum.id(): ",histoNormSum.id()
                normalized=histoDataSum/histoNormSum   
                
                #let's check for values we don't want in the normalized data...
                # isinf : Shows which elements are positive or negative infinity
                # isposinf : Shows which elements are positive infinity
                # isneginf : Shows which elements are negative infinity
                # isnan : Shows which elements are Not a Number        
                
                #normalizedNew=normalized
                normArray=normalized.getSignalArray()
                normArray.flags.writeable=True  #note that initially the array is not writeable, so change this
                indx=np.isinf(normArray)
                normArray[indx]=0    
                indx=np.isnan(normArray)
                normArray[indx]=0     
                normArray.flags.writeable=False #now put it back to nonwriteable
                normalized.setSignalArray(normArray)
                
                
                #Envoke SliceViewer here
                sv = SliceViewer()
                label='MSlice SC VolumeViewer'                
                sv.LoadData('normalized',label)
                xydim=None
                slicepoint=None
                colormin=None
                colormax=None
                colorscalelog=False
                limits=None
                normalization=0
                sv.SetParams(xydim,slicepoint,colormin,colormax,colorscalelog,limits, normalization)
                sv.Show()
                
                
                
                #determine workspace type
                #stubbing this part out for now...
        if Nws < 1:
            #check if we have any workspaces to work with - return if not
            print "No workspaces selected - returning"
            dialog=QtGui.QMessageBox(self)
            dialog.setText("No workspaces selected - returning")
            dialog.exec_()
            return        
        
        
        
        
        pass
        
    def calcXNpts(self):
        print "calcXNpts"
        pass
        
    def calcYNpts(self):
        print "calcYNpts"
        pass

    def pushButtonSCSSurfaceSelect(self):
        print "Single Crystal Surface Slice Button pressed"
        #now extract values from this tab
        SCSXcomboIndex=self.ui.comboBoxSCSliceX.currentIndex()
        SCSXFrom=self.ui.lineEditSCSliceXFrom.text()
        SCSXTo=self.ui.lineEditSCSliceXTo.text()
        SCSXStep=self.ui.lineEditSCSliceXStep.text()
        SCSYcomboIndex=self.ui.comboBoxSCSliceY.currentIndex()
        SCSYFrom=self.ui.lineEditSCSliceYFrom.text()
        SCSYTo=self.ui.lineEditSCSliceYTo.text()
        SCSYStep=self.ui.lineEditSCSliceYStep.text()
        SCSZcomboIndex=self.ui.comboBoxSCSliceZ.currentIndex()
        SCSZFrom=self.ui.lineEditSCSliceZFrom.text()
        SCSZTo=self.ui.lineEditSCSliceZTo.text()
        SCSEcomboIndex=self.ui.comboBoxSCSliceE.currentIndex()
        SCSEFrom=self.ui.lineEditSCSliceEFrom.text()
        SCSETo=self.ui.lineEditSCSliceETo.text()
        SCSIntensityFrom=self.ui.lineEditSCSliceIntensityFrom.text()
        SCSIntensityTo=self.ui.lineEditSCSliceIntensityTo.text()
        SCSSmoothing=self.ui.lineEditSCSliceSmoothing.text()
        SCSEcomboIndex=self.ui.comboBoxSCSliceE.currentIndex()
        SCSThickFrom=self.ui.lineEditSCSliceEFrom.text()
        SCSThickTo=self.ui.lineEditSCSliceETo.text()
        print "SC Surface values: ",SCSXcomboIndex,SCSXFrom,SCSXTo,SCSXStep,SCSYcomboIndex,SCSYFrom,SCSYTo,SCSYStep,SCSEcomboIndex,SCSEFrom,SCSETo,SCSIntensityFrom,SCSIntensityTo,SCSSmoothing
        print "  More SC Surface values: ",SCSEcomboIndex,SCSThickFrom,SCSThickTo
        #**** code to extract data and perform plot placed here
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Single Crystal Sample: Surface Slice")				

        #determine which workspaces have been selected
        table=self.ui.tableWidgetWorkspaces
        #first let's clean up empty rows
        Nrows=table.rowCount()
        Nws=0
        for row in range(Nrows):
            cw=table.cellWidget(row,config.WSM_SelectCol) 
            cbstat=cw.isChecked()
            #check if this workspace is selected for display
            if cbstat == True:
                #case where it is selected
                Nws+=1 #increment selected workspace counter
                #get workspace
                wsitem=str(table.item(row,config.WSM_WorkspaceCol).text())
                print " wsitem:",wsitem
                print " mtd.getObjectNames():",mtd.getObjectNames()
                __ws=mtd.retrieve(wsitem)
                
                #need to determine if this is a single or group workspace to obtain min/max values
                #get min & max range values for the MD workspace
                wsType=__ws.id()
                if wsType == 'WorkspaceGroup':
                    minn=[__ws[0].getXDimension().getMinimum(),__ws[0].getYDimension().getMinimum(),__ws[0].getZDimension().getMinimum(),__ws[0].getTDimension().getMinimum()]
                    maxx=[__ws[0].getXDimension().getMaximum(),__ws[0].getYDimension().getMaximum(),__ws[0].getZDimension().getMaximum(),__ws[0].getTDimension().getMaximum()]
                    NEntries=__ws.getNumberOfEntries()
                else:
                    # single workspace case
                    minn=[__ws.getXDimension().getMinimum(),__ws.getYDimension().getMinimum(),__ws.getZDimension().getMinimum(),__ws.getTDimension().getMinimum()]
                    maxx=[__ws.getXDimension().getMaximum(),__ws.getYDimension().getMaximum(),__ws.getZDimension().getMaximum(),__ws.getTDimension().getMaximum()]
                    NEntries=1
                    
                #get values from GUI and ViewSCDict
                ViewSCDict=self.ui.ViewSCDict
                print "ViewSCDict: ",ViewSCDict
                if SCSXFrom =='':
                    #SCSXFrom=minn[0]
                    label=convertIndexToLabel(self,'X','Slice')   
                    print "  label: ",label                 
                    SCSXFrom = float(ViewSCDict[label]['from'])
                else:
                    SCSXFrom=float(SCSXFrom)
                if SCSXTo =='':
                    #SCSXTo=maxx[0]
                    label=convertIndexToLabel(self,'X','Slice')                    
                    SCSXTo = float(ViewSCDict[label]['to'])
                else:
                    SCSXTo=float(SCSXTo)
                Nscx=int(round((SCSXTo-SCSXFrom)/float(SCSXStep)))
                
                if SCSYFrom =='':
                    #SCSYFrom=minn[1]
                    label=convertIndexToLabel(self,'Y','Slice')                    
                    SCSYFrom = float(ViewSCDict[label]['from'])
                else:
                    SCSYFrom=float(SCSYFrom)
                if SCSYTo =='':
                    #SCSYTo=maxx[1]
                    label=convertIndexToLabel(self,'Y','Slice')                    
                    SCSYTo = float(ViewSCDict[label]['to'])
                else:
                    SCSYTo=float(SCSYTo)
                Nscy=int(round((SCSYTo-SCSYFrom)/float(SCSYStep)))                    
                    
                if SCSZFrom =='':
                    #SCSZFrom=minn[2]
                    label=convertIndexToLabel(self,'Z','Slice')                    
                    SCSZFrom = float(ViewSCDict[label]['from'])
                else:
                    SCSZFrom=float(SCSZFrom)
                if SCSZTo =='':
                    #SCSZTo=maxx[2]
                    label=convertIndexToLabel(self,'Z','Slice')                    
                    SCSZTo = float(ViewSCDict[label]['to'])
                else:
                    SCSZTo=float(SCSZTo)                    
                    
                if SCSEFrom =='':
                    #SCSEFrom=minn[3]
                    label=convertIndexToLabel(self,'E','Slice')                    
                    SCSEFrom = float(ViewSCDict[label]['from'])
                else:
                    SCSEFrom=float(SCSEFrom)
                if SCSETo =='':
                    #SCSETo=maxx[3]
                    label=convertIndexToLabel(self,'E','Slice')                    
                    SCSETo = float(ViewSCDict[label]['to'])
                else:
                    SCSETo=float(SCSETo)
                    
                #Derive names from Viewing Axes u and label fields
                #nameLst=makeSCNames(self)
                #Extract names from Slice View combo boxes
                nameLst=[]
                nameLst.append(self.ui.comboBoxSCSliceX.currentText())
                nameLst.append(self.ui.comboBoxSCSliceY.currentText())
                nameLst.append(self.ui.comboBoxSCSliceZ.currentText())
                nameLst.append(self.ui.comboBoxSCSliceE.currentText())
                #note that the comboBox label and that label needed by MDNormDirectSC are different - search for the case and replace with what's needed
                nameLst=['DeltaE' if x=='E (meV)' else x for x in nameLst]
                                                                    
                #Format: 'name,minimum,maximum,number_of_bins'
                print "Nscx: ",Nscx,"  Nscy: ",Nscy
                AD0=str(nameLst[0])+','+str(SCSXFrom)+','+str(SCSXTo)+','+str(Nscx)
                AD0=AD0.replace(config.XYZUnits,'')
                AD1=str(nameLst[1])+','+str(SCSYFrom)+','+str(SCSYTo)+','+str(Nscy)
                AD1=AD1.replace(config.XYZUnits,'')
                AD2=str(nameLst[2])+','+str(SCSZFrom)+','+str(SCSZTo)+','+str(1)
                AD2=AD2.replace(config.XYZUnits,'')
                AD3=str(nameLst[3])+','+str(SCSEFrom)+','+str(SCSETo)+','+str(10)
                AD3=AD3.replace(config.XYZUnits,'')
                
                print "AD0: ",AD0,'  type: ',type(AD0)
                print "AD1: ",AD1,'  type: ',type(AD1)
                print "AD2: ",AD2,'  type: ',type(AD2)
                print "AD3: ",AD3,'  type: ',type(AD3)
                print "type(__ws): ",type(__ws)
                print "__ws: ",__ws.name
                histoData,histoNorm=MDNormDirectSC(__ws,AlignedDim0=AD0,AlignedDim1=AD1,AlignedDim2=AD2,AlignedDim3=AD3)
                print "histoNorm Complete"
                if wsType == 'WorkspaceGroup':
                    print "histoData.getNumberOfEntries(): ",histoData.getNumberOfEntries()
                    print "histoNorm.getNumberOfEntries(): ",histoNorm.getNumberOfEntries()
                    #Loop thru each workspace in a group and calculate the data and norm for the requested parameters
                    for k in range(NEntries):
                        print "Sum Loop: ",k," of ",NEntries
                        
                        if k == 0:
                            histoDataSum=histoData[k]
                            histoNormSum=histoNorm[k]
                        else:
                            histoDataSum+=histoData[k]
                            histoNormSum+=histoNorm[k]
                else:
                    # case for a single workspace - just pass thru to sum workspaces
                    histoDataSum=histoData
                    histoNormSum=histoNorm
                    
                #upon summing coresponding data and norm data, produce eht normalized result
                print "histoDataSum.id(): ",histoDataSum.id()
                print "histoNormSum.id(): ",histoNormSum.id()
                normalized=histoDataSum/histoNormSum   
                
                #let's check for values we don't want in the normalized data...
                # isinf : Shows which elements are positive or negative infinity
                # isposinf : Shows which elements are positive infinity
                # isneginf : Shows which elements are negative infinity
                # isnan : Shows which elements are Not a Number        
                
                #normalizedNew=normalized
                normArray=normalized.getSignalArray()
                normArray.flags.writeable=True  #note that initially the array is not writeable, so change this
                indx=np.isinf(normArray)
                normArray[indx]=0    
                indx=np.isnan(normArray)
                normArray[indx]=0     
                normArray.flags.writeable=False #now put it back to nonwriteable
                normalized.setSignalArray(normArray)
                
                
                #Envoke SliceViewer here
                sv = SliceViewer()
                label='MSlice SC SliceViewer'                
                sv.LoadData('normalized',label)
                xydim=None
                slicepoint=None
                colormin=None
                colormax=None
                colorscalelog=False
                limits=None
                normalization=0
                sv.SetParams(xydim,slicepoint,colormin,colormax,colorscalelog,limits, normalization)
                sv.Show()
                
                
                
                #determine workspace type
                #stubbing this part out for now...
        if Nws < 1:
            #check if we have any workspaces to work with - return if not
            print "No workspaces selected - returning"
            dialog=QtGui.QMessageBox(self)
            dialog.setText("No workspaces selected - returning")
            dialog.exec_()
            return

            
            


    def pushButtonPowderSlicePlotSliceSelect(self):
        print "Powder Plot Slice Button pressed"
        #now extract values from this tab
        PSXcomboIndex=self.ui.comboBoxPowderSliceX.currentIndex()
        PSXFrom=self.ui.lineEditPowderSliceXFrom.text()
        PSXTo=self.ui.lineEditPowderSliceXTo.text()
        PSXStep=self.ui.lineEditPowderSliceXStep.text()
        PSYcomboIndex=self.ui.comboBoxPowderSliceY.currentIndex()
        PSYFrom=self.ui.lineEditPowderSliceYFrom.text()
        PSYTo=self.ui.lineEditPowderSliceYTo.text()
        PSYStep=self.ui.lineEditPowderSliceYStep.text()
        PSIntensityFrom=self.ui.lineEditPowderSliceIntensityFrom.text()
        PSIntensityTo=self.ui.lineEditPowderSliceIntensityTo.text()
        PSSmoothing=self.ui.lineEditPowderSliceSmoothing.text()
        print "Powder Plot values: ",PSXcomboIndex,PSXFrom,PSXTo,PSXStep,PSYcomboIndex,PSYFrom,PSYTo,PSYStep,PSIntensityFrom,PSIntensityTo,PSSmoothing
        #**** code to extract data and perform plot placed here
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Powder Sample: Show Slice")		

    def pushButtonPowderSliceOplotSliceSelect(self):
        print "Powder Oplot Slice Button pressed"
        #now extract values from this tab
        PSXcomboIndex=self.ui.comboBoxPowderSliceX.currentIndex()
        PSXFrom=self.ui.lineEditPowderSliceXFrom.text()
        PSXTo=self.ui.lineEditPowderSliceXTo.text()
        PSXStep=self.ui.lineEditPowderSliceXStep.text()
        PSYcomboIndex=self.ui.comboBoxPowderSliceY.currentIndex()
        PSYFrom=self.ui.lineEditPowderSliceYFrom.text()
        PSYTo=self.ui.lineEditPowderSliceYTo.text()
        PSYStep=self.ui.lineEditPowderSliceYStep.text()
        PSIntensityFrom=self.ui.lineEditPowderSliceIntensityFrom.text()
        PSIntensityTo=self.ui.lineEditPowderSliceIntensityTo.text()
        PSSmoothing=self.ui.lineEditPowderSliceSmoothing.text()
        print "Powder Oplot values: ",PSXcomboIndex,PSXFrom,PSXTo,PSXStep,PSYcomboIndex,PSYFrom,PSYTo,PSYStep,PSIntensityFrom,PSIntensityTo,PSSmoothing
        #**** code to extract data and perform plot placed here
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Powder Sample: Oplot Slice")				

    def pushButtonPowderSliceSurfaceSliceSelect(self):
        print "Powder Surface Slice Button pressed"
        #now extract values from this tab
        PSXcomboIndex=self.ui.comboBoxPowderSliceX.currentIndex()
        PSXFrom=self.ui.lineEditPowderSliceXFrom.text()
        PSXTo=self.ui.lineEditPowderSliceXTo.text()
        PSXStep=self.ui.lineEditPowderSliceXStep.text()
        PSYcomboIndex=self.ui.comboBoxPowderSliceY.currentIndex()
        PSYFrom=self.ui.lineEditPowderSliceYFrom.text()
        PSYTo=self.ui.lineEditPowderSliceYTo.text()
        PSYStep=self.ui.lineEditPowderSliceYStep.text()
        PSIntensityFrom=self.ui.lineEditPowderSliceIntensityFrom.text()
        PSIntensityTo=self.ui.lineEditPowderSliceIntensityTo.text()
        PSSmoothing=self.ui.lineEditPowderSliceSmoothing.text()
        print "Powder Surface values: ",PSXcomboIndex,PSXFrom,PSXTo,PSXStep,PSYcomboIndex,PSYFrom,PSYTo,PSYStep,PSIntensityFrom,PSIntensityTo,PSSmoothing
        #**** code to extract data and perform plot placed here
        
        #get constants
        #const=constants()
        
        table=self.ui.tableWidgetWorkspaces
        #first let's clean up empty rows
        Nrows=table.rowCount()
        for row in range(Nrows):
            cw=table.cellWidget(row,config.WSM_SelectCol) 
            cbstat=cw.isChecked()
            #check if this workspace is selected for display
            if cbstat == True:
                #case where it is selected
                #get workspace
                wsitem=str(table.item(row,config.WSM_WorkspaceCol).text())
                print " wsitem:",wsitem
                print " mtd.getObjectNames():",mtd.getObjectNames()
                __ws=mtd.retrieve(wsitem)
    
                wsX=__ws.getXDimension()
                wsY=__ws.getYDimension()
                
                xmin=wsX.getMinimum()
                xmax=wsX.getMaximum()
                
                ymin=wsY.getMinimum()
                ymax=wsY.getMaximum()
                
                xname= wsX.getName()
                yname= wsY.getName()
                
                ad0=xname+','+str(xmin)+','+str(xmax)+',100'
                ad1=yname+','+str(ymin)+','+str(ymax)+',100'
                print "ad0: ",ad0
                print "ad1: ",ad1
                BinMD(InputWorkspace=__ws,AlignedDim0=ad0,AlignedDim1=ad1,OutputWorkspace="__MDH")
                __MDH=mtd.retrieve('__MDH')
                sig=__MDH.getSignalArray()
                ne=__MDH.getNumEventsArray()
                dne=sig/ne
 #               dne=sig  #use to just look at the signal array
                
                
                #Incorporate SliceViewer here
                sv = SliceViewer()
                label='Python Only SliceViewer'
                #hard coded workspace for demo purpose - needs to be changed to dynamically pick up workspace
#                LoadMD(filename=r'C:\Users\mid\Documents\Mantid\Powder\CalcProj\zrh_1000_PCalcProj.nxs',OutputWorkspace='ws')
#                sv.LoadData('ws',label)
                
#                exec ("%s = mtd.retrieve(%r)" % (outname,outname))
                #FIXME - retrospectively observing that Sliceview just uses the selected workspace and not the calculated results 
                #FIXME cont: This may not be a problem here as the desired result is usually calculated when using SliceViewer
                sv.LoadData(wsitem,label)
                xydim=None
                slicepoint=None
                colormin=None
                colormax=None
                colorscalelog=False
                limits=None
                normalization=0
                sv.SetParams(xydim,slicepoint,colormin,colormax,colorscalelog,limits, normalization)
                sv.Show()
                
#                figure(1)
#                imshow(flipud(sig))
                """
                figure(row)

#                imshow(flipud(dne.T))
                imshow(flipud(dne),cmap=get_cmap('spectral'))
                                                
                XD,YD=shape(sig)
                
                Ndx=5                  #label span per tick
                xrng=round(xmax-xmin)  #label range
                xbins=(xrng/Ndx)  #number of label ticks 
                
                dx=XD/xbins            #data x dimension divided by number of label ticks gives data bins per label tick
                print "dx: ",dx
                
                Ndy=100
                yrng=round(ymax-ymin)
                ybins=(yrng/Ndy)
                
                dy=YD/ybins
                
                #need to add one to include end point on plot
                xbins=xbins+1
                ybins=ybins+1
                
                xtick_locs=[j for j in arange(xbins)*dx]
                xtick_lbls=[int(j+xmin) for j in arange(xbins)*Ndx] 
#                xtick_lbls.reverse()
                
                ytick_locs=[j-5 for j in arange(ybins)*dy] 
                ytick_lbls=[int(j+ymin) for j in arange(ybins)*Ndy] 
                ytick_lbls.reverse()
                
#                xticks(ytick_locs,ytick_lbls)
#                yticks(xtick_locs,xtick_lbls)
                
#                suptitle('Powder Slice View',fontsize=20)
#                xlabel(wsY.getName(),fontsize=18)
#                ylabel(wsX.getName(),fontsize=18)
                
                yticks(ytick_locs,ytick_lbls)
                xticks(xtick_locs,xtick_lbls)
                
                suptitle('Powder Slice View',fontsize=20)
                ylabel(wsY.getName(),fontsize=18)
                xlabel(wsX.getName(),fontsize=18)
                """
                

#        show()
        
        
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Powder Sample: Surface Slice")				


    def SampleTabWidgetSelect(self):
        print "SampleTabWidget"
        SampleTabIndex=self.ui.SampleTabWidget.currentIndex()
        print "Selected Tab Index: ",SampleTabIndex
        #depending upon which sample is selected, need to select the corresponding slice, cut, and volume tabs
        ViewTabIndex=self.ui.ViewTabWidget.currentIndex()
        #get view tab stacked widget indicies
        ViewTabSliceIndex=self.ui.stackedWidgetSlice.currentIndex()
        print "ViewTabIndex: ",ViewTabIndex," ViewTabSliceIndex: ",ViewTabSliceIndex
        if SampleTabIndex == 0:
            #case where powder sample tab is selected
            self.ui.stackedWidgetSlice.setCurrentIndex(0)
            self.ui.stackedWidgetCut.setCurrentIndex(0)
            self.ui.stackedWidgetVolume.setCurrentIndex(0)			
        else:
            #case where single crystal sample tab is selected
            self.ui.stackedWidgetSlice.setCurrentIndex(1)
            self.ui.stackedWidgetCut.setCurrentIndex(1)
            self.ui.stackedWidgetVolume.setCurrentIndex(1)						

    def deleteAll(self):
        #make sure that workspace name lineEdit is enabled
        self.ui.lineEditWorkspaceName.setEnabled(True)
        Nrows=self.ui.tableWidget.rowCount()
        for delrow in range(Nrows):
            self.ui.tableWidget.removeRow(0)
        self.ui.pushButtonCreateWorkspace.setEnabled(False)
        Nrows=self.ui.tableWidget.rowCount()
        nfilesStr="Number of Files: "+str(Nrows)
        self.ui.LabelNfiles.setText(nfilesStr)
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Deleted All Files")		

    def deleteSelected(self):
        #make sure that workspace name lineEdit is enabled
        self.ui.lineEditWorkspaceName.setEnabled(True)
        #determine number of rows in original list
        Nrows=self.ui.tableWidget.rowCount()
        #selectedIndexes() returns an unsorted list of selected rows
        #but it also returns the selected columns too
        #thus if there are 6 columns, there will be 6 instances of the row, one each for each column
        #also note that if a higher row number is selected first that it will appear first in the list
        #thus a list with duplicates removed and sorted is needed
        indicies = self.ui.tableWidget.selectedIndexes()
        print "indicies: ",indicies
        delrows=[]
        for index in indicies:
            row = index.row()
            print "row: ",row
            delrows.append(row)
        print "delrows: ",delrows
        delrows.sort() #sort ascending to remove selection order
        delrows=list(set(delrows)) #use the set operator to give unique items, but need to convert it back to a list
        print "delrows: ",delrows
        i=0 #incremental counter for the number of rows deleted
        #each time through the loop, a row is removed starting from
        #from small row number to large.  Thus delrows values become
        #outdated by each row removeal - don't see a way to remove
        #multiple rows all at once thus have to adjust the delrow
        #index each time through the loop
        for delrow in delrows:
            print "delrow: ",delrow
            self.ui.tableWidget.removeRow(delrow-i)
            i+=1
        #depending upon the number of rows deleted, need to determine the
        #state of the Load button
        NrowsAfter=self.ui.tableWidget.rowCount()
        print "number of rows: ",Nrows
        print "number of rows after:",NrowsAfter
        if NrowsAfter != Nrows:
            if NrowsAfter == 0:
                #case where there are no files left in the list - disable Load button
                self.ui.pushButtonCreateWorkspace.setEnabled(False)
            if NrowsAfter > 0:
                #case where we still have a data set and it needs to be loaded
                self.ui.pushButtonCreateWorkspace.setEnabled(True)
        Nrows=self.ui.tableWidget.rowCount()
        nfilesStr="Number of Files: "+str(Nrows)
        self.ui.LabelNfiles.setText(nfilesStr)
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Deleted Selected Files")		

    def confirmExit(self):
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
        #close application
            self.close()
        else:
        #do nothing and return
            pass               

    def CreateWorkspace(self):
        #function creates the workspace from files and requires the user to save the workspace to disk
        print "In CreateWorkspace"
        #const=constants()
        #disable load until another set of files has been selected
        self.ui.pushButtonCreateWorkspace.setEnabled(False)

        #set some initial progress on the meter
        self.ui.progressBarStatusProgress.setValue(10)

        #get output filename first
        wsname=self.ui.lineEditWorkspaceName.text()
        filter="NXS (*.nxs);;All files (*.*)"
        wsname=wsname+filter
        wspathname = QtGui.QFileDialog.getSaveFileName(self, 'Save Workspace', wsname,filter)        
        print "Workspace Save: ",wspathname
        #place code here to create the workspace
        #update application progress
        self.ui.progressBarStatusProgress.setValue(25)

        #then save the workspace to file
        fileObj=open(wspathname,'w')
        data=np.random.rand(1024,1024)
        fileObj.write(data)
        fileObj.close()
        self.ui.progressBarStatusProgress.setValue(50)		

        #now update the workspace manager with the new workspace		
        #determine how many files we have
        Nfiles = self.ui.tableWidget.rowCount()
        print "Number of rows: ", Nfiles
        #read scale factors for each file
        row=0 #set row counter
        for row in range(Nfiles):
            #get scale value and print it
            col=config.CWS_ScaleFactorCol
            scale=self.ui.tableWidget.item(row,col)
            print "Scale: ", scale.text()
            #scale cannot be edited once a file is loaded
            self.ui.tableWidget.item(row,col).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)	
            #change the item status to 'Loaded'
            col=config.CWS_StatusCol
            self.ui.tableWidget.setItem(row,col, QtGui.QTableWidgetItem('Loaded'))           
            self.ui.tableWidget.item(row,col).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Loaded Data")		
        wsName=self.ui.lineEditWorkspaceName.text()
        if wsName == "":
            #if no workspace name is given, use a default one
            wsName="NewWorkspace"
            self.ui.lineEditWorkspaceName.setText(wsName)
        #place code here to load workspace into memory and update table in workspace manager
        self.ui.progressBarStatusProgress.setValue(60)		

        #update workspace table
        wsName=self.ui.lineEditWorkspaceName.text()
        print "CreateWorkspace wsName: ",wspathname
        table=self.ui.tableWidgetWorkspaces
        addWStoTable(table,wsName,wspathname)
        self.ui.tableWidgetWorkspaces.resizeColumnsToContents();

        self.ui.progressBarStatusProgress.setValue(100)		
        time.sleep(1)
        self.ui.progressBarStatusProgress.setValue(0)

        #update status
        msg=time.strftime("%a %b %d %Y %H:%M:%S")+' Wrote file: '+wspathname
        self.ui.StatusText.append(msg)

        #once workspace loaded into memory, enable the save workspace button
        #also need to lock the workspace name lineEdit once the workspace has been created
        self.ui.lineEditWorkspaceName.setEnabled(False)

        #once the workspace has been created, saved, and loaded in, take user to workspace manager
        self.ui.stackedWidgetFilesWorkspaces.setCurrentIndex(1)

    def setGProps(self):
        print "SetGoniometerProperties"
        SetGoniometerProperties(self) #call separate GUI to set Goniometer properties
        
    def CheckWorkspace(self):
        #method to check the selected single or group workspace for the following:
        # - motor name
        # - initial (Psi) rotation angle
        # - inital a,b,c
        # - initial alpha, beta, gamma
        
        #need to determine which workspaces are selected 
        #get workspace table to work with
        table=self.ui.tableWidgetWorkspaces
        Nrows=table.rowCount()
        cnt=0
        for row in range(Nrows):
            cw=table.cellWidget(row,config.WSM_SelectCol) 
            cbstat=cw.isChecked()
            if cbstat:
                cnt+=1
                saveRow=row
        if cnt != 1:
            #case where we have the incorrect number of workspaces
            dialog=QtGui.QMessageBox(self)
            dialog.setText("Select only 1 workspace please")
            dialog.exec_()
            return
        #at this point we have one workspace or one workspace group - determine which
        #get the workspace
        tmpwsName=str(table.item(saveRow,config.WSM_WorkspaceCol).text())
        tmpws=mtd.retrieve(tmpwsName)
        if tmpws.id() == 'WorkspaceGroup':
            Nws=len(tmpws)
            wsNames=[]
            for i in range(Nws):
                wsNames.append(tmpws[i].getName())
            wsNames.sort() #sort so that lowest numbered workspace in the group is first in the list - assumes similarly named workspaces!
            wsName=wsNames[0]
            
        else:
            wsName=tmpwsName
        #now retrieve this workspace (in case it's not already been retrieved)
        tmpws=mtd.retrieve(wsName)
        
        #first check if the workspace has any values in it we may want
        try:
            Ei=tmpws.run().getProperty('Ei').value
            self.ui.labelSCEi.setText("Ei: "+"%.3f" % Ei)
            S1=tmpws.run().getProperty('S1').firstValue()
            self.ui.labelSCS1.setText("Start Angle: "+"%.3f" % S1)
            
        except:
            pass
        
        try:
            if not(tmpws.sample().hasOrientedLattice()):
                #case where there is no lattice info to use - inform user and return
                dialog=QtGui.QMessageBox(self)
                dialog.setText("No Lattice Information to Gather from Workspace - returning")
                dialog.exec_()  
                return
        except:
            dialog=QtGui.QMessageBox(self)
            dialog.setText("Incompatible Workspace - returning")
            dialog.exec_()  
            return
        #getting to this point, there should be some lattice info to use
        #get values from the run
        #**** Not sure what we want from the run at this point - leaving commented out code for example use later 
        """
        keys=tmpws.run().keys()
        motor1=tmpws.run().getProperty('s1').value
        """

        #get sample properties
        a=tmpws.sample().getOrientedLattice().a()
        b=tmpws.sample().getOrientedLattice().b()        
        c=tmpws.sample().getOrientedLattice().c()
        alpha=tmpws.sample().getOrientedLattice().alpha()
        beta=tmpws.sample().getOrientedLattice().beta()
        gamma=tmpws.sample().getOrientedLattice().gamma()
        uVector=tmpws.sample().getOrientedLattice().getuVector()
        uVectorX=uVector.getX()
        uVectorY=uVector.getY()
        uVectorZ=uVector.getZ()
        vVector=tmpws.sample().getOrientedLattice().getvVector()
        vVectorX=vVector.getX()
        vVectorY=vVector.getY()
        vVectorZ=vVector.getZ()
        
        #Unit Cell Parameters:
        self.ui.lineEditUCa.setText("%.3f" % a)
        self.ui.lineEditUCb.setText("%.3f" % b)
        self.ui.lineEditUCc.setText("%.3f" % c)
        self.ui.lineEditUCalpha.setText("%.3f" % alpha)
        self.ui.lineEditUCbeta.setText("%.3f" % beta)
        self.ui.lineEditUCgamma.setText("%.3f" % gamma)
        
        #Crystal Orientations:
        self.ui.lineEditSCCOux.setText("%.3f" % uVectorX)
        self.ui.lineEditSCCOuy.setText("%.3f" % uVectorY)
        self.ui.lineEditSCCOuz.setText("%.3f" % uVectorZ)
        self.ui.lineEditSCCOvx.setText("%.3f" % vVectorX)
        self.ui.lineEditSCCOvy.setText("%.3f" % vVectorY)
        self.ui.lineEditSCCOvz.setText("%.3f" % vVectorZ)        
        
        
    def DefaultSCParams(self):
        #Unit Cell Parameters:
        self.ui.lineEditUCa.setText(self.ui.SCUCa)
        self.ui.lineEditUCb.setText(self.ui.SCUCb)
        self.ui.lineEditUCc.setText(self.ui.SCUCc)
        self.ui.lineEditUCalpha.setText(self.ui.SCUCalpha)
        self.ui.lineEditUCbeta.setText(self.ui.SCUCbeta)
        self.ui.lineEditUCgamma.setText(self.ui.SCUCgamma)
        
        #Crystal Orientations:
        self.ui.lineEditSCCOux.setText(self.ui.SCCOux)
        self.ui.lineEditSCCOuy.setText(self.ui.SCCOuy)
        self.ui.lineEditSCCOuz.setText(self.ui.SCCOuz)
        self.ui.lineEditSCCOvx.setText(self.ui.SCCOvx)
        self.ui.lineEditSCCOvy.setText(self.ui.SCCOvy)
        self.ui.lineEditSCCOvz.setText(self.ui.SCCOvz)
        self.ui.lineEditSCCOPsi.setText(self.ui.SCCOPsi)		
        self.ui.lineEditSCCOName.setText(self.ui.SCCOMN)		
        
        #Viewing Angle
        self.ui.lineEditSCVAu1a.setText(self.ui.SCVAu1a)
        self.ui.lineEditSCVAu1b.setText(self.ui.SCVAu1b)
        self.ui.lineEditSCVAu1c.setText(self.ui.SCVAu1c)
        self.ui.lineEditSCVAu1Label.setText(self.ui.SCVAu1Label)
        self.ui.lineEditSCVAu2a.setText(self.ui.SCVAu2a)
        self.ui.lineEditSCVAu2b.setText(self.ui.SCVAu2b)
        self.ui.lineEditSCVAu2c.setText(self.ui.SCVAu2c)
        self.ui.lineEditSCVAu2Label.setText(self.ui.SCVAu2Label)
        self.ui.lineEditSCVAu3a.setText(self.ui.SCVAu3a)
        self.ui.lineEditSCVAu3b.setText(self.ui.SCVAu3b)
        self.ui.lineEditSCVAu3c.setText(self.ui.SCVAu3c)
        self.ui.lineEditSCVAu3Label.setText(self.ui.SCVAu3Label)      
        
        #Clear info
        self.ui.labelSCEi.setText("Ei: ")
        self.ui.labelSCS1.setText("Start Angle: ")

    def SaveSCParams(self):
        
        filter="XML (*.xml);;All files (*.*)"
        xmlname="SingleCrystalParams.xml"
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save Single Crystal GUI Parameters', xmlname,filter)       
        if filename=='':
            #case where no filename was selected
            print "No file selected - returning"
            return
        
        #get parameters from GUI:
        #Unit Cell Parameters:
        SCUCa=str(self.ui.lineEditUCa.text())
        SCUCb=str(self.ui.lineEditUCb.text())
        SCUCc=str(self.ui.lineEditUCc.text())
        SCUCalpha=str(self.ui.lineEditUCalpha.text())
        SCUCbeta=str(self.ui.lineEditUCbeta.text())
        SCUCgamma=str(self.ui.lineEditUCgamma.text())
        
        #Crystal Orientations:
        SCCOux=str(self.ui.lineEditSCCOux.text())
        SCCOuy=str(self.ui.lineEditSCCOuy.text())
        SCCOuz=str(self.ui.lineEditSCCOuz.text())
        SCCOvx=str(self.ui.lineEditSCCOvx.text())
        SCCOvy=str(self.ui.lineEditSCCOvy.text())
        SCCOvz=str(self.ui.lineEditSCCOvz.text())
        SCCOPsi=str(self.ui.lineEditSCCOPsi.text())
        SCCOMN=str(self.ui.lineEditSCCOName.text())		
        
        #Viewing Angle
        SCVAu1a=str(self.ui.lineEditSCVAu1a.text())
        SCVAu1b=str(self.ui.lineEditSCVAu1b.text())
        SCVAu1c=str(self.ui.lineEditSCVAu1c.text())
        SCVAu1Label=str(self.ui.lineEditSCVAu1Label.text())
        SCVAu2a=str(self.ui.lineEditSCVAu2a.text())
        SCVAu2b=str(self.ui.lineEditSCVAu2b.text())
        SCVAu2c=str(self.ui.lineEditSCVAu2c.text())
        SCVAu2Label=str(self.ui.lineEditSCVAu2Label.text())
        SCVAu3a=str(self.ui.lineEditSCVAu3a.text())
        SCVAu3b=str(self.ui.lineEditSCVAu3b.text())
        SCVAu3c=str(self.ui.lineEditSCVAu3c.text())
        SCVAu3Label=str(self.ui.lineEditSCVAu3Label.text())
        
        #pack variables into a dictionary
        params_dict_root={'root':{
                            'SCUCa':SCUCa,
                            'SCUCb':SCUCb,
                            'SCUCc':SCUCc,
                            'SCUCalpha':SCUCalpha,                   
                            'SCUCbeta':SCUCbeta,                                          
                            'SCUCgamma':SCUCgamma,                
                            'SCCOux':SCCOux,
                            'SCCOuy':SCCOuy,                        
                            'SCCOuz':SCCOuz,            
                            'SCCOvx':SCCOvx,
                            'SCCOvy':SCCOvy,                        
                            'SCCOvz':SCCOvz,     
                            'SCCOPsi':SCCOPsi,                        
                            'SCCOMN':SCCOMN,                        
                            'SCVAu1a':SCVAu1a,                    
                            'SCVAu1b':SCVAu1b,                        
                            'SCVAu1c':SCVAu1c,                        
                            'SCVAu1Label':SCVAu1Label,
                            'SCVAu2a':SCVAu2a,                       
                            'SCVAu2b':SCVAu2b,                        
                            'SCVAu2c':SCVAu2c,                        
                            'SCVAu2Label':SCVAu2Label,                        
                            'SCVAu3a':SCVAu3a,
                            'SCVAu3b':SCVAu3b,                        
                            'SCVAu3c':SCVAu3c,                        
                            'SCVAu3Label':SCVAu3Label                                                
                        }}
                        
        params_dict=params_dict_root.get('root') 
        for key,value in params_dict.items():
            print "key: ",key,"  value: ",value, " type(value): ",type(value)
                        
        #create xml from dictionary and save xml to file
        dicttoxmlfile(params_dict_root, filename)
        
        
    def LoadSCParams(self):
        #method to load parameters from file to the Parameters portion of the GUI
        curdir=os.curdir
        filter="XML (*.xml);;All files (*.*)"
        xmlfile = QtGui.QFileDialog.getOpenFileNames(self, 'Open Single Crystal Params File', curdir,filter)
        xmlfile = str(xmlfile[0])
        if xmlfile=='':
            #no file selected
            print "No file selected - returning"
            return
        print "xmlfile: ",xmlfile," type(xmlfile): ",type(xmlfile)
        #retrieve dictionary from xml file
        params_dict_root=xmlfiletodict(xmlfile)
        
        #place dictionary values into GUI
        params_dict=params_dict_root.get('root') # need to strip off root key
        
        #scan dictionary for empty values and substitute a space as setText() cannot set an empty value
        for key,value in params_dict.items():
            if value==None:
                params_dict[key]=''
        
        #Unit Cell Parameters:
        self.ui.lineEditUCa.setText(params_dict.get('SCUCa'))
        self.ui.lineEditUCb.setText(params_dict.get('SCUCb'))
        self.ui.lineEditUCc.setText(params_dict.get('SCUCc'))
        self.ui.lineEditUCalpha.setText(params_dict.get('SCUCalpha'))
        self.ui.lineEditUCbeta.setText(params_dict.get('SCUCbeta'))
        self.ui.lineEditUCgamma.setText(params_dict.get('SCUCgamma'))
        
        #Crystal Orientations:
        self.ui.lineEditSCCOux.setText(params_dict.get('SCCOux'))
        self.ui.lineEditSCCOuy.setText(params_dict.get('SCCOuy'))
        self.ui.lineEditSCCOuz.setText(params_dict.get('SCCOuz'))
        self.ui.lineEditSCCOvx.setText(params_dict.get('SCCOvx'))
        self.ui.lineEditSCCOvy.setText(params_dict.get('SCCOvy'))
        self.ui.lineEditSCCOvz.setText(params_dict.get('SCCOvz'))
        self.ui.lineEditSCCOPsi.setText(params_dict.get('SCCOPsi'))		
        self.ui.lineEditSCCOName.setText(params_dict.get('SCCOMN'))		
        
        #Viewing Angle
        self.ui.lineEditSCVAu1a.setText(params_dict.get('SCVAu1a'))
        self.ui.lineEditSCVAu1b.setText(params_dict.get('SCVAu1b'))
        self.ui.lineEditSCVAu1c.setText(params_dict.get('SCVAu1c'))
        self.ui.lineEditSCVAu1Label.setText(params_dict.get('SCVAu1Label'))
        self.ui.lineEditSCVAu2a.setText(params_dict.get('SCVAu2a'))
        self.ui.lineEditSCVAu2b.setText(params_dict.get('SCVAu2b'))
        self.ui.lineEditSCVAu2c.setText(params_dict.get('SCVAu2c'))
        self.ui.lineEditSCVAu2Label.setText(params_dict.get('SCVAu2Label'))
        self.ui.lineEditSCVAu3a.setText(params_dict.get('SCVAu3a'))
        self.ui.lineEditSCVAu3b.setText(params_dict.get('SCVAu3b'))
        self.ui.lineEditSCVAu3c.setText(params_dict.get('SCVAu3c'))
        self.ui.lineEditSCVAu3Label.setText(params_dict.get('SCVAu3Label'))    

    def UpdateViewSCDict(self):
        print "In UpdateViewSCDict(self)"
        #This method updates the ViewSCDict dictionary any time that a value
        #is changed in the Viewing Axes field changes.  As this can be performed quickly,
        #the entire dictionary is update when a selction is made in lieu of having a
        #separate method for each of the 12 fields that can change.
        
        #Note that currently only the dictionary labels are updated and that
        #other parameters are updated once SC calc projections occurs
        
        ViewSCDict=self.ui.ViewSCDict #for convenience and readability, shorten the name 
        
        #get updated labels
        nameLst=makeSCNames(self)
        #put labels in the View dictionary
        ViewSCDict['u1']['label']=nameLst[0]
        ViewSCDict['u2']['label']=nameLst[1]
        ViewSCDict['u3']['label']=nameLst[2]
        #note that 'E' label does not change...
        #store label changes back into the global dictionary
        self.ui.ViewSCDict=ViewSCDict
        
        #update corresponding ViewSCData labels - X
        self.ui.comboBoxSCSliceX.setItemText(0,ViewSCDict['u1']['label'])
        self.ui.comboBoxSCSliceX.setItemText(1,ViewSCDict['u2']['label'])
        self.ui.comboBoxSCSliceX.setItemText(2,ViewSCDict['u3']['label'])
        self.ui.comboBoxSCSliceX.setItemText(3,ViewSCDict['E']['label'])
        #update corresponding ViewSCData labels - Y
        self.ui.comboBoxSCSliceY.setItemText(0,ViewSCDict['u1']['label'])
        self.ui.comboBoxSCSliceY.setItemText(1,ViewSCDict['u2']['label'])
        self.ui.comboBoxSCSliceY.setItemText(2,ViewSCDict['u3']['label'])
        self.ui.comboBoxSCSliceY.setItemText(3,ViewSCDict['E']['label'])
        #update corresponding ViewSCData labels - Z
        self.ui.comboBoxSCSliceZ.setItemText(0,ViewSCDict['u1']['label'])
        self.ui.comboBoxSCSliceZ.setItemText(1,ViewSCDict['u2']['label'])
        self.ui.comboBoxSCSliceZ.setItemText(2,ViewSCDict['u3']['label'])
        self.ui.comboBoxSCSliceZ.setItemText(3,ViewSCDict['E']['label'])
        #update corresponding ViewSCData labels - E
        self.ui.comboBoxSCSliceE.setItemText(0,ViewSCDict['u1']['label'])
        self.ui.comboBoxSCSliceE.setItemText(1,ViewSCDict['u2']['label'])
        self.ui.comboBoxSCSliceE.setItemText(2,ViewSCDict['u3']['label'])
        self.ui.comboBoxSCSliceE.setItemText(3,ViewSCDict['E']['label'])
        
        
    def UpdateComboSCX(self):
        """
        Wrapper method to perform swapping labels for 'X' comboBox
        """
        print "** UpdateComboSCX"
        label= str(self.ui.comboBoxSCSliceX.currentText())
        self.UpdateViewSCData(label,'u1')
        self.ui.ViewSCDataDeBounce=False
        
    def UpdateComboSCY(self):
        """
        Wrapper method to perform swapping labels for 'Y' comboBox
        """
        print "** UpdateComboSCY"
        label= str(self.ui.comboBoxSCSliceY.currentText())
        self.UpdateViewSCData(label,'u2')
        self.ui.ViewSCDataDeBounce=False
                
    def UpdateComboSCZ(self):
        """
        Wrapper method to perform swapping labels for 'Z' comboBox
        """
        print "** UpdateComboSCZ"
        label= str(self.ui.comboBoxSCSliceZ.currentText())
        self.UpdateViewSCData(label,'u3')
        self.ui.ViewSCDataDeBounce=False
                
    def UpdateComboSCE(self):
        """
        Wrapper method to perform swapping labels for 'E' comboBox
        """
        print "** UpdateComboSCE"
        label= str(self.ui.comboBoxSCSliceE.currentText())
        self.UpdateViewSCData(label,'E')
        self.ui.ViewSCDataDeBounce=False
                
    def UpdateViewSCData(self,newLabel,newKey):
        """
        Method to perform swapping single crystal comboBox labels
        newLabel: new comboBox label
        newKey: key to index used for the swap
        """
        if self.ui.ViewSCDataDeBounce:
            #case we have a second update due to programmtically changing the current index - skip this one
            #print "++++++++ Debounce +++++++++"
            return
        #get labels for each comboBox - should have a duplicate at this point
        labels=[]
        labels.append(str(self.ui.comboBoxSCSliceX.currentText()))
        labels.append(str(self.ui.comboBoxSCSliceY.currentText()))
        labels.append(str(self.ui.comboBoxSCSliceZ.currentText()))
        labels.append(str(self.ui.comboBoxSCSliceE.currentText()))  
        
        #get list of possible labels - should be no duplicates
        labelLst=[]
        ViewSCDict=self.ui.ViewSCDict
        labelLst.append(ViewSCDict['u1']['label'])
        labelLst.append(ViewSCDict['u2']['label'])
        labelLst.append(ViewSCDict['u3']['label'])
        labelLst.append(ViewSCDict['E']['label'])    
        
        #Let's find the missing label
        cntr=0
        for chkLab in labelLst:
            tst=chkLab in labels
            if not(tst):
                #case we found the missing label
                missingLab=chkLab
                missingIndx=cntr
            cntr+=1
        
        #check which labels match the one passed in
        cnt=0
        mtch=[]
        for label in labels:
            if label == newLabel:
                mtch.append(cnt)
            cnt+=1

        if len(mtch) != 2:
            print "Did not find the correct number of labels - 2 expected but found: ",len(mtch)
            
        #check which index matches the index passed in
        cnt=0

        for indx in mtch:
            if indx != int(ViewSCDict[newKey]['index']):
                updateCBIndx=indx
                cnt+=1 #check to make sure we found an updateCBIndx
            if indx == int(ViewSCDict[newKey]['index']):
                otherIndex=indx
                
        if cnt != 1:
            print "Did not find the correct number of indicies- 1 expected but found: ",cnt
        #The indx we found 
        
        #Setting the debounce flag to True enables setCurrentIndex() event generated via the code
        #below to be ignored else letting this even be processed interferes with the current processing
        self.ui.ViewSCDataDeBounce=True 
        if updateCBIndx==0:
            #self.ui.comboBoxSCSliceX.setItemText(oldIndex,ViewSCDict[newKey]['label'])
            self.ui.comboBoxSCSliceX.setCurrentIndex(missingIndx)
        if updateCBIndx==1:
            #self.ui.comboBoxSCSliceY.setItemText(oldIndex,ViewSCDict[newKey]['label'])
            self.ui.comboBoxSCSliceY.setCurrentIndex(missingIndx)
        if updateCBIndx==2:
            #self.ui.comboBoxSCSliceZ.setItemText(oldIndex,ViewSCDict[newKey]['label'])
            self.ui.comboBoxSCSliceZ.setCurrentIndex(missingIndx)
        if updateCBIndx==3:
            #self.ui.comboBoxSCSliceE.setItemText(oldIndex,ViewSCDict[newKey]['label'])
            self.ui.comboBoxSCSliceE.setCurrentIndex(missingIndx)    
            
        #Now that we have the information for the swapped combo boxes, let's swap the corresponding parameters
        #Will simpy swap what's in the GUI widgets
        CBIndx0=mtch[0]
        CBIndx1=mtch[1]
        swapSCViewParams(self,'Slice',CBIndx0,CBIndx1)

    def updateSCNpts(self):
        
        
        #function to update the number of points in the Single Crystal GUI when parameters change affecting the number of points
        
        #Update X NPTS label
        #get parameters:
        if str(self.ui.lineEditSCSliceXFrom.text()) != '':
            XFrom=float(str(self.ui.lineEditSCSliceXFrom.text()))
        else:
            return
        if str(self.ui.lineEditSCSliceXTo.text()) != '':
            XTo=float(str(self.ui.lineEditSCSliceXTo.text()))
        else:
            return
        if str(self.ui.lineEditSCSliceXStep.text()) != '':
            XStep=float(str(self.ui.lineEditSCSliceXStep.text()))
        else:
            return
        
        #Do some checking:
        if XFrom >= XTo:
            #case where the lower limit exceeds or is equal to the upper limit - problem case
            msg="Problem: X From is greater than X To - Please make corrections"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_() 
            return
            
        if XStep == 0:
            #case where the lower limit exceeds or is equal to the upper limit - problem case
            msg="Problem: X Step must be greater than 0 - Please correct"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_() 
            return
    
        try:
            XNpts=(XTo-XFrom)/XStep
        
        except:
            #case where unable to successfully calculate XNpts
            self.ui.labelSCNptsX.setText("Npts:   ")
            msg="Unable to calculate 'X NPTS - please make corrections"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_()         
            return
        else:
            self.ui.labelSCNptsX.setText("Npts: "+str(int(XNpts)))
            
        if XNpts > config.SCXNpts:
            #case where a large number of points has been selected
            msg="Warning: Current X settings will produce a large number of values: "+str(XNpts)+". Consider making changes"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_()         
            return                
        
    
        #Update Y NPTS label
        #get parameters:
        if str(self.ui.lineEditSCSliceYFrom.text()) != '':
            YFrom=float(str(self.ui.lineEditSCSliceYFrom.text()))
        else:
            return
        if str(self.ui.lineEditSCSliceYTo.text()) != '':
            YTo=float(str(self.ui.lineEditSCSliceYTo.text()))
        else:
            return
        if str(self.ui.lineEditSCSliceYStep.text()) != '':
            YStep=float(str(self.ui.lineEditSCSliceYStep.text()))
        else:
            return
        
        #Do some checking:
        if YFrom >= YTo:
            #case where the lower limit exceeds or is equal to the upper limit - problem case
            msg="Problem: Y From is greater than Y To - Please make corrections"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_() 
            return
            
        if YStep == 0:
            #case where the lower limit exceeds or is equal to the upper limit - problem case
            msg="Problem: Y Step must be greater than 0 - Please correct"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_() 
            return
    
        try:
            YNpts=(YTo-YFrom)/YStep
        
        except:
            #case where unable to successfully calculate YNpts
            self.ui.labelSCNptsY.setText("Npts:   "+str(YNpts))
            msg="Unable to calculate 'Y NPTS - please make corrections"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_()         
            return
        else:
            self.ui.labelSCNptsY.setText("Npts: "+str(int(YNpts)))
            
        if YNpts > config.SCYNpts:
            #case where a large number of points has been selected
            msg="Warning: Current Y settings will produce a large number of values: "+str(YNpts)+". Consider making changes"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_()         
            return    

    def UpdateViewSCVDict(self):
        print "In UpdateViewSCVDict(self)"
        #This method updates the ViewSCDict dictionary any time that a value
        #is changed in the Viewing Axes field changes.  As this can be performed quickly,
        #the entire dictionary is update when a selction is made in lieu of having a
        #separate method for each of the 12 fields that can change.
        
        #Note that currently only the dictionary labels are updated and that
        #other parameters are updated once SC calc projections occurs
        
        ViewSCVDict=self.ui.ViewSCVDict #for convenience and readability, shorten the name 
        
        #get updated labels
        nameLst=makeSCNames(self)
        #put labels in the View dictionary
        ViewSCVDict['u1']['label']=nameLst[0]
        ViewSCVDict['u2']['label']=nameLst[1]
        ViewSCVDict['u3']['label']=nameLst[2]
        #note that 'E' label does not change...
        #store label changes back into the global dictionary
        self.ui.ViewSCVDict=ViewSCVDict
        
        #update corresponding ViewSCData labels - X
        self.ui.comboBoxSCVolX.setItemText(0,ViewSCVDict['u1']['label'])
        self.ui.comboBoxSCVolX.setItemText(1,ViewSCVDict['u2']['label'])
        self.ui.comboBoxSCVolX.setItemText(2,ViewSCVDict['u3']['label'])
        self.ui.comboBoxSCVolX.setItemText(3,ViewSCVDict['E']['label'])
        #update corresponding ViewSCData labels - Y
        self.ui.comboBoxSCVolY.setItemText(0,ViewSCVDict['u1']['label'])
        self.ui.comboBoxSCVolY.setItemText(1,ViewSCVDict['u2']['label'])
        self.ui.comboBoxSCVolY.setItemText(2,ViewSCVDict['u3']['label'])
        self.ui.comboBoxSCVolY.setItemText(3,ViewSCVDict['E']['label'])
        #update corresponding ViewSCData labels - Z
        self.ui.comboBoxSCVolZ.setItemText(0,ViewSCVDict['u1']['label'])
        self.ui.comboBoxSCVolZ.setItemText(1,ViewSCVDict['u2']['label'])
        self.ui.comboBoxSCVolZ.setItemText(2,ViewSCVDict['u3']['label'])
        self.ui.comboBoxSCVolZ.setItemText(3,ViewSCVDict['E']['label'])
        #update corresponding ViewSCData labels - E
        self.ui.comboBoxSCVolE.setItemText(0,ViewSCVDict['u1']['label'])
        self.ui.comboBoxSCVolE.setItemText(1,ViewSCVDict['u2']['label'])
        self.ui.comboBoxSCVolE.setItemText(2,ViewSCVDict['u3']['label'])
        self.ui.comboBoxSCVolE.setItemText(3,ViewSCVDict['E']['label'])
        
        
    def UpdateComboSCVX(self):
        """
        Wrapper method to perform swapping labels for 'X' comboBox
        """
        print "** UpdateComboSCVX"
        label= str(self.ui.comboBoxSCVolX.currentText())
        self.UpdateViewSCVData(label,'u1')
        self.ui.ViewSCVDataDeBounce=False
        
    def UpdateComboSCVY(self):
        """
        Wrapper method to perform swapping labels for 'Y' comboBox
        """
        print "** UpdateComboSCVY"
        label= str(self.ui.comboBoxSCVolY.currentText())
        self.UpdateViewSCVData(label,'u2')
        self.ui.ViewSCVDataDeBounce=False
                
    def UpdateComboSCVZ(self):
        """
        Wrapper method to perform swapping labels for 'Z' comboBox
        """
        print "** UpdateComboSCVZ"
        label= str(self.ui.comboBoxSCVolZ.currentText())
        self.UpdateViewSCVData(label,'u3')
        self.ui.ViewSCVDataDeBounce=False
                
    def UpdateComboSCVE(self):
        """
        Wrapper method to perform swapping labels for 'E' comboBox
        """
        print "** UpdateComboSCVE"
        label= str(self.ui.comboBoxSCVolE.currentText())
        self.UpdateViewSCVData(label,'E')
        self.ui.ViewSCVDataDeBounce=False
                
    def UpdateViewSCVData(self,newLabel,newKey):
        """
        Method to perform swapping single crystal comboBox labels
        newLabel: new comboBox label
        newKey: key to index used for the swap
        """
        if self.ui.ViewSCVDataDeBounce:
            #case we have a second update due to programmtically changing the current index - skip this one
            #print "++++++++ Debounce +++++++++"
            return
        #get labels for each comboBox - should have a duplicate at this point
        labels=[]
        labels.append(str(self.ui.comboBoxSCVolX.currentText()))
        labels.append(str(self.ui.comboBoxSCVolY.currentText()))
        labels.append(str(self.ui.comboBoxSCVolZ.currentText()))
        labels.append(str(self.ui.comboBoxSCVolE.currentText()))  
        
        #get list of possible labels - should be no duplicates
        labelLst=[]
        ViewSCVDict=self.ui.ViewSCVDict
        labelLst.append(ViewSCVDict['u1']['label'])
        labelLst.append(ViewSCVDict['u2']['label'])
        labelLst.append(ViewSCVDict['u3']['label'])
        labelLst.append(ViewSCVDict['E']['label'])    
        
        #Let's find the missing label
        cntr=0
        for chkLab in labelLst:
            tst=chkLab in labels
            if not(tst):
                #case we found the missing label
                missingLab=chkLab
                missingIndx=cntr
            cntr+=1
        
        #check which labels match the one passed in
        cnt=0
        mtch=[]
        for label in labels:
            if label == newLabel:
                mtch.append(cnt)
            cnt+=1

        if len(mtch) != 2:
            print "Did not find the correct number of labels - 2 expected but found: ",len(mtch)
            
        #check which index matches the index passed in
        cnt=0

        for indx in mtch:
            if indx != int(ViewSCVDict[newKey]['index']):
                updateCBIndx=indx
                cnt+=1 #check to make sure we found an updateCBIndx
            if indx == int(ViewSCVDict[newKey]['index']):
                otherIndex=indx
                
        if cnt != 1:
            print "Did not find the correct number of indicies- 1 expected but found: ",cnt
        #The indx we found 
        
        #Setting the debounce flag to True enables setCurrentIndex() event generated via the code
        #below to be ignored else letting this even be processed interferes with the current processing
        self.ui.ViewSCVDataDeBounce=True 
        if updateCBIndx==0:
            self.ui.comboBoxSCVolX.setCurrentIndex(missingIndx)
        if updateCBIndx==1:
            self.ui.comboBoxSCVolY.setCurrentIndex(missingIndx)
        if updateCBIndx==2:
            self.ui.comboBoxSCVolZ.setCurrentIndex(missingIndx)
        if updateCBIndx==3:
            self.ui.comboBoxSCVolE.setCurrentIndex(missingIndx)    
            
        #Now that we have the information for the swapped combo boxes, let's swap the corresponding parameters
        #Will simpy swap what's in the GUI widgets
        CBIndx0=mtch[0]
        CBIndx1=mtch[1]
        swapSCViewParams(self,'Volume',CBIndx0,CBIndx1)

    def updateSCVNpts(self):
        
        
        #function to update the number of points in the Single Crystal GUI when parameters change affecting the number of points
        
        #Update X NPTS label
        #get parameters:
        if str(self.ui.lineEditSCVolXFrom.text()) != '':
            XFrom=float(str(self.ui.lineEditSCVolXFrom.text()))
        else:
            return
        if str(self.ui.lineEditSCVolXTo.text()) != '':
            XTo=float(str(self.ui.lineEditSCVolXTo.text()))
        else:
            return
        if str(self.ui.lineEditSCVolXStep.text()) != '':
            XStep=float(str(self.ui.lineEditSCVolXStep.text()))
        else:
            return
        
        #Do some checking:
        if XFrom >= XTo:
            #case where the lower limit exceeds or is equal to the upper limit - problem case
            msg="Problem: X From is greater than X To - Please make corrections"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_() 
            return
            
        if XStep == 0:
            #case where the lower limit exceeds or is equal to the upper limit - problem case
            msg="Problem: X Step must be greater than 0 - Please correct"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_() 
            return
    
        try:
            XNpts=(XTo-XFrom)/XStep
        
        except:
            #case where unable to successfully calculate XNpts
            self.ui.labelSCVNptsX.setText("Npts:   ")
            msg="Unable to calculate 'X NPTS - please make corrections"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_()         
            return
        else:
            self.ui.labelSCVNptsX.setText("Npts: "+str(int(XNpts)))
            
        if XNpts > config.SCXNpts:
            #case where a large number of points has been selected
            msg="Warning: Current X settings will produce a large number of values: "+str(XNpts)+". Consider making changes"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_()         
            return                
        
    
        #Update Y NPTS label
        #get parameters:
        if str(self.ui.lineEditSCVolYFrom.text()) != '':
            YFrom=float(str(self.ui.lineEditSCVolYFrom.text()))
        else:
            return
        if str(self.ui.lineEditSCVolYTo.text()) != '':
            YTo=float(str(self.ui.lineEditSCVolYTo.text()))
        else:
            return
        if str(self.ui.lineEditSCVolYStep.text()) != '':
            YStep=float(str(self.ui.lineEditSCVolYStep.text()))
        else:
            return
        
        #Do some checking:
        if YFrom >= YTo:
            #case where the lower limit exceeds or is equal to the upper limit - problem case
            msg="Problem: Y From is greater than Y To - Please make corrections"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_() 
            return
            
        if YStep == 0:
            #case where the lower limit exceeds or is equal to the upper limit - problem case
            msg="Problem: Y Step must be greater than 0 - Please correct"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_() 
            return
    
        try:
            YNpts=(YTo-YFrom)/YStep
        
        except:
            #case where unable to successfully calculate YNpts
            self.ui.labelSCVNptsY.setText("Npts:   "+str(YNpts))
            msg="Unable to calculate 'Y NPTS - please make corrections"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_()         
            return
        else:
            self.ui.labelSCVNptsY.setText("Npts: "+str(int(YNpts)))
            
        if YNpts > config.SCYNpts:
            #case where a large number of points has been selected
            msg="Warning: Current Y settings will produce a large number of values: "+str(YNpts)+". Consider making changes"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_()         
            return    


        

if __name__=="__main__":
    activeWin=QtGui.QApplication.activeWindow()
    print "Active Window: ",activeWin
    if activeWin == None:
        #case where running this application as a standalone application
        app = QtGui.QApplication(sys.argv)
        msliceapp = MSlice()
        msliceapp.show()
        exit_code=app.exec_()
        print "exit code: ",exit_code
        sys.exit(exit_code)
    else:
        #case running this application within an existing app such as mantidplot
        #in this case, do not need to create application or handle exit case
        msliceapp = MSlice()
        msliceapp.show()