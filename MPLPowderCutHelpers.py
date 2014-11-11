import sys,os
#import Mantid computatinal modules
sys.path.append(os.environ['MANTIDPATH'])
from mantid.simpleapi import *     
import numpy as np
import matplotlib.pyplot as plt

from PyQt4 import Qt,QtCore, QtGui

def DoPlotMSlice(self):
    
    ws_sel=str(self.ui.MPLcomboBoxActiveWorkspace.currentText())
    ws=mtd.retrieve(ws_sel)
    NXDbins=ws.getXDimension().getNBins()
    NYDbins=ws.getYDimension().getNBins()
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
        set1DBinVals(self,ws)
    
    
    
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
    
    
    
    
    if NXDbins > 1 and NYDbins > 1:
        #********************************************************************
        #2D data plot case
        #********************************************************************
        if not(self.doOPlot):self.ui.MPLpushButtonPopPlot.setEnabled(True)
    
    
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
        
        #NbinsX=wsX.getNBins()
        #NbinsY=wsY.getNBins()
        
        NbinsX=int(self.ui.MPLspinBoxAlong.text())
        NbinsY=int(self.ui.MPLspinBoxAlong.text())
    
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
                
            Nxbins=NbinsX
            Nybins=NbinsY
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
                
            Nxbins=NbinsY
            Nybins=NbinsX
            #int((Ato-Afrom)/Astep)
            #Nxbins=int((Ato-Afrom)/Astep)
            #Nybins=int((Ato-Afrom)/Astep)
    
                
        else:
            print "combo box index currently not supported...plot not updated and returning"
            return
    
        #check if the user has selected too many bins.
        if ((Nxbins > 10000) or (Nybins > 10000)):
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
        
        #BinMD seems to require that Qmin != Qmax, if so, bump Qmax up a bit...
        if Qmin == Qmax:
            Qmax=Qmax*1.0001
            
        #now do a sanity check on Qmin and Qmax
        if Qmin > Qmax:
            #problem as this should not occur
            dialog=QtGui.QMessageBox(self)
            dialog.setText("Problem: Qmin > Qmax - Returning")
            dialog.exec_()
            return   
            
        ad0=xname+','+str(Qmin)+','+str(Qmax)+','+str(Nxbins)  #|Q|
        ad1=yname+','+str(Emin)+','+str(Emax)+','+str(Nybins)  # E
        
        #Check GUI for output binning parameters
        if self.ui.radioButtonNBins.isChecked():
            NOutBins=int(str(self.ui.MPLlineEditPowderCutAlongNbins.text()))
            BWOut=(Amax-Amin)/NOutBins
        elif self.ui.radioButtonBinWidth.isChecked():
            BWOut=int(float(str(self.ui.MPLlineEditPowderCutAlongStep.text())))
            NOutBins=int(float((Amax-Amin)/BWOut))
        else:
            #unknown case
            print "Unsupported radiobutton option - returning"
            return
            
    
        if indx == 0:
            #plot energy along X axis
            Nxabins=1
            Nyabins=NOutBins
        elif indx == 1:
            #plot Q along X axis
            Nyabins=1
            Nxabins=NOutBins
        else:
            print "Case unknown..."
            return
        
        tmp=self.ui.MPLlineEditPowderCutWidth.text()
        print "tmp: ",tmp,"  type tmp: ",type(tmp)
        DeltaQE=float(str(self.ui.MPLlineEditPowderCutWidth.text()))
                        
        ad0a=xname+','+str(Qmin-DeltaQE/2)+','+str(Qmax+DeltaQE/2)+','+str(Nxabins)  #|Q|
        ad1a=yname+','+str(Emin)+','+str(Emax)+','+str(Nyabins)  # E
    
        print "ad0: ",ad0
        print "ad1: ",ad1
        print "ad0a: ",ad0a
        print "ad1a: ",ad1a
    
        #Investigate later why these point to the opposite ones...hmm.
        ad0str=ad1.split(',')
        ad1str=ad0.split(',')
    
        #First time thru from MSlice main program these values are not set, so set these labels
        self.ui.MPLlineEditPowderCutAlongFrom.setText("%.3f" % float(ad0str[1]))
        self.ui.MPLlineEditPowderCutAlongTo.setText("%.3f" % float(ad0str[2]))
        self.ui.MPLlineEditPowderCutThickFrom.setText("%.3f" % float(ad1str[1]))
        self.ui.MPLlineEditPowderCutThickTo.setText("%.3f" % float(ad1str[2]))
        self.ui.MPLlineEditPowderCutAlongNbins.setText(str(int(ad0str[3])))
        self.ui.MPLlineEditPowderCutAlongStep.setText("%.3f" % ((float(ad0str[2])-float(ad0str[1]))/float(ad0str[3])))
    
        MDH=BinMD(InputWorkspace=ws,AlignedDim0=ad0,AlignedDim1=ad1)#2D rebinned workspace 
        MDH1D=BinMD(InputWorkspace=ws,AlignedDim0=ad0a,AlignedDim1=ad1a) #define a 1 bin width histogram to have BinMD do summation for us
    
        self.ui.current1DWorkspace=MDH1D  #identify 1D workspace for use later such as with Save Plot WS
    
        #SaveMD(MDH,'C:\Users\mid\Documents\Mantid\Powder\MDH.nxs')  #used for debugging
            
        MDHflatten=MDHistoToWorkspace2D(MDH)
        MDHflatten.setTitle(str(self.ui.MPLcomboBoxActiveWorkspace.currentText())) 
        self.currentPlotWS=MDHflatten  #MDHflatten needed for saving ASCII data
    
        if self.ui.checkBoxUseNorm.isChecked():
            #case to normalize by number of events
            ne=MDH1D.getNumEventsArray()
        else:
            #else just divde by 1 to show data as is
            ne=1
        #                dne=sig/ne
        #dne=sig/ne       
    
        #dims=sig.shape
        #NQ=dims[0]
        #NE=dims[1]
    
        #now sum the data
        if indx==0:
            #case for Energy along x axis
            #sigsum=np.sum(sig,1) #produces E plot
            sigsum=MDH1D.getSignalArray()/ne
        elif indx==1:
            #case for Q along x axis
            #sigsum=np.sum(sig,0) #produces |Q| plot
            sigsum=MDH1D.getSignalArray()/ne
        else:
            print "combo box index currently not supported...plot not updated and returning"
            return            
        
        #calculate errorbar    
        ebar=np.sqrt(MDH1D.getErrorSquaredArray())/ne
            
        #Determine binning parameters
        Nbins=MDH1D.getSignalArray().size
        b1=MDH1D.getYDimension().getMaximum()  #Appears that |Q| is in X and E is in Y for this workspace
        b0=MDH1D.getYDimension().getMinimum()
        
        print "type(MDH): ",type(MDH)
        print "type(MDH1D): ",type(MDH1D)
        print "** XMAX: ",MDH1D.getXDimension().getMaximum()
        print "** XMIN: ",MDH1D.getXDimension().getMinimum()
        print "** YMAX: ",MDH1D.getYDimension().getMaximum()
        print "** YMIN: ",MDH1D.getYDimension().getMinimum()
        
        
        width=(b1-b0)/Nbins
        print "width: ",width
        #Now set these parameters in the GUI
        self.ui.MPLlineEditPowderCutAlongNbins.setText(str(int(Nbins)))
        self.ui.MPLlineEditPowderCutAlongStep.setText("%.2f" % width)
    
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
    
        #print "type(dne): ",type(dne)
        #print "dne.shape: ",dne.shape
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
            if self.ui.checkBoxRemoveNans.isChecked():
                #case to clean up Nan, inf, and -inf in data
                indx=np.isinf(sigsum)
                sigsum[indx]=0
                indx=np.isnan(sigsum)
                sigsum[indx]=0
    
            #determine xaxis values
            Nsigsum=len(sigsum)
            xaxis=((np.arange(float(Nsigsum))/float(Nsigsum-1))*(Amax-Amin))+Amin
                
            plt.plot(xaxis,sigsum,color=linecolor,linestyle=style,label=pltlegend)
            if self.ui.checkBoxErrorBars.isChecked():
                #case to add errorbars
                errcolor=str(self.ui.MPLcomboBoxErrorColor.currentText())
                plt.errorbar(xaxis,sigsum,yerr=ebar,xerr=False,ecolor=errcolor,fmt='')
                #seems to be a bug in errorbar that does not respect the color of the line so just replot the line once errorbar is done
                plt.hold(True)
                plt.plot(xaxis,sigsum,color=linecolor,linestyle=style,label=pltlegend)
                plt.hold(False)
            
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
            plt.plot(xaxis,sigsum,color=markercolor,marker=mstyle,linestyle='')
            plt.hold(False)
    
            #draw new axis
            print "Afrom: ",Afrom
            print "Ato: ",Ato
            print "Amin: ",Amin
            print "Amax: ",Amax
            print "Qmin: ",Qmin
            print "Qmax: ",Qmax
            print "Emin: ",Emin
            print "Emax: ",Emax
            """
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
            """
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
    else:
        #********************************************************************
        #note that we have workspace ws from above
        # 1D case to plot
        #********************************************************************
        if not(self.doOPlot):self.ui.MPLpushButtonPopPlot.setEnabled(True)
        
        if self.ui.checkBoxUseNorm.isChecked():
            #case to normalize by number of events
            ne=ws.getNumEventsArray()
        else:
            #else just divde by 1 to show data as is
            ne=1

        print "type(ws): ",type(ws)
