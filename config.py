#config.py - used to store global constants for MSlice

#int values for mySignal(int)
mySigNorm=10         #normal return value for mySignal
mySigOverwrite=11    #case to overwrite the workspace listed in the Workspace Manager

#Workspace Manager column definitions
WSM_WorkspaceCol=0
WSM_TypeCol=1
WSM_SavedCol=2
WSM_SizeCol=3
WSM_SelectCol=4

#
CWS_FilenameCol=0
CWS_DateCol=1
CWS_TypeCol=2
CWS_SizeCol=3
CWS_ScaleFactorCol=4
CWS_StatusCol=5

#MSlice Single Crystal Number of points "too large" thresholds
SCXNpts=10000
SCYNpts=10000

#Units for HKL combo box labels
XYZUnits=' (RLU)'
SCSStep = 0.035
SCVStep = 0.050