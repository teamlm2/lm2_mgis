# coding=utf8
__author__ = 'B.Ankhbold'

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from geoalchemy2.elements import WKTElement
from qgis.core import *
from sqlalchemy.exc import SQLAlchemyError
from geoalchemy2 import functions
from geoalchemy2.shape import to_shape
from sqlalchemy import func, or_, and_, desc
from decimal import Decimal
from ..view.Ui_ParcelInfoDialog import Ui_ParcelInfoDialog
from ..controller.ParcelInfoFeeDialog import *
from ..utils.PluginUtils import PluginUtils
from ..utils.LayerUtils import LayerUtils
from ..utils.DatabaseUtils import DatabaseUtils
from ..utils.SessionHandler import SessionHandler
from ..utils.FileUtils import FileUtils
from ..model.CaBuilding import *
from ..model.BsPerson import *
from ..model.CtApplication import *
from ..model.ClApplicationStatus import *
from ..model.ClPersonType import *
from ..model.ClDecisionLevel import *
from ..model.ClContractStatus import *
from ..model.ClPersonRole import *
from ..model.UbGisSubject import *
from ..model.ClDocumentRole import *
from ..model.CtDecision import *
from ..model.CaParcelTbl import *
from ..model.CtContractApplicationRole import *
from ..model.CtRecordApplicationRole import *
from ..model.AuLevel1 import *
from ..model.AuLevel2 import *
from ..model.AuLevel3 import *
from ..model import SettingsConstants
from ..model import Constants
from ..model.SetRightTypeApplicationType import *
from ..model.LM2Exception import LM2Exception
from ..model.ClPositionType import *
from ..model.ClUbEditStatus import *
from ..model.AuMpa import *
from ..model.AuMpaZone import *
from ..model.Enumerations import PersonType, UserRight
from ..model.DatabaseHelper import *
from ..model.CaUBParcelTbl import *
from ..utils.SessionHandler import SessionHandler
from ..utils.FilePath import *
from ..utils.FtpConnection import *
from ..model.SdConfiguration import *
from ..model.ClUbParcelType import *
from .qt_classes.UbDocumentViewDelegate import UbDocumentViewDelegate
from .qt_classes.UbNewDocumentViewDelegate import UbNewDocumentViewDelegate
import math
import locale
import os
import pyproj
import urllib2
import shutil
import sys
import datetime
from ftplib import FTP, error_perm
from contextlib import closing
from difflib import SequenceMatcher
import urllib
import urllib2
import json
import codecs

DELETE_STATUS = 40

