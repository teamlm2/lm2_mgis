# coding=utf8
import os

__author__ = 'ankhbold'
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sqlalchemy.exc import SQLAlchemyError
from qgis.core import *
from sqlalchemy import func, or_, extract
from ..utils.LayerUtils import LayerUtils
from ..view.Ui_ParcelInfoFeeDialog import *
from ..utils.SessionHandler import SessionHandler
from ..utils.PluginUtils import *
from ..model.BsPerson import *
from ..model.CtFee import *
from ..model.DatabaseHelper import *
from ..model.SetPayment import *
from ..model.FeeUnified import *
from ..model.ContractSearch import *
from ..model.ClContractStatus import *
from ..model.ClLanduseType import *
from ..model.SetFeeZone import *
from ..model.UbFeeHistory import *
from ..model.PaPaymentPaid import *
from ..model.CtContractApplicationRole import *
from ..model.SetApplicationTypePersonRole import *
from .qt_classes.ComboBoxDelegate import *

class ParcelInfoFeeDialog(QDialog, Ui_ParcelInfoFeeDialog):

    def __init__(self, old_parcel_id, person_id, is_find, plugin, parent=None):

        super(ParcelInfoFeeDialog, self).__init__(parent)
        self.setupUi(self)
        self.plugin = plugin
        self.session = SessionHandler().session_instance()
        self.old_parcel_id = old_parcel_id
        self.person_id = person_id
        self.time_counter = None
        self.close_button.clicked.connect(self.reject)

        self.old_parcel_id_edit.setText(self.old_parcel_id)
        self.person_id_edit.setText(self.person_id)

        self.payment_contract_sbox.setMaximum(9999999999)
        self.payment_before_less_sbox.setMaximum(9999999999)
        self.payment_before_over_sbox.setMaximum(9999999999)
        self.payment_year_sbox.setMaximum(9999999999)
        self.payment_fund_sbox.setMaximum(9999999999)
        self.payment_loss_sbox.setMaximum(9999999999)
        self.payment_total_sbox.setMaximum(9999999999)

        self.paid_before_less_sbox.setMaximum(9999999999)
        self.paid_year_sbox.setMaximum(9999999999)
        self.paid_fund_sbox.setMaximum(9999999999)
        self.paid_city_sbox.setMaximum(9999999999)
        self.paid_district_sbox.setMaximum(9999999999)
        self.paid_invalid_sbox.setMaximum(9999999999)
        self.paid_less_sbox.setMaximum(9999999999)
        self.paid_over_sbox.setMaximum(9999999999)

        employee = DatabaseUtils.current_employee()
        department_id = employee.department_id
        self.city_type = 2
        if department_id == 120:
            self.city_type = 1

        self.select_years = [2019, 2018, 2017, 2016, 2015, 2014]
        self.__setup_table_widget()

        self.__setup_cbox()
        self.selected_year = None
        self.__list_of_paid()
        self.__list_of_payment()

        # if is_find:
        #     self.__load_fee(self.person_id, self.old_parcel_id)
        # else:
        #     self.find_gbox.setEnabled(True)
        #     self.old_parcel_id_edit.setEnabled(True)
        #     self.person_id_edit.setEnabled(True)

    def __setup_table_widget(self):

        self.paid_twidget.setAlternatingRowColors(True)
        self.paid_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.paid_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.paid_twidget.setSelectionMode(QTableWidget.SingleSelection)

        # self.payment_twidget.setAlternatingRowColors(True)
        # self.payment_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        # self.payment_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        # self.payment_twidget.setSelectionMode(QTableWidget.SingleSelection)
        # self.payment_twidget.setWordWrap(True)
        # self.payment_twidget.setDragEnabled(True)

        self.payment_twidget.setAlternatingRowColors(True)
        self.payment_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.payment_twidget.setSelectionMode(QTableWidget.SingleSelection)

        self.status_list = [u'Засагдаагүй', u'Засагдсан']
        delegate = ComboBoxDelegate(0, self.status_list, self.payment_twidget)
        self.payment_twidget.setItemDelegateForColumn(0, delegate)

    def __list_of_payment(self):

        self.payment_twidget.setRowCount(0)

        if self.old_parcel_id == '':
            return
        values = self.session.query(UbFeeHistory). \
            filter(UbFeeHistory.pid == self.old_parcel_id).all()

        for value in values:
            count = self.payment_twidget.rowCount()
            self.payment_twidget.insertRow(count)

            status_desc = u'Засагдаагүй'
            status_code = 1
            if value.status == 2:
                status_desc = u'Засагдсан'
                status_code = 2
            item = QTableWidgetItem(unicode(status_desc))
            item.setData(Qt.UserRole, status_code)
            self.payment_twidget.setItem(count, 0, item)

            city_type = u''
            if value.city_type == 1:
                city_type = u'Нийслэл'
            if value.city_type == 2:
                city_type = u'Дүүрэг'
            item = QTableWidgetItem(city_type)
            item.setData(Qt.UserRole, value.city_type)
            item.setData(Qt.UserRole + 1, value.id)
            self.payment_twidget.setItem(count, 1, item)

            item = QTableWidgetItem(str(value.pid))
            item.setData(Qt.UserRole, value.pid)
            self.payment_twidget.setItem(count, 2, item)

            item = QTableWidgetItem(str(value.current_year))
            item.setData(Qt.UserRole, value.current_year)
            self.payment_twidget.setItem(count, 3, item)

            item = QTableWidgetItem(value.person_register)
            item.setData(Qt.UserRole, value.person_register)
            self.payment_twidget.setItem(count, 4, item)

            item = QTableWidgetItem(value.contract_no)
            item.setData(Qt.UserRole, value.contract_no)
            self.payment_twidget.setItem(count, 5, item)

            item = QTableWidgetItem(str(value.payment_contract))
            item.setData(Qt.UserRole, value.payment_contract)
            self.payment_twidget.setItem(count, 6, item)

            item = QTableWidgetItem(str(value.payment_year))
            item.setData(Qt.UserRole, value.payment_year)
            self.payment_twidget.setItem(count, 7, item)

            item = QTableWidgetItem(str(value.payment_total))
            item.setData(Qt.UserRole, value.city_type)
            self.payment_twidget.setItem(count, 8, item)

            item = QTableWidgetItem(str(value.payment_before_less))
            item.setData(Qt.UserRole, value.payment_before_less)
            self.payment_twidget.setItem(count, 9, item)

            item = QTableWidgetItem(str(value.payment_before_over))
            item.setData(Qt.UserRole, value.payment_before_over)
            self.payment_twidget.setItem(count, 10, item)

            item = QTableWidgetItem(str(value.paid_city))
            item.setData(Qt.UserRole, value.paid_city)
            self.payment_twidget.setItem(count, 11, item)

            item = QTableWidgetItem(str(value.paid_district))
            item.setData(Qt.UserRole, value.paid_district)
            self.payment_twidget.setItem(count, 12, item)

            item = QTableWidgetItem(str(value.invalid_payment))
            item.setData(Qt.UserRole, value.invalid_payment)
            self.payment_twidget.setItem(count, 13, item)

            item = QTableWidgetItem(str(value.paid_before_less))
            item.setData(Qt.UserRole, value.paid_before_less)
            self.payment_twidget.setItem(count, 14, item)

            # delegate_edit4 = QLineEdit()
            # delegate_edit4.setText(value.person_register)
            # self.payment_twidget.setCellWidget(count, 4, delegate_edit4)
            # delegate_edit5 = QLineEdit()
            # delegate_edit5.setText(value.contract_no)
            # self.payment_twidget.setCellWidget(count, 5, delegate_edit5)
            # delegate_doublespin6 = QDoubleSpinBox()
            # delegate_doublespin6.setValue(value.payment_contract)
            # self.payment_twidget.setCellWidget(count, 6, delegate_doublespin6)
            # delegate_doublespin7 = QDoubleSpinBox()
            # delegate_doublespin7.setValue(value.payment_year)
            # self.payment_twidget.setCellWidget(count, 7, delegate_doublespin7)
            # delegate_doublespin8 = QDoubleSpinBox()
            # delegate_doublespin7.setValue(value.payment_year)
            # self.payment_twidget.setCellWidget(count, 8, delegate_doublespin8)
            # delegate_doublespin9 = QDoubleSpinBox()
            # delegate_doublespin7.setValue(value.payment_year)
            # self.payment_twidget.setCellWidget(count, 9, delegate_doublespin9)
            # delegate_doublespin10 = QDoubleSpinBox()
            # delegate_doublespin7.setValue(value.payment_year)
            # self.payment_twidget.setCellWidget(count, 10, delegate_doublespin10)
            # delegate_doublespin11 = QDoubleSpinBox()
            # delegate_doublespin7.setValue(value.payment_year)
            # self.payment_twidget.setCellWidget(count, 11, delegate_doublespin11)
            # delegate_doublespin12 = QDoubleSpinBox()
            # delegate_doublespin7.setValue(value.payment_year)
            # self.payment_twidget.setCellWidget(count, 12, delegate_doublespin12)
            # delegate_doublespin13 = QDoubleSpinBox()
            # delegate_doublespin7.setValue(value.payment_year)
            # self.payment_twidget.setCellWidget(count, 13, delegate_doublespin13)
            # delegate_doublespin14 = QDoubleSpinBox()
            # self.payment_twidget.setCellWidget(count, 14, delegate_doublespin14)
        self.payment_twidget.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)

    def __list_of_paid(self):

        self.paid_twidget.setRowCount(0)
        parcel_id = None
        count = self.session.query(CaUBParcel).filter(CaUBParcel.old_parcel_id == self.old_parcel_id).count()
        if count == 0:
            return
        old_parcel = self.session.query(CaUBParcel).filter(CaUBParcel.old_parcel_id == self.old_parcel_id).one()

        parcel_count = self.session.query(CaParcelTbl). \
            filter(CaParcelTbl.geometry.ST_Equals(old_parcel.geometry)).count()
        if parcel_count > 0:
            parcel = self.session.query(CaParcelTbl). \
                filter(CaParcelTbl.geometry.ST_Equals(old_parcel.geometry)).first()
            parcel_id = parcel.parcel_id

        if not parcel_id:
            return

        values = self.session.query(PaPaymentPaid). \
            filter(PaPaymentPaid.parcel_id == parcel_id).all()

        for value in values:
            count = self.paid_twidget.rowCount()

            self.paid_twidget.insertRow(count)
            item = QTableWidgetItem(str(value.paid_year))
            item.setData(Qt.UserRole, value.paid_year)
            self.paid_twidget.setItem(count, 0, item)
            if value.person_ref:
                person = value.person_ref
                item = QTableWidgetItem(unicode(person.person_register))
                item.setData(Qt.UserRole, person.person_id)
                self.paid_twidget.setItem(count, 1, item)
            if value.contract_ref:
                contract = value.contract_ref
                item = QTableWidgetItem((contract.contract_no))
                item.setData(Qt.UserRole, contract.contract_no)
                self.paid_twidget.setItem(count, 2, item)
            if value.contract_amount:
                item = QTableWidgetItem(str(value.contract_amount))
                item.setData(Qt.UserRole, value.contract_amount)
                self.paid_twidget.setItem(count, 3, item)
            if value.imposition_year_amount:
                item = QTableWidgetItem(str(value.imposition_year_amount))
                item.setData(Qt.UserRole, value.imposition_year_amount)
                self.paid_twidget.setItem(count, 4, item)
            if value.imposition_total_amount:
                item = QTableWidgetItem(str(value.imposition_total_amount))
                item.setData(Qt.UserRole, value.imposition_total_amount)
                self.paid_twidget.setItem(count, 5, item)
            if value.remainning_amount:
                item = QTableWidgetItem(str(value.remainning_amount))
                item.setData(Qt.UserRole, value.remainning_amount)
                self.paid_twidget.setItem(count, 6, item)
            if value.total_amount:
                item = QTableWidgetItem(str(value.total_amount))
                item.setData(Qt.UserRole, value.total_amount)
                self.paid_twidget.setItem(count, 7, item)
            if value.invalid_amount:
                item = QTableWidgetItem(str(value.invalid_amount))
                item.setData(Qt.UserRole, value.invalid_amount)
                self.paid_twidget.setItem(count, 8, item)
            if value.year_amount:
                item = QTableWidgetItem(str(value.year_amount))
                item.setData(Qt.UserRole, value.year_amount)
                self.paid_twidget.setItem(count, 9, item)

        self.paid_twidget.resizeColumnsToContents()

    def __setup_cbox(self):

        self.year_cbox.clear()
        self.city_type_cbox.clear()
        for value in self.select_years:
            self.year_cbox.addItem(str(value), value)

        self.city_type_cbox.addItem(u'Нийслэл', 1)
        self.city_type_cbox.addItem(u'Дүүрэг', 2)

    @pyqtSlot(int)
    def on_year_cbox_currentIndexChanged(self, index):

        self.object_cbox.clear()
        current_year = self.year_cbox.itemData(self.year_cbox.currentIndex())
        values = self.session.query(UbFeeHistory).\
            filter(UbFeeHistory.pid == self.old_parcel_id).\
            filter(UbFeeHistory.current_year == current_year).all()

        for value in values:
            name = ''
            if value.pid:
                name = value.pid

            if value.person_register:
                name = name + ': (' + value.person_register + ') '

            if value.ner:
                name = name + ' ' + value.ner
            self.object_cbox.addItem(name, value.id)

    # @pyqtSlot(int)
    # def on_object_cbox_currentIndexChanged(self, index):
    #
    #     self.__clear_all()
    #     current_id = self.object_cbox.itemData(self.object_cbox.currentIndex())
    #
    #     self.__load_fee_history(current_id)

    @pyqtSlot(QTableWidgetItem)
    def on_payment_twidget_itemClicked(self, item):

        # self.__clear_all()

        selected_row = self.payment_twidget.currentRow()
        item = self.payment_twidget.item(selected_row, 1)
        id = item.data(Qt.UserRole + 1)

        value = self.session.query(UbFeeHistory). \
            filter(UbFeeHistory.id == id).first()

        self.person_id_edit.setText(value.person_register)
        self.contract_no_edit.setText(value.contract_no)
        self.old_parcel_id_edit.setText(str(value.pid))
        self.old_parcel_id = str(value.pid)

        if value.city_type:
            self.city_type_cbox.setCurrentIndex(self.city_type_cbox.findData(value.city_type))

        if value.current_year:
            self.year_cbox.setCurrentIndex(self.year_cbox.findData(value.current_year))

        if value.id:
            self.object_cbox.setCurrentIndex(self.object_cbox.findData(value.id))
        self.__load_fee_history(id)
        self.__list_of_paid()

    def __load_fee_history(self, current_id):

        value = self.session.query(UbFeeHistory).\
            filter(UbFeeHistory.id == current_id).first()

        if not value:
            return

        self.payment_contract_edit.setText(value.contract_no if value.contract_no is not None else '')
        self.payment_area_edit.setText(str(value.document_area) if value.document_area is not None else '0')
        self.payment_zoriulalt_edit.setText(unicode(value.zoriulalt) if value.zoriulalt is not None else '')
        self.payment_name_edit.setText(value.ner if value.ner is not None else '')
        self.decsription_txt.setText(value.description if value.description is not None else '')

        self.payment_contract_sbox.setValue(value.payment_contract if value.payment_contract is not None else 0)
        self.payment_before_less_sbox.setValue(value.payment_before_less if value.payment_before_less is not None else 0)
        self.payment_before_over_sbox.setValue(value.payment_before_over if value.payment_before_over is not None else 0)
        self.payment_year_sbox.setValue(value.payment_year if value.payment_year is not None else 0)
        self.payment_fund_sbox.setValue(value.payment_fund if value.payment_fund is not None else 0)
        self.payment_loss_sbox.setValue(value.payment_loss if value.payment_loss is not None else 0)
        self.payment_total_sbox.setValue(value.payment_total if value.payment_total is not None else 0)

        self.paid_before_less_sbox.setValue(value.paid_before_less if value.paid_before_less is not None else 0)
        self.paid_year_sbox.setValue(value.paid_year if value.paid_year is not None else 0)
        self.paid_fund_sbox.setValue(value.paid_fund if value.paid_fund is not None else 0)
        self.paid_city_sbox.setValue(value.paid_city if value.paid_city is not None else 0)
        self.paid_district_sbox.setValue(value.paid_district if value.paid_district is not None else 0)
        self.paid_invalid_sbox.setValue(value.invalid_payment if value.invalid_payment is not None else 0)
        self.paid_less_sbox.setValue(value.paid_less if value.paid_less is not None else 0)
        self.paid_over_sbox.setValue(value.paid_over if value.paid_over is not None else 0)

    def __clear_all(self):

        # self.payment_contract_edit.clear()
        # self.payment_area_edit.clear()
        # self.payment_zoriulalt_edit.clear()
        # self.payment_name_edit.clear()
        # self.decsription_txt.clear()

        self.payment_contract_sbox.setValue(0)
        self.payment_before_less_sbox.setValue(0)
        self.payment_before_over_sbox.setValue(0)
        self.payment_year_sbox.setValue(0)
        self.payment_fund_sbox.setValue(0)
        self.payment_loss_sbox.setValue(0)
        self.payment_total_sbox.setValue(0)

        self.paid_before_less_sbox.setValue(0)
        self.paid_year_sbox.setValue(0)
        self.paid_fund_sbox.setValue(0)
        self.paid_district_sbox.setValue(0)
        self.paid_city_sbox.setValue(0)
        self.paid_invalid_sbox.setValue(0)
        self.paid_less_sbox.setValue(0)
        self.paid_over_sbox.setValue(0)

    @pyqtSlot()
    def on_clear_button_clicked(self):

        self.person_id_edit.clear()
        self.contract_no_edit.clear()
        self.old_parcel_id_edit.clear()

    @pyqtSlot()
    def on_delete_button_clicked(self):

        selected_items = self.payment_twidget.selectedItems()

        if len(selected_items) == 0:
            self.status_label.setText(self.tr("Only single selection allowed."))
            return None

        selected_row = self.payment_twidget.currentRow()
        item = self.payment_twidget.item(selected_row, 1)
        id = item.data(Qt.UserRole + 1)

        message_box = QMessageBox()
        message_box.setText(u'Сонгогдсон төлбөрийн бүртгэлийг устгах уу?')
        delete_button = message_box.addButton(self.tr("Yes"), QMessageBox.ActionRole)
        message_box.addButton(self.tr("No"), QMessageBox.ActionRole)
        message_box.exec_()

        if not message_box.clickedButton() == delete_button:
            return
        else:
            self.session.query(UbFeeHistory).filter(UbFeeHistory.id == id).delete()

            self.__list_of_payment()

    @pyqtSlot()
    def on_save_button_clicked(self):

        c_year = self.year_cbox.itemData(self.year_cbox.currentIndex())

        is_count = self.session.query(UbFeeHistory). \
            filter(UbFeeHistory.pid == self.old_parcel_id_edit.text()). \
            filter(UbFeeHistory.current_year == c_year).count()

        selected_row = self.payment_twidget.currentRow()
        item = self.payment_twidget.item(selected_row, 1)
        if item:
            current_id = item.data(Qt.UserRole + 1)

            doc_area = 0
            object_count = self.session.query(UbFeeHistory).filter(UbFeeHistory.id == current_id).count()
            if self.payment_area_edit.text():
                doc_area = float(self.payment_area_edit.text())
            # for selected_row in range(self.payment_twidget.rowCount()):
            if object_count == 1:
                object = self.session.query(UbFeeHistory).filter(UbFeeHistory.id == current_id).one()
                item = self.payment_twidget.item(selected_row, 1)
                # current_id = item.data(Qt.UserRole + 1)
                item_year = self.payment_twidget.item(selected_row, 3)
                self.selected_year = item_year.data(Qt.UserRole)

                item_city = self.payment_twidget.item(selected_row, 1)
                city_type = item_city.data(Qt.UserRole)

                item_status = self.payment_twidget.item(selected_row, 0)
                status = 1
                if item_status.text() == u'Засагдсан':
                    status = 2

                object.contract_no = self.payment_contract_edit.text()
                object.document_area = doc_area
                object.zoriulalt = self.payment_zoriulalt_edit.text()
                object.ner = self.payment_name_edit.text()
                object.description = self.decsription_txt.toPlainText()

                object.payment_contract = self.payment_contract_sbox.value()
                object.payment_before_less = self.payment_before_less_sbox.value()
                object.payment_before_over = self.payment_before_over_sbox.value()
                object.payment_year = self.payment_year_sbox.value()
                object.payment_fund = self.payment_fund_sbox.value()
                object.payment_loss = self.payment_loss_sbox.value()
                object.payment_total = self.payment_total_sbox.value()

                object.paid_before_less = self.paid_before_less_sbox.value()
                object.paid_year = self.paid_year_sbox.value()
                object.paid_fund = self.paid_fund_sbox.value()
                object.paid_city = self.paid_city_sbox.value()
                object.paid_district = self.paid_district_sbox.value()
                object.invalid_payment = self.paid_invalid_sbox.value()
                object.paid_less = self.paid_less_sbox.value()
                object.paid_over = self.paid_over_sbox.value()
                object.status = status
                object.city_type = city_type

        if is_count == 0:
            object = UbFeeHistory()

            object.contract_no = self.payment_contract_edit.text()
            object.document_area = doc_area
            object.zoriulalt = self.payment_zoriulalt_edit.text()
            object.ner = self.payment_name_edit.text()
            object.description = self.decsription_txt.toPlainText()

            object.payment_contract = self.payment_contract_sbox.value()
            object.payment_before_less = self.payment_before_less_sbox.value()
            object.payment_before_over = self.payment_before_over_sbox.value()
            object.payment_year = self.payment_year_sbox.value()
            object.payment_fund = self.payment_fund_sbox.value()
            object.payment_loss = self.payment_loss_sbox.value()
            object.payment_total = self.payment_total_sbox.value()

            object.paid_before_less = self.paid_before_less_sbox.value()
            object.paid_year = self.paid_year_sbox.value()
            object.paid_fund = self.paid_fund_sbox.value()
            object.paid_city = self.paid_city_sbox.value()
            object.paid_district = self.paid_district_sbox.value()
            object.invalid_payment = self.paid_invalid_sbox.value()
            object.paid_less = self.paid_less_sbox.value()
            object.paid_over = self.paid_over_sbox.value()

            object.current_year = c_year
            object.pid = self.old_parcel_id
            object.person_register = self.person_id
            object.city_type = self.city_type
            object.status = 2

            self.session.add(object)
        self.__save_status()
        self.session.commit()

        self.__setup_cbox()
        self.year_cbox.setCurrentIndex(self.year_cbox.findData(self.selected_year))
        self.__start_fade_out_timer()
        self.__list_of_payment()

    def __save_status(self):

        for selected_row in range(self.payment_twidget.rowCount()):
            item = self.payment_twidget.item(selected_row, 1)
            current_id = item.data(Qt.UserRole + 1)
            item_status = self.payment_twidget.item(selected_row, 0)
            status = 1
            if item_status.text() == u'Засагдсан':
                status = 2
            count = self.session.query(UbFeeHistory).filter(UbFeeHistory.id == current_id).count()
            if count == 1:
                object = self.session.query(UbFeeHistory).filter(UbFeeHistory.id == current_id).one()
                object.status = status

    @pyqtSlot()
    def on_finish_button_clicked(self):

        current_year = self.year_cbox.itemData(self.year_cbox.currentIndex())
        # current_id = self.object_cbox.itemData(self.object_cbox.currentIndex())

        parcel_id = None
        person_id = None
        contract_id = None
        au2 = None

        old_parcel = self.session.query(CaUBParcel).filter(CaUBParcel.old_parcel_id == self.old_parcel_id).one()

        parcel_count = self.session.query(CaParcelTbl).\
            filter(CaParcelTbl.geometry.ST_Equals(old_parcel.geometry)).count()
        if parcel_count > 0:
            parcel = self.session.query(CaParcelTbl). \
                filter(CaParcelTbl.geometry.ST_Equals(old_parcel.geometry)).first()
            parcel_id = parcel.parcel_id
            au2 = parcel.au2

        if not self.one_select_chbox.isChecked():

            selected_row = self.payment_twidget.currentRow()
            item = self.payment_twidget.item(selected_row, 1)
            if not item:
                PluginUtils.show_message(self, u'Анхааруулга', u'Та оруулах мэдээллээ жагсаалтаас заавал/зөвхөн нэг/ сонгоно уу!')
                return

        if not parcel_id:
            PluginUtils.show_message(self, u'Анхааруулга', u'Нэгж талбар үндсэн мэдээллийн санд бүртгэгдээгүй байна.')
            return

        apps = self.session.query(CtApplication).\
            filter(CtApplication.parcel == parcel_id).all()
        for app in apps:
            app_contracts = self.session.query(CtContractApplicationRole).\
                filter(CtContractApplicationRole.application == app.app_id).\
                filter(CtContractApplicationRole.role == 20).all()
            for app_contract in app_contracts:
                contract_id = app_contract.contract
                contract = self.session.query(CtContract).filter(CtContract.contract_id == app_contract.contract).one()
                if contract.status != 10 or contract.status != 20 or contract.status != 50 or contract.status != 60:
                    contract_id = contract.contract_id
                    app_type = app.app_type
                    app_persons = self.session.query(CtApplicationPersonRole).filter(
                        CtApplicationPersonRole.application == app.app_id).all()
                    for app_person in app_persons:
                        set_app_role = self.session.query(SetApplicationTypePersonRole).\
                            filter(SetApplicationTypePersonRole.type == app_type).\
                            filter(SetApplicationTypePersonRole.role == app_person.role).one()
                        if set_app_role.is_owner:
                            person_id = app_person.person

        if not contract_id:
            PluginUtils.show_message(self, u'Анхааруулга',
                                     u'Үндсэн мэдээллийн санд гэрээний бүртгэл үүсээгүй байна.')
            return

        if not person_id:
            PluginUtils.show_message(self, u'Анхааруулга', u'Үндсэн мэдээллийн санд хуулийн этгээдийн бүртгэл байхгүй байна.')
            return

        message_box = QMessageBox()
        message_box.setText(self.tr("Do you want to import for base database?"))

        yes_button = message_box.addButton(self.tr("Yes"), QMessageBox.ActionRole)
        message_box.addButton(self.tr("No"), QMessageBox.ActionRole)
        message_box.exec_()

        if message_box.clickedButton() != yes_button:
            return

        values = self.session.query(UbFeeHistory).\
            filter(UbFeeHistory.pid == self.old_parcel_id).all()
        date_time_string = QDateTime.currentDateTime().toString(Constants.DATABASE_DATETIME_FORMAT)
        is_one = False

        if not self.one_select_chbox.isChecked():

            selected_row = self.payment_twidget.currentRow()
            item = self.payment_twidget.item(selected_row, 1)
            if not item:
                # PluginUtils.show_message(self, u'Анхааруулга', u'Та оруулах мэдээллээ жагсаалтаас заавал/зөвхөн нэг/ сонгоно уу!')
                return
            current_id = item.data(Qt.UserRole + 1)

            item_year = self.payment_twidget.item(selected_row, 3)
            current_year = item_year.data(Qt.UserRole)
            value = self.session.query(UbFeeHistory).filter(UbFeeHistory.id == current_id).one()
            if value.status == 1:
                PluginUtils.show_error(self, u'Анхааруулга',
                                   u'{0} оны мэдээлэл засагдаагүй тул үндсэн төлөлт болж оруулах боломжгүй. Зөвхөн засагдсан оны мэдээлэл орохыг анхаарна уу!'
                                   .format(current_year))
                return
            count = self.session.query(PaPaymentPaid). \
                filter(PaPaymentPaid.contract_id == contract_id). \
                filter(PaPaymentPaid.person_id == person_id). \
                filter(PaPaymentPaid.paid_year == current_year).count()
            if count == 0:
                total_amount = 0
                object = PaPaymentPaid()
                object.person_id = person_id
                object.contract_id = contract_id
                object.parcel_id = parcel_id
                object.au2 = au2
                object.paid_year = current_year
                object.type_id = 1

                object.invalid_amount = value.invalid_payment
                object.remainning_amount = value.paid_before_less
                object.earning_amount = value.paid_fund
                object.quarter_four = value.paid_year
                if value.paid_less:
                    object.year_amount = value.paid_less
                else:
                    object.year_amount = value.paid_over

                object.imposition_year_amount = value.payment_year
                object.imposition_total_amount = \
                    value.payment_year if value.payment_year is not None else 0 + \
                                                                              value.payment_before_less if value.payment_before_less is not None else 0 - \
                                                                                                                                                      value.payment_before_over if value.payment_before_over is not None else 0 + \
                                                                                                                                                                                                                              value.payment_fund if value.payment_fund is not None else 0 + \
                                                                                                                                                                                                                                                                                        value.payment_fund if value.payment_loss is not None else 0

                object.contract_amount = value.payment_contract

                object.total_amount = value.paid_before_less + value.paid_year + value.paid_fund

                object.created_at = datetime.strptime(date_time_string, Constants.PYTHON_DATETIME_FORMAT)

                self.session.add(object)

        else:
            for value in values:
                if is_one:
                    break
                current_year = value.current_year

                if value.status == 1:
                    PluginUtils.show_error(self, u'Анхааруулга',
                                           u'{0} оны мэдээлэл засагдаагүй тул үндсэн төлөлт болж оруулах боломжгүй. Зөвхөн засагдсан оны мэдээлэл орохыг анхаарна уу!'
                                           .format(current_year))
                else:
                    count = self.session.query(PaPaymentPaid).\
                        filter(PaPaymentPaid.contract_id == contract_id).\
                        filter(PaPaymentPaid.person_id == person_id).\
                        filter(PaPaymentPaid.paid_year == current_year).count()
                    if count == 0:
                        total_amount = 0
                        object = PaPaymentPaid()
                        object.person_id = person_id
                        object.contract_id = contract_id
                        object.parcel_id = parcel_id
                        object.au2 = au2
                        object.paid_year = current_year
                        object.type_id = 1


                        object.invalid_amount = value.invalid_payment
                        object.remainning_amount = value.paid_before_less
                        object.earning_amount = value.paid_fund
                        object.quarter_four = value.paid_year
                        if value.paid_less:
                            object.year_amount = value.paid_less
                        else:
                            object.year_amount = value.paid_over

                        object.imposition_year_amount = value.payment_year
                        object.imposition_total_amount = \
                            value.payment_year if value.payment_year is not None else 0 + \
                                      value.payment_before_less if value.payment_before_less is not None else 0 - \
                                      value.payment_before_over if value.payment_before_over is not None else 0 + \
                                      value.payment_fund if value.payment_fund is not None else 0 + \
                                      value.payment_fund if value.payment_loss is not None else 0

                        object.contract_amount = value.payment_contract

                        object.total_amount = value.paid_before_less + value.paid_year + value.paid_fund

                        object.created_at = datetime.strptime(date_time_string, Constants.PYTHON_DATETIME_FORMAT)

                        self.session.add(object)

        self.session.commit()
        self.__start_fade_out_timer()
        self.__list_of_paid()
        self.__list_of_payment()

    def __start_fade_out_timer(self):

        # self.error_label.setVisible(False)
        self.status_label.setVisible(True)
        self.timer = QTimer()
        self.timer.timeout.connect(self.__fade_status_message)
        self.time_counter = 500
        self.timer.start(10)

    def __fade_status_message(self):

        opacity = int(self.time_counter * 0.5)
        self.status_label.setStyleSheet("QLabel {color: rgba(255,0,0," + str(opacity) + ");}")
        self.status_label.setText(self.tr('Changes applied successfully.'))
        if self.time_counter == 0:
            self.timer.stop()
        self.time_counter -= 1

    @pyqtSlot(int)
    def on_year_sbox_valueChanged(self, sbox_value):

        print ''

    @pyqtSlot()
    def on_find_button_clicked(self):

        employee = DatabaseUtils.current_employee()
        department_id = employee.department_id
        city_type = 2
        if department_id == 120:
            city_type = 1

        au2 = DatabaseUtils.working_l2_code()
        values = self.session.query(UbFeeHistory).\
            filter(UbFeeHistory.au2 == au2).\
            filter(UbFeeHistory.city_type == city_type)

        if self.old_parcel_id_edit.text():
            old_parcel_id = self.old_parcel_id_edit.text()
            old_parcel_id_like = '%' + old_parcel_id + '%'
            values = values.filter(func.lower(UbFeeHistory.pid).like(func.lower(old_parcel_id_like)))
        if self.contract_no_edit.text():
            contract_no = self.contract_no_edit.text()
            contract_no_like = '%' + contract_no + '%'
            values = values.filter(func.lower(UbFeeHistory.contract_no).like(func.lower(contract_no_like)))
        if self.person_id_edit.text():
            person_register = self.person_id_edit.text()
            person_register_like = '%' + person_register + '%'
            values = values.filter(func.lower(UbFeeHistory.person_register).like(func.lower(person_register_like)))

        self.payment_twidget.setRowCount(0)

        for value in values:
            count = self.payment_twidget.rowCount()
            self.payment_twidget.insertRow(count)

            status_desc = u'Засагдаагүй'
            status_code = 1
            if value.status == 2:
                status_desc = u'Засагдсан'
                status_code = 2
            item = QTableWidgetItem(unicode(status_desc))
            item.setData(Qt.UserRole, status_code)
            self.payment_twidget.setItem(count, 0, item)

            city_type = u''
            if value.city_type == 1:
                city_type = u'Нийслэл'
            if value.city_type == 2:
                city_type = u'Дүүрэг'
            item = QTableWidgetItem(city_type)
            item.setData(Qt.UserRole, value.city_type)
            item.setData(Qt.UserRole + 1, value.id)
            self.payment_twidget.setItem(count, 1, item)

            item = QTableWidgetItem(unicode(value.pid))
            item.setData(Qt.UserRole, value.pid)
            self.payment_twidget.setItem(count, 2, item)

            item = QTableWidgetItem(unicode(value.current_year))
            item.setData(Qt.UserRole, value.current_year)
            self.payment_twidget.setItem(count, 3, item)

            item = QTableWidgetItem(value.person_register)
            item.setData(Qt.UserRole, value.person_register)
            self.payment_twidget.setItem(count, 4, item)

            item = QTableWidgetItem(value.contract_no)
            item.setData(Qt.UserRole, value.contract_no)
            self.payment_twidget.setItem(count, 5, item)

            item = QTableWidgetItem(unicode(value.payment_contract))
            item.setData(Qt.UserRole, value.payment_contract)
            self.payment_twidget.setItem(count, 6, item)

            item = QTableWidgetItem(str(value.payment_year))
            item.setData(Qt.UserRole, value.payment_year)
            self.payment_twidget.setItem(count, 7, item)

            item = QTableWidgetItem(str(value.payment_total))
            item.setData(Qt.UserRole, value.city_type)
            self.payment_twidget.setItem(count, 8, item)

            item = QTableWidgetItem(str(value.payment_before_less))
            item.setData(Qt.UserRole, value.payment_before_less)
            self.payment_twidget.setItem(count, 9, item)

            item = QTableWidgetItem(str(value.payment_before_over))
            item.setData(Qt.UserRole, value.payment_before_over)
            self.payment_twidget.setItem(count, 10, item)

            item = QTableWidgetItem(str(value.paid_city))
            item.setData(Qt.UserRole, value.paid_city)
            self.payment_twidget.setItem(count, 11, item)

            item = QTableWidgetItem(str(value.paid_district))
            item.setData(Qt.UserRole, value.paid_district)
            self.payment_twidget.setItem(count, 12, item)

            item = QTableWidgetItem(str(value.invalid_payment))
            item.setData(Qt.UserRole, value.invalid_payment)
            self.payment_twidget.setItem(count, 13, item)

            item = QTableWidgetItem(str(value.paid_before_less))
            item.setData(Qt.UserRole, value.paid_before_less)
            self.payment_twidget.setItem(count, 14, item)

    @pyqtSlot(QTableWidgetItem)
    def on_payment_twidget_itemDoubleClicked(self, item):

        soum = DatabaseUtils.working_l2_code()
        if not soum:
            PluginUtils.show_message(self, self.tr("Connection Error"), self.tr("Please connect to database!!!"))
            return
        layer = LayerUtils.layer_by_data_source("data_ub", 'ca_ub_parcel')

        selected_row = self.payment_twidget.currentRow()
        item = self.payment_twidget.item(selected_row, 1)
        id = item.data(Qt.UserRole + 1)

        value = self.session.query(UbFeeHistory). \
            filter(UbFeeHistory.id == id).first()

        old_parcel_id = str(value.pid)

        self.__select_feature(old_parcel_id, layer)

    def __select_feature(self, parcel_id, layer):

        expression = " old_parcel_id = \'" + parcel_id + "\'"
        request = QgsFeatureRequest()
        request.setFilterExpression(expression)
        feature_ids = []
        if layer:
            iterator = layer.getFeatures(request)

            for feature in iterator:
                feature_ids.append(feature.id())
            if len(feature_ids) == 0:
                self.status_label.setText(self.tr("No parcel assigned"))

            layer.setSelectedFeatures(feature_ids)
            self.plugin.iface.mapCanvas().zoomToSelected(layer)

    @pyqtSlot(int)
    def on_all_status_chbox_stateChanged(self, state):

        if self.all_status_chbox.isChecked():
            for row in range(self.payment_twidget.rowCount()):
                status_desc = u'Засагдсан'
                status_code = 2
                item = self.payment_twidget.item(row, 0)
                item.setText(status_desc)
                item.setData(Qt.UserRole, status_code)
        else:
            for row in range(self.payment_twidget.rowCount()):
                status_desc = u'Засагдаагүй'
                status_code = 1
                item = self.payment_twidget.item(row, 0)
                item.setText(status_desc)
                item.setData(Qt.UserRole, status_code)