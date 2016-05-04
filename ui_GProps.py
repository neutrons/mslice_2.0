# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_GProps.ui'
#
# Created: Wed Mar 04 10:37:50 2015
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_GoniometerProperties(object):
    def setupUi(self, GoniometerProperties):
        GoniometerProperties.setObjectName(_fromUtf8("GoniometerProperties"))
        GoniometerProperties.resize(274, 192)
        self.centralwidget = QtGui.QWidget(GoniometerProperties)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.lineEditGPA0 = QtGui.QLineEdit(self.centralwidget)
        self.lineEditGPA0.setGeometry(QtCore.QRect(110, 40, 113, 20))
        self.lineEditGPA0.setObjectName(_fromUtf8("lineEditGPA0"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(50, 40, 46, 13))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 10, 241, 20))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(50, 60, 46, 13))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.lineEditGPA1 = QtGui.QLineEdit(self.centralwidget)
        self.lineEditGPA1.setGeometry(QtCore.QRect(110, 60, 113, 20))
        self.lineEditGPA1.setObjectName(_fromUtf8("lineEditGPA1"))
        self.pushButtonGPReset = QtGui.QPushButton(self.centralwidget)
        self.pushButtonGPReset.setGeometry(QtCore.QRect(110, 90, 111, 23))
        self.pushButtonGPReset.setObjectName(_fromUtf8("pushButtonGPReset"))
        self.pushButtonGPDone = QtGui.QPushButton(self.centralwidget)
        self.pushButtonGPDone.setGeometry(QtCore.QRect(110, 120, 111, 23))
        self.pushButtonGPDone.setObjectName(_fromUtf8("pushButtonGPDone"))
        GoniometerProperties.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(GoniometerProperties)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 274, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        GoniometerProperties.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(GoniometerProperties)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        GoniometerProperties.setStatusBar(self.statusbar)

        self.retranslateUi(GoniometerProperties)
        QtCore.QMetaObject.connectSlotsByName(GoniometerProperties)

    def retranslateUi(self, GoniometerProperties):
        GoniometerProperties.setWindowTitle(QtGui.QApplication.translate("GoniometerProperties", "Goniometer Properties", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditGPA0.setText(QtGui.QApplication.translate("GoniometerProperties", "0,1,0,1", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("GoniometerProperties", "Axis0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("GoniometerProperties", "Set x,y,z, 1/-1 (1 for ccw, -1 for cw rotation)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("GoniometerProperties", "Axis1", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditGPA1.setText(QtGui.QApplication.translate("GoniometerProperties", "0,1,0,1", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonGPReset.setText(QtGui.QApplication.translate("GoniometerProperties", "Reset", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonGPDone.setText(QtGui.QApplication.translate("GoniometerProperties", "Done", None, QtGui.QApplication.UnicodeUTF8))

