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
        PlanAttributeEditDialog.resize(461, 601)
        self.apply_button = QtGui.QPushButton(PlanAttributeEditDialog)
        self.apply_button.setGeometry(QtCore.QRect(296, 572, 75, 23))
        self.apply_button.setObjectName(_fromUtf8("apply_button"))
        self.help_button = QtGui.QPushButton(PlanAttributeEditDialog)
        self.help_button.setGeometry(QtCore.QRect(210, 572, 75, 23))
        self.help_button.setStyleSheet(_fromUtf8("image: url(:/plugins/lm2/help_button.png);"))
        self.help_button.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/lm2/help_button.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.help_button.setIcon(icon)
        self.help_button.setObjectName(_fromUtf8("help_button"))
        self.close_button = QtGui.QPushButton(PlanAttributeEditDialog)
        self.close_button.setGeometry(QtCore.QRect(380, 572, 75, 23))
        self.close_button.setObjectName(_fromUtf8("close_button"))
        self.line = QtGui.QFrame(PlanAttributeEditDialog)
        self.line.setGeometry(QtCore.QRect(0, 17, 461, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.label = QtGui.QLabel(PlanAttributeEditDialog)
        self.label.setGeometry(QtCore.QRect(6, 6, 391, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.line_2 = QtGui.QFrame(PlanAttributeEditDialog)
        self.line_2.setGeometry(QtCore.QRect(0, 556, 461, 16))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.attribute_group_box = QtGui.QGroupBox(PlanAttributeEditDialog)
        self.attribute_group_box.setGeometry(QtCore.QRect(3, 27, 451, 531))
        self.attribute_group_box.setMinimumSize(QtCore.QSize(451, 531))
        self.attribute_group_box.setMaximumSize(QtCore.QSize(451, 531))
        self.attribute_group_box.setObjectName(_fromUtf8("attribute_group_box"))
        self.status_label = QtGui.QLabel(PlanAttributeEditDialog)
        self.status_label.setGeometry(QtCore.QRect(6, 575, 201, 16))
        self.status_label.setText(_fromUtf8(""))
        self.status_label.setObjectName(_fromUtf8("status_label"))

        self.retranslateUi(PlanAttributeEditDialog)
        QtCore.QMetaObject.connectSlotsByName(PlanAttributeEditDialog)

    def retranslateUi(self, PlanAttributeEditDialog):
        PlanAttributeEditDialog.setWindowTitle(_translate("PlanAttributeEditDialog", "Dialog", None))
        self.apply_button.setText(_translate("PlanAttributeEditDialog", "Apply", None))
        self.close_button.setText(_translate("PlanAttributeEditDialog", "Close", None))
        self.label.setText(_translate("PlanAttributeEditDialog", "Edit parcels attribute", None))
        self.attribute_group_box.setTitle(_translate("PlanAttributeEditDialog", "Attribute Information", None))

import resources_rc
