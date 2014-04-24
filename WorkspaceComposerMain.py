################################################################################
#
# WorkspaceComposerMain.py
#
# April 16, 2014 - original check-in
#
# WorkspaceComposerMain.py is a main program that is called as a child from
# MSlice.py.  WorkspaceComposerMain.py depends upon it's GUI construction from
# WorkspaceComposer.py, in turn, from WorkspaceComposer.ui
#
# The purpose of WorkspaceComposerMain is to provide the user the ability to
# group or add workspaces.  It also gives the user the ability to edit exiting
# workspaces (add or remove workspaces).  Thus WorkspaceComposerMain depends
# upon Mantid workspaces.
#
################################################################################

import sys,os,time
from WorkspaceComposer import *
from PyQt4 import Qt, QtCore, QtGui
#import h5py 
from MSliceHelpers import getReduceAlgFromWorkspace 
#import inspect  #used for debugging purposes
#import Mantid computatinal modules
sys.path.append(os.environ['MANTIDPATH'])
from mantid.simpleapi import *

class WorkspaceComposer(QtGui.QMainWindow):

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_WorkspaceComposer()
        self.ui.setupUi(self)
        self.setWindowTitle("Workspace Composer")
        self.parent=parent #is this a legitimate way to provide parent info to other class methods?  Seems to work - don't know if things can get out of sync doing it this way though...
        print "parent: ",parent
        print "parent.ui: ",parent.ui
        print "QtGui.QMainWindow: ",QtGui.QMainWindow
        QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL('accepted()'), self.buttonBoxOK)
        print "got here 2"
        QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL('accepted()'),parent.on_button_clicked) #use this signal - slot connect to enable the WorkspaceComposer to communicate with the calling widget
        QtCore.QObject.connect(self.ui.pushButtonUpdate, QtCore.SIGNAL('clicked(bool)'), self.Update)
        QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL('rejected()'), self.Exit)
        #get WorkSpaceManager table index
        WSMIndex=self.parent.ui.WSMIndex
        if WSMIndex == -1:
            #case to create a new workspace group
            pass
        else:
            #case to edit an existing workspace group
            #will need to access the workspace manager table and extract workspace group name
            #upon Group Editor initialization will need to populate the table using info from the Workspace Group passed in
            table=self.ui.tableWidgetWGE
            gwsName=str(self.parent.ui.GWSName)
            print "Group Workspace Name: ",gwsName
            #next need to parse the group workspace for individual workspaces for two things:
            #   1. workspace name
            #   2. workspace file location
            
            thisGWS=mtd.retrieve(gwsName)
            try:
                #case for a group workspace
                Nrows=thisGWS.size()
                for row in range(Nrows):
                    wsName=thisGWS[row].name()
