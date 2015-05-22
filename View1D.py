

#import utility modules
import sys

#import PyQt modules
from PyQt4 import QtGui, QtCore, Qt

#include this try/except block to remap QString needed when using IPython
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from matplotlib import rc
from utils_dict_xml import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar

import matplotlib.gridspec as gridspec

import sys, os
#import GUI components generated from Qt Designer .ui file
from ui_View1D import *

#import Mantid computatinal modules - here to save 
sys.path.append(os.environ['MANTIDPATH'])
from mantid.simpleapi import * 

class View1D(QtGui.QMainWindow):
    
    #initialize app
    def __init__(self, parent=None):
        #setup main window
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_View1DMainWindow() #defined in ui_View1D.py
        self.ui.setupUi(self)
        self.parent=parent 
    
        #add action exit for File --> Exit menu option
        self.connect(self.ui.actionExit, QtCore.SIGNAL('triggered()'), self.confirmExit)
        #add signal/slot connection for pushbutton exit request
        self.connect(self.ui.pushButtonExit, QtCore.SIGNAL('clicked()'), self.confirmExit)
        
        #add signal/slot for update
        self.connect(self.ui.pushButtonUpdatePlot, QtCore.SIGNAL('clicked()'), self.plot1Dplot)
        
        #add signal/slot for SaveASCII
        self.connect(self.ui.pushButtonSaveASCII, QtCore.SIGNAL('clicked()'), self.SaveASCII)        
        
        #set default plot color to blue (on index 1)
        self.ui.comboBoxPlotColor.setCurrentIndex(1)
                
        #place workspace and companion file into the local object
        self.ui.ws=self.parent.ui.View1DWS
        self.ui.compFilename=self.parent.ui.View1DcompFilename
        
        
        #initizliaze matplotlib components
        #Place Matplotlib figure within the GUI frame
        #create drawing canvas
        # a figure instance to plot on
        
        matplotlib.rc_context({'toolbar':True})
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        
        #add Navigation Toolbar
        self.navigation_toolbar = NavigationToolbar(self.canvas, self)
        
        layout=QtGui.QVBoxLayout(self.ui.frameView1D)
        layout.addWidget(self.canvas)
        layout.addWidget(self.navigation_toolbar, 0)
        self.layout=layout
        
        #initialize plot colors
        self.ui.sigColor='blue'
        self.ui.ebarColor='red'
        
        #initialize font
        #rc() calls intended to set globals
        #rc('text', usetex=True) #needed to support things like text underlining also need from matplotlib import rc
        rc('font',size='14')
        rc('font',monospace='Courier')
        self.ui.font='Courier'
        self.ui.fontsize='14'
        
        Nfonts=self.ui.fontComboBox.count()
        for fn in range(Nfonts):
            if 'Courier' in self.ui.fontComboBox.itemText(fn):
                #case we found a Courier font
                self.ui.font = self.ui.fontComboBox.itemText(fn)
                self.ui.fontIndex=fn
                self.ui.fontComboBox.setCurrentIndex(fn)
                print "self.ui.fontComboBox.setCurrentIndex(fn): ",self.ui.fontComboBox.setCurrentIndex(fn)
                print "self.ui.fontIndex: ",self.ui.fontIndex
                rc('font',family=self.ui.font)
                print "Initialized font: ",self.ui.font
                break
                
        #initalize the plot
        self.plot1Dplot()
        
    def confirmExit(self):
        reply = QtGui.QMessageBox.question(self, 'Message',
        "Are you sure to quit?", QtGui.QMessageBox.Yes | 
        QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        
        if reply == QtGui.QMessageBox.Yes:
        #close application
            self.close()
        else:
        #do nothing and return
            pass     
            
            
    def plot1Dplot(self):
        
        #extract GUI params
        
        #check if signal and error bar settings
        sigSel=self.ui.radioButtonSignal.isChecked() #radio button for signal select
        ebarSel=self.ui.radioButtonEBar.isChecked()  #radio button for error bar radio button select
        ebarSet=self.ui.checkBoxShowEBar.isChecked() #checkbox for enable/disable error bar display
        
        font = str(self.ui.fontComboBox.currentText())
        if self.ui.checkBoxBoldFont.isChecked():
            fontWeight='bold'
        else:
            fontWeight='normal'
        
        fontSizeText=str(self.ui.comboBoxFontSize.currentText())
        
        fontdict = {
                    'family' : font,
                    'weight' : fontWeight,
                    'size'   : fontSizeText
                    }
        
        matplotlib.rcdefaults() #restore default settings
        #rc('text', usetex=True) #needed to support things like text underlining also need from matplotlib import rc
        rc('font', **fontdict)
        #rc('text', usetex=True)  #note - was unable to change fonts once this command issued
        
        #check status of check boxes
        #chech show status for showing signal
        if sigSel:
            self.ui.sigColor=self.ui.comboBoxPlotColor.currentText()
        
        #check show status for showing error bars
        if ebarSel:
            self.ui.ebarColor=self.ui.comboBoxPlotColor.currentText()
        
        
        #retrieve info from self object
        ws = self.ui.ws
        compFilename = self.ui.compFilename
        
        fig=self.figure
        
        #\boldmath here enables greek characters to be bolder than the wispy "normal" font here
        #matplotlib.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
        matplotlib.rcParams['text.latex.preamble']=[r'\boldmath']
        
        NumEventsArray=ws.getNumEventsArray()    
        signal=ws.getSignalArray()/NumEventsArray
        error2=ws.getErrorSquaredArray()
        ebar=2.0*np.sqrt(error2)/NumEventsArray #define error to span two sigma
        #ebar calculation should be same as: DoSCPlotMSlice() in MPLSCCutHelpers.py
        
        #get dimension extents of these data
        """
        Following code example from MPL1DCutMain.py SavePlotWS():
        __MDH1Dcompact=CreateMDHistoWorkspace(signal,error,Dimensionality=Ndims,Extents=extents,\
                        NumberOfEvents=numEvents,NumberOfBins=numBins,Names=names,Units=units)    
        """
        
        numBins=float(ws.getDimension(0).getNBins())
        xaxis=(float(ws.getDimension(0).getMaximum()) - float(ws.getDimension(0).getMinimum()))*np.arange(0,1,1.0/numBins) +\
                float(ws.getDimension(0).getMinimum())
    
        """
        #define a font dictionary to explicity control specific font parameters
        fontdict=   {'family'   : font,
                    'color'    : 'black',
                    'weight'   : 'bold',
                    'size'     : str(int(fontSizeText)+2),
                    'fontstyle': 'normal',
                    'variant'  : 'normal'
                    }
        """
    
        #create the plot
        ax=plt.subplot(211)
        
        #plot data using errorbars
        sigColor=str(self.ui.sigColor)
        ebarColor=str(self.ui.ebarColor)
        print "sigColor: ",sigColor,'  ebarColor: ',ebarColor
        
        if self.ui.checkBoxShowPlotMarker.isChecked():
            marker='+'
        else:
            marker=','

        if ebarSet:
            #plot with ebar
            plt.cla()
            capsize=int(self.ui.comboBoxEBarThick.currentIndex())+1
            elinewidth=capsize #for now, just lock the sizes of these two
            plt.errorbar(xaxis,signal,color=sigColor,yerr=ebar,xerr=False,ecolor=ebarColor,fmt='',label='_nolegend_',marker=marker,linestyle='-',capsize=capsize,elinewidth=elinewidth)    
        else:
            #plot just signal
            plt.cla()
        
        #seems to be a bug in errorbar that requires overplotting
        lw=int(self.ui.comboBoxLineThick.currentIndex())+1
        plt.plot(xaxis,signal,color=sigColor,marker=marker,linestyle='-',linewidth=lw)
        ax.grid(True)  
        
        #put x and y labels on the plot
        xlabelStr=ws.getXDimension().getName()+' '+ws.getXDimension().getUnits()
        xlabelStr=xlabelStr.replace('^-1','$^\mathbf{(-1)}$') #put ^-1 as superscript (-1)
        ax.set_xlabel(xlabelStr)
        ax.set_ylabel("Signal")
        
        titleStr="1D Plot: "+ws.name()
        #titleStr=titleStr.replace('_','\_') #need to embed as \_ to supress subscripting when using rc('text', usetex=True)
        ax.set_title(titleStr,fontdict=fontdict)
        
        """
        #these two commands redundant given the subsequent plt.gcf().subplots_adjust() commands at the bottom of plot1Dplot()?
        plt.gcf().subplots_adjust(bottom=0.2)
        plt.gcf().subplots_adjust(left=0.15)
        """
    
        #place x/y grid on the plot
        ax.grid(True)

        ax2=plt.subplot(212)
        ax2.axis('off')
        
        #axes fraction 0,0 is lower left of axes and 1,1 is upper right
        #x offset between text on the same row
        xoff0 = 0
        xoff1 = 0.5
        
        yoff = 0.96 #global offset in y axis direction
        
        #dx0 and dx1 
        dx0 = 0   #dx0 gives start position in the row for the first row text block
        dx1 = 0 #dx1 gives start position in the row for the second row text block
        
        #dy0 and dy1
        dy0 = 0 #dy0 starts at zero
        dy1 = -0.05 #dy1 times row number gives y offset between rows
        
        
        #translate xml file to dictionary
        dct=xmlfiletodict(compFilename)
        
        #place two rows of Unit Cell Lattice Parameters
        #plt.annotate(r'\underline{Unit Cell Lattice Parameters}',(dx0+xoff0,dy0*0),(dx1+xoff0,dy1*0+yoff),textcoords='axes fraction')
        plt.annotate('Unit Cell Lattice Parameters',(dx0+xoff0,dy0*0),(dx1+xoff0,dy1*0+yoff),textcoords='axes fraction',weight='bold')
        plt.annotate('a(A):'+dct['root']['a']+'   '+'b(A):'+dct['root']['b']+'   '+'c(A):'+\
                        dct['root']['c'],(dx0+xoff0,dy0*0),(dx1+xoff0,dy1*1+yoff),textcoords='axes fraction')
        plt.annotate(r'$\alpha$(*):'+dct['root']['alpha']+'  '+r'$\beta$(*):'+dct['root']['beta']+'  '+r'$\gamma$(*):'+dct['root']['gamma'],\
                        (dx0+xoff0,dy0*0),(dx1+xoff0,dy1*2+yoff),textcoords='axes fraction')
    
        #place two rows of Crystal Orientation parameters
        #plt.annotate(r'\underline{Crystal Orientation}',(dx0+xoff1,dy0*0),(dx1+xoff1,dy1*0+yoff),textcoords='axes fraction')
        plt.annotate('Crystal Orientation',(dx0+xoff1,dy0*0),(dx1+xoff1,dy1*0+yoff),textcoords='axes fraction',weight='bold')
        plt.annotate('ux:'+dct['root']['ux']+'  uy:'+dct['root']['uy']+'  uz:'+dct['root']['uz'],(dx0+xoff1,dy0*0),(dx1+xoff1,dy1*1+yoff),textcoords='axes fraction')
        plt.annotate('vx:'+dct['root']['vx']+'  vy:'+dct['root']['vy']+'  vz:'+dct['root']['vz'],(dx0+xoff1,dy0*0),(dx1+xoff1,dy1*2+yoff),textcoords='axes fraction')
            
        #place viewing axes also skipping a row
        #plt.annotate(r'\underline{Viewing Axes}',(dx0+xoff0,dy0*0),(dx1+xoff0,dy1*4+yoff),textcoords='axes fraction')
        plt.annotate('Viewing Axes',(dx0+xoff0,dy0*0),(dx1+xoff0,dy1*4+yoff),textcoords='axes fraction',weight='bold')
        plt.annotate('u1:'+dct['root']['u1a']+'  '+dct['root']['u1b']+'  '+dct['root']['u1c'],(dx0+xoff0,dy0*0),(dx1+xoff0,dy1*5+yoff),textcoords='axes fraction')    
        plt.annotate('u2:'+dct['root']['u2a']+'  '+dct['root']['u2b']+'  '+dct['root']['u2c'],(dx0+xoff0,dy0*0),(dx1+xoff0,dy1*6+yoff),textcoords='axes fraction')    
        plt.annotate('u3:'+dct['root']['u3a']+'  '+dct['root']['u3b']+'  '+dct['root']['u3c'],(dx0+xoff0,dy0*0),(dx1+xoff0,dy1*7+yoff),textcoords='axes fraction')    
    
        #place HKLE info
        plt.annotate('HKLE Info',(dx0+xoff1,dy0*0),(dx1+xoff1,dy1*4+yoff),textcoords='axes fraction',weight='bold')    
        mn=str(round(float(dct['root']['minValX']),3))
        mx=str(round(float(dct['root']['maxValX']),3))
        plt.annotate(dct['root']['XName']+'  from: '+mn+' to: '+mx,(dx0+xoff1,dy0*0),(dx1+xoff1,dy1*5+yoff),textcoords='axes fraction')    
        mn=str(round(float(dct['root']['minValY']),3))
        mx=str(round(float(dct['root']['maxValY']),3))
        plt.annotate(dct['root']['YName']+'  thick: '+mn+' to: '+mx,(dx0+xoff1,dy0*0),(dx1+xoff1,dy1*6+yoff),textcoords='axes fraction')    
        mn=str(round(float(dct['root']['minValZ']),3))
        mx=str(round(float(dct['root']['maxValZ']),3))
        plt.annotate(dct['root']['ZName']+'  thick: '+mn+' to: '+mx,(dx0+xoff1,dy0*0),(dx1+xoff1,dy1*7+yoff),textcoords='axes fraction')    
        mn=str(round(float(dct['root']['minValT']),3))
        mx=str(round(float(dct['root']['maxValT']),3))
        plt.annotate(dct['root']['TName']+'  thick: '+mn+' to: '+mx,(dx0+xoff1,dy0*0),(dx1+xoff1,dy1*8+yoff),textcoords='axes fraction')    
        
        
        #format the drawing area
        plt.gcf().subplots_adjust(bottom=-0.25)
        plt.gcf().subplots_adjust(left=0.12)
        plt.gcf().subplots_adjust(right=0.95)
        
        #note that view1D.show() below does the job of rendering the images
    
    def SaveASCII(self):
        print "ws: ",self.ui.ws
        print "ws.name(): ",self.ui.ws.name()
        print "ws.id(): ",self.ui.ws.id()
        
        #note in this case that the input workspace is an MDHisto workspace
        #thus we need to convert it to a matrix workspace to use the SaveAscii Mantid algorithm
        __wsHisto = ConvertMDHistoToMatrixWorkspace(self.ui.ws)
        fname=__wsHisto.getTitle()
        filter='.txt'
        wsname=fname+filter
        filter="TXT (*.txt);;All files (*.*)"
        if self.parent.ui.rememberDataPath=='':
            curdir=os.curdir
        else:
            curdir=self.parent.ui.rememberDataPath
        fname=_fromUtf8(curdir+'/'+fname)
        fsavename = str(QtGui.QFileDialog.getSaveFileName(self, 'Save ASCII Data', fname,filter))
        if fsavename!='':
            #note that here local SaveASCII() function calls the Mantid SaveAscii() function (which could potentially be confusing...)
            SaveAscii(__wsHisto,fsavename,Separator='CSV') #Mantid routine to save a workspace as ascii data

    
if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    print "Launching View1D() "
    view1D = View1D()
    print "View1D() Launched"
    view1D.show()

    exit_code=app.exec_()
    #print "exit code: ",exit_code
    sys.exit(exit_code)
    
