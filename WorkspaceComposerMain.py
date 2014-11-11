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
import re #regular expressions needed to work with equation parsing
from numpy import *
import config  #bring in configuration parameters and constants

class WorkspaceComposer(QtGui.QMainWindow):

    mySignal = QtCore.pyqtSignal(int)  #establish signal for communicating from Workspace Composer to MSlice - must be defined before the constructor

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_WorkspaceComposer()
        self.ui.setupUi(self)
        self.setWindowTitle("Workspace Composer")
        self.parent=parent #is this a legitimate way to provide parent info to other class methods?  Seems to work - don't know if things can get out of sync doing it this way though...
        print "parent: ",parent
        print "parent.ui: ",parent.ui
        print "QtGui.QMainWindow: ",QtGui.QMainWindow
        QtCore.QObject.connect(self.ui.pushButtonDone, QtCore.SIGNAL('clicked(bool)'), self.closeEvent)
        print "got here 2"
        
        #get constants
        const=constants()        
        
#        QtCore.QObject.connect(self.ui.pushButtonCreateWorkspace, QtCore.SIGNAL('clicked(bool)'),parent.on_button_clicked) #use this signal - slot connect to enable the WorkspaceComposer to communicate with the calling widget
        QtCore.QObject.connect(self.ui.pushButtonCreateWorkspace, QtCore.SIGNAL('clicked(bool)'), self.CreateWorkspace)

# Two methods shown here for signaling the on_button_clicked slot - one more generic using clicked, and a second using a custom signal which has the potential to give more fine grained control
#        QtCore.QObject.connect(self.ui.pushButtonCreateWorkspace, QtCore.SIGNAL('clicked(bool)'),parent.on_button_clicked) #use this signal - slot connect to enable the WorkspaceComposer to communicate with the calling widget
        self.mySignal.connect(parent.on_button_clicked)


        QtCore.QObject.connect(self.ui.pushButtonUpdate, QtCore.SIGNAL('clicked(bool)'), self.Update)