#                    wsFile=os.path.normpath(r'C:\Users\mid\Documents\Mantid\Wagman\autoreduce\\'+wsName+'.nxs')  #for now just hard code path name...will eventually need to dig this out of workspace
                    wsFile=''
                    addWStoTable(table,wsName,wsFile)

            except AttributeError:
                #else a single workspace does not have a size attribute and here we're currently only working with group workspaces
                pass
                
    
    
    def buttonBoxOK(self):
        "OK button pressed"
        self.parent.ui.progressBarStatusProgress.setValue(0)
        self.parent.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Workspace Composer Creating Workspace(s)")
        #get info from the widget
        #create a group workspace:
        #  1. extract a list each of file names and locations from table
        #  2. load workspaces using filenames
        #  3. pass workspace names
        
        #get constants
        const=constants()
        
        #first clean up empty rows
        table=self.ui.tableWidgetWGE  
        Nrows=table.rowCount()
        cnt=0
        delrowcntr=0
        statusMsg=''
        for row in range(Nrows):
            print "*** Row: ",row
            
            item=table.item(row,const.WGE_WorkspaceCol) #need to convert item from Qstring to string for comparison to work
            itemStr=str(item)
            print "itemStr: ",itemStr
            if itemStr != 'None':
                print "row: ",row,"  chkTxt: ",itemStr
                cnt +=1
            else:
                print "delete row: ",row
                table.removeRow(row-delrowcntr)
                delrowcntr += 1
                print "Rows remaining: ",table.rowCount()             
        
        self.parent.ui.progressBarStatusProgress.setValue(10) #update progress bar
        #get workspace Group Edit table
        table=self.ui.tableWidgetWGE  
        Nrows=table.rowCount()
        names=[]
        locs=[]
        #build the filename and locations lists
        for row in range(Nrows):          
            str1=str(table.item(row,const.WGE_WorkspaceCol).text())
            names.append(str1)
            str2=str(table.item(row,const.WGE_LocationCol).text())
            locs.append(str2)
        
        #get WorkSpaceManager table index
        WSMIndex=self.parent.ui.WSMIndex
        if WSMIndex == -1:
            #case to create a new workspace group
            #here we just take the workspace files listed in the workspace editor table and create a workspace

            
            #get the Sum Workspaces flag
            if self.ui.checkBoxSumWorkspaces.checkState():
                operator='+'  #if checked, sum workspaces
            else:
                operator=','  #otherwise, keep workspaces separate
            
            #load workspaces    
            loadstr=''
            for row in range(Nrows):
                locpath=os.path.normpath(locs[row])
                if row < Nrows-1:
                    loadstr=loadstr+locs[row]+operator
                else:
                    loadstr=loadstr+locs[row]
                
    #        print "wsnames.id: ",wsnames.id
                
            #create a Group Workspace
            gwsName=str(self.ui.lineEditGroupName.text())
            print "loadstr: ",loadstr
            print "GWName: ",gwsName
            print "Loading Workspaces to Group"
            if self.ui.checkBoxSumWorkspaces.checkState():
                self.parent.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Workspace Composer Loading Summed Workspace: "+str(gwsName))
            else:
                self.parent.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Workspace Composer Loading Workspace: "+str(gwsName))
            self.parent.ui.progressBarStatusProgress.setValue(25) #update progress bar    
            Load(Filename=loadstr,OutputWorkspace=gwsName)  #using a string containing a list of files, create the workspace
            
            #FIXME - this would be the place to do a workspace compatibility check once the workspaces have been loaded in and can be tested
#            if self.ui.checkBoxEnforceCompatibility.checkState():
                
            self.parent.ui.progressBarStatusProgress.setValue(75) #update progress bar
            val=self.ui.lineEditGroupComment.text()
            print "Group Comment: ",val            
            
            
        else:
            #case to edit an existing workspace group
            #The strategy here is to compare the list of names in the workspace versus the names in the workspace group edit table
            #Then delete the workspaces not in table and add those in the table but not yet in the workspace group
            
            #will need to access the workspace manager table and extract workspace group name
            gwsName=str(self.parent.ui.GWSName)
            print "Group Workspace Name: ",gwsName
            thisGWS=mtd.retrieve(gwsName)
            NGWS=thisGWS.size()  #number of workspaces within the existing group of workspaces
            GWSNames=[]
            for n in range(NGWS):
                GWSNames.append(thisGWS[n].name())  #build a list of names
                
            #now that we have the names of the workspaces and table entries, compare and adjust the table
            #add and remove workspaces by using the workspace names
            #to add will also have to load the workspace so that it can be added to the group
            
            #first do the removes
            s2=set(names)
            print "s2: ",s2
            for n in range(NGWS):
                s1=set([GWSNames[n]])
                intersect=s1.intersection(s2)
                print "n: ",n,"  s1: ",s1,"  removes intersect: ",intersect
                if intersect == set([]):
                    #case where workspace not found in the table, so remove it
                    thisGWS.remove(GWSNames[n])
                
            #now do the adds
            s2=set(GWSNames)
            print "s2: ",s2
            for row in range(Nrows):
                s1=set([names[row]])
                intersect=s1.intersection(s2)
                print "row: ",row,"  s1:",s1,"  adds intersect: ",intersect
                if intersect == set([]):
                    #case where table workspace not found in group workspace - so add it
                    #first load the workspace from file
                    percentbusy=int(float(row+1)/float(Nrows))*100
                    self.parent.ui.progressBarStatusProgress.setValue(percentbusy) #update progress bar
                    Load(Filename=locs[row],OutputWorkspace=names[row])
                    
                    #FIXME - place to consider incorporating a workspace compatibility check
