# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_LegendManager.ui'
#
# Created: Mon Jan 12 11:02:17 2015
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindowLegend(object):
    def setupUi(self, MainWindowLegend):
        MainWindowLegend.setObjectName(_fromUtf8("MainWindowLegend"))
        MainWindowLegend.resize(473, 233)
        self.centralwidget = QtGui.QWidget(MainWindowLegend)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tableWidgetLegend = QtGui.QTableWidget(self.centralwidget)
        self.tableWidgetLegend.setMinimumSize(QtCore.QSize(331, 161))
        self.tableWidgetLegend.setRowCount(4)
        self.tableWidgetLegend.setColumnCount(3)
        self.tableWidgetLegend.setObjectName(_fromUtf8("tableWidgetLegend"))
        self.tableWidgetLegend.setColumnCount(3)
        self.tableWidgetLegend.setRowCount(4)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetLegend.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetLegend.setItem(0, 1, item)
        self.horizontalLayout.addWidget(self.tableWidgetLegend)
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setMinimumSize(QtCore.QSize(101, 181))
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.pushButtonExit = QtGui.QPushButton(self.groupBox)
        self.pushButtonExit.setGeometry(QtCore.QRect(10, 150, 81, 23))
        self.pushButtonExit.setObjectName(_fromUtf8("pushButtonExit"))
        self.pushButtonSelectAll = QtGui.QPushButton(self.groupBox)
        self.pushButtonSelectAll.setGeometry(QtCore.QRect(10, 10, 81, 23))
        self.pushButtonSelectAll.setObjectName(_fromUtf8("pushButtonSelectAll"))
        self.pushButtonUpdatePlot = QtGui.QPushButton(self.groupBox)
        self.pushButtonUpdatePlot.setGeometry(QtCore.QRect(10, 70, 81, 23))
        self.pushButtonUpdatePlot.setObjectName(_fromUtf8("pushButtonUpdatePlot"))
        self.pushButtonRefresh = QtGui.QPushButton(self.groupBox)
        self.pushButtonRefresh.setGeometry(QtCore.QRect(10, 120, 81, 23))
        self.pushButtonRefresh.setObjectName(_fromUtf8("pushButtonRefresh"))
        self.pushButtonClearAll = QtGui.QPushButton(self.groupBox)
        self.pushButtonClearAll.setGeometry(QtCore.QRect(10, 40, 81, 23))
        self.pushButtonClearAll.setObjectName(_fromUtf8("pushButtonClearAll"))
        self.horizontalLayout.addWidget(self.groupBox)
        MainWindowLegend.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindowLegend)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 473, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindowLegend.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindowLegend)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindowLegend.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindowLegend)
        QtCore.QMetaObject.connectSlotsByName(MainWindowLegend)

    def retranslateUi(self, MainWindowLegend):
        MainWindowLegend.setWindowTitle(QtGui.QApplication.translate("MainWindowLegend", "Legend Manager", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidgetLegend.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("MainWindowLegend", "1", None, QtGui.QApplication.UnicodeUTF8))
        __sortingEnabled = self.tableWidgetLegend.isSortingEnabled()
        self.tableWidgetLegend.setSortingEnabled(False)
        self.tableWidgetLegend.setSortingEnabled(__sortingEnabled)
        self.pushButtonExit.setText(QtGui.QApplication.translate("MainWindowLegend", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonSelectAll.setText(QtGui.QApplication.translate("MainWindowLegend", "Select All", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonUpdatePlot.setText(QtGui.QApplication.translate("MainWindowLegend", "Update Plot", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonRefresh.setText(QtGui.QApplication.translate("MainWindowLegend", "Update Table", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonClearAll.setText(QtGui.QApplication.translate("MainWindowLegend", "Clear All", None, QtGui.QApplication.UnicodeUTF8))