#        self.currentPlotWS=ConvertToMatrixWorkspace(ws)
        MDHflatten=MDHistoToWorkspace2D(ws)
        MDHflatten.setTitle(str(self.ui.MPLcomboBoxActiveWorkspace.currentText())) 
        self.currentPlotWS=MDHflatten  #MDHflatten needed for saving ASCII data
        self.ui.current1DWorkspace=ws

        sigsum=ws.getSignalArray()/ne
                    #determine xaxis values
        Nsigsum=len(sigsum)
        
        #Set Data Formatting GUI info using the workspace history
        set1DBinVals(self,ws)
        #Now get values from the GUI
        Afrom=float(str(self.ui.MPLlineEditPowderCutAlongFrom.text()))
        Ato=float(str(self.ui.MPLlineEditPowderCutAlongTo.text()))
        
        xaxis=((np.arange(float(Nsigsum))/float(Nsigsum-1))*(Ato-Afrom))+Afrom
        
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
            plt.plot(xaxis,sigsum,color=linecolor,linestyle=style,label=pltlegend)
            if self.ui.checkBoxErrorBars.isChecked():
                #case to add errorbars
                errcolor=str(self.ui.MPLcomboBoxErrorColor.currentText())
                ebar=np.sqrt(ws.getErrorSquaredArray())/ne
                plt.errorbar(xaxis,sigsum,yerr=ebar,xerr=False,ecolor=errcolor,fmt='')
                #seems to be a bug in errorbar that does not respect the color of the line so just replot the line once errorbar is done
                plt.hold(True)
                plt.plot(xaxis,sigsum,color=linecolor,linestyle=style,label=pltlegend)
                plt.hold(False)
            
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
            plt.plot(xaxis,sigsum,color=markercolor,marker=mstyle,linestyle='')
            plt.hold(False)
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

    
def getSVValues(self):
    """
    Function to get the values from the Slice Viewer and provide them to the MPL tools
    
    """
    wsNames=mtd.getObjectNames()
    cntws=0
    lcnt=-1
    indxws=-1
    rcnt=-1
    cntws2=0
    for tws in wsNames:
        lcnt+=1
        pos=tws.find('_line') #look for line workspaces created by SliceViewer
        if pos > 0:
            #case we found a line workspace
            cntws+=1
            indxws=lcnt
        pos2=tws.find('_rebinned') #look for line workspaces created by SliceViewer
        if pos2 > 0:
            #case we found a line workspace
            cntws2+=1
            indxws2=rcnt
    #now check for problems
    if lcnt < 0 or cntws == 0 or cntws > 1 or indxws < 0:
        #case with a problem
        print "Unable to locate a line workspace"
        dialog=QtGui.QMessageBox(self)
        dialog.setText("No workspaces from Slice Viewer Available - Returning to Powder Cut GUI")
        dialog.exec_()
        return
    else:
        pass
    if cntws > 1:
        print "Ambiguous case where more than one line workspace was discovered"
        #in this case, check which workspaces are selected in the Workspace Manager and take the
        #corresponding _line workspace
        table=self.ui.tableWidgetWorkspaces 
        #need to determine which workspaces are selected 
        Nrows=table.rowCount()
        wslst=[]  #to contain the list of currently selected workspaces
        for row in range(Nrows):
            cw=table.cellWidget(row,self.WSM_SelectCol) 
            cbstat=cw.isChecked()
            if cbstat:
                wslst.append(str(table.item(row,self.WSM_WorkspaceCol).text()))
        #now from the list of selected workspaces, check which one has a corresponding "_line" workspace
        #we now have wsNames with the complete list of Mantid workspaces 
        #we also constructed wslst which contains the list of selected workspaces
        #so we need to iterate thru one list to see if any workspaces are contained in the other list
        for ws in wslst:
            if any(ws in w for w in wsNames):
                #if true, we've found the workspace from Workspace Manager that corresponds to Slice Viewer
                #Need to check if Slice Viewer can take more than one workspace in at a time as this case may 
                #need to be handled more carefully
                wsSel=ws  
    else:
        tmpws=wsNames[indxws]
        lws=mtd.retrieve(tmpws)
        
        rws=mtd.retrieve(wsNames[indxws2])
        NbinsX=rws.getXDimension().getNBins()
        NbinsY=rws.getYDimension().getNBins()
        
        """
        #used to debug externally using this workspace
        print "** type(lws): ",type(lws)
        SaveMD(tmpws,Filename='C:\Users\mid\Documents\Mantid\Powder\zrh_1000_line.nxs')
        """
        
        tmpws=tmpws.split('_line')
        if tmpws[0] !=[]:
            #case where we have a workspace
            wsSel=tmpws[0]
            #get the number of output bins
            NOutBins=lws.getSignalArray().size
            #now determine the bin width size
            mx=lws.getXDimension().getMaximum()
            mn=lws.getXDimension().getMinimum()
            BWOut=(mx-mn)/NOutBins
            
            print "** BWOut XMAX: ",lws.getXDimension().getMaximum()
            print "** BWOut XMIN: ",lws.getXDimension().getMinimum()
            print "** BWOut YMAX: ",lws.getYDimension().getMaximum()
            print "** BWOut YMIN: ",lws.getYDimension().getMinimum()

            
            
        else:
            #case where the base workspace did't surface properly...warn and return
            dialog=QtGui.QMessageBox(self)
            dialog.setText("Unable to identify a base workspace name from line workspace - Returning")
            dialog.exec_()
            return            
                
    #At this point we currently assume that we have one selected workspace and one corresponding _line workspace
    
    
    if wsNames[indxws] == wsSel+'_line':
        wsLine=wsNames[indxws]
    else:
        dialog=QtGui.QMessageBox(self)
        dialog.setText("Missing _line workspace - try running Slice Viewer again - returning")
        dialog.exec_()
        return        
    
    """
    In getting to this point, we assume:
        wsSel is the original workspace selected in MSlice Workspace Manager
        wsLine is the corresponding line workspace

    """
    print "  wsSel:  ",wsSel
    print "  wsLine: ",wsLine
    #Need to retrieve these workspaces from the Mantid layer
    wsLine=mtd.retrieve(wsLine)
    

    #first verify the rebinned workspace is not already on the MPL list of workspaces 
    #and if not insert the rebinned workspace into the list
    #  Getting the list of workspaces in the MPL combobox:
    NMPLCombo=self.ui.MPLcomboBoxActiveWorkspace.count()
    if NMPLCombo >0:
        #case where there are more than 0 workspaces in the list
        wsMPLCombo=[self.ui.MPLcomboBoxActiveWorkspace.itemText(i) for i in range(NMPLCombo)]
        
    #now check if wsSel is already on the list
    if any(wsSel in w for w in wsMPLCombo):
        #case where it's already there - do nothing
        pass
    else:
        #case to add the workspace to the list
        self.ui.MPLcomboBoxActiveWorkspace.insertItem(NMPLCombo,wsSel)
        self.ui.MPLcomboBoxActiveWorkspace.setCurrentIndex(NMPLCombo)

    h=wsLine.getHistory()
    ah=h.getAlgorithmHistories()
    Nah=len(ah)
    print "Nah: ",Nah
    #find BinMD history
    cntBMD=0
    for i in range(Nah):
        algName=wsLine.getHistory().getAlgorithmHistories()[i].name()
        if algName == 'BinMD':
            indxBMD=i
            algNameSel=algName
            cntBMD+=1
            #break #this will cause the for loop to terminate early however may want to check for additional BinMD cases
        print i
    if cntBMD > 1:
        print "Ambiguous case - more than one BinMD found!"
    print "indxBMD: ",indxBMD
    NProps=len(ah[indxBMD].getProperties())
    print "NProps: ",NProps
    for i in range(NProps):
        if ah[indxBMD].getProperties()[i].name() == 'BasisVector0':
            indxBV0=i
        if ah[indxBMD].getProperties()[i].name() == 'BasisVector1':
            indxBV1=i
        if ah[indxBMD].getProperties()[i].name() == 'Translation':
            indxTran=i
        if ah[indxBMD].getProperties()[i].name() == 'OutputExtents':
            indxOE=i        
            
        print ah[indxBMD].getProperties()[i].name(),"    ",ah[indxBMD].getProperties()[i].value()
        
    BV0=ah[indxBMD].getProperties()[indxBV0].value()
    BV0=BV0.split(',')
    BV1=ah[indxBMD].getProperties()[indxBV1].value()
    BV1=BV1.split(',')
    Tran=ah[indxBMD].getProperties()[indxTran].value()
    Tran=Tran.split(',')
    OE=ah[indxBMD].getProperties()[indxOE].value()
    OE=OE.split(',')

    X0=float(BV0[2])
    X1=float(BV0[3])
    Y0=float(BV1[2])
    Y1=float(BV1[3])

    T0=float(Tran[0])
    T1=float(Tran[1])
    E0=float(OE[0])
    E1=float(OE[1])
    E2=float(OE[2])
    E3=float(OE[3])

    Emintmp=E0*X0+E1*X1+T1
    Emaxtmp=T1
    Emin=min(Emintmp,Emaxtmp)
    Emax=max(Emintmp,Emaxtmp)
    
    print "** Emin: ",Emin,"  Emax: ",Emax


    Qmintmp=E0*Y0+E1*Y1+T0
    Qmaxtmp=T0
    Qmin=min(Qmintmp,Qmaxtmp)
    Qmax=max(Qmintmp,Qmaxtmp)
    
    print "getXDimension().getMaximum(): ",lws.getXDimension().getMaximum()
    print "getXDimension().getMinimum(): ",lws.getXDimension().getMinimum()
    print "getYDimension().getMaximum(): ",lws.getYDimension().getMaximum()
    print "getYDimension().getMinimum(): ",lws.getYDimension().getMinimum()
    
    DeltaQE=lws.getYDimension().getMaximum() - lws.getYDimension().getMinimum()
    print "DeltaQE: ",DeltaQE
    print "** Qmin: ",Qmin,"  Qmax: ",Qmax          
    
    #now let's set things in the MPLPowderCut GUI
    #put values in the Q and E text boxes
    self.ui.MPLlineEditPowderCutAlongFrom.setText("%.3f" % Emin)
    self.ui.MPLlineEditPowderCutAlongTo.setText("%.3f" % Emax)  
    self.ui.MPLlineEditPowderCutThickFrom.setText("%.3f" % Qmin)
    self.ui.MPLlineEditPowderCutThickTo.setText("%.3f" % Qmax)   
    self.ui.MPLlineEditPowderCutAlongStep.setText("%.2f" % BWOut)
    self.ui.MPLlineEditPowderCutAlongNbins.setText(str(int(NOutBins)))
    self.ui.MPLspinBoxAlong.setValue(int(NbinsY))
    self.ui.MPLspinBoxThick.setValue(int(NbinsX))
    self.ui.MPLlineEditPowderCutWidth.setText("%.3f" % DeltaQE)
    
    print "BWOut: ",BWOut
    
    #set the pulldown menus 
    self.ui.MPLcomboBoxPowderCutAlong.setCurrentIndex(0)
    self.ui.MPLcomboBoxPowderCutThick.setCurrentIndex(1)
    self.ui.MPLcomboBoxPowderCutY.setCurrentIndex(0)
    
    #now that we've set everything, let's call the plot!
    DoPlotMSlice(self)

