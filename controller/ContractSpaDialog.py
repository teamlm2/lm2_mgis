# coding=utf8
__author__ = 'B.Ankhbold'

import os
import re
import math
import time
import locale
import win32api
import win32net
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from geoalchemy2.elements import WKTElement
from qgis.core import *
from sqlalchemy import func, or_, extract
from PyQt4.QtXml import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.core import *
from qgis.gui import *
from inspect import currentframe
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from datetime import date, datetime, timedelta
from ..model import Constants
from ..model.BsPerson import *
from ..model.ClBank import *
from ..model.AuLevel1 import *
from ..model.AuLevel2 import *
from ..model.AuLevel3 import *
from ..model.CaPastureParcel import *
from ..model.ClPastureType import *
from ..model.CtApplicationParcelPasture import *
from ..model import SettingsConstants
from ..model.EnumerationsPasture import ApplicationType
from ..model import ConstantsPasture
from ..model.DatabaseHelper import *
from ..model.CtApplicationPUGParcel import *
from ..model.CtApplicationPUG import *
from ..model.CtGroupMember import *
from ..model.CtPersonGroup import *
from ..view.Ui_ContractSpaDialog import Ui_ContractSpaDialog
from ..model.CtContractDocument import *
from ..model.ClPositionType import *
from ..model.ClPastureValues import *
from ..model.ClContractCondition import *
from ..model.Enumerations import UserRight
from ..model.CtDecisionApplication import *
from ..model.CtDecision import *
from ..model.LM2Exception import LM2Exception
from ..model.CtContractApplicationRole import *
from ..model.ClContractCancellationReason import *
from ..model.ClPastureDocument import ClPastureDocument
from ..model.SetPastureDocument import SetPastureDocument
from ..model.PsPointPastureValue import *
from ..model.SetApplicationTypeDocumentRole import SetApplicationTypeDocumentRole
from ..model.CtApplicationStatus import *
from ..model.SetCertificate import *
from ..model.CaPastureMonitoring import *
from ..model.CaPastureParcelTbl import *
from ..model.CtApplicationParcel import *
from ..model.ClParcelType import *
from ..model.SetApplicationTypePersonRole import *
from ..model.CtApplicationParcel import *
from ..model.CaStateParcelTbl import *
from ..model.SdDepartmentAccount import *
from ..utils.FileUtils import FileUtils
from ..utils.PluginUtils import PluginUtils
from ..utils.LayerUtils import LayerUtils
from ..utils.SessionHandler import SessionHandler
from ..utils.DatabaseUtils import DatabaseUtils
from ..utils.PasturePath import *
from .qt_classes.ComboBoxDelegate import *
from .qt_classes.DropLabel import DropLabel
from .qt_classes.IntegerSpinBoxDelegate import *
from .qt_classes.DoubleSpinBoxDelegate import *
from .qt_classes.ObjectAppDocumentDelegate import ObjectAppDocumentDelegate
from .qt_classes.PastureContractDocumentDelegate import PastureContractDocumentDelegate
from docxtpl import DocxTemplate, RichText

CONTRACTOR_NAME = 0
CONTRACTOR_ID = 1
CONTRACTOR_SHARE = 2
CONTRACTOR_AREA = 3
CONTRACTOR_FEE_CALCULATED = 4
CONTRACTOR_FEE_CONTRACT = 5
CONTRACTOR_GRACE_PERIOD = 6
CONTRACTOR_PAYMENT_FREQUENCY = 7

APP_DOC_PROVIDED_COLUMN = 0
APP_DOC_TYPE_COLUMN = 1
APP_DOC_NAME_COLUMN = 2
APP_DOC_VIEW_COLUMN = 3

DOC_PROVIDED_COLUMN = 0
DOC_TYPE_COLUMN = 1
DOC_NAME_COLUMN = 2
DOC_OPEN_COLUMN = 3
DOC_REMOVE_COLUMN = 4
DOC_VIEW_COLUMN = 5


