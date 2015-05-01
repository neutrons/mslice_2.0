import sys,os
sys.path.append(os.environ['MANTIDPATH'])
from mantid.simpleapi import *

try:
    from PyQt4 import Qt, QtCore, QtGui
    from SliceViewer import *
    doSV=True
except:
    doSV=False

#Define file path and names
path='Z:/data/HYS/BarryWinn/'
file1='HYS_11356_msk_tube_spe.nxs'
file2='HYS_11357_msk_tube_spe.nxs'
file3='HYS_11358_msk_tube_spe.nxs'

#Define workspace names for input workspaces
ws1='HYS_11356_msk_tube_spe'
ws2='HYS_11357_msk_tube_spe'
ws3='HYS_11358_msk_tube_spe'

#Load workspaces
Load(path+file1,OutputWorkspace=ws1)
Load(path+file2,OutputWorkspace=ws2)
Load(path+file3,OutputWorkspace=ws3)

#Group workspaces
GrpWSName='GrpWS'
GroupWorkspaces([ws1,ws2,ws3],OutputWorkspace=GrpWSName)

#set Goniometer
motorName='S1'
Psi='7.5'
ax0='0,1,0,1'
ax1='0,1,0,1'
SetGoniometer(Workspace=GrpWSName,Axis0=motorName+','+ax0,Axis1=Psi+','+ax1) 

#Set UB Matrix
a=4.3
b=4.3
c=4.3
alpha=90
beta=90
gamma=90
u=[1,1,0]
v=[0,0,1]
SetUB(Workspace=GrpWSName,a=a,b=b,c=c,alpha=alpha,beta=beta,gamma=gamma,u=u,v=v)

#Convert workspaces to MD workspaces
GrpWSMDName='GrpWSMD'
Uproj=[1,1,0]
Vproj=[0,0,1]
Wproj=[-1,1,0]
#minn=[-6.5,-6.5,-6.5,-50]
#maxx=[6.5,6.5,6.5,22.5]
minn,maxx = ConvertToMDMinMaxGlobal(InputWorkspace=ws1,QDimensions='Q3D',dEAnalysisMode='Direct')
ConvertToMD(InputWorkspace=GrpWSName,OutputWorkspace=GrpWSMDName,QDimensions='Q3D',QConversionScales='HKL',MinValues=minn,MaxValues=maxx,Uproj=Uproj,Vproj=Vproj,Wproj=Wproj,PreprocDetectorsWS='')

#Merge MD workspaces into a single MD workspace
MrgWSName='MrgWS'
MergeMD(InputWorkspaces=GrpWSMDName,OutputWorkspace=MrgWSName)

#Bin MD workspace into a histogram workspace
AD0='[H,H,0],-6.49413,6.49413,260'
AD1='[0,0,L],-6.49413,6.49413,260'
AD2='[-H,H,0],-6.49413,6.49413,1'
AD3='DeltaE,-49.9957,22.4981,1'
HistoWSName='HistoWS'
BinMD(InputWorkspace=MrgWSName,AlignedDim0=AD0,AlignedDim1=AD1,AlignedDim2=AD2,AlignedDim3=AD3,OutputWorkspace=HistoWSName)

if doSV:
    #Envoke SliceViewer here
    app = QtGui.QApplication(sys.argv)
    sv = SliceViewer()
    label='MSlice SC Viewer'                
    sv.LoadData(HistoWSName,label)
    xydim=None
    slicepoint=None
    colormin=None
    colormax=None
    colorscalelog=False
    limits=None
    normalization=0
    sv.SetParams(xydim,slicepoint,colormin,colormax,colorscalelog,limits, normalization)
    sv.Show()
    exit_code=app.exec_()
    print "exit code: ",exit_code
    sys.exit(exit_code)