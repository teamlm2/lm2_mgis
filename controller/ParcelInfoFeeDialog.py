# coding=utf8
import os

__author__ = 'ankhbold'
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, or_, extract
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

class ParcelInfoFeeDialog(QDialog, Ui_ParcelInfoFeeDialog):

    def __init__(self, old_parcel_id, person_id, is_find, parent=None):

        super(ParcelInfoFeeDialog, self).__init__(parent)
        self.setupUi(self)
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

        self.select_years = [2014, 2015, 2016, 2017, 2018]
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

        self.payment_twidget.setAlternatingRowColors(True)
        self.payment_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.payment_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.payment_twidget.setSelectionMode(QTableWidget.SingleSelection)

    def __list_of_payment(self):

        self.payment_twidget.setRowCount(0)

        values = self.session.query(UbFeeHistory). \
            filter(UbFeeHistory.pid == self.old_parcel_id).all()

        for value in values:
            count = self.payment_twidget.rowCount()
            self.payment_twidget.insertRow(count)

            city_type = u''
            if value.city_type == 1:
                city_type = u'Нийслэл'
            if value.city_type == 2:
                city_type = u'Дүүрэг'
            item = QTableWidgetItem(city_type)
            item.setData(Qt.UserRole, value.city_type)
            item.setData(Qt.UserRole + 1, value.id)
            self.payment_twidget.setItem(count, 0, item)

            item = QTableWidgetItem(str(value.current_year))
            item.setData(Qt.UserRole, value.current_year)
            self.payment_twidget.setItem(count, 1, item)

            item = QTableWidgetItem(value.person_register)
            item.setData(Qt.UserRole, value.person_register)
            self.payment_twidget.setItem(count, 2, item)

            item = QTableWidgetItem(value.contract_no)
            item.setData(Qt.UserRole, value.contract_no)
            self.payment_twidget.setItem(count, 3, item)

            item = QTableWidgetItem(str(value.payment_contract))
            item.setData(Qt.UserRole, value.payment_contract)
            self.payment_twidget.setItem(count, 4, item)

            item = QTableWidgetItem(str(value.payment_year))
            item.setData(Qt.UserRole, value.payment_year)
            self.payment_twidget.setItem(count, 5, item)

            item = QTableWidgetItem(str(value.payment_total))
            item.setData(Qt.UserRole, value.city_type)
            self.payment_twidget.setItem(count, 6, item)

            item = QTableWidgetItem(str(value.payment_before_less))
            item.setData(Qt.UserRole, value.payment_before_less)
            self.payment_twidget.setItem(count, 7, item)

            item = QTableWidgetItem(str(value.payment_before_over))
            item.setData(Qt.UserRole, value.payment_before_over)
            self.payment_twidget.setItem(count, 8, item)

            item = QTableWidgetItem(str(value.paid_city))
            item.setData(Qt.UserRole, value.paid_city)
            self.payment_twidget.setItem(count, 9, item)

            item = QTableWidgetItem(str(value.paid_district))
            item.setData(Qt.UserRole, value.paid_district)
            self.payment_twidget.setItem(count, 10, item)

            item = QTableWidgetItem(str(value.invalid_payment))
            item.setData(Qt.UserRole, value.invalid_payment)
            self.payment_twidget.setItem(count, 11, item)

            item = QTableWidgetItem(str(value.paid_before_less))
            item.setData(Qt.UserRole, value.paid_before_less)
            self.payment_twidget.setItem(count, 12, item)

    def __list_of_paid(self):

        self.paid_twidget.setRowCount(0)
        parcel_id = None
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
            self.object_cbox.addItem(value.pid + ': (' + value.person_register + ') ' + value.ner, value.id)

    @pyqtSlot(int)
    def on_object_cbox_currentIndexChanged(self, index):

        self.__clear_all()
        current_id = self.object_cbox.itemData(self.object_cbox.currentIndex())

        self.__load_fee_history(current_id)

    @pyqtSlot(QTableWidgetItem)
    def on_payment_twidget_itemClicked(self, item):

        # self.__clear_all()

        selected_row = self.payment_twidget.currentRow()
        item = self.payment_twidget.item(selected_row, 0)
        id = item.data(Qt.UserRole + 1)

        value = self.session.query(UbFeeHistory). \
            filter(UbFeeHistory.id == id).first()

        if value.city_type:
            self.city_type_cbox.setCurrentIndex(self.city_type_cbox.findData(value.city_type))

        if value.current_year:
            self.year_cbox.setCurrentIndex(self.year_cbox.findData(value.current_year))

        if value.id:
            self.object_cbox.setCurrentIndex(self.object_cbox.findData(value.id))
        # self.__load_fee_history(id)

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
    def on_save_button_clicked(self):

        current_id = self.object_cbox.itemData(self.object_cbox.currentIndex())
        self.selected_year = self.year_cbox.itemData(self.year_cbox.currentIndex())
        city_type = self.city_type_cbox.itemData(self.city_type_cbox.currentIndex())

        if current_id:
            object = self.session.query(UbFeeHistory).filter(UbFeeHistory.id == current_id).one()

            object.contract_no = self.payment_contract_edit.text()
            object.document_area = float(self.payment_area_edit.text())
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
            object.city_type = city_type
        else:
            object = UbFeeHistory()

            object.contract_no = self.payment_contract_edit.text()
            object.document_area = float(self.payment_area_edit.text())
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

            object.current_year = self.selected_year
            object.pid = self.old_parcel_id
            object.person_register = self.person_id
            object.city_type = city_type

            self.session.add(object)

        self.session.commit()

        self.__setup_cbox()
        self.year_cbox.setCurrentIndex(self.year_cbox.findData(self.selected_year))
        self.__start_fade_out_timer()
        self.__list_of_payment()

    @pyqtSlot()
    def on_finish_button_clicked(self):

        current_year = self.year_cbox.itemData(self.year_cbox.currentIndex())
        current_id = self.object_cbox.itemData(self.object_cbox.currentIndex())
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
        for value in values:
            current_year = value.current_year
            if self.one_select_chbox.isChecked():
                current_year = self.year_cbox.itemData(self.year_cbox.currentIndex())
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
                object.imposition_total_amount = value.payment_year + value.payment_before_less - value.payment_before_over + value.payment_fund + value.payment_loss

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