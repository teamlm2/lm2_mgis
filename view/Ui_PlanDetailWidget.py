# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\PlanDetailWidget.ui'
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

class Ui_PlanDetailWidget(object):
    def setupUi(self, PlanDetailWidget):
        PlanDetailWidget.setObjectName(_fromUtf8("PlanDetailWidget"))
        PlanDetailWidget.resize(415, 712)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PlanDetailWidget.sizePolicy().hasHeightForWidth())
        PlanDetailWidget.setSizePolicy(sizePolicy)
        PlanDetailWidget.setMinimumSize(QtCore.QSize(415, 620))
        PlanDetailWidget.setMaximumSize(QtCore.QSize(415, 524287))
        PlanDetailWidget.setBaseSize(QtCore.QSize(440, 665))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.scrollArea = QtGui.QScrollArea(self.dockWidgetContents)
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, 418, 650))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QtCore.QSize(0, 600))
        self.scrollArea.setMaximumSize(QtCore.QSize(435, 650))
        self.scrollArea.setWidgetResizable(False)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 419, 664))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.error_label = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.error_label.setGeometry(QtCore.QRect(10, 600, 374, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Helvetica"))
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.error_label.setFont(font)
        self.error_label.setStyleSheet(_fromUtf8("QLabel {color : red;}\n"
"font: 75 14pt \"Helvetica\";"))
        self.error_label.setText(_fromUtf8(""))
        self.error_label.setWordWrap(True)
        self.error_label.setObjectName(_fromUtf8("error_label"))
        self.groupBox = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setGeometry(QtCore.QRect(10, 30, 381, 151))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(10, 15, 81, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.type_edit = QtGui.QLineEdit(self.groupBox)
        self.type_edit.setGeometry(QtCore.QRect(10, 35, 361, 20))
        self.type_edit.setReadOnly(True)
        self.type_edit.setObjectName(_fromUtf8("type_edit"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(10, 57, 81, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.decision_level_edit = QtGui.QLineEdit(self.groupBox)
        self.decision_level_edit.setGeometry(QtCore.QRect(10, 77, 361, 20))
        self.decision_level_edit.setReadOnly(True)
        self.decision_level_edit.setObjectName(_fromUtf8("decision_level_edit"))
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(10, 98, 81, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.status_edit = QtGui.QLineEdit(self.groupBox)
        self.status_edit.setGeometry(QtCore.QRect(10, 118, 361, 20))
        self.status_edit.setReadOnly(True)
        self.status_edit.setObjectName(_fromUtf8("status_edit"))
        self.home_button = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.home_button.setGeometry(QtCore.QRect(10, 4, 75, 23))
        self.home_button.setObjectName(_fromUtf8("home_button"))
        self.plan_num_edit = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.plan_num_edit.setGeometry(QtCore.QRect(220, 6, 170, 20))
        self.plan_num_edit.setReadOnly(True)
        self.plan_num_edit.setObjectName(_fromUtf8("plan_num_edit"))
        self.date_edit = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.date_edit.setGeometry(QtCore.QRect(140, 6, 70, 20))
        self.date_edit.setReadOnly(True)
        self.date_edit.setObjectName(_fromUtf8("date_edit"))
        self.tabWidget = QtGui.QTabWidget(self.scrollAreaWidgetContents)
        self.tabWidget.setGeometry(QtCore.QRect(10, 190, 381, 431))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.tableWidget = QtGui.QTableWidget(self.tab)
        self.tableWidget.setGeometry(QtCore.QRect(10, 30, 361, 351))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.main_zone_load_button = QtGui.QPushButton(self.tab)
        self.main_zone_load_button.setGeometry(QtCore.QRect(9, 3, 75, 23))
        self.main_zone_load_button.setObjectName(_fromUtf8("main_zone_load_button"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        PlanDetailWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(PlanDetailWidget)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(PlanDetailWidget)

    def retranslateUi(self, PlanDetailWidget):
        PlanDetailWidget.setWindowTitle(_translate("PlanDetailWidget", "Selection / Filter", None))
        self.groupBox.setTitle(_translate("PlanDetailWidget", "General info", None))
        self.label.setText(_translate("PlanDetailWidget", "Type", None))
        self.label_2.setText(_translate("PlanDetailWidget", "Decision Level", None))
        self.label_3.setText(_translate("PlanDetailWidget", "Status", None))
        self.home_button.setText(_translate("PlanDetailWidget", "Home", None))
        self.main_zone_load_button.setText(_translate("PlanDetailWidget", "Load", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("PlanDetailWidget", "Main Zone", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("PlanDetailWidget", "Sub Zone", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("PlanDetailWidget", "Parcel", None))

