# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ParcelInfoFeeDialog.ui'
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

class Ui_ParcelInfoFeeDialog(object):
    def setupUi(self, ParcelInfoFeeDialog):
        ParcelInfoFeeDialog.setObjectName(_fromUtf8("ParcelInfoFeeDialog"))
        ParcelInfoFeeDialog.resize(867, 537)
        self.close_button = QtGui.QPushButton(ParcelInfoFeeDialog)
        self.close_button.setGeometry(QtCore.QRect(779, 510, 75, 23))
        self.close_button.setObjectName(_fromUtf8("close_button"))
        self.tabWidget = QtGui.QTabWidget(ParcelInfoFeeDialog)
        self.tabWidget.setGeometry(QtCore.QRect(4, 2, 861, 503))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.find_gbox = QtGui.QGroupBox(self.tab)
        self.find_gbox.setEnabled(False)
        self.find_gbox.setGeometry(QtCore.QRect(5, 0, 844, 39))
        self.find_gbox.setObjectName(_fromUtf8("find_gbox"))
        self.find_button = QtGui.QPushButton(self.find_gbox)
        self.find_button.setGeometry(QtCore.QRect(530, 10, 75, 23))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/lm2/zoom.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.find_button.setIcon(icon)
        self.find_button.setObjectName(_fromUtf8("find_button"))
        self.old_parcel_id_edit = QtGui.QLineEdit(self.find_gbox)
        self.old_parcel_id_edit.setEnabled(False)
        self.old_parcel_id_edit.setGeometry(QtCore.QRect(360, 11, 151, 20))
        self.old_parcel_id_edit.setObjectName(_fromUtf8("old_parcel_id_edit"))
        self.person_id_edit = QtGui.QLineEdit(self.find_gbox)
        self.person_id_edit.setEnabled(False)
        self.person_id_edit.setGeometry(QtCore.QRect(90, 11, 151, 20))
        self.person_id_edit.setObjectName(_fromUtf8("person_id_edit"))
        self.label_3 = QtGui.QLabel(self.find_gbox)
        self.label_3.setGeometry(QtCore.QRect(10, 13, 81, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(self.find_gbox)
        self.label_4.setGeometry(QtCore.QRect(250, 13, 101, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.clear_button = QtGui.QPushButton(self.tab)
        self.clear_button.setGeometry(QtCore.QRect(630, 10, 75, 23))
        self.clear_button.setObjectName(_fromUtf8("clear_button"))
        self.groupBox_4 = QtGui.QGroupBox(self.tab)
        self.groupBox_4.setGeometry(QtCore.QRect(280, 250, 281, 225))
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.payment_total_sbox = QtGui.QDoubleSpinBox(self.groupBox_4)
        self.payment_total_sbox.setGeometry(QtCore.QRect(150, 125, 121, 22))
        self.payment_total_sbox.setStyleSheet(_fromUtf8("background-color: rgb(0, 170, 255);"))
        self.payment_total_sbox.setObjectName(_fromUtf8("payment_total_sbox"))
        self.label_25 = QtGui.QLabel(self.groupBox_4)
        self.label_25.setGeometry(QtCore.QRect(150, 105, 121, 16))
        self.label_25.setStyleSheet(_fromUtf8("background-color: rgb(0, 170, 255);"))
        self.label_25.setObjectName(_fromUtf8("label_25"))
        self.label_26 = QtGui.QLabel(self.groupBox_4)
        self.label_26.setGeometry(QtCore.QRect(10, 15, 97, 13))
        self.label_26.setObjectName(_fromUtf8("label_26"))
        self.payment_contract_sbox = QtGui.QDoubleSpinBox(self.groupBox_4)
        self.payment_contract_sbox.setGeometry(QtCore.QRect(10, 35, 121, 22))
        self.payment_contract_sbox.setObjectName(_fromUtf8("payment_contract_sbox"))
        self.label_27 = QtGui.QLabel(self.groupBox_4)
        self.label_27.setGeometry(QtCore.QRect(10, 60, 87, 13))
        self.label_27.setObjectName(_fromUtf8("label_27"))
        self.payment_before_less_sbox = QtGui.QDoubleSpinBox(self.groupBox_4)
        self.payment_before_less_sbox.setGeometry(QtCore.QRect(10, 80, 121, 22))
        self.payment_before_less_sbox.setObjectName(_fromUtf8("payment_before_less_sbox"))
        self.payment_before_over_sbox = QtGui.QDoubleSpinBox(self.groupBox_4)
        self.payment_before_over_sbox.setGeometry(QtCore.QRect(10, 125, 121, 22))
        self.payment_before_over_sbox.setObjectName(_fromUtf8("payment_before_over_sbox"))
        self.label_28 = QtGui.QLabel(self.groupBox_4)
        self.label_28.setGeometry(QtCore.QRect(10, 105, 74, 13))
        self.label_28.setObjectName(_fromUtf8("label_28"))
        self.label_29 = QtGui.QLabel(self.groupBox_4)
        self.label_29.setGeometry(QtCore.QRect(10, 150, 128, 13))
        self.label_29.setObjectName(_fromUtf8("label_29"))
        self.payment_year_sbox = QtGui.QDoubleSpinBox(self.groupBox_4)
        self.payment_year_sbox.setGeometry(QtCore.QRect(10, 170, 121, 22))
        self.payment_year_sbox.setObjectName(_fromUtf8("payment_year_sbox"))
        self.label_30 = QtGui.QLabel(self.groupBox_4)
        self.label_30.setGeometry(QtCore.QRect(150, 60, 97, 13))
        self.label_30.setObjectName(_fromUtf8("label_30"))
        self.payment_fund_sbox = QtGui.QDoubleSpinBox(self.groupBox_4)
        self.payment_fund_sbox.setGeometry(QtCore.QRect(150, 35, 121, 22))
        self.payment_fund_sbox.setObjectName(_fromUtf8("payment_fund_sbox"))
        self.payment_loss_sbox = QtGui.QDoubleSpinBox(self.groupBox_4)
        self.payment_loss_sbox.setGeometry(QtCore.QRect(150, 80, 121, 22))
        self.payment_loss_sbox.setObjectName(_fromUtf8("payment_loss_sbox"))
        self.label_31 = QtGui.QLabel(self.groupBox_4)
        self.label_31.setGeometry(QtCore.QRect(150, 15, 70, 13))
        self.label_31.setObjectName(_fromUtf8("label_31"))
        self.groupBox_5 = QtGui.QGroupBox(self.tab)
        self.groupBox_5.setGeometry(QtCore.QRect(570, 250, 281, 224))
        self.groupBox_5.setStyleSheet(_fromUtf8("background-color: rgb(233, 247, 255);"))
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.paid_less_sbox = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.paid_less_sbox.setGeometry(QtCore.QRect(150, 125, 121, 22))
        self.paid_less_sbox.setStyleSheet(_fromUtf8("background-color: rgb(255, 170, 127);"))
        self.paid_less_sbox.setObjectName(_fromUtf8("paid_less_sbox"))
        self.label_39 = QtGui.QLabel(self.groupBox_5)
        self.label_39.setGeometry(QtCore.QRect(150, 105, 121, 16))
        self.label_39.setStyleSheet(_fromUtf8("background-color: rgb(255, 170, 127);"))
        self.label_39.setObjectName(_fromUtf8("label_39"))
        self.label_40 = QtGui.QLabel(self.groupBox_5)
        self.label_40.setGeometry(QtCore.QRect(10, 15, 99, 13))
        self.label_40.setObjectName(_fromUtf8("label_40"))
        self.paid_before_less_sbox = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.paid_before_less_sbox.setGeometry(QtCore.QRect(10, 35, 121, 22))
        self.paid_before_less_sbox.setObjectName(_fromUtf8("paid_before_less_sbox"))
        self.label_41 = QtGui.QLabel(self.groupBox_5)
        self.label_41.setGeometry(QtCore.QRect(10, 60, 132, 13))
        self.label_41.setObjectName(_fromUtf8("label_41"))
        self.paid_year_sbox = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.paid_year_sbox.setGeometry(QtCore.QRect(10, 80, 121, 22))
        self.paid_year_sbox.setObjectName(_fromUtf8("paid_year_sbox"))
        self.paid_fund_sbox = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.paid_fund_sbox.setGeometry(QtCore.QRect(10, 125, 121, 22))
        self.paid_fund_sbox.setObjectName(_fromUtf8("paid_fund_sbox"))
        self.label_42 = QtGui.QLabel(self.groupBox_5)
        self.label_42.setGeometry(QtCore.QRect(10, 105, 121, 16))
        self.label_42.setObjectName(_fromUtf8("label_42"))
        self.label_43 = QtGui.QLabel(self.groupBox_5)
        self.label_43.setGeometry(QtCore.QRect(10, 150, 121, 16))
        self.label_43.setObjectName(_fromUtf8("label_43"))
        self.paid_district_sbox = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.paid_district_sbox.setGeometry(QtCore.QRect(10, 170, 121, 22))
        self.paid_district_sbox.setObjectName(_fromUtf8("paid_district_sbox"))
        self.label_44 = QtGui.QLabel(self.groupBox_5)
        self.label_44.setGeometry(QtCore.QRect(150, 60, 104, 13))
        self.label_44.setObjectName(_fromUtf8("label_44"))
        self.paid_city_sbox = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.paid_city_sbox.setGeometry(QtCore.QRect(150, 35, 121, 22))
        self.paid_city_sbox.setObjectName(_fromUtf8("paid_city_sbox"))
        self.paid_invalid_sbox = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.paid_invalid_sbox.setGeometry(QtCore.QRect(150, 80, 121, 22))
        self.paid_invalid_sbox.setObjectName(_fromUtf8("paid_invalid_sbox"))
        self.label_45 = QtGui.QLabel(self.groupBox_5)
        self.label_45.setGeometry(QtCore.QRect(150, 15, 86, 13))
        self.label_45.setObjectName(_fromUtf8("label_45"))
        self.label_46 = QtGui.QLabel(self.groupBox_5)
        self.label_46.setGeometry(QtCore.QRect(150, 150, 62, 13))
        self.label_46.setObjectName(_fromUtf8("label_46"))
        self.paid_over_sbox = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.paid_over_sbox.setGeometry(QtCore.QRect(150, 170, 121, 22))
        self.paid_over_sbox.setObjectName(_fromUtf8("paid_over_sbox"))
        self.groupBox = QtGui.QGroupBox(self.tab)
        self.groupBox.setGeometry(QtCore.QRect(10, 250, 261, 226))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.label_47 = QtGui.QLabel(self.groupBox)
        self.label_47.setGeometry(QtCore.QRect(10, 16, 97, 13))
        self.label_47.setObjectName(_fromUtf8("label_47"))
        self.payment_contract_edit = QtGui.QLineEdit(self.groupBox)
        self.payment_contract_edit.setEnabled(True)
        self.payment_contract_edit.setGeometry(QtCore.QRect(10, 36, 131, 20))
        self.payment_contract_edit.setObjectName(_fromUtf8("payment_contract_edit"))
        self.label_22 = QtGui.QLabel(self.groupBox)
        self.label_22.setGeometry(QtCore.QRect(10, 150, 141, 16))
        self.label_22.setObjectName(_fromUtf8("label_22"))
        self.decsription_txt = QtGui.QTextEdit(self.groupBox)
        self.decsription_txt.setGeometry(QtCore.QRect(10, 170, 241, 51))
        self.decsription_txt.setObjectName(_fromUtf8("decsription_txt"))
        self.label_48 = QtGui.QLabel(self.groupBox)
        self.label_48.setGeometry(QtCore.QRect(10, 60, 97, 13))
        self.label_48.setObjectName(_fromUtf8("label_48"))
        self.payment_zoriulalt_edit = QtGui.QLineEdit(self.groupBox)
        self.payment_zoriulalt_edit.setEnabled(True)
        self.payment_zoriulalt_edit.setGeometry(QtCore.QRect(10, 80, 241, 20))
        self.payment_zoriulalt_edit.setObjectName(_fromUtf8("payment_zoriulalt_edit"))
        self.payment_name_edit = QtGui.QLineEdit(self.groupBox)
        self.payment_name_edit.setEnabled(True)
        self.payment_name_edit.setGeometry(QtCore.QRect(10, 126, 241, 20))
        self.payment_name_edit.setObjectName(_fromUtf8("payment_name_edit"))
        self.label_49 = QtGui.QLabel(self.groupBox)
        self.label_49.setGeometry(QtCore.QRect(10, 106, 97, 13))
        self.label_49.setObjectName(_fromUtf8("label_49"))
        self.label_50 = QtGui.QLabel(self.groupBox)
        self.label_50.setGeometry(QtCore.QRect(150, 16, 97, 13))
        self.label_50.setObjectName(_fromUtf8("label_50"))
        self.payment_area_edit = QtGui.QLineEdit(self.groupBox)
        self.payment_area_edit.setEnabled(True)
        self.payment_area_edit.setGeometry(QtCore.QRect(150, 36, 101, 20))
        self.payment_area_edit.setObjectName(_fromUtf8("payment_area_edit"))
        self.line = QtGui.QFrame(self.tab)
        self.line.setGeometry(QtCore.QRect(10, 234, 841, 21))
        self.line.setStyleSheet(_fromUtf8(""))
        self.line.setLineWidth(5)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.tabWidget_2 = QtGui.QTabWidget(self.tab)
        self.tabWidget_2.setGeometry(QtCore.QRect(5, 68, 851, 171))
        self.tabWidget_2.setObjectName(_fromUtf8("tabWidget_2"))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.payment_twidget = QtGui.QTableWidget(self.tab_3)
        self.payment_twidget.setGeometry(QtCore.QRect(4, 3, 838, 141))
        self.payment_twidget.setObjectName(_fromUtf8("payment_twidget"))
        self.payment_twidget.setColumnCount(13)
        self.payment_twidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.payment_twidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.payment_twidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.payment_twidget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.payment_twidget.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.payment_twidget.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.payment_twidget.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.payment_twidget.setHorizontalHeaderItem(6, item)
        item = QtGui.QTableWidgetItem()
        self.payment_twidget.setHorizontalHeaderItem(7, item)
        item = QtGui.QTableWidgetItem()
        self.payment_twidget.setHorizontalHeaderItem(8, item)
        item = QtGui.QTableWidgetItem()
        self.payment_twidget.setHorizontalHeaderItem(9, item)
        item = QtGui.QTableWidgetItem()
        self.payment_twidget.setHorizontalHeaderItem(10, item)
        item = QtGui.QTableWidgetItem()
        self.payment_twidget.setHorizontalHeaderItem(11, item)
        item = QtGui.QTableWidgetItem()
        self.payment_twidget.setHorizontalHeaderItem(12, item)
        self.tabWidget_2.addTab(self.tab_3, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.paid_twidget = QtGui.QTableWidget(self.tab_2)
        self.paid_twidget.setGeometry(QtCore.QRect(4, 3, 838, 110))
        self.paid_twidget.setObjectName(_fromUtf8("paid_twidget"))
        self.paid_twidget.setColumnCount(10)
        self.paid_twidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.paid_twidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.paid_twidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.paid_twidget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.paid_twidget.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.paid_twidget.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.paid_twidget.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.paid_twidget.setHorizontalHeaderItem(6, item)
        item = QtGui.QTableWidgetItem()
        self.paid_twidget.setHorizontalHeaderItem(7, item)
        item = QtGui.QTableWidgetItem()
        self.paid_twidget.setHorizontalHeaderItem(8, item)
        item = QtGui.QTableWidgetItem()
        self.paid_twidget.setHorizontalHeaderItem(9, item)
        self.tabWidget_2.addTab(self.tab_2, _fromUtf8(""))
        self.object_cbox = QtGui.QComboBox(self.tab)
        self.object_cbox.setGeometry(QtCore.QRect(240, 43, 401, 22))
        self.object_cbox.setObjectName(_fromUtf8("object_cbox"))
        self.year_cbox = QtGui.QComboBox(self.tab)
        self.year_cbox.setGeometry(QtCore.QRect(140, 43, 81, 22))
        self.year_cbox.setObjectName(_fromUtf8("year_cbox"))
        self.city_type_cbox = QtGui.QComboBox(self.tab)
        self.city_type_cbox.setGeometry(QtCore.QRect(6, 43, 121, 22))
        self.city_type_cbox.setObjectName(_fromUtf8("city_type_cbox"))
        self.all_chbox = QtGui.QCheckBox(self.tab)
        self.all_chbox.setGeometry(QtCore.QRect(650, 45, 60, 17))
        self.all_chbox.setObjectName(_fromUtf8("all_chbox"))
        self.payment_find_button = QtGui.QPushButton(self.tab)
        self.payment_find_button.setGeometry(QtCore.QRect(720, 42, 75, 23))
        self.payment_find_button.setIcon(icon)
        self.payment_find_button.setObjectName(_fromUtf8("payment_find_button"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.save_button = QtGui.QPushButton(ParcelInfoFeeDialog)
        self.save_button.setGeometry(QtCore.QRect(690, 510, 75, 23))
        self.save_button.setObjectName(_fromUtf8("save_button"))
        self.finish_button = QtGui.QPushButton(ParcelInfoFeeDialog)
        self.finish_button.setGeometry(QtCore.QRect(600, 510, 75, 23))
        self.finish_button.setObjectName(_fromUtf8("finish_button"))
        self.one_select_chbox = QtGui.QCheckBox(ParcelInfoFeeDialog)
        self.one_select_chbox.setGeometry(QtCore.QRect(390, 510, 211, 20))
        self.one_select_chbox.setChecked(False)
        self.one_select_chbox.setObjectName(_fromUtf8("one_select_chbox"))
        self.status_label = QtGui.QLabel(ParcelInfoFeeDialog)
        self.status_label.setGeometry(QtCore.QRect(10, 510, 319, 20))
        self.status_label.setText(_fromUtf8(""))
        self.status_label.setObjectName(_fromUtf8("status_label"))

        self.retranslateUi(ParcelInfoFeeDialog)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(ParcelInfoFeeDialog)

    def retranslateUi(self, ParcelInfoFeeDialog):
        ParcelInfoFeeDialog.setWindowTitle(_translate("ParcelInfoFeeDialog", "Dialog", None))
        self.close_button.setText(_translate("ParcelInfoFeeDialog", "Close", None))
        self.find_gbox.setTitle(_translate("ParcelInfoFeeDialog", "Find", None))
        self.find_button.setText(_translate("ParcelInfoFeeDialog", "Find", None))
        self.label_3.setText(_translate("ParcelInfoFeeDialog", "Person ID", None))
        self.label_4.setText(_translate("ParcelInfoFeeDialog", "Old Parcel ID", None))
        self.clear_button.setText(_translate("ParcelInfoFeeDialog", "New", None))
        self.groupBox_4.setTitle(_translate("ParcelInfoFeeDialog", "Ногдуулалт, төлбөл зохих төлбөр", None))
        self.label_25.setText(_translate("ParcelInfoFeeDialog", "Нийт төлбөр", None))
        self.label_26.setText(_translate("ParcelInfoFeeDialog", "Гэрээ ногд. Төлбөр", None))
        self.label_27.setText(_translate("ParcelInfoFeeDialog", "Дутуу Төлөлт(+)", None))
        self.label_28.setText(_translate("ParcelInfoFeeDialog", "Илүү Төлөлт(-)", None))
        self.label_29.setText(_translate("ParcelInfoFeeDialog", "Тухайн онд ногд. Төлбөр", None))
        self.label_30.setText(_translate("ParcelInfoFeeDialog", "Алданги, торгууль", None))
        self.label_31.setText(_translate("ParcelInfoFeeDialog", "Нөхөн төлбөр", None))
        self.groupBox_5.setTitle(_translate("ParcelInfoFeeDialog", "Төлөлт", None))
        self.label_39.setText(_translate("ParcelInfoFeeDialog", "Дутуу төлөлт", None))
        self.label_40.setText(_translate("ParcelInfoFeeDialog", "Урд оны дутуугаас", None))
        self.label_41.setText(_translate("ParcelInfoFeeDialog", "Тайлангаар ногдуулснаас", None))
        self.label_42.setText(_translate("ParcelInfoFeeDialog", "Хүү, торгууль, бусад", None))
        self.label_43.setText(_translate("ParcelInfoFeeDialog", "Дүүрэгт төлсөн", None))
        self.label_44.setText(_translate("ParcelInfoFeeDialog", "Хүчингүй болсон дүн", None))
        self.label_45.setText(_translate("ParcelInfoFeeDialog", "Нийслэлд төлсөн", None))
        self.label_46.setText(_translate("ParcelInfoFeeDialog", "Илүү төлөлт", None))
        self.groupBox.setTitle(_translate("ParcelInfoFeeDialog", "Мэдээлэл", None))
        self.label_47.setText(_translate("ParcelInfoFeeDialog", "Гэрээний дугаар", None))
        self.label_22.setText(_translate("ParcelInfoFeeDialog", "Тайлбар", None))
        self.label_48.setText(_translate("ParcelInfoFeeDialog", "Зориулалт", None))
        self.label_49.setText(_translate("ParcelInfoFeeDialog", "Оноосон нэр", None))
        self.label_50.setText(_translate("ParcelInfoFeeDialog", "Талайн хэмжээ /м2/", None))
        self.payment_twidget.setSortingEnabled(True)
        item = self.payment_twidget.horizontalHeaderItem(0)
        item.setText(_translate("ParcelInfoFeeDialog", "Төрөл", None))
        item = self.payment_twidget.horizontalHeaderItem(1)
        item.setText(_translate("ParcelInfoFeeDialog", "Жил", None))
        item = self.payment_twidget.horizontalHeaderItem(2)
        item.setText(_translate("ParcelInfoFeeDialog", "Регистр", None))
        item = self.payment_twidget.horizontalHeaderItem(3)
        item.setText(_translate("ParcelInfoFeeDialog", "Гэрээний дугаар", None))
        item = self.payment_twidget.horizontalHeaderItem(4)
        item.setText(_translate("ParcelInfoFeeDialog", "Гэрээнд ногдуулсан дүн", None))
        item = self.payment_twidget.horizontalHeaderItem(5)
        item.setText(_translate("ParcelInfoFeeDialog", "Тухайн онд ногдуулсан дүн", None))
        item = self.payment_twidget.horizontalHeaderItem(6)
        item.setText(_translate("ParcelInfoFeeDialog", "Тухайн жил нийт", None))
        item = self.payment_twidget.horizontalHeaderItem(7)
        item.setText(_translate("ParcelInfoFeeDialog", "Урд оны дутуу төлөлтөөс", None))
        item = self.payment_twidget.horizontalHeaderItem(8)
        item.setText(_translate("ParcelInfoFeeDialog", "Урд оны илүү төлөлтөөс", None))
        item = self.payment_twidget.horizontalHeaderItem(9)
        item.setText(_translate("ParcelInfoFeeDialog", "Нийслэлд төлсөн", None))
        item = self.payment_twidget.horizontalHeaderItem(10)
        item.setText(_translate("ParcelInfoFeeDialog", "Дүүрэгт төлсөн", None))
        item = self.payment_twidget.horizontalHeaderItem(11)
        item.setText(_translate("ParcelInfoFeeDialog", "Хүчингүйд тооцсон дүн", None))
        item = self.payment_twidget.horizontalHeaderItem(12)
        item.setText(_translate("ParcelInfoFeeDialog", "Тайлан оны илүү, дутуу төлөлт ", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_3), _translate("ParcelInfoFeeDialog", "Төлбөрийн мэдээлэл", None))
        self.paid_twidget.setSortingEnabled(True)
        item = self.paid_twidget.horizontalHeaderItem(0)
        item.setText(_translate("ParcelInfoFeeDialog", "Жил", None))
        item = self.paid_twidget.horizontalHeaderItem(1)
        item.setText(_translate("ParcelInfoFeeDialog", "Регистр", None))
        item = self.paid_twidget.horizontalHeaderItem(2)
        item.setText(_translate("ParcelInfoFeeDialog", "Гэрээний дугаар", None))
        item = self.paid_twidget.horizontalHeaderItem(3)
        item.setText(_translate("ParcelInfoFeeDialog", "Гэрээнд ногдуулсан дүн", None))
        item = self.paid_twidget.horizontalHeaderItem(4)
        item.setText(_translate("ParcelInfoFeeDialog", "Тухайн онд ногдуулсан дүн", None))
        item = self.paid_twidget.horizontalHeaderItem(5)
        item.setText(_translate("ParcelInfoFeeDialog", "Тухайн жил нийт", None))
        item = self.paid_twidget.horizontalHeaderItem(6)
        item.setText(_translate("ParcelInfoFeeDialog", "Урд оны дутуу төлөлтөөс", None))
        item = self.paid_twidget.horizontalHeaderItem(7)
        item.setText(_translate("ParcelInfoFeeDialog", "Бүгд дүн", None))
        item = self.paid_twidget.horizontalHeaderItem(8)
        item.setText(_translate("ParcelInfoFeeDialog", "Хүчингүйд тооцсон дүн", None))
        item = self.paid_twidget.horizontalHeaderItem(9)
        item.setText(_translate("ParcelInfoFeeDialog", "Тайлан оны илүү, дутуу төлөлт ", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_2), _translate("ParcelInfoFeeDialog", "ЛМ-н төлбөр төлөлтийн мэдээлэл", None))
        self.all_chbox.setText(_translate("ParcelInfoFeeDialog", "Бүгд", None))
        self.payment_find_button.setText(_translate("ParcelInfoFeeDialog", "Хайх", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("ParcelInfoFeeDialog", "Fee", None))
        self.save_button.setText(_translate("ParcelInfoFeeDialog", "Save", None))
        self.finish_button.setText(_translate("ParcelInfoFeeDialog", "Finish", None))
        self.one_select_chbox.setText(_translate("ParcelInfoFeeDialog", "Зөвхөн сонгогдсон жилийг оруулах", None))

import resources_rc
