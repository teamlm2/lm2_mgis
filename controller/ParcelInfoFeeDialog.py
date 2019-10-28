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

class ParcelInfoFeeDialog(QDialog, Ui_ParcelInfoFeeDialog):

    def __init__(self, old_parcel_id, person_id, is_find, parent=None):

        super(ParcelInfoFeeDialog, self).__init__(parent)
        self.setupUi(self)
        self.session = SessionHandler().session_instance()
        self.old_parcel_id = old_parcel_id
        self.person_id = person_id

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

        self.__setup_cbox()

        # if is_find:
        #     self.__load_fee(self.person_id, self.old_parcel_id)
        # else:
        #     self.find_gbox.setEnabled(True)
        #     self.old_parcel_id_edit.setEnabled(True)
        #     self.person_id_edit.setEnabled(True)

    def __setup_cbox(self):

        values = self.session.query(UbFeeHistory.current_year).filter(UbFeeHistory.pid == self.old_parcel_id).all()

        for value in values:
            self.year_cbox.addItem(str(value.current_year), value.current_year)

    @pyqtSlot(int)
    def on_year_cbox_currentIndexChanged(self, index):

        self.__clear_all()
        current_year = self.year_cbox.itemData(self.year_cbox.currentIndex())
        self.__load_fee_history(current_year)

    def __load_fee_history(self, current_year):

        value = self.session.query(UbFeeHistory).\
            filter(UbFeeHistory.pid == self.old_parcel_id).\
            filter(UbFeeHistory.current_year == current_year).first()

        print value.payment_year

        self.payment_contract_edit.setText(value.contract_no if value.contract_no is not None else '')
        self.payment_area_edit.setText(str(value.document_area) if value.document_area is not None else '0')
        self.payment_zoriulalt_edit.setText(str(value.zoriulalt) if value.zoriulalt is not None else '')
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

        self.payment_contract_edit.clear()
        self.payment_area_edit.clear()
        self.payment_zoriulalt_edit.clear()
        self.payment_name_edit.clear()
        self.decsription_txt.clear()

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