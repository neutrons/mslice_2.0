
import sys,os
sys.path.append(os.environ['MANTIDPATH'])
from mantid.simpleapi import * 
from MPLSCCutHelpers import *

def getMPLParms(self):
    #get selected workspace from 1D Cut MPL app
    ws_sel=str(self.ui.MPLcomboBoxActiveWorkspace.currentText())
    __ws=mtd.retrieve(ws_sel)	
    
    if 'Group' in __ws.id():
        #case for a group workspace
        NXDbins=__ws[0].getXDimension().getNBins()	
        NYDbins=__ws[0].getYDimension().getNBins()
    else:
        #case for an individual workspace
        NXDbins=__ws.getXDimension().getNBins()	
        NYDbins=__ws.getYDimension().getNBins()        
    

    print "NXDbins: ",NXDbins,"  NYDbins: ",NYDbins
    
    #now check if it's a 2D or 1D workspace - need to make sure that Data Formatting is enabled for 2D and disabled for 1D
    if NXDbins > 1 and NYDbins > 1:
        #case for a 2D workspace - enable Data Formatting
        print "Enabling Data Formatting"
        self.ui.MPLgroupBoxDataFormat.setEnabled(True)
    else:
        # 1D case to disable Data Formatting
        print "Disabling Data Formatting"
        self.ui.MPLgroupBoxDataFormat.setEnabled(False)
        
        #FIXME
        #Need to revisit checking for alignment here as set1DBinVals() only
        #works for powder data, however this function getMPLParams() is called
        #by either powder or SC processing.  For now, just disabling this
        #check...
        """
        aligned=set1DBinVals(self,__ws)
        if aligned!=1:
            #case to exit out of plotting data
            dialog=QtGui.QMessageBox(self)
            dialog.setText("Problem: Unaligned data thus unable to determine plot units - Returning")
            dialog.exec_()
            return      
        """
    
    
    #get plot info common to both 2D and 1D plots
    #need to retrieve plot config settings to perform the plot
    #line color
    linecolor=str(self.ui.MPLcomboBoxColor.currentText())
    print "line color: ",linecolor

    #line style
    sindx=self.ui.MPLcomboBoxLineStyle.currentIndex()
    if sindx == 0:
        style='-'
    elif sindx == 1:
        style='--'
    elif sindx == 2:
        style='-.'
    elif sindx == 3:
        style=':'
    else:
        style=''

    markercolor=str(self.ui.MPLcomboBoxColorMarker.currentText())
    print "marker color: ",markercolor
    msindx=self.ui.MPLcomboBoxMarker.currentIndex()
    print "marker index: ",msindx
    if msindx == 0:
        mstyle='o'
    elif msindx == 1:
        mstyle='v'
    elif msindx == 2:
        mstyle='^'
    elif msindx == 3:
        mstyle='<'
    elif msindx == 4:
        mstyle='>'
    elif msindx == 5:
        mstyle='s'
    elif msindx == 6:
        mstyle='p'
    elif msindx == 7:
        mstyle='*'
    elif msindx == 8:
        mstyle='h'
    elif msindx == 9:
        mstyle='H'
    elif msindx == 10:
        mstyle='+'
    elif msindx == 11:
        mstyle='x'
    elif msindx == 12:
        mstyle='D'
    elif msindx == 13:
        mstyle='d'
    elif msindx == 14:
        mstyle='|'
    elif msindx == 15:
        mstyle='_'
    elif msindx == 16:
        mstyle='.'
    elif msindx == 17:
        mstyle=','
    elif msindx == 18:
        mstyle=''
    else:
        mstyle=''            
    
    print "mstyle: ",mstyle

    #get plot title
    try:
        plttitle=str(self.ui.MPLlineEditLabelsTitle.text())
    except:
        plttitle=''
    print "plttitle: ", plttitle

    try:
        pltlegend=str(self.ui.MPLlineEditLabelsLegend.text())
    except:
        pltlegend=''
    print "pltlegend: ",pltlegend

    #get location placement for the legend
    legloc=str(self.ui.MPLcomboBoxLegendPos.currentText())
    
    return __ws, NXDbins, NYDbins, linecolor, style, markercolor, mstyle, plttitle, pltlegend, legloc
    
    
