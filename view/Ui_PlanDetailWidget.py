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
        PlanDetailWidget.resize(600, 800)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PlanDetailWidget.sizePolicy().hasHeightForWidth())
        PlanDetailWidget.setSizePolicy(sizePolicy)
        PlanDetailWidget.setMinimumSize(QtCore.QSize(600, 800))
        PlanDetailWidget.setMaximumSize(QtCore.QSize(600, 800))
        PlanDetailWidget.setBaseSize(QtCore.QSize(440, 665))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.scrollArea = QtGui.QScrollArea(self.dockWidgetContents)
        self.scrollArea.setGeometry(QtCore.QRect(2, 0, 598, 776))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QtCore.QSize(550, 300))
        self.scrollArea.setMaximumSize(QtCore.QSize(600, 1500))
        self.scrollArea.setWidgetResizable(False)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 600, 1000))
        self.scrollAreaWidgetContents.setMinimumSize(QtCore.QSize(550, 1000))
        self.scrollAreaWidgetContents.setMaximumSize(QtCore.QSize(600, 800))
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
        self.groupBox.setGeometry(QtCore.QRect(4, 27, 572, 91))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(10, 14, 150, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.type_edit = QtGui.QLineEdit(self.groupBox)
        self.type_edit.setGeometry(QtCore.QRect(164, 12, 400, 20))
        self.type_edit.setReadOnly(True)
        self.type_edit.setObjectName(_fromUtf8("type_edit"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(10, 39, 150, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.decision_level_edit = QtGui.QLineEdit(self.groupBox)
        self.decision_level_edit.setGeometry(QtCore.QRect(164, 37, 400, 20))
        self.decision_level_edit.setReadOnly(True)
        self.decision_level_edit.setObjectName(_fromUtf8("decision_level_edit"))
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(10, 64, 150, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.status_edit = QtGui.QLineEdit(self.groupBox)
        self.status_edit.setGeometry(QtCore.QRect(164, 62, 400, 20))
        self.status_edit.setReadOnly(True)
        self.status_edit.setObjectName(_fromUtf8("status_edit"))
        self.home_button = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.home_button.setGeometry(QtCore.QRect(10, 4, 75, 23))
        self.home_button.setObjectName(_fromUtf8("home_button"))
        self.plan_num_edit = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.plan_num_edit.setGeometry(QtCore.QRect(248, 6, 170, 20))
        self.plan_num_edit.setReadOnly(True)
        self.plan_num_edit.setObjectName(_fromUtf8("plan_num_edit"))
        self.date_edit = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.date_edit.setGeometry(QtCore.QRect(168, 6, 70, 20))
        self.date_edit.setReadOnly(True)
        self.date_edit.setObjectName(_fromUtf8("date_edit"))
        self.tabWidget = QtGui.QTabWidget(self.scrollAreaWidgetContents)
        self.tabWidget.setGeometry(QtCore.QRect(4, 230, 574, 521))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.main_tree_widget = QtGui.QTreeWidget(self.tab)
        self.main_tree_widget.setGeometry(QtCore.QRect(6, 3, 559, 481))
        self.main_tree_widget.setObjectName(_fromUtf8("main_tree_widget"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.sub_tree_widget = QtGui.QTableWidget(self.tab_2)
        self.sub_tree_widget.setGeometry(QtCore.QRect(10, 10, 361, 320))
        self.sub_tree_widget.setObjectName(_fromUtf8("sub_tree_widget"))
        self.sub_tree_widget.setColumnCount(0)
        self.sub_tree_widget.setRowCount(0)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.parcel_tree_widget = QtGui.QTableWidget(self.tab_3)
        self.parcel_tree_widget.setGeometry(QtCore.QRect(10, 10, 361, 320))
        self.parcel_tree_widget.setObjectName(_fromUtf8("parcel_tree_widget"))
        self.parcel_tree_widget.setColumnCount(0)
        self.parcel_tree_widget.setRowCount(0)
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.groupBox_2 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_2.setGeometry(QtCore.QRect(4, 117, 572, 110))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.load_pbar = QtGui.QProgressBar(self.groupBox_2)
        self.load_pbar.setGeometry(QtCore.QRect(290, 80, 269, 23))
        self.load_pbar.setProperty("value", 0)
        self.load_pbar.setTextDirection(QtGui.QProgressBar.TopToBottom)
        self.load_pbar.setObjectName(_fromUtf8("load_pbar"))
        self.main_zone_load_button = QtGui.QPushButton(self.groupBox_2)
        self.main_zone_load_button.setGeometry(QtCore.QRect(9, 80, 81, 23))
        self.main_zone_load_button.setObjectName(_fromUtf8("main_zone_load_button"))
        self.process_type_cbox = QtGui.QComboBox(self.groupBox_2)
        self.process_type_cbox.setGeometry(QtCore.QRect(163, 16, 400, 22))
        self.process_type_cbox.setObjectName(_fromUtf8("process_type_cbox"))
        self.process_edit = QtGui.QLineEdit(self.groupBox_2)
        self.process_edit.setGeometry(QtCore.QRect(163, 46, 400, 20))
        self.process_edit.setObjectName(_fromUtf8("process_edit"))
        self.label_4 = QtGui.QLabel(self.groupBox_2)
        self.label_4.setGeometry(QtCore.QRect(10, 20, 150, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(self.groupBox_2)
        self.label_5.setGeometry(QtCore.QRect(10, 48, 150, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.main_to_layer_button = QtGui.QPushButton(self.groupBox_2)
        self.main_to_layer_button.setGeometry(QtCore.QRect(100, 80, 81, 23))
        self.main_to_layer_button.setObjectName(_fromUtf8("main_to_layer_button"))
        self.main_edit_attribute_button = QtGui.QPushButton(self.groupBox_2)
        self.main_edit_attribute_button.setGeometry(QtCore.QRect(190, 80, 81, 23))
        self.main_edit_attribute_button.setObjectName(_fromUtf8("main_edit_attribute_button"))
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
        self.main_tree_widget.headerItem().setText(0, _translate("PlanDetailWidget", "Result", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("PlanDetailWidget", "Main Zone", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("PlanDetailWidget", "Sub Zone", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("PlanDetailWidget", "Parcel", None))
        self.groupBox_2.setTitle(_translate("PlanDetailWidget", "Find", None))
        self.main_zone_load_button.setText(_translate("PlanDetailWidget", "Load", None))
        self.label_4.setText(_translate("PlanDetailWidget", "Process Type", None))
        self.label_5.setText(_translate("PlanDetailWidget", "Process Desc", None))
        self.main_to_layer_button.setText(_translate("PlanDetailWidget", "To Layer", None))
        self.main_edit_attribute_button.setText(_translate("PlanDetailWidget", "Edit Attribute", None))

