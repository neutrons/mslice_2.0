"""

#
# MSliceHelpers.py
#
# April 16, 2014 - original check-in
#
# This file is intended to contain various functions required by MSlice.pyw and
# WorkspaceComposerMain.py
#
#
################################################################################
#
# getLastAlgFromH5Workspace
#

"""
import sys, os
#handle potential deprecation warnings as psutil is in transition from
#version 1 to version 2
import warnings
warnings.filterwarnings('ignore',category=DeprecationWarning)
import psutil
#import Mantid computatinal modules
sys.path.append(os.environ['MANTIDPATH'])
from mantid.simpleapi import *
import config
from PyQt4 import Qt, QtCore, QtGui

def getLastAlgFromH5Workspace(H5Workspace,**kwargs):
    """
    #supported keywords:
    # verbose=True or verbose=False
    # workspace=<some integer>
    
    # This algorithm returns the last algorithm from the Mantid workspace -
    # Mantid Algorithms
    
    # This function requires that an HDF file for a Mantid workspace
    # be read in using the h5py module.  Once a similar method is discovered
    # for extracting the algorithm info from the workspace more directly, 
    # this routine can be retired.
    
    # It appears that there is a possiblity for a Mantid workspace file to 
    # contain more than one workspaces and this case is checked.  Howevever
    # up to this point only single workspace workspace files have been used.
    # Though this function does count the number of workspaces within the file
    # and can utilize user selected workspaces via the keyword usage. The default
    # is to use the first workspace.
    
    # There may be multipel algorithms within a workspace and this seems to be
    # typical.  The usual case is to use the algorithm for the last one.  Here 
    # the try - catch method is used to determine the number of MantidAlgorithms.
    
    # Not to confuse that there is an algorithm name listed within the data field
    # of the MantidAlgorithm_* path - these are two separate things.  
    # The algorithm name is that which this function extracts.  So summarizing, 
    # this function can handle multiple MantidAlgorithm_* paths, but is not 
    # setup to handle multiple Algorithm names within a single 
    # MantidAlgorithm_*.data field - currently only 1 Algorithm name is 
    # assumed within the MantidAlgorithm_* data field.
    """
    vstat=False
    wsNum=1 #set default workspace value
    for kw in kwargs.keys():
        if kw.upper() == 'VERBOSE':
            vstat=kwargs[kw]
            print "vstat: ",vstat
        if kw.upper() == 'WORKSPACE':
            wsNum=kwargs[kw]


    #first, let's determine the number of workspaces in the H5Workspace:
    #we can use a similar approach to determine the number of workspaces
    
    index = 1
    lastIndex=-1
    final_index = 500
    if vstat: print "*** final_index: ",final_index
    
    while True:
        if vstat: print "****************************************"
        if vstat: print "*** index: ",index
        try:
            workStr='/mantid_workspace_'+str(index)
            if vstat: print "workStr: ",workStr
            try:
                historyStr2=H5Workspace[workStr].id.valid
                if vstat: print "index: ",index
                index += 1
            except TypeError:
                print "Invalid Workspace Provided - Exiting"
                return ""
        except KeyError: 
            if vstat: print "KeyError"
            lastIndex=index - 1
            break
        except ValueError:
            #case where a workspace is not found - exit function
            return ""
        if index > final_index:
            break
                
    if vstat: print "index: ",index
    if vstat: 
        print "lastWSIndex: ",lastIndex
        if lastIndex > 1:
            print "More than one workspace found: ",lastIndex
    
    if vstat: print "*****************"
    
    if lastIndex < wsNum:
        if vstat: print "requested workspace does not exist, using workspace=1"
        wsNum=1  
        
    #We arrived at the file content by examining HDFView for a workspace file.  
    #Here we automated a way to determine the number of MantidAlgorithms
    
    #we will assume this basic structure: /mantid_workspace_*/process/MantidAlgorithm_*/data
    #We'll use a try catch system to determine the number of algorithms
    
    if vstat: print "*****************"
    
    index = 1 #workspace numbering starts at 1
    lastIndex=-1
    final_index = 500
    
    
    while True:
        if vstat: print "****************************************"
        if vstat: print "*** index: ",index
        try:
            workStr='/mantid_workspace_'+str(wsNum)+'/process/MantidAlgorithm_'+str(index)+'/data/'
            if vstat: print "workStr: ",workStr
            historyNpArray=H5Workspace[workStr].value
            if vstat: print "index: ",index
            index += 1
        except KeyError: 
            #case where no more algorithms found (expected to occur)
            if vstat: print "KeyError"
            lastIndex=index - 1
            break
        except ValueError:
            #case where a workspace is not found - exit function
            return ""
        if index > final_index:
            break
                
    if vstat: print "index: ",index
    if vstat: print "lastAlgIndex: ",lastIndex
    if vstat: print "*****************"
    
    historyStr = str(historyNpArray) #convert np.Array it to a string
    
    #now extract the algorithm from the last run algorithm - 
    #historyStr is comprised of a long string with this information
        
    historySplitList=historyStr.split("\\n")
    
    
    #but let's do it more robustly realizing that Algorithm may not be in postion [0]
    cntr=0
    for subStr in historySplitList:
        #check if subStr contains the Algorithm key
        if "Algorithm:" in subStr:
            cntr += 1
    if cntr > 1:
        if vstat: print "more than one algorithm discovered in the list...something needs to be checked..."
        
    index=cntr-1
    #for now, force index to be 1 as more will be have to learned how to decide which algorithm to use if more than one is present
    if index > 1:
        index=1
    if vstat: print "Algorithm key counter: ",cntr
    if vstat: print "Algorithm index values: ",index
    
    #now to extract just the algorithm used:
    # 1. take out possible extraneous characters
    # 2. take out extraneous quotes
    # 3. remove white spaces
    # 4. remove 'Algorithm: ' from the string by splitting the string into two list items
    # 5. split created two list items, just use the one with the result we want [1]

    Alg=historySplitList[index].replace('[',' ').replace("'"," ").strip().split('Algorithm: ')[1]
    AlgSplit=Alg.split() #splits the string into substrings so we can access the algorithm name apart from the version
    AlgName=AlgSplit[0].strip() #the name is in the first spot and trim any whitespace
    if vstat: print "Algorithm: ",AlgName
    
    #Now let's return the algorithm name we've extracted from the workspace
    return AlgName
