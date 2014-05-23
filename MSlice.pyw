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
from MSliceHelpers import getReduceAlgFromWorkspace, getWorkspaceMemSize
#import h5py 
from WorkspaceComposerMain import *

#import Mantid computatinal modules
sys.path.append(os.environ['MANTIDPATH'])
from mantid.simpleapi import *

#import SliceViewer (here it assumes local module as a Mantid produced module for this does not exist)
from SliceViewer import *

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
        
        const=constants()
		
        #define actions and callbacks
        self.connect(self.ui.actionLoad_Workspace_s, QtCore.SIGNAL('triggered()'), self.WorkspaceManagerPageSelect) #make workspace stack page available to user
        self.connect(self.ui.actionCreateWorkspace, QtCore.SIGNAL('triggered()'), self.CreateWorkspacePageSelect) #define function to call to select files
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

#        col=const.WSM_SelectCol
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

        #setup callbacks for Single Crystal Volume push buttons - Plot, Oplot, and Surface Slice
        QtCore.QObject.connect(self.ui.pushButtonSCPlotVol, QtCore.SIGNAL('clicked(bool)'), self.pushButtonSCVolPlotSelect)
        QtCore.QObject.connect(self.ui.pushButtonSCOplotVol, QtCore.SIGNAL('clicked(bool)'), self.pushButtonSCVolOplotSelect)
 
        #setup SC Volume tab
		#first setup combo boxes
        self.ui.comboBoxSCVolX.setCurrentIndex(1)
        self.ui.comboBoxSCVolX.setCurrentIndex(0)  # seem to need to toggle index 0 to get label to appear initially in GUI
        self.ui.comboBoxSCVolY.setCurrentIndex(1)		
        self.ui.comboBoxSCVolZ.setCurrentIndex(2)	
        self.ui.comboBoxSCVolE.setCurrentIndex(3)			
        self.ui.comboBoxSCVolCT.setCurrentIndex(1)
		
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
        QtCore.QObject.connect(self.ui.pushButtonPowderCutOplot, QtCore.SIGNAL('clicked(bool)'), self.pushButtonPowderCutOplotSelect)

        #setup Powder Cut comboBox initial values
        self.ui.comboBoxPowderCutAlong.setCurrentIndex(1)
        self.ui.comboBoxPowderCutAlong.setCurrentIndex(0) # seem to need to toggle index 0 to get label to appear initially in GUI
        self.ui.comboBoxPowderCutThick.setCurrentIndex(1)
        self.ui.comboBoxPowderCutAlong.setCurrentIndex(1)
        self.ui.comboBoxPowderCutAlong.setCurrentIndex(0) # seem to need to toggle index 0 to get label to appear initially in GUI
		
        #setup callbacks for Single Crystal Slice push buttons - Plot, Oplot, and Surface Slice
        QtCore.QObject.connect(self.ui.pushButtonSCSlicePlotSlice, QtCore.SIGNAL('clicked(bool)'), self.pushButtonSCSlicePlotSliceSelect)
        QtCore.QObject.connect(self.ui.pushButtonSCSliceOplotSlice, QtCore.SIGNAL('clicked(bool)'), self.pushButtonSCSliceOplotSliceSelect)
        QtCore.QObject.connect(self.ui.pushButtonSCSliceSurfaceSlice, QtCore.SIGNAL('clicked(bool)'), self.pushButtonSCSliceSurfaceSliceSelect)
 
        #setup SC Slice tab
		#first setup combo boxes
        self.ui.comboBoxSCSliceX.setCurrentIndex(1)
        self.ui.comboBoxSCSliceX.setCurrentIndex(0)  # seem to need to toggle index 0 to get label to appear initially in GUI
        self.ui.comboBoxSCSliceY.setCurrentIndex(1)		
        self.ui.comboBoxSCSliceZ.setCurrentIndex(2)		
        self.ui.comboBoxSCSliceE.setCurrentIndex(3)				
		
        #setup callbacks for Powder Slice push buttons - Plot, Oplot, and Surface Slice
        QtCore.QObject.connect(self.ui.pushButtonPowderSlicePlotSlice, QtCore.SIGNAL('clicked(bool)'), self.pushButtonPowderSlicePlotSliceSelect)
        QtCore.QObject.connect(self.ui.pushButtonPowderSliceOplotSlice, QtCore.SIGNAL('clicked(bool)'), self.pushButtonPowderSliceOplotSliceSelect)
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

    #add slot for workspace group editor to connect to
    @QtCore.pyqtSlot(int)
    def on_button_clicked(self,val):       #signal for this function defined in WorkspaceComposerMain.py
        #val can be used to let this methold know who called it should that be desired
        
        #get constants
	const=constants()
        
        print "on_button_clicked - val: ",val
        self.ui.pushButtonUpdate.setEnabled(True)
        #now add new group workspace to Workspace Manager table
        table=self.ui.tableWidgetWorkspaces
        GWSName=self.ui.GWSName
        wsname=self.ui.returnName
        wstype=self.ui.returnType
        wssize=self.ui.returnSize
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
                if wsname == str(table.item(row,const.WSM_WorkspaceCol).text()):
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
	const=constants()
	
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
            cw=table.cellWidget(row,const.WSM_SelectCol) 
            cbstat=cw.isChecked()
            if cbstat:
                
                #case to attempt to run calculate projections
                #FIXME - skipped for now, but will need to verify workspace type before running calc proj
                #but for now, we'll assume that it's a powder workspace
                pws=str(table.item(row,const.WSM_WorkspaceCol).text())
                self.ui.StatusText.append(time.strftime('  Input Workspace: '+pws))	
                print "  pws: ",pws
                pws_out=pws+pwsSuffix
                self.ui.StatusText.append(time.strftime('  Output Workspace: '+pws_out))	
                print "  pws_out: ",pws_out
                h=ConvertToMDHelper(pws,'|Q|','Direct')
                #need to figure out how to make the output workspace name 
                ConvertToMD(pws,MinValues=h[0],MaxValues=h[1],QDimensions='|Q|',dEAnalysisMode='Direct',Outputworkspace=pws_out)
                placeholderws=mtd.retrieve(pws_out)
                #once outputworkspace exists, add it back to the table
                pws_type='Powder Calc Proj'
                pws_size=str(float(int(float(placeholderws.getMemorySize())/float(1024*1024)*10))/10)+' MB'
                pws_indx=Nrows+addcntr
                print "pws_out: ",pws_out
                print "pws_type: ",pws_type
                print "pws_size: ",pws_size
                table.insertRow(pws_indx)
                addmemWStoTable(table,pws_out,pws_type,pws_size,pws_indx)
                addCheckboxToWSTCell(table,row,const.WSM_SelectCol,False) #row was: pws_indx-1
                addcntr +=1 #increment row counter for where to add a workspace
        table.resizeColumnsToContents();
        time.sleep(0.2) #give some time since processing before clearing progress bar
        self.ui.progressBarStatusProgress.setValue(0) #clear progress bar
        #upon successful completion enable Powder Calc Proj button
        self.ui.pushButtonPowderCalcProj.setEnabled(True)      
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Powder Calculate Projections Complete")	
        print "Powder Calc Workspaces Processed: "
		
    def SCCalcProjSelect(self):

        #disable Powder Calc Proj until calculations complete
        self.ui.pushButtonSCCalcProj.setEnabled(False)      
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Single Crystal Calculate Projections Initiated")		
		
        #extract values from the line text boxes
		#Unit Cell Parameters:
        SCUCa=self.ui.lineEditUCa.text()
        SCUCb=self.ui.lineEditUCb.text()
        SCUCc=self.ui.lineEditUCc.text()
        SCUCalpha=self.ui.lineEditUCalpha.text()
        SCUCbeta=self.ui.lineEditUCbeta.text()
        SCUCgamma=self.ui.lineEditUCgamma.text()
        print "UC values: ",SCUCa,SCUCb,SCUCc,SCUCalpha,SCUCbeta,SCUCgamma
        
		#Crystal Orientations:
        SCCOux=self.ui.lineEditSCCOux.text()
        SCCOuy=self.ui.lineEditSCCOuy.text()
        SCCOuz=self.ui.lineEditSCCOuz.text()
        SCCOvx=self.ui.lineEditSCCOvx.text()
        SCCOvy=self.ui.lineEditSCCOvy.text()
        SCCOvz=self.ui.lineEditSCCOvz.text()
        SCCOPsi=self.ui.lineEditSCCOPsi.text()		
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
        print "VA - fold u1: ",SCVAu1Fold,SCVAu1Center,SCVAu1Direction,SCVAu1Directiontxt
        print "VA - fold u2: ",SCVAu2Fold,SCVAu2Center,SCVAu2Direction,SCVAu2Directiontxt
        print "VA - fold u3: ",SCVAu3Fold,SCVAu3Center,SCVAu3Direction,SCVAu3Directiontxt
		
        NumActiveWorkspaces=self.ui.numActiveWorkspaces
        #for demo purposes, activate the application status progress bar
        for i in range(NumActiveWorkspaces):
            #************ incorporate Powder Calculate Projections algorithm here
            print "i: ",str(i)
            percentcpubusy=100*(i+1)/NumActiveWorkspaces #determine % busy
            self.ui.progressBarStatusProgress.setValue(percentcpubusy) #adjust progress bar according to % busy
            time.sleep(0.01)  #seem to need a small delay to ensure that status updates
            progressText="  Projecting workspace: "+self.ui.activeWSNames[i]
            print "progressText: ",progressText
            self.ui.StatusText.append(progressText)
            thisWS=self.ui.activeWSVarsList[i]
            SCCP=np.sum(thisWS,axis=0) #to simulate projection, select an axis to sum along
            #examine thisWS size to see if data look "right"
            print "thisWS shape: ",thisWS.shape," WS name: ",self.ui.activeWSNames[i]," SCCP shape: ",SCCP.shape
            time.sleep(1) #have a 1 second delay to enable viewing progress bar update changes
        self.ui.progressBarStatusProgress.setValue(0) #clear progress bar
		
        #upon successful completion enable Powder Calc Proj button
        self.ui.pushButtonSCCalcProj.setEnabled(True)      
        #for now, just enable the corresponding Save Workspaces button
        self.ui.pushButtonSCSaveWorkspace.setEnabled(True) 
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Single Crystal Calculate Projections Complete")		
		

        
    def Update(self):
        print "** Update "
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Updating Workspace Manager")
        const=constants()

        self.ui.tableWidgetWorkspaces.setEnabled(False)
        self.ui.pushButtonPowderCalcProj.setEnabled(True) 
        self.ui.pushButtonSCCalcProj.setEnabled(False) 
        self.ui.activeWSNames=[]
        table=self.ui.tableWidgetWorkspaces
        #first let's clean up empty rows
        Nrows=table.rowCount()
        roff=0
        for row in range(Nrows):
            item=table.item(row,const.WSM_WorkspaceCol) #need to convert item from Qstring to string for comparison to work
            itemStr=str(item)
            print "itemStr: ",itemStr
            if itemStr == 'None':
                table.removeRow(row-roff)
                roff=roff+1	
        #now let's determine which action to take
        
        if self.ui.radioButtonLoadSingleWorkspace.isChecked():  
            #Load workspaces or groups from files
            
            #open dialog box to select files
            curdir=os.curdir
            filter='*.nxs'
            wsFiles = QtGui.QFileDialog.getOpenFileNames(self, 'Open Workspace(s)', curdir,filter)
            
            
            #for each file selected:
            #  - load mantid workspace
            #  - populate workspace manager table
            Nfiles=len(wsFiles)
            
            table=self.ui.tableWidgetWorkspaces
            
            print "Number of files selected: ",Nfiles
            cntr=1
            for wsfile in wsFiles:
                basename=os.path.basename(str(wsfile))
                fileparts=os.path.splitext(basename)
                wsName=fileparts[0]
                Load(Filename=str(wsfile),OutputWorkspace=wsName)
                #make sure workspaces are available at the python level
                
                
                percentbusy=int(float(cntr)/float(Nfiles)*100)
                self.ui.progressBarStatusProgress.setValue(percentbusy) #adjust progress bar according to % busy
                time.sleep(0.01)  #seem to need a small delay to ensure that status updates
                cntr += 1
                #now populate table
                self.ui.StatusText.append("  Loading workspace:"+str(wsName))
                addWStoTable(table,wsName,wsfile)
                #update table with memory size rather than file size in the Size column of the Workspace Manager
                
                
                
            table.resizeColumnsToContents();
            self.ui.progressBarStatusProgress.setValue(0) #adjust progress bar according to % busy
            
        elif self.ui.radioButtonCreateWSG.isChecked():  
            #envoke the workspace group editor to create a group
            print "*** Launching Workspace Group Editor ***"
            self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Calling Workspace Composer Create Workspace")
            self.child_win = WorkspaceComposer(self)
            self.child_win.show()
            
        elif self.ui.radioButtonSelectAll.isChecked():  
            #set all checkboxes in the workspace manager table
            #first check if there are any rows to update selection
            item=table.item(0,const.WSM_WorkspaceCol) #need to convert item from Qstring to string for comparison to work
            itemStr=str(item)