class ParcelInfoDialog(QDockWidget, Ui_ParcelInfoDialog, DatabaseHelper):

    RIGTHTYPE, CODEIDCARD, NAME, FIRSTNAME, OLD_PARCEL_ID, PARCEL_ID, DECISION_NO, DECISION_DATE, CONTRACT_NO, CONTRACT_DATE = range(10)

    zoriulalt = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    STREET_NAME = 7
    KHASHAA_NAME = 6
    GEO_ID = 2
    # OLD_PARCEL_ID = 1

    def __init__(self, plugin, parent=None):

        super(ParcelInfoDialog, self).__init__(parent)
        DatabaseHelper.__init__(self)

        # self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.plugin = plugin
        self.setupUi(self)
        self.session = SessionHandler().session_instance()
        self.keyPressEvent = self.newOnkeyPressEvent
        self.is_find_ubgis = True
        self.parcel_id = None
        # self.__create_subject_view()
        self.application = None
        self.contract = None
        self.record = None
        # self.contract_gbox.setVisible(False)
        # self.record_gbox.setVisible(False)
        self.__old_parcel_no = None
        self.__building_id_list = None
        self.__geometry = None
        self.__building_area = None
        self.__feature = None
        self.__overview_map_scale = None
        self.__coord_transform = None
        self.__second_page_enabled = False
        self.isSave = True

        self.__setup_validators()
        self.__setup_table_widget()
        self.select_years = [2019, 2018, 2017, 2016, 2015, 2014]
        self.__setup_cbox()

        self.person_tabwidget.currentChanged.connect(self.__tab_widget_onChange)  # changed!
        # self.__setup_combo_boxes()

        self.__setup_permissions()
        self.duration_sbox.setMaximum(60)
        self.tab_index = 0
        validator = QtGui.QDoubleValidator()
        self.find_x_coordinate_edit.setValidator(validator)
        self.find_y_coordinate_edit.setValidator(validator)
        # self.__doc_tree_view()
        self.find_tab.currentChanged.connect(self.onChangetab)

        self.decision_date.dateChanged.connect(self.on_decision_date_DateChanged)
        self.contract_date.dateChanged.connect(self.on_contract_date_DateChanged)
        self.end_date.dateChanged.connect(self.on_end_date_DateChanged)
        self.own_date.dateChanged.connect(self.on_own_date_DateChanged)

    def __tab_widget_onChange(self, index):

        if index == 1:
            aimag_list = []
            try:
                aimag_list = self.session.query(AuLevel1.name, AuLevel1.code). \
                    filter(AuLevel1.code != '013').filter(AuLevel1.code != '012').order_by(AuLevel1.name.desc()).all()

            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("Database Query Error"),
                                       self.tr("Could not execute: {0}").format(e.message))
                self.reject()

            self.aimag_cbox.addItem("*", -1)

            for auLevel1 in aimag_list:
                self.aimag_cbox.addItem(auLevel1.name, auLevel1.code)

            working_aimag = DatabaseUtils.working_l1_code()
            working_soum = DatabaseUtils.working_l2_code()
            self.aimag_cbox.setCurrentIndex(self.aimag_cbox.findData(working_aimag))
            self.soum_cbox.setCurrentIndex(self.soum_cbox.findData(working_soum))

    @pyqtSlot(int)
    def on_soum_cbox_currentIndexChanged(self, index):

        soum = self.soum_cbox.itemData(index)

        self.bag_cbox.clear()
        self.bag_cbox.addItem("*", -1)
        bag_list = []

        if soum == -1 or not soum:
            return
        else:
            try:
                bag_list = self.session.query(AuLevel3.code, AuLevel3.name).filter(AuLevel3.code.like(soum + "%")).all()
            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("Database Query Error"),
                                       self.tr("Could not execute: {0}").format(e.message))
                self.reject()

        for au_level3 in bag_list:
            self.bag_cbox.addItem(au_level3.name, au_level3.code)

    @pyqtSlot(int)
    def on_aimag_cbox_currentIndexChanged(self, index):

        aimag = self.aimag_cbox.itemData(index)
        self.soum_cbox.clear()
        self.bag_cbox.clear()

        self.soum_cbox.addItem("*", -1)
        self.bag_cbox.addItem("*", -1)

        soum_list = []
        bag_list = []

        if aimag == -1:
            soum_list = self.session.query(AuLevel2).all()
            for au_level2 in soum_list:
                if au_level2.code[:2] == '01':
                    self.soum_cbox.addItem(au_level2.name, au_level2.code)

        else:
            try:

                soum_list = self.session.query(AuLevel2.name, AuLevel2.code).filter(
                    AuLevel2.code.like(aimag + "%")).all()
                bag_list = self.session.query(AuLevel3.name, AuLevel3.code).filter(
                    AuLevel3.code.like(aimag + "%")).all()

            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("Database Query Error"),
                                       self.tr("Could not execute: {0}").format(e.message))
                self.reject()

            for au_level2 in soum_list:
                self.soum_cbox.addItem(au_level2.name, au_level2.code)

            for au_level3 in bag_list:
                self.bag_cbox.addItem(au_level3.name, au_level3.code)


    def __setup_combo_boxes(self):

        self.aimag_cbox.clear()
        aimag_list = []
        try:
            aimag_list = self.session.query(AuLevel1.name, AuLevel1.code).all()

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("Database Query Error"), self.tr("Could not execute: {0}").format(e.message))
            self.reject()

        self.aimag_cbox.addItem("*", -1)

        for auLevel1 in aimag_list:
            self.aimag_cbox.addItem(auLevel1.name, auLevel1.code)

        working_aimag = DatabaseUtils.working_l1_code()
        working_soum = DatabaseUtils.working_l2_code()
        self.aimag_cbox.setCurrentIndex(self.aimag_cbox.findData(working_aimag))
        self.soum_cbox.setCurrentIndex(self.soum_cbox.findData(working_soum))


    def __is_aimag_tool(self):

        database = QSettings().value(SettingsConstants.DATABASE_NAME)
        if database:
            au1 = database.split('_')[1][:2]
            if au1:
                if au1 != '11':
                    self.parcel_tab_widget.removeTab(
                        self.parcel_tab_widget.indexOf(self.legal_representative_tab))


    def __setup_permissions(self):

        user_name = QSettings().value(SettingsConstants.USER)
        user_rights = DatabaseUtils.userright_by_name(user_name)
        officer = self.session.query(SetRole) \
            .filter(SetRole.user_name == QSettings().value(SettingsConstants.USER)) \
            .filter(SetRole.is_active == True).one()

        self.finish_button.setVisible(False)
        if officer.position == 11:
            self.finish_button.setVisible(True)
            self.edit_status_cbox.clear()
            edit_statuses = self.session.query(ClUbEditStatus).all()
            self.edit_status_cbox.addItem("*", -1)
            for item in edit_statuses:
                self.edit_status_cbox.addItem(str(item.code) + ": " + item.description, item.code)

        if officer.position == 12:
            self.finish_button.setVisible(True)
            self.edit_status_cbox.clear()
            edit_statuses = self.session.query(ClUbEditStatus).all()
            self.edit_status_cbox.addItem("*", -1)
            for item in edit_statuses:
                self.edit_status_cbox.addItem(str(item.code) + ": " + item.description, item.code)

        if officer.position == 13:
            self.finish_button.setVisible(True)
            self.edit_status_cbox.clear()
            edit_statuses = self.session.query(ClUbEditStatus).all()
            self.edit_status_cbox.addItem("*", -1)
            for item in edit_statuses:
                self.edit_status_cbox.addItem(str(item.code) + ": " + item.description, item.code)

        if officer.position == 10:
            self.finish_button.setVisible(True)
            self.edit_status_cbox.clear()
            edit_statuses = self.session.query(ClUbEditStatus).all()
            self.edit_status_cbox.addItem("*", -1)
            for item in edit_statuses:
                self.edit_status_cbox.addItem(str(item.code) + ": " + item.description, item.code)

        if officer.position == 17:
            self.finish_button.setVisible(True)
            self.edit_status_cbox.clear()
            edit_statuses = self.session.query(ClUbEditStatus).all()
            self.edit_status_cbox.addItem("*", -1)
            for item in edit_statuses:
                self.edit_status_cbox.addItem(str(item.code) + ": " + item.description, item.code)


        # else:
        #     self.finish_button.setVisible(False)

        # self.__disable_all()
        #
        # if UserRight.cadastre_update in user_rights:
        #
        #     self.finish_button.setEnabled(True)

    def __disable_all(self):

        self.finish_button.setEnabled(False)

    def __create_subject_view(self):

        sql = ""
        soum_code = DatabaseUtils.working_l2_code()
        if not sql:
            sql = "Create temp view all_subject_search as" + "\n"
            select = " SELECT * FROM s"+soum_code+".all_subject "

            sql = sql + select

        try:
            self.session.execute(sql)
            # self.commit()

        except SQLAlchemyError, e:
            PluginUtils.show_message(self, self.tr("LM2", "Sql Error"), e.message)
            return

    def __setup_validators(self):

        self.capital_asci_letter_validator = QRegExpValidator(QRegExp("[A-Z]"), None)
        self.lower_case_asci_letter_validator = QRegExpValidator(QRegExp("[a-z]"), None)

        self.email_validator = QRegExpValidator(QRegExp("[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,4}"), None)

        self.www_validator = QRegExpValidator(QRegExp("www\\.[a-z0-9._%+-]+\\.[a-z]{2,4}"), None)

        self.numbers_validator = QRegExpValidator(QRegExp("[1-9][0-9]+( *,*[1-9][0-9]+)*"), None)
        self.int_validator = QRegExpValidator(QRegExp("[0-9]+"), None)
        self.zoriulalt_edit.setValidator(self.numbers_validator)

        self.contract_cert_edit.setValidator(self.numbers_validator)
        self.record_cert_edit.setValidator(self.numbers_validator)

    def __setup_cbox(self):

        ftp_host = QSettings().value(SettingsConstants.FTP_IP)

        self.ftp_host_edit.setText(ftp_host)

        # try:
        application_types = self.session.query(ClApplicationType). \
            order_by(ClApplicationType.code).all()
        statuses = self.session.query(ClApplicationStatus).order_by(ClApplicationStatus.code).all()
        landuse_types = self.session.query(ClLanduseType).all()
        person_types = self.session.query(ClPersonType).all()
        # decision_levels = self.session.query(ClDecisionLevel).filter(or_(ClDecisionLevel.code == 10, ClDecisionLevel.code == 20)).all()
        decision_levels = self.session.query(ClDecisionLevel).all()
        contract_statuses = self.session.query(ClContractStatus).all()
        right_types = self.session.query(ClRightType).all()
        edit_statuses = self.session.query(ClUbEditStatus).filter(ClUbEditStatus.code != DELETE_STATUS).all()

        ub_parcel_types = self.session.query(ClUbParcelType).all()

        for item in ub_parcel_types:
            self.ub_parcel_type_cbox.addItem(item.description, item.code)

        # except SQLAlchemyError, e:
        #     PluginUtils.show_error(self, self.tr("File Error"),
        #                            self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

        for item in right_types:
            self.rigth_type_cbox.addItem(item.description, item.code)

        for item in contract_statuses:
            self.contract_status_cbox.addItem(item.description, item.code)

        for item in decision_levels:
            self.decision_level_cbox.addItem(item.description, item.code)

        for item in person_types:
            self.person_type_cbox.addItem(item.description, item.code)

        for item in landuse_types:
            self.parcel_landuse_cbox.addItem(str(item.code) + ": " + item.description, item.code)

        self.edit_status_cbox.addItem("*", -1)
        for item in edit_statuses:
            self.edit_status_cbox.addItem(str(item.code) + ": " + item.description, item.code)

        self.fee_year_layer_cbox.clear()
        for value in self.select_years:
            self.fee_year_layer_cbox.addItem(str(value), value)

    def __setup_table_widget(self):

        self.right_holder_twidget.setAlternatingRowColors(True)
        self.right_holder_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.right_holder_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.right_holder_twidget.setSelectionMode(QTableWidget.SingleSelection)

        self.doc_twidget.setAlternatingRowColors(True)
        self.doc_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.doc_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.doc_twidget.setSelectionMode(QTableWidget.SingleSelection)

        self.doc_twidget.horizontalHeader().resizeSection(0, 50)
        self.doc_twidget.horizontalHeader().resizeSection(1, 250)
        self.doc_twidget.horizontalHeader().resizeSection(2, 50)

        delegate = UbDocumentViewDelegate(self.doc_twidget, self)
        self.doc_twidget.setItemDelegate(delegate)

        self.new_doc_twidget.setAlternatingRowColors(True)
        self.new_doc_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.new_doc_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.new_doc_twidget.setSelectionMode(QTableWidget.SingleSelection)

        self.new_doc_twidget.horizontalHeader().resizeSection(0, 50)
        self.new_doc_twidget.horizontalHeader().resizeSection(1, 250)
        self.new_doc_twidget.horizontalHeader().resizeSection(2, 50)

        new_delegate = UbNewDocumentViewDelegate(self.new_doc_twidget, self)
        self.new_doc_twidget.setItemDelegate(new_delegate)

        self.doc_info_twidget.setAlternatingRowColors(True)
        self.doc_info_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.doc_info_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.doc_info_twidget.cellChanged.connect(self.on_doc_info_twidget_cellChanged)

        self.fee_info_twidget.setAlternatingRowColors(True)
        self.fee_info_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.fee_info_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.fee_info_twidget.cellChanged.connect(self.on_fee_info_twidget_cellChanged)

        self.landuk_info_twidget.setAlternatingRowColors(True)
        self.landuk_info_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.landuk_info_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.landuk_info_twidget.cellChanged.connect(self.on_landuk_info_twidget_cellChanged)

        self.landuk_mortgage_twidget.setAlternatingRowColors(True)
        self.landuk_mortgage_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.landuk_mortgage_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        # self.landuk_mortgage_twidget.cellChanged.connect(self.on_fee_info_twidget_cellChanged)

        self.lpis_info_twidget.setAlternatingRowColors(True)
        self.lpis_info_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.lpis_info_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.lpis_info_twidget.cellChanged.connect(self.on_lpis_info_twidget_cellChanged)

        self.lpis_co_owner_twidget.setAlternatingRowColors(True)
        self.lpis_co_owner_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.lpis_co_owner_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        # self.lpis_co_owner_twidget.cellChanged.connect(self.on_fee_info_twidget_cellChanged)

    def __update_ui(self):

        self.setWindowTitle(self.tr('Old Parcel ID: <{0}>. Select the decision.'.format(self.__old_parcel_no)))
        self.right_holder_twidget.clearContents()
        self.right_holder_twidget.setRowCount(0)

        subjects = self.session.query(UbGisSubject).filter(UbGisSubject.oldpid == self.__old_parcel_no).all()

        for subject in subjects:
            self.__add_subject(subject)

        self.right_holder_twidget.resizeColumnsToContents()

        # if self.right_holder_twidget.rowCount() > 0:
        #     self.right_holder_twidget.selectRow(0)

    def set_parcel_data(self, parcel_no, feature):

        if feature:
            self.__old_parcel_no = parcel_no
            self.__geometry = QgsGeometry(feature.geometry())
            self.__feature = feature
            self.__update_ui()

    def __right_type_description(self, application_type):

        try:
            set_right_type = self.session.query(SetRightTypeApplicationType)\
                .filter(SetRightTypeApplicationType.application_type == application_type).one()

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("Database Query Error"), self.tr("dCould not execute: {0}").format(e.message))
            return None

        return set_right_type.right_type_ref.description

    def __right_type(self, subject):

        right_type = 1

        type = str(subject.gaid)
        if self.__is_number(type):
            if int(type) == 1:
                right_type = 3
            elif int(type) == 2:
                right_type = 2
            elif int(type) == 3:
                right_type = 1
        right_type_subject = self.session.query(ClRightType).filter(ClRightType.code == right_type).one()
        return  right_type_subject

    def __add_subject(self, subject):

        count = self.right_holder_twidget.rowCount()

        if subject:
            self.right_holder_twidget.insertRow(count)
            right_type = self.__right_type(subject)
            item = QTableWidgetItem(right_type.description)
            item.setData(Qt.UserRole, right_type.code)
            self.right_holder_twidget.setItem(count, self.RIGTHTYPE, item)

            item = QTableWidgetItem(unicode(subject.register))
            item.setData(Qt.UserRole, subject.register)
            item.setData(Qt.UserRole + 1, subject.objectid)
            self.right_holder_twidget.setItem(count, self.CODEIDCARD, item)

            item = QTableWidgetItem(unicode(subject.ner))
            item.setData(Qt.UserRole, subject.ner)
            self.right_holder_twidget.setItem(count, self.NAME, item)

            item = QTableWidgetItem(unicode(subject.ovog))
            item.setData(Qt.UserRole, subject.ovog)
            self.right_holder_twidget.setItem(count, self.FIRSTNAME, item)

            item = QTableWidgetItem(str(subject.oldpid))
            item.setData(Qt.UserRole, str(subject.oldpid))
            self.right_holder_twidget.setItem(count, self.OLD_PARCEL_ID, item)

            item = QTableWidgetItem(str(subject.pid))
            item.setData(Qt.UserRole, str(subject.pid))
            self.right_holder_twidget.setItem(count, self.PARCEL_ID, item)

            item = QTableWidgetItem(subject.zovshshiid)
            item.setData(Qt.UserRole, subject.zovshshiid)
            self.right_holder_twidget.setItem(count, self.DECISION_NO, item)

            qt_date = PluginUtils.convert_python_date_to_qt(subject.zovshdate)
            if qt_date is not None:
                item = QTableWidgetItem(qt_date.toString(Constants.DATABASE_DATE_FORMAT))
                item.setData(Qt.UserRole, qt_date)
                self.right_holder_twidget.setItem(count, self.DECISION_DATE, item)
            if right_type.code == 1 or right_type.code == 2:
                item = QTableWidgetItem(subject.gerid)
                item.setData(Qt.UserRole, subject.gerid)
                self.right_holder_twidget.setItem(count, self.CONTRACT_NO, item)

                qt_date = PluginUtils.convert_python_date_to_qt(subject.gerdate)
                if qt_date is not None:
                    item = QTableWidgetItem(qt_date.toString(Constants.DATABASE_DATE_FORMAT))
                    item.setData(Qt.UserRole, qt_date)
                    self.right_holder_twidget.setItem(count, self.CONTRACT_DATE, item)
            else:
                # item = QTableWidgetItem(subject.gerid)
                # item.setData(Qt.UserRole, subject.gerid)
                # self.right_holder_twidget.setItem(count, self.CONTRACT_NO, item)

                qt_date = PluginUtils.convert_python_date_to_qt(subject.uhdate)
                if qt_date is not None:
                    item = QTableWidgetItem(qt_date.toString(Constants.DATABASE_DATE_FORMAT))
                    item.setData(Qt.UserRole, qt_date)
                    self.right_holder_twidget.setItem(count, self.CONTRACT_DATE, item)

    # @pyqtSlot()
    # def on_close_button_clicked(self):
    #
    #     self.reject()

    @pyqtSlot()
    def on_help_button_clicked(self):

        os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/print_cadastral_map.htm")

    @pyqtSlot()
    def on_clear_button_clicked(self):

        self.is_find_ubgis = True
        self.find_button.setEnabled(True)
        self.find_button.setAutoDefault(True)
        self.find_button.setDefault(True)
        self.find_parcel_id_edit.setEnabled(True)
        self.find_person_id_edit.setEnabled(True)
        self.find_firstname_edit.setEnabled(True)
        self.find_lastname_edit.setEnabled(True)
        self.find_street_name_edit.setEnabled(True)
        self.find_khashaa_number_edit.setEnabled(True)

        self.find_x_coordinate_edit.setEnabled(True)
        self.find_y_coordinate_edit.setEnabled(True)

        self.__clear_all()

    def onChangetab(self, i):

        self.tab_index = i

    @pyqtSlot()
    def on_find_button_clicked(self):

        if self.tab_index == 0:
            filter_is_set = False
            self.right_holder_twidget.setRowCount(0)

            subjects = self.session.query(UbGisSubject)

            if self.find_parcel_id_edit.text():
                filter_is_set = True
                value = "%" + self.find_parcel_id_edit.text() + "%"
                subjects = subjects.filter(UbGisSubject.oldpid.like(value))

            if self.find_person_id_edit.text():
                filter_is_set = True
                value = "%" + self.find_person_id_edit.text() + "%"
                subjects = subjects.filter(UbGisSubject.register.like(value))

            if self.find_firstname_edit.text():
                filter_is_set = True
                value = "%"+self.find_firstname_edit.text()+"%"
                subjects = subjects.filter(UbGisSubject.ovog.like(value))

            if self.find_lastname_edit.text():
                filter_is_set = True
                value = "%"+self.find_lastname_edit.text()+"%"
                subjects = subjects.filter(UbGisSubject.ner.like(value))

            if filter_is_set is False:
                PluginUtils.show_message(self, self.tr("None"), self.tr("Please specify a search filter."))
                return

            for subject in subjects.all():
                self.__add_subject(subject)

        if self.tab_index == 2:
            filter_is_set = False
            self.right_holder_twidget.setRowCount(2)

            subjects = self.session.query(UbGisSubject)

            if self.find_street_name_edit.text():
                filter_is_set = True
                value = "%" + self.find_street_name_edit.text() + "%"
                subjects = subjects.filter(UbGisSubject.gudamj.like(value))

            if self.find_khashaa_number_edit.text():
                filter_is_set = True
                value = "%" + self.find_khashaa_number_edit.text() + "%"
                subjects = subjects.filter(UbGisSubject.hashaa.like(value))

            if filter_is_set is False:
                PluginUtils.show_message(self, self.tr("None"), self.tr("Please specify a search filter."))
                return

            for subject in subjects.all():
                self.__add_subject(subject)

            self.right_holder_twidget.resizeColumnsToContents()

            if self.right_holder_twidget.rowCount() > 0:
                self.right_holder_twidget.selectRow(0)
        else:
            if not self.find_x_coordinate_edit.text():
                return
            if not self.find_y_coordinate_edit.text():
                return
            x = float(self.find_x_coordinate_edit.text())
            y = float(self.find_y_coordinate_edit.text())
            self.__find_coordinate(x, y)

    def __is_number(self, s):

        try:
            float(s)  # for int, long and float
        except ValueError:
            try:
                complex(s)  # for complex
            except ValueError:
                return False

        return True

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
                self.error_label.setText(self.tr("No parcel assigned"))

            layer.setSelectedFeatures(feature_ids)
            self.plugin.iface.mapCanvas().zoomToSelected(layer)

    @pyqtSlot(QTableWidgetItem)
    def on_right_holder_twidget_itemDoubleClicked(self, item):

        soum = DatabaseUtils.working_l2_code()
        if not soum:
            PluginUtils.show_message(self, self.tr("Connection Error"), self.tr("Please connect to database!!!"))
            return
        layer = LayerUtils.layer_by_data_source("data_ub", 'ca_ub_parcel')

        selected_row = self.right_holder_twidget.currentRow()
        old_parcel_id = self.right_holder_twidget.item(selected_row, 4).text()

        self.__select_feature(old_parcel_id, layer)

    @pyqtSlot(QTableWidgetItem)
    def on_right_holder_twidget_itemClicked(self, item):

        self.person_street_name_edit.clear()
        self.person_khashaa_edit.clear()
        self.building_edit.clear()
        self.apartment_edit.clear()
        self.decision_num_cbox.clear()

        self.is_find_ubgis = False
        selected_row = self.right_holder_twidget.currentRow()
        person_id  = self.right_holder_twidget.item(selected_row, 1).text()
        object_id = self.right_holder_twidget.item(selected_row, 1).data(Qt.UserRole+1)
        # person info
        person_id = '%'+person_id+'%'
        firstname = ''
        middlename = ''
        name = ''
        phone = ''
        mobile_phone = ''
        person_type = 10
        person_register = ''
        try:
            # subject_persons = self.session.query(UbGisSubject.utas1, UbGisSubject.utas2,UbGisSubject.heid, UbGisSubject.register, UbGisSubject.ovogner, UbGisSubject.ovog, UbGisSubject.ner, UbGisSubject.is_finish).\
            #     filter(UbGisSubject.register.like(person_id)).group_by(UbGisSubject.utas1, UbGisSubject.utas2, UbGisSubject.heid, UbGisSubject.register, UbGisSubject.ovogner, UbGisSubject.ovog, UbGisSubject.ner).all()
            subject_persons = self.session.query(UbGisSubject).filter(UbGisSubject.objectid == object_id).all()
            for subject_person in subject_persons:
                # if subject_person.is_finish:
                #     self.edit_status_cbox.setEnabled(False)
                heid = str(subject_person.heid)
                if self.__is_number(heid):
                    if int(subject_person.heid) == 1:
                        person_type = 10
                    elif int(subject_person.heid) == 2:
                        person_type = 30
                    elif int(subject_person.heid) == 3:
                        person_type = 40
                    elif int(subject_person.heid) == 4:
                        person_type = 50
                    elif int(subject_person.heid) == 5 or str(subject_person.heid) == 5:
                        person_type = 60

                person_register = subject_person.register
                if subject_person.ner:
                    name = subject_person.ner
                if subject_person.utas1:
                    if subject_person.utas1 and len(subject_person.utas1) > 1:
                        mobile_phone = subject_person.utas1
                if subject_person.utas1:
                    if subject_person.utas2 and len(subject_person.utas2) > 1:
                        phone = subject_person.utas2
                if subject_person.ovog:
                    firstname = subject_person.ovog
                if subject_person.ovogner:
                    middlename = subject_person.ovogner

            self.person_type_cbox.setCurrentIndex(self.person_type_cbox.findData(person_type))
            self.personal_id_edit.setText(person_register)
            self.middle_name_edit.setText(middlename)
            self.first_name_edit.setText(firstname)
            self.name_edit.setText(name)

            #person address mapping
            if subject_person.person_au1:
                self.aimag_cbox.setCurrentIndex(self.aimag_cbox.findData(subject_person.person_au1))

            if subject_person.person_au2:
                self.soum_cbox.setCurrentIndex(self.soum_cbox.findData(subject_person.person_au2))

            if subject_person.person_au3:
                self.bag_cbox.setCurrentIndex(self.bag_cbox.findData(subject_person.person_au3))

            self.person_street_name_edit.setText(subject_person.person_streetname)
            self.person_khashaa_edit.setText(subject_person.person_khashaa)
            self.building_edit.setText(subject_person.person_building_no)
            self.apartment_edit.setText(subject_person.person_apartment_no)

            self.__update_date_of_birth(person_register)
            if len(phone) != 0:
                phone = ', '+phone
            self.phone_edit.setText(mobile_phone + phone)

            # parcel info
            old_parcel_id = self.right_holder_twidget.item(selected_row, 4).text()

            parcel_id = ''
            street = ''
            khashaa = ''
            neighbourhood = ''
            landuse_type = 2205
            zoriulalt = 1
            parcel_subjects = self.session.query(UbGisSubject).filter(UbGisSubject.objectid == object_id).all()
            for parcel_subject in parcel_subjects:
                if parcel_subject.oldpid:
                    ub_parcel = self.session.query(CaUBParcelTbl).filter(CaUBParcelTbl.old_parcel_id == parcel_subject.oldpid).one()

                    self.parcel_id_edit.setText(ub_parcel.parcel_id)
                    self.edit_status_cbox.setCurrentIndex(self.edit_status_cbox.findData(ub_parcel.edit_status))
                self.old_parcel_id_edit.setText(parcel_subject.oldpid)
                if parcel_subject.gudamj:
                    street = parcel_subject.gudamj
                    neighbourhood = parcel_subject.gudamj
                if parcel_subject.hashaa:
                    khashaa = parcel_subject.hashaa
                if parcel_subject.zoriulalt:
                    zoriulalt = parcel_subject.zoriulalt
                landuse_type = self.__landuse_type(parcel_subject).code

            self.zoriulalt_edit.setText(str(zoriulalt))
            self.streetname_edit.setText(street)
            self.khashaa_edit.setText(khashaa)
            self.neighbourhood_edit.setText(neighbourhood)
            self.parcel_landuse_cbox.setCurrentIndex(self.parcel_landuse_cbox.findData(landuse_type))

            # decision info
            decision_no = ''
            decision_date = None
            decision_level = 10
            right_type = 1

            app_type = None

            contract_no = ''
            certificate_no = ''
            create_date = None
            end_date = None
            duration = 0
            contract_status = 20

            record_cert_no = ''
            record_date = None
            for subject in parcel_subjects:
                if subject.zovshshiid:
                    decision_no = subject.zovshshiid
                if subject.zovshdate:
                    decision_date = subject.zovshdate
                if subject.gaid:
                    right_type = self.__right_type(subject).code
                decision_level = self.__decision_level(subject).code
                app_type = subject.app_type
                if right_type == 1 or right_type == 2:
                    if subject.gerid:
                        contract_no = subject.gerid
                    if subject.gerchid:
                        certificate_no = subject.gerchid
                    if subject.gerdate:
                        create_date = subject.gerdate
                    if subject.duusdate:
                        end_date = subject.duusdate
                        now_year = int(QDate().currentDate().toString("yyyy"))
                        end_year = int(PluginUtils.convert_python_date_to_qt(end_date).toString("yyyy"))
                        if now_year > end_year:
                            contract_status = 30
                    if subject.gerdate and subject.duusdate:
                        create_date = subject.gerdate
                        begin_year = int(PluginUtils.convert_python_date_to_qt(create_date).toString("yyyy"))
                        end_year = int(PluginUtils.convert_python_date_to_qt(end_date).toString("yyyy"))
                        if end_year > begin_year:
                            duration = end_year - begin_year
                else:
                    if subject.uhid:
                        record_cert_no = subject.uhid
                    if subject.uhdate:
                        record_date = subject.uhdate

            self.decision_no_edit.setText(decision_no)
            if decision_date:
                qt_date = PluginUtils.convert_python_date_to_qt(decision_date)
                self.decision_date.setDate(qt_date)
            else:
                self.decision_date.setDate(QDate(1900, 01, 01))
            self.decision_level_cbox.setCurrentIndex(self.decision_level_cbox.findData(decision_level))
            self.rigth_type_cbox.setCurrentIndex(self.rigth_type_cbox.findData(right_type))

            if app_type:
                self.application_type_cbox.setCurrentIndex(self.application_type_cbox.findData(app_type))
            else:
                self.application_type_cbox.setCurrentIndex(0)

            # contract info qt
            self.contract_full_edit.setText(self.__generate_contract_number())
            # self.contract_no_edit.setText(contract_no)
            self.contract_cert_edit.setText(certificate_no)
            if create_date:
                qt_date = PluginUtils.convert_python_date_to_qt(create_date)
                self.contract_date.setDate(qt_date)
            else:
                self.contract_date.setDate(QDate(1900, 01, 01))
            if end_date:
                qt_date = PluginUtils.convert_python_date_to_qt(end_date)
                self.end_date.setDate(qt_date)
            else:
                self.end_date.setDate(QDate(1900, 01, 01))
            self.duration_sbox.setValue(duration)
            self.contract_status_cbox.setCurrentIndex(self.contract_status_cbox.findData(contract_status))

            # record info qt
            self.record_cert_edit.setText(record_cert_no)
            self.record_full_edit.setText(self.__generate_record_number())
            if record_date:
                qt_date = PluginUtils.convert_python_date_to_qt(record_date)
                self.own_date.setDate(qt_date)
            else:
                self.own_date.setDate(QDate(1900, 01, 01))

            # documents
            self.__load_doc()

            # fee
            self.__load_fee(person_id, old_parcel_id)

            # landuk
            self.__load_landuk(person_id, old_parcel_id)

            # lpis
            self.__load_lpis(person_id, old_parcel_id)

            # person address
            self.__load_pesron_address(person_id)

        except SQLAlchemyError, e:
            self.rollback()

    def __load_pesron_address(self, person_id):

        soum_code = DatabaseUtils.working_l2_code()

        sql = "select person.register, person.street, person.khashaa " \
              "from ub_fee_person person " \
                                     "where person.register like :person_id " \
                                     "group by person.register, person.street, person.khashaa "

        result = self.session.execute(sql, {'person_id': person_id})

        for item_row in result:

            person_id = item_row[0]
            street = item_row[1]
            khashaa = item_row[2]

            self.person_street_name_edit.setText((street))
            self.person_khashaa_edit.setText((khashaa))

    def __load_lpis(self, person_id, old_parcel_id):

        # person_id = '%'+person_id+'%'
        # old_parcel_id = '%'+old_parcel_id+'%'
        self.lpis_info_twidget.setRowCount(0)
        sql = "select register, ovog, ner, utas, note,duuregid, horoo, bairshil, pid::text, zaharea, landcost, " \
              "zahid, certid, certdate, status::text, id " \
              "from ub_lpis where pid::text = :pid or register = :person_id "

        result = self.session.execute(sql, {'pid': old_parcel_id,
                                            'person_id': person_id})
        row = 0
        for item_row in result:
            row = self.lpis_info_twidget.rowCount()
            self.lpis_info_twidget.insertRow(row)
            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[0]))
            item.setData(Qt.UserRole, item_row[0])
            item.setData(Qt.UserRole+1, item_row[15])
            self.lpis_info_twidget.setItem(row, 0, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[1]))
            self.lpis_info_twidget.setItem(row, 1, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[2]))
            self.lpis_info_twidget.setItem(row, 2, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[3]))
            self.lpis_info_twidget.setItem(row, 3, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[4]))
            self.lpis_info_twidget.setItem(row, 4, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[7]))
            self.lpis_info_twidget.setItem(row, 5, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[8]))
            self.lpis_info_twidget.setItem(row, 6, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[9]))
            self.lpis_info_twidget.setItem(row, 7, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[10]))
            self.lpis_info_twidget.setItem(row, 8, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[11]))
            self.lpis_info_twidget.setItem(row, 9, item)
            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[12]))
            self.lpis_info_twidget.setItem(row, 10, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[14]))
            self.lpis_info_twidget.setItem(row, 11, item)

            row =+ 1

    def __load_landuk(self, person_id, old_parcel_id):

        # person_id = '%'+person_id+'%'
        # old_parcel_id = '%'+old_parcel_id+'%'
        self.landuk_info_twidget.setRowCount(0)
        sql = "select register, middlename, firstname, name, address, phone, " \
              "objectid, old_pid " \
              "from ub_landuk_info where pid::text = :pid or register = :person_id "

        result = self.session.execute(sql, {'pid': old_parcel_id,
                                            'person_id': person_id})
        row = 0
        for item_row in result:
            row = self.landuk_info_twidget.rowCount()
            self.landuk_info_twidget.insertRow(row)
            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[0]))
            item.setData(Qt.UserRole, item_row[6])
            item.setData(Qt.UserRole+1, item_row[7])
            self.landuk_info_twidget.setItem(row, 0, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[1]))
            self.landuk_info_twidget.setItem(row, 1, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[2]))
            self.landuk_info_twidget.setItem(row, 2, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[3]))
            self.landuk_info_twidget.setItem(row, 3, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[4]))
            self.landuk_info_twidget.setItem(row, 4, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[5]))
            self.landuk_info_twidget.setItem(row, 5, item)

            row =+ 1

    def __load_fee(self, person_id, old_parcel_id):

        self.fee_info_twidget.setRowCount(0)
        sql = "select register, name, phone1, phone2, phone3, phone4, phone5, phone6, phone7, phone8, phone9, phone10, phone11, phone12, " \
              "city, district, bag, street, khashaa " \
              "from ub_fee_person where pid = :pid or register = :person_id "

        result = self.session.execute(sql, {'pid': old_parcel_id,
                                            'person_id': person_id})
        row = 0
        for item_row in result:

            row = self.fee_info_twidget.rowCount()
            self.fee_info_twidget.insertRow(row)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(item_row[0]))
            item.setData(Qt.UserRole, item_row[0])
            self.fee_info_twidget.setItem(row, 0, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText((item_row[1]))
            item.setData(Qt.UserRole, item_row[1])
            self.fee_info_twidget.setItem(row, 1, item)

            phone = None
            if item_row[2] != None and item_row[2] != '':
                if phone:
                    phone = phone + ', ' + item_row[2]
                else:
                    phone = item_row[2]
            if item_row[3] != None and item_row[3] != '':
                if phone:
                    phone = phone + ', ' + item_row[3]
                else:
                    phone = item_row[3]
            if item_row[4] != None and item_row[4] != '':
                if phone:
                    phone = phone + ', ' + item_row[4]
                else:
                    phone = item_row[4]
            if item_row[5] != None and item_row[5] != '':
                if phone:
                    phone = phone + ', ' + item_row[5]
                else:
                    phone = item_row[2]
            if item_row[6] != None and item_row[6] != '':
                if phone:
                    phone = phone + ', ' + item_row[6]
                else:
                    phone = item_row[6]
            if item_row[7] != None and item_row[7] != '':
                if phone:
                    phone = phone + ', ' + item_row[7]
                else:
                    phone = item_row[7]
            if item_row[8] != None and item_row[8] != '':
                if phone:
                    phone = phone + ', ' + item_row[8]
                else:
                    phone = item_row[8]
            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(phone)
            self.fee_info_twidget.setItem(row, 2, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText((item_row[14]))
            item.setData(Qt.UserRole, item_row[14])
            self.fee_info_twidget.setItem(row, 3, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText((item_row[15]))
            item.setData(Qt.UserRole, item_row[15])
            self.fee_info_twidget.setItem(row, 4, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText((item_row[16]))
            item.setData(Qt.UserRole, item_row[16])
            self.fee_info_twidget.setItem(row, 5, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText((item_row[17]))
            item.setData(Qt.UserRole, item_row[17])
            self.fee_info_twidget.setItem(row, 6, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText((item_row[17]))
            item.setData(Qt.UserRole, item_row[17])
            self.fee_info_twidget.setItem(row, 7, item)

            row =+ 1

    def __decision_level(self,subject):

        level_code = 20
        level_txt = unicode(subject.zovshbaig)
        if level_txt == u'НЗД' or level_txt == u'НЗАА':
            level_code = 10
        elif level_txt == u'АЗД':
            level_code = 30
        elif level_txt == u'СЗД':
            level_code = 40
        elif level_txt == u'НАТ':
            level_code = 70
        decision_level = self.session.query(ClDecisionLevel).filter(ClDecisionLevel.code == level_code).one()
        return decision_level

    def __landuse_type(self, subject):

        landuse_type = 2205

        type = str(subject.zoriulalt)
        if self.__is_number(type):

            if int(type) == 1:
                landuse_type = 2205
            elif int(type) == 2:
                landuse_type = 2101
            elif int(type) == 3:
                landuse_type = 2104
            elif int(type) == 4:
                landuse_type = 2105
            elif int(type) == 5:
                landuse_type = 2107
            elif int(type) == 6:
                landuse_type = 2113
            elif int(type) == 7:
                landuse_type = 1604
            elif int(type) == 8:
                landuse_type = 2119
            elif int(type) == 9:
                landuse_type = 3401
            elif int(type) == 10:
                landuse_type = 3103
            elif int(type) == 11:
                landuse_type = 3303
            elif int(type) == 12:
                landuse_type = 2111
            elif int(type) == 13:
                landuse_type = 2108
            elif int(type) == 14:
                landuse_type = 2109
            elif int(type) == 15:
                landuse_type = 2116
            elif int(type) == 16:
                landuse_type = 2117
            elif int(type) == 17:
                landuse_type = 2302
            elif int(type) == 18:
                landuse_type = 2601
            elif int(type) == 19:
                landuse_type = 1401
            elif int(type) == 20:
                landuse_type = 1607
            elif int(type) == 21:
                landuse_type = 1305
            elif int(type) == 22:
                landuse_type = 1606
            elif int(type) == 23:
                landuse_type = 2101
            elif int(type) == 24:
                landuse_type = 2111

        landuse_subject = self.session.query(ClLanduseType).filter(ClLanduseType.code == landuse_type).one()
        return  landuse_subject

    def __auto_correct_private_person_id(self, text):

        original_text = text
        first_letters = text[:2]
        rest = text[2:]

        first_large_letters = first_letters.upper()

        reg = QRegExp("[0-9]+")

        new_text = first_large_letters + rest

        if len(rest) > 0:

            if not reg.exactMatch(rest):
                for i in rest:
                    if not i.isdigit():
                        rest = rest.replace(i, "")

                new_text = first_large_letters + rest
        if original_text:
            if len(original_text) > 7:
                self.__update_date_of_birth(original_text)

        if len(new_text) > 10:
            new_text = new_text[:10]

        return new_text

    def __update_date_of_birth(self, original_text):

        if original_text:
            if len(original_text) > 7:

                year = original_text[2:4]
                month = original_text[4:6]
                day = original_text[6:8]
                reg = QRegExp("[0-9]+")

                if reg.exactMatch(year) \
                        and reg.exactMatch(month) \
                        and reg.exactMatch(day):

                    current_year = str(QDate().currentDate().year())[2:]

                    if int(year) == 0 or int(year) <= int(current_year):
                        year = "20" + year
                    else:
                        year = "19" + year
                    date = QDate(int(year), int(month), int(day))
                    self.date_of_birth_date.setDate(date)

                if not self.__check_age_applicants(original_text):
                    self.error_label.clear()
                    self.error_label.setText("Person under the age of 18.")
                    return
                else:
                    self.error_label.clear()

    def __check_age_applicants(self, original_text):

        self.is_age_18 = None

        today = datetime.date.today()
        t_y = today.year
        t_m = today.month
        t_d = today.day

        year = original_text[2:4]
        if self.__is_number(year):
            year = original_text[2:4]
        else:
            year = 0
        current_year = str(QDate().currentDate().year())[2:]
        if int(year) == 0 or int(year) <= int(current_year):
            year = "20" + year
        else:
            year = "19" + year
        month = original_text[4:6]
        day = original_text[6:8]
        b_y = 0
        b_m = 0
        b_d = 0
        if self.__is_number(year):
            b_y = int(year)
        if self.__is_number(month):
            b_m = int(month)
        if self.__is_number(day):
            b_d = int(day)
        age_y = int(t_y) - int(b_y)
        if age_y == 18:
            age_m = t_m - b_m
            if age_m == 0:
                age_d = int(b_d) - int(t_d)
                if age_d == 0:
                    self.is_age_18 = True
                elif age_d > 0:
                    self.is_age_18 = False
                else:
                    self.is_age_18 = True
            elif age_m > 0:
                self.is_age_18 = True
            else:
                self.is_age_18 = False
        elif age_y > 18:
            self.is_age_18 = True
        elif age_y < 18:
            self.is_age_18 = False

        if self.is_age_18 == True:
            return True
        else:
            return False

    def __validate_entity_id(self, text):

        valid = self.int_validator.regExp().exactMatch(text)

        if not valid:
            self.error_label.setText(self.tr("Company id should be with numbers only."))
            return False
        if len(text) > 7:
            cut = text[:7]
            self.personal_id_edit.setText(cut)

        return True

    def __validate_private_person_id(self, text):

        original_text = text
        first_letters = text[:2]
        rest = text[2:]
        first_large_letters = first_letters.upper()

        reg = QRegExp("[0-9][0-9]+")
        is_valid = True

        if first_large_letters[0:1] not in Constants.CAPITAL_MONGOLIAN \
                and first_large_letters[1:2] not in Constants.CAPITAL_MONGOLIAN:
            self.error_label.setText(
                self.tr("First letters of the person id should be capital letters and in mongolian."))
            is_valid = False

        if len(original_text) > 2:
            if not reg.exactMatch(rest):
                self.error_label.setText(
                    self.tr("After the first two capital letters, the person id should contain only numbers."))
                is_valid = False

        if len(original_text) > 10:
            self.error_label.setText(self.tr("The person id shouldn't be longer than 10 characters."))
            is_valid = False

        return is_valid

    def __validate_person_name(self, text):

        person_type = self.person_type_cbox.itemData(self.person_type_cbox.currentIndex())
        if person_type == 10 or person_type == 20 or person_type == 50:
            if not text:
                text = ''
            if len(text) <= 0:
                return False

            first_letter = text[0]
            rest = text[1:]
            result_capital = self.capital_asci_letter_validator.regExp().indexIn(rest)
            result_lower = self.lower_case_asci_letter_validator.regExp().indexIn(rest)

            if first_letter not in Constants.CAPITAL_MONGOLIAN:
                self.error_label.setText(self.tr("The first letter and the letter after of a "
                                                 "name and the letter after a \"-\"  should be a capital letters."))
                return False

            if len(rest) > 0:

                if result_capital != -1 or result_lower != -1:
                    self.error_label.setText(self.tr("Only mongolian characters are allowed."))
                    return False

                for i in range(len(rest)):
                    if rest[i] not in Constants.LOWER_CASE_MONGOLIAN and rest[i] != "-":
                        if len(rest) - 1 == i:
                            return True

                        if rest[i - 1] != "-":
                            self.error_label.setText(
                                self.tr("Capital letters are only allowed at the beginning of a name or after a \"-\". "))
                            return False

        return True

    def __capitalize_after_minus(self, text):

        new_text = text
        if len(text) < 1:
            return

        for i in range(len(text)):
            if i == len(text) - 1:
                return new_text
            if text[i] == "-":
                if not text[i + 1] in Constants.CAPITAL_MONGOLIAN:
                    new_text = text.replace("-" + text[i + 1], "-" + text[i + 1].upper())

        return new_text

    def __remove_numbers(self, text):

        if self.int_validator.regExp().indexIn(text) != -1:
            new_text = "".join([i for i in text if not i.isdigit()])
            return new_text

        return text

    def __replace_spaces(self, text):

        if len(text) == 0:
            return text

        if " " in text:
            text_new = text.replace(" ", "-")
            return text_new

        return text

    def __capitalize_first_letter(self, text):

        capital_letters = Constants.CAPITAL_MONGOLIAN
        first_letter = text[:1]

        if first_letter not in capital_letters:
            upper_letter = first_letter.upper()
            list_text = list(text)
            if len(list_text) == 0:
                return ""

            list_text[0] = upper_letter
            return "".join(list_text)

        return text

    def __auto_correct_person_name(self, text):

        # Private Persons:
        # 1st: replace spaces
        # 2cnd: remove numbers
        new_text = self.__capitalize_first_letter(text)
        new_text = self.__replace_spaces(new_text)
        new_text = self.__remove_numbers(new_text)
        new_text = self.__capitalize_after_minus(new_text)
        return new_text

    def __validate_company_name(self, text):

        # no validation so far
        if text == "":
            return False

        return True

    def __capitalize_first_letter(self, text):

        capital_letters = Constants.CAPITAL_MONGOLIAN
        first_letter = text[:1]

        if first_letter not in capital_letters:
            upper_letter = first_letter.upper()
            list_text = list(text)
            if len(list_text) == 0:
                return ""

            list_text[0] = upper_letter
            return "".join(list_text)

        return text

    def __auto_correct_company_name(self, text):

        cap_value = self.__capitalize_first_letter(text)
        return cap_value

    @pyqtSlot(str)
    def on_middle_name_edit_textChanged(self, text):

        self.middle_name_edit.setStyleSheet(self.styleSheet())
        person_type = self.person_type_cbox.itemData(self.person_type_cbox.currentIndex())

        # type of Company/state organisation:
        if person_type == PersonType.mongolian_state_org \
                or person_type == PersonType.mongolian_buisness \
                or person_type == PersonType.legal_entity_foreign \
                or person_type == PersonType.foreign_citizen:
            new_text = self.__auto_correct_company_name(text)

            if new_text != text:
                self.middle_name_edit.setText(new_text)
                return

            if not self.__validate_company_name(text):
                self.middle_name_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)

        # type of private person
        else:

            new_text = self.__auto_correct_person_name(text)
            if new_text != text:
                self.middle_name_edit.setText(new_text)
                return
            if not new_text:
                new_text = ''
            if not self.__validate_person_name(new_text):
                self.middle_name_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)

    @pyqtSlot(str)
    def on_name_edit_textChanged(self, text):

        self.name_edit.setStyleSheet(self.styleSheet())
        person_type = self.person_type_cbox.itemData(self.person_type_cbox.currentIndex())

        # type of Company/state organisation:
        if person_type == PersonType.mongolian_state_org \
                or person_type == PersonType.mongolian_buisness \
                or person_type == PersonType.legal_entity_foreign \
                or person_type == PersonType.foreign_citizen:
            new_text = self.__auto_correct_company_name(text)

            if new_text != text:
                self.name_edit.setText(new_text)
                return

            if not self.__validate_company_name(text):
                self.name_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)

        # type of private person
        else:

            new_text = self.__auto_correct_person_name(text)
            if new_text != text:
                self.name_edit.setText(new_text)
                return

            if not self.__validate_person_name(new_text):
                self.name_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)

    @pyqtSlot(str)
    def on_first_name_edit_textChanged(self, text):

        self.first_name_edit.setStyleSheet(self.styleSheet())
        person_type = self.person_type_cbox.itemData(self.person_type_cbox.currentIndex())

        # type of Company/state organisation:
        if person_type == PersonType.mongolian_state_org \
                or person_type == PersonType.mongolian_buisness \
                or person_type == PersonType.legal_entity_foreign \
                or person_type == PersonType.foreign_citizen:
            new_text = self.__auto_correct_company_name(text)

            if new_text != text:
                self.first_name_edit.setText(new_text)
                return

            if not self.__validate_company_name(text):
                self.first_name_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)

        # type of private person
        else:

            new_text = self.__auto_correct_person_name(text)
            if new_text != text:
                self.first_name_edit.setText(new_text)
                return

            if not self.__validate_person_name(new_text):
                self.first_name_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)

    @pyqtSlot(str)
    def on_personal_id_edit_textChanged(self, text):

        self.personal_id_edit.setStyleSheet(self.styleSheet())
        person_type = self.person_type_cbox.itemData(self.person_type_cbox.currentIndex())

        if person_type == PersonType.legally_capable_mongolian or person_type == PersonType.legally_uncapable_mongolian:
            new_text = self.__auto_correct_private_person_id(text)

            if new_text is not text:
                self.personal_id_edit.setText(new_text)
                # return

            if not self.__validate_private_person_id(text):
                self.personal_id_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
                return

        elif person_type == PersonType.mongolian_buisness or person_type == PersonType.mongolian_state_org:

            if not self.__validate_entity_id(text):
                self.personal_id_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)

    @pyqtSlot(int)
    def on_is_ftp_edit_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.ftp_host_edit.setEnabled(True)
        else:
            self.ftp_host_edit.setEnabled(False)

    @pyqtSlot(int)
    def on_zoriulalt_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.zoriulalt_edit.setEnabled(True)
        else:
            self.zoriulalt_edit.setEnabled(False)

    @pyqtSlot(int)
    def on_khashaa_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.khashaa_edit.setEnabled(True)
        else:
            self.khashaa_edit.setEnabled(False)

    @pyqtSlot(int)
    def on_street_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.streetname_edit.setEnabled(True)
        else:
            self.streetname_edit.setEnabled(False)

    @pyqtSlot(int)
    def on_landuse_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.parcel_landuse_cbox.setEnabled(True)
        else:
            self.parcel_landuse_cbox.setEnabled(False)

    @pyqtSlot(int)
    def on_neighbourhood_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.neighbourhood_edit.setEnabled(True)
        else:
            self.neighbourhood_edit.setEnabled(False)

    @pyqtSlot(int)
    def on_person_type_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.person_type_cbox.setEnabled(True)
        else:
            self.person_type_cbox.setEnabled(False)

    @pyqtSlot(int)
    def on_person_id_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.personal_id_edit.setEnabled(True)
        else:
            self.personal_id_edit.setEnabled(False)

    @pyqtSlot(int)
    def on_middlename_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.middle_name_edit.setEnabled(True)
        else:
            self.middle_name_edit.setEnabled(False)

    @pyqtSlot(int)
    def on_lastname_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.name_edit.setEnabled(True)
        else:
            self.name_edit.setEnabled(False)

    @pyqtSlot(int)
    def on_firstname_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.first_name_edit.setEnabled(True)
        else:
            self.first_name_edit.setEnabled(False)

    @pyqtSlot(int)
    def on_phone_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.phone_edit.setEnabled(True)
        else:
            self.phone_edit.setEnabled(False)

    @pyqtSlot(int)
    def on_right_type_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.rigth_type_cbox.setEnabled(True)
        else:
            self.rigth_type_cbox.setEnabled(False)

    @pyqtSlot(int)
    def on_level_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.decision_level_cbox.setEnabled(True)
        else:
            self.decision_level_cbox.setEnabled(False)

    @pyqtSlot(int)
    def on_decision_no_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.decision_no_edit.setEnabled(True)
        else:
            self.decision_no_edit.setEnabled(False)

    @pyqtSlot(int)
    def on_decision_date_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.decision_date.setEnabled(True)
        else:
            self.decision_date.setEnabled(False)

    # @pyqtSlot(int)
    # def on_contract_no_chbox_stateChanged(self, state):
    #
    #     if state == Qt.Checked:
    #         self.contract_no_edit.setEnabled(True)
    #     else:
    #         self.contract_no_edit.setEnabled(False)

    @pyqtSlot(int)
    def on_contract_certificate_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.contract_cert_edit.setEnabled(True)
        else:
            self.contract_cert_edit.setEnabled(False)

    @pyqtSlot(int)
    def on_contract_date_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.contract_date.setEnabled(True)
        else:
            self.contract_date.setEnabled(False)

    @pyqtSlot(int)
    def on_end_date_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.end_date.setEnabled(True)
        else:
            self.end_date.setEnabled(False)

    @pyqtSlot(int)
    def on_duration_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.duration_sbox.setEnabled(True)
        else:
            self.duration_sbox.setEnabled(False)

    @pyqtSlot(int)
    def on_contract_status_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.contract_status_cbox.setEnabled(True)
        else:
            self.contract_status_cbox.setEnabled(False)

    @pyqtSlot(int)
    def on_own_date_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.own_date.setEnabled(True)
        else:
            self.own_date.setEnabled(False)

    @pyqtSlot(int)
    def on_record_certificate_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.record_cert_edit.setEnabled(True)
        else:
            self.record_cert_edit.setEnabled(False)

    def __clear_all(self):

        # Find
        self.find_parcel_id_edit.clear()
        self.find_person_id_edit.clear()

        self.find_firstname_edit.clear()
        self.find_lastname_edit.clear()
        self.find_street_name_edit.clear()
        self.find_khashaa_number_edit.clear()

        self.find_x_coordinate_edit.clear()
        self.find_y_coordinate_edit.clear()

        self.right_holder_twidget.setRowCount(0)

        # Parcel
        self.parcel_id_edit.clear()
        self.old_parcel_id_edit.clear()
        self.khashaa_edit.clear()
        self.streetname_edit.clear()
        self.zoriulalt_edit.clear()
        # self.parcel_landuse_cbox.clear()
        self.neighbourhood_edit.clear()

        self.zoriulalt_chbox.setChecked(False)
        self.khashaa_chbox.setChecked(False)
        self.street_chbox.setChecked(False)
        self.landuse_chbox.setChecked(False)
        self.neighbourhood_chbox.setChecked(False)

        # Person
        # self.person_type_cbox.clear()
        self.personal_id_edit.clear()
        self.middle_name_edit.clear()
        self.name_edit.clear()
        self.first_name_edit.clear()
        self.phone_edit.clear()

        self.person_id_chbox.setChecked(False)
        self.middlename_chbox.setChecked(False)
        self.lastname_chbox.setChecked(False)
        self.firstname_chbox.setChecked(False)
        self.phone_chbox.setChecked(False)

        self.person_street_name_edit.clear()
        self.person_khashaa_edit.clear()
        self.building_edit.clear()
        self.apartment_edit.clear()

        # Decision
        self.decision_no_edit.clear()
        self.right_type_chbox.setChecked(False)
        self.level_chbox.setChecked(False)
        self.decision_no_chbox.setChecked(False)
        self.decision_date_chbox.setChecked(False)

        # Contract
        # self.contract_no_edit.clear()
        self.contract_cert_edit.clear()
        self.contract_full_edit.clear()
        # self.contract_no_chbox.setChecked(False)
        self.contract_certificate_chbox.setChecked(False)
        self.contract_date_chbox.setChecked(False)
        self.end_date_chbox.setChecked(False)
        self.duration_chbox.setChecked(False)
        self.contract_status_chbox.setChecked(False)

        # Ownership
        # self.record_no_edit.clear()
        self.record_cert_edit.clear()
        self.record_full_edit.clear()
        # self.record_no_chbox.setChecked(False)
        self.record_certificate_chbox.setChecked(False)
        self.own_date_chbox.setChecked(False)


    def __save_subject(self, objectid):

        subject = self.session.query(UbGisSubject).filter(UbGisSubject.objectid == objectid).one()

        # Parcel
        subject.hashaa = self.khashaa_edit.text()
        subject.gudamj = self.streetname_edit.text()
        if self.zoriulalt_edit.text():
            subject.zoriulalt = self.zoriulalt_edit.text()

        # Person
        heid = 1
        person_type = self.person_type_cbox.itemData(self.person_type_cbox.currentIndex())
        if person_type == 10:
            heid = 1
        elif person_type == 20:
            heid = 1
        elif person_type == 30:
            heid = 2
        elif person_type == 40:
            heid = 3
        elif person_type == 50:
            heid = 4
        elif person_type == 60:
            heid = 5
        subject.heid = heid
        subject.register = self.personal_id_edit.text()
        subject.ovogner = self.middle_name_edit.text()
        subject.ovog = self.first_name_edit.text()
        subject.ner = self.name_edit.text()
        subject.utas1 = self.phone_edit.text()

        #person_address
        person_au1 = None
        person_au2 = None
        person_au3 = None
        if self.aimag_cbox.currentIndex() != -1:
            person_au1 = self.aimag_cbox.itemData(self.aimag_cbox.currentIndex())
        if self.soum_cbox.currentIndex() != -1:
            person_au2 = self.soum_cbox.itemData(self.soum_cbox.currentIndex())
        if self.bag_cbox.currentIndex() != -1:
            person_au3 = self.bag_cbox.itemData(self.bag_cbox.currentIndex())

        subject.person_au1 = person_au1
        subject.person_au2 = person_au2
        subject.person_au3 = person_au3

        subject.person_streetname = self.person_street_name_edit.text()
        subject.person_khashaa = self.person_khashaa_edit.text()
        subject.person_building_no = self.building_edit.text()
        subject.person_apartment_no = self.apartment_edit.text()

        # Decision
        gaid = 3
        zovshbaig = u'ДЗД'
        right_type = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())
        app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())
        decision_level = self.decision_level_cbox.itemData(self.decision_level_cbox.currentIndex())
        if right_type == 1:
            gaid = 3
        elif right_type == 2:
            gaid = 2
        elif right_type == 3:
            gaid = 1

        if decision_level == 10:
            zovshbaig = u'НЗД'
        elif decision_level == 20:
            zovshbaig = u'ДЗД'
        elif decision_level == 30:
            zovshbaig = u'АЗД'
        elif decision_level == 40:
            zovshbaig = u'СЗД'
        elif decision_level == 70:
            zovshbaig = u'НАТ'

        subject.gaid = gaid
        subject.zovshbaig = zovshbaig
        subject.zovshshiid = self.decision_no_edit.text()
        decision_date = PluginUtils.convert_qt_date_to_python(self.decision_date.date())
        subject.zovshdate = decision_date
        subject.app_type = app_type

        # Contract
        if gaid == 2 or gaid == 3:
            # subject.gerid = self.contract_no_edit.text()
            subject.gerchid = self.contract_cert_edit.text()
            contract_date = PluginUtils.convert_qt_date_to_python(self.contract_date.date())
            subject.gerdate = contract_date
            end_date = PluginUtils.convert_qt_date_to_python(self.end_date.date())
            subject.duusdate = end_date

        # Ownership
        if gaid == 1:

            record_date = PluginUtils.convert_qt_date_to_python(self.own_date.date())
            subject.uhdate = record_date
            subject.uhid = self.record_cert_edit.text()

        old_parcel_id = self.old_parcel_id_edit.text()
        ub_parcel = self.session.query(CaUBParcelTbl).filter(CaUBParcelTbl.old_parcel_id == old_parcel_id).one()
        edit_status = self.edit_status_cbox.itemData(self.edit_status_cbox.currentIndex())
        ub_parcel_type = self.ub_parcel_type_cbox.itemData(self.ub_parcel_type_cbox.currentIndex())

        ub_parcel.ub_parcel_type = ub_parcel_type
        ub_parcel.type_created_by = self.__current_sd_user().user_id
        ub_parcel.type_updated_by = self.__current_sd_user().user_id
        ub_parcel.type_created_at = PluginUtils.convert_qt_date_to_python(QDate.currentDate())
        ub_parcel.type_updated_at = PluginUtils.convert_qt_date_to_python(QDate.currentDate())

        if ub_parcel.edit_status != 10:
            subject.status_date = PluginUtils.convert_qt_date_to_python(QDate.currentDate())

            subject.status_user = DatabaseUtils.current_user().user_name

        if self.edit_status_cbox.currentIndex() == -1:
            ub_parcel.edit_status = 30
        else:
            ub_parcel.edit_status = edit_status

    def __current_sd_user(self):

        officer = self.session.query(SetRole) \
            .filter(SetRole.user_name == QSettings().value(SettingsConstants.USER)) \
            .filter(SetRole.is_active == True).one()

        sd_user = self.session.query(SdUser).filter(SdUser.gis_user_real == officer.user_name_real).first()
        return sd_user

    @pyqtSlot()
    def on_save_button_clicked(self):

        if len(self.right_holder_twidget.selectedItems()) == 0:
            self.error_label.setText(self.tr("Select one item to save."))
            return

        if self.edit_status_cbox.itemData(self.edit_status_cbox.currentIndex()) == -1:
            PluginUtils.show_message(self, self.tr("LM2", "Alert"), self.tr("Please select edit status!!!"))
            return
        selected_row = self.right_holder_twidget.currentRow()
        object_id = self.right_holder_twidget.item(selected_row, 1).data(Qt.UserRole + 1)
        if object_id:
            edit_status = self.edit_status_cbox.itemData(self.edit_status_cbox.currentIndex())
            if edit_status == DELETE_STATUS:
                self.__save_delete_parcel()
            self.__save_subject(object_id)
        self.session.commit()
        PluginUtils.show_message(self, self.tr("LM2", "Success"), self.tr("Success saved"))

    @pyqtSlot(str)
    def on_zoriulalt_edit_textChanged(self, text):

        landuse_type = 2205

        type = text
        if self.__is_number(type):
            if int(type) in self.zoriulalt:
                if int(type) == 1:
                    landuse_type = 2205
                elif int(type) == 2:
                    landuse_type = 2101
                elif int(type) == 3:
                    landuse_type = 2104
                elif int(type) == 4:
                    landuse_type = 2105
                elif int(type) == 5:
                    landuse_type = 2107
                elif int(type) == 6:
                    landuse_type = 2113
                elif int(type) == 7:
                    landuse_type = 1604
                elif int(type) == 8:
                    landuse_type = 2119
                elif int(type) == 9:
                    landuse_type = 3401
                elif int(type) == 10:
                    landuse_type = 3103
                elif int(type) == 11:
                    landuse_type = 3303
                elif int(type) == 12:
                    landuse_type = 2111
                elif int(type) == 13:
                    landuse_type = 2108
                elif int(type) == 14:
                    landuse_type = 2109
                elif int(type) == 15:
                    landuse_type = 2116
                elif int(type) == 16:
                    landuse_type = 2117
                elif int(type) == 17:
                    landuse_type = 2302
                elif int(type) == 18:
                    landuse_type = 2601
                elif int(type) == 19:
                    landuse_type = 1401
                elif int(type) == 20:
                    landuse_type = 1607
                elif int(type) == 21:
                    landuse_type = 1305
                elif int(type) == 22:
                    landuse_type = 1606
                elif int(type) == 23:
                    landuse_type = 2101
                elif int(type) == 24:
                    landuse_type = 2111

        self.parcel_landuse_cbox.setCurrentIndex(self.parcel_landuse_cbox.findData(landuse_type))

    def __validate_apartment_number(self, number, object_name):

        if len(number) == 0:
            return True

        # Apartment-number should start with a number and contain only one letter
        first_number = number[0]
        letter = number[-1]
        reg = QRegExp("[0-9]")
        result = reg.exactMatch(first_number)

        if not result:
            self.error_label.setText(self.tr("{0} string contains not just numbers.").format(object_name))
            return False

        if letter not in Constants.LOWER_CASE_MONGOLIAN and not letter.isdigit():
            self.error_label.setText(self.tr("{0} number contains wrong letters.").format(object_name))
            return False

        count = 0
        for letter in number:
            if letter in Constants.LOWER_CASE_MONGOLIAN:
                count += 1

        if count > 1:
            self.error_label.setText(self.tr("{0} number contains more than one letter.").format(object_name))
            return False

        return True

    @pyqtSlot(str)
    def on_khashaa_edit_textChanged(self, text):

        self.khashaa_edit.setStyleSheet(self.styleSheet())
        if not self.__validate_apartment_number(text, self.tr("Khashaa")):
            self.khashaa_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)

    def __validate_street_name(self, name):

        if name == "":
            return True

        for i in range(len(name)):
            if name[i].isdigit():
                if name[i - 1] != "-":
                    self.error_label.setText(self.tr("Street name can only end with a number, if a - is in front. "))
                return False

            if name[i] == "-":
                rest = name[i + 1:]

                if rest.isdigit():
                    return True
                else:
                    self.error_label.setText(self.tr("Street name can end with a number, if a - is in front. "))
                    return False

        return True

    @pyqtSlot(str)
    def on_streetname_edit_textChanged(self, text):

        self.streetname_edit.setStyleSheet(self.styleSheet())
        capital_letters = Constants.CAPITAL_MONGOLIAN
        first_letter = text[:1]

        if first_letter not in capital_letters:
            self.streetname_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)

        cap_value = self.__capitalize_first_letter(text)
        self.streetname_edit.setText(cap_value)
        if not self.__validate_street_name(cap_value):
            self.streetname_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)

    def __validate_decision_no(self, decision_no):

        first_letter = decision_no[:1]

        if decision_no == "" or first_letter == " " or decision_no is None:
            return False
        else:
            return True

    def __validate_certificate(self, certificate_no):

        first_letter = certificate_no[:1]

        if certificate_no == "" or first_letter == " " or certificate_no is None:
            return False
        else:
            return True

    @pyqtSlot(str)
    def on_decision_no_edit_textChanged(self, text):

        self.decision_no_edit.setStyleSheet(self.styleSheet())

        if not self.__validate_decision_no(text):
            self.decision_no_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)

        au_level2 = DatabaseUtils.current_working_soum_schema()
        year_filter = str(self.decision_date.date().toString("yyyy"))
        decision_no = au_level2 + '-' + self.decision_no_edit.text() +'/' + year_filter
        self.decision_full_edit.setText(decision_no)

    @pyqtSlot(str)
    def on_contract_cert_edit_textChanged(self, text):

        self.contract_cert_edit.setStyleSheet(self.styleSheet())

        right_type = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())
        if right_type == 1 or right_type == 2:
            if not self.__validate_certificate(text):
                self.contract_cert_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)

    @pyqtSlot(str)
    def on_record_cert_edit_textChanged(self, text):

        self.record_cert_edit.setStyleSheet(self.styleSheet())

        right_type = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())
        if right_type == 3:
            if not self.__validate_certificate(text):
                self.record_cert_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)

    @pyqtSlot(int)
    def on_duration_sbox_valueChanged(self, value):

        decision_year = self.decision_date.date().year()
        decision_month = self.decision_date.date().month()
        decision_day = self.decision_date.date().day()
        self.end_date.setDate(QDate(int(decision_year)+value, decision_month, decision_day))

    # Decision Date Changed
    def on_decision_date_DateChanged(self, newDate):

        right_type = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())
        self.decision_date.setStyleSheet(self.styleSheet())
        if not self.__validate_decision_date(newDate):
            self.decision_date.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)

        if right_type == 3:
            self.own_date.setDate(newDate)
        else:
            self.contract_date.setDate(newDate)

        au_level2 = DatabaseUtils.current_working_soum_schema()
        year_filter = str(newDate.toString("yyyy"))
        decision_no = au_level2 + '-' + self.decision_no_edit.text() + '/' + year_filter
        self.decision_full_edit.setText(decision_no)

    def __validate_decision_date(self, newDate):

        decision_year = newDate.year()
        if decision_year <= 1900 or QDate.currentDate() < newDate:
            return False
        else:
            return True

    # Contract Date Changed
    def on_contract_date_DateChanged(self, newDate):

        self.contract_date.setStyleSheet(self.styleSheet())
        if not self.__validate_contract_date(newDate):
            self.contract_date.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)

    # Contract Date Changed
    def on_end_date_DateChanged(self, newDate):

        self.end_date.setStyleSheet(self.styleSheet())
        if not self.__validate_end_date(newDate):
            self.end_date.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)

        duration = self.end_date.date().year() - self.decision_date.date().year()
        # self.duration_sbox.setValue(duration)
        # self.duration_sbox.setMinimum(duration)

    # Contract Date Changed
    def on_own_date_DateChanged(self, newDate):

        self.own_date.setStyleSheet(self.styleSheet())
        if not self.__validate_own_date(newDate):
            self.own_date.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)

    def __validate_contract_date(self, newDate):

        right_type = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())
        decision_date = self.decision_date.date()
        if (decision_date > newDate or QDate.currentDate() < newDate) and (right_type == 1 or right_type == 2):
            return False
        else:
            return True

    def __validate_end_date(self, newDate):

        right_type = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())
        contract_date = self.contract_date.date()
        if contract_date >= newDate and (right_type == 1 or right_type == 2):
            return False
        else:
            return True

    def __validate_own_date(self, newDate):

        right_type = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())
        decision_date = self.decision_date.date()
        decision_year = newDate.year()
        if right_type == 3:
            if (decision_year <= 1900 or QDate.currentDate() < newDate) or decision_date > newDate:
                return False
            else:
                return True

    def __generate_application_number(self):

        au_level2 = DatabaseUtils.current_working_soum_schema()
        right_type = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())

        app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())

        # app_type = 1
        # if right_type == 1:
        #     app_type = 6
        # elif right_type == 2:
        #     app_type == 5
        # elif right_type == 3:
        #     app_type == 1

        app_no_part_0 = au_level2
        app_no_part_1 = (str(app_type).zfill(2))
        app_type_filter = "%-" + str(app_type).zfill(2) + "-%"
        soum_filter = str(au_level2) + "-%"
        qt_date = self.decision_date.date()
        year_filter = "%-" + str(qt_date.toString("yy"))

        try:

            count = self.session.query(CtApplication) \
                        .filter(CtApplication.app_no.like("%-%"))\
                        .filter(CtApplication.app_no.like(app_type_filter))  \
                        .filter(CtApplication.app_no.like(soum_filter)) \
                        .filter(CtApplication.app_no.like(year_filter)) \
                    .order_by((func.substr(CtApplication.app_no, 10, 14)).desc()).count()

            # count = self.session.query(CtApplication) \
            #     .filter(CtApplication.app_no.like("%-%")) \
            #     .filter(CtApplication.app_no.like(app_type_filter)) \
            #     .filter(CtApplication.app_no.like(soum_filter)) \
            #     .filter(CtApplication.app_no.like(year_filter)) \
            #     .order_by((CtApplication.app_no).split('-')[2].desc()).first()

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

        if count > 0:
            # try:
            # max_number_app = self.session.query(CtApplication) \
            #     .filter(CtApplication.app_no.like("%-%")) \
            #     .filter(CtApplication.app_no.like(app_type_filter)) \
            #     .filter(CtApplication.app_no.like(soum_filter)) \
            #     .filter(CtApplication.app_no.like(year_filter)) \
            #     .order_by((CtApplication.app_no).split  ('-')[2].desc()).first()

            sql = "select split_part(app_no, '-', 3)::int, app_no from data_soums_union.ct_application " \
                    "where app_no like " + "'" + soum_filter + "'" + " and app_no like "+ "'" + app_type_filter + "'" +" and app_no like "+ "'" + year_filter + "'" +" " \
                    "order by split_part(app_no, '-', 3)::int desc limit 1; "
            result = self.session.execute(sql)
            for item_row in result:
                max_number_app = item_row[0]
            # max_number_app = self.session.query(CtApplication)\
            #     .filter(CtApplication.app_no.like("%-%"))\
            #     .filter(CtApplication.app_no.like(app_type_filter)) \
            #     .filter(CtApplication.app_no.like(soum_filter)) \
            #     .filter(CtApplication.app_no.like(year_filter)) \
            #     .order_by(int(func.substr(CtApplication.app_no, 10, 14)).desc()).first()
            #     app_no_numbers = max_number_app.app_no.split("-")
                app_no_numbers = max_number_app

                # app_no_part_2 = str(int(app_no_numbers[2]) + 1).zfill(5)
                app_no_part_2 = str(int(app_no_numbers) + 1).zfill(5)
            # except SQLAlchemyError, e:
            #     PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            #     return
        else:
            app_no_part_2 = "00001"

        app_no_part_3 = (qt_date.toString("yy"))
        app_no = app_no_part_0 + '-' + app_no_part_1 + '-' + app_no_part_2 + '-' + app_no_part_3

        return app_no

    def __validaty_of_ubparcel(self):

        valid = True
        old_parcel_id = self.old_parcel_id_edit.text()
        error_message = self.tr("The parcel info can't be saved. The following errors have been found: ")
        ub_parcel = self.session.query(CaUBParcelTbl).filter(CaUBParcelTbl.old_parcel_id == old_parcel_id).one()
        parcel_within_count = self.session.query(CaParcel).filter(
            ub_parcel.geometry.ST_Within(CaParcel.geometry)).count()

        wkb_elem = self.session.query(CaUBParcelTbl.geometry).filter(CaUBParcelTbl.old_parcel_id == old_parcel_id).scalar()
        shply_geom = to_shape(wkb_elem)
        wkt_geom = shply_geom.to_wkt()
        params = urllib.urlencode({'geom': wkt_geom})
        f = urllib.urlopen("http://192.168.15.222/api/geo/parcel/check/by/geom/wkt", params)
        data = json.load(f)
        status = data['status']
        result = data['result']
        if not status:
            # PluginUtils.show_message(self, u'Амжилтгүй', u'Өгөгдөл буруу байна!!!')
            valid = False
            parcel_error = u'Өгөгдөл буруу байна!!!'
            error_message = error_message + "\n \n" + parcel_error
            # return
        else:
            if result:
                # PluginUtils.show_message(self, u'Амжилтгүй', u'Газар олгох боломжгүй байршил!!!')
                valid = False
                parcel_error = u'Газар олгох боломжгүй байршил!!!'
                error_message = error_message + "\n \n" + parcel_error
                # return

        # parcel
        validaty_result = self.__check_parcel_correct(ub_parcel.geometry, '')

        if not validaty_result[0]:
            valid = False
            log_measage = validaty_result[1]
            error_message = error_message + "\n \n" + log_measage

        if parcel_within_count > 0:
            valid = False
            parcel_error = self.tr("Duplicate Parcel.")
            error_message = error_message + "\n \n" + parcel_error
        text = self.khashaa_edit.text()
        if not self.__validate_apartment_number(text, self.tr("Khashaa")):
            valid = False
            khashaa_error = self.tr("Khashaa number contains wrong letters.")
            error_message = error_message + "\n \n" + khashaa_error
        text = self.streetname_edit.text()
        cap_value = self.__capitalize_first_letter(text)
        self.streetname_edit.setText(cap_value)
        if not self.__validate_street_name(cap_value):
            valid = False
            street_error = self.tr("Street name contains wrong letters.")
            error_message = error_message + "\n \n" + street_error

        # person
        person_type = self.person_type_cbox.itemData(self.person_type_cbox.currentIndex())

        text = self.personal_id_edit.text()
        if person_type == PersonType.legally_capable_mongolian or person_type == PersonType.legally_uncapable_mongolian:
            new_text = self.__auto_correct_private_person_id(text)

            if new_text is not text:
                self.personal_id_edit.setText(new_text)

            if not self.__validate_private_person_id(text):
                valid = False
                street_error = self.tr("Person id error!.")
                error_message = error_message + "\n \n" + street_error

        elif person_type == PersonType.mongolian_buisness or person_type == PersonType.mongolian_state_org:

            if not self.__validate_entity_id(text):
                valid = False
                street_error = self.tr("Company id error!.")
                error_message = error_message + "\n \n" + street_error

        text = self.middle_name_edit.text()

        # type of Company/state organisation:
        if person_type == PersonType.mongolian_state_org \
                or person_type == PersonType.mongolian_buisness \
                or person_type == PersonType.legal_entity_foreign \
                or person_type == PersonType.foreign_citizen:
            new_text = self.__auto_correct_company_name(text)

            if new_text != text:
                self.middle_name_edit.setText(new_text)

            if not self.__validate_company_name(text):
                valid = False
                street_error = self.tr("Company contact Middle name error!.")
                error_message = error_message + "\n \n" + street_error

        # type of private person
        else:

            new_text = self.__auto_correct_person_name(text)
            if new_text != text:
                self.middle_name_edit.setText(new_text)

            if not self.__validate_person_name(new_text):
                valid = False
                street_error = self.tr("Person middle name error!.")
                error_message = error_message + "\n \n" + street_error

        text = self.name_edit.text()

        # type of Company/state organisation:
        if person_type == PersonType.mongolian_state_org \
                or person_type == PersonType.mongolian_buisness \
                or person_type == PersonType.legal_entity_foreign \
                or person_type == PersonType.foreign_citizen:
            new_text = self.__auto_correct_company_name(text)

            if new_text != text:
                self.name_edit.setText(new_text)

            if not self.__validate_company_name(text):
                valid = False
                street_error = self.tr("Company name error!.")
                error_message = error_message + "\n \n" + street_error

        # type of private person
        else:

            new_text = self.__auto_correct_person_name(text)
            if new_text != text:
                self.name_edit.setText(new_text)

            if not self.__validate_person_name(new_text):
                valid = False
                street_error = self.tr("Person name error!.")
                error_message = error_message + "\n \n" + street_error

        text = self.first_name_edit.text()

        # type of Company/state organisation:
        if person_type == PersonType.mongolian_state_org \
                or person_type == PersonType.mongolian_buisness \
                or person_type == PersonType.legal_entity_foreign \
                or person_type == PersonType.foreign_citizen:
            new_text = self.__auto_correct_company_name(text)

            if new_text != text:
                self.first_name_edit.setText(new_text)

            if not self.__validate_company_name(text):
                valid = False
                street_error = self.tr("Company contact first name error!.")
                error_message = error_message + "\n \n" + street_error

        # type of private person
        else:

            new_text = self.__auto_correct_person_name(text)
            if new_text != text:
                self.first_name_edit.setText(new_text)


            if not self.__validate_person_name(new_text):
                valid = False
                street_error = self.tr("Person first name error!.")
                error_message = error_message + "\n \n" + street_error

        text = self.decision_no_edit.text()
        if not self.__validate_decision_no(text):
            valid = False
            street_error = self.tr("Decision number error!.")
            error_message = error_message + "\n \n" + street_error

        right_type = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())
        if right_type == 1 or right_type == 2:
            text = self.contract_cert_edit.text()
        else:
            text = self.record_cert_edit.text()
        if not self.__validate_certificate(text):
            valid = False
            street_error = self.tr("Certificate number error!.")
            error_message = error_message + "\n \n" + street_error

        date = self.decision_date.date()
        if not self.__validate_decision_date(date):
            valid = False
            street_error = self.tr("Decision date error!.")
            error_message = error_message + "\n \n" + street_error

        if right_type == 1 or right_type == 2:
            date = self.contract_date.date()
            if not self.__validate_contract_date(date):
                valid = False
                street_error = self.tr("Contract date error!.")
                error_message = error_message + "\n \n" + street_error

            date = self.end_date.date()
            if not self.__validate_end_date(date):
                valid = False
                street_error = self.tr("Contract end date error!.")
                error_message = error_message + "\n \n" + street_error
        if not valid:
            valid = False

        decision_no = self.decision_full_edit.text()
        decision_level = self.decision_level_cbox.itemData(self.decision_level_cbox.currentIndex())
        decision_count = self.session.query(CtDecision).filter(CtDecision.decision_no == decision_no).\
            filter(CtDecision.decision_level == decision_level).count()
        if decision_count == 1:
            self.decision = self.session.query(CtDecision).filter(CtDecision.decision_no == decision_no). \
                filter(CtDecision.decision_level == decision_level).one()
            app_dec_count = self.session.query(CtDecisionApplication).filter(
                CtDecisionApplication.decision == self.decision.decision_id).count()
            if app_dec_count > 0:
                app_dec = self.session.query(CtDecisionApplication).filter(
                    CtDecisionApplication.decision == self.decision.decision_id).first()
                application = app_dec.application_ref

                if application:
                    application_type = application.app_type
                    app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())
                    if app_type != application_type:
                        # PluginUtils.show_message(self, self.tr("LM2", "Application Type"),
                        #                          self.tr("Can't match application type!!!"))
                        # self.isSave = False
                        valid = False
                        street_error = self.tr("Can't match application type!!!")
                        error_message = error_message + "\n \n" + street_error

        return valid, error_message

    @pyqtSlot(int)
    def on_rigth_type_cbox_currentIndexChanged(self, index):

        self.application_type_cbox.clear()
        rigth_code = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())

        if rigth_code == 1 or rigth_code == 2:
            self.contract_gbox.setVisible(True)
            self.record_gbox.setVisible(False)
        elif rigth_code == 3:
            self.record_gbox.setVisible(True)
            self.contract_gbox.setVisible(False)

        rigth_apps = self.session.query(SetRightTypeApplicationType).filter(
            SetRightTypeApplicationType.right_type == rigth_code). \
            order_by(SetRightTypeApplicationType.application_type).all()

        for item in rigth_apps:
            app_type_count = self.session.query(ClApplicationType).filter(
                ClApplicationType.code == item.application_type).count()
            if app_type_count == 1:
                app_type = self.session.query(ClApplicationType).filter(
                    ClApplicationType.code == item.application_type).one()
                self.application_type_cbox.addItem(app_type.description, app_type.code)

    @pyqtSlot()
    def on_finish_button_clicked(self):

        if len(self.right_holder_twidget.selectedItems()) == 0:
            PluginUtils.show_error(self, self.tr("Alert"), self.tr("Select one item to finish."))
            return

        validaty_result = self.__validaty_of_ubparcel()

        if not validaty_result[0]:
            log_measage = validaty_result[1]

            PluginUtils.show_error(self, self.tr("Invalid parcel info"), log_measage)
            return

        message_box = QMessageBox()
        message_box.setText(self.tr("Do you want to import for base database?"))

        yes_button = message_box.addButton(self.tr("Yes"), QMessageBox.ActionRole)
        message_box.addButton(self.tr("No"), QMessageBox.ActionRole)
        message_box.exec_()

        if message_box.clickedButton() == yes_button:
            self.create_savepoint()
            # try:
            self.__save_person()
            self.__save_parcel()

            # self.__save_application_details()

            self.__save_applicant()

            self.__save_status()

            self.__save_decision()

            self.__save_contract_owner()

            selected_row = self.right_holder_twidget.currentRow()
            objectid = self.right_holder_twidget.item(selected_row, 1).data(Qt.UserRole + 1)
            subject = self.session.query(UbGisSubject).filter(UbGisSubject.objectid == objectid).one()
            subject.is_finish = True
            subject.finish_user = DatabaseUtils.current_user().user_name
            subject.finish_date = PluginUtils.convert_qt_date_to_python(QDate.currentDate())
            # except LM2Exception, e:
            #     self.rollback_to_savepoint()
            #     PluginUtils.show_error(self, e.title(), e.message())
            #     return

            self.commit()

        self.__import_archive()

    def __multi_owner_save(self, person_id):

        self.create_savepoint()
        try:
            register = person_id

            sql = "select register, ovog,ner ,hen,zahid " \
                  "from ub_lpis_co info " \
                  "where oregister = :register "

            result = self.session.execute(sql, {'register': register})
            row = 0
            for item_row in result:
                person_id = item_row[0]

                name = item_row[1]
                first_name = item_row[2]

                person_count = self.session.query(BsPerson).filter(BsPerson.person_register == person_id).count()
                if person_count > 0:
                    bs_person = self.session.query(BsPerson).filter(BsPerson.person_register == person_id).one()
                else:
                    bs_person = BsPerson()

                    bs_person.person_register = person_id
                    bs_person.type = 10
                    bs_person.name = name
                    bs_person.first_name = first_name

                    self.session.add(bs_person)

                # self.session.flush()
        except SQLAlchemyError, e:
            self.rollback_to_savepoint()
            raise LM2Exception(self.tr("File Error"),
                               self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

    def __generate_record_number(self):

        soum = DatabaseUtils.current_working_soum_schema()
        soum_filter = soum + "-%"
        qt_date = self.own_date.date()
        try:
            record_number_filter = "%-{0}/%".format(str(qt_date.toString("yyyy")))

            # return
            count = self.session.query(CtOwnershipRecord) \
                        .filter(CtOwnershipRecord.record_no.like("%-%")) \
                        .filter(CtOwnershipRecord.record_no.like(soum + "-%")) \
                        .filter(CtOwnershipRecord.record_no.like(record_number_filter))  \
                        .filter(CtOwnershipRecord.au2 == soum) \
                        .order_by(func.substr(CtOwnershipRecord.record_no, 10, 16).desc()).count()
            if count == 0:
                cu_max_number = "00001"

            else:
                sql = "select split_part(record_no, '/', 2)::int, record_no from data_soums_union.ct_ownership_record " \
                      "where record_no like " + "'" + soum_filter + "'" + " and record_no like " + "'" + record_number_filter + "'" + " " \
                                     "order by split_part(record_no, '/', 2)::int desc limit 1; "
                result = self.session.execute(sql)
                for item_row in result:
                    cu_max_number = item_row[0]
                # cu_max_number = self.session.query(CtOwnershipRecord.record_no)\
                #                     .filter(CtOwnershipRecord.record_no.like("%-%")) \
                #                     .filter(CtOwnershipRecord.record_no.like(soum + "-%")) \
                #                     .filter(CtOwnershipRecord.record_no.like(record_number_filter)) \
                #                     .filter(CtOwnershipRecord.au2 == soum) \
                #     .order_by(func.substr(CtOwnershipRecord.record_no, 10, 16).desc()).first()
                #
                # cu_max_number = cu_max_number[0]
                # minus_split_number = cu_max_number.split("-")
                # slash_split_number = minus_split_number[1].split("/")
                # cu_max_number = int(slash_split_number[1]) + 1
                    cu_max_number = int(cu_max_number) + 1

            year = qt_date.toString("yyyy")
            number = soum + "-" + year + "/" + str(cu_max_number).zfill(5)

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("Database Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

        return number

    def __generate_contract_number(self):

        soum = DatabaseUtils.current_working_soum_schema()
        soum_filter = soum + "-%"
        qt_date = self.contract_date.date()
        try:
            contract_number_filter = "%-{0}/%".format(str(qt_date.toString("yyyy")))

            count = self.session.query(CtContract) \
                .filter(CtContract.contract_no.like("%-%")) \
                .filter(CtContract.contract_no.like(soum+"-%")) \
                .filter(CtContract.contract_no.like(contract_number_filter)) \
                .filter(CtContract.au2 == soum) \
                .order_by(func.substr(CtContract.contract_no, 10, 16).desc()).count()
            if count == 0:
                cu_max_number = "00001"
            else:
                sql = "select split_part(contract_no, '/', 2)::int, contract_no from data_soums_union.ct_contract " \
                        "where contract_no like " + "'" + soum_filter + "'" + " and contract_no like " + "'" + contract_number_filter + "'" + " " \
                        "order by split_part(contract_no, '/', 2)::int desc limit 1; "
                result = self.session.execute(sql)
                for item_row in result:
                    cu_max_number = item_row[0]
                # cu_max_number = self.session.query(CtContract.contract_no) \
                #     .filter(CtContract.contract_no.like("%-%")) \
                #     .filter(CtContract.contract_no.like(soum + "-%")) \
                #     .filter(CtContract.contract_no.like(contract_number_filter)) \
                #     .filter(CtContract.au2 == soum) \
                #     .order_by(func.substr(CtContract.contract_no, 10, 16).desc()).first()
                #     cu_max_number = cu_max_number

                    # minus_split_number = cu_max_number.split("-")
                    # slash_split_number = minus_split_number[1].split("/")
                    # cu_max_number = int(slash_split_number[1]) + 1
                    cu_max_number = int(cu_max_number) + 1
            soum = DatabaseUtils.current_working_soum_schema()
            year = qt_date.toString("yyyy")
            number = soum + "-" + year + "/" + str(cu_max_number).zfill(5)

        except SQLAlchemyError, e:
            raise LM2Exception(self.tr("Database Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

        return number

    def __save_contract_owner(self):

        right_type = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())

        if right_type == 1 or right_type == 2:
            contract_no = self.__generate_contract_number()
            self.create_savepoint()
            try:
                self.contract = CtContract()
                self.contract.type = 1
                self.contract.contract_no = contract_no
                self.contract.contract_begin = self.contract_date.date().toString(Constants.DATABASE_DATE_FORMAT)
                self.contract.contract_date = self.contract_date.date().toString(Constants.DATABASE_DATE_FORMAT)
                self.contract.contract_end = self.end_date.date().toString(Constants.DATABASE_DATE_FORMAT)
                self.contract.certificate_no = int(self.contract_cert_edit.text())
                self.contract.status = Constants.CONTRACT_STATUS_ACTIVE
                self.contract.au2 = DatabaseUtils.working_l2_code()

                self.session.add(self.contract)


                app_type = None
                obj_type = 'contract\Contract'
                qt_date = self.contract_date.date()
                # contract_number_filter = "%-{0}/%".format(str(qt_date.toString("yyyy")))
                year = qt_date.toString("yyyy")
                PluginUtils.generate_auto_app_no(str(year), app_type, DatabaseUtils.working_l2_code(), obj_type, self.session)

                contract_app = CtContractApplicationRole()
                contract_app.application_ref = self.application
                contract_app.application = self.application.app_id
                contract_app.contract = self.contract.contract_id
                contract_app.contract_ref = self.contract

                contract_app.role = Constants.APPLICATION_ROLE_CREATES
                self.contract.application_roles.append(contract_app)
            except SQLAlchemyError, e:
                self.rollback_to_savepoint()
                raise LM2Exception(self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
        else:
            record_no = self.__generate_record_number()
            self.create_savepoint()
            try:
                self.record = CtOwnershipRecord()
                self.record.record_no = record_no
                self.record.record_date = self.own_date.date().toString(Constants.DATABASE_DATE_FORMAT)
                self.record.record_begin = self.decision_date.date().toString(Constants.DATABASE_DATE_FORMAT)
                self.record.certificate_no = int(self.record_cert_edit.text())
                self.record.status = Constants.RECORD_STATUS_ACTIVE
                self.record.au2 = DatabaseUtils.working_l2_code()

                self.session.add(self.record)

                app_type = None
                obj_type = 'record\OwnershipRecord'
                qt_date = self.own_date.date()
                # contract_number_filter = "%-{0}/%".format(str(qt_date.toString("yyyy")))
                year = qt_date.toString("yyyy")
                PluginUtils.generate_auto_app_no(str(year), app_type, DatabaseUtils.working_l2_code(), obj_type, self.session)

                record_app = CtRecordApplicationRole()
                record_app.application_ref = self.application
                record_app.application = self.application.app_id
                record_app.record = self.record.record_id

                record_app.role = Constants.APPLICATION_ROLE_CREATES
                self.record.application_roles.append(record_app)
            except SQLAlchemyError, e:
                self.rollback_to_savepoint()
                raise LM2Exception(self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

    def __save_decision(self):

        decision_level = self.decision_level_cbox.itemData(self.decision_level_cbox.currentIndex())
        decision_no = self.decision_full_edit.text()

        decision_count = self.session.query(CtDecision).filter(CtDecision.decision_no == decision_no).\
            filter(CtDecision.decision_level == decision_level).count()
        self.create_savepoint()
        try:
            if decision_count == 1:
                self.decision = self.session.query(CtDecision).filter(CtDecision.decision_no == decision_no).\
                    filter(CtDecision.decision_level == decision_level).one()

            else:
                self.decision = CtDecision()

                self.decision.decision_date = self.decision_date.date().toString(Constants.DATABASE_DATE_FORMAT)
                self.decision.decision_no = decision_no
                self.decision.decision_level = decision_level
                self.decision.imported_by = DatabaseUtils.current_sd_user().user_id
                self.decision.au2 = DatabaseUtils.working_l2_code()
                self.session.add(self.decision)
                self.session.flush()

            decision_app = CtDecisionApplication()
            decision_app.decision = self.decision.decision_id
            decision_app.decision_result = 10
            decision_app.application = self.application.app_id
            self.decision.results.append(decision_app)
        except SQLAlchemyError, e:
            self.rollback_to_savepoint()
            raise LM2Exception(self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
        # self.session.flush()

    def __save_status(self):

        status_date = self.decision_date.date().toString(Constants.DATABASE_DATE_FORMAT)

        statuses = self.session.query(ClApplicationStatus).\
            filter(ClApplicationStatus.code != 1). \
            filter(ClApplicationStatus.code != 8). \
            filter(ClApplicationStatus.code < 10).order_by(ClApplicationStatus.code.asc()).all()

        self.create_savepoint()
        try:
            for status in statuses:
                application_status = CtApplicationStatus()
                application_status.ct_application = self.application
                application_status.status = status.code
                application_status.status_ref = status
                application_status.status_date = status_date

                # current_user = QSettings().value(SettingsConstants.USER)
                # officer = self.session.query(SetRole).filter_by(user_name=current_user).filter(SetRole.is_active == True).one()
                application_status.next_officer_in_charge = DatabaseUtils.current_sd_user().user_id
                application_status.next_officer_in_charge_ref = DatabaseUtils.current_sd_user()
                application_status.officer_in_charge_ref = DatabaseUtils.current_sd_user()
                application_status.officer_in_charge = DatabaseUtils.current_sd_user().user_id
                self.application.statuses.append(application_status)
        except SQLAlchemyError, e:
            self.rollback_to_savepoint()
            raise LM2Exception(self.tr("File Error"),
                               self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

    def __save_applicant(self):

        person_id = self.personal_id_edit.text()
        person = self.session.query(BsPerson).filter(BsPerson.person_register == person_id).\
            order_by(BsPerson.parent_id.asc()).first()
        role_ref = self.session.query(ClPersonRole).filter_by(
            code=Constants.APPLICANT_ROLE_CODE).one()

        # self.create_savepoint()
        # try:
        app_person_role = CtApplicationPersonRole()
        app_person_role.application = self.application.app_id
        app_person_role.share = Decimal(1.0)
        app_person_role.role = Constants.APPLICANT_ROLE_CODE
        app_person_role.role_ref = role_ref
        app_person_role.person = person.person_id
        app_person_role.person_ref = person
        app_person_role.main_applicant = True

        self.application.stakeholders.append(app_person_role)

        # except SQLAlchemyError, e:
        #     self.rollback_to_savepoint()
        #     raise LM2Exception(self.tr("File Error"),
        #                        self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

        self.__multi_applicant_save(person_id, self.application)

    def __multi_applicant_save(self, person_id, application):

        register = person_id

        sql = "select register, ovog,ner ,hen,zahid " \
              "from ub_lpis_co info " \
              "where oregister = :register "

        result = self.session.execute(sql, {'register': register})
        self.create_savepoint()
        try:
            row = 0
            for item_row in result:
                person_id = item_row[0]

                person = self.session.query(BsPerson).filter(BsPerson.person_register == person_id).one()

                role_ref = self.session.query(ClPersonRole).filter_by(
                    code=Constants.APPLICANT_ROLE_CODE).one()
                app_person_count = self.session.query(CtApplicationPersonRole).\
                    filter(CtApplicationPersonRole.application == application.app_id).\
                    filter(CtApplicationPersonRole.role == Constants.APPLICANT_ROLE_CODE).\
                    filter(CtApplicationPersonRole.person == person.person_id).count()
                if app_person_count == 0:
                    app_person_role = CtApplicationPersonRole()
                    app_person_role.application = application.app_id
                    app_person_role.share = Decimal(0)
                    app_person_role.role = Constants.APPLICANT_ROLE_CODE
                    app_person_role.role_ref = role_ref
                    app_person_role.person = person.person_id
                    app_person_role.person_ref = person
                    app_person_role.main_applicant = True

                    application.stakeholders.append(app_person_role)
        except SQLAlchemyError, e:
            self.rollback_to_savepoint()
            raise LM2Exception(self.tr("File Error"),
                               self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

    def __save_person(self):

        person_id = self.personal_id_edit.text()
        person_id = person_id.upper()
        self.create_savepoint()
        try:
            person_count = self.session.query(BsPerson).filter(BsPerson.person_register == person_id).count()
            if person_count > 0:
                bs_person = self.session.query(BsPerson).filter(BsPerson.person_register == person_id).first()
            else:
                bs_person = BsPerson()

                person_type = self.person_type_cbox.itemData(self.person_type_cbox.currentIndex())
                bs_person.person_register = person_id
                bs_person.type = person_type
                if person_type == 10 or person_type == 20 or person_type == 50:
                    bs_person.name = self.first_name_edit.text()
                    bs_person.first_name = self.name_edit.text()
                    bs_person.middle_name = self.middle_name_edit.text()
                else:
                    bs_person.name = self.name_edit.text()
                    bs_person.contact_surname = self.middle_name_edit.text()
                    bs_person.contact_first_name = self.first_name_edit.text()

                bs_person.date_of_birth = DatabaseUtils.convert_date(self.date_of_birth_date.date())
                bs_person.mobile_phone = self.phone_edit.text()
                bs_person.address_building_no = self.building_edit.text()
                bs_person.address_apartment_no = self.apartment_edit.text()
                bs_person.address_street_name = self.person_street_name_edit.text()
                bs_person.address_khaskhaa = self.person_khashaa_edit.text()

                aimag = self.aimag_cbox.itemData(self.aimag_cbox.currentIndex())
                if aimag == -1:
                    bs_person.au_level1_ref = None
                else:
                    bs_person.address_au_level1 = aimag

                soum = self.soum_cbox.itemData(self.soum_cbox.currentIndex())
                if soum == -1:
                    bs_person.address_au_level2 = None
                else:
                    bs_person.address_au_level2 = soum

                bag = self.bag_cbox.itemData(self.bag_cbox.currentIndex())
                if bag == -1:
                    bs_person.address_au_level3 = None
                else:
                    bs_person.address_au_level3 = bag
                if person_count == 0:
                    self.session.add(bs_person)
        except SQLAlchemyError, e:
            self.rollback_to_savepoint()
            raise LM2Exception(self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
        # self.session.flush()

        self.__multi_owner_save(person_id)

    def __check_parcel_correct(self, geometry, error_message):

        organization = DatabaseUtils.current_user_organization()

        valid = True
        if not organization:
            return

        if organization == 1:
            # Тусгай хамгаалалтай болон чөлөөт бүсд нэгж талбар оруулж болохгүй
            count = self.session.query(AuMpa.id) \
                .filter(geometry.ST_Intersects(AuMpa.geometry)).count()
            if count > 0:
                valid = False
                parcel_error = self.tr("Parcels mpa boundary overlap!!!")
                error_message = error_message + "\n \n" + parcel_error
        elif organization == 3:
            # Тусгай хамгаалалтай газар нутгаас өөр газар нэгж талбар оруулж болохгүй
            count = self.session.query(AuMpa.id) \
                .filter(geometry.ST_Within(AuMpa.geometry)).count()

            if count == 0:
                valid = False
                parcel_error = self.tr("Parcels out mpa boundary overlap!!!")
                error_message = error_message + "\n \n" + parcel_error
        elif organization == 5:
            # Чөлөөт бүсээс өөр газар нэгж талбар оруулж болохгүй
            test = 0

        return valid, error_message

    def __save_parcel(self):

        parcel_id = self.parcel_id_edit.text()

        old_parcel_id = self.old_parcel_id_edit.text()
        ub_parcel = self.session.query(CaUBParcelTbl).filter(CaUBParcelTbl.old_parcel_id == old_parcel_id).one()
        landuse = self.parcel_landuse_cbox.itemData(self.parcel_landuse_cbox.currentIndex())
        app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())
        au_level1 = DatabaseUtils.working_l1_code()
        au_level2 = DatabaseUtils.working_l2_code()
        self.create_savepoint()
        # try:
        parcel_count = self.session.query(CaParcelTbl.parcel_id).filter(CaParcelTbl.parcel_id == parcel_id).count()
        if parcel_count > 0:
            # parcel = self.session.query(CaParcel).filter(CaParcel.parcel_id == parcel_id).one()
            # parcel.parcel_id = None
            parcel = CaParcel()
            message_box = QMessageBox()
            message_box.setText(u'Нэгж талбарын дугаар давхардаж байна. Шинэ дугаар олгох бол үргэлжүүлнэ үү.')

            no_button = message_box.addButton(self.tr("Yes"), QMessageBox.ActionRole)
            message_box.addButton(self.tr("No"), QMessageBox.ActionRole)
            message_box.exec_()

            if not message_box.clickedButton() == no_button:
                return
            # PluginUtils.show_message(self, u'Анхааруулга',
            #                          u'Нэгж талбарын дугаар давхардаж байна.')
            # return
        elif parcel_count == 0:
            parcel = CaParcel()
            if len(parcel_id) == 10:
                parcel.parcel_id = parcel_id
            else:
                message_box = QMessageBox()
                message_box.setText(u'Нэгж талбарын дугаар буруу байна. Шинэ дугаар олгох бол үргэлжүүлнэ үү.')

                no_button = message_box.addButton(self.tr("Yes"), QMessageBox.ActionRole)
                message_box.addButton(self.tr("No"), QMessageBox.ActionRole)
                message_box.exec_()

                if not message_box.clickedButton() == no_button:
                    return

                # PluginUtils.show_message(self, u'Анхааруулга',
                #                          u'Нэгж талбарын дугаар буруу байна./Жишээ нь: Дугаарын оронгийн урт таарахгүй/')
                # return
        parcel.old_parcel_id = old_parcel_id
        parcel.geo_id = old_parcel_id
        parcel.landuse = landuse
        parcel.address_khashaa = self.khashaa_edit.text()
        parcel.address_streetname = self.streetname_edit.text()
        parcel.address_neighbourhood = self.neighbourhood_edit.text()
        # valid_from = self.decision_date.date().toString(Constants.DATABASE_DATE_FORMAT)

        valid_from = PluginUtils.convert_qt_date_to_python(QDate.currentDate())
        parcel.valid_from = valid_from
        parcel.geometry = ub_parcel.geometry
        self.session.add(parcel)
        self.session.flush()

        app_time = self.decision_date.date().toString(Constants.DATABASE_DATE_FORMAT)
        status_date = self.decision_date.date().toString(Constants.DATABASE_DATE_FORMAT)
        app_no = self.__generate_application_number()
        right_type = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())

        duration = self.duration_sbox.value()
        landuse = self.parcel_landuse_cbox.itemData(self.parcel_landuse_cbox.currentIndex())

        # try:
        # check if the app_no is still valid, otherwise generate new one
        self.application = CtApplication()

        application_status = CtApplicationStatus()
        application_status.ct_application = self.application
        status = self.session.query(ClApplicationStatus).filter_by(code='1').one()
        application_status.status = 1
        application_status.status_ref = status
        application_status.status_date = status_date
        self.application.app_no = app_no
        self.application.app_type = app_type
        self.application.requested_landuse = landuse
        self.application.approved_landuse = landuse
        self.application.app_timestamp = app_time
        self.application.requested_duration = duration
        self.application.approved_duration = duration
        self.application.right_type = right_type
        self.application.created_by = DatabaseUtils.current_sd_user().user_id
        # self.application.created_at = app_time
        # self.application.updated_at = app_time
        self.application.au1 = au_level1
        self.application.au2 = au_level2
        self.application.remarks = ''

        # current_user = QSettings().value(SettingsConstants.USER)
        # officer = self.session.query(SetRole).filter_by(user_name=current_user).filter(SetRole.is_active == True).one()
        application_status.next_officer_in_charge = DatabaseUtils.current_sd_user().user_id
        application_status.next_officer_in_charge_ref = DatabaseUtils.current_sd_user()
        application_status.officer_in_charge_ref = DatabaseUtils.current_sd_user()
        application_status.officer_in_charge = DatabaseUtils.current_sd_user().user_id
        self.application.statuses.append(application_status)

        self.application.parcel = parcel.parcel_id
        self.session.add(self.application)

        # except SQLAlchemyError, e:
        #     self.rollback_to_savepoint()
        #     raise LM2Exception(self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

        qt_date = self.decision_date.date()
        year = str(qt_date.toString("yy"))
        obj_type = 'application\Application'
        PluginUtils.generate_auto_app_no(str(year), str(app_type).zfill(2), au_level2, obj_type, self.session)
            # self.session.commit()

    def __save_application_details(self):

        app_time = self.decision_date.date().toString(Constants.DATABASE_DATE_FORMAT)
        status_date = self.decision_date.date().toString(Constants.DATABASE_DATE_FORMAT)
        app_no = self.__generate_application_number()
        right_type = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())

        app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())

        duration = self.duration_sbox.value()
        landuse = self.parcel_landuse_cbox.itemData(self.parcel_landuse_cbox.currentIndex())

        au_level1 = DatabaseUtils.working_l1_code()
        au_level2 = DatabaseUtils.working_l2_code()
        # try:
        # check if the app_no is still valid, otherwise generate new one
        # self.application = CtApplication()

        application_status = CtApplicationStatus()
        application_status.ct_application = self.application
        status = self.session.query(ClApplicationStatus).filter_by(code='1').one()
        application_status.status = 1
        application_status.status_ref = status
        application_status.status_date = status_date
        self.application.app_no = app_no
        self.application.app_type = app_type
        self.application.requested_landuse = landuse
        self.application.approved_landuse = landuse
        self.application.app_timestamp = app_time
        self.application.requested_duration = duration
        self.application.approved_duration = duration
        self.application.right_type = right_type
        self.application.created_by = DatabaseUtils.current_sd_user().user_id
        # self.application.created_at = app_time
        # self.application.updated_at = app_time
        self.application.au1 = au_level1
        self.application.au2 = au_level2
        self.application.remarks = ''

        # current_user = QSettings().value(SettingsConstants.USER)
        # officer = self.session.query(SetRole).filter_by(user_name=current_user).filter(SetRole.is_active == True).one()
        application_status.next_officer_in_charge = DatabaseUtils.current_sd_user().user_id
        application_status.next_officer_in_charge_ref = DatabaseUtils.current_sd_user()
        application_status.officer_in_charge_ref = DatabaseUtils.current_sd_user()
        application_status.officer_in_charge = DatabaseUtils.current_sd_user().user_id
        self.application.statuses.append(application_status)

        self.application.parcel = self.parcel_id
        self.session.add(self.application)
        self.session.commit()

        # except SQLAlchemyError, e:
        #     self.rollback_to_savepoint()
        #     raise LM2Exception(self.tr("File Error"),
        #                        self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))


    def __doc_tree_view(self):

        model = QFileSystemModel()
        model.setRootPath(FilePath.ub_archive_path())

        self.treeView.setModel(model)
        self.treeView.setRootIndex(model.index(FilePath.ub_archive_path()))
        self.treeView.doubleClicked.connect(self.test)

        rootdir = FilePath.ub_archive_path()

        for subdir, dirs, files in os.walk(rootdir):
            for file in files:
                print file
                print os.path.join(subdir, file)
                print os.path.basename(os.path.dirname(os.path.join(subdir, file)))

    def test(self, signal):

        file_path = self.treeView.model().filePath(signal)
        print(file_path)

    def __is_file(self, ftp ,filename):

        current = ftp.pwd()
        try:
            ftp.cwd(filename)
        except:
            ftp.cwd(current)
            return True
        ftp.cwd(current)
        return False

    @pyqtSlot()
    def on_ftp_connect_button_clicked(self):

        # database_name = QSettings().value(SettingsConstants.DATABASE_NAME)
        # ftp_user_code = database_name.split('_')[1]
        # ftp_user = 'user'+ftp_user_code

        ftp_user = QSettings().value(SettingsConstants.USER)[:8]

        QSettings().setValue(SettingsConstants.FTP_IP, self.ftp_host_edit.text())
        QSettings().setValue(SettingsConstants.FTP_USER, ftp_user)

        ftp_host = self.ftp_host_edit.text()
        retry = True
        while (retry):
            try:
                ftp = FTP(ftp_host, ftp_user, ftp_user)
                ftp.connect()
                retry = False
                self.ftp_connect_button.setEnabled(False)

            except IOError as e:
                retry = True
                PluginUtils.show_message(self, self.tr("LM2", "FTP connection"), self.tr("Document server not connect!!!"))
                return

    def __ftp_find_file(self, files, ftp, doc_id):

        if not files:
            ftp.cwd('/home/administrator/Archive-UB/BGD')
            files = ftp.nlst(str(doc_id))
        if not files:
            ftp.cwd('/home/administrator/Archive-UB/BHD')
            files = ftp.nlst(str(doc_id))
        if not files:
            ftp.cwd('/home/administrator/Archive-UB/BND')
            files = ftp.nlst(str(doc_id))
        if not files:
            ftp.cwd('/home/administrator/Archive-UB/BZD')
            files = ftp.nlst(str(doc_id))
        if not files:
            ftp.cwd('/home/administrator/Archive-UB/CHD')
            files = ftp.nlst(str(doc_id))
        if not files:
            ftp.cwd('/home/administrator/Archive-UB/HUD')
            files = ftp.nlst(str(doc_id))
        if not files:
            ftp.cwd('/home/administrator/Archive-UB/ND')
            files = ftp.nlst(str(doc_id))
        if not files:
            ftp.cwd('/home/administrator/Archive-UB/SBD')
            files = ftp.nlst(str(doc_id))
        if not files:
            ftp.cwd('/home/administrator/Archive-UB/SHD')
            files = ftp.nlst(str(doc_id))

        return files, ftp.pwd()

    @pyqtSlot()
    def on_load_docs_button_clicked(self):

        self.doc_twidget.setRowCount(0)
        ftp_host = QSettings().value(SettingsConstants.FTP_IP)
        ftp_user = QSettings().value(SettingsConstants.FTP_USER)

        ftp = FTP(ftp_host, ftp_user, ftp_user)

        doc_id = self.documet_cbox.itemData(self.documet_cbox.currentIndex())

        files = []
        is_find_doc = False
        parent_path = ''
        if doc_id:

            try:
                if doc_id in ftp.nlst():
                    files = ftp.nlst(str(doc_id))
                else:
                    files = self.__ftp_find_file(files, ftp, doc_id)[0]
                    parent_path = self.__ftp_find_file(files, ftp, doc_id)[1]

            except error_perm:
                files = self.__ftp_find_file(files, ftp, doc_id)[0]
                parent_path = self.__ftp_find_file(files, ftp, doc_id)[1]
                is_find_doc = True

            if is_find_doc:
                try:
                    if doc_id in ftp.nlst():
                        files = ftp.nlst(doc_id)
                except error_perm:
                    is_find_doc = True

            doc_no_list = []
            docs = self.session.query(ClDocumentRole).all()
            for doc in docs:
                doc_code = str(doc.code)
                if len(doc_code) == 1:
                    doc_code = '0'+doc_code
                doc_no_list.append(doc_code)
            for f in files:
                files = ftp.nlst(f)
                for n in files:
                    if self.__is_file(ftp, n):

                        file_name = str(n.split('/')[-1])
                        doc_no = str(n.split('/')[-2])[:2]

                        subdir = parent_path + '/' + str(n.split('/')[0]) + '/' + str(n.split('/')[1]) + '/' + str(n.split('/')[2])
                        # subdir = str(n.split('/')[0]) + '/' + str(n.split('/')[1]) + '/' + str(n.split('/')[2])

                        if doc_no in doc_no_list:
                            document = self.session.query(ClDocumentRole).filter(ClDocumentRole.code == doc_no).one()

                            row = self.doc_twidget.rowCount()
                            self.doc_twidget.insertRow(row)

                            item_name = QTableWidgetItem()
                            item_name.setText(str(file_name))
                            item_name.setData(Qt.UserRole, ftp.pwd())
                            item_name.setData(Qt.UserRole + 1, n)

                            item_description = QTableWidgetItem()
                            item_description.setText(document.description)

                            item_view = QTableWidgetItem()

                            self.doc_twidget.setItem(row, 0, item_name)
                            self.doc_twidget.setItem(row, 1, item_description)
                            self.doc_twidget.setItem(row, 2, item_view)
            self.__load_doc_info()

    @pyqtSlot(int, int)
    def on_lpis_info_twidget_cellChanged(self, row, column):

        changed_item = self.lpis_info_twidget.item(row, column)
        if changed_item:
            if changed_item.checkState() == Qt.Checked:
                if column == 0:
                    self.personal_id_edit.setText(changed_item.text())
                if column == 1:
                    self.first_name_edit.setText(changed_item.text())
                if column == 2:
                    self.name_edit.setText(changed_item.text())
                if column == 3:
                    self.phone_edit.setText(changed_item.text())
                if column == 5:
                    self.person_street_name_edit.setText(changed_item.text())
                if column == 6:
                    self.parcel_id_edit.setText(changed_item.text())
                if column == 9:
                    self.decision_no_edit.setText(changed_item.text())
                if column == 10:
                    self.record_cert_edit.setText(changed_item.text())

    @pyqtSlot(int, int)
    def on_landuk_info_twidget_cellChanged(self, row, column):

        changed_item = self.landuk_info_twidget.item(row, column)
        if changed_item:
            if changed_item.checkState() == Qt.Checked:
                if column == 0:
                    self.personal_id_edit.setText(changed_item.text())
                if column == 1:
                    self.middle_name_edit.setText(changed_item.text())
                if column == 2:
                    self.name_edit.setText(changed_item.text())
                if column == 3:
                    self.first_name_edit.setText(changed_item.text())
                if column == 4:
                    self.person_street_name_edit.setText(changed_item.text())
                if column == 5:
                    self.phone_edit.setText(changed_item.text())

    @pyqtSlot(int, int)
    def on_fee_info_twidget_cellChanged(self, row, column):

        changed_item = self.fee_info_twidget.item(row, column)
        if changed_item:
            if changed_item.checkState() == Qt.Checked:
                if column == 0:
                    self.personal_id_edit.setText(changed_item.text())
                if column == 1:
                    self.name_edit.setText(changed_item.text())
                if column == 2:
                    self.phone_edit.setText(changed_item.text())
                if column == 6:
                    self.person_street_name_edit.setText(changed_item.text())
                if column == 7:
                    self.person_khashaa_edit.setText(changed_item.text())

    @pyqtSlot(int, int)
    def on_doc_info_twidget_cellChanged(self, row, column):

        changed_item = self.doc_info_twidget.item(row, column)
        if changed_item.checkState() == Qt.Checked:
            if column == 0:
                self.parcel_id_edit.setText(changed_item.text())
            if column == 1:
                decision_level = 10
                if changed_item.text() == u'ДЗД':
                    decision_level = 20
                elif changed_item.text() == u'АЗД':
                    decision_level = 30
                elif changed_item.text() == u'СЗД':
                    decision_level = 40
                elif changed_item.text() == u'НАТ':
                    decision_level = 70
                self.decision_level_cbox.setCurrentIndex(self.decision_level_cbox.findData(decision_level))
            if column == 2:
                self.decision_no_edit.setText(changed_item.text())
            if column == 3:
                self.decision_date.setDate(changed_item.data(Qt.UserRole))
            if column == 4:
                self.first_name_edit.setText(changed_item.text())
            if column == 5:
                self.name_edit.setText(changed_item.text())
            if column == 6:
                self.personal_id_edit.setText(changed_item.text())
            if column == 7:
                self.streetname_edit.setText(changed_item.text())
                self.neighbourhood_edit.setText(changed_item.text())

    def __load_doc_info(self):

        self.doc_info_twidget.setRowCount(0)
        doc_id = self.documet_cbox.itemData(self.documet_cbox.currentIndex())

        sql = "select new_block_id, decision_level, decision_no, decision_date, firstname, name, register, address " \
              "from ub_document where document_no = :doc_id "

        result = self.session.execute(sql, {'doc_id': doc_id})
        row = 0
        for item_row in result:
            new_pid = item_row[0]

            row = self.doc_info_twidget.rowCount()
            self.doc_info_twidget.insertRow(row)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(unicode(new_pid))
            item.setData(Qt.UserRole, new_pid)
            self.doc_info_twidget.setItem(row, 0, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText((item_row[1]))
            item.setData(Qt.UserRole, item_row[1])
            self.doc_info_twidget.setItem(row, 1, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(item_row[2])
            item.setData(Qt.UserRole, item_row[2])
            self.doc_info_twidget.setItem(row, 2, item)

            decision_date = datetime.datetime.strptime(item_row[3], '%Y%m%d').date()
            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(str(decision_date))
            item.setData(Qt.UserRole, decision_date)
            self.doc_info_twidget.setItem(row, 3, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(item_row[4])
            item.setData(Qt.UserRole, item_row[4])
            self.doc_info_twidget.setItem(row, 4, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(item_row[5])
            item.setData(Qt.UserRole, item_row[5])
            self.doc_info_twidget.setItem(row, 5, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(item_row[6])
            item.setData(Qt.UserRole, item_row[6])
            self.doc_info_twidget.setItem(row, 6, item)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)
            item.setText(item_row[7])
            item.setData(Qt.UserRole, item_row[7])
            self.doc_info_twidget.setItem(row, 7, item)

            row =+ 1

    def __load_doc(self):

        self.documet_cbox.clear()
        old_parcel_id = self.old_parcel_id_edit.text()
        person_id = self.personal_id_edit.text()

        sql = "select document_no, decision_date, register, firstname, name " \
              "from ub_document where pid = :pid or register = :person_id "

        result = self.session.execute(sql, {'pid': old_parcel_id,
                                            'person_id': person_id})
        for row in result:
            doc_id = row[0]
            doc_decs = row[1]+'-/'+unicode(row[2])+'/-'+unicode(row[4])
            self.documet_cbox.addItem(doc_decs, doc_id)

    @pyqtSlot()
    def on_fee_view_button_clicked(self):

        old_parcel_id = self.old_parcel_id_edit.text()
        person_id = self.personal_id_edit.text()
        is_find = False
        if self.old_parcel_id_edit.text():
            is_find = True
        dialog = ParcelInfoFeeDialog(old_parcel_id, person_id, is_find, self.plugin)
        dialog.exec_()

    @pyqtSlot()
    def on_fee_layer_view_button_clicked(self):

        root = QgsProject.instance().layerTreeRoot()

        restrictions = DatabaseUtils.working_l2_code()
        if not restrictions:
            PluginUtils.show_message(self, self.tr("Connection Error"), self.tr("Please connect to database!!!"))
            return

        mygroup = root.findGroup("UbGIS")
        if mygroup is None:
            mygroup = root.insertGroup(8, "UbGIS")

        schema_name = "data_ub"
        table_name = "ca_ub_parcel_fee"
        layer_list = []
        layers = QgsMapLayerRegistry.instance().mapLayers()

        for id, layer in layers.iteritems():
            if layer.type() == QgsMapLayer.VectorLayer:
                uri_string = layer.dataProvider().dataSourceUri()
                uri = QgsDataSourceURI(uri_string)
                if uri.table() == table_name:
                    if uri.schema() == schema_name:
                        layer_list.append(id)

        vlayer = LayerUtils.layer_by_data_source(schema_name, table_name)
        if vlayer:
            QgsMapLayerRegistry.instance().removeMapLayers(layer_list)

        vlayer_parcel = LayerUtils.load_ub_data_layer_by_name("ca_ub_parcel_fee", "gid")

        employee = DatabaseUtils.current_employee()
        department_id = employee.department_id

        city_type_name = u''
        if department_id == 120:
            city_type = 1
            city_type_name = 'City'
            expression = 'city_type = 1'
            exp = QgsExpression(expression)
            exp.prepare(vlayer_parcel.pendingFields())
            request = QgsFeatureRequest().setFilterExpression(expression)
            vlayer_parcel.getFeatures(request)
        else:
            city_type = 2
            expression = 'city_type = 2'
            city_type_name = 'District'
            exp = QgsExpression(expression)
            exp.prepare(vlayer_parcel.pendingFields())
            request = QgsFeatureRequest().setFilterExpression(expression)
            vlayer_parcel.getFeatures(request)
        au2 = DatabaseUtils.working_l2_code()
        selected_year = self.fee_year_layer_cbox.itemData(self.fee_year_layer_cbox.currentIndex())
        sql_layer = "(SELECT row_number() OVER () AS gid, p.parcel_id, p.old_parcel_id, p.landuse, p.area_m2, h.document_area, h.current_year, " \
                    "h.city_type, h.status, p.address_khashaa, p.address_streetname, p.address_neighbourhood, p.valid_from, p.valid_till, p.geometry, " \
                    "p.edit_status, p.au2 FROM data_ub.ca_ub_parcel_tbl p " \
                    "JOIN data_ub.ub_fee_history h ON p.old_parcel_id::text = h.pid::text " \
                    "where p.au2 = " + "'" + au2 + "'" + " and h.current_year = " + str(selected_year) + " and city_type = " + str(city_type) + ")"

        layer_name = str(selected_year) + "_" + (city_type_name)
        layers = QgsMapLayerRegistry.instance().mapLayers()

        for id, layer in layers.iteritems():
            if layer.type() == QgsMapLayer.VectorLayer:
                if layer.name() == layer_name:
                    layer_list.append(id)

        vlayer_parcel = LayerUtils.layer_by_data_source("", sql_layer)
        if vlayer_parcel:
            QgsMapLayerRegistry.instance().removeMapLayers(layer_list)
        vlayer_parcel = LayerUtils.load_temp_table(sql_layer, layer_name)

        mygroup.addLayer(vlayer_parcel)

        vlayer_parcel.setLayerName(QApplication.translate("Plugin", layer_name))

        vlayer_parcel.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "template\style/ub_parcel_fee.qml")

    @pyqtSlot()
    def on_layer_view_button_clicked(self):

        root = QgsProject.instance().layerTreeRoot()

        restrictions = DatabaseUtils.working_l2_code()
        if not restrictions:
            PluginUtils.show_message(self, self.tr("Connection Error"), self.tr("Please connect to database!!!"))
            return

        mygroup = root.findGroup("UbGIS")
        if mygroup is None:
            mygroup = root.insertGroup(8, "UbGIS")

        is_pug_parcel = False

        vlayer_parcel = LayerUtils.load_ub_data_layer_by_name("ca_ub_parcel", "old_parcel_id")


        layers = self.plugin.iface.legendInterface().layers()

        for layer in layers:
            if layer.name() == "UbGISParcel":
                is_pug_parcel = True
        if not is_pug_parcel:
            mygroup.addLayer(vlayer_parcel)

        vlayer_parcel.setLayerName(QApplication.translate("Plugin", "UbGISParcel"))
        vlayer_parcel.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "template\style/ub_parcel.qml")

        table_name = "ca_ub_decision"
        vlayer = LayerUtils.layer_by_data_source("data_ub", table_name)
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer(table_name, "row_number", "data_ub")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/ca_ub_desicion.qml")
        vlayer.setLayerName(self.tr("Ub Decision Type"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            mygroup.addLayer(vlayer)

        table_name = "ub_sort"
        vlayer = LayerUtils.layer_by_data_source("report", table_name)
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer(table_name, "row_number", "report")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/ca_ub_sort.qml")
        vlayer.setLayerName(self.tr("Ub Sort"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            mygroup.addLayer(vlayer)

    @pyqtSlot(QTableWidgetItem)
    def on_landuk_info_twidget_itemClicked(self, item):

        selected_row = self.landuk_info_twidget.currentRow()
        object_id = self.landuk_info_twidget.item(selected_row, 0).data(Qt.UserRole)
        old_pid = self.landuk_info_twidget.item(selected_row, 0).data(Qt.UserRole + 1)

        sql = "select person_type_desc, country,contact_firstname,contact_lastname,contact_position, " \
              "pid::text, zoriulalt_desc, area_m2, fee, unit_price, decision_no, decision_date, certificate_no, duration, " \
              "right_type_desc, is_mortgage, objectid, old_pid " \
              "from ub_landuk_info info " \
              "where objectid = :object_id "

        result = self.session.execute(sql, {'object_id': object_id})
        for item_row in result:
            self.landuk_person_type_edit.setText(item_row[0])
            self.landuk_country_edit.setText(item_row[1])
            self.contact_firstname_edit.setText(item_row[2])
            self.contact_lastname_edit.setText(item_row[3])
            self.contact_position_edit.setText((item_row[4]))
            self.landuk_parcel_id_edit.setText(str(item_row[5]))
            self.landuk_landuse_edit.setText(item_row[6])
            self.landuk_area_edit.setText(str(item_row[7]))
            self.landuk_fee_edit.setText(str(item_row[8]))
            self.landuk_unit_price_edit.setText(str(item_row[9]))
            self.landuk_deicsion_no_edit.setText(item_row[10])
            self.landuk_certificate_edit.setText(str(item_row[12]))
            self.landuk_duration_edit.setText(str(item_row[13]))
            self.landuk_right_type_edit.setText(item_row[14])
            self.is_mortgage_edit.setText(str(item_row[15]))

        self.__load_landuk_bank(old_pid)

    def __load_landuk_bank(self, old_pid):

        self.landuk_mortgage_twidget.setRowCount(0)

        sql = "select person_name, bank_name, rent_contract_no, mortgage_contract_no,mortgate_date, price, is_mortgage, objectid, old_pid " \
              "from ub_landuk_bank bank " \
              "where old_pid = :old_pid "
        result = self.session.execute(sql, {'old_pid': old_pid})
        row = 0
        for item_row in result:
            row = self.landuk_mortgage_twidget.rowCount()
            self.landuk_mortgage_twidget.insertRow(row)
            item = QTableWidgetItem()
            item.setText(unicode(item_row[0]))
            item.setData(Qt.UserRole, item_row[7])
            item.setData(Qt.UserRole+1, item_row[8])
            self.landuk_mortgage_twidget.setItem(row, 0, item)

            item = QTableWidgetItem()
            item.setText(unicode(item_row[1]))
            self.landuk_mortgage_twidget.setItem(row, 1, item)

            item = QTableWidgetItem()
            item.setText(unicode(item_row[2]))
            self.landuk_mortgage_twidget.setItem(row, 2, item)

            item = QTableWidgetItem()
            item.setText(unicode(item_row[3]))
            self.landuk_mortgage_twidget.setItem(row, 3, item)

            item = QTableWidgetItem()
            item.setText(unicode(item_row[4]))
            self.landuk_mortgage_twidget.setItem(row, 4, item)

            item = QTableWidgetItem()
            item.setText(unicode(item_row[5]))
            self.landuk_mortgage_twidget.setItem(row, 5, item)

            item = QTableWidgetItem()
            item.setText(unicode(item_row[6]))
            self.landuk_mortgage_twidget.setItem(row, 6, item)

            row =+ 1

    @pyqtSlot(int)
    def on_landuk_search_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.landuk_person_id_edit.setEnabled(True)
            self.landuk_old_parcel_id_edit.setEnabled(True)
            self.landuk_find_button.setEnabled(True)
        else:
            self.landuk_person_id_edit.setEnabled(False)
            self.landuk_old_parcel_id_edit.setEnabled(False)
            self.landuk_find_button.setEnabled(False)

    @pyqtSlot(int)
    def on_lpis_search_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.lpis_person_id_edit.setEnabled(True)
            self.lpis_old_parcel_id_edit.setEnabled(True)
            self.lpis_find_button.setEnabled(True)
        else:
            self.lpis_person_id_edit.setEnabled(False)
            self.lpis_old_parcel_id_edit.setEnabled(False)
            self.lpis_find_button.setEnabled(False)

    @pyqtSlot()
    def on_landuk_find_button_clicked(self):

        person_id = self.landuk_person_id_edit.text()
        old_parcel_id = self.landuk_old_parcel_id_edit.text()
        self.__load_landuk(person_id, old_parcel_id)

    @pyqtSlot()
    def on_lpis_find_button_clicked(self):

        person_id = self.lpis_person_id_edit.text()
        old_parcel_id = self.lpis_old_parcel_id_edit.text()
        self.__load_lpis(person_id, old_parcel_id)

    @pyqtSlot(QTableWidgetItem)
    def on_lpis_info_twidget_itemClicked(self, item):

        self.lpis_co_owner_twidget.setRowCount(0)

        selected_row = self.lpis_info_twidget.currentRow()
        if selected_row == -1:
            return
        register = self.lpis_info_twidget.item(selected_row, 0).data(Qt.UserRole)
        lpis_id = self.lpis_info_twidget.item(selected_row, 0).data(Qt.UserRole + 1)

        sql = "select register, ovog,ner ,hen,zahid " \
              "from ub_lpis_co info " \
              "where oregister = :register "

        result = self.session.execute(sql, {'register': register})
        row = 0
        for item_row in result:
            row = self.lpis_co_owner_twidget.rowCount()
            self.lpis_co_owner_twidget.insertRow(row)
            item = QTableWidgetItem()
            item.setText(unicode(item_row[0]))
            item.setData(Qt.UserRole, item_row[0])
            self.lpis_co_owner_twidget.setItem(row, 0, item)

            item = QTableWidgetItem()
            item.setText(unicode(item_row[1]))
            self.lpis_co_owner_twidget.setItem(row, 1, item)

            item = QTableWidgetItem()
            item.setText(unicode(item_row[2]))
            self.lpis_co_owner_twidget.setItem(row, 2, item)

            item = QTableWidgetItem()
            item.setText(unicode(item_row[3]))
            self.lpis_co_owner_twidget.setItem(row, 3, item)

            item = QTableWidgetItem()
            item.setText(unicode(item_row[4]))
            self.lpis_co_owner_twidget.setItem(row, 4, item)

            row =+ 1

    def __find_coordinate(self, x, y):

        scale = self.point_scale_sbox.value()
        if self.coordinate_chbox.isChecked():
            p = pyproj.Proj(
                "+proj=tmerc +lat_0=0 +lon_0=105 +k=1 +x_0=500000 +y_0=0 +ellps=WGS84 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs")

            lon, lat = p(x, y, inverse=True)
            x = lon
            y = lat

            p = pyproj.Proj(proj='utm', zone=48, ellps='WGS84')
            x, y = p(x, y)

        rect = QgsRectangle(
            float(x) - scale,
            float(y) - scale,
            float(x) + scale,
            float(y) + scale)

        mc = self.plugin.iface.mapCanvas()
        mc.setExtent(rect)
        mc.refresh()

    @staticmethod
    def __utm_proj4def_from_point_itrf(point):

        proj4Def = ""
        zoneNumber = ((point.x() + 180) / 6) + 1
        zoneNumber = str(zoneNumber).split(".")[0]

        proj4Def = "tmerc +lat_0=0 +lon_0=105 +k=1 +x_0=500000 +y_0=0 +ellps=WGS84 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
        # if point.y() < 0:
        #     proj4Def = "+proj=utm +zone={0} +south +datum=WGS84 +units=m +no_defs".format(zoneNumber)
        # else:
        #     proj4Def = "+proj=utm +zone={0} +datum=WGS84 +units=m +no_defs".format(zoneNumber)

        return proj4Def

    def newOnkeyPressEvent(self, e):
        if self.is_find_ubgis:
            if e.key() == QtCore.Qt.Key_Enter:
                self.find_button.click()
                print "User has pushed escape"


    def keyPressEvent(self, eventQKeyEvent):
        key = eventQKeyEvent.key()
        if key == QtCore.Qt.Key_F1:
            print 'Help'
        elif key == QtCore.Qt.Key_F5:
            print 'Reload'
        elif key == QtCore.Qt.Key_Left:
            print 'Left'
        elif key == QtCore.Qt.Key_Up:
            print 'Up'
        elif key == QtCore.Qt.Key_Right:
            print 'Right'
        elif key == QtCore.Qt.Key_Down:
            print 'Down'

    @pyqtSlot()
    def on_current_dialog_closed(self):

        DialogInspector().set_dialog_visible(False)

    def check_dir_ftp(self, dir, ftp_conn):

        filelist = []
        ftp_conn.retrlines('LIST', filelist.append)
        found = False

        for f in filelist:
            if f.split()[-1] == dir and f.lower().startswith('d'):
                found = True

        return found

    @pyqtSlot()
    def on_load_new_docs_button_clicked(self):

        self.new_doc_twidget.setRowCount(0)
        is_find_doc = False

        soum_code = DatabaseUtils.working_l2_code()
        archive_path = 'geomaster_archive/'+soum_code
        if not self.parcel_id_edit.text():
            return

        base_parcel_id = None
        parcel_id = self.parcel_id_edit.text()
        ub_parcel_count = self.session.query(CaUBParcelTbl).filter(CaUBParcelTbl.parcel_id == parcel_id).count()
        if ub_parcel_count > 0:
            ub_parcel = self.session.query(CaUBParcelTbl).filter(CaUBParcelTbl.parcel_id == parcel_id).first()
            base_parcel_id = ub_parcel.parcel_base_id

        if not base_parcel_id:
            return

        if not self.decision_no_edit.text():
            return

        files = None
        decision_no = self.decision_no_edit.text()
        decision_no = decision_no.replace('/', '')
        if DatabaseUtils.ftp_connect():
            ftp = DatabaseUtils.ftp_connect()
            ftp = ftp[0]
            ftp.cwd(archive_path)
            # FtpConnection.chdir(archive_ftp_path_role, ftp[0])

            try:
                if str(parcel_id) in ftp.nlst():

                    files = ftp.nlst(str(parcel_id))
                else:
                    is_find_doc = False
            except error_perm:
                is_find_doc = False

            if not files:

                parcel_id = '0' + parcel_id[:2] + '0' + parcel_id[2:]

                try:
                    if str(parcel_id) in ftp.nlst():

                        files = ftp.nlst(str(parcel_id))
                    else:
                        is_find_doc = False
                except error_perm:
                    is_find_doc = False

            if not files:
                return

            ch_path = None
            self.decision_num_cbox.clear()
            for f in files:
                f = codecs.decode(f, 'utf-8')
                self.decision_num_cbox.addItem(f, f)

                doc_decision = f.split('/')[-1]
                # doc_decision = doc_decision.decode('utf8')
                doc_decision_no = doc_decision.split('-')[-1]

                doc_decision_no = doc_decision_no.upper()
                decision_no = decision_no.upper()

                doc_decision_no = doc_decision_no.replace('A', '')
                decision_no = decision_no.replace('A', '')

                # doc_decision_no = codecs.decode(doc_decision_no, 'utf-8')

                doc_decision_no = doc_decision_no.replace('A', '')
                decision_no = decision_no.replace('A', '')

                if self.__mysplit(decision_no)[1] == self.__mysplit(doc_decision_no)[1]:
                    self.decision_num_cbox.setCurrentIndex(
                        self.decision_num_cbox.findData(f))

    @pyqtSlot(int)
    def on_decision_num_cbox_currentIndexChanged(self, index):

        self.new_doc_twidget.setRowCount(0)
        ch_path = self.decision_num_cbox.itemData(self.decision_num_cbox.currentIndex())
        soum_code = DatabaseUtils.working_l2_code()
        archive_path = 'geomaster_archive/' + soum_code
        if not DatabaseUtils.ftp_connect():
            return
        ftp = DatabaseUtils.ftp_connect()
        ftp = ftp[0]

        ftp.cwd(archive_path)

        # ftp.cwd(ch_path)
        if ch_path:
            ftp.cwd(unicode(ch_path).encode('utf8'))

            try:
                files = ftp.nlst()
            except error_perm:
                is_find_doc = False

            if not files:
                return

            for f in files:

                if self.__is_file(ftp, f):
                    file_full_name = f
                    file_name = f.split('.')[0]
                    file_type = str(f.split('.')[-1])
                    doc_no = file_name[-2:]

                    if self.session.query(ClDocumentRole).filter(ClDocumentRole.code == doc_no).count() == 1:
                        document = self.session.query(ClDocumentRole).filter(ClDocumentRole.code == doc_no).one()

                        row = self.new_doc_twidget.rowCount()
                        self.new_doc_twidget.insertRow(row)

                        item_name = QTableWidgetItem()
                        item_name.setText(str(file_name))
                        item_name.setData(Qt.UserRole, ftp)
                        item_name.setData(Qt.UserRole + 1, file_full_name)
                        item_name.setData(Qt.UserRole + 2, file_type)
                        item_name.setData(Qt.UserRole + 3, doc_no)

                        item_description = QTableWidgetItem()
                        item_description.setText(document.description)

                        item_view = QTableWidgetItem()

                        self.new_doc_twidget.setItem(row, 0, item_name)
                        self.new_doc_twidget.setItem(row, 1, item_description)
                        self.new_doc_twidget.setItem(row, 2, item_view)

    def __import_archive(self):

        decision_no = self.decision_no_edit.text()
        decision_no = decision_no.replace('/', '')

        f = self.decision_num_cbox.itemData(self.decision_num_cbox.currentIndex())
        if not f:
            return
        doc_decision = f.split('/')[-1]
        # doc_decision = doc_decision.decode('utf8')
        doc_decision_no = doc_decision.split('-')[-1]

        doc_decision_no = doc_decision_no.upper()
        decision_no = decision_no.upper()

        doc_decision_no = doc_decision_no.replace('A', '')
        decision_no = decision_no.replace('A', '')

        doc_decision_no = doc_decision_no.replace(u'A', '')
        decision_no = decision_no.replace(u'A', '')

        if self.__mysplit(decision_no)[1] == self.__mysplit(doc_decision_no)[1]:
            message_box = QMessageBox()
            message_box.setText(u'Цахим архив оруулах уу?')

            yes_button = message_box.addButton(u'Тийм', QMessageBox.ActionRole)
            message_box.addButton(u'Үгүй', QMessageBox.ActionRole)
            message_box.exec_()

            if message_box.clickedButton() == yes_button:
                if DatabaseUtils.ftp_connect():
                    ftp = None
                    for row in range(self.new_doc_twidget.rowCount()):

                        # archive_ftp_path = FilePath.app_ftp_parent_path() + '/' + str(self.parent.current_application_no())
                        ftp = self.new_doc_twidget.item(row, 0).data(Qt.UserRole)
                        file_name = self.new_doc_twidget.item(row, 0).data(Qt.UserRole + 1)
                        file_type = self.new_doc_twidget.item(row, 0).data(Qt.UserRole + 2)
                        role = self.new_doc_twidget.item(row, 0).data(Qt.UserRole + 3)

                        if str(role) == '17':
                            role = '22'

                        view_pdf = open(FilePath.view_file_path(), 'wb')
                        view_png = open(FilePath.view_file_png_path(), 'wb')

                        file_url = None
                        if file_type == 'png':
                            ftp.retrbinary('RETR ' + file_name, view_png.write)
                            file_url = FilePath.view_file_png_path()
                        else:
                            ftp.retrbinary('RETR ' + file_name, view_pdf.write)
                            file_url = FilePath.view_file_path()
                        view_pdf.close()
                        view_png.close()
                        if file_url:

                            if DatabaseUtils.ftp_connect():
                                ftp = DatabaseUtils.ftp_connect()
                                file_info = QFileInfo(file_url)
                                file_name = str(self.application.app_no) + "-" + str(role).zfill(
                                    2) + "." + file_info.suffix()
                                archive_ftp_path = FilePath.app_ftp_parent_path() + '/' + str(self.application.app_no)
                                archive_ftp_path_role = archive_ftp_path + '/' + str(role).zfill(2)
                                FtpConnection.chdir(archive_ftp_path_role, ftp[0])
                                FtpConnection.upload_app_ftp_file(file_url, file_name,ftp[0])

                                app_id = self.application.app_id

                                conf = self.session.query(SdConfiguration).filter(SdConfiguration.code == 'ip_web_lm').one()
                                urllib2.urlopen(
                                    'http://' + conf.value + '/api/application/document/move?app_id=' + str(app_id))


                    conf = self.session.query(SdConfiguration).filter(SdConfiguration.code == 'ip_web_lm').one()
                    urllib2.urlopen(
                        'http://' + conf.value + '/api/application/document/move?app_id=' + str(
                            self.application.app_id))

    def __similar(self, a, b):

        return SequenceMatcher(None, a, b).ratio()

    def __mysplit(self, s):

        head = s.rstrip('0123456789')

        tail = s[len(head):]
        return head, tail

    @pyqtSlot(int)
    def on_edit_status_cbox_currentIndexChanged(self, index):

        self.delete_gbox.setVisible(False)
        self.deleted_decision_date.setDate(QDate.currentDate())
        code = self.edit_status_cbox.itemData(self.edit_status_cbox.currentIndex())
        if code == DELETE_STATUS:
            self.delete_gbox.setVisible(True)

    def __save_delete_parcel(self):

        if not self.delete_decision_no_edit.text():
            PluginUtils.show_message(self, u'Анхааруулга', u'Нэгт талбарыг устгасан шийдвэрийн дугаарыг оруулна уу!')
            return

        old_parcel_id = self.old_parcel_id_edit.text()
        ub_parcel = self.session.query(CaUBParcelTbl).filter(CaUBParcelTbl.old_parcel_id == old_parcel_id).one()
        edit_status = self.edit_status_cbox.itemData(self.edit_status_cbox.currentIndex())

        ub_parcel.edit_status = edit_status
        ub_parcel.deleted_status_date = PluginUtils.convert_qt_date_to_python(QDate.currentDate())
        ub_parcel.deleted_status_decision_date = PluginUtils.convert_qt_date_to_python(self.deleted_decision_date.date())
        ub_parcel.deleted_status_decision_no = self.delete_decision_no_edit.text()
        ub_parcel.deleted_status_comment = self.deleted_comment_edit.toPlainText()
        ub_parcel.deleted_status_user = DatabaseUtils.current_user().user_name