"""
###################################################################################
#
# getReducedAlgFromH5Workspace
#
###################################################################################
"""

def getReduceAlgFromH5Workspace(H5Workspace,**kwargs):
    # Supported keywords:
    # verbose=True or verbose=False
    # workspace=<some integer>
    
    # This algorithm returns the last reduction algorithm from the 
    # Mantid workspace - Mantid Algorithms sequence.  For example, reduction
    # might be followed by a rebinning or transpose operation which would
    # mask the reduction algorithm used when just checking to use the last
    # algorithm
    
    # This function requires that an HDF file for a Mantid workspace
    # be read in using the h5py module.  Once a similar method is discovered
    # for extracting the algorithm info from the workspace more directly, 
    # this routine can be retired.
    
    vstat=False
    wsNum=1 #set default workspace value
    for kw in kwargs.keys():
        if kw.upper() == 'VERBOSE':
            vstat=kwargs[kw]
            print "vstat: ",vstat
        if kw.upper() == 'WORKSPACE':
            wsNum=kwargs[kw]


    #first, let's determine the number of workspaces in the H5Workspace:
    #we can use a similar approach to determine the number of workspaces
    
    index = 1
    lastIndex=-1
    final_index = 500
    if vstat: print "*** final_index: ",final_index
    
    while True:
        if vstat: print "****************************************"
        if vstat: print "*** index: ",index
        try:
            workStr='/mantid_workspace_'+str(index)
            if vstat: print "workStr: ",workStr
            try:
                historyStr2=H5Workspace[workStr].id.valid
                if vstat: print "index: ",index
                index += 1
            except TypeError:
                print "Invalid Workspace Provided - Exiting"
                return ""
        except KeyError: 
            if vstat: print "KeyError"
            lastIndex=index - 1
            break
        except ValueError:
            #case where a workspace is not found - exit function
            return ""
        if index > final_index:
            break
                
    if vstat: print "index: ",index
    if vstat: 
        print "lastWSIndex: ",lastIndex
        if lastIndex > 1:
            print "More than one workspace found: ",lastIndex
    
    if vstat: print "*****************"
    
    if lastIndex < wsNum:
        if vstat: print "requested workspace does not exist, using workspace=1"
        wsNum=1  
        
    #We arrived at the file content by examining HDFView for a workspace file.  
    #Here we automated a way to determine the number of MantidAlgorithms
    
    #we will assume this basic structure: /mantid_workspace_*/process/MantidAlgorithm_*/data
    #We'll use a try catch system to determine the number of algorithms
    
    if vstat: print "*****************"
    
    index = 1 #workspace numbering starts at 1
    lastIndex=-1
    final_index = 500
    
    AlgName=""
    ReduceAlgName=""
    
    while True:
        if vstat: print "****************************************"
        if vstat: print "*** index: ",index
        try:
            workStr='/mantid_workspace_'+str(wsNum)+'/process/MantidAlgorithm_'+str(index)+'/data/'
            if vstat: print "workStr: ",workStr
            historyNpArray=H5Workspace[workStr].value
            if vstat: print "index: ",index
            historyStr = str(historyNpArray) #convert np.Array it to a string
            
            #now extract the algorithm from the last run algorithm - 
            #historyStr is comprised of a long string with this information
                
            historySplitList=historyStr.split("\\n")            
            #now to extract just the algorithm used:
            # 1. take out possible extraneous characters
            # 2. take out extraneous quotes
            # 3. remove white spaces
            # 4. remove 'Algorithm: ' from the string by splitting the string into two list items
            # 5. split created two list items, just use the one with the result we want [1]
            Alg=historySplitList[0].replace('[',' ').replace("'"," ").strip().split('Algorithm: ')[1]
            AlgSplit=Alg.split() #splits the string into substrings so we can access the algorithm name apart from the version
            AlgName=AlgSplit[0].strip() #the name is in the first spot and trim any whitespace
            if vstat: print "Algorithm: ",AlgName
            
            if AlgName =="":
                #case where an algorithm name not found - no update
                pass
            elif AlgName == "Load":
                ReduceAlgName="Raw Data"
            elif AlgName == "DgsReduction":
                ReduceAlgName=AlgName
            elif AlgName == "SofQW3":
                ReduceAlgName=AlgName
            index += 1
        except KeyError: 
            #case where no more algorithms found (expected to occur)
            if vstat: print "KeyError"
            lastIndex=index - 1
            break
        except ValueError:
            #case where a workspace is not found - exit function
            return ""
        if index > final_index:
            break
                
    if vstat: print "index: ",index
    if vstat: print "lastAlgIndex: ",lastIndex
    if vstat: print "*****************"
    
        
    #Now let's return the reduction algorithm name we've extracted from the workspace
    return ReduceAlgName

"""
###################################################################################
#
# getReducedAlgFromWorkspace
#
###################################################################################
"""

def getReduceAlgFromWorkspace(Workspace,**kwargs):
    
    
    #supported keywords:
    # verbose=True or verbose=False
    # workspace=<some integer>
    
    import sys,os
    sys.path.append(os.environ['MANTIDPATH'])
    from mantid.simpleapi import *
    
    #This function requires a manted workspace from which plot units are extracted and the
    #reduction algorithm used is inferred.
        
    vstat=False
    wsNum=1 #set default workspace value
    for kw in kwargs.keys():
        if kw.upper() == 'VERBOSE':
            vstat=kwargs[kw]
            print "vstat: ",vstat
            
    vstat=True    #for debugging set vstat true
    
    if vstat:
        print "Workspace: ",Workspace
            
    #first let's check if the workspace exists
    Ndims=-1
    
    try:
        stat=mtd.doesExist(str(Workspace))
    except NameError:
        stat=False
        if vstat:
            print "Workspace is not defined"
    
    if vstat:
        print "stat: ",stat
        print mtd.doesExist(str(Workspace))
