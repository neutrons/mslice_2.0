# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'WorkspaceComposer.ui'
#
# Created: Thu May 22 14:16:34 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_WorkspaceComposer(object):
    def setupUi(self, WorkspaceComposer):
        WorkspaceComposer.setObjectName(_fromUtf8("WorkspaceComposer"))
        WorkspaceComposer.resize(913, 497)
        self.centralwidget = QtGui.QWidget(WorkspaceComposer)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(690, 20, 211, 361))
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.line = QtGui.QFrame(self.groupBox)
        self.line.setGeometry(QtCore.QRect(10, 180, 191, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.groupBox_5 = QtGui.QGroupBox(self.groupBox)
        self.groupBox_5.setGeometry(QtCore.QRect(10, 190, 191, 161))
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.label = QtGui.QLabel(self.groupBox_5)
        self.label.setGeometry(QtCore.QRect(10, 20, 171, 20))
        self.label.setObjectName(_fromUtf8("label"))
        self.lineEditGroupName = QtGui.QLineEdit(self.groupBox_5)
        self.lineEditGroupName.setGeometry(QtCore.QRect(10, 40, 171, 20))
        self.lineEditGroupName.setObjectName(_fromUtf8("lineEditGroupName"))
        self.pushButtonCreateWorkspace = QtGui.QPushButton(self.groupBox_5)
        self.pushButtonCreateWorkspace.setEnabled(False)
        self.pushButtonCreateWorkspace.setGeometry(QtCore.QRect(20, 130, 121, 23))
        self.pushButtonCreateWorkspace.setToolTip(_fromUtf8(""))
        self.pushButtonCreateWorkspace.setObjectName(_fromUtf8("pushButtonCreateWorkspace"))
        self.radioButtonSumWS = QtGui.QRadioButton(self.groupBox_5)
        self.radioButtonSumWS.setGeometry(QtCore.QRect(10, 80, 161, 20))
        self.radioButtonSumWS.setObjectName(_fromUtf8("radioButtonSumWS"))
        self.radioButtonGroupWS = QtGui.QRadioButton(self.groupBox_5)
        self.radioButtonGroupWS.setGeometry(QtCore.QRect(10, 60, 161, 17))
        self.radioButtonGroupWS.setObjectName(_fromUtf8("radioButtonGroupWS"))
        self.radioButtonExecuteEqn = QtGui.QRadioButton(self.groupBox_5)
        self.radioButtonExecuteEqn.setGeometry(QtCore.QRect(10, 100, 171, 17))
        self.radioButtonExecuteEqn.setObjectName(_fromUtf8("radioButtonExecuteEqn"))
        self.groupBox_6 = QtGui.QGroupBox(self.groupBox)
        self.groupBox_6.setGeometry(QtCore.QRect(10, 10, 191, 161))
        self.groupBox_6.setObjectName(_fromUtf8("groupBox_6"))
        self.pushButtonUpdate = QtGui.QPushButton(self.groupBox_6)
        self.pushButtonUpdate.setGeometry(QtCore.QRect(20, 120, 111, 23))
        self.pushButtonUpdate.setObjectName(_fromUtf8("pushButtonUpdate"))
        self.radioButtonRemoveSelected = QtGui.QRadioButton(self.groupBox_6)
        self.radioButtonRemoveSelected.setGeometry(QtCore.QRect(10, 90, 151, 17))
        self.radioButtonRemoveSelected.setObjectName(_fromUtf8("radioButtonRemoveSelected"))
        self.radioButtonClearAll = QtGui.QRadioButton(self.groupBox_6)
        self.radioButtonClearAll.setGeometry(QtCore.QRect(10, 70, 151, 17))
        self.radioButtonClearAll.setObjectName(_fromUtf8("radioButtonClearAll"))
        self.radioButtonSelectAll = QtGui.QRadioButton(self.groupBox_6)
        self.radioButtonSelectAll.setGeometry(QtCore.QRect(10, 50, 151, 17))
        self.radioButtonSelectAll.setObjectName(_fromUtf8("radioButtonSelectAll"))
        self.radioButtonLoadData = QtGui.QRadioButton(self.groupBox_6)
        self.radioButtonLoadData.setGeometry(QtCore.QRect(10, 30, 161, 17))
        self.radioButtonLoadData.setChecked(True)
        self.radioButtonLoadData.setObjectName(_fromUtf8("radioButtonLoadData"))
        self.groupBox_2 = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 370, 661, 81))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.lineEditEquation = QtGui.QLineEdit(self.groupBox_2)
        self.lineEditEquation.setGeometry(QtCore.QRect(10, 50, 641, 20))
        self.lineEditEquation.setObjectName(_fromUtf8("lineEditEquation"))
        self.label_5 = QtGui.QLabel(self.groupBox_2)
        self.label_5.setGeometry(QtCore.QRect(10, 30, 641, 20))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.groupBox_4 = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_4.setGeometry(QtCore.QRect(10, 20, 661, 341))
        self.groupBox_4.setStyleSheet(_fromUtf8("border-color: rgb(0, 0, 0);\n"
""))
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.tableWidgetWGE = QtGui.QTableWidget(self.groupBox_4)
        self.tableWidgetWGE.setGeometry(QtCore.QRect(10, 20, 641, 300))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(200)
        sizePolicy.setHeightForWidth(self.tableWidgetWGE.sizePolicy().hasHeightForWidth())
        self.tableWidgetWGE.setSizePolicy(sizePolicy)
        self.tableWidgetWGE.setMaximumSize(QtCore.QSize(730, 300))
        self.tableWidgetWGE.setSizeIncrement(QtCore.QSize(5, 5))
        self.tableWidgetWGE.setLineWidth(3)
        self.tableWidgetWGE.setRowCount(15)
        self.tableWidgetWGE.setColumnCount(7)
        self.tableWidgetWGE.setObjectName(_fromUtf8("tableWidgetWGE"))
        item = QtGui.QTableWidgetItem()
        self.tableWidgetWGE.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetWGE.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetWGE.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetWGE.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetWGE.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetWGE.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetWGE.setHorizontalHeaderItem(6, item)
        self.tableWidgetWGE.horizontalHeader().setVisible(True)
        self.tableWidgetWGE.horizontalHeader().setDefaultSectionSize(87)
        self.tableWidgetWGE.verticalHeader().setDefaultSectionSize(18)
        self.tableWidgetWGE.verticalHeader().setMinimumSectionSize(10)
        self.pushButtonDone = QtGui.QPushButton(self.centralwidget)
        self.pushButtonDone.setGeometry(QtCore.QRect(720, 420, 141, 23))
        self.pushButtonDone.setObjectName(_fromUtf8("pushButtonDone"))
        WorkspaceComposer.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(WorkspaceComposer)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 913, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        WorkspaceComposer.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(WorkspaceComposer)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        WorkspaceComposer.setStatusBar(self.statusbar)

        self.retranslateUi(WorkspaceComposer)
        QtCore.QObject.connect(self.centralwidget, QtCore.SIGNAL(_fromUtf8("customContextMenuRequested(QPoint)")), self.centralwidget.show)
        QtCore.QObject.connect(self.pushButtonUpdate, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.pushButtonUpdate.show)
        QtCore.QObject.connect(self.pushButtonCreateWorkspace, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.radioButtonLoadData.show)
        QtCore.QObject.connect(self.pushButtonDone, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.pushButtonDone.show)
        QtCore.QMetaObject.connectSlotsByName(WorkspaceComposer)

    def retranslateUi(self, WorkspaceComposer):
        WorkspaceComposer.setWindowTitle(_translate("WorkspaceComposer", "MainWindow", None))
        self.groupBox_5.setTitle(_translate("WorkspaceComposer", "Select Task", None))
        self.label.setText(_translate("WorkspaceComposer", "Resulting Workspace Name:", None))
        self.lineEditGroupName.setText(_translate("WorkspaceComposer", "NewWorkspace", None))
        self.pushButtonCreateWorkspace.setText(_translate("WorkspaceComposer", "Create Workspace", None))
        self.radioButtonSumWS.setText(_translate("WorkspaceComposer", "Sum Workspaces", None))
        self.radioButtonGroupWS.setText(_translate("WorkspaceComposer", "Group Workspaces", None))
        self.radioButtonExecuteEqn.setText(_translate("WorkspaceComposer", "Execute Equation", None))
        self.groupBox_6.setTitle(_translate("WorkspaceComposer", "Select Data", None))
        self.pushButtonUpdate.setText(_translate("WorkspaceComposer", "Update", None))
        self.radioButtonRemoveSelected.setText(_translate("WorkspaceComposer", "Remove Selected", None))
        self.radioButtonClearAll.setText(_translate("WorkspaceComposer", "Clear All", None))
        self.radioButtonSelectAll.setText(_translate("WorkspaceComposer", "Select All", None))
        self.radioButtonLoadData.setText(_translate("WorkspaceComposer", "Load Data", None))
        self.groupBox_2.setTitle(_translate("WorkspaceComposer", "Workspace Algebra Section", None))
        self.lineEditEquation.setToolTip(_translate("WorkspaceComposer", "Enter an equation using the workspace indicies listed in the Workspace List above.  The shorter Index names are used for convenience.", None))
        self.label_5.setText(_translate("WorkspaceComposer", "Enter Equation - use workspace names or indicies from the table above, for example:  (ws0-ws1)/ws2", None))
        self.groupBox_4.setTitle(_translate("WorkspaceComposer", "Workspace List", None))
        item = self.tableWidgetWGE.horizontalHeaderItem(0)
        item.setText(_translate("WorkspaceComposer", "Index", None))
        item = self.tableWidgetWGE.horizontalHeaderItem(1)
        item.setText(_translate("WorkspaceComposer", "Workspace", None))
        item = self.tableWidgetWGE.horizontalHeaderItem(2)
        item.setText(_translate("WorkspaceComposer", "Location", None))
        item = self.tableWidgetWGE.horizontalHeaderItem(3)
        item.setText(_translate("WorkspaceComposer", "Date", None))
        item = self.tableWidgetWGE.horizontalHeaderItem(4)
        item.setText(_translate("WorkspaceComposer", "Size", None))
        item = self.tableWidgetWGE.horizontalHeaderItem(5)
        item.setText(_translate("WorkspaceComposer", "In Memory", None))
        item = self.tableWidgetWGE.horizontalHeaderItem(6)
        item.setText(_translate("WorkspaceComposer", "Select", None))
        self.pushButtonDone.setText(_translate("WorkspaceComposer", "Done", None))

