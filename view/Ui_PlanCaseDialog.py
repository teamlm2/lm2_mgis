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
        self.type_edit.setGeometry(QtCore.QRect(190, 32, 304, 20))
        self.type_edit.setReadOnly(True)
        self.type_edit.setObjectName(_fromUtf8("type_edit"))
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(190, 15, 231, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.date_edit = QtGui.QLineEdit(self.groupBox)
        self.date_edit.setGeometry(QtCore.QRect(10, 32, 71, 20))
        self.date_edit.setReadOnly(True)
        self.date_edit.setObjectName(_fromUtf8("date_edit"))
        self.plan_num_edit = QtGui.QLineEdit(self.groupBox)
        self.plan_num_edit.setGeometry(QtCore.QRect(90, 32, 91, 20))
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
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.result_twidget = QtGui.QTreeWidget(self.tab)
        self.result_twidget.setGeometry(QtCore.QRect(401, 6, 361, 397))
        self.result_twidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.result_twidget.setObjectName(_fromUtf8("result_twidget"))
        self.result_twidget.header().setDefaultSectionSize(100)
        self.import_groupbox = QtGui.QGroupBox(self.tab)
        self.import_groupbox.setEnabled(True)
        self.import_groupbox.setGeometry(QtCore.QRect(11, 0, 381, 241))
        self.import_groupbox.setObjectName(_fromUtf8("import_groupbox"))
        self.parcel_shape_edit = QtGui.QLineEdit(self.import_groupbox)
        self.parcel_shape_edit.setGeometry(QtCore.QRect(9, 212, 311, 21))
        self.parcel_shape_edit.setReadOnly(True)
        self.parcel_shape_edit.setObjectName(_fromUtf8("parcel_shape_edit"))
        self.label = QtGui.QLabel(self.import_groupbox)
        self.label.setGeometry(QtCore.QRect(10, 193, 311, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.open_parcel_file_button = QtGui.QPushButton(self.import_groupbox)
        self.open_parcel_file_button.setGeometry(QtCore.QRect(330, 210, 42, 25))
        self.open_parcel_file_button.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/lm2/open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.open_parcel_file_button.setIcon(icon1)
        self.open_parcel_file_button.setObjectName(_fromUtf8("open_parcel_file_button"))
        self.point_rbutton = QtGui.QRadioButton(self.import_groupbox)
        self.point_rbutton.setGeometry(QtCore.QRect(150, 173, 82, 17))
        self.point_rbutton.setObjectName(_fromUtf8("point_rbutton"))
        self.line_rbutton = QtGui.QRadioButton(self.import_groupbox)
        self.line_rbutton.setGeometry(QtCore.QRect(280, 173, 91, 17))
        self.line_rbutton.setObjectName(_fromUtf8("line_rbutton"))
        self.polygon_rbutton = QtGui.QRadioButton(self.import_groupbox)
        self.polygon_rbutton.setEnabled(True)
        self.polygon_rbutton.setGeometry(QtCore.QRect(10, 173, 82, 17))
        self.polygon_rbutton.setObjectName(_fromUtf8("polygon_rbutton"))
        self.shp_process_type_cbox = QtGui.QComboBox(self.import_groupbox)
        self.shp_process_type_cbox.setEnabled(False)
        self.shp_process_type_cbox.setGeometry(QtCore.QRect(10, 145, 361, 22))
        self.shp_process_type_cbox.setToolTip(_fromUtf8(""))
        self.shp_process_type_cbox.setObjectName(_fromUtf8("shp_process_type_cbox"))
        self.if_single_type_chbox = QtGui.QCheckBox(self.import_groupbox)
        self.if_single_type_chbox.setGeometry(QtCore.QRect(10, 105, 361, 17))
        self.if_single_type_chbox.setObjectName(_fromUtf8("if_single_type_chbox"))
        self.default_plan_zone_chbox = QtGui.QCheckBox(self.import_groupbox)
        self.default_plan_zone_chbox.setGeometry(QtCore.QRect(10, 124, 361, 17))
        self.default_plan_zone_chbox.setObjectName(_fromUtf8("default_plan_zone_chbox"))
        self.shp_rigth_form_cbox = QtGui.QComboBox(self.import_groupbox)
        self.shp_rigth_form_cbox.setEnabled(True)
        self.shp_rigth_form_cbox.setGeometry(QtCore.QRect(10, 34, 361, 22))
        self.shp_rigth_form_cbox.setToolTip(_fromUtf8(""))
        self.shp_rigth_form_cbox.setObjectName(_fromUtf8("shp_rigth_form_cbox"))
        self.label_6 = QtGui.QLabel(self.import_groupbox)
        self.label_6.setGeometry(QtCore.QRect(11, 17, 361, 16))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.shp_right_type_change_cbox = QtGui.QComboBox(self.import_groupbox)
        self.shp_right_type_change_cbox.setEnabled(False)
        self.shp_right_type_change_cbox.setGeometry(QtCore.QRect(10, 80, 361, 22))
        self.shp_right_type_change_cbox.setObjectName(_fromUtf8("shp_right_type_change_cbox"))
        self.label_7 = QtGui.QLabel(self.import_groupbox)
        self.label_7.setGeometry(QtCore.QRect(10, 60, 361, 16))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.message_label = QtGui.QLabel(self.tab)
        self.message_label.setGeometry(QtCore.QRect(13, 240, 377, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.message_label.setFont(font)
        self.message_label.setObjectName(_fromUtf8("message_label"))
        self.message_txt_edit = QtGui.QPlainTextEdit(self.tab)
        self.message_txt_edit.setGeometry(QtCore.QRect(10, 242, 381, 163))
        self.message_txt_edit.setReadOnly(True)
        self.message_txt_edit.setObjectName(_fromUtf8("message_txt_edit"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.main_tree_widget = QtGui.QTreeWidget(self.tab_2)
        self.main_tree_widget.setGeometry(QtCore.QRect(10, 83, 751, 135))
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
        self.add_button.setGeometry(QtCore.QRect(10, 219, 30, 25))
        self.add_button.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/lm2/down_button.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_button.setIcon(icon2)
        self.add_button.setObjectName(_fromUtf8("add_button"))
        self.remove_button = QtGui.QPushButton(self.tab_2)
        self.remove_button.setGeometry(QtCore.QRect(50, 219, 30, 25))
        self.remove_button.setText(_fromUtf8(""))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/lm2/up_button.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remove_button.setIcon(icon3)
        self.remove_button.setObjectName(_fromUtf8("remove_button"))
        self.label_11 = QtGui.QLabel(self.tab_2)
        self.label_11.setGeometry(QtCore.QRect(7, 8, 80, 16))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.plan_cbox = QtGui.QComboBox(self.tab_2)
        self.plan_cbox.setGeometry(QtCore.QRect(90, 5, 281, 22))
        self.plan_cbox.setObjectName(_fromUtf8("plan_cbox"))
        self.find_button = QtGui.QPushButton(self.tab_2)
        self.find_button.setGeometry(QtCore.QRect(687, 58, 75, 23))
        self.find_button.setObjectName(_fromUtf8("find_button"))
        self.current_tree_widget = QtGui.QTreeWidget(self.tab_2)
        self.current_tree_widget.setGeometry(QtCore.QRect(10, 270, 751, 136))
        self.current_tree_widget.setWordWrap(True)
        self.current_tree_widget.setObjectName(_fromUtf8("current_tree_widget"))
        self.current_tree_widget.header().setDefaultSectionSize(200)
        self.form_type_cbox = QtGui.QComboBox(self.tab_2)
        self.form_type_cbox.setGeometry(QtCore.QRect(460, 5, 300, 22))
        self.form_type_cbox.setObjectName(_fromUtf8("form_type_cbox"))
        self.label_12 = QtGui.QLabel(self.tab_2)
        self.label_12.setGeometry(QtCore.QRect(378, 8, 80, 16))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.form_change_button = QtGui.QPushButton(self.tab_2)
        self.form_change_button.setEnabled(False)
        self.form_change_button.setGeometry(QtCore.QRect(687, 245, 75, 23))
        self.form_change_button.setObjectName(_fromUtf8("form_change_button"))
        self.form_type_change_cbox = QtGui.QComboBox(self.tab_2)
        self.form_type_change_cbox.setEnabled(False)
        self.form_type_change_cbox.setGeometry(QtCore.QRect(206, 221, 261, 22))
        self.form_type_change_cbox.setObjectName(_fromUtf8("form_type_change_cbox"))
        self.change_form_check_box = QtGui.QCheckBox(self.tab_2)
        self.change_form_check_box.setGeometry(QtCore.QRect(91, 223, 110, 17))
        self.change_form_check_box.setObjectName(_fromUtf8("change_form_check_box"))
        self.right_type_change_cbox = QtGui.QComboBox(self.tab_2)
        self.right_type_change_cbox.setEnabled(False)
        self.right_type_change_cbox.setGeometry(QtCore.QRect(480, 221, 200, 22))
        self.right_type_change_cbox.setObjectName(_fromUtf8("right_type_change_cbox"))
        self.current_process_type_cbox = QtGui.QComboBox(self.tab_2)
        self.current_process_type_cbox.setEnabled(True)
        self.current_process_type_cbox.setGeometry(QtCore.QRect(206, 246, 474, 22))
        self.current_process_type_cbox.setObjectName(_fromUtf8("current_process_type_cbox"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.label_13 = QtGui.QLabel(self.tab_3)
        self.label_13.setGeometry(QtCore.QRect(7, 8, 80, 16))
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.cadastre_right_type_cbox = QtGui.QComboBox(self.tab_3)
        self.cadastre_right_type_cbox.setGeometry(QtCore.QRect(90, 5, 251, 22))
        self.cadastre_right_type_cbox.setObjectName(_fromUtf8("cadastre_right_type_cbox"))
        self.label_14 = QtGui.QLabel(self.tab_3)
        self.label_14.setGeometry(QtCore.QRect(350, 8, 80, 16))
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.land_use_type_cbox = QtGui.QComboBox(self.tab_3)
        self.land_use_type_cbox.setGeometry(QtCore.QRect(429, 5, 331, 22))
        self.land_use_type_cbox.setObjectName(_fromUtf8("land_use_type_cbox"))
        self.label_84 = QtGui.QLabel(self.tab_3)
        self.label_84.setGeometry(QtCore.QRect(430, 34, 81, 16))
        self.label_84.setObjectName(_fromUtf8("label_84"))
        self.label_25 = QtGui.QLabel(self.tab_3)
        self.label_25.setGeometry(QtCore.QRect(270, 31, 150, 17))
        self.label_25.setObjectName(_fromUtf8("label_25"))
        self.parcel_khashaa_edit = QtGui.QLineEdit(self.tab_3)
        self.parcel_khashaa_edit.setGeometry(QtCore.QRect(430, 50, 75, 20))
        self.parcel_khashaa_edit.setObjectName(_fromUtf8("parcel_khashaa_edit"))
        self.parcel_streetname_edit = QtGui.QLineEdit(self.tab_3)
        self.parcel_streetname_edit.setGeometry(QtCore.QRect(516, 50, 160, 20))
        self.parcel_streetname_edit.setObjectName(_fromUtf8("parcel_streetname_edit"))
        self.label_83 = QtGui.QLabel(self.tab_3)
        self.label_83.setGeometry(QtCore.QRect(515, 31, 150, 17))
        self.label_83.setObjectName(_fromUtf8("label_83"))
        self.parcel_right_holder_name_edit = QtGui.QLineEdit(self.tab_3)
        self.parcel_right_holder_name_edit.setGeometry(QtCore.QRect(270, 50, 150, 20))
        self.parcel_right_holder_name_edit.setObjectName(_fromUtf8("parcel_right_holder_name_edit"))
        self.personal_parcel_edit = QtGui.QLineEdit(self.tab_3)
        self.personal_parcel_edit.setGeometry(QtCore.QRect(140, 50, 120, 20))
        self.personal_parcel_edit.setObjectName(_fromUtf8("personal_parcel_edit"))
        self.label_70 = QtGui.QLabel(self.tab_3)
        self.label_70.setGeometry(QtCore.QRect(140, 34, 120, 11))
        self.label_70.setObjectName(_fromUtf8("label_70"))
        self.parcel_num_edit = QtGui.QLineEdit(self.tab_3)
        self.parcel_num_edit.setGeometry(QtCore.QRect(10, 50, 120, 20))
        self.parcel_num_edit.setObjectName(_fromUtf8("parcel_num_edit"))
        self.label_22 = QtGui.QLabel(self.tab_3)
        self.label_22.setGeometry(QtCore.QRect(10, 31, 120, 17))
        self.label_22.setObjectName(_fromUtf8("label_22"))
        self.cadastre_form_change_button = QtGui.QPushButton(self.tab_3)
        self.cadastre_form_change_button.setEnabled(False)
        self.cadastre_form_change_button.setGeometry(QtCore.QRect(686, 239, 75, 23))
        self.cadastre_form_change_button.setObjectName(_fromUtf8("cadastre_form_change_button"))
        self.cad_add_button = QtGui.QPushButton(self.tab_3)
        self.cad_add_button.setGeometry(QtCore.QRect(10, 213, 30, 25))
        self.cad_add_button.setText(_fromUtf8(""))
        self.cad_add_button.setIcon(icon2)
        self.cad_add_button.setObjectName(_fromUtf8("cad_add_button"))
        self.cadastre_change_form_check_box = QtGui.QCheckBox(self.tab_3)
        self.cadastre_change_form_check_box.setGeometry(QtCore.QRect(91, 217, 110, 17))
        self.cadastre_change_form_check_box.setObjectName(_fromUtf8("cadastre_change_form_check_box"))
        self.cadastre_current_twidget = QtGui.QTableWidget(self.tab_3)
        self.cadastre_current_twidget.setGeometry(QtCore.QRect(10, 266, 751, 140))
        self.cadastre_current_twidget.setObjectName(_fromUtf8("cadastre_current_twidget"))
        self.cadastre_current_twidget.setColumnCount(4)
        self.cadastre_current_twidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.cadastre_current_twidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.cadastre_current_twidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.cadastre_current_twidget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.cadastre_current_twidget.setHorizontalHeaderItem(3, item)
        self.cadastre_current_twidget.horizontalHeader().setDefaultSectionSize(200)
        self.cadastre_current_twidget.horizontalHeader().setMinimumSectionSize(35)
        self.cadastre_current_twidget.verticalHeader().setDefaultSectionSize(30)
        self.cadastre_current_twidget.verticalHeader().setMinimumSectionSize(19)
        self.cadastre_form_type_change_cbox = QtGui.QComboBox(self.tab_3)
        self.cadastre_form_type_change_cbox.setEnabled(False)
        self.cadastre_form_type_change_cbox.setGeometry(QtCore.QRect(206, 215, 261, 22))
        self.cadastre_form_type_change_cbox.setObjectName(_fromUtf8("cadastre_form_type_change_cbox"))
        self.cad_remove_button = QtGui.QPushButton(self.tab_3)
        self.cad_remove_button.setGeometry(QtCore.QRect(50, 213, 30, 25))
        self.cad_remove_button.setText(_fromUtf8(""))
        self.cad_remove_button.setIcon(icon3)
        self.cad_remove_button.setObjectName(_fromUtf8("cad_remove_button"))
        self.cadastre_twidget = QtGui.QTableWidget(self.tab_3)
        self.cadastre_twidget.setGeometry(QtCore.QRect(10, 74, 751, 135))
        self.cadastre_twidget.setObjectName(_fromUtf8("cadastre_twidget"))
        self.cadastre_twidget.setColumnCount(0)
        self.cadastre_twidget.setRowCount(0)
        self.cadastre_twidget.horizontalHeader().setDefaultSectionSize(370)
        self.cadastre_twidget.horizontalHeader().setMinimumSectionSize(35)
        self.cadastre_find_button = QtGui.QPushButton(self.tab_3)
        self.cadastre_find_button.setGeometry(QtCore.QRect(686, 49, 75, 23))
        self.cadastre_find_button.setObjectName(_fromUtf8("cadastre_find_button"))
        self.cadastre_right_type_change_cbox = QtGui.QComboBox(self.tab_3)
        self.cadastre_right_type_change_cbox.setEnabled(False)
        self.cadastre_right_type_change_cbox.setGeometry(QtCore.QRect(480, 215, 200, 22))
        self.cadastre_right_type_change_cbox.setObjectName(_fromUtf8("cadastre_right_type_change_cbox"))
        self.cad_process_type_cbox = QtGui.QComboBox(self.tab_3)
        self.cad_process_type_cbox.setEnabled(True)
        self.cad_process_type_cbox.setGeometry(QtCore.QRect(206, 240, 474, 22))
        self.cad_process_type_cbox.setObjectName(_fromUtf8("cad_process_type_cbox"))
        self.cadastre_all_check_box = QtGui.QCheckBox(self.tab_3)
        self.cadastre_all_check_box.setGeometry(QtCore.QRect(12, 244, 110, 17))
        self.cadastre_all_check_box.setObjectName(_fromUtf8("cadastre_all_check_box"))
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName(_fromUtf8("tab_4"))
        self.monitoring_twidget = QtGui.QTableWidget(self.tab_4)
        self.monitoring_twidget.setGeometry(QtCore.QRect(10, 30, 751, 141))
        self.monitoring_twidget.setObjectName(_fromUtf8("monitoring_twidget"))
        self.monitoring_twidget.setColumnCount(2)
        self.monitoring_twidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.monitoring_twidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.monitoring_twidget.setHorizontalHeaderItem(1, item)
        self.monitoring_twidget.horizontalHeader().setDefaultSectionSize(370)
        self.monitoring_remove_button = QtGui.QPushButton(self.tab_4)
        self.monitoring_remove_button.setGeometry(QtCore.QRect(49, 174, 30, 25))
        self.monitoring_remove_button.setText(_fromUtf8(""))
        self.monitoring_remove_button.setIcon(icon3)
        self.monitoring_remove_button.setObjectName(_fromUtf8("monitoring_remove_button"))
        self.monitoring_add_button = QtGui.QPushButton(self.tab_4)
        self.monitoring_add_button.setGeometry(QtCore.QRect(9, 174, 30, 25))
        self.monitoring_add_button.setText(_fromUtf8(""))
        self.monitoring_add_button.setIcon(icon2)
        self.monitoring_add_button.setObjectName(_fromUtf8("monitoring_add_button"))
        self.monitoring_right_type_change_cbox = QtGui.QComboBox(self.tab_4)
        self.monitoring_right_type_change_cbox.setEnabled(False)
        self.monitoring_right_type_change_cbox.setGeometry(QtCore.QRect(479, 176, 200, 22))
        self.monitoring_right_type_change_cbox.setObjectName(_fromUtf8("monitoring_right_type_change_cbox"))
        self.monitoring_form_type_change_cbox = QtGui.QComboBox(self.tab_4)
        self.monitoring_form_type_change_cbox.setEnabled(False)
        self.monitoring_form_type_change_cbox.setGeometry(QtCore.QRect(205, 176, 261, 22))
        self.monitoring_form_type_change_cbox.setObjectName(_fromUtf8("monitoring_form_type_change_cbox"))
        self.monitoring_change_form_check_box = QtGui.QCheckBox(self.tab_4)
        self.monitoring_change_form_check_box.setGeometry(QtCore.QRect(90, 178, 110, 17))
        self.monitoring_change_form_check_box.setObjectName(_fromUtf8("monitoring_change_form_check_box"))
        self.monitoring_process_type_cbox = QtGui.QComboBox(self.tab_4)
        self.monitoring_process_type_cbox.setEnabled(True)
        self.monitoring_process_type_cbox.setGeometry(QtCore.QRect(205, 201, 474, 22))
        self.monitoring_process_type_cbox.setObjectName(_fromUtf8("monitoring_process_type_cbox"))
        self.monitoring_form_change_button = QtGui.QPushButton(self.tab_4)
        self.monitoring_form_change_button.setEnabled(False)
        self.monitoring_form_change_button.setGeometry(QtCore.QRect(685, 200, 75, 23))
        self.monitoring_form_change_button.setObjectName(_fromUtf8("monitoring_form_change_button"))
        self.monitoring_current_twidget = QtGui.QTableWidget(self.tab_4)
        self.monitoring_current_twidget.setGeometry(QtCore.QRect(10, 230, 751, 140))
        self.monitoring_current_twidget.setObjectName(_fromUtf8("monitoring_current_twidget"))
        self.monitoring_current_twidget.setColumnCount(4)
        self.monitoring_current_twidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.monitoring_current_twidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.monitoring_current_twidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.monitoring_current_twidget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.monitoring_current_twidget.setHorizontalHeaderItem(3, item)
        self.monitoring_current_twidget.horizontalHeader().setDefaultSectionSize(200)
        self.monitoring_current_twidget.horizontalHeader().setMinimumSectionSize(35)
        self.monitoring_current_twidget.verticalHeader().setDefaultSectionSize(30)
        self.monitoring_current_twidget.verticalHeader().setMinimumSectionSize(19)
        self.land_use_type_cbox_2 = QtGui.QComboBox(self.tab_4)
        self.land_use_type_cbox_2.setGeometry(QtCore.QRect(473, 3, 141, 22))
        self.land_use_type_cbox_2.setObjectName(_fromUtf8("land_use_type_cbox_2"))
        self.label_15 = QtGui.QLabel(self.tab_4)
        self.label_15.setGeometry(QtCore.QRect(110, 6, 80, 16))
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.label_16 = QtGui.QLabel(self.tab_4)
        self.label_16.setGeometry(QtCore.QRect(383, 6, 80, 16))
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.cadastre_right_type_cbox_2 = QtGui.QComboBox(self.tab_4)
        self.cadastre_right_type_cbox_2.setGeometry(QtCore.QRect(193, 3, 151, 22))
        self.cadastre_right_type_cbox_2.setObjectName(_fromUtf8("cadastre_right_type_cbox_2"))
        self.monitoring_find_button = QtGui.QPushButton(self.tab_4)
        self.monitoring_find_button.setGeometry(QtCore.QRect(690, 2, 75, 23))
        self.monitoring_find_button.setObjectName(_fromUtf8("monitoring_find_button"))
        self.monitoring_year_sbox = QtGui.QSpinBox(self.tab_4)
        self.monitoring_year_sbox.setGeometry(QtCore.QRect(10, 3, 87, 22))
        self.monitoring_year_sbox.setMinimum(2003)
        self.monitoring_year_sbox.setMaximum(9999)
        self.monitoring_year_sbox.setProperty("value", 2019)
        self.monitoring_year_sbox.setObjectName(_fromUtf8("monitoring_year_sbox"))
        self.tabWidget.addTab(self.tab_4, _fromUtf8(""))
        self.status_label = QtGui.QLabel(PlanCaseDialog)
        self.status_label.setGeometry(QtCore.QRect(10, 510, 399, 16))
        self.status_label.setText(_fromUtf8(""))
        self.status_label.setObjectName(_fromUtf8("status_label"))
        self.main_load_pbar = QtGui.QProgressBar(PlanCaseDialog)
        self.main_load_pbar.setGeometry(QtCore.QRect(520, 538, 261, 14))
        self.main_load_pbar.setProperty("value", 0)
        self.main_load_pbar.setTextDirection(QtGui.QProgressBar.TopToBottom)
        self.main_load_pbar.setObjectName(_fromUtf8("main_load_pbar"))
        self.error_label = QtGui.QLabel(PlanCaseDialog)
        self.error_label.setGeometry(QtCore.QRect(10, 538, 501, 16))
        self.error_label.setText(_fromUtf8(""))
        self.error_label.setObjectName(_fromUtf8("error_label"))

        self.retranslateUi(PlanCaseDialog)
        self.tabWidget.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(PlanCaseDialog)

    def retranslateUi(self, PlanCaseDialog):
        PlanCaseDialog.setWindowTitle(_translate("PlanCaseDialog", "Dialog", None))
        self.groupBox.setTitle(_translate("PlanCaseDialog", "General information", None))
        self.label_2.setText(_translate("PlanCaseDialog", "Date & Number", None))
        self.label_3.setText(_translate("PlanCaseDialog", "Type", None))
        self.label_4.setText(_translate("PlanCaseDialog", "Status", None))
        self.close_button.setText(_translate("PlanCaseDialog", "Close", None))
        self.apply_button.setText(_translate("PlanCaseDialog", "Apply", None))
        self.result_twidget.headerItem().setText(0, _translate("PlanCaseDialog", "Maintenance Case Objects", None))
        self.import_groupbox.setTitle(_translate("PlanCaseDialog", "Import", None))
        self.label.setText(_translate("PlanCaseDialog", "Parcel Shapefile", None))
        self.point_rbutton.setText(_translate("PlanCaseDialog", "Point", None))
        self.line_rbutton.setText(_translate("PlanCaseDialog", "Line", None))
        self.polygon_rbutton.setText(_translate("PlanCaseDialog", "Polygon", None))
        self.if_single_type_chbox.setText(_translate("PlanCaseDialog", "Зөвхөн нэг арга хэмжээгээр оруулах", None))
        self.default_plan_zone_chbox.setText(_translate("PlanCaseDialog", "Үндсэн тохиргооноос авах", None))
        self.label_6.setText(_translate("PlanCaseDialog", "Арга хэмжээний төрөл", None))
        self.label_7.setText(_translate("PlanCaseDialog", "Эрхийн төрөл", None))
        self.message_label.setText(_translate("PlanCaseDialog", "Message Information", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("PlanCaseDialog", "New Parcel Import", None))
        self.main_tree_widget.setSortingEnabled(True)
        self.main_tree_widget.headerItem().setText(0, _translate("PlanCaseDialog", "Үр дүн", None))
        self.label_10.setText(_translate("PlanCaseDialog", "Zone Type", None))
        self.label_5.setText(_translate("PlanCaseDialog", "Process Type", None))
        self.label_11.setText(_translate("PlanCaseDialog", "Plan", None))
        self.find_button.setText(_translate("PlanCaseDialog", "Find", None))
        self.current_tree_widget.setSortingEnabled(True)
        self.current_tree_widget.headerItem().setText(0, _translate("PlanCaseDialog", "ГЗБТ-ны үйл ажиллагаа", None))
        self.current_tree_widget.headerItem().setText(1, _translate("PlanCaseDialog", "Үйл ажиллагааны төрөл", None))
        self.current_tree_widget.headerItem().setText(2, _translate("PlanCaseDialog", "Эрхийн төрөл", None))
        self.current_tree_widget.headerItem().setText(3, _translate("PlanCaseDialog", "Хаанаас авсан", None))
        self.label_12.setText(_translate("PlanCaseDialog", "Form Type", None))
        self.form_change_button.setText(_translate("PlanCaseDialog", "Change", None))
        self.change_form_check_box.setText(_translate("PlanCaseDialog", "Change right form", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("PlanCaseDialog", "Other Plan Import", None))
        self.label_13.setText(_translate("PlanCaseDialog", "Right Type", None))
        self.label_14.setText(_translate("PlanCaseDialog", "Land Use", None))
        self.label_84.setText(_translate("PlanCaseDialog", "Khashaa", None))
        self.label_25.setText(_translate("PlanCaseDialog", "Right Holder Name", None))
        self.label_83.setText(_translate("PlanCaseDialog", "Street Name", None))
        self.label_70.setText(_translate("PlanCaseDialog", "Personal / Company ID", None))
        self.label_22.setText(_translate("PlanCaseDialog", "Parcel Number", None))
        self.cadastre_form_change_button.setText(_translate("PlanCaseDialog", "Change", None))
        self.cadastre_change_form_check_box.setText(_translate("PlanCaseDialog", "Change right form", None))
        self.cadastre_current_twidget.setSortingEnabled(True)
        item = self.cadastre_current_twidget.horizontalHeaderItem(0)
        item.setText(_translate("PlanCaseDialog", "Cadastre Parcel Information", None))
        item = self.cadastre_current_twidget.horizontalHeaderItem(1)
        item.setText(_translate("PlanCaseDialog", "Zone Type", None))
        item = self.cadastre_current_twidget.horizontalHeaderItem(2)
        item.setText(_translate("PlanCaseDialog", "Form Type", None))
        item = self.cadastre_current_twidget.horizontalHeaderItem(3)
        item.setText(_translate("PlanCaseDialog", "Right Type", None))
        self.cadastre_find_button.setText(_translate("PlanCaseDialog", "Find", None))
        self.cadastre_all_check_box.setText(_translate("PlanCaseDialog", "Бүгдийг сонгох", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("PlanCaseDialog", "Import Cadastre", None))
        item = self.monitoring_twidget.horizontalHeaderItem(0)
        item.setText(_translate("PlanCaseDialog", "Бэлчээрийн мэдээлэл", None))
        item = self.monitoring_twidget.horizontalHeaderItem(1)
        item.setText(_translate("PlanCaseDialog", "Төлөв байдлын мэдээлэл", None))
        self.monitoring_change_form_check_box.setText(_translate("PlanCaseDialog", "Change right form", None))
        self.monitoring_form_change_button.setText(_translate("PlanCaseDialog", "Change", None))
        self.monitoring_current_twidget.setSortingEnabled(True)
        item = self.monitoring_current_twidget.horizontalHeaderItem(0)
        item.setText(_translate("PlanCaseDialog", "Cadastre Parcel Information", None))
        item = self.monitoring_current_twidget.horizontalHeaderItem(1)
        item.setText(_translate("PlanCaseDialog", "Zone Type", None))
        item = self.monitoring_current_twidget.horizontalHeaderItem(2)
        item.setText(_translate("PlanCaseDialog", "Form Type", None))
        item = self.monitoring_current_twidget.horizontalHeaderItem(3)
        item.setText(_translate("PlanCaseDialog", "Right Type", None))
        self.label_15.setText(_translate("PlanCaseDialog", "Баг", None))
        self.label_16.setText(_translate("PlanCaseDialog", "Улирал", None))
        self.monitoring_find_button.setText(_translate("PlanCaseDialog", "Find", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("PlanCaseDialog", "Import From Monitoring", None))

import resources_rc
