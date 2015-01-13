#!/usr/bin/python

"""
LegendManager.py

Example Application to enable a user to edit content and display of matplotlib
plot labels.  The application creates a matplotlib.pyplot figure with three 
plots, and each plot has a label.  A basic PyQt4 GUI is presented which enables 
the user to select each label for display or not along with the ability to edit
the label text via the table in the GUI.

"""

#import utility modules
import sys
from MSliceHelpers import *  #needed to add checkboxes to status column in table
#import matplotlib to be compatible with PyQt4
import matplotlib
if matplotlib.get_backend() != 'QT4Agg':
    matplotlib.use('QT4Agg')
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt

#import PyQt modules
from PyQt4 import QtGui, QtCore, Qt

#include this try/except block to remap QString needed when using IPython
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

#import GUI components generated from Qt Designer .ui file
from ui_LegendManager import *

class LegendManager(QtGui.QMainWindow):
    
    #initialize app
    def __init__(self, parent=None):
        
        #setup main window
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle("App Template Main")
        self.ui = Ui_MainWindowLegend() #defined in ui_AppTemplate.py
        self.ui.setupUi(self)
        self.parent=parent
        self.connect(self.ui.pushButtonSelectAll, QtCore.SIGNAL('clicked()'), self.SelectAll)
        self.connect(self.ui.pushButtonClearAll, QtCore.SIGNAL('clicked()'), self.ClearAll)
        self.connect(self.ui.pushButtonUpdatePlot, QtCore.SIGNAL('clicked()'), self.UpdatePlot)
        self.connect(self.ui.pushButtonRefresh, QtCore.SIGNAL('clicked()'), self.Refresh)
    
        #add action exit for File --> Exit menu option
        self.connect(self.ui.pushButtonExit, QtCore.SIGNAL('clicked()'), self.Exit)
        
        ax=self.parent.ui.ax

        #get handles and labels for current plots
        handles, LabLst = ax.get_legend_handles_labels()
        
        Nlabs=len(LabLst)
        #inform user if no legend labels to manage
        if Nlabs ==0:
            #case where there are no labels

            dialog=QtGui.QMessageBox(self)
            dialog.setText("There are no plot legends to manage - returning")
            dialog.exec_() 
            self.close()
            #sys.exit()
        
        #Initialize table
        HzHeaders=['Label Text','Label Color','Status']
        self.ui.tableWidgetLegend.setHorizontalHeaderLabels(HzHeaders)
        w=self.ui.tableWidgetLegend.geometry().size().width()
        #w=330
        self.ui.tableWidgetLegend.setColumnWidth(0,0.5*w) #Label text
        self.ui.tableWidgetLegend.setColumnWidth(1,0.25*w) #Label color
        self.ui.tableWidgetLegend.setColumnWidth(2,0.25*w) #Select Status
        self.ui.tableWidgetLegend.resizeRowsToContents()
        self.ui.tableWidgetLegend.setRowCount(Nlabs)

        #Now fill the rows
        Nrows=self.ui.tableWidgetLegend.rowCount()
        for i in range(Nrows):
            #add the labels
            item=QtGui.QTableWidgetItem()
            #item.setData(QtCore.Qt.DisplayRole,LabLst[i]) 
            item.setText(_fromUtf8(LabLst[i])) 
            self.ui.tableWidgetLegend.setItem(i,0,item)
            #add label colors
            item=QtGui.QTableWidgetItem()
            item.setText(_fromUtf8(handles[i].get_color())) 
            item.setTextColor(QtGui.QColor(handles[i].get_color()))
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.ui.tableWidgetLegend.setItem(i,1,item)            
            #add the select checkboxes
            if handles[i].get_visible():
                addCheckboxToWSTCell(self.ui.tableWidgetLegend,i,2,True)
            else:
                addCheckboxToWSTCell(self.ui.tableWidgetLegend,i,2,False)
            
        self.ui.tableWidgetLegend.verticalHeader().setVisible(False)
        
    def SelectAll(self):
        #Select all labels to display
        table=self.ui.tableWidgetLegend
        Nrows=table.rowCount()
        for i in range(Nrows):
            addCheckboxToWSTCell(table,i,2,True)
                
        
    def ClearAll(self):
        #Select no labels to display
        table=self.ui.tableWidgetLegend
        Nrows=table.rowCount()
        for i in range(Nrows):
            addCheckboxToWSTCell(table,i,2,False)
        
    def UpdatePlot(self):
        #Check the table for new label text and for which labels to show
        #Then put this new legend on the plot
        table=self.ui.tableWidgetLegend
        ax=self.parent.ui.ax
        fig=self.parent.figure
        plt.figure(fig.number)
        #code for checking which labels are selected to show
        Nrows=table.rowCount()
        selrow=[]
        handles, LabLst = ax.get_legend_handles_labels()
        for row in range(Nrows):
            #get checkbox status            
            cw=table.cellWidget(row,2) 
            #get new label text
            newLab=str(table.item(row,0).text())
            handles[row].set_label(newLab)
            
            cbstat=cw.isChecked()
            if cbstat == True:
                #case to identify selected row number
                selrow.append(row)
                handles[row].set_visible(True)
            else:
                handles[row].set_visible(False)
        
        for k in range(2):
            #show selected labels
            
            if k == 0:
                #Powder Cut figure
                fig=self.parent.figure
                plt.figure(fig.number)
            else:
                fig=self.parent.shadowFigure
                plt.figure(fig.number)
            
            Nshow=len(selrow)
            if Nshow > 0:
                #show new legend if there's something to show
                handles, LabLst = ax.get_legend_handles_labels()
                newHand=[]
                newLab=[]
    
                for i in range(Nshow):
                    handles[selrow[i]].set_label(LabLst[selrow[i]])
                    newHand.append(handles[selrow[i]])
                    newLab.append(LabLst[selrow[i]])
                    #plt.legend(newHand,newLab)
                    plt.legend(newHand,newLab)
            else:
                #take the legend off of the plot
                #plt.legend([],[])
                print "Clear Legend"
                plt.legend([],[],frameon=False)
                #plt.legend_=None
                
        self.parent.canvas.draw()
        self.parent.canvas.setVisible(True)
        
    def Refresh(self):
        table=self.ui.tableWidgetLegend
        ax=self.parent.ui.ax
        #get handles and labels for current plots
        handles, LabLst = ax.get_legend_handles_labels()
        Nlabs=len(LabLst)
        print "LabLst: ",LabLst
        
        #just delete all of the old rows out of the table
        Nrows=table.rowCount()
        for i in range(Nrows):
            table.removeRow(0)
        
        table.setRowCount(Nlabs)
        
        #Now fill the rows
        for i in range(Nlabs):
            #add the labels
            item=QtGui.QTableWidgetItem()
            item.setData(QtCore.Qt.DisplayRole,LabLst[i]) 
            table.setItem(i,0,item)
            #add label colors
            item=QtGui.QTableWidgetItem()
            item.setText(_fromUtf8(handles[i].get_color())) 
            item.setTextColor(QtGui.QColor(handles[i].get_color()))
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.ui.tableWidgetLegend.setItem(i,1,item)  
            #add the select checkboxes
            if handles[i].get_visible():
                addCheckboxToWSTCell(self.ui.tableWidgetLegend,i,2,True)
            else:
                addCheckboxToWSTCell(self.ui.tableWidgetLegend,i,2,False)
        
    def Exit(self):
        #Exit application
        self.close()
  
if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = LegendManager()
    myapp.show()

    exit_code=app.exec_()
    #print "exit code: ",exit_code
    sys.exit(exit_code)