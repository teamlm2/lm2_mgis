# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\PlanCaseDialog.ui'
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

class Ui_PlanCaseDialog(object):
    def setupUi(self, PlanCaseDialog):
        PlanCaseDialog.setObjectName(_fromUtf8("PlanCaseDialog"))
        PlanCaseDialog.resize(785, 486)
        self.import_groupbox = QtGui.QGroupBox(PlanCaseDialog)
        self.import_groupbox.setEnabled(True)
        self.import_groupbox.setGeometry(QtCore.QRect(20, 30, 351, 90))
        self.import_groupbox.setObjectName(_fromUtf8("import_groupbox"))
        self.parcel_shape_edit = QtGui.QLineEdit(self.import_groupbox)
        self.parcel_shape_edit.setGeometry(QtCore.QRect(96, 58, 200, 21))
        self.parcel_shape_edit.setReadOnly(True)
        self.parcel_shape_edit.setObjectName(_fromUtf8("parcel_shape_edit"))
        self.label = QtGui.QLabel(self.import_groupbox)
        self.label.setGeometry(QtCore.QRect(97, 39, 101, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.open_parcel_file_button = QtGui.QPushButton(self.import_groupbox)
        self.open_parcel_file_button.setGeometry(QtCore.QRect(300, 56, 40, 25))
        self.open_parcel_file_button.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/lm2/open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.open_parcel_file_button.setIcon(icon)
        self.open_parcel_file_button.setObjectName(_fromUtf8("open_parcel_file_button"))
        self.radioButton = QtGui.QRadioButton(self.import_groupbox)
        self.radioButton.setGeometry(QtCore.QRect(10, 20, 82, 17))
        self.radioButton.setObjectName(_fromUtf8("radioButton"))
        self.radioButton_2 = QtGui.QRadioButton(self.import_groupbox)
        self.radioButton_2.setGeometry(QtCore.QRect(10, 40, 82, 17))
        self.radioButton_2.setObjectName(_fromUtf8("radioButton_2"))
        self.radioButton_3 = QtGui.QRadioButton(self.import_groupbox)
        self.radioButton_3.setEnabled(True)
        self.radioButton_3.setGeometry(QtCore.QRect(10, 60, 82, 17))
        self.radioButton_3.setObjectName(_fromUtf8("radioButton_3"))
        self.result_twidget = QtGui.QTreeWidget(PlanCaseDialog)
        self.result_twidget.setGeometry(QtCore.QRect(410, 36, 351, 318))
        self.result_twidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.result_twidget.setObjectName(_fromUtf8("result_twidget"))
        self.result_twidget.header().setDefaultSectionSize(100)
        self.groupBox = QtGui.QGroupBox(PlanCaseDialog)
        self.groupBox.setGeometry(QtCore.QRect(20, 130, 351, 221))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))

        self.retranslateUi(PlanCaseDialog)
        QtCore.QMetaObject.connectSlotsByName(PlanCaseDialog)

    def retranslateUi(self, PlanCaseDialog):
        PlanCaseDialog.setWindowTitle(_translate("PlanCaseDialog", "Dialog", None))
        self.import_groupbox.setTitle(_translate("PlanCaseDialog", "Import", None))
        self.label.setText(_translate("PlanCaseDialog", "Parcel Shapefile", None))
        self.radioButton.setText(_translate("PlanCaseDialog", "Point", None))
        self.radioButton_2.setText(_translate("PlanCaseDialog", "Line", None))
        self.radioButton_3.setText(_translate("PlanCaseDialog", "Polygon", None))
        self.result_twidget.headerItem().setText(0, _translate("PlanCaseDialog", "Maintenance Case Objects", None))
        self.groupBox.setTitle(_translate("PlanCaseDialog", "GroupBox", None))

import resources_rc