#            print "itemStr: ",itemStr
            #then only update the rows if rows with content are discovered.
            if itemStr != 'None':
                Nrows=table.rowCount()
                for row in range(Nrows):
                    addCheckboxToWSTCell(table,row,const.WSM_SelectCol,True)            

        elif self.ui.radioButtonClearAll.isChecked():  
            #clear all checkboxes in the workspace manager table
            #first check if there are any rows to update selection
            item=table.item(0,const.WSM_WorkspaceCol) #need to convert item from Qstring to string for comparison to work
            itemStr=str(item)
#            print "itemStr: ",itemStr
            #then only update the rows if rows with content are discovered.
            if itemStr != 'None':
                Nrows=table.rowCount()
                for row in range(Nrows):
                    addCheckboxToWSTCell(table,row,const.WSM_SelectCol,False)          
        elif self.ui.radioButtonEditSelected.isChecked():  
            #edit existing workspace group using the workspace group editor
            self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Calling Workspace Composer Edit Workspace")
            #first need to determine which workspace selected in the workspace manager
            table=self.ui.tableWidgetWorkspaces
            #first let's clean up empty rows
            Nrows=table.rowCount()
            selrow=[]
            for row in range(Nrows):
                #get checkbox status            
                cw=table.cellWidget(row,const.WSM_SelectCol) 
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
                dialog.setText("No workspaces selected to edit")
                dialog.exec_()
                return
            elif len(selrow) > 0:
                #preferred case - just do it
                print "type WSMIndex: ",type(self.ui.WSMIndex)
                for row in selrow:
                    self.ui.WSMIndex.append(row)   #WorkSpaceManager Index gives the row number of that table.  -1 indicates new group to be created
                    self.ui.GWSName.append(str(table.item(row,const.WSM_WorkspaceCol).text()))
                self.child_win = WorkspaceComposer(self)
                self.child_win.show()                    
                
            else:
                print "this case not anticipated...doing nothing"
            
        elif self.ui.radioButtonSaveSelected.isChecked():  
            #save selected workspaces
            table=self.ui.tableWidgetWorkspaces
            #first let's clean up empty rows
            Nrows=table.rowCount()
            selrow=[]
            for row in range(Nrows):
                #get checkbox status            
                cw=table.cellWidget(row-roff,const.WSM_SelectCol) 
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
                    wsname=str(table.item(row,const.WSM_WorkspaceCol).text())
                    
                filter='.nxs'
                wsnamext=wsname+filter
                wspathname = str(QtGui.QFileDialog.getSaveFileName(self, 'Save Workspace', wsnamext,filter))
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
                    table.item(row,const.WSM_SavedCol).setText('Yes')
                    
                    
            elif len(selrow) > 1:
                #when saving more than one file, user selects directory and filenames are automatically generated.

                dialog=QtGui.QMessageBox(self)
                dialog.setText("Multiple files selected to save - user selects the directory to save the files and filenames will be automatically generated")
                dialog.exec_()
                             
                filter='.nxs'
