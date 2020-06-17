# coding=utf8
__author__ = 'B.Ankhbold'

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from geoalchemy2.elements import WKTElement
from qgis.core import *
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, or_, and_, desc
from geoalchemy2 import functions
from geoalchemy2.shape import to_shape
from inspect import currentframe
from decimal import Decimal
from ..view.Ui_ParcelMpaDialog import *
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
from ..model.MpaGisEditSubject import *
from ..model.ClDocumentRole import *
from ..model.CtDecision import *
from ..model.CaParcelTbl import *
from ..model.CtContractApplicationRole import *
from ..model.AuLevel1 import *
from ..model.AuLevel2 import *
from ..model.AuLevel3 import *
from ..model import SettingsConstants
from ..model import Constants
from ..model.SetRightTypeApplicationType import *
from ..model.LM2Exception import LM2Exception
from ..model.ClPositionType import *
from ..model.ClUbEditStatus import *
from ..model.Enumerations import PersonType, UserRight
from ..model.DatabaseHelper import *
from ..model.AuMpa import *
from ..utils.SessionHandler import SessionHandler
from ..utils.FilePath import *
from .qt_classes.UbDocumentViewDelegate import UbDocumentViewDelegate
import math
import locale
import os
import pyproj
from difflib import SequenceMatcher
import urllib
import urllib2
import json
import shutil
import sys
import datetime
from ftplib import FTP, error_perm
from contextlib import closing

