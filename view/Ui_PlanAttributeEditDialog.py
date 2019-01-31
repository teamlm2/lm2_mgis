# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\PlanAttributeEditDialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_PlanAttributeEditDialog(object):
    def setupUi(self, PlanAttributeEditDialog):
        PlanAttributeEditDialog.setObjectName(_fromUtf8("PlanAttributeEditDialog"))
        PlanAttributeEditDialog.resize(402, 578)
        self.ok_button = QtGui.QPushButton(PlanAttributeEditDialog)
        self.ok_button.setGeometry(QtCore.QRect(232, 549, 75, 23))
        self.ok_button.setObjectName(_fromUtf8("ok_button"))
        self.help_button = QtGui.QPushButton(PlanAttributeEditDialog)
        self.help_button.setGeometry(QtCore.QRect(146, 549, 75, 23))
        self.help_button.setStyleSheet(_fromUtf8("image: url(:/plugins/lm2/help_button.png);"))
        self.help_button.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/lm2/help_button.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.help_button.setIcon(icon)
        self.help_button.setObjectName(_fromUtf8("help_button"))
        self.close_button = QtGui.QPushButton(PlanAttributeEditDialog)
        self.close_button.setGeometry(QtCore.QRect(316, 549, 75, 23))
        self.close_button.setObjectName(_fromUtf8("close_button"))
        self.tableWidget = QtGui.QTableWidget(PlanAttributeEditDialog)
        self.tableWidget.setGeometry(QtCore.QRect(10, 30, 381, 501))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        self.line = QtGui.QFrame(PlanAttributeEditDialog)
        self.line.setGeometry(QtCore.QRect(0, 17, 401, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.label = QtGui.QLabel(PlanAttributeEditDialog)
        self.label.setGeometry(QtCore.QRect(6, 6, 391, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.line_2 = QtGui.QFrame(PlanAttributeEditDialog)
        self.line_2.setGeometry(QtCore.QRect(0, 533, 401, 16))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))

        self.retranslateUi(PlanAttributeEditDialog)
        QtCore.QMetaObject.connectSlotsByName(PlanAttributeEditDialog)

    def retranslateUi(self, PlanAttributeEditDialog):
        PlanAttributeEditDialog.setWindowTitle(_translate("PlanAttributeEditDialog", "Dialog", None))
        self.ok_button.setText(_translate("PlanAttributeEditDialog", "Ok", None))
        self.close_button.setText(_translate("PlanAttributeEditDialog", "Close", None))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("PlanAttributeEditDialog", "Attribute Name", None))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("PlanAttributeEditDialog", "Attribute Value", None))
        self.label.setText(_translate("PlanAttributeEditDialog", "Edit parcels attribute", None))

import resources_rc