#        QtCore.QObject.connect(self.ui.pushButtonDone, QtCore.SIGNAL('clicked(bool)'), self.Exit)
        #get WorkSpaceManager table index
        WSMIndex=self.parent.ui.WSMIndex
        print "--> WSMIndex: ",WSMIndex
        if WSMIndex == []:
            #case to create a new workspace group
            #in this case, suggest a unique new workspace name
            #first, get existing workspace names
            BaseNameStr='NewWorkspace'
            ewn=mtd.getObjectNames()  #get existing workspace names
            cntr=0      #set workspace name check counter to 0
            Ncntr=1000  #pick an upper number of unique names to select
            while cntr < Ncntr:
                NewNameStr=BaseNameStr+'_'+str(cntr)
                if NewNameStr not in ewn:
                    cntr=Ncntr  #terminate while loop
                    self.ui.lineEditGroupName.setText(NewNameStr) #set unique name in the lineEdit field
                else:
                    cntr +=1  #increment loop counter and try again to find a unique name
        else:
            #case to edit an existing workspace or set of workspaces
            #will need to access the workspace manager table and extract workspace group name
            #upon Group Editor initialization will need to populate the table using info from the Workspace Group passed in
            table=self.ui.tableWidgetWGE
            if len(self.parent.ui.GWSName) == 1:
                #in this case, we have a single workspace name.
                #this could be a single workspace or a grouped workspace
                #if single, just display it
                #if group, display group contents
                gwsName=self.parent.ui.GWSName[0]
                print "gwsName: ",gwsName," type: ",type(gwsName)
                thisGWS=mtd.retrieve(gwsName)
                if 'Group' in str(type(thisGWS)):
                    #case where the workspace is a group workspace
                    #then list each file in the workspace
                    Nrows=thisGWS.size()
                    inMemCntr=0
                    for row in range(Nrows):
                        wsName=thisGWS[row].name()
    #                    wsFile=os.path.normpath(r'C:\Users\mid\Documents\Mantid\Wagman\autoreduce\\'+wsName+'.nxs')  #for now just hard code path name...will eventually need to dig this out of workspace
                        wsFile=''
                        WCaddWStoTable(table,wsName,wsFile)
                        print "row: ",row,"  wsName: ",wsName,"  Type: ",type(wsName)
                        if mtd.doesExist(wsName):
                            #if it exists, then it's in memory and say this
                            table.item(row,const.WGE_InMemCol).setText("Yes")
                            #also give the memory footprint size
                            #first need to determine if workspace is a group workspace or single workspace
                            tmpws = mtd.retrieve(wsName)
                            inMemCntr +=1 #increment the in memory counter
                    sz=0
                    row=0
                    for ws in thisGWS:
                        sz = ws.getMemorySize()       
                        SizeStr=str(int(float(sz)/float(1024*1024)))+' MB'
                        table.item(row,const.WGE_SizeCol).setText(SizeStr)
                        row +=1
                    
                else:
                    #case where it's an individual workspace - just list the one workspace
                    wsName=thisGWS.name()
                    wsFile=''
                    WCaddWStoTable(table,wsName,wsFile)                    
                    if mtd.doesExist(wsName):
                        table.item(0,const.WGE_InMemCol).setText("Yes")
                    sz=thisGWS.getMemorySize()
                    szStr=str(int(float(sz)/float(1024*1024)))+' MB'
                    table.item(0,const.WGE_SizeCol).setText(szStr)                    
                    
                #also need to push this name to the resulting workspace name field
                self.ui.lineEditGroupName.setText(gwsName)
                print "Group Workspace Name: ",gwsName
                #since workspace exists, enable Create Workspace button
                self.ui.pushButtonCreateWorkspace.setEnabled(True) 
            elif len(self.parent.ui.GWSName) > 1:
                #in this case we have more than one workspace name.
                #these workspaces have the potential to be of any type
                #here the workspaces are listed as they are named and groups are
                #not expanded for fear of losing track of which files are in which group
                Nws=len(WSMIndex)
                gwsName=self.parent.ui.GWSName
                print "--> gwsName: ",gwsName
                for row in range(Nws):
                    ws=mtd.retrieve(gwsName[row])
                    wsName=gwsName[row]
                    wsFile=''
                    WCaddWStoTable(table,wsName,wsFile)
                    print "row: ",row,"  wsName: ",wsName,"  Type: ",type(wsName)
                    if mtd.doesExist(wsName):
                        #if it exists, then it's in memory and say this
                        table.item(row,const.WGE_InMemCol).setText("Yes")
                    sz = ws.getMemorySize()       
                    if int(sz) == 0:
						#then check if this is a group workspace and get it's size accordingly
                        try:
                            sz=0
                            for wsr in ws:
                                sz += wsr.getMemorySize()
                        except:
                            pass
                    SizeStr=str(float(int(float(sz)/float(1024*1024)*10))/10)+' MB' #use *10 then /10 to show down to .1 MB
                    table.item(row,const.WGE_SizeCol).setText(SizeStr)                    
                #since workspace exists, enable Create Workspace button
                self.ui.pushButtonCreateWorkspace.setEnabled(True) 
    
    def CreateWorkspace(self):
        print "**** Create Workspace button pressed"
        self.parent.ui.progressBarStatusProgress.setValue(0)
        self.parent.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Workspace Composer Creating Workspace(s)")
        #get info from the widget
        #create a group workspace:
        #  1. extract a list each of file names and locations from table
        #  2. load workspaces using filenames
        #  3. pass workspace names
        
        #get constants
        const=constants()
        sigVal=config.mySigNorm
        
        #make sure all workspaces are available at the python level