#        print mtd.doesExist(Workspace) #FIXME - need to use try catch if using Workspace this way...
    
    if stat:
        #case where it exists, now make sure that workspace is at python (rather than Mantid) layer
        wsr=mtd.retrieve(str(Workspace))  #retrieve seems to work OK if workspace is either at Mantid or already at the Python level
        print "type(wsr): ",type(wsr)
        
        #now check if the workspace is a group workspace or single workspace
        if 'Group' in str(type(wsr)):
            #case where the workspace is a group workspace
            cntr=0
            xdchk=''
            ydchk=''
            for ws in wsr:
                xdimName=ws.getXDimension().getName()
                ydimName=ws.getYDimension().getName() 
                if cntr ==0:
                    #case to set first occurance of dimensions
                    xdchk=xdimName
                    ydchk=ydimName
                else:
                    if (xdchk != xdimName) or (ydchk != ydimName):
                        #case where the workspaces do not have the same dimensionality
                        print "--------> Dimensionality mismatch!"
                        #deal with what to do here later...
                cntr +=1
                
            Ndims=2
        else:
            #case for a single workspace
            xdimName=wsr.getXDimension().getName()
            ydimName=wsr.getYDimension().getName()    
            Ndims=2
            pass
        
        
        """
        #leave this check for another time - will need to consider the case for group workspaces
        #may not need this check as the x and y dim check may be sufficient.
        try:
            zdimName=wsr.getZDimension().getName()
            Ndims=3
            if vstat:
                print "Unknown case with 3 dimensions - probably a problem...but continuing on"
        except RuntimeError:
            #expect this case for powder 2D workspaces
            pass
        """
    else:
        if vstat:
            print "getReduceAlgFromWorkspace: Workspace does not exist...returning"
        return ''
#FIXME - these dimension names should be brough out to config.py
    if ((xdimName=='Energy transfer') & (ydimName=='')):
        #case where we have energy spectra (by pixel but not by any particular units
        AlgName='DgsReduction'
    elif ((xdimName=='Energy transfer') & (ydimName=='q')):
        #case where we have S(Q,w)
        AlgName='SofQ'
    else:
        #if here, we don't know the workspace type...
        AlgName=''
        
        
    #Trying a different approach for now - just using the workspace ID instead
    #of trying to extract information so the following code will negate all 
    #of the prior code in this function...will eventually sort this out and decide
    #which code to keep
    
    ws=mtd.retrieve(Workspace)
    AlgName=ws.id()
    

    #Now let's return the algorithm name we've extracted from the workspace
    return AlgName
    
    
    
    
"""
###################################################################################
#
# getWorkspaceMemSize
#
###################################################################################
#
# Provide a Mantid workspace and this function will return it's memory footprint size
#
# workspaceName is a string variable with the name of the Mantid workspace
"""

def getWorkspaceMemSize(workspaceName):

    ws=mtd.retrieve(workspaceName)
    if 'Group' in str(type(ws)):
        #case where the workspace is a group workspace
        #iterate through the workspaces in the group to get the total size
        #of the group
        sz=0
        row=0
        for thisws in ws:
            sz += thisws.getMemorySize()       
            row +=1
    else:
        #case where it's an individual workspace - get it's size
        sz=ws.getMemorySize()
    SizeStr=str(float(int(float(sz)/float(1024*1024)*10))/10)+' MB' #use *10 then /10 to show down to .1 MB
    return SizeStr

"""
###################################################################################
#
# ListWorkspaces
#
###################################################################################
#
# Provide a Mantid workspace and this function will return the list of names
# within a group workspace or just return the single name if it's a single
# workspace
"""

def ListWorkspaces(workspace):
    
    ws=mtd.retrieve(workspaceName)
    wsList=[]
    if 'Group' in str(type(ws)):
        #case where the workspace is a group workspace
        #iterate through the workspaces to get the list of names

        for thisws in ws:
            wsList.append(thisws)
    else:
        wsList.append(workspace)
    return wsList


def constantUpdateActor(self):
    #const=constants()
    #mode to show status in percentage
    cpu_stats = psutil.cpu_times_percent(interval=0.1,percpu=False)
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
            home = os.path.expanduser("~")
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
    #const=constants()
    print "** In addmemWStoTable"
    print "table: ",table
    print "wsname: ",wsname
    print "wstype: ",wstype
    print "wssize: ",wssize
    print "wsindex: ",wsindex

    #Need to check if workspace already exists in table
    Nrows=table.rowCount()
    for row in range(Nrows):   
        try:
            wschk=str(table.item(row,config.WSM_WorkspaceCol).text())
            print "wschk: ",wschk
            print "wsname: ",wsname
            if wschk == wsname:
                print "Duplicate workspace name - not adding another entry and returning"
                dialog=QtGui.QMessageBox()
                dialog.setText("Duplicate filename - please correct and try again")
                dialog.exec_()  
                return
        except:
            #just skip this test with any empty rows that might be in the table
            pass

    #Overriding wstype and just using the workspace ID here
    ws=mtd.retrieve(wsname)
    wstype=ws.id()
    
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
    col=config.WSM_SelectCol
#        addComboboxToWSTCell(table,userow,col)
    addCheckboxToWSTCell(table,wsindex,col,True)
    
    #now add the row
    userow=wsindex		
    print "userow: ",userow
    table.setItem(userow,config.WSM_WorkspaceCol,QtGui.QTableWidgetItem(wsname)) #Workspace Name 
    table.setItem(userow,config.WSM_TypeCol,QtGui.QTableWidgetItem(wstype)) #Workspace Type
    table.setItem(userow,config.WSM_SavedCol,QtGui.QTableWidgetItem(saved)) #FIXXME Hard coded for now
    table.setItem(userow,config.WSM_SizeCol,QtGui.QTableWidgetItem(wssize)) #Size 
    addCheckboxToWSTCell(table,userow,config.WSM_SelectCol,True)
