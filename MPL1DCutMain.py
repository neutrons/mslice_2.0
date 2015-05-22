import sys, os
import copy

from ui_MPL1DCut import *
from PyQt4 import Qt, QtCore, QtGui
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
#ignore potential matplotlib backend selection warnings as the backend may already be selected when running via mantidplot
import warnings
warnings.filterwarnings('ignore',category=UserWarning)
"""
#backend_qt4 should alreadt be loaded from the main MSLice app
import matplotlib
if matplotlib.get_backend() != 'QT4Agg':
    matplotlib.use('QT4Agg')
"""
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar


import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from MSliceHelpers import *
from os.path import basename

#import Mantid computatinal modules
sys.path.append(os.environ['MANTIDPATH'])
from mantid.simpleapi import * 

from MPLPowderCutHelpers import *
from MPLSCCutHelpers import *
from MPL1DCutHelpers import *

from LegendManager import *

class MPL1DCut(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MPL1DCutMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("1D Cut")
        self.parent=parent 
        
        #establish signals and slots
        QtCore.QObject.connect(self.ui.MPLpushButtonLegendEdit, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.LegendEdit)
        QtCore.QObject.connect(self.ui.MPLcomboBoxErrorColor, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.ShowEBars)
        QtCore.QObject.connect(self.ui.MPLpushButtonImportData, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.DoImport)
        QtCore.QObject.connect(self.ui.MPLpushButtonPlot, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.DoPlot)
        QtCore.QObject.connect(self.ui.MPLpushButtonOPlot, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.DoOPlot)
        QtCore.QObject.connect(self.ui.MPLpushButtonPlaceText, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.DoAnnotate)
        QtCore.QObject.connect(self.ui.MPLpushButtonRemoveText, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.RemText)
        QtCore.QObject.connect(self.ui.MPLpushButtonPlaceArrow, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.DoArrow)
        QtCore.QObject.connect(self.ui.MPLpushButtonRemoveArrow, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.RemArrow)
        QtCore.QObject.connect(self.ui.MPLpushButtonPopPlot, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.PopPlot)
        QtCore.QObject.connect(self.ui.MPLpushButtonSaveASCII, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.SaveASCII)
        QtCore.QObject.connect(self.ui.MPLpushButtonSaveHistory, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.SaveHistory)
        QtCore.QObject.connect(self.ui.MPLpushButtonSavePlotWS, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.SavePlotWS)
        QtCore.QObject.connect(self.ui.MPLpushButtonDone, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.Done)
        
        QtCore.QObject.connect(self.ui.MPLpushButtonResetParams, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.ResetParams)
        #set reset flag status to false
        self.ui.ResetParams=False
        
        #History Tab
        QtCore.QObject.connect(self.ui.MPLpushButtonUpdateHistory, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.UpdateHistory)
        QtCore.QObject.connect(self.ui.MPLcheckBoxExpandAll, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.ExpandAll)
        
        #Comment Tab
        QtCore.QObject.connect(self.ui.MPLpushButtonSaveComments, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.UpdateComments)
        QtCore.QObject.connect(self.ui.MPLcheckBoxReadOnly, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.ReadOnly)
        
        QtCore.QObject.connect(self.ui.MPLcomboBoxActiveWorkspace, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.SelectWorkspace)
        
        #change show error bars text using greek char for sigma
        #need to set the Greek characters using unicode format as the global style sheet seems to be overriding setting the font for these labels.
        SYMBOLIC_BASE = 880  #offset into the unicode font set to the Symbolic, or in this case, Greek and Coptic alphabet - see here: http://www.alanwood.net/unicode/fontsbyrange.html 
        self.ui.checkBoxErrorBars.setText('Show Error Bars as +'+unichr(SYMBOLIC_BASE + 83)+' and -'+unichr(SYMBOLIC_BASE + 83))
        self.ui.checkBoxErrorBars.setChecked(True)
        
        #now that the widget has been established, copy over values from MSlice
        #Workspace List and insert them into the MPLcomboBoxActiveWorkspace combo box
        
        #get the list of workspaces
        wslist=self.parent.ui.wslist
        print "wslist: ",wslist
        
        #now need to parse workspaces to determine which are grouped workspaces to list each workspace separately in the plot GUI
        Nws=len(wslist)
        wstotlist=[]
        for n in range(Nws):
            __tmpws=mtd.retrieve(wslist[n])
            wstotlist.append(wslist[n])
            
            """
            #believe this code block is a vestage for when workspaces within a group were processed separately. 
            if 'Group' in str(type(__tmpws)):
            #case to get all workspace names from the group
                for __ws in __tmpws:
                    wstotlist.append(__ws.name())
            else:
                #case we just have a single workspace
                wstotlist.append(wslist[n])
            """
        
        print "Total number of workspaces passed to 1D Cut: ",wstotlist
        #now put workspaces into workspace combo box
        Nws=len(wstotlist)
        for n in range(Nws):
            if n == 0:
                #case to use the existing row in the combo box
                self.ui.MPLcomboBoxActiveWorkspace.setItemText(n,str(wstotlist[n]))
            else:
                #case to add rows to insert workspace names
                self.ui.MPLcomboBoxActiveWorkspace.insertItem(n,wstotlist[n])
                
            #Also need to add any newly created workspaces back into the MSlice Workspace Manager
            #workspaceLocation=''
            table=self.parent.ui.tableWidgetWorkspaces
            workspaceLocation=''
            addWStoTable(table,wstotlist[n],workspaceLocation)    
        
        #update Comments tab while we're working with the workspace lists
        self.getComments()        
        
        if self.parent.ui.mode1D == 'Powder':
            
            #parent mode could change, set the mode for this current GUI
            self.ui.mode='Powder'
            
            #set stackedWidgetCut index
            self.ui.stackedWidgetCut.setCurrentIndex(0)
            #Data Formatting - copy powder parameters over from MSlice main application
            self.ui.MPLlineEditPowderCutAlongFrom.setText(self.parent.ui.lineEditPowderCutAlongFrom.text())
            self.ui.MPLlineEditPowderCutAlongTo.setText(self.parent.ui.lineEditPowderCutAlongTo.text())
            self.ui.MPLlineEditPowderCutAlongStep.setText(self.parent.ui.lineEditPowderCutAlongStep.text())
            
            self.ui.MPLlineEditPowderCutThickFrom.setText(self.parent.ui.lineEditPowderCutThickFrom.text())
            self.ui.MPLlineEditPowderCutThickTo.setText(self.parent.ui.lineEditPowderCutThickTo.text())
            
            self.ui.MPLlineEditPowderCutYFrom.setText(self.parent.ui.lineEditPowderCutYFrom.text())
            self.ui.MPLlineEditPowderCutYTo.setText(self.parent.ui.lineEditPowderCutYTo.text())
            
            indx_Along=self.parent.ui.comboBoxPowderCutAlong.currentIndex()
            indx_Thick=self.parent.ui.comboBoxPowderCutThick.currentIndex()
            indx_Y=self.parent.ui.comboBoxPowderCutY.currentIndex()
            self.ui.MPLcomboBoxPowderCutAlong.setCurrentIndex(indx_Along)
            self.ui.MPLcomboBoxPowderCutThick.setCurrentIndex(indx_Thick)
            self.ui.MPLcomboBoxPowderCutY.setCurrentIndex(indx_Y)
        elif self.parent.ui.mode1D == 'SC':
            
            #parent mode could change, set the mode for this current GUI
            self.ui.mode='SC'
            
            #set stackedWidgetCut index
            self.ui.stackedWidgetCut.setCurrentIndex(1)
            #transfer MSlice main app parameters to this GUI app
            
            self.ui.lineEditSCCutXFrom.setText(self.parent.ui.lineEditSCCutXFrom.text())
            self.ui.lineEditSCCutXTo.setText(self.parent.ui.lineEditSCCutXTo.text())
            self.ui.lineEditSCCutXStep.setText(self.parent.ui.lineEditSCCutXStep.text())
            self.ui.lineEditSCCutYFrom.setText(self.parent.ui.lineEditSCCutYFrom.text())
            self.ui.lineEditSCCutYTo.setText(self.parent.ui.lineEditSCCutYTo.text())
            self.ui.lineEditSCCutZFrom.setText(self.parent.ui.lineEditSCCutZFrom.text())
            self.ui.lineEditSCCutZTo.setText(self.parent.ui.lineEditSCCutZTo.text())
            self.ui.lineEditSCCutEFrom.setText(self.parent.ui.lineEditSCCutEFrom.text())
            self.ui.lineEditSCCutETo.setText(self.parent.ui.lineEditSCCutETo.text())
            self.ui.lineEditSCCutIntensityFrom.setText(self.parent.ui.lineEditSCCutIntensityFrom.text())
            self.ui.lineEditSCCutIntensityTo.setText(self.parent.ui.lineEditSCCutIntensityTo.text())
            self.ui.comboBoxSCCutX.setCurrentIndex(self.parent.ui.comboBoxSCCutX.currentIndex())
            self.ui.comboBoxSCCutY.setCurrentIndex(self.parent.ui.comboBoxSCCutY.currentIndex())
            self.ui.comboBoxSCCutZ.setCurrentIndex(self.parent.ui.comboBoxSCCutZ.currentIndex())
            self.ui.comboBoxSCCutE.setCurrentIndex(self.parent.ui.comboBoxSCCutE.currentIndex())
            self.ui.comboBoxSCCutIntensity.setCurrentIndex(self.parent.ui.comboBoxSCCutIntensity.currentIndex())
        else:
            #unsupported mode - complain"
            print "Unsupported GUI mode - returning"
            return
               
        #Plot Configuration
        self.ui.MPLlineEditLabelsIntensity.setText(self.parent.ui.lineEditLabelsIntensity.text())
        self.ui.MPLlineEditLabelsTitle.setText(self.parent.ui.lineEditLabelsTitle.text())
        self.ui.MPLlineEditLabelsLegend.setText(self.parent.ui.lineEditLabelsLegend.text())
        
        self.ui.ax=None
        
        #Place Matplotlib figure within the GUI frame
        #create drawing canvas
        # a figure instance to plot on
        
        matplotlib.rc_context({'toolbar':True})
        self.shadowFigure = plt.figure()
        plt.figure(self.shadowFigure.number)
        self.figure = plt.figure()
        #format the drawing area size
        plt.gcf().subplots_adjust(bottom=0.15)
        plt.gcf().subplots_adjust(left=0.13)
        plt.gcf().subplots_adjust(right=0.95)
        plt.subplot(111).grid(True)
        
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.shadowCanvas=FigureCanvas(self.shadowFigure)
        self.shadowCanvas.set_window_title('Popout Figure')
        self.canvas = FigureCanvas(self.figure)
        
        #add Navigation Toolbar
        self.navigation_toolbar = NavigationToolbar(self.canvas, self)
        self.shadow_navigation_toolbar = NavigationToolbar(self.shadowCanvas, self.shadowCanvas)
        
        layout=QtGui.QVBoxLayout(self.ui.MPLframe)
        layout.addWidget(self.canvas)
        layout.addWidget(self.navigation_toolbar, 0)
        self.layout=layout

        self.doOPlot=False  #initialize to do plot (rather than oplot)
        
        self.doAnnotate=False #flag used to annotate text on plots
        self.doArrow=False #flag used to place arrows on plots
        
        #select Plot as the default tab
        self.ui.MPLtabWidgetPlotHistory.setCurrentIndex(0)
        
        #perform initiations for single crystal plot cut
        #need to deepcopy the ViewSCCDict dictionary over
        #copying this dictionary enable each instance of MPL1DCut to operate 
        #independently without stepping on other instances of itself
        self.ui.ViewSCCDict=copy.deepcopy(self.parent.ui.ViewSCCDict)
        
        #Define signal/slot for changing View Data combo box selections
        QtCore.QObject.connect(self.ui.comboBoxSCCutX, QtCore.SIGNAL('currentIndexChanged(int)'),self.UpdateComboSCCX)
        QtCore.QObject.connect(self.ui.comboBoxSCCutY, QtCore.SIGNAL('currentIndexChanged(int)'),self.UpdateComboSCCY)
        QtCore.QObject.connect(self.ui.comboBoxSCCutZ, QtCore.SIGNAL('currentIndexChanged(int)'),self.UpdateComboSCCZ)
        QtCore.QObject.connect(self.ui.comboBoxSCCutE, QtCore.SIGNAL('currentIndexChanged(int)'),self.UpdateComboSCCE)
        self.ui.ViewSCCDataDeBounce=False #need a debouncing flag since we're generating two index changed events: one for using the mouse to select the combobox item, 
        #and a second for programmatically changing the current index when updating the ViewSCCDict.  Skip the second update...

        #Define signal/slot for handling SCXNpts and SCYNpts calculations upon value changes
        QtCore.QObject.connect(self.ui.lineEditSCCutXFrom, QtCore.SIGNAL('textChanged(QString)'),self.updateSCCNpts)
        QtCore.QObject.connect(self.ui.lineEditSCCutXTo, QtCore.SIGNAL('textChanged(QString)'),self.updateSCCNpts)
        QtCore.QObject.connect(self.ui.lineEditSCCutXStep, QtCore.SIGNAL('textChanged(QString)'),self.updateSCCNpts)
        #QtCore.QObject.connect(self.ui.lineEditSCCutYFrom, QtCore.SIGNAL('textChanged(QString)'),self.updateSCCNpts)
        #QtCore.QObject.connect(self.ui.lineEditSCCutYTo, QtCore.SIGNAL('textChanged(QString)'),self.updateSCCNpts)
        
        #Also need to copy comboBox labels over from Main GUI 
        for i in range(4):
            self.ui.comboBoxSCCutX.setItemText(i, self.parent.ui.comboBoxSCCutX.itemText(i))
            self.ui.comboBoxSCCutY.setItemText(i, self.parent.ui.comboBoxSCCutY.itemText(i))
            self.ui.comboBoxSCCutZ.setItemText(i, self.parent.ui.comboBoxSCCutZ.itemText(i))
            self.ui.comboBoxSCCutE.setItemText(i, self.parent.ui.comboBoxSCCutE.itemText(i))
        #then set the comboBoxes to the correct indicies according to the main app
        self.ui.comboBoxSCCutX.setCurrentIndex(self.parent.ui.comboBoxSCCutX.currentIndex())
        self.ui.comboBoxSCCutY.setCurrentIndex(self.parent.ui.comboBoxSCCutY.currentIndex())
        self.ui.comboBoxSCCutZ.setCurrentIndex(self.parent.ui.comboBoxSCCutZ.currentIndex())
        self.ui.comboBoxSCCutE.setCurrentIndex(self.parent.ui.comboBoxSCCutE.currentIndex())
        
        #copy over step size
        self.ui.lineEditSCCutXStep.setText(self.parent.ui.lineEditSCCutXStep.text())
        #set Bin Width as the default
        self.ui.radioButtonSCBinWidth.setChecked(True)
        #calculate and display the number of bins corresponding to the bin width
                
        self.ui.pushButtonSCCShowParams.click()
        QtCore.QObject.connect(self.ui.comboBoxSCCutX, QtCore.SIGNAL('currentIndexChanged(int)'),self.updateSCCNpts)
        self.updateSCCNpts()
        QtCore.QObject.connect(self.ui.lineEditSCCutXNbins, QtCore.SIGNAL('textChanged(QString)'),self.updateSCCBW)
        
        
        #setup callbacks for SC Cut push buttons - Plot and Oplot 
        #QtCore.QObject.connect(self.ui.pushButtonSCCutPlot, QtCore.SIGNAL('clicked(bool)'), self.pushButtonSCCutPlotSelect)
        QtCore.QObject.connect(self.ui.pushButtonSCCShowParams, QtCore.SIGNAL('clicked(bool)'), self.pushButtonSCCShowParamsSelect)
        

        
        #Launch plot in bringing up the application
        if self.parent.ui.mode1D == 'Powder':
            #initiate powder plot
            self.DoPlot()
            pass
        elif self.parent.ui.mode1D == 'SC':
            #initiate SC plot
            self.DoPlot()
            pass
        else:
            #unsupported mode - complain"
            print "Unsupported GUI mode - returning"
            return        
        
    
    def SelectWorkspace(self):
        #Note that this method is called if current index is changed for
        #MPLcomboBoxActiveWorkspace, such as when adding a workspace to the 
        #MPL dropdown list of available 1D workspaces
        
        #get selected workspace
        wsindx=self.ui.MPLcomboBoxActiveWorkspace.currentIndex()
        self.ui.MPLcurrentWS=str(self.ui.MPLcomboBoxActiveWorkspace.currentText())
        if self.ui.MPLcurrentWS=='':
            #case where we do not have a workspace
            return
        else:
            
            #now check if it's a 2D or 1D workspace - need to make sure that Data Formatting is enabled for 2D and disabled for 1D
            __ws=mtd.retrieve(self.ui.MPLcurrentWS)
            NXbins=__ws.getXDimension().getNBins()
            NYbins=__ws.getYDimension().getNBins()
            print "NXbins: ",NXbins,"  NYbins: ",NYbins
            if NXbins > 1 and NYbins > 1:
                #case for a 2D workspace - enable Data Formatting
                print "Enabling Data Formatting"
                self.ui.MPLgroupBoxDataFormat.setEnabled(True)
            else:
                # 1D case to disable Data Formatting
                print "Disabling Data Formatting"
                self.ui.MPLgroupBoxDataFormat.setEnabled(False)
                #set1DBinVals(self,__ws) #commented out temporarily - needed for placing powder params on MPL GUI
                self.pushButtonSCCShowParamsSelect()
        
        #update the selected workspace label in the comments tab
        self.getComments()
                
        print "Selected Workspace: ",self.ui.MPLcurrentWS

    def pushButtonSCCShowParamsSelect(self):
        #Utility function to transfer values from ViewSCCDict into the 
        #corresponding view fields in the Cut GUI
        ViewSCCDict=self.ui.ViewSCCDict
        
        label=convertIndexToLabel(self,'X','Cut')    
        if ViewSCCDict[label]['from'] != '':                
            SCSXFrom = str("%.3f" % ViewSCCDict[label]['from'])
            self.ui.lineEditSCCutXFrom.setText(SCSXFrom)

        label=convertIndexToLabel(self,'X','Cut')   
        if ViewSCCDict[label]['to'] != '':      
            SCSXTo = str("%.3f" % ViewSCCDict[label]['to'])
            self.ui.lineEditSCCutXTo.setText(SCSXTo)
        
        label=convertIndexToLabel(self,'Y','Cut')    
        if ViewSCCDict[label]['from'] != '':
            SCSYFrom = str("%.3f" % ViewSCCDict[label]['from'])
            self.ui.lineEditSCCutYFrom.setText(SCSYFrom)
        
        label=convertIndexToLabel(self,'Y','Cut')
        if ViewSCCDict[label]['to'] != '':
            SCSYTo = str("%.3f" % ViewSCCDict[label]['to'])
            self.ui.lineEditSCCutYTo.setText(SCSYTo)
        
        label=convertIndexToLabel(self,'Z','Cut')     
        if ViewSCCDict[label]['from'] != '':
            SCSZFrom = str("%.3f" % ViewSCCDict[label]['from'])
            self.ui.lineEditSCCutZFrom.setText(SCSZFrom)
        
        label=convertIndexToLabel(self,'Z','Cut')
        if ViewSCCDict[label]['to'] != '':
            SCSZTo = str("%.3f" % ViewSCCDict[label]['to'])  
            self.ui.lineEditSCCutZTo.setText(SCSZTo)
        
        label=convertIndexToLabel(self,'E','Cut')                    
        if ViewSCCDict[label]['from'] != '':
            SCSEFrom = str("%.3f" % ViewSCCDict[label]['from'])    
            self.ui.lineEditSCCutEFrom.setText(SCSEFrom)
        
        label=convertIndexToLabel(self,'E','Cut')  
        if ViewSCCDict[label]['to'] != '':
            SCSETo = str("%.3f" % ViewSCCDict[label]['to'])       
            self.ui.lineEditSCCutETo.setText(SCSETo)

    def UpdateViewSCCDict(self):
        print "In UpdateViewSCCDict(self)"
        #This method updates the ViewSCCDict dictionary any time that a value
        #is changed in the Viewing Axes field changes.  As this can be performed quickly,
        #the entire dictionary is update when a selction is made in lieu of having a
        #separate method for each of the 12 fields that can change.
        
        #Note that currently only the dictionary labels are updated and that
        #other parameters are updated once SC calc projections occurs
        
        ViewSCCDict=self.ui.ViewSCCDict #for convenience and readability, shorten the name 
        
        #get updated labels
        nameLst=makeSCNames(self)
        #put labels in the View dictionary
        ViewSCCDict['u1']['label']=nameLst[0]
        ViewSCCDict['u2']['label']=nameLst[1]
        ViewSCCDict['u3']['label']=nameLst[2]
        #note that 'E' label does not change...
        #store label changes back into the global dictionary
        self.ui.ViewSCCDict=ViewSCCDict
        
        #update corresponding ViewSCData labels - X
        self.ui.comboBoxSCCutX.setItemText(0,ViewSCCDict['u1']['label'])
        self.ui.comboBoxSCCutX.setItemText(1,ViewSCCDict['u2']['label'])
        self.ui.comboBoxSCCutX.setItemText(2,ViewSCCDict['u3']['label'])
        self.ui.comboBoxSCCutX.setItemText(3,ViewSCCDict['E']['label'])
        #update corresponding ViewSCData labels - Y
        self.ui.comboBoxSCCutY.setItemText(0,ViewSCCDict['u1']['label'])
        self.ui.comboBoxSCCutY.setItemText(1,ViewSCCDict['u2']['label'])
        self.ui.comboBoxSCCutY.setItemText(2,ViewSCCDict['u3']['label'])
        self.ui.comboBoxSCCutY.setItemText(3,ViewSCCDict['E']['label'])
        #update corresponding ViewSCData labels - Z
        self.ui.comboBoxSCCutZ.setItemText(0,ViewSCCDict['u1']['label'])
        self.ui.comboBoxSCCutZ.setItemText(1,ViewSCCDict['u2']['label'])
        self.ui.comboBoxSCCutZ.setItemText(2,ViewSCCDict['u3']['label'])
        self.ui.comboBoxSCCutZ.setItemText(3,ViewSCCDict['E']['label'])
        #update corresponding ViewSCData labels - E
        self.ui.comboBoxSCCutE.setItemText(0,ViewSCCDict['u1']['label'])
        self.ui.comboBoxSCCutE.setItemText(1,ViewSCCDict['u2']['label'])
        self.ui.comboBoxSCCutE.setItemText(2,ViewSCCDict['u3']['label'])
        self.ui.comboBoxSCCutE.setItemText(3,ViewSCCDict['E']['label'])
        
        
    def UpdateComboSCCX(self):
        """
        Wrapper method to perform swapping labels for 'X' comboBox
        """
        print "** UpdateComboSCX"
        label= str(self.ui.comboBoxSCCutX.currentText())
        self.UpdateViewSCCData(label,'u1')
        self.ui.ViewSCCDataDeBounce=False
        
    def UpdateComboSCCY(self):
        """
        Wrapper method to perform swapping labels for 'Y' comboBox
        """
        print "** UpdateComboSCY"
        label= str(self.ui.comboBoxSCCutY.currentText())
        self.UpdateViewSCCData(label,'u2')
        self.ui.ViewSCCDataDeBounce=False
                
    def UpdateComboSCCZ(self):
        """
        Wrapper method to perform swapping labels for 'Z' comboBox
        """
        print "** UpdateComboSCZ"
        label= str(self.ui.comboBoxSCCutZ.currentText())
        self.UpdateViewSCCData(label,'u3')
        self.ui.ViewSCCDataDeBounce=False
                
    def UpdateComboSCCE(self):
        """
        Wrapper method to perform swapping labels for 'E' comboBox
        """
        print "** UpdateComboSCE"
        label= str(self.ui.comboBoxSCCutE.currentText())
        self.UpdateViewSCCData(label,'E')
        self.ui.ViewSCCDataDeBounce=False
                
    def UpdateViewSCCData(self,newLabel,newKey):
        """
        Method to perform swapping single crystal comboBox labels
        newLabel: new comboBox label
        newKey: key to index used for the swap
        """
        if self.ui.ViewSCCDataDeBounce:
            #case we have a second update due to programmtically changing the current index - skip this one
            #print "++++++++ Debounce +++++++++"
            return
        #get labels for each comboBox - should have a duplicate at this point
        labels=[]
        labels.append(str(self.ui.comboBoxSCCutX.currentText()))
        labels.append(str(self.ui.comboBoxSCCutY.currentText()))
        labels.append(str(self.ui.comboBoxSCCutZ.currentText()))
        labels.append(str(self.ui.comboBoxSCCutE.currentText()))  
        
        #get list of possible labels - should be no duplicates
        labelLst=[]
        ViewSCCDict=self.ui.ViewSCCDict
        labelLst.append(ViewSCCDict['u1']['label'])
        labelLst.append(ViewSCCDict['u2']['label'])
        labelLst.append(ViewSCCDict['u3']['label'])
        labelLst.append(ViewSCCDict['E']['label'])    
        
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
            if indx != int(ViewSCCDict[newKey]['index']):
                updateCBIndx=indx
                cnt+=1 #check to make sure we found an updateCBIndx
            if indx == int(ViewSCCDict[newKey]['index']):
                otherIndex=indx
                
        if cnt != 1:
            print "Did not find the correct number of indicies- 1 expected but found: ",cnt
        #The indx we found 
        
        #Setting the debounce flag to True enables setCurrentIndex() event generated via the code
        #below to be ignored else letting this even be processed interferes with the current processing
        self.ui.ViewSCCDataDeBounce=True 
        if updateCBIndx==0:
            self.ui.comboBoxSCCutX.setCurrentIndex(missingIndx)
        if updateCBIndx==1:
            self.ui.comboBoxSCCutY.setCurrentIndex(missingIndx)
        if updateCBIndx==2:
            self.ui.comboBoxSCCutZ.setCurrentIndex(missingIndx)
        if updateCBIndx==3:
            self.ui.comboBoxSCCutE.setCurrentIndex(missingIndx)    
            
        #Now that we have the information for the swapped combo boxes, let's swap the corresponding parameters
        #Will simpy swap what's in the GUI widgets
        CBIndx0=mtch[0]
        CBIndx1=mtch[1]
        swapSCViewParams(self,'Cut',CBIndx0,CBIndx1)

    def updateSCCNpts(self):
        
        
        #function to update the number of points in the Single Crystal GUI when parameters change affecting the number of points
        
        #Update X NPTS label
        #get parameters:
        
        label=convertIndexToLabel(self,'X','Cut')    
        if self.ui.lineEditSCCutXFrom.text() != '':
            XFrom=float(self.ui.lineEditSCCutXFrom.text())
        elif self.ui.ViewSCCDict[label]['from'] != '':                
            XFrom = self.ui.ViewSCCDict[label]['from']
        else:
            XFrom = 0
            
        if self.ui.lineEditSCCutXTo.text() != '':
            XTo=float(self.ui.lineEditSCCutXTo.text())   
        elif self.ui.ViewSCCDict[label]['to'] != '':                
            XTo = self.ui.ViewSCCDict[label]['to']
        else:
            XTo = 100        
    
        try:
            XStep = float(self.ui.lineEditSCCutXStep.text())  
        except:
            XStep = float(XTo - XFrom)
        
        #Do some checking:
        if XFrom >= XTo:
            #case where the lower limit exceeds or is equal to the upper limit - problem case
            msg="Problem: X From is greater than X To - Please make corrections"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_() 
            return
        
        """
        if XStep == 0:
            #case where the lower limit exceeds or is equal to the upper limit - problem case
            msg="Problem: X Step must be greater than 0 - Please correct"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_() 
            return
        """
    
        try:
            XNpts=(XTo-XFrom)/XStep
        
        except:
            """
            #case where unable to successfully calculate XNpts
            self.ui.lineEditSCCutXNbins.setText("")
            msg="Unable to calculate 'X NPTS - please make corrections"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_()         
            return
            """
            self.ui.lineEditSCCutXNbins.setText("")
            XNpts=0
        else:
            self.ui.lineEditSCCutXNbins.setText(str(int(round(XNpts))))
            
        if XNpts > config.SCXNpts:
            #case where a large number of points has been selected
            msg="Warning: Current X settings will produce a large number of values: "+str(XNpts)+". Consider making changes"
            dialog=QtGui.QMessageBox(self)
            dialog.setText(msg)
            dialog.exec_()         
            return                

    def updateSCCBW(self):
        
        
        #function to update the number of points in the Single Crystal GUI when parameters change affecting the number of points
        
        #Update X NPTS label
        #get parameters:
        
        if self.ui.radioButtonSCNBins.isChecked():
            label=convertIndexToLabel(self,'X','Cut')    
            if self.ui.lineEditSCCutXFrom.text() != '':
                XFrom=float(self.ui.lineEditSCCutXFrom.text())
            elif self.ui.ViewSCCDict[label]['from'] != '':                
                XFrom = self.ui.ViewSCCDict[label]['from']
            else:
                #XFrom = 0
                pass
                
            if self.ui.lineEditSCCutXTo.text() != '':
                XTo=float(self.ui.lineEditSCCutXTo.text())   
            elif self.ui.ViewSCCDict[label]['to'] != '':                
                XTo = self.ui.ViewSCCDict[label]['to']
            else:
                #XTo = 100  
                pass      
            
            if self.ui.lineEditSCCutXNbins.text() != '':
                XNpts = float(self.ui.lineEditSCCutXNbins.text())
            else:
                #XNpts = 100
                #self.ui.lineEditSCCutXNbins.setText(str(XNpts))
                XNpts=1
                pass
            
            XStep = (XTo - XFrom)/XNpts
            self.ui.lineEditSCCutXStep.setText("%.3f" % XStep)

        
    def LegendEdit(self):
        print "Legend Edit"
        LM=LegendManager(self)
        LM.show()
        
    def ShowEBars(self):
        self.ui.checkBoxErrorBars.setCheckState(True) 
        #seems that setting state to true is making checkbox tristate
        #so disable tristate once state has been set
        self.ui.checkBoxErrorBars.setTristate(False)

    def DoImport(self):
        #case to check mantid workspaces for workspaces created by Slice Viewer
        #Looking for two workspaces
        #  <ws>_line
        #  <ws>_rebinned
        #
        # Will use <ws>_line to re-generate the Q and E ranges that produced the line plot
        # <ws>_rebinned contains the rebinned data from with to re-create the line plot shown in Slice Viewer
        # The advantage to re-creating the line plot versus just using the line plot from <ws>_line is that
        # one can use the MPLPowderCut tool to modify the ranges to sum else one is stuck with just the one 
        # plot view obtained from the <ws>_line workspace.
        
        #check if Not to ask user for overwritting Data Formatting values exists
        try:
            #case that it does, do nothing here
            self.MPLNoAsk
        except:
            #case that it does not so set no ask to false
            self.MPLNoAsk=False
        
        if self.MPLNoAsk==True:
            #case not to present dialog
            pass
        else:
            #present dialog
            title=_fromUtf8('Warning!')
            msg=_fromUtf8('Continuing will Overwrite Data Formatting Values with those from the Slice Viewer')
            txt1=_fromUtf8('Continue')
            txt2=_fromUtf8('Continue and Do Not Ask Again')
            txt3=_fromUtf8('Exit')
            button=QtGui.QMessageBox.warning(self,title,msg,txt1,txt2,txt3)
            print "Button Pressed: ",button
            if button==0:
                self.MPLNoAsk=False
            elif button==1:
                self.MPLNoAsk=True
            elif button==2:
                return #exit out of this function if this button is selected
            else:
                pass   
        #if we get here, we've gotten to the point to import information created by Slice Viewer
        getSVValues(self) #call to MPLPowderCutHelpers.py   
        

        
        
    def DoOPlot(self):
        self.doOPlot=True
        self.DoPlot()
        
        
    def DoPlot(self):
        print "*************** Do Plot *********************"
        
        
        if self.ui.mode == 'Powder':
            DoPowderPlotMSlice(self) #call to MPLPowderCutHelpers.py  
        elif self.ui.mode == 'SC':
            #set stackedWidgetCut index
            DoSCPlotMSlice(self) #call to MPLPowderCutHelpers.py  
        else:
            #unsupported mode - complain"
            print "Unsupported GUI mode - returning"
            return

        
    def DoAnnotate(self):
        self.doAnnotate=True
        self.canvas.mpl_connect('button_press_event', self.onclick)
        
    def onclick(self,event):
        if self.doAnnotate:
            #first get the text to annotate
            txt=str(self.ui.MPLlineEditTextAnnotate.text())
            for pl in range(2):   
                if pl == 0:
                    self.canvas #enable drawing area
                    fig=self.figure
                    plt.figure(fig.number)
                    self.ui.txt=plt.text(event.xdata,event.ydata,txt)
                else:
                    self.shadowCanvas
                    fig=self.shadowFigure
                    plt.figure(fig.number)
                    self.ui.shadowtxt=plt.text(event.xdata,event.ydata,txt)
                
            self.canvas.draw()
            self.shadowCanvas.draw()
        self.doAnnotate=False
        
    def RemText(self):
        try:
            print "Removing Annotation Text"
            
            for pl in range(2):   
                if pl == 0:
                    self.canvas #enable drawing area
                    fig=self.figure
                    plt.figure(fig.number)
                    self.ui.txt.remove()
                else:
                    self.shadowCanvas
                    fig=self.shadowFigure
                    plt.figure(fig.number)
                    self.ui.shadowtxt.remove()
            
            self.canvas.draw()
            self.shadowCanvas.draw()
        except:
            #case where the button was pushed more than once and arrow should already be gone...do nothing
            pass
    
    def DoArrow(self):
        self.doArrow=True
        self.canvas.mpl_connect('button_press_event', self.onaclick)
        
    def onaclick(self,event):
        if self.doArrow:
            #first get the arrow direction
            dindx=self.ui.MPLcomboBoxArrow.currentIndex()
            #create arrow size relative to data range
            [xmin,xmax,ymin,ymax]=plt.axis()
            print "xmin: ",xmin," xmax: ",xmax," ymin: ",ymin," ymax: ",ymax
            delx=xmax-xmin
            dely=ymax-ymin
            #frac(tion) and h(ead)frac selected by trial and error...used to determine the relative size of the arrow
            frac=0.04  
            hfrac=0.02
            print "dindx: ",dindx
            for pl in range(2):
                if pl == 0:
                    self.canvas #enable drawing area
                    fig=self.figure
                    plt.figure(fig.number)
                else:
                    self.shadowCanvas
                    fig=self.shadowFigure
                    plt.figure(fig.number)   
                if dindx==0:
                    #point left
                    if pl==0:
                        self.ui.arrow=plt.arrow(event.xdata+frac*delx+hfrac*delx,event.ydata,-frac*delx,0,head_width=hfrac*dely,head_length=hfrac*delx,width=hfrac/5*dely,fc="k",ec="k")
                    else:
                        self.ui.shadowarrow=plt.arrow(event.xdata+frac*delx+hfrac*delx,event.ydata,-frac*delx,0,head_width=hfrac*dely,head_length=hfrac*delx,width=hfrac/5*dely,fc="k",ec="k")
                elif dindx==1:
                    #point right
                    if pl==0:
                        self.ui.arrow=plt.arrow(event.xdata-(frac*delx+hfrac*delx),event.ydata,frac*delx,0,head_width=hfrac*dely,head_length=hfrac*delx,width=hfrac/5*dely,fc="k",ec="k")
                    else:
                        self.ui.shadowarrow=plt.arrow(event.xdata-(frac*delx+hfrac*delx),event.ydata,frac*delx,0,head_width=hfrac*dely,head_length=hfrac*delx,width=hfrac/5*dely,fc="k",ec="k")
                        
                elif dindx==2:
                    #point up
                    if pl==0:
                        self.ui.arrow=plt.arrow(event.xdata,event.ydata-(frac*dely+hfrac*dely),0,frac*dely,head_width=hfrac*delx,head_length=hfrac*dely,width=hfrac/5*delx,fc="k",ec="k")
                    else:
                        self.ui.shadowarrow=plt.arrow(event.xdata,event.ydata-(frac*dely+hfrac*dely),0,frac*dely,head_width=hfrac*delx,head_length=hfrac*dely,width=hfrac/5*delx,fc="k",ec="k")
                        
                elif dindx==3:
                    #point down
                    if pl==0:
                        self.ui.arrow=plt.arrow(event.xdata,event.ydata+frac*dely+hfrac*dely,0,-frac*dely,head_width=hfrac*delx,head_length=hfrac*dely,width=hfrac/5*delx,fc="k",ec="k")
                    else:
                        self.ui.shadowarrow=plt.arrow(event.xdata,event.ydata+frac*dely+hfrac*dely,0,-frac*dely,head_width=hfrac*delx,head_length=hfrac*dely,width=hfrac/5*delx,fc="k",ec="k")
                        
                else:
                    #should never get here...
                    pass
            self.canvas.draw()
            self.shadowCanvas.draw()
        self.doArrow=False
        
    def RemArrow(self):
        try:
            self.ui.arrow.remove()
            self.canvas.draw()
            self.ui.shadowarrow.remove()
            self.shadowCanvas.draw()

        except:
            #case where the button was pushed more than once and arrow should already be gone...do nothing
            pass
            
    def PopPlot(self):
        
        

        """
        ax=plt.subplot(211)
        plt.figure(self.shadowFigure.number)
        #plt.figure()
        #format the drawing area
        #plt.subplot(211)
        plt.gcf().subplots_adjust(bottom=-0.25)
        plt.gcf().subplots_adjust(left=0.12)
        plt.gcf().subplots_adjust(right=0.95) 
        
        ax2=plt.subplot(212)
        ax2.axis('off')
        #axes fraction 0,0 is lower left of axes and 1,1 is upper right
        #x offset between text on the same row
        xoff0 = 0
        xoff1 = 0.5
        
        yoff = 0.096 #global offset in y axis direction
        
        #dx0 and dx1 
        dx0 = 0   #dx0 gives start position in the row for the first row text block
        dx1 = 0 #dx1 gives start position in the row for the second row text block
        
        #dy0 and dy1
        dy0 = 0 #dy0 starts at zero
        dy1 = -0.05 #dy1 times row number gives y offset between rows
        
        plt.subplot(212)
        plt.annotate('Some Text',(dx0+xoff0,dy0*0),(dx1+xoff0,dy1*0+yoff),textcoords='axes fraction')
        

        """

        plt.gcf().subplots_adjust(bottom=0.25)
        plt.gcf().subplots_adjust(left=0.12)
        plt.gcf().subplots_adjust(right=0.95)   
        #plt.annotate('Some Text',(0,0),(0,-0.25),textcoords='axes fraction')
        
        #display data ranges:
        name0=str(self.ui.histoDataSum.getDimension(0).getName())
        mn0=str(round(float(str(self.ui.histoDataSum.getDimension(0).getMinimum())),3))
        mx0=str(round(float(str(self.ui.histoDataSum.getDimension(0).getMaximum())),3))
        name1=str(self.ui.histoDataSum.getDimension(1).getName())
        mn1=str(round(float(str(self.ui.histoDataSum.getDimension(1).getMinimum())),3))
        mx1=str(round(float(str(self.ui.histoDataSum.getDimension(1).getMaximum())),3))
        name2=str(self.ui.histoDataSum.getDimension(2).getName())
        mn2=str(round(float(str(self.ui.histoDataSum.getDimension(2).getMinimum())),3))
        mx2=str(round(float(str(self.ui.histoDataSum.getDimension(2).getMaximum())),3))
        name3=str(self.ui.histoDataSum.getDimension(3).getName())
        mn3=str(round(float(str(self.ui.histoDataSum.getDimension(3).getMinimum())),3))
        mx3=str(round(float(str(self.ui.histoDataSum.getDimension(3).getMaximum())),3))
        
        dy1 = -0.05  #spacing between text lines
        
        """
        print 4 blocks of text with each block formatted as:
        name
        min val
        max val
        """
        xoff = 0.25 #offset between the text blocks
        xa=0.04 #minor tuning of text placement

        plt.annotate(name0,(0,0),(0+xa,-0.25+0*dy1),textcoords='axes fraction')
        plt.annotate(mn0,(0,0),(0+xa,-0.25+1*dy1),textcoords='axes fraction')        
        plt.annotate(mx0,(0,0),(0+xa,-0.25+2*dy1),textcoords='axes fraction')    
        
        plt.annotate(name1,(0,0),(1*xoff+xa,-0.25+0*dy1),textcoords='axes fraction')
        plt.annotate(mn1,(0,0),(1*xoff+xa,-0.25+1*dy1),textcoords='axes fraction')        
        plt.annotate(mx1,(0,0),(1*xoff+xa,-0.25+2*dy1),textcoords='axes fraction')    
        
        plt.annotate(name2,(0,0),(2*xoff+xa,-0.25+0*dy1),textcoords='axes fraction')
        plt.annotate(mn2,(0,0),(2*xoff+xa,-0.25+1*dy1),textcoords='axes fraction')        
        plt.annotate(mx2,(0,0),(2*xoff+xa,-0.25+2*dy1),textcoords='axes fraction')    

        plt.annotate(name3,(0,0),(3*xoff+xa,-0.25+0*dy1),textcoords='axes fraction')
        plt.annotate(mn3,(0,0),(3*xoff+xa,-0.25+1*dy1),textcoords='axes fraction')        
        plt.annotate(mx3,(0,0),(3*xoff+xa,-0.25+2*dy1),textcoords='axes fraction')    
        
        plt.draw()          
        self.shadowFigure.canvas.draw()  
        self.shadowCanvas.setVisible(True) 

        
        """
        plt.subplot(211)
        plt.figure(self.shadowFigure.number)
        plt.subplot(212)
        plt.figure(self.shadowFigure.number)
        plt.subplot(212).axis('off')
        """
        #self.shadowFigure = plt.figure()
        #self.shadowCanvas=FigureCanvas(self.shadowFigure)
        self.shadow_navigation_toolbar = NavigationToolbar(self.shadowCanvas, self.shadowCanvas)
        """
        
        #format the drawing area
        #plt.subplot(211)
        plt.gcf().subplots_adjust(bottom=-0.25)
        plt.gcf().subplots_adjust(left=0.12)
        plt.gcf().subplots_adjust(right=0.95)        
        """
        
        
        self.ui.MPLpushButtonPopPlot.setEnabled(False)
        """
        winID=self.ui.MPLframe.effectiveWinId()
        print " Save Window ID: ",winID
#        winID=QtGui.qApp.activeWindow()
#        print " Save Window ID2: ",winID
#        winID=self.ui.MPLPowderCutMainWindow.winID()
#        print " Save Window ID2: ",winID

        #        pwinID=self.ui.MPLframe.WinId()
#        print " Save Window ID 2: ",pwinID
        
        ws=self.currentPlotWS
        print "ws.getTitle: ",ws.getTitle()
        print "type(ws): ",type(ws)
        fname=ws.getTitle()
        filter='.jpg'
        wsname=fname+filter
        filename = str(QtGui.QFileDialog.getSaveFileName(self, 'Save Plot Window', fname,filter))
        qf=QtCore.QFile(filename)
        qf.open(QtCore.QIODevice.WriteOnly)
        
        #FIXME - currently writing zero length files...not sure the issue...
        p = QtGui.QPixmap.grabWindow(winID)
#        p = QtGui.QPixmap.grabWindow(1)

        p.save(qf, format=None)
        print " Saved: ",filename
        """
            
            
    def SaveASCII(self):
        __ws=self.currentPlotWS
        print "__ws.getTitle: ",__ws.getTitle()
        print "type(__ws): ",type(__ws)
        fname=__ws.getTitle()
        filter='.txt'
        wsname=fname+filter
        filter="TXT (*.txt);;All files (*.*)"
        if self.parent.ui.rememberDataPath=='':
            curdir=os.curdir
        else:
            curdir=self.parent.ui.rememberDataPath
        fname=_fromUtf8(curdir+'/'+fname)
        print "fname: ",fname
        print "type(fname): ",type(fname)
        fsavename = str(QtGui.QFileDialog.getSaveFileName(self, 'Save ASCII Data', fname,filter))
        if fsavename!='':
            SaveAscii(__ws,fsavename,Separator='CSV') #Mantid routine to save a workspace as ascii data
        
    def SaveHistory(self):
        #case to extract the tree widget structure and save the items to file
        #must first Update History to fill the tree structure - so find the number of items in the tree first
        NTreeItems=self.ui.treeWidgetHistory.topLevelItemCount()
        if NTreeItems <= 0:
            #case where no items are in the tree - inform user and return
            dialog=QtGui.QMessageBox(self)
            dialog.setText("No workspace history found - From History tab, run Update History then use Save History")
            dialog.exec_()  
        else:
            #case to get the filename and save history to file
            filter='.txt'
            #get workspace name from workspace label
            wsName=str(self.ui.MPLlabelWSName.text())
            if wsName!='':
                #parse out workspace name from the label
                wsName=wsName.split(": ")
                wsName=wsName[1] #extract just the workspace name to preface the output filename
                fname=wsName+'_history'+filter
                filter="TXT (*.txt);;All files (*.*)"
                if self.parent.ui.rememberDataPath=='':
                    curdir=os.curdir
                else:
                    curdir=self.parent.ui.rememberDataPath
                fname=_fromUtf8(curdir+'/'+fname)
                fsavename = str(QtGui.QFileDialog.getSaveFileName(self, 'Save Workspace History to File', fname,filter))
                if fsavename != '':
                    #case to save history
                    #open file
                    with open(fsavename, 'w') as f:
                        #write header info
                        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        f.write('\r')
                        f.write(str(self.ui.MPLlabelWSName.text()))
                        f.write('\r')
                        #now progress through the tree for each item
                        for i in range(NTreeItems):
                            item=self.ui.treeWidgetHistory.topLevelItem(i)
                            f.write(str(item.text(0)))
                            f.write('\r')
                            NChildren=item.childCount()
                            if NChildren > 0:
                                #then write each item child to file
                                for j in range(NChildren):
                                    txt=str(item.child(j).text(0))
                                    f.write('\t')
                                    f.write(txt)
                                    f.write('\r')

        
    def SavePlotWS(self):
        #check if a workspace is a 1D plot workspace and if so, save it
        print " self.ui.current1DWorkspace: ",self.ui.current1DWorkspace
        try:
            __MDH1D=self.ui.current1DWorkspace
        except:
            #case where there is no 1D workspace to save
            print "No 1D workspace to save - returning"
            return
            
        #Normalize signal and error squared by NumEventsArray
        NumEventsArray=__MDH1D.getNumEventsArray()
        signal=__MDH1D.getSignalArray()
        error2=__MDH1D.getErrorSquaredArray()
        error=np.sqrt(error2)
        ebar=2.0*np.sqrt(error2)/NumEventsArray

        Ndims=4
        extents=str(__MDH1D.getXDimension().getMinimum())+','+str(__MDH1D.getXDimension().getMaximum())+\
                    ','+str(__MDH1D.getYDimension().getMinimum())+','+str(__MDH1D.getYDimension().getMaximum())+\
                    ','+str(__MDH1D.getZDimension().getMinimum())+','+str(__MDH1D.getZDimension().getMaximum())+\
                    ','+str(__MDH1D.getTDimension().getMinimum())+','+str(__MDH1D.getTDimension().getMaximum())
        numBins=str(__MDH1D.getXDimension().getNBins())+',1,1,1'
        names=[__MDH1D.getXDimension().getName(),__MDH1D.getYDimension().getName(),__MDH1D.getZDimension().getName(),__MDH1D.getTDimension().getName()]
        #names='a,b,c,d'
        units=[__MDH1D.getXDimension().getUnits(),__MDH1D.getYDimension().getUnits(),__MDH1D.getZDimension().getUnits(),__MDH1D.getTDimension().getUnits()]
        
        print "Ndims: ",Ndims
        print "extents: ",extents
        print "numBins: ",numBins
        print "names: ",names
        print "units: ",units
        
        
        #extract history data for this workspace:
        histDict=histToDict(__MDH1D)
        print "histDict: "
        print histDict

        """
        Important note!
        bug in CreateMDHistoWorkspace for using NumberOfEvents property prior to mantid 3.4
        """
        #case to create a compact 1D workspace
        __MDH1Dcompact=CreateMDHistoWorkspace(signal,error,Dimensionality=Ndims,Extents=extents,\
                        NumberOfEvents=NumEventsArray,\
                        NumberOfBins=numBins,Names=names,Units=units)
        #note that CreateMDHistoWorkspace() takes errors in and the resultant workspace
        #returns squared error array - need to take this into account
        #also note that need to use a 3.4 or later build of mantid in order to be able to use
        #the NumberOfEvents input array as prior versions do not recognize this field
        
        #uncomment the following line to use the full 1D workspace in place of the compact one
        #__MDH1Dcompact = __MDH1D

        
        #create a workspace save name based upon the workspace name in the Select Workspace pull down menu
        wsName=str(self.ui.MPLcomboBoxActiveWorkspace.currentText())
        wsName=wsName+'_1D'
        ws=wsName #placeholder string name that will become a workspace when Load() occurs below
        filter='.nxs'
        fname=wsName+filter
        filter="NXS (*.nxs);;All files (*.*)"
        if self.parent.ui.rememberDataPath=='':
            curdir=os.curdir
        else:
            curdir=self.parent.ui.rememberDataPath
        fname=_fromUtf8(curdir+'/'+fname)
        
        fsavename = str(QtGui.QFileDialog.getSaveFileName(self, 'Save 1D Workspace', fname,filter))
        if fsavename !='':
            #need to update wsName to be commensurate with the filename once the user has specified the workspace filename
            tmp=basename(fsavename) #returns the filename
            tmp=tmp.split('.')
            wsName=tmp[0] 
            #then need to update the workspace name to match the requested workspace name
            mtd.addOrReplace(wsName,__MDH1Dcompact)
            print "** fsavename: ",fsavename
            if fsavename != '':
                #case to save workspace
                print "Saving workspace: ",__MDH1Dcompact.name()
                print "  Workspace ID: ",__MDH1Dcompact.id()
                try:
                    #first try to save as MD workspace
                    SaveMD(__MDH1Dcompact,Filename=fsavename) #save workspace
                except:
                    try:
                        #if saving as MD fails, try SaveNexus
                        SaveNexus(__MDH1Dcompact,Filename=fsavename) #save workspace
                    except:
                        #otherwise - give up...
                        print "Unable to successfully save workspace - returning"
                        return
                
                basefname=os.path.splitext(fsavename)
                compFilename=basefname[0]+'.xml'
                write1DCompanionFile(histDict,compFilename)
    
                Load(fsavename,OutputWorkspace=ws) #loading workspace back in under new name is easiest way (I know) to associate the workspace with the name
            else:
                print "No filename given - returning"
                return
            #Now add workspace to the list of workspaces in the MPL Select Workspace list    
            #but fitst check if the name already exists and only add new names
            Nws=self.ui.MPLcomboBoxActiveWorkspace.count()
            cnt=0
            for i in range(Nws):
                CBitemName=self.ui.MPLcomboBoxActiveWorkspace.itemText(i)
                print "CBitemName: ",CBitemName
                if CBitemName == wsName:
                    #if we find the name already, increment counter indicating the find
                    cnt+=1
            print "cnt: ",cnt
            if cnt == 0:
                #case to add new workspace name
                self.ui.MPLcomboBoxActiveWorkspace.insertItem(Nws,wsName)
                #set Select Workspace to this new workspace
                self.ui.MPLcomboBoxActiveWorkspace.setCurrentIndex(Nws)
                
            #need to disable the Data Formatting block since the 1D workspace should not be rebinned
            self.ui.MPLgroupBoxDataFormat.setEnabled(False)
            
            #also need to add workspace name to Workspace Manager table
            table=self.parent.ui.tableWidgetWorkspaces
            workspaceLocation=''
            addWStoTable(table,wsName,workspaceLocation)
        
    def ResetParams(self):
        #case to restore Data Formatting values to those in the selected workspace
        #toggle reset parameters flag to on
        self.ui.ResetParams=True
        #use DoPlot() to set parameters
        self.DoPlot()
        #toggle reset parameters flag back off
        self.ui.ResetParams=False

        
    def UpdateHistory(self):
        #method to update the Tree Widget tab with the history information from the file in the 'Select Workspace' pulldown menu
        #find the workspace to get the history from        
        wsName=str(self.ui.MPLcomboBoxActiveWorkspace.currentText())
        
        if wsName == '':
            print "No workspace selected - returning"
            return
        
        __ws=mtd.retrieve(wsName)
        
        NEntries=len(__ws.getHistory().getAlgorithmHistories())
        
        try:
            #check if there is past history in the tree and clear it
            self.ui.treeWidgetHistory.clear()
        except:
            #if no past history, move onward
            pass
        
        for i in range(NEntries):
            NTags=len(__ws.getHistory().getAlgorithmHistories()[i].getProperties())
            print __ws.getHistory().getAlgorithmHistories()[i].name()
            entry=__ws.getHistory().getAlgorithmHistories()[i].name()
            newItem=QtGui.QTreeWidgetItem( [entry])
            for j in range(NTags):
                name=__ws.getHistory().getAlgorithmHistories()[i].getProperties()[j].name()
                value=__ws.getHistory().getAlgorithmHistories()[i].getProperties()[j].value()
                txt="  "+name+": "+value
                if value != '':
                    #print "  ",name,": ",value
                    child=QtGui.QTreeWidgetItem( [txt])
                    newItem.addChild(child)
                else:
                    pass
            self.ui.treeWidgetHistory.addTopLevelItem(newItem)    
            if self.ui.MPLcheckBoxExpandAll.isChecked():
                #case to expand items in tree widget
                self.ui.treeWidgetHistory.expandItem(newItem)
            else:
                self.ui.treeWidgetHistory.collapseItem(newItem)
        #set the workspace name text field so people know which history is being shown
        self.ui.MPLlabelWSName.setText("Workspace: "+wsName)
        
    def ExpandAll(self):
        self.UpdateHistory()

    def UpdateComments(self):
        #method to update the Tree Widget tab with the history information from the file in the 'Select Workspace' pulldown menu
        #find the workspace to get the history from        
        wsName=str(self.ui.MPLcomboBoxActiveWorkspace.currentText())
        
        if wsName == '':
            print "No workspace selected - returning"
            return
        
        __ws=mtd.retrieve(wsName)
        
        NEntries=len(__ws.getHistory().getAlgorithmHistories())
        
        #check readonly status - should only get here if readonly not enabled
        if self.ui.MPLcheckBoxReadOnly.isChecked():
            print "ReadOnly case mismatch - returning"
            return
        
        #Read in text from text 
        txt=self.ui.MPLtextEditComments.toPlainText()
        txtstr=str(txt)
        print "** type(txtstr): ",type(txtstr)
        print "** txtstr: ",txtstr
            
        #Put text into workspace
        __ws.setComment(txtstr)
        
        #Save workspace
        #create a workspace save name based upon the workspace name in the Select Workspace pull down menu
        wsName=str(self.ui.MPLcomboBoxActiveWorkspace.currentText())
        filter='.nxs'
        fname=wsName+filter
        fsavename = str(QtGui.QFileDialog.getSaveFileName(self, 'Save Workspace', fname,filter))
        #need to update wsName to be commensurate with the filename once the user has specified the workspace filename
        tmp=basename(fsavename) #returns the filename
        tmp=tmp.split('.')
        wsName=tmp[0] 
        #then need to update the workspace name to match the requested workspace name
        mtd.addOrReplace(wsName,__ws)
        print "** fsavename: ",fsavename
        if fsavename != '':
            #case to save workspace
            print "Saving workspace: ",__ws.name()
            print "  Workspace ID: ",__ws.id()
            try:
                #first try to save as MD workspace
                SaveMD(__ws,Filename=fsavename) #save workspace
            except:
                try:
                    #if saving as MD fails, try SaveNexus
                    SaveNexus(__ws,Filename=fsavename) #save workspace
                except:
                    #otherwise - give up...
                    print "Unable to successfully save workspace - returning"
                    return

            Load(fsavename,OutputWorkspace=__ws) #loading workspace back in under new name is easiest way (I know) to associate the workspace with the name
        else:
            print "No filename given - returning"
            return
        #Now add workspace to the list of workspaces in the MPL Select Workspace list    
        #but fitst check if the name already exists and only add new names
        Nws=self.ui.MPLcomboBoxActiveWorkspace.count()
        cnt=0
        for i in range(Nws):
            CBitemName=self.ui.MPLcomboBoxActiveWorkspace.itemText(i)
            print "CBitemName: ",CBitemName
            if CBitemName == wsName:
                #if we find the name already, increment counter indicating the find
                cnt+=1
        print "cnt: ",cnt
        if cnt == 0:
            #case to add new workspace name
            self.ui.MPLcomboBoxActiveWorkspace.insertItem(Nws,wsName)
            #set Select Workspace to this new workspace
            self.ui.MPLcomboBoxActiveWorkspace.setCurrentIndex(Nws)        

        #set the workspace name text field so people know which history is being shown
        self.ui.MPLlabelCSelectedWorkspace.setText("Workspace: "+wsName)        
        
    def ReadOnly(self):
        #checkbox for the Comments tab to determine if comments are read only or editable
        #default is read only

        if self.ui.MPLcheckBoxReadOnly.isChecked():
            #case to make text area read only
            self.ui.MPLtextEditComments.setReadOnly(True)
            self.ui.MPLpushButtonSaveComments.setEnabled(False)
        else:
            #case to enable editing 
            self.ui.MPLtextEditComments.setReadOnly(False)
            self.ui.MPLpushButtonSaveComments.setEnabled(True)
            self.ui.MPLtextEditComments.setFocus(True)
            
    def getComments(self):
        #method to call to extract comments from a file and place them in the Comments tab
        wsName=str(self.ui.MPLcomboBoxActiveWorkspace.currentText())
        if wsName == '':
            print "No workspace selected - returning"
            return
        #retrive the workspace
        __ws=mtd.retrieve(wsName)        

        #update comments tab workspace selected label
        self.ui.MPLlabelCSelectedWorkspace.setText('Workspace: '+wsName)
        #get text string from current workspace
        txtstr=__ws.getComment()
        print "txtstr: ",txtstr
        #write it to text edit
        self.ui.MPLtextEditComments.setText(txtstr)
        
        
    def Done(self):
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            #close application
            self.close()
        else:
            #do nothing and return
            pass               
        
if __name__=="__main__":
    print "MPLPC __main__"
    app = QtGui.QApplication(sys.argv)
    MPLPC = MPL1DCut()
    MPLPC.show()
    sys.exit(app.exec_())

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    