#        mtd.importAll()

        #get WorkSpaceManager table index
        WSMIndex=self.parent.ui.WSMIndex
        print "WSMIndex: ",WSMIndex     
                        
        #first clean up empty rows
        table=self.ui.tableWidgetWGE  
        Nrows=table.rowCount()
        print "Nrows before cleaning table: ",Nrows
        cnt=0
        delrowcntr=0
        statusMsg=''
        if Nrows >0:
            
            for row in Nrows-arange(Nrows)-1:
                item=str(table.item(row,0))
                print "row: ",row," item: ",item,"  str(item): ",str(item)
                if item == 'None':
                    print "...Deleting row: ",row
                    table.removeRow(row)
        
        #now that the table has been cleaned up, redefine Nrows
        Nrows=table.rowCount()
        
        self.parent.ui.progressBarStatusProgress.setValue(10) #update progress bar
        #get workspace Group Edit table
#        table=self.ui.tableWidgetWGE  
        Nrows=table.rowCount()
        print "Nrows after cleaning table: ",Nrows
        names=[]
        locs=[]
        #build the filename and locations lists
        for row in range(Nrows):          
            str1=str(table.item(row,const.WGE_WorkspaceCol).text())
            names.append(str1)
            str2=str(table.item(row,const.WGE_LocationCol).text())
            locs.append(str2)
        
        if WSMIndex == []:
            #case to create a new workspace group
            #here we just take the workspace files listed in the workspace editor table and create a workspace

            #verify that the output workspace name 
            gwsName=str(self.ui.lineEditGroupName.text())
            ewn=mtd.getObjectNames()  #get existing workspace names
            if gwsName in ewn:
                dialog=QtGui.QMessageBox.question(self,'Message','Non-unique workspace name - overwrite existing workspace?',QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
#                dialog.exec_()
                if dialog == QtGui.QMessageBox.Yes:
                    #case to overwrite the current workspace name
                    sigVal=config.mySigOverwrite
                    pass
                else:
                    #case to re-select a name
                    dialog=QtGui.QMessageBox(self)
                    dialog.setText("Then return and please enter a unique workspace name")
                    dialog.exec_()
                    return

            
            
        else:
            #case to edit an existing workspace
            gwsName=str(self.parent.ui.GWSName)
            #in this case, automatically enable Create Workspace button
            self.ui.pushButtonCreateWorkspace.setEnabled(True) 
            pass
            
        #check which Task has been selected
        #Note that in the cases of grouping and summing that all workspaces in the table are used, not just those selected
        table=self.ui.tableWidgetWGE  
        Nrows=table.rowCount()
        if Nrows >0:
            if self.ui.radioButtonGroupWS.isChecked():
                print "** Group Workspaces"
                #case to group files into a workspace
                #get the list of workspaces to group
                
                #check if there are any table rows selected, if not, just return
                NwsSel=0
                for row in range(Nrows):
                    cw=table.cellWidget(row,const.WGE_SelectCol) 
                    if cw.isChecked():
                        NwsSel += 1
                        
                if NwsSel == 0:
                    #case with no workspaces to operate with - just return
                    return
                
                
                
                grpLst=[]
                gwsSize=0
                gwsName=str(self.ui.lineEditGroupName.text()) 
                print "check for overwrite"
                print "  gwsName: ",gwsName
                print "  GWSName: ",self.parent.ui.GWSName
                if gwsName in self.parent.ui.GWSName:
                    print "Overwrite Case"
                    sigVal=config.mySigOverwrite
                
                for row in range(Nrows):
                    percentbusy=int(100*(row+1)/Nrows)
                    self.parent.ui.progressBarStatusProgress.setValue(percentbusy) #update progress bar
                    ws=str(table.item(row,const.WGE_WorkspaceCol).text())
                    tmpws=mtd.retrieve(ws)
                    #special case to account for - first time thru with a non-grouped single workspace
                    #need to get the group name from the lineEditGroupName field else the new group gets put back into the
                    #original workspace name making things very confusing as to what just happened.
                    if Nrows ==1:
                        if 'IEventWorkspace' in str(type(tmpws)):
                            
                            sigVal=config.mySigNorm #usual case for 1 would otherwise be to overwrite
                            #need to figure out what to do here for case of moving to list from integers
                            self.parent.ui.WSMIndex=[1] #need to bump up the Workspace Manager table index too
                    cw=table.cellWidget(row,const.WGE_SelectCol) 
                    if cw.isChecked():
                        #only group those workspaces that are selected in the composer table
                        grpLst.append(ws)
                    if row ==0:
                        gwsType=getReduceAlgFromWorkspace(ws)  #FIXME - for now, just use the type from the first workspace, eventually ws type consistency needs to be checked.
                        print "gwsType: ",gwsType
                print "Group Name: ",gwsName
                print "Group List: ",grpLst
                exec("%s = GroupWorkspaces(%r)" % (gwsName,grpLst))
                tmpgws=mtd.retrieve(gwsName)
                gwsSize=0
                for gws in tmpgws:
                    gwsSize += gws.getMemorySize()
                gwsSizeStr=str(int(float(gwsSize)/float(1024*1024)))+' MB'
                print "mtd.getObjectNames(): ",mtd.getObjectNames() #checking if this worked or not 
            elif self.ui.radioButtonSumWS.isChecked():
                gwsName=str(self.ui.lineEditGroupName.text()) 
                #case to sum workspaces
                print "** Sum Workspaces"
                #case to sum workspaces already in memory into a new workspace
                #get the list of workspaces to sum
                
                #check if there are any table rows selected, if not, just return
                NwsSel=0
                for row in range(Nrows):
                    cw=table.cellWidget(row,const.WGE_SelectCol) 
                    if cw.isChecked():
                        NwsSel += 1
                        
                if NwsSel == 0:
                    #case with no workspaces to operate with - just return
                    return
                
                sumSize=0
                first=0
                for row in range(Nrows):
                    percentbusy=int(100*(row+1)/Nrows)
                    self.parent.ui.progressBarStatusProgress.setValue(percentbusy) #update progress bar
                    try:
                        cw=table.cellWidget(row,const.WGE_SelectCol) 
                        if cw.isChecked():
                            ws=str(table.item(row,const.WGE_WorkspaceCol).text())
                            if first == 0:
                                sumws=CloneWorkspace(ws)
                                #in case there is only one workspace, sumws won't be visible at the Mantid level, so add it
                                print "--sumws size: ",sumws.getMemorySize()/(1024*1024), "row: ",row," ws: ",ws, "sumws: ",sumws
                                sumType=getReduceAlgFromWorkspace(sumws)  #FIXME - for now, just use the type from the first workspace, eventually ws type consistency needs to be checked.
                                first +=1
                            #only sum selected workspaces
                            else:
                                print "**Performing Sum  row: ",row
                                sumws += mtd.retrieve(ws)
                            
                    except ValueError:
                        dialog=QtGui.QMessageBox(self)
                        dialog.setText("The workspaces are not compatible for summation")
                        dialog.exec_()
                        return    
     
                exec("%s = sumws" % (gwsName))
                eval("mtd.addOrReplace(%r,%s,)" % (gwsName,gwsName))       

                exec("sumSize=%s.getMemorySize()" % gwsName)  #get size of the output workspace
                sumSizeStr=str(int(float(sumSize)/float(1024*1024)))+' MB'
                gwsSizeStr=sumSizeStr
                gwsType=sumType
                print "mtd.getObjectNames(): ",mtd.getObjectNames() #checking if this worked or not            
            elif self.ui.radioButtonExecuteEqn.isChecked():
                #case to execute an equation a user has entered
                
                #check if an equation is to be processed 
                eqnstr=str(self.ui.lineEditEquation.text())
                if eqnstr != '':
                    #case where there appears to be an equation entered
                    print "Calculating Equation"
                    #determine number of workspaces in equation - convert string to upper case to reduce naming ambiguity when using workspace indicies ws0, Ws0 or WS0 for instance
                    UpperEqnStr=eqnstr.upper()  #equation string to work with where case is not an issue when discovering the ws* Ws* wS* WS* ways of representation
                    RplEqnStr=eqnstr #the replacement equation string will start with the original equation string
                    strts=[m.start() for m in re.finditer('WS',UpperEqnStr)]
                    Nws=len(strts) #number of workspaces in the equation
                    Nchars=len(eqnstr) #numbers of characters in the equation
                    if Nws >0:
                        print "Case to parse equation"
                        wsinames=[] #list to contain the workspace index names
                        for indx in range(Nws):
                            #for each workspace, determine how many numeric digits they have
                            #single workspace equation would look like: (ws1-ws2)/ws3
                            #not currently supporting a range of workspaces...would need to think more about how to implement this generally
                            
                            cntr=0
                            flag=True #used to make sure we're only checking for one workspace at a time and not traversing the entire list
                            for pos in range(Nchars-(strts[indx]+2)):
                                posoff=pos+(strts[indx]+2)
        #                        print "     pos: ",pos,"  posoff: ",posoff," UpperEqnStr[posoff]: ",UpperEqnStr[posoff]
                                #check if character is alphanumeric 
                                if UpperEqnStr[posoff].isalnum() and flag:
                                    #then make sure we have a number and not a character
                                    if not(UpperEqnStr[posoff].isalpha()):
                                        cntr+=1
                                else:
                                    flag=False
                            key=UpperEqnStr[strts[indx]:strts[indx]+cntr+2]  #adding 2 to count for the 'ws' characters in the string
                            wsinames.append(key) #update the list of workspace names
                            print "*** Indx: ",indx,"   Key: ",key,"  pos: ",pos,"  posoff: ",posoff,"  strts[indx]: ",strts[indx],"  cntr: ",cntr #FIXME: currently seeing incorrect keys here...
                        print "wsinames: ",wsinames
                        #now that we have the workspace index names, let's find the corresponding workspace names in the table
                        Nrows=table.rowCount()
                        cnt=0
                        replcntr=0
                        for row in range(Nrows):
                            print "*** Row: ",row
                            #obtain workspace index for current row
                            wsi=table.item(row,const.WGE_WSIndexCol).text()
                            wsiStr=str(wsi)
                            
                            #now check if there is a match between the current index and any from the equation
                            print " wsinames: ",str(wsinames),"  wsiStr: ",wsiStr.upper()
                            if str(wsinames).upper().find(wsiStr.upper()) > 0:
                                replcntr+=1
                                #case we found a match - now replace the index with the actual workspace name in the equation
                            
                                wsname=table.item(row,const.WGE_WorkspaceCol).text() #need to convert item from Qstring to string for comparison to work
                                if row == 0:
                                    #case to identify the first workspace and clone it for use as the container used by the output workspace
                                    clonews=CloneWorkspace(str(wsname))
                                wsnameStr=str(wsname)
                                RplEqnStr=RplEqnStr.replace(wsiStr,wsnameStr)
                                #make sure that workspace is at python layer
        #                        wsnameStr=mtd.retrieve(wsnameStr)
        #                        print " Workspace existance check: ",mtd.doesExist(wsnameStr)
        #                        print " Seeing if the workspace has surfaced: "
        #                        print " wsnameStr: ",wsnameStr
        #                        print " End WS check"
                        print "  **** Equation: ",RplEqnStr
                        if replcntr != Nws:
                            #case where the number of workspace name replacements does not match the number of workspace indicies in the equation
                            print "Workspace name mismatch...returning"
                            return
                                
                        
                    elif Nchars>0:
                        #case where workspace names rather than workspace indicies are given
                        RplEqnStr=str(self.ui.lineEditEquation.text())
                        print "  **** Equation(elif): ",RplEqnStr
                    else:
                        print "No workspaces identified in the equation...returning"
                        return
                        
                    #make sure all workspaces are at the python working level
                    mtdws=mtd.getObjectNames()
                    mtdlst=[]
                    Nmtdws=len(mtdws)
                    print "Nmtdws: ",Nmtdws
                    for wsi in range(Nmtdws):
                        thismtdws=mtdws[wsi]
                        mtdlst.append(mtd.retrieve(thismtdws))
                        print " ----------> Retrieved workspace: ",mtdlst[wsi].name()
                        print "             End retrieve"
                        
                    #if we get here, we have an algorithm to run!
                    try:
                        print "performing equation: ",RplEqnStr
                        outname=str(self.ui.lineEditGroupName.text())
                        print " outname: ", outname," type: ",type(outname)
                        print " RplEqnStr: ",RplEqnStr," type:",type(RplEqnStr)
                        self.parent.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Executing equation: "+outname+"="+RplEqnStr)
                        mtd.importAll()
                        exec ("%s = clonews" % outname)  #first equate a cloned workspace to outname
                        exec ("%s = %s" % (outname,RplEqnStr)) #now let the equation results be put into the cloned outname workspace 
                        print "**mtd.getObjectNames(): ",mtd.getObjectNames()
                        exec ("%s = mtd.retrieve(%r)" % (outname,outname)) #now make the output workspace available to python
                        print "........"
                        print "Result type of equation placed in workspace: ",outname
                        
                    except Exception, e:
                        print "Equation failed to execute...something is wrong, please check and try again"
                        print str(e)
                        print " Looking at variables in table: "
                        print " dir(): ",dir()
                        self.parent.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Equation failed to execute...please check and try again")
                        print "Workspaces in memory: ",mtd.getObjectNames()
                        return
                        
                    #if we get here, add the output workspace to the table
                    gwsName=outname
                    gwsType=getReduceAlgFromWorkspace(outname)
                    
                    OWS=mtd.retrieve(outname) # make sure output workspace is at the python layer
                    gwsSize = OWS.getMemorySize()
                    gwsSize=int(float(gwsSize)/float(1024*1024))
                    gwsSizeStr=str(gwsSize)+' MB'                
                         
            else:
                #should never get here...
                print "Undefined case - returning"
                return
             
        
            

        
        #remnants of passing stuff back and forth between parent and child apps
#        print "self.parent.ui.someval: ",self.parent.ui.someval
#        self.parent.ui.someval=42
        self.parent.ui.progressBarStatusProgress.setValue(100) #update progress bar
        self.parent.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Workspace Composer Workspace Create Complete")
        print "gwsName: ",gwsName,"  gwsType: ",gwsType,"  gwsSizeStr: ",gwsSizeStr
        self.parent.ui.returnType=gwsType  #need to get workspace type from the newly created workspace
        self.parent.ui.returnSize=gwsSizeStr
        self.parent.ui.returnName=str(self.ui.lineEditGroupName.text())
        print " mySignal:  sigval:",sigVal
        self.mySignal.emit(sigVal)

#        self.emit(QtCore.SIGNAL('mySignal'))
        
        #now that we have the info we need, destroy the WorkspaceComposer
#        self.close()      
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
        if Nrows > 0:
            for row in range(Nrows):
                print "*** Row: ",row
                try:
                    #try will work if the table row,col has any data
                    #in this case, do not delete the row in the table
                    item=table.item(row,const.WGE_WorkspaceCol).text() #need to convert item from Qstring to string for comparison to work
                    itemStr=str(item)
                    print "itemStr: ",itemStr
                except AttributeError:
                    #in this case we have an empty row to delete
                    print "delete row: ",row
                    table.removeRow(row-delrowcntr)
                    delrowcntr += 1
                    print "Rows remaining: ",table.rowCount()      
                
        #update the number of rows following clean-up
        Nrows=table.rowCount()        
        
        #get WorkSpaceManager table index
        WSMIndex=self.parent.ui.WSMIndex
        print "WSMIndex: ",WSMIndex
        
        if WSMIndex == []:
            #case to create a new workspace group
            WSGroup='LocalGroup'
            pass
        else:
            #case to edit an existing workspace group
            #will need to access the workspace manager table and extract workspace group name
            gwsName=self.parent.ui.GWSName
            print "Group Workspace Name: ",gwsName
#            thisGWS=mtd.retrieve(gwsName)  
        
        #first, determinw which is selected
        if self.ui.radioButtonLoadData.isChecked():
            #case to select workspaces
            print "Choose Workspace Selected"
            
            curdir=os.curdir
            filter='*.nxs'
            wsFiles = QtGui.QFileDialog.getOpenFileNames(self, 'Open Workspace(s)', curdir,filter)
            if len(wsFiles) > 0:
                self.parent.ui.WSMIndex=[]  #if workspaces are chosen, then enable those new workspaces to be loaded via the buttonBoxOK() procedure
            
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
                WCaddWStoTable(table,wsName,wsFile)  #adds a workspace to table from file

                    
            Nrows=table.rowCount()
            loadedWS=mtd.getObjectNames()
            if Nrows >0:
                for row in range(Nrows):
                    percentbusy=int(100*(row+1)/Nrows)
                    self.parent.ui.progressBarStatusProgress.setValue(percentbusy) #update progress bar
                    try:
                        item=table.item(row,const.WGE_WorkspaceCol).text() #need to convert item from Qstring to string for comparison to work
                        itemStr=str(item)
                        print "itemStr: ",itemStr                
    
                        if itemStr in loadedWS:
                            print "row: ",row,"  workspace: ",itemStr," is already in memory"
                            #then make sure that 'In Memory' shows this
                            table.item(row,const.WGE_InMemCol).setText("Yes")
                        else:
                            #Load this workspace into memory into the "Mantid Level"
                            #first get the location of the workspace file
                            WSFile=str(table.item(row,const.WGE_LocationCol).text())
                            print "Loading file: ",WSFile
                            Load(Filename=WSFile,OutputWorkspace=itemStr)
                            #now make workspace available at the python level
                            exec("%s = mtd.retrieve(%r)" % (itemStr,itemStr))     
                            #then update the in-memory column
                            table.item(row,const.WGE_InMemCol).setText("Yes")
							#case to generate the in-memory size of the workspace and replace the file size listed in the table
                        tmpws=mtd.retrieve(itemStr)
                        if 'Group' in str(type(tmpws)):
                        #case to get cumulative size for each member of the group in memory
                            sz=0
                            for ws in tmpws:
                                sz += ws.getMemorySize()
                        else:
                            sz=tmpws.getMemorySize()
                        ws_size=str(int(round(float(sz)/(1024*1024))))+' MB'
                        table.item(row,const.WGE_SizeCol).setText(ws_size)
                    except AttributeError:
                        #case where there is no row to use to load data
                        pass
            #once data have been loaded, then enable the Create Workspace button
            self.ui.pushButtonCreateWorkspace.setEnabled(True)                     
                    
#            table.resizeColumnsToContents();                    
            #for user convenience, automatically select the Load Data radio button

            
        elif self.ui.radioButtonSelectAll.isChecked():
            print "Select All Selected"
            
            Nrows=table.rowCount()
            if Nrows >0:
                for row in range(Nrows):
                    try:
                        item=table.item(row,const.WGE_WorkspaceCol).text() #need to convert item from Qstring to string for comparison to work
                        itemStr=str(item)
                        addCheckboxToWSTCell(table,row,const.WGE_SelectCol,True)
                    except AttributeError:
                        #case where the row is empty - do nothing
                        pass
            
            
        elif self.ui.radioButtonClearAll.isChecked():
            print "Clear All Selected"
            Nrows=table.rowCount()
            if Nrows >0:
                for row in range(Nrows):
                    try:
                        item=table.item(row,const.WGE_WorkspaceCol).text() #need to convert item from Qstring to string for comparison to work
                        itemStr=str(item)
                        addCheckboxToWSTCell(table,row,const.WGE_SelectCol,False)
                    except AttributeError:
                        #case where the row is empty - do nothing
                        pass     
            
        elif self.ui.radioButtonRemoveSelected.isChecked():
            print "Remove Selected Selected"
            #first check if there are any rows to update selection
            Nrows=table.rowCount()
            if Nrows >0:
                roff=0
                rcntr=0
                for row in range(Nrows):
                    try:
                        item=table.item(rcntr,const.WGE_WorkspaceCol).text() #need to convert item from Qstring to string for comparison to work
                        itemStr=str(item)
                        print "itemStr: ",itemStr
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
                                
                                delws=str(table.item(rcntr,const.WGE_WorkspaceCol).text())
                                self.parent.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Workspace Composer Removing: "+delws)
                                table.removeRow(rcntr)
                                roff += 1
                                #also remove this workspace from memory if it exists
                                try:
                                    #might want to rethink deleting the workspace at this point.
                                    #as deleting a workspace from memory also removes it from 
                                    #any other groups in memory that it may also be a member of
                                    #a possible alternative would be to delist the workspace leaving deletion for the Workspace Mgr
                                    #however in so doing, via the Workspace Mgr, there would be unreachable workspaces to delete within groups
                                    #so for now, this delete capability remains included within the workspace composer
                                    mtd.remove(delws)
                                except:
                                    #placeholder in case the workspace had not yet been loaded to memory - need to do nothing in this case
                                    pass
                        except AttributeError:
                            #case where rows have been deleted and nothing to check or do
                            pass
                    except:
                        #case with an empty row
                        pass
                                                    
        else:
            print "No radio buttons selected - do nothing"
        time.sleep(0.5)   
        self.parent.ui.progressBarStatusProgress.setValue(0) #update progress bar
        
        
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
        #Make sure that the table is empty before exiting
        table=self.ui.tableWidgetWGE  
        print "Removing rows"
        Nrows=table.rowCount()
        for row in range(Nrows):
            table.removeRow(row)
     
        print "Handling Workspace Group Edit GUI Close"
        self.parent.ui.pushButtonUpdate.setEnabled(True)
        self.parent.ui.WSMIndex = [] #clear the WSMIndex flag
        self.parent.ui.GWSName=[]
        self.parent.ui.GWSType=[]
        self.parent.ui.GWSSize=[]    
        self.close()
        
    def Exit(self):

        #Make sure that the table is empty before exiting
        table=self.ui.tableWidgetWGE  
        print ".Removing rows"
        Nrows=table.rowCount()
        for row in range(Nrows):
            table.removeRow(row)

        self.parent.ui.pushButtonUpdate.setEnabled(True)
        self.parent.ui.WSMIndex = []
        self.parent.ui.GWSName=[]
        self.parent.ui.GWSType=[]
        self.parent.ui.GWSSize=[]        
        self.close()
        

#************* beginning of global functions and classes ****************

class constants:
    def __init__(self):
        self.WGE_WSIndexCol=0
        self.WGE_WorkspaceCol=1
        self.WGE_LocationCol=2
        self.WGE_DateCol=3
        self.WGE_SizeCol=4
        self.WGE_InMemCol=5
        self.WGE_SelectCol=6
        

def WCaddWStoTable(table,workspaceName,workspaceLocation):
    #function to add a single workspace to the workspace manager table
	# workspaces may originate from create workspace or the list of files
	
    #get constants
    const=constants()
    
    if workspaceLocation != '':
        print "WCaddWStoTable workspaceName: ",workspaceName
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
    wsindex='ws'+str(userow)
    table.setItem(userow,const.WGE_WSIndexCol,QtGui.QTableWidgetItem(wsindex))
    table.setItem(userow,const.WGE_WorkspaceCol,QtGui.QTableWidgetItem(workspaceName)) #Workspace Name 
    table.setItem(userow,const.WGE_LocationCol,QtGui.QTableWidgetItem(workspaceLocation)) #Workspace Location (path+file) 
    table.item(userow,const.WGE_LocationCol).setFont(QtGui.QFont('Courier',10))
    table.setItem(userow,const.WGE_DateCol,QtGui.QTableWidgetItem(ws_date)) 
    table.setItem(userow,const.WGE_SizeCol,QtGui.QTableWidgetItem(ws_size)) 
    table.setItem(userow,const.WGE_InMemCol,QtGui.QTableWidgetItem("No")) 
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