#    table.setItem(userow,config.WSM_SelectCol,QtGui.QTableWidgetItem('')) #select - will want to change this


def addWStoTable(table,workspaceName,workspaceLocation):
    #function to add a single workspace to the workspace manager table
	# workspaces may originate from create workspace or the list of files
    print "addWStoTable workspaceName: ",workspaceName
    print "workspaceLocation: ",workspaceLocation
    
        #Need to check if workspace already exists in table
    Nrows=table.rowCount()
    for row in range(Nrows):   
        wschk=str(table.item(row,config.WSM_WorkspaceCol).text())
        print "wschk: ",wschk
        print "workspaceName: ",workspaceName
        if wschk == workspaceName:
            print "Duplicate workspace name - not adding another entry and returning"
            return
    
    
    #get constants
    #const=constants()

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
    else:
        print "WSAlg: ",WSAlg
    

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
    table.setItem(userow,config.WSM_WorkspaceCol,QtGui.QTableWidgetItem(workspaceName)) #Workspace Name 
    table.setItem(userow,config.WSM_TypeCol,QtGui.QTableWidgetItem(WSAlg)) #Workspace Type
    table.setItem(userow,config.WSM_SavedCol,QtGui.QTableWidgetItem('yes')) #FIXXME Hard coded for now
    table.setItem(userow,config.WSM_SizeCol,QtGui.QTableWidgetItem(ws_size)) #Size 
    table.setItem(userow,config.WSM_SelectCol,QtGui.QTableWidgetItem('')) #select - will want to change this

"""
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

"""

def makeSCNames(self):

    """
    helper function to extract GUI info to build the name fields needed by MDNormDirectSC
    SC Viewing Axes define the variables to use
    Labels need to be integrated with a,b,c for each of u1,u2,and u3
    a,b,c can be floating point numbers
    name results are returned as a list of strings
    however -1H should be -H (drop the 1)
    """
    print "In makeSCNames"
    print "self: ",self
    print "type self.ui.lineEditSCVAu1a.text(): ",type(self.ui.lineEditSCVAu1a.text())
    print "self.ui.lineEditSCVAu1a.text(): ",self.ui.lineEditSCVAu1a.text()
    print "type str(self.ui.lineEditSCVAu1a.text()): ",type(str(self.ui.lineEditSCVAu1a.text()))
    print "str(self.ui.lineEditSCVAu1a.text()): ",str(self.ui.lineEditSCVAu1a.text())
    
    u1a=str(self.ui.lineEditSCVAu1a.text())
    u1b=str(self.ui.lineEditSCVAu1b.text())
    u1c=str(self.ui.lineEditSCVAu1c.text())
    u1Label=str(self.ui.lineEditSCVAu1Label.text())
    print "***** u1a: ",u1a,"  u1b: ",u1b,"  u1c: ",u1c,"  u1Label: ",u1Label
    
    if u1a == '1':
        lab1a=''
    elif u1a == '-1':
        lab1a='-'
    else:
        lab1a=u1a
    if u1a == '0':
        lab1a=str(lab1a)
    else:
        lab1a=str(lab1a)+str(u1Label)
    print "lab1a: ",lab1a,"  u1Label: ",u1Label
    print "lab1a: ",lab1a
    if u1b == '1':
        lab1b=''
    elif u1b == '-1':
        lab1b='-'
    else:
        lab1b=u1b
    if u1b == '0':
        lab1b=str(lab1b)
    else:
        lab1b=str(lab1b)+str(u1Label)
    print "lab1b: ",lab1b
    if u1c == '1':
        lab1c=''
    elif u1c == '-1':
        lab1c='-'
    else:
        lab1c=u1c
    if u1c == '0':
        lab1c=str(lab1c)
    else:
        lab1c=str(lab1c)+str(u1Label)
    print "lab1c: ",lab1c
    u1Name='['+lab1a+','+lab1b+','+lab1c+']'+ config.XYZUnits
    print "u1Name: ",u1Name

    u2a=str(self.ui.lineEditSCVAu2a.text())
    u2b=str(self.ui.lineEditSCVAu2b.text())
    u2c=str(self.ui.lineEditSCVAu2c.text())
    u2Label=str(self.ui.lineEditSCVAu2Label.text())
    if u2a == '1':
        lab2a=''
    elif u2a == '-1':
        lab2a='-'
    else:
        lab2a=u2a
    if u2a == '0':
        lab2a=str(lab2a)
    else:
        lab2a=str(lab2a)+str(u2Label)
    if u2b == '1':
        lab2b=''
    elif u2b == '-1':
        lab2b='-'
    else:
        lab2b=u2b
    if u2b == '0':
        lab2b=str(lab2b)
    else:
        lab2b=str(lab2b)+str(u2Label)
    if u2c == '1':
        lab2c=''
    elif u2c == '-1':
        lab2c='-'
    else:
        lab2c=u2c
    if u2c == '0':
        lab2c=str(lab2c)
    else:
        lab2c=str(lab2c)+str(u2Label)

    u2Name='['+lab2a+','+lab2b+','+lab2c+']'+config.XYZUnits
    print "u2Name: ",u2Name
            
    u3a=str(self.ui.lineEditSCVAu3a.text())
    u3b=str(self.ui.lineEditSCVAu3b.text())
    u3c=str(self.ui.lineEditSCVAu3c.text())
    u3Label=str(self.ui.lineEditSCVAu3Label.text())
    if u3a == '1':
        lab3a=''
    elif u3a == '-1':
        lab3a='-'
    else:
        lab3a=u3a
    if u3a == '0':
        lab3a=str(lab3a)
    else:
        lab3a=str(lab3a)+str(u3Label)
    if u3b == '1':
        lab3b=''
    elif u3b == '-1':
        lab3b='-'
    else:
        lab3b=u3b
    if u3b == '0':
        lab3b=str(lab3b)
    else:
        lab3b=str(lab3b)+str(u3Label)
    if u3c == '1':
        lab3c=''
    elif u3c == '-1':
        lab3c='-'
    else:
        lab3c=u3c
    if u3c == '0':
        lab3c=str(lab3c)
    else:
        lab3c=str(lab3c)+str(u3Label)
    u3Name='['+lab3a+','+lab3b+','+lab3c+']'+config.XYZUnits
    print "u3Name: ",u3Name
    
    print "***** u1Name: ",u1Name," u2Name: ",u2Name," u3Name: ",u3Name
    return [u1Name,u2Name,u3Name]

    
