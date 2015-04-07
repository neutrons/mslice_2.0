
import sys,os
sys.path.append(os.environ['MANTIDPATH'])
from mantid.simpleapi import * 


def getMPLParms(self):
    print "Gothere2"
    ws_sel=str(self.ui.MPLcomboBoxActiveWorkspace.currentText())
    __ws=mtd.retrieve(ws_sel)	
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
        aligned=set1DBinVals(self,__ws)
        if aligned!=1:
            #case to exit out of plotting data
            dialog=QtGui.QMessageBox(self)
            dialog.setText("Problem: Unaligned data thus unable to determine plot units - Returning")
            dialog.exec_()
            return      
    
    
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