#                    if self.ui.checkBoxEnforceCompatibility.checkState():
                    
                    #then add it to the group
                    thisGWS.add(names[row])
                    
            #now that we have the correct set of workspaces in the group, check if they are to be summed
            #get the Sum Workspaces flag
            #FIXME - need to determine the correct mantid algorithm for summing workspaces
            if self.ui.checkBoxSumWorkspaces.checkState():
                operator='+'  #if checked, sum workspaces
            else:
                operator=','  #otherwise, keep workspaces separate
                    
            #during development, display what we did...
            NGWSchk=thisGWS.size()  #number of workspaces within the existing group of workspaces
            print "*** check resulting group: ***"
            for n in range(NGWSchk):
                print "n: ",n,"  workspace: ",thisGWS[n].name()         

        #for now, get group workspace type from the workspace group edit table
        #when enforcing workspace consistency, this approach is reasonable
#        gwsType=str(table.item(row,const.WGE_DataTransformCol).text())

        ws=mtd.retrieve(names[0])
        print "ws: ",ws
        print "wstype: ",type(ws)
        print "mtd.getObjectNames(): ",mtd.getObjectNames()
        gwsType=getReduceAlgFromWorkspace(ws)  #FIXME - for now, just use the type from the first workspace, eventually ws type consistency needs to be checked.
        print "gwsType: ",gwsType
        
        
        #now let's determine the size of the group workspace
        thisGWS=mtd.retrieve(gwsName)
        Nws=thisGWS.size()
        gwsSize=0
        for n in range(Nws):
            gwsSize += thisGWS[n].getMemorySize()
        gwsSize=int(float(gwsSize)/float(1024*1024))
        gwsSize=str(gwsSize)+' MB'
        
        
        #remnants of passing stuff back and forth between parent and child apps
#        print "self.parent.ui.someval: ",self.parent.ui.someval
#        self.parent.ui.someval=42
        self.parent.ui.progressBarStatusProgress.setValue(100) #update progress bar
        self.parent.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Workspace Composer Workspace Create Complete")
        print "gwsName: ",gwsName,"  gwsType: ",gwsType
        self.parent.ui.GWSName=gwsName
        self.parent.ui.GWSType=gwsType  #need to get workspace type from the newly created workspace
        self.parent.ui.GWSSize=gwsSize
        self.parent.mySignal.emit()
        #now that we have the info we need, destroy the WorkspaceComposer
        self.close()      
        time.sleep(0.5)   
        self.parent.ui.progressBarStatusProgress.setValue(0) #update progress bar
        
    def Update(self):
        #case to check the radio buttons and perform accordingly
        
        #get constants
        const=constants()
        
        #get workspace Group Edit table
        table=self.ui.tableWidgetWGE
        
        #first clean up empty rows
        Nrows=table.rowCount()
        cnt=0
        delrowcntr=0
        statusMsg=''
        for row in range(Nrows):
            print "*** Row: ",row
            
            item=table.item(row,const.WGE_WorkspaceCol) #need to convert item from Qstring to string for comparison to work
            itemStr=str(item)
            print "itemStr: ",itemStr
            if itemStr != 'None':
                print "row: ",row,"  chkTxt: ",itemStr
                cnt +=1
            else:
                print "delete row: ",row
                table.removeRow(row-delrowcntr)
                delrowcntr += 1
                print "Rows remaining: ",table.rowCount()      
                
        #update the number of rows following clean-up
        Nrows=table.rowCount()        
        
        #get WorkSpaceManager table index
        WSMIndex=self.parent.ui.WSMIndex
        print "WSMIndex: ",WSMIndex
        
        if WSMIndex == -1:
            #case to create a new workspace group
            WSGroup='LocalGroup'
            pass
        else:
            #case to edit an existing workspace group
            #will need to access the workspace manager table and extract workspace group name
            gwsName=str(self.parent.ui.GWSName)
            print "Group Workspace Name: ",gwsName
            thisGWS=mtd.retrieve(gwsName)
        
        #first, determinw which is selected
        if self.ui.radioButtonChooseWorkspace.isChecked():
            #case to select workspaces
            print "Choose Workspace Selected"
                
            curdir=os.curdir
            filter='*.nxs'
            wsFiles = QtGui.QFileDialog.getOpenFileNames(self, 'Open Workspace(s)', curdir,filter)
  		
            for wsFile in wsFiles:
                #eventually wsName will be read from the file but for now extract it from filename
                #determine the common part from the filenames to use as the suggested workspace name
                cp=os.path.basename(str(wsFile))
                print "cp: ",cp
                splt=os.path.split(str(cp))
                print "splt: ",splt
                basename=os.path.basename(splt[-1]).split('.')[0] 
                print "basename: ",basename
                wsName=basename
                print "wsFile: ",wsFile
                addWStoTable(table,wsName,wsFile)
