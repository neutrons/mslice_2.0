import numpy as np
import matplotlib.pyplot as plt
from MPL1DCutHelpers import *
import time
import config
from MSliceHelpers import *


def DoSCPlotMSlice(self):
    print "Gothere1"
    __ws, NXDbins, NYDbins, linecolor, style, markercolor, mstyle, plttitle, pltlegend, legloc = getMPLParms(self)
    
    #make some test data
    #xaxis=range(100)
    #sigsum=range(100)
    
    #produce 1D Cut data
    pushButtonSCPlotCut(self)
    sigsum=self.ui.normalized.getSignalArray()
    xaxis=range(len(sigsum))
    
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
            ebar=2.0*np.sqrt(__ws.getErrorSquaredArray())/ne
            plt.errorbar(xaxis,sigsum,yerr=ebar,xerr=False,ecolor=errcolor,fmt='',label='_nolegend_')
            #seems to be a bug in errorbar that does not respect the color of the line so just replot the line once errorbar is done
            plt.hold(True)
            plt.plot(xaxis,sigsum,color=linecolor,linestyle=style,label=pltlegend)
            plt.hold(False)
        
        plt.legend(loc=legloc)
        if not(self.doOPlot):
            
            plt.title(plttitle)
            """
            plt.xlabel(XAxisStr,labelpad=20)
            plt.ylabel(YAxisStr)
            if ((str(self.ui.MPLlineEditPowderCutYFrom.text())) != '' and (str(self.ui.MPLlineEditPowderCutYTo.text()) != '')):
                rmin=float(str(self.ui.MPLlineEditPowderCutYFrom.text()))
                rmax=float(str(self.ui.MPLlineEditPowderCutYTo.text()))
                plt.ylim([rmin,rmax])
            else:
                plt.ylim([np.min(sigsum),np.max(sigsum)])
            """
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
        
    
    
    pass
    
    