#                wsnamext=wsname+filter
#                wspathname = str(QtGui.QFileDialog.getSaveFileName(self, 'Save Workspace', wsnamext,filter))
                home=getHomeDir()
                wspathname = str(QtGui.QFileDialog.getExistingDirectory(self,'Save Workspaces Directory',home))
                print "Workspace Save: ",wspathname
                
                #check if files already exist
                fcnt=0
                fstat=False
                for row in selrow:
                    wsname=str(str(table.item(row,const.WSM_WorkspaceCol).text()))
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
                    
                if reply == QtGui.QMessageBox.Yes:
                    #case to overwrite files
                    if wspathname != '':
                        #wspathname will be empty if the cancel button was selected on the path dialog.
                        cntr=1
                        for row in selrow:
                            wsname=str(str(table.item(row,const.WSM_WorkspaceCol).text()))
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
                            table.item(row,const.WSM_SavedCol).setText('Yes')
                            cntr += 1

                time.sleep(0.2)
                self.ui.progressBarStatusProgress.setValue(0) 

            else:
                print "this case not anticipated...doing nothing"
            

            
        elif self.ui.radioButtonRemoveSelected.isChecked(): 
            #remove selected workspaces from the application
            
            print "Remove Selected Selected"
            #first check if there are any rows to update selection
            item=table.item(0,const.WSM_WorkspaceCol) #need to convert item from Qstring to string for comparison to work
            itemStr=str(item)
            print "itemStr: ",itemStr
            #then only update the rows if rows with content are discovered.
            if itemStr != 'None':
                Nrows=table.rowCount()
                roff=0
                rcntr=0
                for row in range(Nrows):
                    item=table.item(row-roff,const.WSM_WorkspaceCol)
                    itemStr=str(item)
                    print "itemStr: ",itemStr
                    #then only update the rows if rows with content are discovered.
                    if itemStr != 'None':
                        #get checkbox status            
                        cw=table.cellWidget(row-roff,const.WSM_SelectCol) 
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
                            wsname=str(table.item(row-roff,const.WSM_WorkspaceCol).text())
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
        elif self.ui.radioButtonProcessSelected.isChecked():  
            #case to enable corresponding tabs and buttons according to the workspaces selected
            #can also check for compatibility of workspaces before continuing to process
            pass
        else:
            print "unsupported radiobutton option...doing nothing"
        self.ui.tableWidgetWorkspaces.setEnabled(True)
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Workspace Manager Update Complete")
		
    def performWorkspaceActions(self):
        print "performWorkspaceActions"
        const=constants()
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
            item=table.item(row,const.WSM_WorkspaceCol) #need to convert item from Qstring to string for comparison to work
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
            item=table.item(row,const.WSM_WorkspaceCol) #need to convert item from Qstring to string for comparison to work
            itemStr=str(item)
            print "itemStr: ",itemStr
            if itemStr != 'None':
                itemText=str(table.item(row,const.WSM_WorkspaceCol).text())
                print "row: ",row
                rowComboboxIndex=table.cellWidget(row,const.WSM_ActionCol).currentIndex()
                print "rowAction: ",rowComboboxIndex
                if rowComboboxIndex == 0:
                    print "Load case"
                    NumActiveRows +=1 #increment active workspaces counter
                    #add names of active workspaces to the list - since list is cleared each time this function is called, need to add items each time
                    self.ui.activeWSNames.append(itemText)
                    print "itemText: ",itemText," self.ui.activeWSNames: ",self.ui.activeWSNames
                    #determine if data already loaded, if so, skip load
                    loadStat=str(table.item(row,const.WSM_StatusCol).text())
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
                    table.setItem(row,const.WSM_StatusCol,QtGui.QTableWidgetItem(status)) #Status col=5
                    #if any data are loaded, set cal proj buttons active
                    calcProjFlag +=1

                elif rowComboboxIndex == 1:
                    print "Unload case"
                    loadStat=str(table.item(row,const.WSM_StatusCol).text())
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
                    wkspc=str(table.item(row,const.WSM_WorkspaceCol).text())
                    print "Removing Workspace: ",wkspc
                    loadStat=str(table.item(row,const.WSM_StatusCol).text())
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
            itemText=str(table.item(row,const.WSM_LastAlgCol).text())
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
		
    def pushButtonSCVolPlotSelect(self):
        print "SC Vol Plot Callback"
        #now extract values from this tab
        SCVXcomboIndex=self.ui.comboBoxSCVolX.currentIndex()
        SCVXFrom=self.ui.lineEditSCVolXFrom.text()
        SCVXTo=self.ui.lineEditSCVolXTo.text()
        SCVXStep=self.ui.lineEditSCVolXStep.text()
        SCVYcomboIndex=self.ui.comboBoxSCVolY.currentIndex()
        SCVYFrom=self.ui.lineEditSCVolYFrom.text()
        SCVYTo=self.ui.lineEditSCVolYTo.text()
        SCVYStep=self.ui.lineEditSCVolYStep.text()
        SCVZcomboIndex=self.ui.comboBoxSCVolZ.currentIndex()
        SCVZFrom=self.ui.lineEditSCVolZFrom.text()
        SCVZTo=self.ui.lineEditSCVolZTo.text()
        SCVZStep=self.ui.lineEditSCVolZStep.text()
        SCVEcomboIndex=self.ui.comboBoxSCVolE.currentIndex()
        SCVEFrom=self.ui.lineEditSCVolEFrom.text()
        SCVETo=self.ui.lineEditSCVolETo.text()
        SCVEStep=self.ui.lineEditSCVolEStep.text()
        SCVIntensityFrom=self.ui.lineEditSCVolIntensityFrom.text()
        SCVIntensityTo=self.ui.lineEditSCVolIntensityTo.text()
        SCVSmoothing=self.ui.lineEditSCVolSmoothing.text()
        SCVCTIndex=self.ui.comboBoxSCVolCT.currentIndex()
        print "SC Vol Plot values: ",SCVXcomboIndex,SCVXFrom,SCVXTo,SCVXStep,SCVYcomboIndex,SCVYFrom,SCVYTo,SCVYStep,SCVZcomboIndex,SCVZFrom,SCVZTo,SCVZStep,SCVEcomboIndex,SCVEFrom,SCVETo,SCVEStep,SCVIntensityFrom,SCVIntensityTo,SCVSmoothing,SCVCTIndex
        #**** code to extract data and perform plot placed here
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Single Crystal Sample: Plot Volume")				

    def pushButtonSCVolOplotSelect(self):
        print "SC Vol Oplot Callback"
        #now extract values from this tab
        SCVXcomboIndex=self.ui.comboBoxSCVolX.currentIndex()
        SCVXFrom=self.ui.lineEditSCVolXFrom.text()
        SCVXTo=self.ui.lineEditSCVolXTo.text()
        SCVXStep=self.ui.lineEditSCVolXStep.text()
        SCVYcomboIndex=self.ui.comboBoxSCVolY.currentIndex()
        SCVYFrom=self.ui.lineEditSCVolYFrom.text()
        SCVYTo=self.ui.lineEditSCVolYTo.text()
        SCVYStep=self.ui.lineEditSCVolYStep.text()
        SCVZcomboIndex=self.ui.comboBoxSCVolZ.currentIndex()
        SCVZFrom=self.ui.lineEditSCVolZFrom.text()
        SCVZTo=self.ui.lineEditSCVolZTo.text()
        SCVZStep=self.ui.lineEditSCVolZStep.text()
        SCVEcomboIndex=self.ui.comboBoxSCVolE.currentIndex()
        SCVEFrom=self.ui.lineEditSCVolEFrom.text()
        SCVETo=self.ui.lineEditSCVolETo.text()
        SCVEStep=self.ui.lineEditSCVolEStep.text()
        SCVIntensityFrom=self.ui.lineEditSCVolIntensityFrom.text()
        SCVIntensityTo=self.ui.lineEditSCVolIntensityTo.text()
        SCVSmoothing=self.ui.lineEditSCVolSmoothing.text()
        SCVCTIndex=self.ui.comboBoxSCVolCT.currentIndex()
        print "SC Vol Oplot values: ",SCVXcomboIndex,SCVXFrom,SCVXTo,SCVXStep,SCVYcomboIndex,SCVYFrom,SCVYTo,SCVYStep,SCVZcomboIndex,SCVZFrom,SCVZTo,SCVZStep,SCVEcomboIndex,SCVEFrom,SCVETo,SCVEStep,SCVIntensityFrom,SCVIntensityTo,SCVSmoothing,SCVCTIndex
		
        #**** code to extract data and perform plot placed here
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Single Crystal Sample: Oplot Volume")				
		
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

		
    def pushButtonPowderCutOplotSelect(self):
        print "Powder Cut Oplot Callback"
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
        print "Powder Cut Oplot Values: ",PCAIndex,PCAFrom,PCATo,PCAStep,PCTIndex,PCTFrom,PCTTo,PCYIndex,PCYFrom,PCYTo
        #**** code to extract data and perform oplot placed here		
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Powder Sample: Oplot Cut")				

		
    def pushButtonSCSlicePlotSliceSelect(self):
        print "Single Crystal Plot Slice Button pressed"
        #now extract values from this tab
        SCSXcomboIndex=self.ui.comboBoxSCSliceX.currentIndex()
        SCSXFrom=self.ui.lineEditSCSliceXFrom.text()
        SCSXTo=self.ui.lineEditSCSliceXTo.text()
        SCSXStep=self.ui.lineEditSCSliceXStep.text()
        SCSYcomboIndex=self.ui.comboBoxSCSliceY.currentIndex()
        SCSYFrom=self.ui.lineEditSCSliceYFrom.text()
        SCSYTo=self.ui.lineEditSCSliceYTo.text()
        SCSYStep=self.ui.lineEditSCSliceYStep.text()
        SCSEcomboIndex=self.ui.comboBoxSCSliceE.currentIndex()
        SCSEFrom=self.ui.lineEditSCSliceEFrom.text()
        SCSETo=self.ui.lineEditSCSliceETo.text()
        SCSIntensityFrom=self.ui.lineEditSCSliceIntensityFrom.text()
        SCSIntensityTo=self.ui.lineEditSCSliceIntensityTo.text()
        SCSSmoothing=self.ui.lineEditSCSliceSmoothing.text()
        SCSEcomboIndex=self.ui.comboBoxSCSliceE.currentIndex()
        SCSThickFrom=self.ui.lineEditSCSliceEFrom.text()
        SCSThickTo=self.ui.lineEditSCSliceETo.text()
        SCSCTcomboIndex=self.ui.comboBoxSCSliceCT.currentIndex()
        print "SC Plot values: ",SCSXcomboIndex,SCSXFrom,SCSXTo,SCSXStep,SCSYcomboIndex,SCSYFrom,SCSYTo,SCSYStep,SCSEcomboIndex,SCSEFrom,SCSETo,SCSIntensityFrom,SCSIntensityTo,SCSSmoothing
        print "  More SC Plot values: ",SCSEcomboIndex,SCSThickFrom,SCSThickTo,SCSCTcomboIndex
        #**** code to extract data and perform plot placed here
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Single Crystal Sample: Show Slice")				

		
    def pushButtonSCSliceOplotSliceSelect(self):
        print "Single Crystal Oplot Slice Button pressed"
        #now extract values from this tab
        SCSXcomboIndex=self.ui.comboBoxSCSliceX.currentIndex()
        SCSXFrom=self.ui.lineEditSCSliceXFrom.text()
        SCSXTo=self.ui.lineEditSCSliceXTo.text()
        SCSXStep=self.ui.lineEditSCSliceXStep.text()
        SCSYcomboIndex=self.ui.comboBoxSCSliceY.currentIndex()
        SCSYFrom=self.ui.lineEditSCSliceYFrom.text()
        SCSYTo=self.ui.lineEditSCSliceYTo.text()
        SCSYStep=self.ui.lineEditSCSliceYStep.text()
        SCSEcomboIndex=self.ui.comboBoxSCSliceE.currentIndex()
        SCSEFrom=self.ui.lineEditSCSliceEFrom.text()
        SCSETo=self.ui.lineEditSCSliceETo.text()
        SCSIntensityFrom=self.ui.lineEditSCSliceIntensityFrom.text()
        SCSIntensityTo=self.ui.lineEditSCSliceIntensityTo.text()
        SCSSmoothing=self.ui.lineEditSCSliceSmoothing.text()
        SCSEcomboIndex=self.ui.comboBoxSCSliceE.currentIndex()
        SCSThickFrom=self.ui.lineEditSCSliceEFrom.text()
        SCSThickTo=self.ui.lineEditSCSliceETo.text()
        SCSCTcomboIndex=self.ui.comboBoxSCSliceCT.currentIndex()
        print "SC Oplot values: ",SCSXcomboIndex,SCSXFrom,SCSXTo,SCSXStep,SCSYcomboIndex,SCSYFrom,SCSYTo,SCSYStep,SCSEcomboIndex,SCSEFrom,SCSETo,SCSIntensityFrom,SCSIntensityTo,SCSSmoothing
        print "  More SC Oplot values: ",SCSEcomboIndex,SCSThickFrom,SCSThickTo,SCSCTcomboIndex
        #**** code to extract data and perform plot placed here
        self.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Single Crystal Sample: Oplot Slice")				

		
    def pushButtonSCSliceSurfaceSliceSelect(self):
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
        const=constants()
        
        table=self.ui.tableWidgetWorkspaces
        #first let's clean up empty rows
        Nrows=table.rowCount()
        for row in range(Nrows):
            cw=table.cellWidget(row,const.WSM_SelectCol) 
            cbstat=cw.isChecked()
            #check if this workspace is selected for display
            if cbstat == True:
                #case where it is selected
                #get workspace
                wsitem=str(table.item(row,const.WSM_WorkspaceCol).text())
                print " wsitem:",wsitem
                print " mtd.getObjectNames():",mtd.getObjectNames()
                ws=mtd.retrieve(wsitem)
    
                wsX=ws.getXDimension()
                wsY=ws.getYDimension()
                
                xmin=wsX.getMinimum()
                xmax=wsX.getMaximum()
                
                ymin=wsY.getMinimum()
                ymax=wsY.getMaximum()
                
                xname= wsX.getName()
                yname= wsY.getName()
                
                ad0=xname+','+str(xmin)+','+str(xmax)+',100'
                ad1=yname+','+str(ymin)+','+str(ymax)+',100'
                
                MDH=BinMD(InputWorkspace=ws,AlignedDim0=ad0,AlignedDim1=ad1)
                sig=MDH.getSignalArray()
                ne=MDH.getNumEventsArray()