#            table.resizeColumnsToContents();
                    
            self.ui.labelNumWorkspaces.setText('Number of Workspaces:  '+str(cnt))
            if statusMsg == '':
                statusMsg=' Workspace Select OK'
            self.ui.labelStatusMsg.setText('Status Message: '+statusMsg)
            
        elif self.ui.radioButtonSelectAll.isChecked():
            print "Select All Selected"
            #first check if there are any rows to update selection
            item=table.item(0,const.WGE_WorkspaceCol) #need to convert item from Qstring to string for comparison to work
            itemStr=str(item)
            print "itemStr: ",itemStr
            #then only update the rows if rows with content are discovered.
            if itemStr != 'None':
                Nrows=table.rowCount()
                for row in range(Nrows):
                    addCheckboxToWSTCell(table,row,const.WGE_SelectCol,True)
            
            
        elif self.ui.radioButtonClearAll.isChecked():
            print "Clear All Selected"
            #first check if there are any rows to update selection
            item=table.item(0,const.WGE_WorkspaceCol) #need to convert item from Qstring to string for comparison to work
            itemStr=str(item)
            print "itemStr: ",itemStr
            #then only update the rows if rows with content are discovered.
            if itemStr != 'None':
                Nrows=table.rowCount()
                for row in range(Nrows):
                    addCheckboxToWSTCell(table,row,const.WGE_SelectCol,False)            
            
        elif self.ui.radioButtonRemoveSelected.isChecked():
            print "Remove Selected Selected"
            #first check if there are any rows to update selection
            item=table.item(0,const.WGE_WorkspaceCol) #need to convert item from Qstring to string for comparison to work
            itemStr=str(item)
            print "itemStr: ",itemStr
            #then only update the rows if rows with content are discovered.
            if itemStr != 'None':
                Nrows=table.rowCount()
                roff=0
                rcntr=0
                for row in range(Nrows):
                    #get checkbox status            
                    cw=table.cellWidget(row-roff,const.WGE_SelectCol) 
                    try:
                        cbstat=cw.isChecked()
                        print "row: ",row," cbstat: ",cbstat
                        if cbstat == True:
                            #case to remove a row
                            rcntr=row-roff
                            if rcntr < 0:
                                rcntr=0
                            print "   rcntr: ",rcntr
                            #need to check if workspace exists and if so, remove it - also need to think about the consequences of removing a workspace with regards to other workspaces it may be in...
                            #for now, just removing the row from the table
                            
                            delws=str(table.item(row,const.WGE_WorkspaceCol).text())
                            self.parent.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Workspace Composer Removing: "+delws)
                            table.removeRow(rcntr)
                            roff += 1
                    except AttributeError:
                        #case where rows have been deleted and nothing do check or do
                        pass

        else:
            print "No radio buttons selected - do nothing"
        
    def resizeEvent(self,resizeEvent):