class ParcelMpaDialog(QDockWidget, Ui_ParcelMpaDialog, DatabaseHelper):

    RIGTHTYPE, CODEIDCARD, NAME, FIRSTNAME, OLD_PARCEL_ID, PARCEL_ID, DECISION_NO, DECISION_DATE, CONTRACT_NO, CONTRACT_DATE = range(10)

    zoriulalt = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    STREET_NAME = 7
    KHASHAA_NAME = 6
    GEO_ID = 2
    # OLD_PARCEL_ID = 1

    def __init__(self, plugin, parent=None):

        super(ParcelMpaDialog, self).__init__(parent)
        DatabaseHelper.__init__(self)

        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.plugin = plugin
        self.session = SessionHandler().session_instance()
        # self.keyPressEvent = self.newOnkeyPressEvent
        self.is_find_ubgis = True
        self.parcel_id = None
        self.setupUi(self)

        self.application = None
        self.contract = None
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
    #
        self.__setup_cbox()
    #
        self.person_tabwidget.currentChanged.connect(self.__tab_widget_onChange)  # changed!
        self.__setup_combo_boxes()
    #
    #     self.__setup_permissions()
        self.duration_sbox.setMaximum(5)
        self.tab_index = 0
        validator = QtGui.QDoubleValidator()
        self.find_x_coordinate_edit.setValidator(validator)
        self.find_y_coordinate_edit.setValidator(validator)
    #     # self.__doc_tree_view()
        self.find_tab.currentChanged.connect(self.onChangetab)

        self.decision_date.dateChanged.connect(self.on_decision_date_DateChanged)
        self.contract_date.dateChanged.connect(self.on_contract_date_DateChanged)
        self.end_date.dateChanged.connect(self.on_end_date_DateChanged)

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


    # def __is_aimag_tool(self):
    #
    #     database = QSettings().value(SettingsConstants.DATABASE_NAME)
    #     if database:
    #         au1 = database.split('_')[1][:2]
    #         if au1:
    #             if au1 != '11':
    #                 self.parcel_tab_widget.removeTab(
    #                     self.parcel_tab_widget.indexOf(self.legal_representative_tab))
    #
    #
    def __setup_permissions(self):
    #
         user_name = QSettings().value(SettingsConstants.USER)
         user_rights = DatabaseUtils.userright_by_name(user_name)
         officer = self.session.query(SetRole) \
             .filter(SetRole.user_name == QSettings().value(SettingsConstants.USER)) \
             .filter(SetRole.is_active == True).one()

         self.finish_button.setVisible(True)
         if officer.position == 100:
    #         self.finish_button.setVisible(True)
    #     if officer.position == 12:
    #         self.finish_button.setVisible(True)
    #     if officer.position == 13:
    #         self.finish_button.setVisible(True)
    #     # else:
    #     #     print 'sdak'
    #     #     self.finish_button.setVisible(False)
    #
          self.__disable_all()
    #     #
          if UserRight.cadastre_update in user_rights:
    #
              self.finish_button.setEnabled(False)
    #
    def __disable_all(self):

        self.finish_button.setEnabled(False)


    def __setup_validators(self):

        self.capital_asci_letter_validator = QRegExpValidator(QRegExp("[A-Z]"), None)
        self.lower_case_asci_letter_validator = QRegExpValidator(QRegExp("[a-z]"), None)

        self.email_validator = QRegExpValidator(QRegExp("[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,4}"), None)

        self.www_validator = QRegExpValidator(QRegExp("www\\.[a-z0-9._%+-]+\\.[a-z]{2,4}"), None)

        self.numbers_validator = QRegExpValidator(QRegExp("[1-9][0-9]+( *,*[1-9][0-9]+)*"), None)
        self.int_validator = QRegExpValidator(QRegExp("[0-9]+"), None)
        self.zoriulalt_edit.setValidator(self.numbers_validator)

        self.contract_cert_edit.setValidator(self.numbers_validator)

    def __setup_cbox(self):

        # try:
        application_types = self.session.query(ClApplicationType).filter(ClApplicationType.code == 22). \
            order_by(ClApplicationType.code).all()
        statuses = self.session.query(ClApplicationStatus).order_by(ClApplicationStatus.code).all()
        landuse_types = self.session.query(ClLanduseType).all()
        person_types = self.session.query(ClPersonType).all()
        # decision_levels = self.session.query(ClDecisionLevel).filter(or_(ClDecisionLevel.code == 10, ClDecisionLevel.code == 20)).all()
        decision_levels = self.session.query(ClDecisionLevel).filter(ClDecisionLevel.code == 80).all()
        contract_statuses = self.session.query(ClContractStatus).all()
        right_types = self.session.query(ClRightType).filter(ClRightType.code == 1).all()
        edit_statuses = self.session.query(ClUbEditStatus).all()

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

        for item in application_types:
            self.application_type_cbox.addItem(item.description, item.code)

    def __setup_table_widget(self):

        self.right_holder_twidget.setAlternatingRowColors(True)
        self.right_holder_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.right_holder_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.right_holder_twidget.setSelectionMode(QTableWidget.SingleSelection)

    def __update_ui(self):

        self.setWindowTitle(self.tr('Old Parcel ID: <{0}>. Select the decision.'.format(self.__old_parcel_no)))
        self.right_holder_twidget.clearContents()
        self.right_holder_twidget.setRowCount(0)

        subjects = self.session.query(MpaGisEditSubject).filter(MpaGisEditSubject.gid == self.__old_parcel_no).all()

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

        right_type = self.session.query(ClRightType).filter(ClRightType.code == 1).one()
        if subject:
            self.right_holder_twidget.insertRow(count)

            item = QTableWidgetItem(right_type.description)
            item.setData(Qt.UserRole, right_type.code)
            self.right_holder_twidget.setItem(count, self.RIGTHTYPE, item)

            item = QTableWidgetItem(unicode(subject.register))
            item.setData(Qt.UserRole, subject.register)
            item.setData(Qt.UserRole + 1, subject.gid)
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

            item = QTableWidgetItem(str(subject.gid))
            item.setData(Qt.UserRole, (subject.gid))
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

            subjects = self.session.query(MpaGisEditSubject)

            if self.find_parcel_id_edit.text():
                filter_is_set = True
                value = "%" + self.find_parcel_id_edit.text() + "%"
                subjects = subjects.filter(MpaGisEditSubject.oldpid.like(value))

            if self.find_person_id_edit.text():
                filter_is_set = True
                value = "%" + self.find_person_id_edit.text() + "%"
                subjects = subjects.filter(MpaGisEditSubject.register.like(value))

            if self.find_firstname_edit.text():
                filter_is_set = True
                value = "%"+self.find_firstname_edit.text()+"%"
                subjects = subjects.filter(MpaGisEditSubject.ovog.like(value))

            if self.find_lastname_edit.text():
                filter_is_set = True
                value = "%"+self.find_lastname_edit.text()+"%"
                subjects = subjects.filter(MpaGisEditSubject.ner.like(value))

            if filter_is_set is False:
                PluginUtils.show_message(self, self.tr("None"), self.tr("Please specify a search filter."))
                return

            for subject in subjects.all():
                self.__add_subject(subject)

        if self.tab_index == 2:
            filter_is_set = False
            self.right_holder_twidget.setRowCount(2)

            subjects = self.session.query(MpaGisEditSubject)

            if self.find_street_name_edit.text():
                filter_is_set = True
                value = "%" + self.find_street_name_edit.text() + "%"
                subjects = subjects.filter(MpaGisEditSubject.gudamj.like(value))

            if self.find_khashaa_number_edit.text():
                filter_is_set = True
                value = "%" + self.find_khashaa_number_edit.text() + "%"
                subjects = subjects.filter(MpaGisEditSubject.hashaa.like(value))

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

        expression = " gid = \'" + parcel_id + "\'"
        request = QgsFeatureRequest()
        request.setFilterExpression(expression)
        feature_ids = []
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
        layer = LayerUtils.layer_by_data_source("data_ub", 'ca_mpa_parcel_edit_view')

        selected_row = self.right_holder_twidget.currentRow()
        old_parcel_id = self.right_holder_twidget.item(selected_row, 4).text()
        gid = self.right_holder_twidget.item(selected_row, 5).data(Qt.UserRole)

        self.__select_feature(str(gid), layer)

    @pyqtSlot(QTableWidgetItem)
    def on_right_holder_twidget_itemClicked(self, item):

        self.person_street_name_edit.clear()
        self.person_khashaa_edit.clear()
        self.building_edit.clear()
        self.apartment_edit.clear()

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
        # try:
        subject_persons = self.session.query(MpaGisEditSubject).filter(MpaGisEditSubject.gid == object_id).all()
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
        parcel_subjects = self.session.query(MpaGisEditSubject).filter(MpaGisEditSubject.gid == object_id).all()
        for parcel_subject in parcel_subjects:
            self.edit_status_cbox.setCurrentIndex(self.edit_status_cbox.findData(parcel_subject.edit_status))
            self.old_parcel_id_edit.setText(str(parcel_subject.gid))
            if parcel_subject.gudamj:
                street = parcel_subject.gudamj
                neighbourhood = parcel_subject.gudamj
            if parcel_subject.hashaa:
                khashaa = parcel_subject.hashaa
            if parcel_subject.zoriulalt:
                zoriulalt = parcel_subject.zoriulalt
            landuse_type = parcel_subject.landuse_code

        self.zoriulalt_edit.setText(unicode(zoriulalt))
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

        for subject in parcel_subjects:
            if subject.zovshshiid:
                decision_no = subject.zovshshiid
            if subject.zovshdate:
                decision_date = subject.zovshdate
            if subject.gaid:
                right_type_object = self.session.query(ClRightType).filter(ClRightType.code == 1).one()
                right_type = right_type_object.code
            decision_level = subject.zovshbaig
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
        self.contract_no_edit.setText(contract_no)
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

        # person address
        self.__load_pesron_address(person_id)

        # except SQLAlchemyError, e:
        #     self.rollback()

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

    # @pyqtSlot(int)
    # def on_is_ftp_edit_chbox_stateChanged(self, state):
    #
    #     if state == Qt.Checked:
    #         self.ftp_host_edit.setEnabled(True)
    #     else:
    #         self.ftp_host_edit.setEnabled(False)
    #
    # @pyqtSlot(int)
    # def on_zoriulalt_chbox_stateChanged(self, state):
    #
    #     if state == Qt.Checked:
    #         self.zoriulalt_edit.setEnabled(True)
    #     else:
    #         self.zoriulalt_edit.setEnabled(False)
    #
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

    @pyqtSlot(int)
    def on_contract_no_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.contract_no_edit.setEnabled(True)
        else:
            self.contract_no_edit.setEnabled(False)

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
        self.contract_no_edit.clear()
        self.contract_cert_edit.clear()
        self.contract_full_edit.clear()
        self.contract_no_chbox.setChecked(False)
        self.contract_certificate_chbox.setChecked(False)
        self.contract_date_chbox.setChecked(False)
        self.end_date_chbox.setChecked(False)
        self.duration_chbox.setChecked(False)
        self.contract_status_chbox.setChecked(False)

    def __save_subject(self, objectid):


        subject = self.session.query(MpaGisEditSubject).filter(MpaGisEditSubject.gid == objectid).one()

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

        # Decision

        right_type = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())
        app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())
        decision_level = self.decision_level_cbox.itemData(self.decision_level_cbox.currentIndex())

        subject.gaid = right_type
        subject.zovshbaig = decision_level
        subject.zovshshiid = self.decision_no_edit.text()
        decision_date = PluginUtils.convert_qt_date_to_python(self.decision_date.date())
        subject.zovshdate = decision_date
        subject.app_type = app_type

        subject.gerid = self.contract_no_edit.text()
        subject.gerchid = self.contract_cert_edit.text()
        contract_date = PluginUtils.convert_qt_date_to_python(self.contract_date.date())
        subject.gerdate = contract_date
        end_date = PluginUtils.convert_qt_date_to_python(self.end_date.date())
        subject.duusdate = end_date

        edit_status = self.edit_status_cbox.itemData(self.edit_status_cbox.currentIndex())

        if subject.edit_status != 10:
            subject.status_date = PluginUtils.convert_qt_date_to_python(QDate.currentDate())
            subject.status_user = DatabaseUtils.current_user().user_name

        if self.edit_status_cbox.currentIndex() == -1:
            subject.edit_status = 30
        else:
            subject.edit_status = edit_status
    #
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
            self.__save_subject(object_id)
        self.session.commit()
        PluginUtils.show_message(self, self.tr("LM2", "Success"), self.tr("Success saved"))
    #
    # @pyqtSlot(str)
    # def on_zoriulalt_edit_textChanged(self, text):
    #
    #     landuse_type = 2205
    #
    #     type = text
    #     if self.__is_number(type):
    #         if int(type) in self.zoriulalt:
    #             if int(type) == 1:
    #                 landuse_type = 2205
    #             elif int(type) == 2:
    #                 landuse_type = 2101
    #             elif int(type) == 3:
    #                 landuse_type = 2104
    #             elif int(type) == 4:
    #                 landuse_type = 2105
    #             elif int(type) == 5:
    #                 landuse_type = 2107
    #             elif int(type) == 6:
    #                 landuse_type = 2113
    #             elif int(type) == 7:
    #                 landuse_type = 1604
    #             elif int(type) == 8:
    #                 landuse_type = 2119
    #             elif int(type) == 9:
    #                 landuse_type = 3401
    #             elif int(type) == 10:
    #                 landuse_type = 3103
    #             elif int(type) == 11:
    #                 landuse_type = 3303
    #             elif int(type) == 12:
    #                 landuse_type = 2111
    #             elif int(type) == 13:
    #                 landuse_type = 2108
    #             elif int(type) == 14:
    #                 landuse_type = 2109
    #             elif int(type) == 15:
    #                 landuse_type = 2116
    #             elif int(type) == 16:
    #                 landuse_type = 2117
    #             elif int(type) == 17:
    #                 landuse_type = 2302
    #             elif int(type) == 18:
    #                 landuse_type = 2601
    #             elif int(type) == 19:
    #                 landuse_type = 1401
    #             elif int(type) == 20:
    #                 landuse_type = 1607
    #             elif int(type) == 21:
    #                 landuse_type = 1305
    #             elif int(type) == 22:
    #                 landuse_type = 1606
    #             elif int(type) == 23:
    #                 landuse_type = 2101
    #             elif int(type) == 24:
    #                 landuse_type = 2111
    #
    #     self.parcel_landuse_cbox.setCurrentIndex(self.parcel_landuse_cbox.findData(landuse_type))
    #
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
                    .order_by(func.substr(CtApplication.app_no, 10, 14).desc()).count()

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

        if count > 0:
            try:
                max_number_app = self.session.query(CtApplication)\
                    .filter(CtApplication.app_no.like("%-%"))\
                    .filter(CtApplication.app_no.like(app_type_filter)) \
                    .filter(CtApplication.app_no.like(soum_filter)) \
                    .filter(CtApplication.app_no.like(year_filter)) \
                    .order_by(func.substr(CtApplication.app_no, 10, 14).desc()).first()
            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return

            app_no_numbers = max_number_app.app_no.split("-")

            app_no_part_2 = str(int(app_no_numbers[2]) + 1).zfill(5)

        else:
            app_no_part_2 = "00001"

        app_no_part_3 = (qt_date.toString("yy"))
        app_no = app_no_part_0 + '-' + app_no_part_1 + '-' + app_no_part_2 + '-' + app_no_part_3
        return app_no


    def __validaty_of_ubparcel(self):

        valid = True
        old_parcel_id = self.old_parcel_id_edit.text()
        error_message = self.tr("The parcel info can't be saved. The following errors have been found: ")
        ub_parcel = self.session.query(MpaGisEditSubject).filter(MpaGisEditSubject.gid == old_parcel_id).one()
        parcel_within_count = self.session.query(CaParcel).filter(
            ub_parcel.geometry.ST_Within(CaParcel.geometry)).count()

        wkb_elem = self.session.query(MpaGisEditSubject.geometry).filter(
            MpaGisEditSubject.gid == old_parcel_id).scalar()
        shply_geom = to_shape(wkb_elem)
        wkt_geom = shply_geom.to_wkt()
        params = urllib.urlencode({'geom': wkt_geom})
        f = urllib.urlopen("http://192.168.15.222/api/geo/parcel/check/by/geom/wkt", params)
        data = json.load(f)
        status = data['status']
        result = data['result']
        if not status:
            valid = False
            parcel_error = u'Өгөгдөл буруу байна!!!'
            error_message = error_message + "\n \n" + parcel_error
        else:
            if result:
                valid = False
                parcel_error = u'Газар олгох боломжгүй байршил!!!'
                error_message = error_message + "\n \n" + parcel_error

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
                street_error = self.tr("Person Middle name error!.")
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
                street_error = self.tr("Person first name error!.")
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

    # @pyqtSlot(int)
    # def on_rigth_type_cbox_currentIndexChanged(self, index):
    #
    #     self.application_type_cbox.setCurrentIndex(self.application_type_cbox.findData(22))
        # self.application_type_cbox.clear()
        # rigth_code = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())
        #
        # rigth_apps = self.session.query(SetRightTypeApplicationType).filter(
        #     SetRightTypeApplicationType.right_type == rigth_code). \
        #     order_by(SetRightTypeApplicationType.application_type).all()
        #
        # for item in rigth_apps:
        #     app_type = self.session.query(ClApplicationType).filter(
        #         ClApplicationType.code == item.application_type).one()
        #     self.application_type_cbox.addItem(app_type.description, app_type.code)

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
            subject = self.session.query(MpaGisEditSubject).filter(MpaGisEditSubject.gid == objectid).one()
            subject.is_finish = True
            subject.finish_user = DatabaseUtils.current_user().user_name
            subject.finish_date = PluginUtils.convert_qt_date_to_python(QDate.currentDate())
            self.commit()
            # except SQLAlchemyError, e:
            #     self.rollback()
            #     PluginUtils.show_error(self, self.tr("File Error"),
            #                                self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            #     return
            # return

    def __generate_contract_number(self):

        soum = DatabaseUtils.current_working_soum_schema()
        qt_date = self.contract_date.date()
        try:
            contract_number_filter = "%-{0}/%".format(str(qt_date.toString("yyyy")))

            count = self.session.query(CtContract) \
                .filter(CtContract.contract_no.like("%-%")) \
                .filter(CtContract.contract_no.like(contract_number_filter)) \
                .filter(CtContract.au2 == soum) \
                .order_by(func.substr(CtContract.contract_no, 10, 16).desc()).count()
            if count == 0:
                cu_max_number = "00001"
            else:
                cu_max_number = self.session.query(CtContract.contract_no) \
                    .filter(CtContract.contract_no.like("%-%")) \
                    .filter(CtContract.contract_no.like(contract_number_filter)) \
                    .filter(CtContract.au2 == soum) \
                    .order_by(func.substr(CtContract.contract_no, 10, 16).desc()).first()
                cu_max_number = cu_max_number[0]

                minus_split_number = cu_max_number.split("-")
                slash_split_number = minus_split_number[1].split("/")
                cu_max_number = int(slash_split_number[1]) + 1

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

    def __save_decision(self):

        # user = DatabaseUtils.current_user()
        # current_employee = self.session.query(SetRole) \
        #     .filter(SetRole.user_name == user.user_name) \
        #     .filter(SetRole.is_active == True).one()
        decision_level = self.decision_level_cbox.itemData(self.decision_level_cbox.currentIndex())
        decision_no = self.decision_full_edit.text()

        decision_count = self.session.query(CtDecision).filter(CtDecision.decision_no == decision_no).\
            filter(CtDecision.decision_level == decision_level).count()
        if decision_count == 1:
            self.decision = self.session.query(CtDecision).filter(CtDecision.decision_no == decision_no).\
                filter(CtDecision.decision_level == decision_level).one()
            # app_dec_count = self.session.query(CtDecisionApplication).filter(
            #     CtDecisionApplication.decision == self.decision.decision_no).count()
            # if app_dec_count > 0:
            #     app_dec = self.session.query(CtDecisionApplication).filter(CtDecisionApplication.decision == self.decision.decision_no).first()
            #     application = app_dec.application_ref
            #     application_type = application.app_type
            #     app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())
            #     if app_type != application_type:
            #         PluginUtils.show_message(self, self.tr("LM2", "Application Type"),
            #                                  self.tr("Can't match application type!!!"))
            #         self.isSave = False
            #         return
        else:
            self.decision = CtDecision()

            self.decision.decision_date = self.decision_date.date().toString(Constants.DATABASE_DATE_FORMAT)
            self.decision.decision_no = decision_no
            self.decision.decision_level = decision_level
            self.decision.imported_by = DatabaseUtils.current_sd_user().user_id
            self.decision.au2 = DatabaseUtils.working_l2_code()
            self.session.add(self.decision)

        decision_app = CtDecisionApplication()
        decision_app.decision = self.decision.decision_id
        decision_app.decision_result = 10
        decision_app.application = self.application.app_id
        self.decision.results.append(decision_app)

    def __save_status(self):

        status_date = self.decision_date.date().toString(Constants.DATABASE_DATE_FORMAT)

        statuses = self.session.query(ClApplicationStatus).all()

        for status in statuses:
            if status.code != 8 and status.code != 1 and status.code < 10:
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

    def __save_applicant(self):

        person_id = self.personal_id_edit.text()
        person = self.session.query(BsPerson).filter(BsPerson.person_register == person_id).one()
        role_ref = self.session.query(ClPersonRole).filter_by(
            code=Constants.APPLICANT_ROLE_CODE).one()

        app_person_role = CtApplicationPersonRole()
        app_person_role.application = self.application.app_id
        app_person_role.share = Decimal(1.0)
        app_person_role.role = Constants.APPLICANT_ROLE_CODE
        app_person_role.role_ref = role_ref
        app_person_role.person = person.person_id
        app_person_role.person_ref = person
        app_person_role.main_applicant = True

        self.application.stakeholders.append(app_person_role)

        self.__multi_applicant_save(person_id, self.application)

    def __multi_applicant_save(self, person_id, application):

        register = person_id

        sql = "select register, ovog,ner ,hen,zahid " \
              "from ub_lpis_co info " \
              "where oregister = :register "

        result = self.session.execute(sql, {'register': register})
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

    def __save_person(self):

        person_id = self.personal_id_edit.text()
        person_id = person_id.upper()
        person_count = self.session.query(BsPerson).filter(BsPerson.person_register == person_id).count()
        if person_count > 0:
            bs_person = self.session.query(BsPerson).filter(BsPerson.person_register == person_id).one()
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
            # self.session.flush()

            # self.__multi_owner_save(person_id)

    def __save_parcel(self):

        parcel_id = self.parcel_id_edit.text()

        old_parcel_id = self.old_parcel_id_edit.text()
        ub_parcel = self.session.query(MpaGisEditSubject).filter(MpaGisEditSubject.gid == old_parcel_id).one()
        landuse = self.parcel_landuse_cbox.itemData(self.parcel_landuse_cbox.currentIndex())

        parcel_count = self.session.query(CaParcel).filter(CaParcel.parcel_id == parcel_id).count()
        if parcel_count == 1:
            parcel = self.session.query(CaParcel).filter(CaParcel.parcel_id == parcel_id).one()
            parcel.parcel_id = None
        else:
            parcel = CaParcel()
            if len(parcel_id) == 10:
                parcel.parcel_id = parcel_id

        parcel.old_parcel_id = old_parcel_id
        parcel.geo_id = old_parcel_id
        parcel.landuse = landuse
        parcel.address_khashaa = self.khashaa_edit.text()
        parcel.address_streetname = self.streetname_edit.text()
        parcel.address_neighbourhood = self.neighbourhood_edit.text()
        valid_from = self.decision_date.date().toString(Constants.DATABASE_DATE_FORMAT)
        parcel.valid_from = valid_from
        parcel.geometry = ub_parcel.geometry
        self.session.add(parcel)
        self.session.flush()

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


        qt_date = self.decision_date.date()
        year = str(qt_date.toString("yy"))
        obj_type = 'application\Application'
        PluginUtils.generate_auto_app_no(str(year), str(app_type).zfill(2), au_level2, obj_type, self.session)

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

        self.application.parcel = self.parcel_id
        self.session.add(self.application)

        # except SQLAlchemyError, e:
        #     self.rollback_to_savepoint()
        #     raise LM2Exception(self.tr("File Error"),
        #                        self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))


    @pyqtSlot()
    def on_layer_view_button_clicked(self):

        root = QgsProject.instance().layerTreeRoot()

        mygroup = root.findGroup(u"Тусгай хэрэгцээний газар")
        if mygroup is None:
            mygroup = root.insertGroup(8, u"Тусгай хэрэгцээний газар")

        is_pug_parcel = False

        vlayer_parcel = LayerUtils.load_ub_data_layer_by_name("ca_mpa_parcel_edit_view", "gid")

        layers = self.plugin.iface.legendInterface().layers()

        for layer in layers:
            if layer.name() == "MpaParcelEdit":
                is_pug_parcel = True
        if not is_pug_parcel:

            mygroup.addLayer(vlayer_parcel)
        # QgsMapLayerRegistry.instance().addMapLayer(vlayer)
        vlayer_parcel.setLayerName(QApplication.translate("Plugin", "MpaParcelEdit"))
        vlayer_parcel.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "template\style/ca_mpa_edit_parcel.qml")

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

    # def newOnkeyPressEvent(self, e):
    #     if self.is_find_ubgis:
    #         if e.key() == QtCore.Qt.Key_Enter:
    #             self.find_button.click()
    #             print "User has pushed escape"


    # def keyPressEvent(self, eventQKeyEvent):
    #     key = eventQKeyEvent.key()
    #     if key == QtCore.Qt.Key_F1:
    #         print 'Help'
    #     elif key == QtCore.Qt.Key_F5:
    #         print 'Reload'
    #     elif key == QtCore.Qt.Key_Left:
    #         print 'Left'
    #     elif key == QtCore.Qt.Key_Up:
    #         print 'Up'
    #     elif key == QtCore.Qt.Key_Right:
    #         print 'Right'
    #     elif key == QtCore.Qt.Key_Down:
    #         print 'Down'
    #
    # @pyqtSlot()
    # def on_current_dialog_closed(self):
    #
    #     DialogInspector().set_dialog_visible(False)