#                dne=sig/ne
                dne=sig
                
                
                #Incorporate SliceViewer here
                sv = SliceViewer()
                label='Python Only SliceViewer'
                #hard coded workspace for demo purpose - needs to be changed to dynamically pick up workspace
#                LoadMD(filename=r'C:\Users\mid\Documents\Mantid\Powder\CalcProj\zrh_1000_PCalcProj.nxs',OutputWorkspace='ws')
#                sv.LoadData('ws',label)
                
#                exec ("%s = mtd.retrieve(%r)" % (outname,outname))
                
                sv.LoadData(wsitem,label)
                xydim=None
                slicepoint=None
                colormin=None
                colormax=None
                colorscalelog=False
                limits=None
                normalization=1
                sv.SetParams(xydim,slicepoint,colormin,colormax,colorscalelog,limits, normalization)
                sv.Show()
                
#                figure(1)
#                imshow(flipud(sig))
                
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
                
                
        show()
        
        
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
        const=constants()
        #disable load until another set of files has been selected
        self.ui.pushButtonCreateWorkspace.setEnabled(False)
		
        #set some initial progress on the meter
        self.ui.progressBarStatusProgress.setValue(10)

        #get output filename first
        wsname=self.ui.lineEditWorkspaceName.text()
        filter='.nxs'
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
            col=const.CWS_ScaleFactorCol
            scale=self.ui.tableWidget.item(row,col)
            print "Scale: ", scale.text()
            #scale cannot be edited once a file is loaded
            self.ui.tableWidget.item(row,col).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)	
            #change the item status to 'Loaded'
            col=const.CWS_StatusCol
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
			

        
#************* beginning of global functions and classes ****************