def getSVValues(self):
    """
    Function to get the values from the Slice Viewer and provide them to the MPL tools
    
    """
    wsNames=mtd.getObjectNames()
    cntws=0    #line workspace counter
    lcnt=-1    #workspace counter (not crazy with this choice of variable name here)
    indxws=-1  #index of line workspace
    wslst=[]   #list to contain base workspace names to be used in case multiple sliceviewers can be imported from
    for tws in wsNames:
        lcnt+=1
        pos=tws.find('_line') #look for line workspaces created by SliceViewer
        if pos > 0:
            #case we found a line workspace
            cntws+=1
            indxws=lcnt
            #extract base workspacename and append this to the list
            tmpbase=tws.split('_line')
            wslst.append(tmpbase[0])

    #now check for problems
    if lcnt < 0 or cntws == 0 or indxws < 0:
        #case with a problem
        print "Unable to locate a line workspace"
        print "Current Mantid workspaces: ",mtd.getObjectNames()
        dialog=QtGui.QMessageBox(self)
        dialog.setText("No workspaces from Slice Viewer Available - Returning to Powder Cut GUI")
        dialog.exec_()
        return
    else:
        pass
    if cntws > 1:
        print "Ambiguous case where more than one line workspace was discovered"
        print "wslst: ",wslst
        #wsSel is a base workspace name, not a line workspace name
        wsSel,ok = QtGui.QInputDialog.getItem(self,"Available Workspaces","Select from the list:",wslst)
        if ok==False:
            #case where a selction was cancelled - exit out of method 
            print "No workspace selected - returning"
            return
        print "Selected Workspace: ",wsSel," OK/Cancel: ",ok
        
        wsSel=str(wsSel)  #convert from QString to string
        wsLine=wsSel+'_line'
        
        """
        #in this case, check which workspaces are selected in the Workspace Manager and take the
        #corresponding _line workspace
        table=self.ui.tableWidgetWorkspaces 
        #need to determine which workspaces are selected 
        Nrows=table.rowCount()
        wslst=[]  #to contain the list of currently selected workspaces
        for row in range(Nrows):
            cw=table.cellWidget(row,self.WSM_SelectCol) 
            cbstat=cw.isChecked()
            if cbstat:
                wslst.append(str(table.item(row,self.WSM_WorkspaceCol).text()))
        #now from the list of selected workspaces, check which one has a corresponding "_line" workspace
        #we now have wsNames with the complete list of Mantid workspaces 
        #we also constructed wslst which contains the list of selected workspaces
        #so we need to iterate thru one list to see if any workspaces are contained in the other list
        for ws in wslst:
            if any(ws in w for w in wsNames):
                #if true, we've found the workspace from Workspace Manager that corresponds to Slice Viewer
                #Need to check if Slice Viewer can take more than one workspace in at a time as this case may 
                #need to be handled more carefully
                wsSel=ws  
        """
        
    else:
        #case with just a single _line workspace
        wsLine=wsNames[indxws]
        wsSel=wsLine.split('_line')
        wsSel=wsSel[0] #convert from list to str 
        
    """
    In getting to this point, we assume:
        wsSel is the original workspace selected in MSlice Workspace Manager
        wsLine is the corresponding line workspace
        both are string names for the workspaces
    """
        
    #At this point we currently assume that we have one selected workspace and one corresponding _line workspace
    print "  wsSel:  ",wsSel," workspace exists: ",mtd.doesExist(wsSel)
    print "  wsLine: ",wsLine," workspace exists: ",mtd.doesExist(wsLine)
    print "  available workspaces: ",mtd.getObjectNames()
    #Need to retrieve these workspaces from the Mantid layer
    try:
        #verify that the _line workspace exists 
        __lws=mtd.retrieve(wsLine)
    except:
        #else handle that it does not
        dialog=QtGui.QMessageBox(self)
        dialog.setText("Missing _line workspace - try running Slice Viewer again - returning")
        dialog.exec_()
        return          
    
    """
    #used to debug externally using this workspace
    print "** type(__lws): ",type(__lws)
    SaveMD(__lws,Filename='C:\Users\mid\Documents\Mantid\Powder\zrh_1000_line.nxs')
    """
    
    if wsSel !='':
        #get the number of output bins
        NOutBins=__lws.getSignalArray().size
        #now determine the bin width size
        mx=__lws.getXDimension().getMaximum()
        mn=__lws.getXDimension().getMinimum()
        BWOut=(mx-mn)/NOutBins
        
        print "** BWOut XMAX: ",__lws.getXDimension().getMaximum()
        print "** BWOut XMIN: ",__lws.getXDimension().getMinimum()
        print "** BWOut YMAX: ",__lws.getYDimension().getMaximum()
        print "** BWOut YMIN: ",__lws.getYDimension().getMinimum()

    else:
        #case where the base workspace did't surface properly...warn and return
        dialog=QtGui.QMessageBox(self)
        dialog.setText("Unable to identify a base workspace name from line workspace - Returning")
        dialog.exec_()
        return            
                
    #  Getting the list of workspaces in the MPL combobox:
    NMPLCombo=self.ui.MPLcomboBoxActiveWorkspace.count()
    #Some workspace management going on here:
    #  * Merge and BinMD workspace is something like: 'HYS_11356_msk_tube_spe_SCProj_histo'
    #  * BinMD appends '_histo' to this workspace name
    #  * However need to use the Merge workspace name for MPL1DCut tool which is minus the _histo so that new plots can reuse the Merge workspace into BinMD
    #  * Thus strip off the _histo from the workspace name to get back to the Mrg (merged) workspace
    wsSelMrg=wsSel
    wsSelMrg=wsSelMrg.split('_histo')
    wsSelMrg=wsSelMrg[0]
    if NMPLCombo >0:
        #case where there are more than 0 workspaces in the list
        wsMPLCombo=[str(self.ui.MPLcomboBoxActiveWorkspace.itemText(i)) for i in range(NMPLCombo)]
        indx=wsMPLCombo.index(wsSelMrg)
        print " wsMPLCombo: ",wsMPLCombo
    #now check if wsSelMrg is already on the list
    if any(wsSelMrg in w for w in wsMPLCombo):
        #case where it's already in the list so set this 2D workspace as the 
        #current workspace in the MPL workspace selection combo box
        self.ui.MPLcomboBoxActiveWorkspace.setCurrentIndex(indx)
        pass
    else:
        #case to add the workspace to the list
        self.ui.MPLcomboBoxActiveWorkspace.insertItem(NMPLCombo,wsSelMrg)
        self.ui.MPLcomboBoxActiveWorkspace.setCurrentIndex(NMPLCombo)
        
    #At this point, need to branch according to SC or Powder
    if self.ui.mode == 'SC':
        #get parameters from line workspace
        params = getSVValuesSC(self,__lws)
        #update MPL GUI with these parameters
        fill1DCutGUIParms(self,params)
        #plot results
        DoSCPlotMSlice(self)
        #mtd.remove(__lws.name()) #used for debugging
        
    elif self.ui.mode == 'Powder':
        getSVValuesPowder(self,__lws)
        
    else:
        print "Undefined mode - returning"
        return
        