def swapSCViewParams(self,tab,CBIndx0,CBIndx1):

    """Utility function to swap the parameters for the single crystal view tabs
    self - main MSlice object
    tab - string indicating which tab ('Slice','Cut','Volume') - necessary as each tab has different widget names
    CBIndx0 - first combo box index to switch
    CBIndx1 - second combo box index to switch
    This utility simply swaps the contents of the GUI widgets
    """
    
    if CBIndx0 == CBIndx1:
        print "Cannot have CBIndx0 and CBIndx1 equal - returning"
        return
    #perform swap:
    #move contents of CBIndx0 to tmp
    #move contents of CBIndx1 to CBIndx0
    #move contents of tmp to CBIndx1
    
    
    if tab == 'Slice':
        print "** Slice Tab Selected"
        #move CBIndx0 values to tmp
        if CBIndx0 == 0:
            f0=self.ui.lineEditSCSliceXFrom.text()
            t0=self.ui.lineEditSCSliceXTo.text()
        elif CBIndx0 == 1:
            f0=self.ui.lineEditSCSliceYFrom.text()
            t0=self.ui.lineEditSCSliceYTo.text()            
        elif CBIndx0 == 2:
            f0=self.ui.lineEditSCSliceZFrom.text()
            t0=self.ui.lineEditSCSliceZTo.text()
        elif CBIndx0 == 3:
            f0=self.ui.lineEditSCSliceEFrom.text()
            t0=self.ui.lineEditSCSliceETo.text()
        else:
            print "Unable to identify CBIndx0 - returning"
            return
            
        print "f0: ",f0," t0: ",t0

        #then get CBIndx1 values
        if CBIndx1 == 0:
            f1=self.ui.lineEditSCSliceXFrom.text()
            t1=self.ui.lineEditSCSliceXTo.text()
        elif CBIndx1 == 1:
            f1=self.ui.lineEditSCSliceYFrom.text()
            t1=self.ui.lineEditSCSliceYTo.text()            
        elif CBIndx1 == 2:
            f1=self.ui.lineEditSCSliceZFrom.text()
            t1=self.ui.lineEditSCSliceZTo.text()
        elif CBIndx1 == 3:
            f1=self.ui.lineEditSCSliceEFrom.text()
            t1=self.ui.lineEditSCSliceETo.text()
        else:
            print "Unable to identify CBIndx0 - returning"
            return
            
        print "f1: ",f1," t1: ",t1
            
        #now place CBIndx1 values in CBIndx0
        if CBIndx0 == 0:
            self.ui.lineEditSCSliceXFrom.setText(f1)
            self.ui.lineEditSCSliceXTo.setText(t1)
        elif CBIndx0 == 1:
            self.ui.lineEditSCSliceYFrom.setText(f1)
            self.ui.lineEditSCSliceYTo.setText(t1)            
        elif CBIndx0 == 2:
            self.ui.lineEditSCSliceZFrom.setText(f1)
            self.ui.lineEditSCSliceZTo.setText(t1)
        elif CBIndx0 == 3:
            self.ui.lineEditSCSliceEFrom.setText(f1)
            self.ui.lineEditSCSliceETo.setText(t1)
        else:
            print "Unable to identify CBIndx0 - returning"
            return

        #finally place CBIndx0 values into CBIndx1
        if CBIndx1 == 0:
            self.ui.lineEditSCSliceXFrom.setText(f0)
            self.ui.lineEditSCSliceXTo.setText(t0)
        elif CBIndx1 == 1:
            self.ui.lineEditSCSliceYFrom.setText(f0)
            self.ui.lineEditSCSliceYTo.setText(t0)            
        elif CBIndx1 == 2:
            self.ui.lineEditSCSliceZFrom.setText(f0)
            self.ui.lineEditSCSliceZTo.setText(t0)
        elif CBIndx1 == 3:
            self.ui.lineEditSCSliceEFrom.setText(f0)
            self.ui.lineEditSCSliceETo.setText(t0)
        else:
            print "Unable to identify CBIndx0 - returning"
            return


    elif tab == 'Cut':
        pass #stub for Cut tab
        #move CBIndx0 values to tmp
        if CBIndx0 == 0:
            f0=self.ui.lineEditSCCutXFrom.text()
            t0=self.ui.lineEditSCCutXTo.text()
        elif CBIndx0 == 1:
            f0=self.ui.lineEditSCCutYFrom.text()
            t0=self.ui.lineEditSCCutYTo.text()            
        elif CBIndx0 == 2:
            f0=self.ui.lineEditSCCutZFrom.text()
            t0=self.ui.lineEditSCCutZTo.text()
        elif CBIndx0 == 3:
            f0=self.ui.lineEditSCCutEFrom.text()
            t0=self.ui.lineEditSCCutETo.text()
        else:
            print "Unable to identify CBIndx0 - returning"
            return
            
        print "f0: ",f0," t0: ",t0

        #then get CBIndx1 values
        if CBIndx1 == 0:
            f1=self.ui.lineEditSCCutXFrom.text()
            t1=self.ui.lineEditSCCutXTo.text()
        elif CBIndx1 == 1:
            f1=self.ui.lineEditSCCutYFrom.text()
            t1=self.ui.lineEditSCCutYTo.text()            
        elif CBIndx1 == 2:
            f1=self.ui.lineEditSCCutZFrom.text()
            t1=self.ui.lineEditSCCutZTo.text()
        elif CBIndx1 == 3:
            f1=self.ui.lineEditSCCutEFrom.text()
            t1=self.ui.lineEditSCCutETo.text()
        else:
            print "Unable to identify CBIndx0 - returning"
            return
            
        print "f1: ",f1," t1: ",t1
            
        #now place CBIndx1 values in CBIndx0
        if CBIndx0 == 0:
            self.ui.lineEditSCCutXFrom.setText(f1)
            self.ui.lineEditSCCutXTo.setText(t1)
        elif CBIndx0 == 1:
            self.ui.lineEditSCCutYFrom.setText(f1)
            self.ui.lineEditSCCutYTo.setText(t1)            
        elif CBIndx0 == 2:
            self.ui.lineEditSCCutZFrom.setText(f1)
            self.ui.lineEditSCCutZTo.setText(t1)
        elif CBIndx0 == 3:
            self.ui.lineEditSCCutEFrom.setText(f1)
            self.ui.lineEditSCCutETo.setText(t1)
        else:
            print "Unable to identify CBIndx0 - returning"
            return

        #finally place CBIndx0 values into CBIndx1
        if CBIndx1 == 0:
            self.ui.lineEditSCCutXFrom.setText(f0)
            self.ui.lineEditSCCutXTo.setText(t0)
        elif CBIndx1 == 1:
            self.ui.lineEditSCCutYFrom.setText(f0)
            self.ui.lineEditSCCutYTo.setText(t0)            
        elif CBIndx1 == 2:
            self.ui.lineEditSCCutZFrom.setText(f0)
            self.ui.lineEditSCCutZTo.setText(t0)
        elif CBIndx1 == 3:
            self.ui.lineEditSCCutEFrom.setText(f0)
            self.ui.lineEditSCCutETo.setText(t0)
        else:
            print "Unable to identify CBIndx0 - returning"
            return        
        
        
        
        
    elif tab == 'Volume':
        print "** Volume Tab Selected"
        #move CBIndx0 values to tmp
        if CBIndx0 == 0:
            f0=self.ui.lineEditSCVolXFrom.text()
            t0=self.ui.lineEditSCVolXTo.text()
        elif CBIndx0 == 1:
            f0=self.ui.lineEditSCVolYFrom.text()
            t0=self.ui.lineEditSCVolYTo.text()            
        elif CBIndx0 == 2:
            f0=self.ui.lineEditSCVolZFrom.text()
            t0=self.ui.lineEditSCVolZTo.text()
        elif CBIndx0 == 3:
            f0=self.ui.lineEditSCVolEFrom.text()
            t0=self.ui.lineEditSCVolETo.text()
        else:
            print "Unable to identify CBIndx0 - returning"
            return
            
        print "f0: ",f0," t0: ",t0

        #then get CBIndx1 values
        if CBIndx1 == 0:
            f1=self.ui.lineEditSCVolXFrom.text()
            t1=self.ui.lineEditSCVolXTo.text()
        elif CBIndx1 == 1:
            f1=self.ui.lineEditSCVolYFrom.text()
            t1=self.ui.lineEditSCVolYTo.text()            
        elif CBIndx1 == 2:
            f1=self.ui.lineEditSCVolZFrom.text()
            t1=self.ui.lineEditSCVolZTo.text()
        elif CBIndx1 == 3:
            f1=self.ui.lineEditSCVolEFrom.text()
            t1=self.ui.lineEditSCVolETo.text()
        else:
            print "Unable to identify CBIndx0 - returning"
            return
            
        print "f1: ",f1," t1: ",t1
            
        #now place CBIndx1 values in CBIndx0
        if CBIndx0 == 0:
            self.ui.lineEditSCVolXFrom.setText(f1)
            self.ui.lineEditSCVolXTo.setText(t1)
        elif CBIndx0 == 1:
            self.ui.lineEditSCVolYFrom.setText(f1)
            self.ui.lineEditSCVolYTo.setText(t1)            
        elif CBIndx0 == 2:
            self.ui.lineEditSCVolZFrom.setText(f1)
            self.ui.lineEditSCVolZTo.setText(t1)
        elif CBIndx0 == 3:
            self.ui.lineEditSCVolEFrom.setText(f1)
            self.ui.lineEditSCVolETo.setText(t1)
        else:
            print "Unable to identify CBIndx0 - returning"
            return

        #finally place CBIndx0 values into CBIndx1
        if CBIndx1 == 0:
            self.ui.lineEditSCVolXFrom.setText(f0)
            self.ui.lineEditSCVolXTo.setText(t0)
        elif CBIndx1 == 1:
            self.ui.lineEditSCVolYFrom.setText(f0)
            self.ui.lineEditSCVolYTo.setText(t0)            
        elif CBIndx1 == 2:
            self.ui.lineEditSCVolZFrom.setText(f0)
            self.ui.lineEditSCVolZTo.setText(t0)
        elif CBIndx1 == 3:
            self.ui.lineEditSCVolEFrom.setText(f0)
            self.ui.lineEditSCVolETo.setText(t0)
        else:
            print "Unable to identify CBIndx0 - returning"
            return        
        
        pass #stub for Volume tab
    else:
        print "Incorrect tab identifier specified - bug in code - returning"
        return
        
        