class ContractSpaDialog(QDialog, Ui_ContractSpaDialog, DatabaseHelper):

    def __init__(self, plugin, contract, navigator, attribute_update, parent=None):

        super(ContractSpaDialog, self).__init__(parent)
        DatabaseHelper.__init__(self)
        self.navigator = navigator
        self.plugin = plugin

        self.attribute_update = attribute_update
        self.session = SessionHandler().session_instance()
        self.__geometry = None
        self.contract = contract
        self.item_model = None
        self.updating = None
        self.app_id = None
        self.__coord_transform = None
        self.setupUi(self)

        self.contract_date.setDate(QDate().currentDate())
        self.cancelation_date.setDate(QDate().currentDate())

        self.setWindowTitle(self.tr("Create / Edit Contract"))
        self.drop_label = DropLabel("application", self.application_groupbox)
        self.drop_label.itemDropped.connect(self.on_drop_label_itemDropped)
        self.close_button.clicked.connect(self.reject)
        self.__set_up_assigned_parcel_twidget()
        self.__setup_combo_boxes()
        self.status_label.clear()
        self.is_certificate = False

        self.x_point_utm = None
        self.y_point_utm = None

        if self.attribute_update:
            self.__setup_mapping()
        else:
            try:
                self.__generate_contract_number()
            except LM2Exception, e:
                PluginUtils.show_error(self, e.title(), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                self.reject()
        self.__setup_doc_twidgets()
        self.__setup_permissions()

    def __set_up_twidget(self, table_widget):

        table_widget.setAlternatingRowColors(True)
        table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        table_widget.setSelectionMode(QTableWidget.SingleSelection)

        # table_widget.setColumnWidth(0, 300)
        header = table_widget.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)

    def __set_up_assigned_parcel_twidget(self):

        self.__set_up_twidget(self.assigned_parcel_twidget)

    def __generate_contract_number(self):

        try:
            contract_number_filter = "%-{0}/%".format(str(QDate().currentDate().toString("yyyy")))

            count = self.session.query(CtContract).filter(CtContract.contract_no != str(self.contract.contract_no)) \
                .filter(CtContract.contract_no.like("%-%")) \
                .filter(CtContract.contract_no.like(contract_number_filter)) \
                .order_by(func.substr(CtContract.contract_no, 10, 16).desc()).count()
            if count == 0:
                cu_max_number = "00001"
            else:
                cu_max_number = self.session.query(CtContract.contract_no) \
                    .filter(CtContract.contract_no != str(self.contract.contract_no)) \
                    .filter(CtContract.contract_no.like("%-%")) \
                    .filter(CtContract.contract_no.like(contract_number_filter)) \
                    .order_by(func.substr(CtContract.contract_no, 10, 16).desc()).first()
                cu_max_number = cu_max_number[0]

                minus_split_number = cu_max_number.split("-")
                slash_split_number = minus_split_number[1].split("/")
                cu_max_number = int(slash_split_number[1]) + 1

            soum = DatabaseUtils.current_working_soum_schema()
            year = QDate().currentDate().toString("yyyy")
            number = soum + "-" + year + "/" + str(cu_max_number).zfill(5)

            self.contract_num_edit.setText(number)
            self.contract.contract_no = number

            app_type = None
            obj_type = 'contract\Contract'
            PluginUtils.generate_auto_app_no(str(year), app_type, soum, obj_type, self.session)

        except SQLAlchemyError, e:
            raise LM2Exception(self.tr("Database Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

    def __certificate_type(self):

        try:
            # Find the first applicant's person_type and select the certificate number accordingly
            app_no = self.application_this_contract_based_edit.text()
            if len(app_no) == 0:
                return -1
            app_no_count = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).count()
            if app_no_count == 0:
                return -1

            app = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).one()
            contractor = app.stakeholders.filter(CtApplicationPersonRole.role == Constants.APPLICANT_ROLE_CODE).first()

            person = contractor.person_ref
            person_type = person.type
            if person_type == 10 or person_type == 20:
                certificate_type = 10
            elif person_type == 30:
                certificate_type = 20
            elif person_type == 5 or person_type == 6:
                certificate_type = 30
            else:
                certificate_type = 40

            return certificate_type

        except SQLAlchemyError, e:
            raise LM2Exception(self.tr("Database Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

    def __calculate_certificate_no(self):

        # try:
        certificate_type = self.__certificate_type()

        certificate_settings = self.__certificate_settings(certificate_type)

        max_certificate_no = certificate_settings[Constants.CERTIFICATE_CURRENT_NUMBER] + 1

        # except SQLAlchemyError, e:
        #     raise LM2Exception(self.tr("Database Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

        if certificate_settings[Constants.CERTIFICATE_FIRST_NUMBER] <= max_certificate_no \
                <= certificate_settings[Constants.CERTIFICATE_LAST_NUMBER]:

            return max_certificate_no

        else:
            self.error_label.setText(self.tr("The certificate number is out of range. Change the Admin Settings."))
            self.error_label.setStyleSheet(Constants.ERROR_TWIDGET_STYLESHEET)
            self.apply_button.setEnabled(False)
            return -1

    def __certificate_settings(self, certificate_type):

        first_no, last_no, current_no = self.session.query(SetCertificate.range_first_no, SetCertificate.range_last_no, SetCertificate.current_no)\
            .filter(SetCertificate.certificate_type == certificate_type).order_by(SetCertificate.begin_date.desc()).limit(1).one()

        return {Constants.CERTIFICATE_FIRST_NUMBER: first_no, Constants.CERTIFICATE_LAST_NUMBER: last_no, Constants.CERTIFICATE_CURRENT_NUMBER: current_no}

    def __setup_permissions(self):

        user_name = QSettings().value(SettingsConstants.USER)
        user_rights = DatabaseUtils.userright_by_name(user_name)

        if UserRight.contracting_update in user_rights:
            self.apply_button.setEnabled(True)
            self.unassign_button.setEnabled(True)
            self.search_button.setEnabled(True)
            self.accept_button.setEnabled(True)
            self.status_groupbox.setEnabled(True)
            self.contract_cancellation_groupbox.setEnabled(True)
            self.documents_groupbox.setEnabled(True)

        else:
            self.apply_button.setEnabled(False)
            self.unassign_button.setEnabled(False)
            self.search_button.setEnabled(False)
            self.accept_button.setEnabled(False)
            self.status_groupbox.setEnabled(False)
            self.contract_cancellation_groupbox.setEnabled(False)
            self.documents_groupbox.setEnabled(False)

    def __setup_mapping(self):

        # try:
        self.contract_num_edit.setText(self.contract.contract_no)
        qt_date = PluginUtils.convert_python_date_to_qt(self.contract.contract_date)
        if qt_date is not None:
            self.contract_date.setDate(qt_date)

        contract_begin = PluginUtils.convert_python_date_to_qt(self.contract.contract_begin)
        contract_end = PluginUtils.convert_python_date_to_qt(self.contract.contract_end)

        if contract_begin is not None:
            self.contract_begin_date.setDate(contract_begin)

        if contract_end is not None:
            self.contract_end_date.setDate(contract_end)
            duration = contract_end.year() - contract_begin.year()
            self.duration_sbox.setValue(duration)

        self.__load_application_information()

        self.__setup_status()

        if self.contract.cancellation_date:
            qt_date = PluginUtils.convert_python_date_to_qt(self.contract.cancellation_date)

            self.cancelation_date.setDate(qt_date)
            self.cancellation_date_check_box.setCheckState(Qt.Checked)

            if self.contract.cancellation_reason is not None:
                self.other_reason_rbutton.setChecked(True)
                self.other_reason_cbox.setCurrentIndex(
                    self.other_reason_cbox.findData(self.contract.cancellation_reason))
            else:
                self.application_based_rbutton.setChecked(True)

                cancellation_application_c = self.contract.application_roles\
                    .filter_by(role=Constants.APP_ROLE_CANCEL).count()
                if cancellation_application_c != 0:
                    cancellation_application = self.contract.application_roles\
                        .filter_by(role=Constants.APP_ROLE_CANCEL).one()

                    if cancellation_application is None:
                        PluginUtils.show_error(self, self.tr("Error loading Contract"),
                                               self.tr("Could not load contract. Cancellation application not found"))
                        self.reject()

                    self.app_number_cbox.setCurrentIndex(
                        self.app_number_cbox.findText(cancellation_application.application))
                    self.type_edit.setText(cancellation_application.application_ref.app_type_ref.description)

        application_role = self.contract.application_roles.filter_by(role=Constants.APPLICATION_ROLE_CREATES).one()
        application = application_role.application_ref

        if application_role is None or application is None:
            PluginUtils.show_error(self, self.tr("Error loading Contract"),
                                   self.tr("This contract has no valid application assigned."))
            self.reject()
            return
        self.app_id = application.app_id
        self.application_this_contract_based_edit.setText(application.app_no)
        self.application_type_edit.setText(application.app_type_ref.description)

        # except SQLAlchemyError, e:
        #     PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

    def __setup_status(self):

        if self.contract.status == Constants.CONTRACT_STATUS_DRAFT:
            self.draft_rbutton.setChecked(True)
        elif self.contract.status == Constants.CONTRACT_STATUS_ACTIVE:
            self.active_rbutton.setChecked(True)
        elif self.contract.status == Constants.CONTRACT_STATUS_EXPIRED:
            self.expired_rbutton.setChecked(True)
        elif self.contract.status == Constants.CONTRACT_STATUS_CANCELLED:
            self.cancelled_rbutton.setChecked(True)

    def __setup_combo_boxes(self):

        # self.document_path_edit.setText(PasturePath.contrac_file_path())
        # try:
        restrictions = DatabaseUtils.working_l2_code()
        user = DatabaseUtils.current_user()
        currect_user = user.position
        self.print_officer_cbox.setDisabled(False)
        print_officers = self.session.query(SetRole).filter(
            or_(SetRole.position == 5, SetRole.position == 6, SetRole.position == 7, SetRole.position == 8,
                SetRole.position == currect_user)).all()
        # filter(or_(SetRole.position == 9, SetRole.position == currect_user)). \
        # filter(SetRole.is_active == True). \
        # filter(SetRole.user_name.startswith(user_start)).all()
        soum_code = DatabaseUtils.working_l2_code()
        for officer in print_officers:
            l2_code_list = officer.restriction_au_level2.split(',')
            if soum_code in l2_code_list:
                officer_name = officer.surname[:1] + '.' + officer.first_name
                self.print_officer_cbox.addItem(officer_name, officer.user_name_real)
            else:
                self.print_officer_cbox.setDisabled(True)
        # app_contract_count = self.session.query(CtContractApplicationRole).filter(CtContractApplicationRole.contract == self.contract.contract_id).count()

        # if app_contract_count == 1:
        #     app_contract = self.session.query(CtContractApplicationRole).filter_by(contract=self.contract.contract_id).one()
        #     application = self.session.query(CtApplication).filter_by(app_id=app_contract.application).one()
            # apps = self.session.query(CtApplication.app_no).order_by(CtApplication.app_no).all()

            # for app in apps:
            #     self.app_number_cbox.addItem(app[0])
            #
            # self.app_number_cbox.setCurrentIndex(-1)

        reasons = self.session.query(ClContractCancellationReason).all()
        for reason in reasons:
            self.other_reason_cbox.addItem(reason.description, reason.code)

        # except SQLAlchemyError, e:
        #     PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
        #     return

    def __copy_application_from_navigator(self):

        selected_applications = self.navigator.application_results_twidget.selectedItems()

        if len(selected_applications) == 0:
            PluginUtils.show_error(self, self.tr("Query error"), self.tr("No applications selected in the Navigator."))
            return

        selected_application = selected_applications[0]

        try:
            current_app_no = selected_application.data(Qt.UserRole)
            app_no_count = self.session.query(CtApplication).filter_by(app_no=current_app_no).count()

            if app_no_count == 0:
                PluginUtils.show_error(self, self.tr("Working Soum"),
                                       self.tr("The selected Application {0} is not within the working soum. \n \n "
                                               "Change the Working soum to create a new application for the parcel.")
                                       .format(current_app_no))
                return

            application = self.session.query(CtApplication).filter_by(app_no=current_app_no).one()

            if not self.__validate_application(application):
                return

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

        self.found_edit.setText(application.app_no)

    def __validate_application(self, application):

        #checks that there is a decision for this application
        #checks that the decision was "approved"

        app_contarct_count = self.session.query(CtContractApplicationRole).\
            filter(CtContractApplicationRole.application == application.app_id).count()
        if app_contarct_count > 0:
            PluginUtils.show_error(self, self.tr("Application Error"),
                                   self.tr("This applicaton already created contract."))
            return False

        # last_decision_count = self.session.query(CtDecision).join(CtApplication.decision_result).filter(
        #     CtApplication.app_no == application.app_no) \
        #     .order_by(CtDecision.decision_date.desc()).count()
        # if last_decision_count == 0:
        #     PluginUtils.show_error(self, self.tr("Application Error"),
        #                            self.tr("It is not allowed to add an application without decision."))
        #     return False
        #
        # last_decision_count = self.session.query(CtDecision).join(CtApplication.decision_result) \
        #     .join(CtDecisionApplication.decision_ref) \
        #     .filter(CtApplication.app_no == application.app_no) \
        #     .filter(CtDecisionApplication.decision_result == Constants.DECISION_RESULT_APPROVED).count()
        #
        # if last_decision_count == 0:
        #     PluginUtils.show_error(self, self.tr("Application Error"),
        #                            self.tr("There is no approved decision result for this application."))
        #     return False

        #check that there is a parcel for this application
        ct_app_parcels_count = self.session.query(CtApplicationPUGParcel.application == application.app_id).count()
        if ct_app_parcels_count == 0:
            PluginUtils.show_error(self, self.tr("Application Error"),
                                   self.tr("It is not allowed to add applications without assigned parcel."))
            return False

        #check that there is a duration, if there should be one
        # if application.app_type in ConstantsPasture.APPLICATION_TYPE_WITH_DURATION:
        #     if application.approved_duration == 0 or application is None:
        #         PluginUtils.show_error(self, self.tr("Application Error"),
        #                                self.tr("There is no approved duration for this application."))
        #         return False
        #
        # if application.app_type not in ConstantsPasture.CONTRACT_TYPES:
        #     PluginUtils.show_error(self, self.tr("Application Error"),
        #                            self.tr("Its not allowed to create a contract based on this application type"))
        #     return False

        return True

    def __load_application_information(self):

        # parcel infos:
        application_role = self.contract.application_roles.filter_by(role=Constants.APPLICATION_ROLE_CREATES).one()
        application = application_role.application_ref

        app_parcel_count = self.session.query(CtApplicationParcel).filter(
            CtApplicationParcel.app_id == application.app_id).count()
        if app_parcel_count == 1:
            app_parcel = self.session.query(CtApplicationParcel).filter(
                CtApplicationParcel.app_id == application.app_id).one()
            if app_parcel.parcel_type:
                current_parcel_type = app_parcel.parcel_type
                parcel_type = self.session.query(ClParcelType).filter(ClParcelType.code == current_parcel_type).one()
                parcel_table_name = str(parcel_type.table_name)
                if app_parcel.parcel_id:
                    parcel_id = app_parcel.parcel_id
                    sql = "select parcel_id, area_m2, landuse from " + parcel_table_name + " where parcel_id = " + "'" + parcel_id + "'"
                    values = self.session.execute(sql).fetchall()
                    for row in values:
                        parcel_id = row[0]
                        area_m2 = str(row[1])
                        landuse_code = row[2]

                        count = self.assigned_parcel_twidget.rowCount()
                        self.assigned_parcel_twidget.insertRow(count)

                        item = QTableWidgetItem(parcel_id)
                        item.setIcon(QIcon(QPixmap(":/plugins/lm2/parcel.png")))
                        item.setData(Qt.UserRole, parcel_id)
                        self.assigned_parcel_twidget.setItem(count, 0, item)

                        item = QTableWidgetItem(str(area_m2))
                        item.setData(Qt.UserRole, area_m2)
                        self.assigned_parcel_twidget.setItem(count, 1, item)

                        landuse_count = self.session.query(ClLanduseType).filter(
                            ClLanduseType.code == landuse_code).count()
                        if landuse_count == 1:
                            landuse = self.session.query(ClLanduseType).filter(
                                ClLanduseType.code == landuse_code).one()

                            item = QTableWidgetItem(unicode(landuse.description))
                            item.setData(Qt.UserRole, landuse.code)
                            self.assigned_parcel_twidget.setItem(count, 2, item)

        #app date
        qt_date = PluginUtils.convert_python_date_to_qt(application.app_timestamp)
        self.contract_begin_date.setDate(qt_date)

        self.duration_sbox.setValue(5)

    @pyqtSlot(int)
    def on_duration_sbox_valueChanged(self, value):

        year = self.contract_begin_date.date().year()
        month = self.contract_begin_date.date().month()
        day = self.contract_begin_date.date().day()
        self.contract_end_date.setDate(QDate(int(year) + value, month, day))

    def __contract_status(self):

        if self.draft_rbutton.isChecked():
            return ConstantsPasture.CONTRACT_STATUS_DRAFT
        elif self.active_rbutton.isChecked():
            return ConstantsPasture.CONTRACT_STATUS_ACTIVE
        elif self.expired_rbutton.isChecked():
            return ConstantsPasture.CONTRACT_STATUS_EXPIRED
        elif self.cancelled_rbutton.isChecked():
            return ConstantsPasture.CONTRACT_STATUS_CANCELLED

    def __add_archived_fee_row(self, row, person, fee):

        item = QTableWidgetItem(u'{0}, {1}'.format(person.name, person.first_name))
        item.setData(Qt.UserRole, person.person_id)
        self.__lock_item(item)
        self.archive_land_fee_twidget.setItem(row, CONTRACTOR_NAME, item)
        item = QTableWidgetItem(u'{0}'.format(person.person_id))
        self.__lock_item(item)
        self.archive_land_fee_twidget.setItem(row, CONTRACTOR_ID, item)
        item = QTableWidgetItem('{0}'.format(fee.share))
        self.__lock_item(item)
        self.archive_land_fee_twidget.setItem(row, CONTRACTOR_SHARE, item)
        item = QTableWidgetItem('{0}'.format(fee.area))
        self.__lock_item(item)
        self.archive_land_fee_twidget.setItem(row, CONTRACTOR_AREA, item)
        item = QTableWidgetItem('{0}'.format(fee.fee_calculated))
        self.__lock_item(item)
        self.archive_land_fee_twidget.setItem(row, CONTRACTOR_FEE_CALCULATED, item)
        item = QTableWidgetItem('{0}'.format(fee.fee_contract))
        self.__lock_item(item)
        self.archive_land_fee_twidget.setItem(row, CONTRACTOR_FEE_CONTRACT, item)
        item = QTableWidgetItem('{0}'.format(fee.grace_period))
        self.__lock_item(item)
        self.archive_land_fee_twidget.setItem(row, CONTRACTOR_GRACE_PERIOD, item)
        payment_frequency = self.session.query(ClPaymentFrequency).get(fee.payment_frequency)
        item = QTableWidgetItem(u'{0}'.format(payment_frequency.description))
        self.__lock_item(item)
        self.archive_land_fee_twidget.setItem(row, CONTRACTOR_PAYMENT_FREQUENCY, item)

    def __setup_twidget(self, table_widget):

        table_widget.setAlternatingRowColors(True)
        table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        table_widget.setSelectionMode(QTableWidget.SingleSelection)

    def __setup_doc_twidgets(self):

        self.doc_twidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.doc_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.doc_twidget.horizontalHeader().resizeSection(0, 50)
        self.doc_twidget.horizontalHeader().resizeSection(1, 270)
        self.doc_twidget.horizontalHeader().resizeSection(2, 200)
        self.doc_twidget.horizontalHeader().resizeSection(3, 50)
        self.doc_twidget.horizontalHeader().resizeSection(4, 50)
        self.doc_twidget.horizontalHeader().resizeSection(5, 50)

        delegate = PastureContractDocumentDelegate(self.doc_twidget, self)
        self.doc_twidget.setItemDelegate(delegate)

        # try:
        self.__add_doc_types()
            # self.__update_doc_twidget()

        # except SQLAlchemyError, e:
        #     PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
        #     return

    def __remove_document_items(self, twidget):

        while twidget.rowCount() > 0:
            twidget.removeRow(0)

    def __add_doc_types(self):

        app_no = self.application_this_contract_based_edit.text()
        if len(app_no) == 0:
            return
        app = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).one()

        required_doc_types = self.session.query(SetPastureDocument).\
            filter(SetPastureDocument.app_type == app.app_type).filter(SetPastureDocument.parent_type == 2).all()

        for doc in required_doc_types:
            docType = self.session.query(ClPastureDocument).filter(ClPastureDocument.code == doc.document).one()
            item_provided = QTableWidgetItem()
            item_provided.setCheckState(Qt.Unchecked)

            item_doc_type = QTableWidgetItem(docType.description)
            item_doc_type.setData(Qt.UserRole, docType.code)
            item_doc_type.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            item_name = QTableWidgetItem("")
            item_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            item_view = QTableWidgetItem("")
            item_delete = QTableWidgetItem("")
            item_open = QTableWidgetItem("")
            row = self.doc_twidget.rowCount()

            self.doc_twidget.insertRow(row)
            self.doc_twidget.setItem(row, DOC_TYPE_COLUMN, item_doc_type)
            self.doc_twidget.setItem(row, DOC_NAME_COLUMN, item_name)
            self.doc_twidget.setItem(row, DOC_PROVIDED_COLUMN, item_provided)
            self.doc_twidget.setItem(row, DOC_VIEW_COLUMN, item_view)
            self.doc_twidget.setItem(row, DOC_OPEN_COLUMN, item_open)
            self.doc_twidget.setItem(row, DOC_REMOVE_COLUMN, item_delete)

    @pyqtSlot()
    def on_load_doc_button_clicked(self):

        self.__update_doc_twidget()

    def __update_doc_twidget(self):

        file_path = PasturePath.contrac_file_path()

        host = QSettings().value(SettingsConstants.HOST, "")
        contract_no = self.contract.contract_no
        contract_no = contract_no.replace("/", "-")
        if host == "localhost":
            file_path = file_path + '/' + contract_no
            if not os.path.exists(file_path):
                os.makedirs(file_path)
        else:
            file_path = file_path + '\\' + contract_no
            if not os.path.exists(file_path):
                os.makedirs(file_path)

        for file in os.listdir(file_path):
            os.listdir(file_path)
            if file.endswith(".pdf"):
                doc_type = file[17:-4]
                file_name = file
                contract_no = file[:16]
                contract_no = contract_no[:10] +'/'+ contract_no[-5:]

                for i in range(self.doc_twidget.rowCount()):
                    doc_type_item = self.doc_twidget.item(i, DOC_TYPE_COLUMN)

                    doc_type_code = str(doc_type_item.data(Qt.UserRole))

                    if len(str(doc_type_item.data(Qt.UserRole))) == 1:
                        doc_type_code = '0'+ str(doc_type_item.data(Qt.UserRole))
                    if len(doc_type) == 1:
                        doc_type = '0' + doc_type
                    if doc_type == doc_type_code and self.contract.contract_no == contract_no:
                        item_name = self.doc_twidget.item(i, DOC_NAME_COLUMN)
                        item_name.setText(file_name)

                        item_provided = self.doc_twidget.item(i, DOC_PROVIDED_COLUMN)
                        item_provided.setCheckState(Qt.Checked)

                        item_open = self.doc_twidget.item(i, DOC_OPEN_COLUMN)
                        item_remove = self.doc_twidget.item(i, DOC_REMOVE_COLUMN)
                        item_view = self.doc_twidget.item(i, DOC_VIEW_COLUMN)

                        self.doc_twidget.setItem(i, DOC_PROVIDED_COLUMN, item_provided)
                        self.doc_twidget.setItem(i, DOC_OPEN_COLUMN, item_open)
                        self.doc_twidget.setItem(i, DOC_REMOVE_COLUMN, item_remove)
                        self.doc_twidget.setItem(i, DOC_VIEW_COLUMN, item_view)
                        self.doc_twidget.setItem(i, DOC_NAME_COLUMN, item_name)

    def __lock_item(self, item):

        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    def __save_settings(self):

        # try:
        self.__save_contract()
        return True

        # except LM2Exception, e:
        #     PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

    def __save_contract(self):

        # self.create_savepoint()
        # try:
        if self.active_rbutton.isChecked():

            if self.contract.cancellation_date != None:
                PluginUtils.show_error(self, self.tr("Error saving contract"),
                                   self.tr("This contract cancelled. You create a new contract"))
                return

        if self.contract.application_roles.filter_by(role=ConstantsPasture.APPLICATION_ROLE_CANCELS).count() != 0:
            PluginUtils.show_error(self, self.tr("Error saving contract"),
                                   self.tr("It is not allowed to save a contract. This contract cancelled."))
            return

        if self.contract.application_roles.filter_by(role=ConstantsPasture.APPLICATION_ROLE_CREATES).count() == 0:
            PluginUtils.show_error(self, self.tr("Error saving contract"),
                                   self.tr("It is not allowed to save a contract without an assigned application."))
            return

        self.contract.status = self.__contract_status()

        self.contract.certificate_no = 0

        if self.cancellation_date_check_box.isChecked():

            self.contract.cancellation_date = self.cancelation_date.date().toString(ConstantsPasture.DATABASE_DATE_FORMAT)

            if self.application_based_rbutton.isChecked():
                self.__save_cancellation_app()
            else:
                self.contract.cancellation_reason = self.other_reason_cbox.itemData(
                    self.other_reason_cbox.currentIndex())


        self.contract.contract_begin = self.contract_begin_date.date().toString(ConstantsPasture.DATABASE_DATE_FORMAT)
        self.contract.contract_date = self.contract_date.date().toString(ConstantsPasture.DATABASE_DATE_FORMAT)
        self.contract.contract_begin = self.contract_end_date.date().toString(ConstantsPasture.DATABASE_DATE_FORMAT)

        if not self.attribute_update:
            self.contract.certificate_no = 0

    def __start_fade_out_timer(self):

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

    def __save_cancellation_app(self):

        cancel_count = self.contract.application_roles.filter_by(role=ConstantsPasture.APPLICATION_ROLE_CANCELS).count()
        # self.contract.cancellation_reason = None
        # if cancel_count > 0:
        #     # update
        #     cancellation_app = self.contract.application_roles.filter_by(role=ConstantsPasture.APPLICATION_ROLE_CANCELS).one()
        #     cancellation_app.application = self.app_number_cbox.currentText()
        # else:
        #     # insert
        #     contract_app = CtContractApplicationRole()
        #     contract_app.application = self.app_number_cbox.currentText()
        #     contract_app.contract = self.contract.contract_id
        #     contract_app.role = ConstantsPasture.APP_ROLE_CANCEL
        #     self.contract.application_roles.append(contract_app)

    def __save_other_reason(self):

        cancel_count = self.contract.application_roles.filter_by(role=ConstantsPasture.APPLICATION_ROLE_CANCELS).count()
        if cancel_count > 0:
            self.contract.application_roles.filter_by(role=ConstantsPasture.APPLICATION_ROLE_CANCELS).delete()

        self.contract.cancellation_reason = self.other_reason_cbox.itemData(self.other_reason_cbox.currentIndex())

    def __read_active_conditions(self):

        for row in range(self.item_model.rowCount(QModelIndex())):
            item = self.item_model.item(row)
            self.__toggle_item(item)

    def __toggle_item(self, item):

        if item.hasChildren():
            for row in range(item.rowCount()):
                child = item.child(row)
                self.__toggle_item(child)
        else:
            code = item.data(Qt.UserRole)
            if code is None:
                return
            if self.__condition_assigned(code):
                item.setCheckState(Qt.Checked)

    def __condition_assigned(self, code):

        contract = self.session.query(CtContract).get(self.contract.contract_id)
        count = contract.conditions.filter(CtContractCondition.condition == code).count()
        if count > 0:
            return True
        return False

    def __item_model(self, app_type):

        model = QStandardItemModel()
        parent_item = model.invisibleRootItem()
        item1 = None

        contract_conditions = self.session.query(ClContractCondition).order_by(ClContractCondition.code).all()

        if app_type == 5:
            right_type = 2  # possession
        elif app_type == 6:
            right_type = 1  # use
        else:
            right_type = 2

        sub_conditions = list()
        used_conditions = list()

        for condition in contract_conditions:

            filter_str = '{0}'.format(right_type)
            code = '{0}'.format(condition.code)
            filter_str += code[1:4]
            level2 = code[4:5]

            if filter_str in sub_conditions:
                continue

            if code.startswith('{0}'.format(right_type)):

                sub_conditions.append(filter_str)
                row = list()
                item = QStandardItem()
                item.setText(u'Гэрээний нөхцөл: {0}.{1}'.format(code[1:2], code[2:4].lstrip('0')))
                item.setCheckable(True)
                row.append(item)
                parent_item.appendRow(row)
                grouped_conditions1 = self.session.query(ClContractCondition). \
                    filter(ClContractCondition.code / 1000 == int(filter_str)).order_by(ClContractCondition.code).all()

                for condition1 in grouped_conditions1:

                    code1 = '{0}'.format(condition1.code)
                    description1 = condition1.description

                    if not condition1.code in used_conditions:
                        item1 = QStandardItem()
                        item1.setText(u'{0}...'.format(description1[:50]))
                        item1.setData(condition1.code, Qt.UserRole)
                        item1.setCheckable(True)
                        item.appendRow(item1)
                        level2 = code1[4:5]
                        used_conditions.append(condition1.code)

                    if level2 != '0':

                        grouped_conditions2 = self.session.query(ClContractCondition). \
                            filter(ClContractCondition.code / 100 == int(filter_str + level2)). \
                            order_by(ClContractCondition.code).all()

                        for condition2 in grouped_conditions2:

                            code2 = '{0}'.format(condition2.code)
                            description2 = condition2.description

                            if not code2.endswith('0'):

                                if condition2.code in used_conditions:
                                    continue

                                item2 = QStandardItem()
                                item2.setText(u'{0}...'.format(description2[:50]))
                                item2.setData(condition2.code, Qt.UserRole)
                                item2.setCheckable(True)
                                item1.appendRow(item2)
                                used_conditions.append(condition2.code)

        headers = [""]
        model.setHorizontalHeaderLabels(headers)

        return model

    def __check_item(self, item, toggled_list):

        if item.checkState() != Qt.Unchecked:
            code = item.data(Qt.UserRole)
            if not code is None:
                toggled_list.append(code)
            if item.hasChildren():
                for row in range(item.rowCount()):
                    child = item.child(row)
                    self.__check_item(child, toggled_list)

    def __item_changed(self, item):

        parent = item.parent()

        if item.checkState() == Qt.Checked:
            if item.hasChildren():
                for row in range(item.rowCount()):
                    child = item.child(row)
                    child.setCheckState(Qt.Checked)
            if not parent is None:
                for row in range(parent.rowCount()):
                    child = parent.child(row)
                    if child.checkState() == Qt.Unchecked:
                        parent.setCheckState(Qt.PartiallyChecked)
                        return
                parent.setCheckState(Qt.Checked)

        elif item.checkState() == Qt.Unchecked:
            if item.hasChildren():
                for row in range(item.rowCount()):
                    child = item.child(row)
                    child.setCheckState(Qt.Unchecked)
            if not parent is None:
                for row in range(parent.rowCount()):
                    child = parent.child(row)
                    if child.checkState() == Qt.Checked or child.checkState() == Qt.PartiallyChecked:
                        parent.setCheckState(Qt.PartiallyChecked)
                        return
                parent.setCheckState(Qt.Unchecked)

        else:
            if not parent is None:
                parent.setCheckState(Qt.PartiallyChecked)

    def __show_preview(self, item):

        code = item.data(Qt.UserRole)

        if code is None:
            self.preview_text_edit.setHtml(u'<html><b>{0}</b></html>'.format(item.text()))
        else:
            condition = self.session.query(ClContractCondition).get(code)
            text_len = len(self.preview_text_edit.toPlainText())
            if text_len > 0:
                whitespace = '<html><br></html>'
            else:
                whitespace = '<html></html>'
            if item.hasChildren():
                self.preview_text_edit.setHtml(
                    self.preview_text_edit.toHtml() + whitespace + u'<html><i>{0}</i></html>'.format(
                        condition.description))
            else:
                self.preview_text_edit.setHtml(
                    self.preview_text_edit.toHtml() + whitespace + u'<html>{0}</html>'.format(condition.description))

        if item.hasChildren():
            for row in range(item.rowCount()):
                child = item.child(row)
                self.__show_preview(child)

    @pyqtSlot(int)
    def on_app_number_cbox_currentIndexChanged(self, current_index):

        if self.app_number_cbox.currentIndex() == -1:
            return

        try:
            app_number = self.app_number_cbox.itemText(current_index)
            if self.application_this_contract_based_edit.text():
                current_application_creates = self.contract.application_roles.filter_by(
                    role=ConstantsPasture.APPLICATION_ROLE_CREATES).one()
                if current_application_creates.application_ref.app_no == app_number:
                    PluginUtils.show_error(self, self.tr("Error"),
                                           self.tr("The application that creates the contract, can't cancel it."))
                    self.app_number_cbox.setCurrentIndex(-1)
                    return

            app = self.session.query(CtApplication).filter(CtApplication.app_no == app_number).one()
            self.type_edit.setText(app.app_type_ref.description)

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

    @pyqtSlot(bool)
    def on_application_based_rbutton_toggled(self, checked):

        if checked:
            self.app_number_cbox.setEnabled(True)
            self.other_reason_cbox.setEnabled(False)
            try:
                if self.app_number_cbox.currentIndex() == -1:
                    return

                app_number = self.app_number_cbox.itemText(self.app_number_cbox.currentIndex())
                app = self.session.query(CtApplication).filter(CtApplication.app_no == app_number).one()
                self.type_edit.setText(app.app_type_ref.description)

            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return
        else:
            self.app_number_cbox.setEnabled(False)
            self.other_reason_cbox.setEnabled(True)
            self.type_edit.setText("")

    @pyqtSlot(int)
    def on_cancellation_date_check_box_stateChanged(self, state_status):

        if state_status == Qt.Checked:
            self.cancelation_date.setEnabled(True)
            self.app_number_cbox.setEnabled(True)
            self.application_based_rbutton.setEnabled(True)
            self.other_reason_rbutton.setEnabled(True)
            self.application_type_edit.setEnabled(True)
            self.person_id_edit.setEnabled(True)
        else:
            self.cancelation_date.setEnabled(False)
            self.app_number_cbox.setEnabled(False)
            self.application_based_rbutton.setEnabled(False)
            self.other_reason_rbutton.setEnabled(False)
            self.application_type_edit.setEnabled(False)
            self.person_id_edit.setEnabled(False)

    @pyqtSlot()
    def on_accept_button_clicked(self):

        current_app_no = self.found_edit.text()

        if current_app_no == "":
            return
        try:
            application = self.session.query(CtApplication).filter_by(app_no=current_app_no).one()

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

        self.application_this_contract_based_edit.setText(application.app_no)
        self.application_type_edit.setText(application.app_type_ref.description)
        self.found_edit.setText("")

        contract_app = CtContractApplicationRole()
        contract_app.application_ref = application
        contract_app.application = application.app_id
        contract_app.contract = self.contract.contract_id
        contract_app.contract_ref = self.contract

        contract_app.role = ConstantsPasture.APPLICATION_ROLE_CREATES
        self.contract.application_roles.append(contract_app)

        # try:
        self.__load_application_information()

        # except SQLAlchemyError, e:
        #     PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
        #     return

        self.accept_button.setEnabled(False)

    @pyqtSlot(int)
    def on_time_period_cbox_currentIndexChanged(self, idx):

        self.archive_land_fee_twidget.clearContents()
        self.archive_land_fee_twidget.setRowCount(0)

        if idx == -1:
            return

        # read begin date from cbox
        begin_date = self.time_period_cbox.itemData(idx, Qt.UserRole)

        base_figures = self.session.query(CtArchivedFee.base_fee_per_m2, CtArchivedFee.subsidized_area,
                                          CtArchivedFee.subsidized_fee_rate).distinct(). \
            filter(CtArchivedFee.contract == self.contract.contract_id). \
            filter(CtArchivedFee.valid_from == begin_date).one()

        self.archive_base_fee_edit.setText('{0}'.format(base_figures.base_fee_per_m2))
        self.archive_subsidized_area_edit.setText('{0}'.format(base_figures.subsidized_area))
        self.archive_subsidized_fee_rate_edit.setText('{0}'.format(base_figures.subsidized_fee_rate))

        app_no = self.application_this_contract_based_edit.text()
        if len(app_no) == 0:
            return
        app_no_count = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).count()
        if app_no_count == 0:
            return

        app = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).one()
        contractors = app.stakeholders.filter(CtApplicationPersonRole.role == ConstantsPasture.APPLICANT_ROLE_CODE).all()
        if app_no[6:-9] == '07' or app_no[6:-9] == '14':
            contractors = app.stakeholders.filter(CtApplicationPersonRole.role == ConstantsPasture.NEW_RIGHT_HOLDER_CODE).all()
        row = 0
        for contractor in contractors:
            person = contractor.person_ref
            fee_count = person.archived_fees.filter(CtArchivedFee.contract == self.contract.contract_id). \
                filter(CtArchivedFee.valid_from == begin_date).count()
            if fee_count > 0:
                self.archive_land_fee_twidget.setRowCount(row + 1)
                fee = person.archived_fees.filter(CtArchivedFee.contract == self.contract.contract_id). \
                    filter(CtArchivedFee.valid_from == begin_date).one()
                self.__add_archived_fee_row(row, person, fee)
                row += 1

        self.archive_land_fee_twidget.resizeColumnToContents(0)
        self.archive_land_fee_twidget.resizeColumnToContents(1)
        self.archive_land_fee_twidget.resizeColumnToContents(2)
        self.archive_land_fee_twidget.resizeColumnToContents(3)
        self.archive_land_fee_twidget.resizeColumnToContents(4)
        self.archive_land_fee_twidget.resizeColumnToContents(5)
        self.archive_land_fee_twidget.horizontalHeader().setResizeMode(6, QHeaderView.Stretch)

    @pyqtSlot()
    def on_unassign_button_clicked(self):

        self.application_this_contract_based_edit.setText("")
        self.application_type_edit.setText("")

        try:
            self.contract.application_roles.filter_by(role=ConstantsPasture.APPLICATION_ROLE_CREATES).delete()
        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

        self.accept_button.setEnabled(True)

    @pyqtSlot()
    def on_drop_label_itemDropped(self):

        self.__copy_application_from_navigator()

    @pyqtSlot()
    def on_search_button_clicked(self):

        if not self.enter_application_num_edit.text():
            return

        # try:
        app_no = self.enter_application_num_edit.text()
        count = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).count()
        if count == 1:
            application = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).one()
            self.app_id = application.app_id
            if not self.__validate_application(application):
                return

            self.found_edit.setText(application.app_no)
            self.enter_application_num_edit.setText("")
        else:
            PluginUtils.show_error(self, self.tr("Database Error"),
                                   self.tr("Found multiple applications for the number {0}.").format(app_no))

        # except SQLAlchemyError, e:
        #     PluginUtils.show_error(self, self.tr("Database Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

    @pyqtSlot()
    def on_apply_button_clicked(self):

        if not self.__save_settings():
            return

        app_no = self.application_this_contract_based_edit.text()
        application = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).one()
        app_status9_count = self.session.query(CtApplicationStatus)\
            .filter(CtApplicationStatus.application == application.app_id)\
            .filter(CtApplicationStatus.status == 9).count()

        if self.active_rbutton.isChecked() and app_status9_count == 0:
            new_status = CtApplicationStatus()
            new_status.application = application.app_id
            new_status.next_officer_in_charge = DatabaseUtils.current_sd_user().user_id
            new_status.officer_in_charge = DatabaseUtils.current_sd_user().user_id
            new_status.status = 9
            new_status.status_date = self.contract.contract_date
            self.session.add(new_status)

        self.commit()
        self.__start_fade_out_timer()
        self.attribute_update = True

    def reject(self):

        self.rollback()
        QDialog.reject(self)

    def __contract_possess(self):

        aimag_code = self.application_this_contract_based_edit.text()[:3]
        # try:
        aimag = self.session.query(AuLevel1).filter(AuLevel1.code == aimag_code).one()
        # except SQLAlchemyError, e:
        #     raise LM2Exception(self.tr("Database Query Error"),
        #                        self.tr("aCould not execute: {0}").format(e.message))
        soum_code = self.application_this_contract_based_edit.text()[:5]
        # try:
        soum = self.session.query(AuLevel2).filter(AuLevel2.code == soum_code).one()
        # except SQLAlchemyError, e:
        #     raise LM2Exception(self.tr("Database Query Error"),
        #                        self.tr("aCould not execute: {0}").format(e.message))

        app_no = self.application_this_contract_based_edit.text()

        app_status = self.session.query(CtApplicationStatus).filter(
            CtApplicationStatus.application == self.app_id).order_by(CtApplicationStatus.status.desc()).all()
        for p in app_status:
            if p.status == 9:
                officer = DatabaseUtils.get_sd_employee(p.officer_in_charge);
                break
                # officer = self.session.query(SetRole).filter(SetRole.user_name_real == p.officer_in_charge).one()
            else:
                officer = DatabaseUtils.get_sd_employee(p.officer_in_charge);
                # officer = self.session.query(SetRole).filter(SetRole.user_name_real == p.officer_in_charge).one()
        # except SQLAlchemyError, e:
        #     raise LM2Exception(self.tr("Database Query Error"),
        #                        self.tr("aCould not execute: {0}").format(e.message))

        if not officer:
            officer = DatabaseUtils.current_employee()

        if not officer:
            for p in app_status:
                officer = DatabaseUtils.get_sd_employee(p.officer_in_charge);
                if officer:
                    break

        self.officer = officer
        app_no = self.application_this_contract_based_edit.text()

        # try:
        # app_person = self.session.query(CtApplicationPersonRole).filter(
        #     CtApplicationPersonRole.application == self.app_id).all()

        app_person = self.session.query(CtApplicationPersonRole). \
            join(CtApplication, CtApplicationPersonRole.application == CtApplication.app_id). \
            join(SetApplicationTypePersonRole, CtApplication.app_type == SetApplicationTypePersonRole.type). \
            filter(CtApplication.app_id == self.app_id). \
            filter(SetApplicationTypePersonRole.role == CtApplicationPersonRole.role). \
            filter(SetApplicationTypePersonRole.is_owner == True).all()

        # app_person_new_count = self.session.query(CtApplicationPersonRole). \
        #     filter(CtApplicationPersonRole.application == self.app_id). \
        #     filter(CtApplicationPersonRole.role == 70).count()
        # if app_person_new_count > 0:
        #     app_person = self.session.query(CtApplicationPersonRole). \
        #         filter(CtApplicationPersonRole.application == self.app_id). \
        #         filter(CtApplicationPersonRole.role == 70).all()
        person = None
        for p in app_person:
            if p.main_applicant == True:
                person = self.session.query(BsPerson).filter(BsPerson.person_id == p.person).one()

                bank_count = self.session.query(ClBank).filter(ClBank.code == person.bank).count()
                person_bank_name = " "
                if bank_count != 0:
                    bank = self.session.query(ClBank).filter(ClBank.code == person.bank).one()
                    person_bank_name = bank.description

                aimag_count = self.session.query(AuLevel1).filter(
                    AuLevel1.code == person.address_au_level1).count()
                aimag_name = " "
                if aimag_count != 0:
                    aimag = self.session.query(AuLevel1).filter(AuLevel1.code == person.address_au_level1).one()
                    aimag_name = aimag.name

                soum_count = self.session.query(AuLevel2).filter(
                    AuLevel2.code == person.address_au_level2).count()
                soum_name = " "
                if soum_count != 0:
                    soum_person = self.session.query(AuLevel2).filter(AuLevel2.code == person.address_au_level2).one()
                    soum_name = soum_person.name

                bag_count = self.session.query(AuLevel2).filter(
                    AuLevel3.code == person.address_au_level3).count()
                bag_name = " "
                if bag_count != 0:
                    bag = self.session.query(AuLevel3).filter(AuLevel3.code == person.address_au_level3).one()
                    bag_name = bag.name
        #
        # except SQLAlchemyError, e:
        #     raise LM2Exception(self.tr("Database Query Error"),
        #                        self.tr("aCould not execute: {0}").format(e.message))

        base_fee = 0
        payment = 0
        contract_no = self.contract_num_edit.text()

        # try:
        # data = self.__fee_geoware()
        # if data:
        #     if data['status']:
        #         for value in data['data']:
        #             payment = payment + value['payment']
        #             base_fee = round(float(value['base_fee_per_m2']))
        local_name = " "
        address_street_name = ""
        address_khaskhaa = ""
        address_building_no = ""
        address_entrance_no = ""
        address_apartment_no = ""
        person_address = ""
        person_register = ""

        if person:
            if person.address_street_name != None:
                address_street_name = person.address_street_name + u" гудамж, "
            if person.address_khaskhaa != None:
                address_khaskhaa = person.address_khaskhaa
            if person.address_building_no != None:
                address_building_no = person.address_building_no + u" байр, "
            if person.address_entrance_no != None:
                address_entrance_no = person.address_entrance_no + ', '
            if person.address_apartment_no != None:
                address_apartment_no = person.address_apartment_no
            if person.address_street_name != None or person.address_khaskhaa != None:
                if person.address_town_or_local_name != None:
                    local_name = person.address_town_or_local_name + ', '
                person_address = aimag_name + ", " + soum_name + ", " + bag_name + ", " + local_name + address_street_name + address_khaskhaa
            elif person.address_building_no != None or person.address_entrance_no != None:
                if person.address_town_or_local_name != None:
                    local_name = person.address_town_or_local_name + ', '
                person_address = aimag_name + ", " + soum_name + ", " + bag_name + ", " + local_name + address_building_no + address_entrance_no + address_apartment_no
            else:
                if person.address_town_or_local_name != None:
                    local_name = person.address_town_or_local_name
                person_address = aimag_name + ", " + soum_name + ", " + bag_name + ", " + local_name
        app_type = self.application_type_edit.text()[:2]
        path = FileUtils.map_file_path()
        default_path = r'D:/TM_LM2/contracts'

        tpl = DocxTemplate(path+'geree_niitiin_ezemshil_DX.docx')

        if not officer:
            PluginUtils.show_message(self, self.tr(" Employee"), self.tr("Employee not found"))
            return

        o_position = ''
        aimag_name = aimag.name
        soum_name = soum.name
        contract_no = self.contract_num_edit.text()
        cerificate_no = ''
        contract_date = self.contract_date.text()
        contract_date_year = contract_date[0:-6]
        contract_date_month = contract_date[5:-3]
        contract_date_day = contract_date[-2:]
        dec_year = ''
        dec_month = ''
        dec_day = ''
        o_firstname = officer.firstname
        o_surname = officer.lastname
        if officer.position_ref:
            o_position = officer.position_ref.name
        company_name = ''
        person_surname = ''
        person_firstname = ''
        contact_position = ''
        person_full_name = ''
        if person:
            person_register = person.person_register
            if person.type == 10 or person.type == 20 or person.type == 50:
                person_surname = person.name
                person_firstname = person.first_name
                person_full_name = person_surname + u' овогтой ' + person_firstname
            elif person.type == 30 or person.type == 40 or person.type == 60 or person.type == 70:
                company_name = person.name
                contact_position = person.contact_position
                person_surname = person.contact_surname
                person_firstname = person.contact_first_name
                person_full_name = person.name

        base_fee = str(base_fee)

        quarterly1_fee = str(payment / 4)
        quarterly2_fee = str(payment / 4)
        quarterly3_fee = str(payment / 4)
        quarterly4_fee = str(payment / 4)
        payment = str(payment)
        # bank_name = report_settings[Constants.REPORT_BANK]
        # account_no = report_settings[Constants.REPORT_BANK_ACCOUNT]
        # office_address = report_settings[Constants.REPORT_ADDRESS]

        aimag_name = ''
        soum_name = ''
        bag_name = ''
        street_name = ''
        khashaa_name = ''

        fee_area = ''
        fee_rate = ''

        bank_name = ''
        account_no = ''
        bank_value = ''
        department_name = ''
        department_phone = ''
        department_address = ''
        head_surname = ''
        head_firstname = ''
        person_bank_name = ''
        person_account = ''
        person_phone = ''
        person_email = ''

        if self.officer.department_ref:
            department = self.officer.department_ref
            department_id = department.department_id

            department_accounts = self.session.query(SdDepartmentAccount).filter(
                SdDepartmentAccount.department_id == department_id).all()
            for value in department_accounts:
                account_no = value.account_no
                bank = value.bank_ref
                bank_name = bank.description
                bank_full_value = bank_name + ' - ' + account_no
                if bank_value == '':
                    bank_value =  bank_full_value
                else:
                    bank_value = bank_value + ', ' + bank_full_value

            # if self.officer.department_ref.bank_name:
            #     bank_name = self.officer.department_ref.bank_name
            # if self.officer.department_ref.account_no:
            #     account_no = self.officer.department_ref.account_no
            if self.officer.department_ref.name:
                department_name = self.officer.department_ref.name
            if self.officer.department_ref.phone:
                department_phone = self.officer.department_ref.phone
            if self.officer.department_ref.address:
                department_address = self.officer.department_ref.address
            if self.officer.department_ref.head_surname:
                head_surname = self.officer.department_ref.head_surname
            if self.officer.department_ref.head_firstname:
                head_firstname = self.officer.department_ref.head_firstname

        if person:
            person_bank_name = person.person_bank_name
            person_account = person.bank_account_no
            person_phone = person.phone
            person_email = person.email_address

        parcel_id = ''
        area_m2 = 0
        landuse = ''

        if self.session.query(CtApplicationParcel).filter(CtApplicationParcel.app_id == self.app_id).count() > 0:
            app_parcel = self.session.query(CtApplicationParcel).filter(CtApplicationParcel.app_id == self.app_id).first()
            parcel_id = app_parcel.parcel_id
            if self.session.query(CaStateParcelTbl).filter(CaStateParcelTbl.parcel_id == parcel_id) > 0:
                parcel = self.session.query(CaStateParcelTbl).filter(CaStateParcelTbl.parcel_id == parcel_id).first()
                area_m2 = parcel.area_m2
                if parcel.landuse:
                    landuse_type = self.session.query(ClLanduseType).filter(
                        ClLanduseType.code == parcel.landuse).one()
                    landuse = landuse_type.description

        sum_name_dec = ''
        sum_officer = ''

        if contact_position is None:
            contact_position = ''
        if company_name is None:
            company_name = ''
        if person_surname is None:
            person_surname = ''
        if person_firstname is None:
            person_firstname = ''
        if person:
            if person.type == 10 or person.type == 20 or person.type == 50:
                company_name = person_surname + u'овогтой' + person_firstname
            elif person.type == 30 or person.type == 40 or person.type == 60 or person.type == 70 or person.type == 80:
                company_name = company_name + u'-н ' + contact_position + u' ' + person_surname + u' овогтой ' + person_firstname

        if self.is_sign_checkbox.isChecked():
            darga_signature = self.print_officer_cbox.currentText() + u'/.............................../ тамга/'
            darga_position = self.position_lbl.text()
        else:
            darga_signature = ''
            darga_position = ''

        duration_year = ''

        au1 = DatabaseUtils.working_l1_code()
        if au1 == '011':
            local_aimag_name = aimag_name + u' Хот'
        else:
            local_aimag_name = aimag_name + u' Аймаг, ' + soum_name + u' сум'

        context = {
            'local_aimag_name': local_aimag_name,
            'property_no': '',
            'aimag_name': aimag_name,
            'contract_no': contract_no,
            'cert_no': cerificate_no,
            'c_year': time.strftime("%Y"),
            'c_month': time.strftime("%m"),
            'c_day': time.strftime("%d"),
            'sum_name': soum_name,
            'sum_name_dec': sum_name_dec,
            'sum_officer': sum_officer,
            'dec_year': dec_year,
            'dec_month': dec_month,
            'dec_day': dec_day,
            # 'dec_no': decision_no,
            'o_firstname': o_firstname,
            'o_surname': o_surname,
            'o_position': o_position,
            'company_name': company_name,
            'contact_position': contact_position,
            'person_full_name': person_full_name,
            'person_surname': person_surname,
            'person_firstname': person_firstname,
            'area_m2': area_m2,
            'landuse': landuse,
            'base_fee': base_fee,
            'payment': payment,
            'quarterly1_fee': quarterly1_fee,
            'quarterly2_fee': quarterly2_fee,
            'quarterly3_fee': quarterly3_fee,
            'quarterly4_fee': quarterly4_fee,
            'bank_value': bank_value,
            # 'bank_name': bank_name,
            # 'account_no': account_no,
            'office_address': department_address,
            'office_name': department_name,
            'department_name': department_name,
            'office_phone': department_phone,
            'aimag': aimag_name,
            'soum': soum_name,
            'bag': bag_name,
            'street': street_name,
            'khashaa': khashaa_name,
            'fee_area': fee_area,
            'fee_rate': fee_rate,
            'person_address': person_address,
            'person_bank_name': person_bank_name,
            'person_account': person_account,
            'person_phone': person_phone,
            'person_email': person_email,
            'person_id': person_register,
            'parcel_id': parcel_id,
            'duration_year': duration_year,
            'darga_position': darga_position,
            'head_surname': head_surname,
            'head_firstname': head_firstname,
            'darga_signature': darga_signature
        }

        tpl.render(context)

        # try:
        tpl.save(default_path + "/" + contract_no[:-6] + '-' + contract_no[-5:] + ".docx")
        QDesktopServices.openUrl(
            QUrl.fromLocalFile(default_path + "/" + contract_no[:-6] + '-' + contract_no[-5:] + ".docx"))
        # except IOError, e:
        #     PluginUtils.show_error(self, self.tr("Out error"),
        #                            self.tr("This file is already opened. Please close re-run"))

    def __group_name(self):

        app_no = self.application_this_contract_based_edit.text()
        application_instance = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).one()
        app_id = application_instance.app_id
        app_person = self.session.query(CtApplicationPersonRole).filter(
            CtApplicationPersonRole.application == app_id).all()

        parcel_count = self.session.query(CtApplicationPUGParcel).filter(
            CtApplicationPUGParcel.application == app_id).count()
        if parcel_count == 0:
            PluginUtils.show_message(self, self.tr("parcel none"), self.tr("None Parcel!!!"))
            return

        for p in app_person:
            if p.main_applicant == True:
                person = self.session.query(BsPerson).filter(BsPerson.person_id == p.person).one()
        app_pug = self.session.query(CtApplicationPUG).filter(
            CtApplicationPUG.application == app_id).all()
        group_name = u'Бүлэгт хамаарахгүй'
        group_no = None
        for app_group in app_pug:
            group_member_count = self.session.query(CtGroupMember).filter(CtGroupMember.group_no == app_group.group_no). \
                filter(CtGroupMember.person == person.person_id).count()
            if group_member_count == 1:
                group = self.session.query(CtPersonGroup).filter(CtPersonGroup.group_no == app_group.group_no).one()
                group_name = group.group_name
                group_no = group.group_no
        return group_name

    @pyqtSlot()
    def on_print_contract_button_clicked(self):

        self.__contract_possess()
    #
    # def __admin_settings(self, table_name):
    #
    #     session = SessionHandler().session_instance()
    #     lookup = {}
    #     l2_code = DatabaseUtils.working_l2_code()
    #     try:
    #         sql = "SELECT * FROM " + "s" + l2_code + ".{0};".format(table_name)
    #         result = session.execute(sql).fetchall()
    #         for row in result:
    #             lookup[row[0]] = row[1]
    #
    #     except exc.SQLAlchemyError, e:
    #         PluginUtils.show_error(self, self.tr("SQL Error"), e.message)
    #
    #     return lookup

    @pyqtSlot()
    def on_print_soil_qual_pass_edit_clicked(self):

        current_file = os.path.dirname(__file__) + "/.." + "/pentaho/contract_soil_qual_pass.prpt"
        QDesktopServices.openUrl(QUrl.fromLocalFile(current_file))

    @pyqtSlot(QModelIndex)
    def on_conditions_tree_clicked(self, index):

        item = self.item_model.itemFromIndex(index)
        self.preview_text_edit.clear()
        self.__show_preview(item)

    @pyqtSlot()
    def on_help_button_clicked(self):

        if self.tab_widget.currentIndex() == 0:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/contract_application.htm")
        elif self.tab_widget.currentIndex() == 1:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/contract_parcel.htm")
        elif self.tab_widget.currentIndex() == 2:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/contract_contract_details.htm")
        elif self.tab_widget.currentIndex() == 3:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/contract_conditions.htm")
        elif self.tab_widget.currentIndex() == 4:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/contract_landfee.htm")
        elif self.tab_widget.currentIndex() == 5:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/contract_landfee_history.htm")
        elif self.tab_widget.currentIndex() == 6:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/contract_documents.htm")
        elif self.tab_widget.currentIndex() == 7:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/contract_application_document.htm")
        elif self.tab_widget.currentIndex() == 8:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/contract_prints.htm")

    #public functions
    def current_create_application(self):

        try:
            con_app_roles = self.contract.application_roles\
                    .filter(CtContractApplicationRole.role == ConstantsPasture.APPLICATION_ROLE_CREATES).one()

        except LM2Exception, e:
                PluginUtils.show_error(self, e.title(), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return

        return con_app_roles.application_ref

    def current_parent_object(self):

        return self.contract

    def current_parent_object_no(self):

        return self.contract_num_edit.text()

    @pyqtSlot(str)
    def on_person_id_edit_textChanged(self, text):

        self.app_number_cbox.clear()
        value = "%" + text + "%"

        application = self.session.query(CtApplication)\
            .join(CtApplicationPersonRole, CtApplication.app_id == CtApplicationPersonRole.application)\
            .join(BsPerson, CtApplicationPersonRole.person == BsPerson.person_id)\
            .filter(BsPerson.person_id.ilike(value)).all()

        for app in application:
            self.app_no = app.app_no
            self.app_number_cbox.addItem(self.app_no, self.app_no)

    @pyqtSlot(bool)
    def on_cancelled_rbutton_toggled(self, state):

        if state:
            try:
                contract_apps = self.session.query(CtContractApplicationRole).\
                    filter(CtContractApplicationRole.contract == self.contract.contract_id).all()
                for contract_app in contract_apps:
                    mortgage_count = self.session.query(CtApp8Ext).\
                        filter(CtApp8Ext.app_id == contract_app.application).count()
                    if mortgage_count > 0:
                        mortgage = self.session.query(CtApp8Ext).\
                        filter(CtApp8Ext.app_id == contract_app.application).one()
                        today = date.today()
                        mortgage_date = mortgage.end_mortgage_period
                        if today < mortgage_date:
                            self.apply_button.setEnabled(False)
                            PluginUtils.show_message(self, self.tr("Mortgage"), self.tr("The Contract can not cancel. it is relating to the mortgage."))
                            return
            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return
        else:
            self.apply_button.setEnabled(True)

    @pyqtSlot(bool)
    def on_expired_rbutton_toggled(self, state):

        if self.contract.status == ConstantsPasture.CONTRACT_STATUS_EXPIRED:
            if not state and self.cancelled_rbutton.isChecked() == False:
                PluginUtils.show_message(self, self.tr('Expired contracts'), self.tr('Expired contracts!'))
                self.expired_rbutton.setChecked(True)
                return