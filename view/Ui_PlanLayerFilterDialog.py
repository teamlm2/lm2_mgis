# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\PlanLayerFilterDialog.ui'
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

class Ui_PlanLayerFilterDialog(object):
    def setupUi(self, PlanLayerFilterDialog):
        PlanLayerFilterDialog.setObjectName(_fromUtf8("PlanLayerFilterDialog"))
        PlanLayerFilterDialog.resize(533, 666)
        self.groupBox = QtGui.QGroupBox(PlanLayerFilterDialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 12, 511, 261))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.admin_unit_treewidget = QtGui.QTreeWidget(self.groupBox)
        self.admin_unit_treewidget.setGeometry(QtCore.QRect(10, 20, 491, 231))
        self.admin_unit_treewidget.setObjectName(_fromUtf8("admin_unit_treewidget"))
        self.admin_unit_treewidget.headerItem().setText(0, _fromUtf8("1"))
        self.groupBox_2 = QtGui.QGroupBox(PlanLayerFilterDialog)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 270, 511, 351))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.process_type_treewidget = QtGui.QTreeWidget(self.groupBox_2)
        self.process_type_treewidget.setGeometry(QtCore.QRect(10, 20, 491, 321))
        self.process_type_treewidget.setObjectName(_fromUtf8("process_type_treewidget"))
        self.process_type_treewidget.headerItem().setText(0, _fromUtf8("1"))
        self.pushButton = QtGui.QPushButton(PlanLayerFilterDialog)
        self.pushButton.setGeometry(QtCore.QRect(366, 630, 75, 23))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.close_button = QtGui.QPushButton(PlanLayerFilterDialog)
        self.close_button.setGeometry(QtCore.QRect(450, 630, 75, 23))
        self.close_button.setObjectName(_fromUtf8("close_button"))
        self.help_button = QtGui.QPushButton(PlanLayerFilterDialog)
        self.help_button.setGeometry(QtCore.QRect(280, 630, 75, 23))
        self.help_button.setStyleSheet(_fromUtf8("image: url(:/plugins/lm2/help_button.png);"))
        self.help_button.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/lm2/help_button.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.help_button.setIcon(icon)
        self.help_button.setObjectName(_fromUtf8("help_button"))

        self.retranslateUi(PlanLayerFilterDialog)
        QtCore.QMetaObject.connectSlotsByName(PlanLayerFilterDialog)

    def retranslateUi(self, PlanLayerFilterDialog):
        PlanLayerFilterDialog.setWindowTitle(_translate("PlanLayerFilterDialog", "Dialog", None))
        self.groupBox.setTitle(_translate("PlanLayerFilterDialog", "Admin Units", None))
        self.groupBox_2.setTitle(_translate("PlanLayerFilterDialog", "Process Type", None))
        self.pushButton.setText(_translate("PlanLayerFilterDialog", "Ok", None))
        self.close_button.setText(_translate("PlanLayerFilterDialog", "Close", None))

import resources_rc