def convertIndexToLabel(self,comboBox,mode):
    """
    self is MSlice main object
    comboBox is a text string indicating which of X,Y,Z,E combo boxes are being examined
    
    The currentIndex() for the selected comboBox is identified and returned 
    
    """
    
    if mode == 'Cut':
        #not implemented yet
        ViewSCDict=self.ui.ViewSCCDict
    elif mode == 'Slice':
        ViewSCDict=self.ui.ViewSCSDict
    elif mode == 'Volume':
        ViewSCDict=self.ui.ViewSCVDict
    else:
        print "Unknown mode"
    
    if comboBox == 'X':
        if mode == 'Cut':
            labelCB=str(self.ui.comboBoxSCCutX.currentText())
        elif mode == 'Slice':
            labelCB=str(self.ui.comboBoxSCSliceX.currentText())
        elif mode == 'Volume':
            labelCB=str(self.ui.comboBoxSCVolX.currentText())
        else:
            #case should not occur
            pass
        if labelCB == ViewSCDict['u1']['label']:
            labelDict='u1'
        elif labelCB == ViewSCDict['u2']['label']:
            labelDict='u2'
        elif labelCB == ViewSCDict['u3']['label']:
            labelDict='u3'
        elif labelCB == ViewSCDict['E']['label']:
            labelDict='E'
        else:
            print "Label match not found - returning"
            return
        
    elif comboBox == 'Y':
        if mode == 'Cut':
            labelCB=str(self.ui.comboBoxSCCutY.currentText())
        elif mode == 'Slice':
            labelCB=str(self.ui.comboBoxSCSliceY.currentText())
        elif mode == 'Volume':
            labelCB=str(self.ui.comboBoxSCVolY.currentText())
        else:
            #case should not occur
            pass
        if labelCB == ViewSCDict['u1']['label']:
            labelDict='u1'
        elif labelCB == ViewSCDict['u2']['label']:
            labelDict='u2'
        elif labelCB == ViewSCDict['u3']['label']:
            labelDict='u3'
        elif labelCB == ViewSCDict['E']['label']:
            labelDict='E'    
        else:
            print "Label match not found - returning"
            return
                            
    elif comboBox == 'Z':
        if mode == 'Cut':
            labelCB=str(self.ui.comboBoxSCCutZ.currentText())
        elif mode == 'Slice':
            labelCB=str(self.ui.comboBoxSCSliceZ.currentText())
        elif mode == 'Volume':
            labelCB=str(self.ui.comboBoxSCVolZ.currentText())
        else:
            #case should not occur
            pass
        if labelCB == ViewSCDict['u1']['label']:
            labelDict='u1'
        elif labelCB == ViewSCDict['u2']['label']:
            labelDict='u2'
        elif labelCB == ViewSCDict['u3']['label']:
            labelDict='u3'
        elif labelCB == ViewSCDict['E']['label']:
            labelDict='E'
        else:
            print "Label match not found - returning"
            return            
        
    elif comboBox == 'E':
        if mode == 'Cut':
            labelCB=str(self.ui.comboBoxSCCutE.currentText())
        elif mode == 'Slice':
            labelCB=str(self.ui.comboBoxSCSliceE.currentText())
        elif mode == 'Volume':
            labelCB=str(self.ui.comboBoxSCVolE.currentText())
        else:
            #case should not occur
            pass
        if labelCB == ViewSCDict['u1']['label']:
            labelDict='u1'
        elif labelCB == ViewSCDict['u2']['label']:
            labelDict='u2'
        elif labelCB == ViewSCDict['u3']['label']:
            labelDict='u3'
        elif labelCB == ViewSCDict['E']['label']:
            labelDict='E'
        else:
            print "Label match not found - returning"
            return
        
    else:
        print "Unknown combo box - returning"
        return
    
    
    return labelDict
        

