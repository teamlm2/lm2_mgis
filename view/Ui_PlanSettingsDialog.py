# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PlanSettingsDialog.ui'
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

class Ui_PlanSettingsDialog(object):
    def setupUi(self, PlanSettingsDialog):
        PlanSettingsDialog.setObjectName(_fromUtf8("PlanSettingsDialog"))
        PlanSettingsDialog.resize(892, 571)
        self.line = QtGui.QFrame(PlanSettingsDialog)
        self.line.setGeometry(QtCore.QRect(443, 20, 20, 511))
        self.line.setLineWidth(3)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.process_type_treewidget = QtGui.QTreeWidget(PlanSettingsDialog)
        self.process_type_treewidget.setGeometry(QtCore.QRect(460, 90, 421, 361))
        self.process_type_treewidget.setObjectName(_fromUtf8("process_type_treewidget"))
        self.process_type_treewidget.headerItem().setText(0, _fromUtf8("1"))
        self.tmp_plan_type_cbox = QtGui.QComboBox(PlanSettingsDialog)
        self.tmp_plan_type_cbox.setGeometry(QtCore.QRect(460, 40, 361, 22))
        self.tmp_plan_type_cbox.setObjectName(_fromUtf8("tmp_plan_type_cbox"))
        self.default_plan_zone_chbox = QtGui.QCheckBox(PlanSettingsDialog)
        self.default_plan_zone_chbox.setGeometry(QtCore.QRect(460, 70, 151, 17))
        self.default_plan_zone_chbox.setObjectName(_fromUtf8("default_plan_zone_chbox"))

        self.retranslateUi(PlanSettingsDialog)
        QtCore.QMetaObject.connectSlotsByName(PlanSettingsDialog)

    def retranslateUi(self, PlanSettingsDialog):
        PlanSettingsDialog.setWindowTitle(_translate("PlanSettingsDialog", "Dialog", None))
        self.default_plan_zone_chbox.setText(_translate("PlanSettingsDialog", "Default plan zone", None))

