################################################################################
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
################################################################################


def getLastAlgFromH5Workspace(H5Workspace,**kwargs):
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
    
###################################################################################
#
# getReducedAlgFromH5Workspace
#
###################################################################################

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


###################################################################################
#
# getReducedAlgFromWorkspace
#
###################################################################################


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
        xdimName=wsr.getXDimension().getName()
        ydimName=wsr.getYDimension().getName()    
        Ndims=2
        try:
            zdimName=wsr.getZDimension().getName()
            Ndims=3
            if vstat:
                print "Unknown case with 3 dimensions - probably a problem...but continuing on"
        except RuntimeError:
            #expect this case for powder 2D workspaces
            pass
    else:
        if vstat:
            print "getReduceAlgFromWorkspace: Workspace does not exist...returning"
        return ''

    if ((xdimName=='Energy transfer') & (ydimName=='')):
        #case where we have energy spectra (by pixel but not by any particular units
        AlgName='DgsReduction'
    elif ((xdimName=='Energy transfer') & (ydimName=='q')):
        #case where we have S(Q,w)
        AlgName='SofQ'
    else:
        #if here, we don't know the workspace type...
        AlgName=''

    #Now let's return the algorithm name we've extracted from the workspace
    return AlgName
    


