class constants:
    def __init__(self):
#        self.WSM_WorkspaceCol=0
#        self.WSM_LastAlgCol=1
#        self.WSM_LocationCol=2
#        self.WSM_DateCol=3
#        self.WSM_SizeCol=4
#        self.WSM_ActionCol=5
#        self.WSM_StatusCol=6
        self.WSM_WorkspaceCol=0
        self.WSM_TypeCol=1
        self.WSM_SavedCol=2
        self.WSM_SizeCol=3
        self.WSM_SelectCol=4

        
        self.CWS_FilenameCol=0
        self.CWS_DateCol=1
        self.CWS_TypeCol=2
        self.CWS_SizeCol=3
        self.CWS_ScaleFactorCol=4
        self.CWS_StatusCol=5
        

def constantUpdateActor(self):
    const=constants()
    #mode to show status in percentage
    cpu_stats = psutil.cpu_times_percent(interval=1,percpu=False)
    percentcpubusy = 100.0 - cpu_stats.idle
    self.ui.progressBarStatusCPU.setValue(percentcpubusy)
    percentmembusy=psutil.virtual_memory().percent
    self.ui.progressBarStatusMemory.setValue(percentmembusy)
    Ncpus=len(psutil.cpu_percent(percpu=True))
    totalcpustr='CPU Count: '+str(Ncpus)
