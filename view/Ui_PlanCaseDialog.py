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
        PlanCaseDialog.resize(785, 559)
        self.groupBox = QtGui.QGroupBox(PlanCaseDialog)
        self.groupBox.setGeometry(QtCore.QRect(5, 8, 774, 58))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(10, 16, 167, 13))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.type_edit = QtGui.QLineEdit(self.groupBox)
        self.type_edit.setGeometry(QtCore.QRect(220, 32, 270, 20))
        self.type_edit.setReadOnly(True)
        self.type_edit.setObjectName(_fromUtf8("type_edit"))
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(220, 15, 81, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.date_edit = QtGui.QLineEdit(self.groupBox)
        self.date_edit.setGeometry(QtCore.QRect(10, 32, 71, 20))
        self.date_edit.setReadOnly(True)
        self.date_edit.setObjectName(_fromUtf8("date_edit"))
        self.plan_num_edit = QtGui.QLineEdit(self.groupBox)
        self.plan_num_edit.setGeometry(QtCore.QRect(90, 32, 122, 20))
        self.plan_num_edit.setReadOnly(True)
        self.plan_num_edit.setObjectName(_fromUtf8("plan_num_edit"))
        self.status_edit = QtGui.QLineEdit(self.groupBox)
        self.status_edit.setGeometry(QtCore.QRect(499, 32, 270, 20))
        self.status_edit.setReadOnly(True)
        self.status_edit.setObjectName(_fromUtf8("status_edit"))
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(499, 16, 81, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.line = QtGui.QFrame(PlanCaseDialog)
        self.line.setGeometry(QtCore.QRect(0, 6, 785, 7))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.line_2 = QtGui.QFrame(PlanCaseDialog)
        self.line_2.setGeometry(QtCore.QRect(0, 530, 785, 7))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.help_button = QtGui.QPushButton(PlanCaseDialog)
        self.help_button.setGeometry(QtCore.QRect(518, 503, 75, 23))
        self.help_button.setStyleSheet(_fromUtf8("image: url(:/plugins/lm2/help_button.png);"))
        self.help_button.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/lm2/help_button.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.help_button.setIcon(icon)
        self.help_button.setObjectName(_fromUtf8("help_button"))
        self.close_button = QtGui.QPushButton(PlanCaseDialog)
        self.close_button.setGeometry(QtCore.QRect(697, 503, 75, 23))
        self.close_button.setObjectName(_fromUtf8("close_button"))
        self.apply_button = QtGui.QPushButton(PlanCaseDialog)
        self.apply_button.setGeometry(QtCore.QRect(607, 503, 75, 23))
        self.apply_button.setObjectName(_fromUtf8("apply_button"))
        self.tabWidget = QtGui.QTabWidget(PlanCaseDialog)
        self.tabWidget.setGeometry(QtCore.QRect(5, 67, 775, 433))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.main_tree_widget = QtGui.QTreeWidget(self.tab_2)
        self.main_tree_widget.setGeometry(QtCore.QRect(10, 90, 751, 135))
        self.main_tree_widget.setWordWrap(True)
        self.main_tree_widget.setObjectName(_fromUtf8("main_tree_widget"))
        self.label_10 = QtGui.QLabel(self.tab_2)
        self.label_10.setGeometry(QtCore.QRect(7, 34, 80, 16))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.zone_type_cbox = QtGui.QComboBox(self.tab_2)
        self.zone_type_cbox.setGeometry(QtCore.QRect(90, 31, 281, 22))
        self.zone_type_cbox.setObjectName(_fromUtf8("zone_type_cbox"))
        self.main_process_type_cbox = QtGui.QComboBox(self.tab_2)
        self.main_process_type_cbox.setGeometry(QtCore.QRect(90, 58, 581, 22))
        self.main_process_type_cbox.setObjectName(_fromUtf8("main_process_type_cbox"))
        self.label_5 = QtGui.QLabel(self.tab_2)
        self.label_5.setGeometry(QtCore.QRect(7, 61, 80, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.add_button = QtGui.QPushButton(self.tab_2)
        self.add_button.setGeometry(QtCore.QRect(360, 230, 30, 25))
        self.add_button.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/lm2/down_button.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_button.setIcon(icon1)
        self.add_button.setObjectName(_fromUtf8("add_button"))
        self.remove_button = QtGui.QPushButton(self.tab_2)
        self.remove_button.setGeometry(QtCore.QRect(400, 230, 30, 25))
        self.remove_button.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/lm2/up_button.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remove_button.setIcon(icon2)
        self.remove_button.setObjectName(_fromUtf8("remove_button"))
        self.label_11 = QtGui.QLabel(self.tab_2)
        self.label_11.setGeometry(QtCore.QRect(7, 8, 80, 16))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.plan_cbox = QtGui.QComboBox(self.tab_2)
        self.plan_cbox.setGeometry(QtCore.QRect(90, 5, 280, 22))
        self.plan_cbox.setObjectName(_fromUtf8("plan_cbox"))
        self.find_button = QtGui.QPushButton(self.tab_2)
        self.find_button.setGeometry(QtCore.QRect(686, 58, 75, 23))
        self.find_button.setObjectName(_fromUtf8("find_button"))
        self.current_tree_widget = QtGui.QTreeWidget(self.tab_2)
        self.current_tree_widget.setGeometry(QtCore.QRect(10, 260, 751, 135))
        self.current_tree_widget.setWordWrap(True)
        self.current_tree_widget.setObjectName(_fromUtf8("current_tree_widget"))
        self.current_tree_widget.header().setDefaultSectionSize(200)
        self.form_type_cbox = QtGui.QComboBox(self.tab_2)
        self.form_type_cbox.setGeometry(QtCore.QRect(460, 5, 300, 22))
        self.form_type_cbox.setObjectName(_fromUtf8("form_type_cbox"))
        self.label_12 = QtGui.QLabel(self.tab_2)
        self.label_12.setGeometry(QtCore.QRect(378, 8, 80, 16))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.result_twidget = QtGui.QTreeWidget(self.tab)
        self.result_twidget.setGeometry(QtCore.QRect(401, 6, 361, 391))
        self.result_twidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.result_twidget.setObjectName(_fromUtf8("result_twidget"))
        self.result_twidget.header().setDefaultSectionSize(100)
        self.import_groupbox = QtGui.QGroupBox(self.tab)
        self.import_groupbox.setEnabled(True)
        self.import_groupbox.setGeometry(QtCore.QRect(11, 0, 381, 141))
        self.import_groupbox.setObjectName(_fromUtf8("import_groupbox"))
        self.parcel_shape_edit = QtGui.QLineEdit(self.import_groupbox)
        self.parcel_shape_edit.setGeometry(QtCore.QRect(9, 104, 311, 21))
        self.parcel_shape_edit.setReadOnly(True)
        self.parcel_shape_edit.setObjectName(_fromUtf8("parcel_shape_edit"))
        self.label = QtGui.QLabel(self.import_groupbox)
        self.label.setGeometry(QtCore.QRect(10, 85, 112, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.open_parcel_file_button = QtGui.QPushButton(self.import_groupbox)
        self.open_parcel_file_button.setGeometry(QtCore.QRect(330, 102, 42, 25))
        self.open_parcel_file_button.setText(_fromUtf8(""))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/lm2/open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.open_parcel_file_button.setIcon(icon3)
        self.open_parcel_file_button.setObjectName(_fromUtf8("open_parcel_file_button"))
        self.point_rbutton = QtGui.QRadioButton(self.import_groupbox)
        self.point_rbutton.setGeometry(QtCore.QRect(10, 20, 82, 17))
        self.point_rbutton.setObjectName(_fromUtf8("point_rbutton"))
        self.line_rbutton = QtGui.QRadioButton(self.import_groupbox)
        self.line_rbutton.setGeometry(QtCore.QRect(10, 40, 82, 17))
        self.line_rbutton.setObjectName(_fromUtf8("line_rbutton"))
        self.polygon_rbutton = QtGui.QRadioButton(self.import_groupbox)
        self.polygon_rbutton.setEnabled(True)
        self.polygon_rbutton.setGeometry(QtCore.QRect(10, 60, 82, 17))
        self.polygon_rbutton.setObjectName(_fromUtf8("polygon_rbutton"))
        self.message_label = QtGui.QLabel(self.tab)
        self.message_label.setGeometry(QtCore.QRect(12, 150, 377, 71))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.message_label.setFont(font)
        self.message_label.setObjectName(_fromUtf8("message_label"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.status_label = QtGui.QLabel(PlanCaseDialog)
        self.status_label.setGeometry(QtCore.QRect(10, 510, 399, 16))
        self.status_label.setText(_fromUtf8(""))
        self.status_label.setObjectName(_fromUtf8("status_label"))
        self.main_load_pbar = QtGui.QProgressBar(PlanCaseDialog)
        self.main_load_pbar.setGeometry(QtCore.QRect(520, 538, 261, 14))
        self.main_load_pbar.setProperty("value", 0)
        self.main_load_pbar.setTextDirection(QtGui.QProgressBar.TopToBottom)
        self.main_load_pbar.setObjectName(_fromUtf8("main_load_pbar"))

        self.retranslateUi(PlanCaseDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(PlanCaseDialog)

    def retranslateUi(self, PlanCaseDialog):
        PlanCaseDialog.setWindowTitle(_translate("PlanCaseDialog", "Dialog", None))
        self.groupBox.setTitle(_translate("PlanCaseDialog", "General information", None))
        self.label_2.setText(_translate("PlanCaseDialog", "Date & Number", None))
        self.label_3.setText(_translate("PlanCaseDialog", "Type", None))
        self.label_4.setText(_translate("PlanCaseDialog", "Status", None))
        self.close_button.setText(_translate("PlanCaseDialog", "Close", None))
        self.apply_button.setText(_translate("PlanCaseDialog", "Apply", None))
        self.main_tree_widget.setSortingEnabled(True)
        self.main_tree_widget.headerItem().setText(0, _translate("PlanCaseDialog", "Result", None))
        self.label_10.setText(_translate("PlanCaseDialog", "Zone Type", None))
        self.label_5.setText(_translate("PlanCaseDialog", "Process Type", None))
        self.label_11.setText(_translate("PlanCaseDialog", "Plan", None))
        self.find_button.setText(_translate("PlanCaseDialog", "Find", None))
        self.current_tree_widget.setSortingEnabled(True)
        self.current_tree_widget.headerItem().setText(0, _translate("PlanCaseDialog", "Parcel Info", None))
        self.current_tree_widget.headerItem().setText(1, _translate("PlanCaseDialog", "Form type", None))
        self.current_tree_widget.headerItem().setText(2, _translate("PlanCaseDialog", "From", None))
        self.label_12.setText(_translate("PlanCaseDialog", "Form Type", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("PlanCaseDialog", "Other Plan Import", None))
        self.result_twidget.headerItem().setText(0, _translate("PlanCaseDialog", "Maintenance Case Objects", None))
        self.import_groupbox.setTitle(_translate("PlanCaseDialog", "Import", None))
        self.label.setText(_translate("PlanCaseDialog", "Parcel Shapefile", None))
        self.point_rbutton.setText(_translate("PlanCaseDialog", "Point", None))
        self.line_rbutton.setText(_translate("PlanCaseDialog", "Line", None))
        self.polygon_rbutton.setText(_translate("PlanCaseDialog", "Polygon", None))
        self.message_label.setText(_translate("PlanCaseDialog", "Message Information", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("PlanCaseDialog", "New Parcel Import", None))

import resources_rc
