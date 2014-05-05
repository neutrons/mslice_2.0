from SliceViewer import *

if __name__=="__main__":
    
#    ws=Load(r'C:\Users\mid\Documents\Mantid\Powder\zrh_1000_sqw.nxs')
#    print "ws: ",ws
    app = QtGui.QApplication(sys.argv)
    sv = SliceViewer()
    LoadMD(filename=r'C:\Users\mid\Documents\Mantid\Powder\CalcProj\zrh_1000_PCalcProj.nxs',OutputWorkspace='ws')
    label='Python Only SliceViewer'
    sv.LoadData('ws',label)
    xydim=None
    slicepoint=None
    colormin=None
    colormax=None
    colorscalelog=False
    limits=None
    normalization=1
    sv.SetParams(xydim,slicepoint,colormin,colormax,colorscalelog,limits, normalization)
    sv.Show()

    sys.exit(app.exec_())