#        print "Total CPU str: ",totalcpustr
    self.ui.labelCPUCount.setText(totalcpustr)
    totalmem=int(round(float(psutil.virtual_memory().total)/(1024*1024*1024)))
#        print "Total Mem: ",totalmem
    totalmemstr='Max Mem: '+str(totalmem)+' GB'
#        print "Total Mem str: ",totalmemstr
    self.ui.labelMaxMem.setText(totalmemstr)
				
def getHomeDir():
        if sys.platform == 'win32':
            home = expanduser("~")
        else:
            home=os.getenv("HOME")
        return home
    
def addCheckboxToWSTCell(table,row,col,state):
    
    if state == '':
        state=False
    
    checkbox = QtGui.QCheckBox()
    checkbox.setText('Select')
    checkbox.setChecked(state)
    
    #adding a widget which will be inserted into the table cell
    #then centering the checkbox within this widget which in turn,
    #centers it within the table column :-)
    QW=QtGui.QWidget()
    cbLayout=QtGui.QHBoxLayout(QW)
    cbLayout.addWidget(checkbox)
    cbLayout.setAlignment(QtCore.Qt.AlignCenter)
    cbLayout.setContentsMargins(0,0,0,0)
    
    table.setCellWidget(row,col, checkbox) #if just adding the checkbox directly
