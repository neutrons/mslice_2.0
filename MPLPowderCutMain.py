import sys, os

from MPLPowderCut import *
from PyQt4 import Qt, QtCore, QtGui
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

import matplotlib
if matplotlib.get_backend() != 'QT4Agg':
    matplotlib.use('QT4Agg')
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt

import numpy as np

from datetime import datetime


#import Mantid computatinal modules
sys.path.append(os.environ['MANTIDPATH'])
from mantid.simpleapi import *

class MPLPowderCut(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MPLPowderCutMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Powder Cut")
        self.parent=parent 
        
        #establish signals and slots
        QtCore.QObject.connect(self.ui.MPLpushButtonPlot, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.DoPlot)
        QtCore.QObject.connect(self.ui.MPLpushButtonOPlot, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.DoOPlot)
        QtCore.QObject.connect(self.ui.MPLpushButtonPlaceText, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.DoAnnotate)
        QtCore.QObject.connect(self.ui.MPLpushButtonRemoveText, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.RemText)
        QtCore.QObject.connect(self.ui.MPLpushButtonPlaceArrow, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.DoArrow)
        QtCore.QObject.connect(self.ui.MPLpushButtonRemoveArrow, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.RemArrow)
        QtCore.QObject.connect(self.ui.MPLpushButtonSavePlot, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.SavePlot)
        QtCore.QObject.connect(self.ui.MPLpushButtonSaveData, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.SaveData)
        QtCore.QObject.connect(self.ui.MPLpushButtonDone, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.Done)
        
        
        QtCore.QObject.connect(self.ui.MPLcomboBoxActiveWorkspace, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.SelectWorkspace)
        
        #now that the widget has been established, copy over values from MSlice
        #Workspace List and insert them into the MPLcomboBoxActiveWorkspace combo box
        
        #get the list of workspaces
        wslist=self.parent.ui.wslist
        print "wslist: ",wslist
        
        #now need to parse workspaces to determine which are grouped workspaces to list each workspace separately in the plot GUI
        Nws=len(wslist)
        wstotlist=[]
        for n in range(Nws):
            tmpws=mtd.retrieve(wslist[n])
            if 'Group' in str(type(tmpws)):
            #case to get all workspace names from the group
                for ws in tmpws:
                    wstotlist.append(ws)
            else:
                #case we just have a single workspace
                wstotlist.append(wslist[n])
        
        print "Total number of workspaces passed to Powder Cut: ",wstotlist
        #now put workspaces into workspace combo box
        Nws=len(wstotlist)
        for n in range(Nws):
            if n == 0:
                #case to use the existing row in the combo box
                self.ui.MPLcomboBoxActiveWorkspace.setItemText(n,str(wstotlist[n]))
            else:
                #case to add rows to insert workspace names
                self.ui.MPLcomboBoxActiveWorkspace.insertItem(n,wstotlist[n])
            
        #Data Formatting
        self.ui.MPLlineEditPowderCutAlongFrom.setText(self.parent.ui.lineEditPowderCutAlongFrom.text())
        self.ui.MPLlineEditPowderCutAlongTo.setText(self.parent.ui.lineEditPowderCutAlongTo.text())
        self.ui.MPLlineEditPowderCutAlongStep.setText(self.parent.ui.lineEditPowderCutAlongStep.text())
        
        self.ui.MPLlineEditPowderCutThickFrom.setText(self.parent.ui.lineEditPowderCutThickFrom.text())
        self.ui.MPLlineEditPowderCutThickTo.setText(self.parent.ui.lineEditPowderCutThickTo.text())
        
        self.ui.MPLlineEditPowderCutYFrom.setText(self.parent.ui.lineEditPowderCutYFrom.text())
        self.ui.MPLlineEditPowderCutYTo.setText(self.parent.ui.lineEditPowderCutYTo.text())
        
        indx_Along=self.parent.ui.comboBoxPowderCutAlong.currentIndex()
        indx_Thick=self.parent.ui.comboBoxPowderCutThick.currentIndex()
        indx_Y=self.parent.ui.comboBoxPowderCutY.currentIndex()
        self.ui.MPLcomboBoxPowderCutAlong.setCurrentIndex(indx_Along)
        self.ui.MPLcomboBoxPowderCutThick.setCurrentIndex(indx_Thick)
        self.ui.MPLcomboBoxPowderCutY.setCurrentIndex(indx_Y)
               
        #Plot Configuration
        self.ui.MPLlineEditLabelsIntensity.setText(self.parent.ui.lineEditLabelsIntensity.text())
        self.ui.MPLlineEditLabelsTitle.setText(self.parent.ui.lineEditLabelsTitle.text())
        self.ui.MPLlineEditLabelsLegend.setText(self.parent.ui.lineEditLabelsLegend.text())
        
        #Place Matplotlib figure within the GUI frame
        #create drawing canvas
        # a figure instance to plot on
        
        matplotlib.rc_context({'toolbar':True})
        self.shadowFigure = plt.figure()
        plt.figure(self.shadowFigure.number)
        self.figure = plt.figure()

        
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.shadowCanvas=FigureCanvas(self.shadowFigure)
        self.shadowCanvas.set_window_title('Popout Figure')
        self.canvas = FigureCanvas(self.figure)
        
        #add Navigation Toolbar
        self.navigation_toolbar = NavigationToolbar(self.canvas, self)
        self.shadow_navigation_toolbar = NavigationToolbar(self.shadowCanvas, self.shadowCanvas)
        
        layout=QtGui.QVBoxLayout(self.ui.MPLframe)
        layout.addWidget(self.canvas)
        layout.addWidget(self.navigation_toolbar, 0)
        self.layout=layout

        self.doOPlot=False  #initialize to do plot (rather than oplot)
        
        self.doAnnotate=False #flag used to annotate text on plots
        self.doArrow=False #flag used to place arrows on plots
        
        #Launch plot in bringing up the application
        self.DoPlot()
    
    def SelectWorkspace(self):
        #get selected workspace
        wsindx=self.ui.MPLcomboBoxActiveWorkspace.currentIndex()
        if wsindx==0:
            #case where we have selected the descriptive text - no workspace selected
            self.ws=''  #clear out the workspace in this case
        else:
            self.ws=str(self.ui.MPLcomboBoxActiveWorkspace.currentText())
            
        print "Selected Workspace: ",self.ws

    def DoOPlot(self):
        self.doOPlot=True
        self.DoPlot()
        
        
    def DoPlot(self):
        print "*************** Do Plot *********************"
        
        if not(self.doOPlot):self.ui.MPLpushButtonSavePlot.setEnabled(True)
        
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
        
        #query GUI for X and Y axes
        #X axis from "along" combo box
        xindx=self.ui.MPLcomboBoxPowderCutAlong.currentIndex()
        print "xindx: ",xindx
        if xindx==0:
            #Energy
            XAxisStr="E (meV)"
        elif xindx==1:
            #|Q|
            XAxisStr='|Q| ($\AA^{-1}$)'
        elif xindx==2:
            #2Theta
            XAxisStr=r'2theta ($^o$)'
        elif xindx==3:
            #Det Pixels
            XAxisStr="Detector Pixel"
        else:
            #undefined case...
            pass
            
        
        #Y axis from "y" combo box MPLcomboBoxPowderCutY
        yindx=self.ui.MPLcomboBoxPowderCutY.currentIndex()
        print "yindx: ",yindx
        if yindx==0:
            #Intensity - get label from GUI MPLlineEditLabelsIntensity
            YAxisStr=str(self.ui.MPLlineEditLabelsIntensity.text())
            if YAxisStr == '':
                #use a default Y axis string if the GUI does not have a value
                YAxisStr="Intensity (arb. units)"
        elif yindx==1:
            #Energy
            YAxisStr="E (meV)"
        elif yindx==2:
            #|Q|
            YAxisStr=r'|Q| ($\AA^{-1}$)'
        elif yindx==3:
            #2Theta
            YAxisStr=r'2theta ($^o$)'
        elif yindx==4:
            #Det Pixels
            YAxisStr="Detector Pixel"
        else:
            #undefined case...
            pass        
        
        #get selected workspace from combo box
        ws_sel=str(self.ui.MPLcomboBoxActiveWorkspace.currentText())
        
        #now extract data from workspace
        ws=mtd.retrieve(ws_sel)

        wsX=ws.getXDimension()
        wsY=ws.getYDimension()
        
        xmin=wsX.getMinimum()
        xmax=wsX.getMaximum()
        
        ymin=wsY.getMinimum()
        ymax=wsY.getMaximum()
        
        xname= wsX.getName()
        yname= wsY.getName()
        
        delx=xmax-xmin
        dely=ymax-ymin
        
        #verify that data are ordered as expected
        if ((xname != '|Q|') or (yname != 'E')):
            print "---> Data order mismatch...data order verification needed"
            #FIXME eventually should not just check, but correct this condition
        
        #for now, just figure out if Q or E is along the x axis...
        indx=self.ui.MPLcomboBoxPowderCutAlong.currentIndex()
        print "indx: ",indx
        if indx==0:
            #case for Energy along x axis
            minv=ymin
            maxv=ymax
            
            #determine the ranges of data to work with
            #from:to
            if str(self.ui.MPLlineEditPowderCutAlongFrom.text()) != '':
                Afrom=float(str(self.ui.MPLlineEditPowderCutAlongFrom.text()))
            else:
                Afrom=minv
            print "trash: ",str(self.ui.MPLlineEditPowderCutAlongTo.text()) == ''
            print "trash type: ",type(self.ui.MPLlineEditPowderCutAlongTo.text())
            print 
            if str(self.ui.MPLlineEditPowderCutAlongTo.text()) != '':
                Ato=float(str(self.ui.MPLlineEditPowderCutAlongTo.text()))
            else:
                Ato=maxv
            if str(self.ui.MPLlineEditPowderCutAlongStep.text()) != '':
                Astep=float(str(self.ui.MPLlineEditPowderCutAlongStep.text()))
            else:
                Astep=0.035  #FIXME - this value should eventually be obtained from a config.py file
            if str(self.ui.MPLlineEditPowderCutThickFrom.text()) != '':
                Tfrom=float(str(self.ui.MPLlineEditPowderCutThickFrom.text()))
            else:
                Tfrom=xmin
            if str(self.ui.MPLlineEditPowderCutThickTo.text()) != '':
                Tto=float(str(self.ui.MPLlineEditPowderCutThickTo.text()))
            else:
                Tto=xmax
            
            Qmin=Tfrom
            Qmax=Tto
            Emin=Afrom
            Emax=Ato
            Amin=Afrom
            Amax=Ato
                
            Nxbins=100
            Nybins=100
#            Nxbins=int((Ato-Afrom)/Astep)
#            Nybins=int((Ato-Afrom)/Astep)

            
        elif indx==1:
            #case for Q along x axis
            minv=xmin
            maxv=xmax
            
            #determine the ranges of data to work with
            #from:to
            if str(self.ui.MPLlineEditPowderCutAlongFrom.text()) != '':
                Afrom=float(str(self.ui.MPLlineEditPowderCutAlongFrom.text()))
            else:
                Afrom=minv
            if str(self.ui.MPLlineEditPowderCutAlongTo.text()) != '':
                Ato=float(str(self.ui.MPLlineEditPowderCutAlongTo.text()))
            else:
                Ato=maxv
            if str(self.ui.MPLlineEditPowderCutAlongStep.text()) != '':
                Astep=float(str(self.ui.MPLlineEditPowderCutAlongStep.text()))
            else:
                Astep=0.035  #FIXME - this value should eventually be obtained from a config.py file
            if str(self.ui.MPLlineEditPowderCutThickFrom.text()) != '':
                Tfrom=float(str(self.ui.MPLlineEditPowderCutThickFrom.text()))
            else:
                Tfrom=ymin
            if str(self.ui.MPLlineEditPowderCutThickTo.text()) != '':
                Tto=float(str(self.ui.MPLlineEditPowderCutThickTo.text()))
            else:
                Tto=ymax
                
            Qmin=Afrom
            Qmax=Ato
            Emin=Tfrom
            Emax=Tto
            Amin=Afrom
            Amax=Ato
                
            Nxbins=100
            Nybins=100#int((Ato-Afrom)/Astep)
#            Nxbins=int((Ato-Afrom)/Astep)
#            Nybins=int((Ato-Afrom)/Astep)

                
        else:
            print "combo box index currently not supported...plot not updated and returning"
            return
        
        #check if the user has selected too many bins.
        if ((Nxbins > 1000) or (Nybins > 1000)):
            reply = QtGui.QMessageBox.question(self, 'Message',
                "The number of bins will exceed 1000 - continue (yes) or return (no) to reselect step size?", QtGui.QMessageBox.Yes | 
                QtGui.QMessageBox.No, QtGui.QMessageBox.No)

            if reply == QtGui.QMessageBox.Yes:
                #case to continue 
                pass
            else:
                #case to return and reselect
                return    
            
            
            
        #bin the data
        ad0=xname+','+str(Qmin)+','+str(Qmax)+','+str(Nxbins)  #|Q|
        ad1=yname+','+str(Emin)+','+str(Emax)+','+str(Nybins)  # E
        
        print "ad0: ",ad0
        print "ad1: ",ad1
        
        MDH=BinMD(InputWorkspace=ws,AlignedDim0=ad0,AlignedDim1=ad1)
        MDHflatten=MDHistoToWorkspace2D(MDH)
        MDHflatten.setTitle(str(self.ui.MPLcomboBoxActiveWorkspace.currentText())) 
        
        self.currentPlotWS=MDHflatten
        sig_orig=MDH.getSignalArray()
        sig=np.copy(sig_orig) #provide a working copy of the data to keep the original data in tact
        ne=MDH.getNumEventsArray()
#                dne=sig/ne
        dne=sig       
        
        dims=sig.shape
        NQ=dims[0]
        NE=dims[1]
        
        Emini=int(float(Emin-ymin)/float(dely)*NE)
        Emaxi=int(float(Emax-ymin)/float(dely)*NE)
        Qmini=int(float(Qmin-xmin)/float(delx)*NQ)
        Qmaxi=int(float(Qmax-xmin)/float(delx)*NQ)
        
        print "Emini: ",Emini,"  Emaxi: ",Emaxi," NE: ",NE," Emin: ",Emin," Emax: ",Emax," ymax: ",ymax," dely: ",dely
        print "Qmini: ",Qmini,"  Qmaxi: ",Qmaxi," NQ: ",NQ," Qmin: ",Qmin," Qmax: ",Qmax," xmax: ",xmax," delx: ",delx
       
        
        #now sum the data
        if indx==0:
            #case for Energy along x axis
            sigsum=np.sum(sig[Emini:Emaxi,Qmini:Qmaxi],1) #produces E plot
        elif indx==1:
            #case for Q along x axis
            sigsum=np.sum(sig[Emini:Emaxi,Qmini:Qmaxi],0) #produces |Q| plot
        else:
            print "combo box index currently not supported...plot not updated and returning"
            return           

        if str(self.ui.MPLlineEditPowderCutYFrom.text()) != '':
            Yfrom=float(str(self.ui.MPLlineEditPowderCutYFrom.text()))
        else:
            Yfrom=np.min(sigsum) #use a conservative minimum value
        if str(self.ui.MPLlineEditPowderCutYTo.text()) != '':
            Yto=float(str(self.ui.MPLlineEditPowderCutYTo.text()))
        else:
            Yto=np.max(sigsum) #use an upper bound maximum value
            
        mn=np.min(sigsum)
        mx=np.max(sigsum)
        print "** mn: ",mn," mx: ",mx
        
        print "type(dne): ",type(dne)
        print "dne.shape: ",dne.shape
        print "type(sigsum): ",type(sigsum)
        print "sigsum.shape: ",sigsum.shape
        print "XAxisStr: ",XAxisStr
        print "YAxisStr: ",YAxisStr
                
        #use a loop to plot once to the PyQt figure and second to the shadow figure
        for pl in range(2):   
            if pl == 0:
                self.canvas #enable drawing area
                fig=self.figure
            else:
                self.shadowCanvas
                fig=self.shadowFigure
            plt.figure(fig.number)

            #plot data
            ax=plt.subplot(111)
            if not(self.doOPlot):plt.clf
            if self.doOPlot:plt.hold(True)
            print "min(sigsum): ",np.min(sigsum),"  max(sigsum):", np.max(sigsum)
            plt.plot(sigsum,color=linecolor,linestyle=style,label=pltlegend)
            plt.legend(loc=legloc)
            if not(self.doOPlot):
                
                plt.title(plttitle)
                plt.xlabel(XAxisStr,labelpad=20)
                plt.ylabel(YAxisStr)
                if ((str(self.ui.MPLlineEditPowderCutYFrom.text())) != '' and (str(self.ui.MPLlineEditPowderCutYTo.text()) != '')):
                    rmin=float(str(self.ui.MPLlineEditPowderCutYFrom.text()))
                    rmax=float(str(self.ui.MPLlineEditPowderCutYTo.text()))
                    plt.ylim([rmin,rmax])
                else:
                    plt.ylim([np.min(sigsum),np.max(sigsum)])
            plt.hold(True)
            #overplot markers
            plt.plot(sigsum,color=markercolor,marker=mstyle,linestyle='')
            plt.hold(False)

    #       draw new axis
            print "Amin: ",Amin
            print "Amax: ",Amax
            print "Qmin: ",Qmin
            print "Qmax: ",Qmax
            print "Emin: ",Emin
            print "Emax: ",Emax

            Nticks=5.0
            delv=np.abs(Amax-Amin)
            tick_locations=delv*np.arange(Nticks)/(Nticks-1)+Amin
            #limit to 1 decimal place
            tick_locations=tick_locations.astype('float')
            tick_locations=tick_locations*10
            tick_locations=tick_locations.astype('int')
            tick_locations=tick_locations.astype('float')
            tick_locations=tick_locations/10
            tick_vals=[]
            for n in tick_locations:
                tick_vals.append(str(n))
                    
            plt.setp( ax.get_xticklabels(), visible=False)
            plt.setp( ax.get_xticklines(), visible=False)
            
            ax1=plt.twiny()
            plt.setp( ax1.get_xticklabels(), visible=True)
            plt.setp( ax1.get_xticklines(), visible=True)
            ax1.set_xticks(tick_locations) #new locations - sets number of ticks
            ax1.set_xticklabels(tick_vals) #new values - sets values of the ticks
            ax1.xaxis.set_ticks_position('bottom')
            ax1.set_axisbelow(True)
            
            if pl == 0:
                self.canvas.draw()
                self.canvas.setVisible(True)

                print "self.figure.number: ",self.figure.number
                pass
            else:
                self.shadowCanvas.draw()
                self.shadowCanvas.setVisible(False)

                print "self.shadowFigure.number: ",self.shadowFigure.number
                pass

        #clear oplot flag
        self.doOPlot=False
        
        
    def DoAnnotate(self):
        self.doAnnotate=True
        self.canvas.mpl_connect('button_press_event', self.onclick)
        
    def onclick(self,event):
        if self.doAnnotate:
            #first get the text to annotate
            txt=str(self.ui.MPLlineEditTextAnnotate.text())
            for pl in range(2):   
                if pl == 0:
                    self.canvas #enable drawing area
                    fig=self.figure
                    plt.figure(fig.number)
                    self.ui.txt=plt.text(event.xdata,event.ydata,txt)
                else:
                    self.shadowCanvas
                    fig=self.shadowFigure
                    plt.figure(fig.number)
                    self.ui.shadowtxt=plt.text(event.xdata,event.ydata,txt)
                
            self.canvas.draw()
            self.shadowCanvas.draw()
        self.doAnnotate=False
        
    def RemText(self):
        try:
            print "Removing Annotation Text"
            
            for pl in range(2):   
                if pl == 0:
                    self.canvas #enable drawing area
                    fig=self.figure
                    plt.figure(fig.number)
                    self.ui.txt.remove()
                else:
                    self.shadowCanvas
                    fig=self.shadowFigure
                    plt.figure(fig.number)
                    self.ui.shadowtxt.remove()
            
            self.canvas.draw()
            self.shadowCanvas.draw()
        except:
            #case where the button was pushed more than once and arrow should already be gone...do nothing
            pass
    
    def DoArrow(self):
        self.doArrow=True
        self.canvas.mpl_connect('button_press_event', self.onaclick)
        
    def onaclick(self,event):
        if self.doArrow:
            #first get the arrow direction
            dindx=self.ui.MPLcomboBoxArrow.currentIndex()
            #create arrow size relative to data range
            [xmin,xmax,ymin,ymax]=plt.axis()
            print "xmin: ",xmin," xmax: ",xmax," ymin: ",ymin," ymax: ",ymax
            delx=xmax-xmin
            dely=ymax-ymin
            #frac(tion) and h(ead)frac selected by trial and error...used to determine the relative size of the arrow
            frac=0.04  
            hfrac=0.02
            print "dindx: ",dindx
            for pl in range(2):
                if pl == 0:
                    self.canvas #enable drawing area
                    fig=self.figure
                    plt.figure(fig.number)
                else:
                    self.shadowCanvas
                    fig=self.shadowFigure
                    plt.figure(fig.number)   
                if dindx==0:
                    #point left
                    if pl==0:
                        self.ui.arrow=plt.arrow(event.xdata+frac*delx+hfrac*delx,event.ydata,-frac*delx,0,head_width=hfrac*dely,head_length=hfrac*delx,width=hfrac/5*dely,fc="k",ec="k")
                    else:
                        self.ui.shadowarrow=plt.arrow(event.xdata+frac*delx+hfrac*delx,event.ydata,-frac*delx,0,head_width=hfrac*dely,head_length=hfrac*delx,width=hfrac/5*dely,fc="k",ec="k")
                elif dindx==1:
                    #point right
                    if pl==0:
                        self.ui.arrow=plt.arrow(event.xdata-(frac*delx+hfrac*delx),event.ydata,frac*delx,0,head_width=hfrac*dely,head_length=hfrac*delx,width=hfrac/5*dely,fc="k",ec="k")
                    else:
                        self.ui.shadowarrow=plt.arrow(event.xdata-(frac*delx+hfrac*delx),event.ydata,frac*delx,0,head_width=hfrac*dely,head_length=hfrac*delx,width=hfrac/5*dely,fc="k",ec="k")
                        
                elif dindx==2:
                    #point up
                    if pl==0:
                        self.ui.arrow=plt.arrow(event.xdata,event.ydata-(frac*dely+hfrac*dely),0,frac*dely,head_width=hfrac*delx,head_length=hfrac*dely,width=hfrac/5*delx,fc="k",ec="k")
                    else:
                        self.ui.shadowarrow=plt.arrow(event.xdata,event.ydata-(frac*dely+hfrac*dely),0,frac*dely,head_width=hfrac*delx,head_length=hfrac*dely,width=hfrac/5*delx,fc="k",ec="k")
                        
                elif dindx==3:
                    #point down
                    if pl==0:
                        self.ui.arrow=plt.arrow(event.xdata,event.ydata+frac*dely+hfrac*dely,0,-frac*dely,head_width=hfrac*delx,head_length=hfrac*dely,width=hfrac/5*delx,fc="k",ec="k")
                    else:
                        self.ui.shadowarrow=plt.arrow(event.xdata,event.ydata+frac*dely+hfrac*dely,0,-frac*dely,head_width=hfrac*delx,head_length=hfrac*dely,width=hfrac/5*delx,fc="k",ec="k")
                        
                else:
                    #should never get here...
                    pass
            self.canvas.draw()
            self.shadowCanvas.draw()
        self.doArrow=False
        
    def RemArrow(self):
        try:
            self.ui.arrow.remove()
            self.canvas.draw()
            self.ui.shadowarrow.remove()
            self.shadowCanvas.draw()

        except:
            #case where the button was pushed more than once and arrow should already be gone...do nothing
            pass
            
    def SavePlot(self):
        
        self.shadowCanvas.setVisible(True)
        self.shadowFigure = plt.figure()
        self.shadowCanvas=FigureCanvas(self.shadowFigure)
        self.shadow_navigation_toolbar = NavigationToolbar(self.shadowCanvas, self.shadowCanvas)
        
        self.ui.MPLpushButtonSavePlot.setEnabled(False)
        """
        winID=self.ui.MPLframe.effectiveWinId()
        print " Save Window ID: ",winID
#        winID=QtGui.qApp.activeWindow()
#        print " Save Window ID2: ",winID
#        winID=self.ui.MPLPowderCutMainWindow.winID()
#        print " Save Window ID2: ",winID

        #        pwinID=self.ui.MPLframe.WinId()
#        print " Save Window ID 2: ",pwinID
        
        ws=self.currentPlotWS
        print "ws.getTitle: ",ws.getTitle()
        print "type(ws): ",type(ws)
        fname=ws.getTitle()
        filter='.jpg'
        wsname=fname+filter
        filename = str(QtGui.QFileDialog.getSaveFileName(self, 'Save Plot Window', fname,filter))
        qf=QtCore.QFile(filename)
        qf.open(QtCore.QIODevice.WriteOnly)
        
        #FIXME - currently writing zero length files...not sure the issue...
        p = QtGui.QPixmap.grabWindow(winID)
#        p = QtGui.QPixmap.grabWindow(1)

        p.save(qf, format=None)
        print " Saved: ",filename
        """
            
            
    def SaveData(self):
        ws=self.currentPlotWS
        print "ws.getTitle: ",ws.getTitle()
        print "type(ws): ",type(ws)
        fname=ws.getTitle()
        filter='.txt'
        wsname=fname+filter
        fsavename = str(QtGui.QFileDialog.getSaveFileName(self, 'Save ASCII Data', fname,filter))
        SaveAscii(ws,fsavename)
        
    def Done(self):
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
			#close application
            self.close()
        else:
			#do nothing and return
            pass               
        
if __name__=="__main__":
    print "MPLPC __main__"
    app = QtGui.QApplication(sys.argv)
    MPLPC = MPLPowderCut()
    MPLPC.show()
    sys.exit(app.exec_())

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    