# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\AddressNavigatorWidget.ui'
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

class Ui_AddressNavigatorWidget(object):
    def setupUi(self, AddressNavigatorWidget):
        AddressNavigatorWidget.setObjectName(_fromUtf8("AddressNavigatorWidget"))
        AddressNavigatorWidget.resize(500, 758)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AddressNavigatorWidget.sizePolicy().hasHeightForWidth())
        AddressNavigatorWidget.setSizePolicy(sizePolicy)
        AddressNavigatorWidget.setMinimumSize(QtCore.QSize(500, 620))
        AddressNavigatorWidget.setMaximumSize(QtCore.QSize(500, 524287))
        AddressNavigatorWidget.setBaseSize(QtCore.QSize(440, 665))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.scrollArea = QtGui.QScrollArea(self.dockWidgetContents)
        self.scrollArea.setGeometry(QtCore.QRect(1, 0, 498, 700))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QtCore.QSize(0, 650))
        self.scrollArea.setMaximumSize(QtCore.QSize(500, 700))
        self.scrollArea.setWidgetResizable(False)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 500, 750))
        self.scrollAreaWidgetContents.setMinimumSize(QtCore.QSize(0, 650))
        self.scrollAreaWidgetContents.setMaximumSize(QtCore.QSize(16777215, 800))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.working_l1_cbox = QtGui.QComboBox(self.scrollAreaWidgetContents)
        self.working_l1_cbox.setGeometry(QtCore.QRect(4, 4, 170, 22))
        self.working_l1_cbox.setObjectName(_fromUtf8("working_l1_cbox"))
        self.working_l2_cbox = QtGui.QComboBox(self.scrollAreaWidgetContents)
        self.working_l2_cbox.setGeometry(QtCore.QRect(184, 4, 170, 22))
        self.working_l2_cbox.setObjectName(_fromUtf8("working_l2_cbox"))
        self.tabWidget = QtGui.QTabWidget(self.scrollAreaWidgetContents)
        self.tabWidget.setGeometry(QtCore.QRect(6, 34, 466, 631))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.selected_parcel_load_button = QtGui.QPushButton(self.tab_2)
        self.selected_parcel_load_button.setGeometry(QtCore.QRect(9, 50, 221, 23))
        self.selected_parcel_load_button.setObjectName(_fromUtf8("selected_parcel_load_button"))
        self.geographic_name_edit = QtGui.QLineEdit(self.tab_2)
        self.geographic_name_edit.setGeometry(QtCore.QRect(10, 290, 441, 20))
        self.geographic_name_edit.setObjectName(_fromUtf8("geographic_name_edit"))
        self.label = QtGui.QLabel(self.tab_2)
        self.label.setGeometry(QtCore.QRect(10, 273, 74, 13))
        self.label.setObjectName(_fromUtf8("label"))
        self.khashaa_no_edit = QtGui.QLineEdit(self.tab_2)
        self.khashaa_no_edit.setGeometry(QtCore.QRect(10, 412, 441, 20))
        self.khashaa_no_edit.setObjectName(_fromUtf8("khashaa_no_edit"))
        self.label_2 = QtGui.QLabel(self.tab_2)
        self.label_2.setGeometry(QtCore.QRect(10, 395, 85, 13))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(self.tab_2)
        self.label_3.setGeometry(QtCore.QRect(10, 321, 74, 13))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.streets_cbox = QtGui.QComboBox(self.tab_2)
        self.streets_cbox.setGeometry(QtCore.QRect(10, 340, 387, 22))
        self.streets_cbox.setObjectName(_fromUtf8("streets_cbox"))
        self.str_count_sbox = QtGui.QSpinBox(self.tab_2)
        self.str_count_sbox.setGeometry(QtCore.QRect(403, 340, 48, 22))
        self.str_count_sbox.setProperty("value", 2)
        self.str_count_sbox.setObjectName(_fromUtf8("str_count_sbox"))
        self.layer_type_cbox = QtGui.QComboBox(self.tab_2)
        self.layer_type_cbox.setGeometry(QtCore.QRect(10, 20, 281, 22))
        self.layer_type_cbox.setObjectName(_fromUtf8("layer_type_cbox"))
        self.get_address_button = QtGui.QPushButton(self.tab_2)
        self.get_address_button.setGeometry(QtCore.QRect(10, 442, 283, 23))
        self.get_address_button.setObjectName(_fromUtf8("get_address_button"))
        self.address_parcel_twidget = QtGui.QTableWidget(self.tab_2)
        self.address_parcel_twidget.setGeometry(QtCore.QRect(10, 80, 441, 141))
        self.address_parcel_twidget.setObjectName(_fromUtf8("address_parcel_twidget"))
        self.address_parcel_twidget.setColumnCount(3)
        self.address_parcel_twidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.address_parcel_twidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.address_parcel_twidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.address_parcel_twidget.setHorizontalHeaderItem(2, item)
        self.address_parcel_twidget.horizontalHeader().setDefaultSectionSize(140)
        self.apply_address_button = QtGui.QPushButton(self.tab_2)
        self.apply_address_button.setGeometry(QtCore.QRect(10, 510, 283, 23))
        self.apply_address_button.setObjectName(_fromUtf8("apply_address_button"))
        self.selected_parcel_remove_button = QtGui.QPushButton(self.tab_2)
        self.selected_parcel_remove_button.setGeometry(QtCore.QRect(250, 50, 201, 23))
        self.selected_parcel_remove_button.setObjectName(_fromUtf8("selected_parcel_remove_button"))
        self.str_txt_lbl = QtGui.QLabel(self.tab_2)
        self.str_txt_lbl.setGeometry(QtCore.QRect(10, 381, 441, 16))
        font = QtGui.QFont()
        font.setPointSize(6)
        font.setBold(True)
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.str_txt_lbl.setFont(font)
        self.str_txt_lbl.setText(_fromUtf8(""))
        self.str_txt_lbl.setObjectName(_fromUtf8("str_txt_lbl"))
        self.str_txt_lbl_2 = QtGui.QLabel(self.tab_2)
        self.str_txt_lbl_2.setGeometry(QtCore.QRect(10, 370, 90, 13))
        self.str_txt_lbl_2.setObjectName(_fromUtf8("str_txt_lbl_2"))
        self.str_type_lbl = QtGui.QLabel(self.tab_2)
        self.str_type_lbl.setGeometry(QtCore.QRect(110, 369, 341, 16))
        self.str_type_lbl.setText(_fromUtf8(""))
        self.str_type_lbl.setObjectName(_fromUtf8("str_type_lbl"))
        self.address_layer_button = QtGui.QPushButton(self.tab_2)
        self.address_layer_button.setGeometry(QtCore.QRect(10, 570, 283, 23))
        self.address_layer_button.setObjectName(_fromUtf8("address_layer_button"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.selected_str_load_button = QtGui.QPushButton(self.tab)
        self.selected_str_load_button.setGeometry(QtCore.QRect(10, 20, 281, 23))
        self.selected_str_load_button.setObjectName(_fromUtf8("selected_str_load_button"))
        self.tabWidget_2 = QtGui.QTabWidget(self.tab)
        self.tabWidget_2.setGeometry(QtCore.QRect(10, 70, 441, 531))
        self.tabWidget_2.setObjectName(_fromUtf8("tabWidget_2"))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.str_nodes_twidget = QtGui.QTableWidget(self.tab_3)
        self.str_nodes_twidget.setGeometry(QtCore.QRect(10, 10, 411, 221))
        self.str_nodes_twidget.setObjectName(_fromUtf8("str_nodes_twidget"))
        self.str_nodes_twidget.setColumnCount(3)
        self.str_nodes_twidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.str_nodes_twidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.str_nodes_twidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.str_nodes_twidget.setHorizontalHeaderItem(2, item)
        self.str_nodes_twidget.horizontalHeader().setDefaultSectionSize(133)
        self.apply_button = QtGui.QPushButton(self.tab_3)
        self.apply_button.setGeometry(QtCore.QRect(10, 250, 75, 23))
        self.apply_button.setObjectName(_fromUtf8("apply_button"))
        self.tabWidget_2.addTab(self.tab_3, _fromUtf8(""))
        self.tab_5 = QtGui.QWidget()
        self.tab_5.setObjectName(_fromUtf8("tab_5"))
        self.tabWidget_2.addTab(self.tab_5, _fromUtf8(""))
        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName(_fromUtf8("tab_4"))
        self.tabWidget_2.addTab(self.tab_4, _fromUtf8(""))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        AddressNavigatorWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(AddressNavigatorWidget)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(AddressNavigatorWidget)

    def retranslateUi(self, AddressNavigatorWidget):
        AddressNavigatorWidget.setWindowTitle(_translate("AddressNavigatorWidget", "Selection / Filter", None))
        self.selected_parcel_load_button.setText(_translate("AddressNavigatorWidget", "Хаягийн мэдээллийн санд оруулах", None))
        self.label.setText(_translate("AddressNavigatorWidget", "Газар зүйн нэр", None))
        self.label_2.setText(_translate("AddressNavigatorWidget", "Хашааны дугаар", None))
        self.label_3.setText(_translate("AddressNavigatorWidget", "Гудамж", None))
        self.get_address_button.setText(_translate("AddressNavigatorWidget", "Хаяг авах", None))
        item = self.address_parcel_twidget.horizontalHeaderItem(0)
        item.setText(_translate("AddressNavigatorWidget", "Нэгж талбарын дугаар", None))
        item = self.address_parcel_twidget.horizontalHeaderItem(1)
        item.setText(_translate("AddressNavigatorWidget", "Давхаргын төрөл", None))
        item = self.address_parcel_twidget.horizontalHeaderItem(2)
        item.setText(_translate("AddressNavigatorWidget", "Хаягийн төлөв", None))
        self.apply_address_button.setText(_translate("AddressNavigatorWidget", "Хадгалах", None))
        self.selected_parcel_remove_button.setText(_translate("AddressNavigatorWidget", "Хаягийн мэдээллийн сангаас хасах", None))
        self.str_txt_lbl_2.setText(_translate("AddressNavigatorWidget", "Гудамжны төрөл:", None))
        self.address_layer_button.setText(_translate("AddressNavigatorWidget", "Давхарга", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("AddressNavigatorWidget", "Нэгж талбар", None))
        self.selected_str_load_button.setText(_translate("AddressNavigatorWidget", "Гудамжны мэдээлэл харах", None))
        item = self.str_nodes_twidget.horizontalHeaderItem(0)
        item.setText(_translate("AddressNavigatorWidget", "ID", None))
        item = self.str_nodes_twidget.horizontalHeaderItem(1)
        item.setText(_translate("AddressNavigatorWidget", "X", None))
        item = self.str_nodes_twidget.horizontalHeaderItem(2)
        item.setText(_translate("AddressNavigatorWidget", "Y", None))
        self.apply_button.setText(_translate("AddressNavigatorWidget", "Apply", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_3), _translate("AddressNavigatorWidget", "Эхлэлийн Цэг", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_5), _translate("AddressNavigatorWidget", "Хамаарах Зам", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_4), _translate("AddressNavigatorWidget", "Хавсралт Материал", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("AddressNavigatorWidget", "Гудамж", None))