#    table.setCellWidget(row,col, QW)


def addmemWStoTable(table,wsname,wstype,wssize,wsindex):
    
    #get constants
    const=constants()

    
    if wstype == '':
        wstype = 'unknown'

    saved='No'
    
    #First determine if there is an open row
    #need to determine the available row number in the workspace table
    
    Nrows=table.rowCount()
    print "Nrows: ",Nrows,"  wsindex: ",wsindex

    #check if the row index supplied is >= to the number of rows
    #if so, add a row
    if wsindex >= Nrows:  #check if we need to add a row or not
        #case to insert
        table.insertRow(Nrows)
    col=const.WSM_SelectCol
#        addComboboxToWSTCell(table,userow,col)
    addCheckboxToWSTCell(table,wsindex,col,True)
    
    #now add the row
    userow=wsindex		
    print "userow: ",userow
    table.setItem(userow,const.WSM_WorkspaceCol,QtGui.QTableWidgetItem(wsname)) #Workspace Name 
    table.setItem(userow,const.WSM_TypeCol,QtGui.QTableWidgetItem(wstype)) #Workspace Type
    table.setItem(userow,const.WSM_SavedCol,QtGui.QTableWidgetItem(saved)) #FIXXME Hard coded for now
    table.setItem(userow,const.WSM_SizeCol,QtGui.QTableWidgetItem(wssize)) #Size 
    addCheckboxToWSTCell(table,userow,const.WSM_SelectCol,True)