#       segment to inspect members of the main widget
#        mems=inspect.getmembers(self.ui.centralwidget)
#        for name,value in mems:
#            print name,value
#        print "Geometry: ",self.ui.centralwidget.geometry()

        geom=self.ui.centralwidget.geometry() #returns a QRect structure - use methods to get values
        print "geom: ",geom
        print "height: ",geom.height()

        self.ui.tableWidgetWGE.setGeometry(QtCore.QRect(geom.x()+10, geom.y()+20, 751, geom.height()-25))  #hard coded numbers from QTableWidget x,y,width,height defined via QT Designer - need a more automatic way to get this info

    def closeEvent(self,event):
        #case when 'X' selected to destroy widget
        print "Handling Workspace Group Edit GUI Close"
        self.parent.ui.pushButtonUpdate.setEnabled(True)
        event.accept()
        
    def Exit(self):
        #case when cancel button is clicked
        print "Cancel Button clicked"
        self.parent.ui.pushButtonUpdate.setEnabled(True)
        self.close()
        

#************* beginning of global functions and classes ****************

class constants:
    def __init__(self):
        self.WGE_WorkspaceCol=0
#        self.WGE_DataTransformCol=1
        self.WGE_LocationCol=1
        self.WGE_DateCol=2
        self.WGE_SizeCol=3
        self.WGE_SelectCol=4
        

def addWStoTable(table,workspaceName,workspaceLocation):
    #function to add a single workspace to the workspace manager table
	# workspaces may originate from create workspace or the list of files
	
    #get constants
    const=constants()
    
    if workspaceLocation != '':
        print "addWStoTable workspaceName: ",workspaceName
        print "workspaceLocation: ",workspaceLocation
        

    
        #then get info about the workspace file
        ws_date=str(time.ctime(os.path.getctime(workspaceLocation)))
        ws_size=str(int(round(float(os.stat(workspaceLocation).st_size)/(1024*1024))))+' MB'
        
        #also need the Mantid Algorithm used to create the workspace
        #for now, this will be obtained by reading the workspace as an HDF file and
        #extracting the algorithm information.
    
#        h5WS=h5py.File(str(workspaceLocation),'r')
#        WSAlg=getReduceAlgFromH5Workspace(h5WS)
        
#        WSAlg=getReduceAlgFromWorkspace(workspaceName)
        
#        if WSAlg == "":
#            WSAlg="Not Available"
#            WSAlg="DgsReduction.."  #hard coded for now...
    else:
        ws_date=''
        ws_size=''
        WSAlg=''
    

    #two cases of rows:
    #    1. Case where all or some rows are empty and just add directly to first available row
	#    2. Case where all rows have content and need to add a row in this case
	
    #First determine if there is an open row
    #need to determine the available row number in the workspace table
    Nrows=table.rowCount()
    print "Nrows: ",Nrows

    emptyRowCnt=0
    emptyRows = []

    # determine how many empty rows
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
        col=const.WGE_SelectCol
#        addComboboxToWSTCell(table,userow,col)
        addCheckboxToWSTCell(table,userow,col,False)

    #now add the row		
    table.setItem(userow,const.WGE_WorkspaceCol,QtGui.QTableWidgetItem(workspaceName)) #Workspace Name 
    table.setItem(userow,const.WGE_LocationCol,QtGui.QTableWidgetItem(workspaceLocation)) #Workspace Location (path+file) 
    table.item(userow,const.WGE_LocationCol).setFont(QtGui.QFont('Courier',10))
    table.setItem(userow,const.WGE_DateCol,QtGui.QTableWidgetItem(ws_date)) 
    table.setItem(userow,const.WGE_SizeCol,QtGui.QTableWidgetItem(ws_size)) 
    addCheckboxToWSTCell(table,userow,const.WGE_SelectCol,True)	
#    table.setItem(userow,const.WGE_DataTransformCol,QtGui.QTableWidgetItem(WSAlg))   
    
         
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
#    table.setCellWidget(row,col, QW)     #this method of setting the checkbox would be preferrable if I could figure out how to access the isChecked() status when using an embedding widget

if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    wcapp = WorkspaceComposer()
    wcapp.show()
    sys.exit(app.exec_())