def histToDict(ws):
    """ 
    Utility to extract the history from a workspace and place it within a
    dictionary.  The resulting dictionary is returned to the calling program
    """
    
    histDict={}
    #NEntries=len(ws.getHistory().getAlgorithmHistories())
    NEntries=ws.getHistory().size()
    subDicts=[] #list of dictionary names within the main dictionary
    cntr=0
    for i in range(NEntries):
                NTags=len(ws.getHistory().getAlgorithmHistories()[i].getProperties())
                print ws.getHistory().getAlgorithmHistories()[i].name()
                entry=ws.getHistory().getAlgorithmHistories()[i].name()
                #histories can contain multiple entries with duplicate names.  
                #However the latest duplicate name will be the one that survies
                #placement into the dictionary.  To avoid this issue, check each
                #dictionary label to see if it has been used before and if so,
                #add an index counter value to the name to keep it unique.
                #Not doing this will append all of the key/value pairs into the
                #original dictionary declaration.
                if entry in subDicts:
                    entry=entry+str(cntr) #append a unique identifier to this subDict
                    cntr+=1 #increment counter
                subDicts.append(entry) #put new subDict in list
                #place each key/value pair into the corresponding subDict
                for j in range(NTags):
                    name=ws.getHistory().getAlgorithmHistories()[i].getProperties()[j].name()
                    value=ws.getHistory().getAlgorithmHistories()[i].getProperties()[j].value()
                    histDict.setdefault(entry,{})[name]=value

    #Get combo box labels - also add them to histDict
    XName=ws.getXDimension().getName()
    if XName == 'DeltaE':
        XName = 'E (meV)'
    else:
        XName=XName+config.XYZUnits
    histDict.setdefault('Names',{})['XName']=XName
    YName=ws.getYDimension().getName()
    if YName == 'DeltaE':
        YName = 'E (meV)'
    else:
        YName=YName+config.XYZUnits
    histDict.setdefault('Names',{})['YName']=YName
    ZName=ws.getZDimension().getName()
    if ZName == 'DeltaE':
        ZName = 'E (meV)'
    else:
        ZName=ZName+config.XYZUnits
    histDict.setdefault('Names',{})['ZName']=ZName
    TName=ws.getTDimension().getName()
    if TName == 'DeltaE':
        TName = 'E (meV)'
    else:
        TName=TName+config.XYZUnits
    histDict.setdefault('Names',{})['TName']=TName

    return histDict