#    table.setItem(userow,const.WSM_SelectCol,QtGui.QTableWidgetItem('')) #select - will want to change this

       	
def addWStoTable(table,workspaceName,workspaceLocation):
    #function to add a single workspace to the workspace manager table
	# workspaces may originate from create workspace or the list of files
    print "addWStoTable workspaceName: ",workspaceName
    print "workspaceLocation: ",workspaceLocation
    
    #get constants
    const=constants()

    #then get info about the workspace file
#    ws_date=str(time.ctime(os.path.getctime(workspaceLocation)))
#    ws_size=str(int(round(float(os.stat(workspaceLocation).st_size)/(1024*1024))))+' MB'
    ws_size=getWorkspaceMemSize(workspaceName)
    
    #also need the Mantid Algorithm used to create the workspace
    #for now, this will be obtained by reading the workspace as an HDF file and
    #extracting the algorithm information.

#    h5WS=h5py.File(str(workspaceLocation),'r')
#    WSAlg=getReduceAlgFromH5Workspace(h5WS)
    
    WSAlg=getReduceAlgFromWorkspace(workspaceName)

    
    if WSAlg == "":
        WSAlg="Not Available"
    

    #two cases of rows:
    #    1. Case where all or some rows are empty and just add directly to first available row
	#    2. Case where all rows have content and need to add a row in this case
	
    #First determine if there is an open row
    #need to determine the available row number in the workspace table
    
    Nrows=table.rowCount()
    print "Nrows: ",Nrows

    emptyRowCnt=0
    emptyRows = []
	
    for row in range(Nrows):
        item=str(table.item(row,0)) 
        if item == 'None':
            emptyRowCnt +=1
            emptyRows.append(row)
    print "emptyRows: ",emptyRows,"  emptyRowCnt: ",emptyRowCnt
    if emptyRowCnt != 0:
        #case where there is an empty row to use
        userow=int(emptyRows[0])
    else:
        #case where a row needs to be added
        userow=Nrows #recall that row indexing starts at zero thus the row to add would be at position Nrows
        table.insertRow(Nrows)
        col=4
#        addComboboxToWSTCell(table,userow,col)
        addCheckboxToWSTCell(table,userow,col,True)

    #now add the row		
    table.setItem(userow,const.WSM_WorkspaceCol,QtGui.QTableWidgetItem(workspaceName)) #Workspace Name 
    table.setItem(userow,const.WSM_TypeCol,QtGui.QTableWidgetItem(WSAlg)) #Workspace Type
    table.setItem(userow,const.WSM_SavedCol,QtGui.QTableWidgetItem('yes')) #FIXXME Hard coded for now
    table.setItem(userow,const.WSM_SizeCol,QtGui.QTableWidgetItem(ws_size)) #Size 
    table.setItem(userow,const.WSM_SelectCol,QtGui.QTableWidgetItem('')) #select - will want to change this

		
if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    msliceapp = MSlice()
    msliceapp.show()

    sys.exit(app.exec_())