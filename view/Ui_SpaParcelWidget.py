# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\SpaParcelWidget.ui'
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

class Ui_SpaParcelWidget(object):
    def setupUi(self, SpaParcelWidget):
        SpaParcelWidget.setObjectName(_fromUtf8("SpaParcelWidget"))
        SpaParcelWidget.resize(415, 711)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SpaParcelWidget.sizePolicy().hasHeightForWidth())
        SpaParcelWidget.setSizePolicy(sizePolicy)
        SpaParcelWidget.setMinimumSize(QtCore.QSize(415, 620))
        SpaParcelWidget.setMaximumSize(QtCore.QSize(415, 524287))
        SpaParcelWidget.setBaseSize(QtCore.QSize(415, 665))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.scrollArea = QtGui.QScrollArea(self.dockWidgetContents)
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, 411, 650))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QtCore.QSize(0, 550))
        self.scrollArea.setMaximumSize(QtCore.QSize(435, 650))
        self.scrollArea.setWidgetResizable(False)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 419, 664))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.tabWidget = QtGui.QTabWidget(self.scrollAreaWidgetContents)
        self.tabWidget.setGeometry(QtCore.QRect(10, 60, 386, 600))
        self.tabWidget.setMaximumSize(QtCore.QSize(16777215, 600))
        self.tabWidget.setUsesScrollButtons(True)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.pasture_tab = QtGui.QWidget()
        self.pasture_tab.setObjectName(_fromUtf8("pasture_tab"))
        self.groupBox_18 = QtGui.QGroupBox(self.pasture_tab)
        self.groupBox_18.setGeometry(QtCore.QRect(5, 30, 371, 277))
        self.groupBox_18.setAutoFillBackground(False)
        self.groupBox_18.setObjectName(_fromUtf8("groupBox_18"))
        self.pasture_parcel_id_edit = QtGui.QLineEdit(self.groupBox_18)
        self.pasture_parcel_id_edit.setGeometry(QtCore.QRect(190, 29, 170, 20))
        self.pasture_parcel_id_edit.setObjectName(_fromUtf8("pasture_parcel_id_edit"))
        self.member_name_edit = QtGui.QLineEdit(self.groupBox_18)
        self.member_name_edit.setGeometry(QtCore.QRect(10, 188, 170, 20))
        self.member_name_edit.setObjectName(_fromUtf8("member_name_edit"))
        self.member_register_edit = QtGui.QLineEdit(self.groupBox_18)
        self.member_register_edit.setGeometry(QtCore.QRect(10, 150, 170, 20))
        self.member_register_edit.setObjectName(_fromUtf8("member_register_edit"))
        self.pasture_contract_no_edit = QtGui.QLineEdit(self.groupBox_18)
        self.pasture_contract_no_edit.setGeometry(QtCore.QRect(190, 188, 170, 20))
        self.pasture_contract_no_edit.setObjectName(_fromUtf8("pasture_contract_no_edit"))
        self.pasture_app_no_edit = QtGui.QLineEdit(self.groupBox_18)
        self.pasture_app_no_edit.setGeometry(QtCore.QRect(190, 150, 170, 20))
        self.pasture_app_no_edit.setObjectName(_fromUtf8("pasture_app_no_edit"))
        self.label_62 = QtGui.QLabel(self.groupBox_18)
        self.label_62.setGeometry(QtCore.QRect(190, 11, 170, 16))
        self.label_62.setObjectName(_fromUtf8("label_62"))
        self.label_64 = QtGui.QLabel(self.groupBox_18)
        self.label_64.setGeometry(QtCore.QRect(10, 171, 170, 17))
        self.label_64.setObjectName(_fromUtf8("label_64"))
        self.label_65 = QtGui.QLabel(self.groupBox_18)
        self.label_65.setGeometry(QtCore.QRect(10, 132, 170, 17))
        self.label_65.setObjectName(_fromUtf8("label_65"))
        self.label_66 = QtGui.QLabel(self.groupBox_18)
        self.label_66.setGeometry(QtCore.QRect(190, 132, 170, 17))
        self.label_66.setObjectName(_fromUtf8("label_66"))
        self.label_67 = QtGui.QLabel(self.groupBox_18)
        self.label_67.setGeometry(QtCore.QRect(190, 171, 170, 17))
        self.label_67.setObjectName(_fromUtf8("label_67"))
        self.pasture_app_date_edit = QtGui.QDateEdit(self.groupBox_18)
        self.pasture_app_date_edit.setEnabled(False)
        self.pasture_app_date_edit.setGeometry(QtCore.QRect(190, 215, 91, 21))
        self.pasture_app_date_edit.setCalendarPopup(True)
        self.pasture_app_date_edit.setObjectName(_fromUtf8("pasture_app_date_edit"))
        self.pasture_clear_button = QtGui.QPushButton(self.groupBox_18)
        self.pasture_clear_button.setGeometry(QtCore.QRect(210, 245, 75, 23))
        self.pasture_clear_button.setObjectName(_fromUtf8("pasture_clear_button"))
        self.pasture_find_button = QtGui.QPushButton(self.groupBox_18)
        self.pasture_find_button.setGeometry(QtCore.QRect(290, 245, 75, 23))
        self.pasture_find_button.setDefault(True)
        self.pasture_find_button.setObjectName(_fromUtf8("pasture_find_button"))
        self.pasture_date_cbox = QtGui.QCheckBox(self.groupBox_18)
        self.pasture_date_cbox.setGeometry(QtCore.QRect(12, 216, 171, 20))
        self.pasture_date_cbox.setObjectName(_fromUtf8("pasture_date_cbox"))
        self.pasture_results_label = QtGui.QLabel(self.groupBox_18)
        self.pasture_results_label.setGeometry(QtCore.QRect(10, 247, 121, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Lucida Grande"))
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.pasture_results_label.setFont(font)
        self.pasture_results_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.pasture_results_label.setObjectName(_fromUtf8("pasture_results_label"))
        self.label_68 = QtGui.QLabel(self.groupBox_18)
        self.label_68.setGeometry(QtCore.QRect(10, 10, 170, 17))
        self.label_68.setObjectName(_fromUtf8("label_68"))
        self.pasture_group_cbox = QtGui.QComboBox(self.groupBox_18)
        self.pasture_group_cbox.setGeometry(QtCore.QRect(10, 28, 171, 22))
        self.pasture_group_cbox.setObjectName(_fromUtf8("pasture_group_cbox"))
        self.label_69 = QtGui.QLabel(self.groupBox_18)
        self.label_69.setGeometry(QtCore.QRect(10, 51, 170, 17))
        self.label_69.setObjectName(_fromUtf8("label_69"))
        self.pasture_landuse_cbox = QtGui.QComboBox(self.groupBox_18)
        self.pasture_landuse_cbox.setGeometry(QtCore.QRect(10, 69, 351, 22))
        self.pasture_landuse_cbox.setObjectName(_fromUtf8("pasture_landuse_cbox"))
        self.app_type_cbox = QtGui.QComboBox(self.groupBox_18)
        self.app_type_cbox.setGeometry(QtCore.QRect(10, 108, 351, 22))
        self.app_type_cbox.setObjectName(_fromUtf8("app_type_cbox"))
        self.label_70 = QtGui.QLabel(self.groupBox_18)
        self.label_70.setGeometry(QtCore.QRect(10, 90, 170, 17))
        self.label_70.setObjectName(_fromUtf8("label_70"))
        self.delete_button = QtGui.QPushButton(self.groupBox_18)
        self.delete_button.setGeometry(QtCore.QRect(130, 245, 75, 23))
        self.delete_button.setObjectName(_fromUtf8("delete_button"))
        self.groupBox_19 = QtGui.QGroupBox(self.pasture_tab)
        self.groupBox_19.setGeometry(QtCore.QRect(6, 305, 371, 241))
        self.groupBox_19.setObjectName(_fromUtf8("groupBox_19"))
        self.pasture_results_twidget = QtGui.QTableWidget(self.groupBox_19)
        self.pasture_results_twidget.setGeometry(QtCore.QRect(5, 20, 361, 155))
        self.pasture_results_twidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.pasture_results_twidget.setObjectName(_fromUtf8("pasture_results_twidget"))
        self.pasture_results_twidget.setColumnCount(0)
        self.pasture_results_twidget.setRowCount(0)
        self.pasture_contract_view_button = QtGui.QPushButton(self.groupBox_19)
        self.pasture_contract_view_button.setGeometry(QtCore.QRect(256, 183, 111, 23))
        self.pasture_contract_view_button.setObjectName(_fromUtf8("pasture_contract_view_button"))
        self.pasture_app_view_button = QtGui.QPushButton(self.groupBox_19)
        self.pasture_app_view_button.setGeometry(QtCore.QRect(130, 183, 121, 23))
        self.pasture_app_view_button.setObjectName(_fromUtf8("pasture_app_view_button"))
        self.pasture_layer_view_button = QtGui.QPushButton(self.groupBox_19)
        self.pasture_layer_view_button.setGeometry(QtCore.QRect(5, 183, 121, 23))
        self.pasture_layer_view_button.setObjectName(_fromUtf8("pasture_layer_view_button"))
        self.error_label = QtGui.QLabel(self.groupBox_19)
        self.error_label.setGeometry(QtCore.QRect(10, 213, 351, 21))
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
        self.pasture_app_add_button = QtGui.QPushButton(self.pasture_tab)
        self.pasture_app_add_button.setGeometry(QtCore.QRect(141, 6, 111, 23))
        self.pasture_app_add_button.setObjectName(_fromUtf8("pasture_app_add_button"))
        self.draft_decision_button = QtGui.QPushButton(self.pasture_tab)
        self.draft_decision_button.setGeometry(QtCore.QRect(265, 6, 111, 23))
        self.draft_decision_button.setObjectName(_fromUtf8("draft_decision_button"))
        self.tabWidget.addTab(self.pasture_tab, _fromUtf8(""))
        self.working_l1_cbox = QtGui.QComboBox(self.scrollAreaWidgetContents)
        self.working_l1_cbox.setGeometry(QtCore.QRect(205, 5, 191, 26))
        self.working_l1_cbox.setObjectName(_fromUtf8("working_l1_cbox"))
        self.working_l2_cbox = QtGui.QComboBox(self.scrollAreaWidgetContents)
        self.working_l2_cbox.setGeometry(QtCore.QRect(205, 30, 191, 26))
        self.working_l2_cbox.setObjectName(_fromUtf8("working_l2_cbox"))
        self.label = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label.setGeometry(QtCore.QRect(20, 10, 186, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_2.setGeometry(QtCore.QRect(20, 35, 191, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        SpaParcelWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(SpaParcelWidget)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(SpaParcelWidget)
        SpaParcelWidget.setTabOrder(self.working_l1_cbox, self.working_l2_cbox)
        SpaParcelWidget.setTabOrder(self.working_l2_cbox, self.tabWidget)
        SpaParcelWidget.setTabOrder(self.tabWidget, self.scrollArea)

    def retranslateUi(self, SpaParcelWidget):
        SpaParcelWidget.setWindowTitle(_translate("SpaParcelWidget", "Selection / Filter", None))
        self.groupBox_18.setTitle(_translate("SpaParcelWidget", "Criteria", None))
        self.label_62.setText(_translate("SpaParcelWidget", "Parcel ID", None))
        self.label_64.setText(_translate("SpaParcelWidget", "Member Name", None))
        self.label_65.setText(_translate("SpaParcelWidget", "Group member register", None))
        self.label_66.setText(_translate("SpaParcelWidget", "Application No", None))
        self.label_67.setText(_translate("SpaParcelWidget", "Contract No", None))
        self.pasture_app_date_edit.setDisplayFormat(_translate("SpaParcelWidget", "yyyy-MM-dd", None))
        self.pasture_clear_button.setText(_translate("SpaParcelWidget", "Clear", None))
        self.pasture_find_button.setText(_translate("SpaParcelWidget", "Find", None))
        self.pasture_date_cbox.setText(_translate("SpaParcelWidget", "Application Date", None))
        self.pasture_results_label.setText(_translate("SpaParcelWidget", "Results:", None))
        self.label_68.setText(_translate("SpaParcelWidget", "Pasture Group", None))
        self.label_69.setText(_translate("SpaParcelWidget", "Land use type", None))
        self.label_70.setText(_translate("SpaParcelWidget", "Application type", None))
        self.delete_button.setText(_translate("SpaParcelWidget", "Delete", None))
        self.groupBox_19.setTitle(_translate("SpaParcelWidget", "Results", None))
        self.pasture_contract_view_button.setText(_translate("SpaParcelWidget", "View Contract", None))
        self.pasture_app_view_button.setText(_translate("SpaParcelWidget", "View App", None))
        self.pasture_layer_view_button.setText(_translate("SpaParcelWidget", "Layer View/ Hide", None))
        self.pasture_app_add_button.setText(_translate("SpaParcelWidget", "Application Add", None))
        self.draft_decision_button.setText(_translate("SpaParcelWidget", "Draft/ Decision", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.pasture_tab), _translate("SpaParcelWidget", "Pasture(PUA)", None))
        self.label.setText(_translate("SpaParcelWidget", "Working Aimag / Duureg", None))
        self.label_2.setText(_translate("SpaParcelWidget", "Working Soum", None))
