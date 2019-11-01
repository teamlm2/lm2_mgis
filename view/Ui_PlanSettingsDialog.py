# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\PlanSettingsDialog.ui'
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
        self.tabWidget = QtGui.QTabWidget(PlanSettingsDialog)
        self.tabWidget.setGeometry(QtCore.QRect(5, 26, 441, 511))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.zone_level_rbutton = QtGui.QRadioButton(self.tab)
        self.zone_level_rbutton.setGeometry(QtCore.QRect(10, 10, 221, 17))
        self.zone_level_rbutton.setObjectName(_fromUtf8("zone_level_rbutton"))
        self.zone_type_rbutton = QtGui.QRadioButton(self.tab)
        self.zone_type_rbutton.setGeometry(QtCore.QRect(10, 30, 221, 17))
        self.zone_type_rbutton.setObjectName(_fromUtf8("zone_type_rbutton"))
        self.right_type_rbutton = QtGui.QRadioButton(self.tab)
        self.right_type_rbutton.setGeometry(QtCore.QRect(10, 50, 221, 17))
        self.right_type_rbutton.setObjectName(_fromUtf8("right_type_rbutton"))
        self.plan_type_rbutton = QtGui.QRadioButton(self.tab)
        self.plan_type_rbutton.setGeometry(QtCore.QRect(10, 70, 221, 17))
        self.plan_type_rbutton.setObjectName(_fromUtf8("plan_type_rbutton"))
        self.settings_twidget = QtGui.QTableWidget(self.tab)
        self.settings_twidget.setGeometry(QtCore.QRect(10, 110, 421, 373))
        self.settings_twidget.setObjectName(_fromUtf8("settings_twidget"))
        self.settings_twidget.setColumnCount(2)
        self.settings_twidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.settings_twidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.settings_twidget.setHorizontalHeaderItem(1, item)
        self.sec_zone_rbutton = QtGui.QRadioButton(self.tab)
        self.sec_zone_rbutton.setGeometry(QtCore.QRect(10, 90, 221, 17))
        self.sec_zone_rbutton.setObjectName(_fromUtf8("sec_zone_rbutton"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.plan_zone_treewidget = QtGui.QTreeWidget(self.tab_2)
        self.plan_zone_treewidget.setGeometry(QtCore.QRect(10, 2, 421, 481))
        self.plan_zone_treewidget.setObjectName(_fromUtf8("plan_zone_treewidget"))
        self.plan_zone_treewidget.headerItem().setText(0, _fromUtf8("1"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.apply_button = QtGui.QPushButton(PlanSettingsDialog)
        self.apply_button.setGeometry(QtCore.QRect(723, 541, 75, 23))
        self.apply_button.setObjectName(_fromUtf8("apply_button"))
        self.close_button = QtGui.QPushButton(PlanSettingsDialog)
        self.close_button.setGeometry(QtCore.QRect(813, 541, 75, 23))
        self.close_button.setObjectName(_fromUtf8("close_button"))
        self.help_button = QtGui.QPushButton(PlanSettingsDialog)
        self.help_button.setGeometry(QtCore.QRect(634, 541, 75, 23))
        self.help_button.setStyleSheet(_fromUtf8("image: url(:/plugins/lm2/help_button.png);"))
        self.help_button.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/lm2/help_button.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.help_button.setIcon(icon)
        self.help_button.setObjectName(_fromUtf8("help_button"))
        self.status_label = QtGui.QLabel(PlanSettingsDialog)
        self.status_label.setGeometry(QtCore.QRect(10, 545, 591, 16))
        self.status_label.setText(_fromUtf8(""))
        self.status_label.setObjectName(_fromUtf8("status_label"))
        self.line_2 = QtGui.QFrame(PlanSettingsDialog)
        self.line_2.setGeometry(QtCore.QRect(1, 14, 890, 20))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.label = QtGui.QLabel(PlanSettingsDialog)
        self.label.setGeometry(QtCore.QRect(10, 6, 451, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.line = QtGui.QFrame(PlanSettingsDialog)
        self.line.setGeometry(QtCore.QRect(443, 24, 20, 511))
        self.line.setLineWidth(3)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.default_plan_zone_chbox = QtGui.QCheckBox(PlanSettingsDialog)
        self.default_plan_zone_chbox.setGeometry(QtCore.QRect(460, 27, 151, 17))
        self.default_plan_zone_chbox.setObjectName(_fromUtf8("default_plan_zone_chbox"))
        self.process_type_treewidget = QtGui.QTreeWidget(PlanSettingsDialog)
        self.process_type_treewidget.setGeometry(QtCore.QRect(460, 46, 421, 491))
        self.process_type_treewidget.setObjectName(_fromUtf8("process_type_treewidget"))
        self.process_type_treewidget.headerItem().setText(0, _fromUtf8("1"))

        self.retranslateUi(PlanSettingsDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(PlanSettingsDialog)

    def retranslateUi(self, PlanSettingsDialog):
        PlanSettingsDialog.setWindowTitle(_translate("PlanSettingsDialog", "Dialog", None))
        self.zone_level_rbutton.setText(_translate("PlanSettingsDialog", "Бүсийн түвшин", None))
        self.zone_type_rbutton.setText(_translate("PlanSettingsDialog", "Арга хэмжээний төрөл", None))
        self.right_type_rbutton.setText(_translate("PlanSettingsDialog", "Эрхийн төрөл", None))
        self.plan_type_rbutton.setText(_translate("PlanSettingsDialog", "Төлөвлөгөөний төрөл", None))
        item = self.settings_twidget.horizontalHeaderItem(0)
        item.setText(_translate("PlanSettingsDialog", "Is Check", None))
        item = self.settings_twidget.horizontalHeaderItem(1)
        item.setText(_translate("PlanSettingsDialog", "Name", None))
        self.sec_zone_rbutton.setText(_translate("PlanSettingsDialog", "Хязгаарлалтын бүс", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("PlanSettingsDialog", "Үндсэн тохиргоо", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("PlanSettingsDialog", "Арга хэмжээний давхардлын тохиргоо", None))
        self.apply_button.setText(_translate("PlanSettingsDialog", "Apply", None))
        self.close_button.setText(_translate("PlanSettingsDialog", "Close", None))
        self.label.setText(_translate("PlanSettingsDialog", "Газар зохион байгуулалтын төлөвлөгөөний тохиргоо", None))
        self.default_plan_zone_chbox.setText(_translate("PlanSettingsDialog", "Show all", None))

import resources_rc
