import numpy as np
import matplotlib.pyplot as plt
import time
import config
from MSliceHelpers import *
from utils_dict_xml import *

def DoSCPlotMSlice(self):
    #Not sure why, but it was necessary to include MPL1DCutHelpers inside this function definition for it to be found
    from MPL1DCutHelpers import *
    
    #get parameters from 1D cut GUI
    __wstmp, NXDbins, NYDbins, linecolor, style, markercolor, mstyle, plttitle, pltlegend, legloc = getMPLParms(self)
    #FIXME
    #Found in Linux version that plot cut seemed to be stepping on the 
    #workspace used by sliceviewer.  To circumvent this problem, passing a 
    #clone workspace to the cut tool - seems to work for now but maybe worth
    #a second look sometime.
    __ws=CloneWorkspace(__wstmp)
    #cut the workspace
    produce1DCut(self,__ws)
    #note that __ws not used in this function past this point
    
    if self.ui.checkBoxUseNorm.isChecked():
        sigsum=self.ui.histoDataSum.getSignalArray()/self.ui.histoDataSum.getNumEventsArray()
        normsum=self.ui.histoDataSum.getNumEventsArray()
    else:
        sigsum=self.ui.histoDataSum.getSignalArray()
        normsum=1

    #During each plotting pass, update ASCII data available to be saved to file
    createASCII(self)
    #define the 1D workspace in case user wants to save this out to a file
    self.ui.current1DWorkspace=self.ui.histoDataSum
    
    Nsigsum = len(sigsum)
    indx=self.ui.comboBoxSCCutX.currentIndex() #use comboBox currentIndex() as the pointer to the corresponding dimension names
    #note that when creating the histo workspaces that they are oredred according the AD* values
    #thus the one we want to use for plotting is always in position 0 here.
    print "** indx: ",indx
    if str(self.ui.lineEditSCCutXFrom.text()) != '':
        Amin=float(str(self.ui.lineEditSCCutXFrom.text()))
    else:
        Amin=self.ui.histoDataSum.getDimension(0).getMinimum()
    if str(self.ui.lineEditSCCutXTo.text()) != '':
        Amax=float(str(self.ui.lineEditSCCutXTo.text()))
    else:
        Amax=self.ui.histoDataSum.getDimension(0).getMaximum()
    
    name=self.ui.histoDataSum.getDimension(0).getName()
    units=self.ui.histoDataSum.getDimension(0).getUnits()
    if units == "DeltaE":
        units= " in E(meV)"
    
    XAxisStr=name+" "+units
    for i in range(4):
        #print "  "+self.ui.histoDataSum.getDimension(i).getName()
        pass
    YAxisStr='Signal'
    print " XAxisStr: ",XAxisStr

    xaxis=((np.arange(float(Nsigsum))/float(Nsigsum-1))*(Amax-Amin))+Amin
    
    #for debug purposes
    #SaveMD(self.ui.normalized,Filename='wsn.nxs')
    
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
        self.ui.ax=ax
        if not(self.doOPlot):plt.clf
        if self.doOPlot:plt.hold(True)
        plt.plot(xaxis,sigsum,color=linecolor,linestyle=style,label=pltlegend)
        if self.ui.checkBoxErrorBars.isChecked():
            #case to add errorbars
            errcolor=str(self.ui.MPLcomboBoxErrorColor.currentText())
            
            #The variance has units of Data^2, while the mean and std have the same units as Data
            #thus take sqrt of data before normalizing
            ebar=2.0*np.sqrt(self.ui.histoDataSum.getErrorSquaredArray())/normsum
            plt.errorbar(xaxis,sigsum,yerr=ebar,xerr=False,ecolor=errcolor,fmt='',label='_nolegend_')
            #seems to be a bug in errorbar that does not respect the color of the line so just replot the line once errorbar is done
            plt.hold(True)
            plt.plot(xaxis,sigsum,color=linecolor,linestyle=style,label=pltlegend)
            plt.hold(False)
        
        plt.legend(loc=legloc)
        if not(self.doOPlot):
            
            plt.title(plttitle)
            plt.xlabel(XAxisStr,labelpad=20)
            plt.ylabel(YAxisStr)
            """
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
        
    #check if we are in OPlot mode or not, if not, then enable pop plot button
    if not(self.doOPlot):self.ui.MPLpushButtonPopPlot.setEnabled(True)
    #clear oplot flag
    self.doOPlot=False
    
    
def produce1DCut(self,__ws):
    """
    Function to extract MPL GUI parameters and workspace parameters
    in order to construct a call to the 1D Cut algorithm function below
    
    """
    
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
        
    #**** code to extract data and perform plot placed here
    self.parent.ui.StatusText.append(time.strftime("%a %b %d %Y %H:%M:%S")+" - Single Crystal Sample: Plot Cut")				
    
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
    print "__ws: ",__ws.name()

    #make call to Mantid algorithms
    __wsHisto = alg1DCut(__ws,AD0,AD1,AD2,AD3) 
    print " __wsHisto.name(): ",__wsHisto.name()
        
    #save results in the object
    self.ui.histoDataSum=__wsHisto

        
def alg1DCut(__ws,AD0,AD1,AD2,AD3):
    #Final 1D cut algorithm implemented here utilizing Mantid algorithms
    #This function is formatted to facilitate it being unit tested
    
    #here __ws is a single workspace, either always was a single workspace or it was merged into one
    
    #to adapt this function to work with either 2D or 1D workspaces, must first
    #check workspace dimensionallity
    
    if 'Group' in __ws.id():
        #case for a group workspace
        NXDbins=__ws[0].getXDimension().getNBins()	
        NYDbins=__ws[0].getYDimension().getNBins()
    else:
        #case for an individual workspace
        NXDbins=__ws.getXDimension().getNBins()	
        NYDbins=__ws.getYDimension().getNBins() 
    
    print "NXDbins: ",NXDbins,"  NYDbins: ",NYDbins
    
    
    """
    The method below uses the newly developed MDNormDirectSC() mantid algorithm.
    However an issue was discovered that the resultant summed workspaces are not
    of the correct type for SliceViewer to output <wsName>_line workspaces.  
    Realizing this, the "old" method of using ConvertToMD --> MergeMD --> BinMD
    will be used in it's place below.  Using BinMD enables use of non-orthogonal
    lines cut from the 2D workspaces in SliceViewer, however the normalization method 
    in MDNormDirectSC() is better.
    
    For now it's more direct to just use the BinMD methodology and revisit using
    the newer MDNormDirectSC method in future versions of MSlice which will give
    the opportunity to revisit SliceViewer as well.
    """
    """
    #only need to use the given workspace in 1D case
    if not(NXDbins > 1 and NYDbins > 1):
        #1D case
        histoDataSum=__ws
        histoNormSum=__ws/__ws #don't have a norm workspace in this case so make one as a placeholder...
        
    else:
        #Here in 2D case, need to do more...    
        wsType=__ws.id()
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
    """
    
    """
    BinMD method for calculating workspaces to use with SliceViewer
    
    """

    #now check the dimensionality
    
    __ows=__ws.name()+'_histo'
    NXbins=__ws.getXDimension().getNBins()
    NYbins=__ws.getYDimension().getNBins()
    print "NXbins: ",NXbins,"  NYbins: ",NYbins
    if NXbins > 1 and NYbins > 1:
        #case for a MD workspace - perform BinMD to create the 1D data set
        #requires BinMD to be run
        BinMD(__ws,AlignedDim0=AD0,AlignedDim1=AD1,AlignedDim2=AD2,AlignedDim3=AD3,OutputWorkspace=__ows)
        __wsHisto = mtd.retrieve(__ows)
    else:
        #case where BinMD has alread been done previously
        print "Bypassing BinMD"
        __wsHisto=__ws


    
    return __wsHisto

    
def createASCII(self):
    #using the current 1D workspace, create an ASCII data set to save
    #self.currentPlotWS=ConvertToMatrixWorkspace(__ws)
    #FIXME - question for if users want normalized or non-normalized data here
    #Currently non-normalized data is provided
    __MDHflatten=MDHistoToWorkspace2D(self.ui.histoDataSum)
    __MDHflatten.setTitle(str(self.ui.MPLcomboBoxActiveWorkspace.currentText())) 
    self.currentPlotWS=__MDHflatten  #__MDHflatten needed for saving ASCII data    
    
    pass
    
def getSVValuesSC(self,__lws):
    """
    This helper function extracts the history values from the  __lws line workspace.  
    The returned results are
    formatted for easy access for populating the SC version of the1D Cut GUI
    
    """
    #This import needs to be inside the function definition as python
    #scoping does not traverse multiple levels
    #import config
    
    #Next two lines for debug...
    #from mantid.simpleapi import * 
    #SaveMD(__lws,Filename='C:/Users/mid/Documents/PyQt/MSlice/mslice_2.0-0.304-dev/lws.nxs')
    
    #extract history info from 
    #get the number of history entries
    NEntries=len(__lws.getHistory().getAlgorithmHistories())    
    #find the last BinMD operation as we can get binning parameters from here
    cntrBinMD=0
    binMDIndicies=[]
    for i in NEntries-np.arange(NEntries)-1:
        entry=__lws.getHistory().getAlgorithmHistories()[i].name()
        if entry=='BinMD':
            cntrBinMD+=1
            binMDIndicies.append(i)
            #case we found the BinMD case - exit loop
            #break
            
    #check if more than one BinMD found in workspace history
    if cntrBinMD == 1:
        #case we just had one BinMD
        indx=0
    elif cntrBinMD == 0:
        print "No BinMD history found - returning"
        return
    else:
        #case to find more recent BinMD with AlignedDim* content
        #reverse list to check from most recent BinMD to oldest
        binMDIndicies.reverse() #reverse done in place
        indx=-1
        for tstindx in binMDIndicies:
            #check if there is content in AlignedDim0
            if __lws.getHistory().getAlgorithmHistories()[tstindx].getProperties()[2].value() != '':
                #case we have something
                indx=tstindx
                break
        if indx == -1:
            print "Did not find a BinMD case to extract info from!"
            return
            
    binMDIndx=indx
    NTags=len(__lws.getHistory().getAlgorithmHistories()[binMDIndx].getProperties())
    ad0str=''
    ad1str=''
    ad2str=''
    ad3str=''
    cntr=0
    for j in range(NTags):
        name=str(__lws.getHistory().getAlgorithmHistories()[binMDIndx].getProperties()[j].name())
        value=str(__lws.getHistory().getAlgorithmHistories()[binMDIndx].getProperties()[j].value())
        #print " name:  ",name
        #print " value: ",value
        #value=value.split(',')
        if name=='AlignedDim0':
            ad0str=value
            cntr+=1
        if name=='AlignedDim1':
            ad1str=value
            cntr+=1
        if name=='AlignedDim2':
            ad2str=value
            cntr+=1
        if name=='AlignedDim3':
            ad3str=value
            cntr+=1
    if cntr != 4:
        print "** Warning - Did not find 4 dimensions"
    
    #Now parse history strings for name, min, max, and Nbins
    adlst=[ad0str,ad1str,ad2str,ad3str]
    adlstparse=[]
    cntr=0
    for aditem in adlst:\
    
        if cntr == 0:
            minv=__lws.getXDimension().getMinimum()
            maxv=__lws.getXDimension().getMaximum()
            nbins=__lws.getXDimension().getNBins()
        if cntr == 1:
            minv=__lws.getYDimension().getMinimum()
            maxv=__lws.getYDimension().getMaximum()
            nbins=__lws.getYDimension().getNBins()
        if cntr == 2:
            minv=__lws.getZDimension().getMinimum()
            maxv=__lws.getZDimension().getMaximum()
            nbins=__lws.getZDimension().getNBins()
        if cntr == 3:
            minv=__lws.getTDimension().getMinimum()
            maxv=__lws.getTDimension().getMaximum()
            nbins=__lws.getTDimension().getNBins()
        cntr+=1
        #extract name, min, max, and nbins from each string
        try:
            #case we have HKL name
            indx0=aditem.index('[')
            indx1=aditem.index(']')
            name=aditem[indx0:indx1+1]
            shrtstr=aditem[indx1+2:]
            shrtstr=shrtstr.split(',')
            adlstparse.append([name+config.XYZUnits,shrtstr[0],shrtstr[1],shrtstr[2]])
            #FIXME
            #Note - attempted to utilize user selected region values from Slice Viewer here, 
            #however the values in the file do not seem to correspond to the values 
            #on the screen from SliceViewer.  So for now, just showing full range
            #adlstparse.append([name+config.XYZUnits,str(minv),str(maxv),str(nbins)])
        except:
            #case we have DeltaE name
            aditem=aditem.strip('DeltaE,')
            shrtstr=aditem.split(',')
            adlstparse.append(['E (meV)',shrtstr[0],shrtstr[1],shrtstr[2]])
            #adlstparse.append(['E (meV)',str(minv),str(maxv),str(nbins)])
    print adlstparse
    return adlstparse
        
def fill1DCutGUIParms(self,params):
    
    #fill the comboBoxes

    print params[0][0]
    print params[1][0]
    print params[2][0]
    print params[3][0]

    self.ui.comboBoxSCCutX.setItemText(0,params[0][0])
    self.ui.comboBoxSCCutX.setItemText(1,params[1][0])
    self.ui.comboBoxSCCutX.setItemText(2,params[2][0])
    self.ui.comboBoxSCCutX.setItemText(3,params[3][0])
    self.ui.comboBoxSCCutX.setCurrentIndex(1) #use Index=1 here to make plot axes correspond to those from SliceViewer
 
    self.ui.comboBoxSCCutY.setItemText(0,params[0][0])
    self.ui.comboBoxSCCutY.setItemText(1,params[1][0])
    self.ui.comboBoxSCCutY.setItemText(2,params[2][0])
    self.ui.comboBoxSCCutY.setItemText(3,params[3][0])
    self.ui.comboBoxSCCutY.setCurrentIndex(0)#and use Index=0 here to make plot axes correspond to those from SliceViewer

    self.ui.comboBoxSCCutZ.setItemText(0,params[0][0])
    self.ui.comboBoxSCCutZ.setItemText(1,params[1][0])
    self.ui.comboBoxSCCutZ.setItemText(2,params[2][0])
    self.ui.comboBoxSCCutZ.setItemText(3,params[3][0])
    self.ui.comboBoxSCCutZ.setCurrentIndex(2)

    self.ui.comboBoxSCCutE.setItemText(0,params[0][0])
    self.ui.comboBoxSCCutE.setItemText(1,params[1][0])
    self.ui.comboBoxSCCutE.setItemText(2,params[2][0])
    self.ui.comboBoxSCCutE.setItemText(3,params[3][0])
    self.ui.comboBoxSCCutE.setCurrentIndex(3)
    
    #Update Line Edit controls - limit number of significant digits 
    sigdig=3 #later this can be made a config.py parameter if desired
    self.ui.lineEditSCCutXFrom.setText(str(round(float(params[0][1]),sigdig)))
    self.ui.lineEditSCCutXTo.setText(str(round(float(params[0][2]),sigdig)))
    self.ui.lineEditSCCutYFrom.setText(str(round(float(params[1][1]),sigdig)))
    self.ui.lineEditSCCutYTo.setText(str(round(float(params[1][2]),sigdig)))
    self.ui.lineEditSCCutZFrom.setText(str(round(float(params[2][1]),sigdig)))
    self.ui.lineEditSCCutZTo.setText(str(round(float(params[2][2]),sigdig)))
    self.ui.lineEditSCCutEFrom.setText(str(round(float(params[3][1]),sigdig)))
    self.ui.lineEditSCCutETo.setText(str(round(float(params[3][2]),sigdig)))
    #currently not implementing intensity
    #self.ui.lineEditSCCutIntensityFrom.setText()
    #self.ui.lineEditSCCutIntensityTo.setText()
    
    #Update local dictionary used to keep track of things for the combo boxes and lineEdit controls
    #Define Slice Single Crystal Cut Tab dictionary used for creating data to view
    ViewSCCDict={}

    ViewSCCDict.setdefault('u1',{})['index']='0'
    ViewSCCDict.setdefault('u1',{})['label']=params[0][0]
    ViewSCCDict.setdefault('u1',{})['from']=''
    ViewSCCDict.setdefault('u1',{})['to']=''
    ViewSCCDict.setdefault('u1',{})['Intensity']=''
    
    ViewSCCDict.setdefault('u2',{})['index']='1'
    ViewSCCDict.setdefault('u2',{})['label']=params[1][0]
    ViewSCCDict.setdefault('u2',{})['from']=''
    ViewSCCDict.setdefault('u2',{})['to']=''
    ViewSCCDict.setdefault('u2',{})['Intensity']=''
    
    ViewSCCDict.setdefault('u3',{})['index']='2'
    ViewSCCDict.setdefault('u3',{})['label']=params[2][0]
    ViewSCCDict.setdefault('u3',{})['from']=''
    ViewSCCDict.setdefault('u3',{})['to']=''
    ViewSCCDict.setdefault('u3',{})['Intensity']=''
    
    ViewSCCDict.setdefault('E',{})['index']='3'
    ViewSCCDict.setdefault('E',{})['label']=params[3][0]
    ViewSCCDict.setdefault('E',{})['from']=''
    ViewSCCDict.setdefault('E',{})['to']=''
    ViewSCCDict.setdefault('E',{})['Intensity']=''
    #make dictionary available to MSlice
    self.ui.ViewSCCDict=ViewSCCDict
    
    print "*** Workspaces: "
    print mtd.getObjectNames()
   
    pass
    

def write1DCompanionFile(histDict,filename):
    
    #function to take a history dictionary and produce an XML file from it
    #that is compatible with the SC parameters xml file format

    Uproj=histDict['ConvertToMD']['Uproj'].split(',')
    Vproj=histDict['ConvertToMD']['Vproj'].split(',')
    Wproj=histDict['ConvertToMD']['Wproj'].split(',')   

    u=histDict['SetUB']['u'].split(',')
    v=histDict['SetUB']['v'].split(',')

    u1=histDict['ConvertToMD']['Uproj'].split(',')
    u2=histDict['ConvertToMD']['Vproj'].split(',')
    u3=histDict['ConvertToMD']['Wproj'].split(',')

    minVals=histDict['ConvertToMD']['MinValues'].split(',')
    maxVals=histDict['ConvertToMD']['MaxValues'].split(',')

    #pack variables into a dictionary
    params_dict_root={'root':{
                        'a':histDict['SetUB']['a'],
                        'b':histDict['SetUB']['b'],
                        'c':histDict['SetUB']['c'],
                        'alpha':histDict['SetUB']['alpha'],                   
                        'beta':histDict['SetUB']['beta'],                                          
                        'gamma':histDict['SetUB']['gamma'],                
                        'ux':u[0],
                        'uy':u[1],                        
                        'uz':u[2],            
                        'vx':v[0],
                        'vy':v[1],                        
                        'vz':v[2],     
                        'Psi':'',                        
                        'MN':'',                        
                        'u1a':u1[0],                    
                        'u1b':u1[1],                        
                        'u1c':u1[2],                        
                        'u1Label':'',
                        'u2a':u2[0],                       
                        'u2b':u2[1],                        
                        'u2c':u2[2],                        
                        'u2Label':'',                        
                        'u3a':u3[0],
                        'u3b':u3[1],                        
                        'u3c':u3[2],                        
                        'u3Label':'',
                        'minValX':minVals[0],
                        'minValY':minVals[1],
                        'minValZ':minVals[2],
                        'minValT':minVals[3],        
                        'maxValX':maxVals[0],
                        'maxValY':maxVals[1],
                        'maxValZ':maxVals[2],
                        'maxValT':maxVals[3],   
                        'XName':histDict['Names']['XName'],
                        'YName':histDict['Names']['YName'],
                        'ZName':histDict['Names']['ZName'],
                        'TName':histDict['Names']['TName']
                    }}

    dicttoxmlfile(params_dict_root, filename)
    
    
    








































    