def updateSCParms(self,histDict,modes):
    #case to update the Single Crystal Slice tab parameters
    #values to use are in histDict
    #expecting mode values of:
    # - 'Cut'
    # - 'Slice'
    # - 'Volume'
    #modes is expecited to be a list of strings (may just be one string)
    #this enables all three tabs to be updated from this one call.
    #Example: modes=['Slice']
    
    #FIXME - note that it is possible that there could be multiple entries
    #for SetUB, SetGoniometer, and ConvertToMD, however these cases are not
    #currently being checked and handled - will address this if it becomes an
    #issue.
    
    #Update Unit Cell Lattice Parameters
    a = '%.2f' % float(histDict['SetUB']['a'])
    b = '%.2f' % float(histDict['SetUB']['b'])
    c = '%.2f' % float(histDict['SetUB']['c'])
    alpha = '%.2f' % float(histDict['SetUB']['alpha'])
    beta = '%.2f' % float(histDict['SetUB']['beta'])
    gamma ='%.2f' % float(histDict['SetUB']['gamma'])
    uvec = histDict['SetUB']['u'].split(',')
    vvec = histDict['SetUB']['v'].split(',')

    #Get Goniometer settings
    Axis0=histDict['SetGoniometer']['Axis0'].split(',')
    Axis1=histDict['SetGoniometer']['Axis1'].split(',')

    #Get Viewing axes info
    Uproj=histDict['ConvertToMD']['Uproj'].split(',')
    Vproj=histDict['ConvertToMD']['Vproj'].split(',')
    Wproj=histDict['ConvertToMD']['Wproj'].split(',')

    #Get min/max values
    MinVals=histDict['ConvertToMD']['MinValues'].split(',')
    MaxVals=histDict['ConvertToMD']['MaxValues'].split(',')    


        
    #set Unit Cell, Crystal Orientation, Goniometer, and Viewing Axes fields
    self.ui.lineEditUCa.setText(a)
    self.ui.lineEditUCb.setText(b)
    self.ui.lineEditUCc.setText(c)
    self.ui.lineEditUCalpha.setText(alpha)
    self.ui.lineEditUCbeta.setText(beta)
    self.ui.lineEditUCgamma.setText(gamma)
    self.ui.lineEditSCCOux.setText(uvec[0])
    self.ui.lineEditSCCOuy.setText(uvec[1])
    self.ui.lineEditSCCOuz.setText(uvec[2])
    self.ui.lineEditSCCOvx.setText(vvec[0])
    self.ui.lineEditSCCOvy.setText(vvec[1])
    self.ui.lineEditSCCOvz.setText(vvec[2])
    self.ui.lineEditSCCOPsi.setText(Axis1[0])
    self.ui.lineEditSCCOName.setText(Axis0[0])
    self.ui.lineEditSCVAu1a.setText(Uproj[0])
    self.ui.lineEditSCVAu1b.setText(Uproj[1])
    self.ui.lineEditSCVAu1c.setText(Uproj[2])
    self.ui.lineEditSCVAu2a.setText(Vproj[0])
    self.ui.lineEditSCVAu2b.setText(Vproj[1])
    self.ui.lineEditSCVAu2c.setText(Vproj[2])
    self.ui.lineEditSCVAu3a.setText(Wproj[0])
    self.ui.lineEditSCVAu3b.setText(Wproj[1])
    self.ui.lineEditSCVAu3c.setText(Wproj[2])
    
    self.ui.lineEditSCWorkspaceSuffix.setText('_SCProj')
    
    #set Viewing Axes Labels
    #need to extract each label from its corresponding dimensional name
    self.ui.lineEditSCVAu1Label.setText(getLabelChar(histDict,'XName'))
    self.ui.lineEditSCVAu2Label.setText(getLabelChar(histDict,'YName'))
    self.ui.lineEditSCVAu3Label.setText(getLabelChar(histDict,'ZName'))
    
    #can now call methods for updating ViewSCSDict and for populating the 
    #view tabs as if the 'Calculate Projections' button was pressed
    
    #update ViewSCCDict with minn and maxx values calculated above

    self.ui.ViewSCCDict['u1']['from']=float(MinVals[0])
    self.ui.ViewSCCDict['u1']['to']=float(MaxVals[0])      
    self.ui.ViewSCCDict['u2']['from']=float(MinVals[1])
    self.ui.ViewSCCDict['u2']['to']=float(MaxVals[1])
    self.ui.ViewSCCDict['u3']['from']=float(MinVals[2])
    self.ui.ViewSCCDict['u3']['to']=float(MaxVals[2])
    self.ui.ViewSCCDict['E']['from']=float(MinVals[3])
    self.ui.ViewSCCDict['E']['to']=float(MaxVals[3])
    
    #update ViewSCSDict with minn and maxx values calculated above

    self.ui.ViewSCSDict['u1']['from']=float(MinVals[0])
    self.ui.ViewSCSDict['u1']['to']=float(MaxVals[0])      
    self.ui.ViewSCSDict['u2']['from']=float(MinVals[1])
    self.ui.ViewSCSDict['u2']['to']=float(MaxVals[1])
    self.ui.ViewSCSDict['u3']['from']=float(MinVals[2])
    self.ui.ViewSCSDict['u3']['to']=float(MaxVals[2])
    self.ui.ViewSCSDict['E']['from']=float(MinVals[3])
    self.ui.ViewSCSDict['E']['to']=float(MaxVals[3])
    
    #update ViewSCVDict with minn and maxx values calculated above

    self.ui.ViewSCVDict['u1']['from']=float(MinVals[0])
    self.ui.ViewSCVDict['u1']['to']=float(MaxVals[0])      
    self.ui.ViewSCVDict['u2']['from']=float(MinVals[1])
    self.ui.ViewSCVDict['u2']['to']=float(MaxVals[1])
    self.ui.ViewSCVDict['u3']['from']=float(MinVals[2])
    self.ui.ViewSCVDict['u3']['to']=float(MaxVals[2])
    self.ui.ViewSCVDict['E']['from']=float(MinVals[3])
    self.ui.ViewSCVDict['E']['to']=float(MaxVals[3])
    
    #Now update ViewSCSDict() and ViewSCVDict() with changes from the GUI
    self.UpdateViewSCCDict()
    self.UpdateViewSCSDict()
    self.UpdateViewSCVDict()

        

def getLabelChar(histDict,dimName):
    """
    Function to extract the label character from the dimensional name
    Example: dimensional name may be [-H,H,0] --> H
    Function expects dimName(s) to be one of:
    XName
    YName
    ZName
    TName
    """
    
    #extract label from histDict dictionary
    label=histDict['Names'][dimName]
    
    #realize that label may have '(RLU)' appended - don't want this part in label
    label.replace('RLU','')
    
    #now search for H, K, or L in label
    #Important assumption here: assumed that each label will only contain ONE
    #of H, K, or L 
    
    if 'H' in label:
        return 'H'
        
    elif 'K' in label:
        return 'K'
        
    elif 'L' in label:
        return 'L'
    else:
        return ''
        
    


