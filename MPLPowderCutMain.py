import sys, os

from MPLPowderCut import *
from PyQt4 import Qt, QtCore, QtGui
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

import matplotlib
if matplotlib.get_backend() != 'QT4Agg':
    matplotlib.use('QT4Agg')
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

class MPLPowderCut(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MPLPowderCutMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Powder Cut")
        self.parent=parent 
        
        #establish signals and slots
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
        
        QtCore.QObject.connect(self.ui.MPLpushButtonUpdateHistory, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.UpdateHistory)
        QtCore.QObject.connect(self.ui.MPLcheckBoxExpandAll, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.ExpandAll)
        
        QtCore.QObject.connect(self.ui.MPLpushButtonSaveComments, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.UpdateComments)
        QtCore.QObject.connect(self.ui.MPLcheckBoxReadOnly, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.ReadOnly)
        
        QtCore.QObject.connect(self.ui.MPLcomboBoxActiveWorkspace, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.SelectWorkspace)
        
        #now that the widget has been established, copy over values from MSlice
        #Workspace List and insert them into the MPLcomboBoxActiveWorkspace combo box
        
        #get the list of workspaces
        wslist=self.parent.ui.wslist
        print "wslist: ",wslist
        
        #now need to parse workspaces to determine which are grouped workspaces to list each workspace separately in the plot GUI
        Nws=len(wslist)
        wstotlist=[]
        for n in range(Nws):
            tmpws=mtd.retrieve(wslist[n])
            if 'Group' in str(type(tmpws)):
            #case to get all workspace names from the group
                for ws in tmpws:
                    wstotlist.append(ws)
            else:
                #case we just have a single workspace
                wstotlist.append(wslist[n])
        
        print "Total number of workspaces passed to Powder Cut: ",wstotlist
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
            
        #Data Formatting
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
               
        #Plot Configuration
        self.ui.MPLlineEditLabelsIntensity.setText(self.parent.ui.lineEditLabelsIntensity.text())
        self.ui.MPLlineEditLabelsTitle.setText(self.parent.ui.lineEditLabelsTitle.text())
        self.ui.MPLlineEditLabelsLegend.setText(self.parent.ui.lineEditLabelsLegend.text())
        
        #Place Matplotlib figure within the GUI frame
        #create drawing canvas
        # a figure instance to plot on
        
        matplotlib.rc_context({'toolbar':True})
        self.shadowFigure = plt.figure()
        plt.figure(self.shadowFigure.number)
        self.figure = plt.figure()

        
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
        
        #Launch plot in bringing up the application
        self.DoPlot()
    
    def SelectWorkspace(self):
        #get selected workspace
        wsindx=self.ui.MPLcomboBoxActiveWorkspace.currentIndex()
        self.ui.MPLcurrentWS=str(self.ui.MPLcomboBoxActiveWorkspace.currentText())
        if self.ui.MPLcurrentWS=='':
            #case where we do not have a workspace
            return
        else:
            
            #now check if it's a 2D or 1D workspace - need to make sure that Data Formatting is enabled for 2D and disabled for 1D
            ws=mtd.retrieve(self.ui.MPLcurrentWS)
            NXbins=ws.getXDimension().getNBins()
            NYbins=ws.getYDimension().getNBins()
            print "NXbins: ",NXbins,"  NYbins: ",NYbins
            if NXbins > 1 and NYbins > 1:
                #case for a 2D workspace - enable Data Formatting
                print "Enabling Data Formatting"
                self.ui.MPLgroupBoxDataFormat.setEnabled(True)
            else:
                # 1D case to disable Data Formatting
                print "Disabling Data Formatting"
                self.ui.MPLgroupBoxDataFormat.setEnabled(False)
                set1DBinVals(self,ws)
        
        #update the selected workspace label in the comments tab
        self.getComments()
                
        print "Selected Workspace: ",self.ui.MPLcurrentWS

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
            title=QtCore.QString('Warning!')
            msg=QtCore.QString('Continuing will Overwrite Data Formatting Values with those from the Slice Viewer')
            txt1=QtCore.QString('Continue')
            txt2=QtCore.QString('Continue and Do Not Ask Again')
            txt3=QtCore.QString('Exit')
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
        DoPlotMSlice(self) #call to MPLPowderCutHelpers.py  

        
        
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
        
        self.shadowCanvas.setVisible(True)
        self.shadowFigure = plt.figure()
        self.shadowCanvas=FigureCanvas(self.shadowFigure)
        self.shadow_navigation_toolbar = NavigationToolbar(self.shadowCanvas, self.shadowCanvas)
        
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
        ws=self.currentPlotWS
        print "ws.getTitle: ",ws.getTitle()
        print "type(ws): ",type(ws)
        fname=ws.getTitle()
        filter='.txt'
        wsname=fname+filter
        fsavename = str(QtGui.QFileDialog.getSaveFileName(self, 'Save ASCII Data', fname,filter))
        SaveAscii(ws,fsavename)
        
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
            #parse out workspace name from the label
            wsName=wsName.split(": ")
            wsName=wsName[1] #extract just the workspace name to preface the output filename
            fname=wsName+filter
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
            MDH1D=self.ui.current1DWorkspace
        except:
            #case where there is no 1D workspace to save
            print "No 1D workspace to save - returning"
            return
        #create a workspace save name based upon the workspace name in the Select Workspace pull down menu
        wsName=str(self.ui.MPLcomboBoxActiveWorkspace.currentText())
        wsName=wsName+'_1D'
        ws=wsName #placeholder string name that will become a workspace when Load() occurs below
        filter='.nxs'
        fname=wsName+filter
        fsavename = str(QtGui.QFileDialog.getSaveFileName(self, 'Save 1D Workspace', fname,filter))
        #need to update wsName to be commensurate with the filename once the user has specified the workspace filename
        tmp=basename(fsavename) #returns the filename
        tmp=tmp.split('.')
        wsName=tmp[0] 
        #then need to update the workspace name to match the requested workspace name
        mtd.addOrReplace(wsName,MDH1D)
        print "** fsavename: ",fsavename
        if fsavename != '':
            #case to save workspace
            print "Saving workspace: ",MDH1D.name()
            print "  Workspace ID: ",MDH1D.id()
            try:
                #first try to save as MD workspace
                SaveMD(MDH1D,Filename=fsavename) #save workspace
            except:
                try:
                    #if saving as MD fails, try SaveNexus
                    SaveNexus(MDH1D,Filename=fsavename) #save workspace
                except:
                    #otherwise - give up...
                    print "Unable to successfully save workspace - returning"
                    return

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

        
    def UpdateHistory(self):
        #method to update the Tree Widget tab with the history information from the file in the 'Select Workspace' pulldown menu
        #find the workspace to get the history from        
        wsName=str(self.ui.MPLcomboBoxActiveWorkspace.currentText())
        
        if wsName == '':
            print "No workspace selected - returning"
            return
        
        ws=mtd.retrieve(wsName)
        
        NEntries=len(ws.getHistory().getAlgorithmHistories())
        
        try:
            #check if there is past history in the tree and clear it
            self.ui.treeWidgetHistory.clear()
        except:
            #if no past history, move onward
            pass
        
        for i in range(NEntries):
            NTags=len(ws.getHistory().getAlgorithmHistories()[i].getProperties())
            print ws.getHistory().getAlgorithmHistories()[i].name()
            entry=ws.getHistory().getAlgorithmHistories()[i].name()
            newItem=QtGui.QTreeWidgetItem( [entry])
            for j in range(NTags):
                name=ws.getHistory().getAlgorithmHistories()[i].getProperties()[j].name()
                value=ws.getHistory().getAlgorithmHistories()[i].getProperties()[j].value()
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
        
        ws=mtd.retrieve(wsName)
        
        NEntries=len(ws.getHistory().getAlgorithmHistories())
        
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
        ws.setComment(txtstr)
        
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
        mtd.addOrReplace(wsName,ws)
        print "** fsavename: ",fsavename
        if fsavename != '':
            #case to save workspace
            print "Saving workspace: ",ws.name()
            print "  Workspace ID: ",ws.id()
            try:
                #first try to save as MD workspace
                SaveMD(ws,Filename=fsavename) #save workspace
            except:
                try:
                    #if saving as MD fails, try SaveNexus
                    SaveNexus(ws,Filename=fsavename) #save workspace
                except:
                    #otherwise - give up...
                    print "Unable to successfully save workspace - returning"
                    return

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
        ws=mtd.retrieve(wsName)        

        #update comments tab workspace selected label
        self.ui.MPLlabelCSelectedWorkspace.setText('Workspace: '+wsName)
        #get text string from current workspace
        txtstr=ws.getComment()
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
    MPLPC = MPLPowderCut()
    MPLPC.show()
    sys.exit(app.exec_())

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    