def set1DBinVals(self,ws):
    #first check if we have a valie workspace
    try:
        #if the workspace has a name, it's an existing workspace
        ws.name()
    except:
        print "Workspace does not exist - returning"
        return
        
    NXDbins=ws.getXDimension().getNBins()
    NYDbins=ws.getYDimension().getNBins()
    
    if NXDbins > 1 and NYDbins > 1:
        #2D workspace case - return
        print "2D workspace given but need 1D workspace - returning"
        return
    
    #get the number of history entries
    NEntries=len(ws.getHistory().getAlgorithmHistories())    
    #find the last BinMD operation as we can get binning parameters from here
    for i in NEntries-np.arange(NEntries)-1:
        entry=ws.getHistory().getAlgorithmHistories()[i].name()
        if entry=='BinMD':
            #case we found the BinMD case - exit loop
            break
    NTags=len(ws.getHistory().getAlgorithmHistories()[i].getProperties())
    for j in range(NTags):
        name=str(ws.getHistory().getAlgorithmHistories()[i].getProperties()[j].name())
        value=str(ws.getHistory().getAlgorithmHistories()[i].getProperties()[j].value())
        value=value.split(',')
        if name=='AlignedDim0':
            ad0str=value
        if name=='AlignedDim1':
            ad1str=value
    
    if ad1str[3]=='1':
        #case where ad0 contains the Amin and Amax values
        self.ui.MPLlineEditPowderCutAlongFrom.setText("%.3f" % float(ad0str[1]))
        self.ui.MPLlineEditPowderCutAlongTo.setText("%.3f" % float(ad0str[2]))
        self.ui.MPLlineEditPowderCutThickFrom.setText("%.3f" % float(ad1str[1]))
        self.ui.MPLlineEditPowderCutThickTo.setText("%.3f" % float(ad1str[2]))
        self.ui.MPLlineEditPowderCutAlongNbins.setText(str(int(ad0str[3])))
        self.ui.MPLlineEditPowderCutAlongStep.setText("%.3f" % ((float(ad0str[2])-float(ad0str[1]))/float(ad0str[3])))
        
    if ad0str[3]=='1':
        #case where ad1 contains the Amin and Amax values
        self.ui.MPLlineEditPowderCutAlongFrom.setText("%.3f" % float(ad1str[1]))
        self.ui.MPLlineEditPowderCutAlongTo.setText("%.3f" % float(ad1str[2]))
        self.ui.MPLlineEditPowderCutThickFrom.setText("%.3f" % float(ad0str[1]))
        self.ui.MPLlineEditPowderCutThickTo.setText("%.3f" % float(ad0str[2]))
        self.ui.MPLlineEditPowderCutAlongNbins.setText(str(int(ad1str[3])))
        self.ui.MPLlineEditPowderCutAlongStep.setText("%.3f" % ((float(ad1str[2])-float(ad1str[1]))/float(ad1str[3])))
        
    #use the number of bins corresponding to the 1D data array
    self.ui.radioButtonNBins.setChecked(True)
        
        
        
        
        
        
    
    
    