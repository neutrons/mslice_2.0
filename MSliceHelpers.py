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

