def pushButtonSCPlotCut(self):
    print "Single Crystal Plot Cut Button pressed"
    
    #now extract values from this tab
    SCSXcomboIndex=self.ui.comboBoxSCCutX.currentIndex()
    SCSXFrom=self.ui.lineEditSCCutXFrom.text()
    SCSXTo=self.ui.lineEditSCCutXTo.text()
    SCSXStep=self.ui.lineEditSCCutXStep.text()
    SCSYcomboIndex=self.ui.comboBoxSCCutY.currentIndex()
    SCSYFrom=self.ui.lineEditSCCutYFrom.text()
    SCSYTo=self.ui.lineEditSCCutYTo.text()
    SCSZcomboIndex=self.ui.comboBoxSCCutZ.currentIndex()
    SCSZFrom=self.ui.lineEditSCCutZFrom.text()
    SCSZTo=self.ui.lineEditSCCutZTo.text()
    SCSEcomboIndex=self.ui.comboBoxSCCutE.currentIndex()
    SCSEFrom=self.ui.lineEditSCCutEFrom.text()
    SCSETo=self.ui.lineEditSCCutETo.text()
    SCSIntensityFrom=self.ui.lineEditSCCutIntensityFrom.text()
    SCSIntensityTo=self.ui.lineEditSCCutIntensityTo.text()
    SCSEcomboIndex=self.ui.comboBoxSCCutE.currentIndex()
    SCSThickFrom=self.ui.lineEditSCCutEFrom.text()
    SCSThickTo=self.ui.lineEditSCCutETo.text()
    print "SC Surface values: ",SCSXcomboIndex,SCSXFrom,SCSXTo,SCSXStep,SCSYcomboIndex,SCSYFrom,SCSYTo,SCSEcomboIndex,SCSEFrom,SCSETo,SCSIntensityFrom,SCSIntensityTo
    print "  More SC Surface values: ",SCSEcomboIndex,SCSThickFrom,SCSThickTo
    
    #**** code to extract data and perform plot placed here
    self.parent.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Single Crystal Sample: Plot Cut")				

    #determine which workspaces have been selected
    table=self.parent.ui.tableWidgetWorkspaces
    #first let's clean up empty rows
    Nrows=table.rowCount()
    Nws=0
    for row in range(Nrows):
        cw=table.cellWidget(row,config.WSM_SelectCol) 
        cbstat=cw.isChecked()
        #check if this workspace is selected for display
        if cbstat == True:
            #case where it is selected
            Nws+=1 #increment selected workspace counter
            #get workspace
            wsitem=str(table.item(row,config.WSM_WorkspaceCol).text())
            print " wsitem:",wsitem
            print " mtd.getObjectNames():",mtd.getObjectNames()
            __ws=mtd.retrieve(wsitem)
            
            #need to determine if this is a single or group workspace to obtain min/max values
            #get min & max range values for the MD workspace
            wsType=__ws.id()
            if wsType == 'WorkspaceGroup':
                minn=[__ws[0].getXDimension().getMinimum(),__ws[0].getYDimension().getMinimum(),__ws[0].getZDimension().getMinimum(),__ws[0].getTDimension().getMinimum()]
                maxx=[__ws[0].getXDimension().getMaximum(),__ws[0].getYDimension().getMaximum(),__ws[0].getZDimension().getMaximum(),__ws[0].getTDimension().getMaximum()]
                NEntries=__ws.getNumberOfEntries()
            else:
                # single workspace case
                minn=[__ws.getXDimension().getMinimum(),__ws.getYDimension().getMinimum(),__ws.getZDimension().getMinimum(),__ws.getTDimension().getMinimum()]
                maxx=[__ws.getXDimension().getMaximum(),__ws.getYDimension().getMaximum(),__ws.getZDimension().getMaximum(),__ws.getTDimension().getMaximum()]
                NEntries=1
                
            #get values from GUI and ViewSCCDict
            ViewSCCDict=self.ui.ViewSCCDict
            print "ViewSCCDict: ",ViewSCCDict
            if SCSXFrom =='':
                #SCSXFrom=minn[0]
                label=convertIndexToLabel(self,'X','Cut')   
                print "  label: ",label                 
                SCSXFrom = float(ViewSCCDict[label]['from'])
            else:
                SCSXFrom=float(SCSXFrom)
            if SCSXTo =='':
                #SCSXTo=maxx[0]
                label=convertIndexToLabel(self,'X','Cut')                    
                SCSXTo = float(ViewSCCDict[label]['to'])
            else:
                SCSXTo=float(SCSXTo)
            Nscx=int(round((SCSXTo-SCSXFrom)/float(SCSXStep)))
            
            if SCSYFrom =='':
                #SCSYFrom=minn[1]
                label=convertIndexToLabel(self,'Y','Cut')                    
                SCSYFrom = float(ViewSCCDict[label]['from'])
            else:
                SCSYFrom=float(SCSYFrom)
            if SCSYTo =='':
                #SCSYTo=maxx[1]
                label=convertIndexToLabel(self,'Y','Cut')                    
                SCSYTo = float(ViewSCCDict[label]['to'])
            else:
                SCSYTo=float(SCSYTo)    
                
            if SCSZFrom =='':
                #SCSZFrom=minn[2]
                label=convertIndexToLabel(self,'Z','Cut')                    
                SCSZFrom = float(ViewSCCDict[label]['from'])
            else:
                SCSZFrom=float(SCSZFrom)
            if SCSZTo =='':
                #SCSZTo=maxx[2]
                label=convertIndexToLabel(self,'Z','Cut')                    
                SCSZTo = float(ViewSCCDict[label]['to'])
            else:
                SCSZTo=float(SCSZTo)                    
                
            if SCSEFrom =='':
                #SCSEFrom=minn[3]
                label=convertIndexToLabel(self,'E','Cut')                    
                SCSEFrom = float(ViewSCCDict[label]['from'])
            else:
                SCSEFrom=float(SCSEFrom)
            if SCSETo =='':
                #SCSETo=maxx[3]
                label=convertIndexToLabel(self,'E','Cut')                    
                SCSETo = float(ViewSCCDict[label]['to'])
            else:
                SCSETo=float(SCSETo)
                
            #Derive names from Viewing Axes u and label fields
            #nameLst=makeSCNames(self)
            #Extract names from Plot Cut combo boxes
            nameLst=[]
            nameLst.append(self.ui.comboBoxSCCutX.currentText())
            nameLst.append(self.ui.comboBoxSCCutY.currentText())
            nameLst.append(self.ui.comboBoxSCCutZ.currentText())
            nameLst.append(self.ui.comboBoxSCCutE.currentText())
            #note that the comboBox label and that label needed by MDNormDirectSC are different - search for the case and replace with what's needed
            nameLst=['DeltaE' if x=='E (meV)' else x for x in nameLst]
                                                                
            #Format: 'name,minimum,maximum,number_of_bins'
            AD0=str(nameLst[0])+','+str(SCSXFrom)+','+str(SCSXTo)+','+str(Nscx)
            AD0=AD0.replace(config.XYZUnits,'')
            AD1=str(nameLst[1])+','+str(SCSYFrom)+','+str(SCSYTo)+','+str(1)
            AD1=AD1.replace(config.XYZUnits,'')
            AD2=str(nameLst[2])+','+str(SCSZFrom)+','+str(SCSZTo)+','+str(1)
            AD2=AD2.replace(config.XYZUnits,'')
            AD3=str(nameLst[3])+','+str(SCSEFrom)+','+str(SCSETo)+','+str(1)
            AD3=AD3.replace(config.XYZUnits,'')
            
            print "AD0: ",AD0,'  type: ',type(AD0)
            print "AD1: ",AD1,'  type: ',type(AD1)
            print "AD2: ",AD2,'  type: ',type(AD2)
            print "AD3: ",AD3,'  type: ',type(AD3)
            print "type(__ws): ",type(__ws)
            print "__ws: ",__ws.name
            histoData,histoNorm=MDNormDirectSC(__ws,AlignedDim0=AD0,AlignedDim1=AD1,AlignedDim2=AD2,AlignedDim3=AD3)
            print "histoNorm Complete"
            if wsType == 'WorkspaceGroup':
                print "histoData.getNumberOfEntries(): ",histoData.getNumberOfEntries()
                print "histoNorm.getNumberOfEntries(): ",histoNorm.getNumberOfEntries()
                #Loop thru each workspace in a group and calculate the data and norm for the requested parameters
                for k in range(NEntries):
                    print "Sum Loop: ",k," of ",NEntries
                    
                    if k == 0:
                        histoDataSum=histoData[k]
                        histoNormSum=histoNorm[k]
                    else:
                        histoDataSum+=histoData[k]
                        histoNormSum+=histoNorm[k]
            else:
                # case for a single workspace - just pass thru to sum workspaces
                histoDataSum=histoData
                histoNormSum=histoNorm
                
            #upon summing coresponding data and norm data, produce eht normalized result
            print "histoDataSum.id(): ",histoDataSum.id()
            print "histoNormSum.id(): ",histoNormSum.id()
            normalized=histoDataSum/histoNormSum   
            
            #let's check for values we don't want in the normalized data...
            # isinf : Shows which elements are positive or negative infinity
            # isposinf : Shows which elements are positive infinity
            # isneginf : Shows which elements are negative infinity
            # isnan : Shows which elements are Not a Number        
            
            #normalizedNew=normalized
            normArray=normalized.getSignalArray()
            normArray.flags.writeable=True  #note that initially the array is not writeable, so change this
            indx=np.isinf(normArray)
            normArray[indx]=0    
            indx=np.isnan(normArray)
            normArray[indx]=0     
            normArray.flags.writeable=False #now put it back to nonwriteable
            normalized.setSignalArray(normArray)
            
            
            #Plot data here - note, not currently addressing having multiple
            #FIXME - check if multiple plots needs to be supported
            #data sets to plot and not sure that this case needs to be supported
            #given how the application is currently constructed - will sort this
            #out later
            self.ui.normalized=normalized
            
            
            
            #determine workspace type
            #stubbing this part out for now...
    if Nws < 1:
        #check if we have any workspaces to work with - return if not
        print "No workspaces selected - returning"
        dialog=QtGui.QMessageBox(self)
        dialog.setText("No workspaces selected - returning")
        dialog.exec_()
        return