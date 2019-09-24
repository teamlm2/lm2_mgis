# coding=utf8

__author__ = 'B.Ankhbold'

from types import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from qgis.core import *
from qgis.gui import *
from sqlalchemy import func, or_, and_, desc,extract
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
from sqlalchemy.sql import exists
from datetime import date, datetime, timedelta
from inspect import currentframe
import os
import types
import textwrap
import win32api
import win32net
import win32netcon,win32wnet
from ..utils.FileUtils import FileUtils
from ..model.LM2Exception import LM2Exception
from ..model.ClApplicationStatus import ClApplicationStatus
from ..model.BsPerson import *
from ..model.ClPersonRole import *
from ..model.ClPositionType import *
from ..model.ClPastureType import *
from ..model.CtContractApplicationRole import *
from ..model.CtRecordApplicationRole import *
from ..model.CtApplicationStatus import *
from ..model.CtOwnershipRecord import *
from ..model.CaTmpParcel import *
from ..model.CaPastureParcel import *
from ..model.CaPUGBoundary import *
from ..model.CtDecision import *
from ..model.CtDecisionApplication import *
from ..model.SetRightTypeApplicationType import *
from ..model.ClPastureDocument import *
from ..model.SetPastureDocument import *
from ..model.SetPersonTypeApplicationType import *
from ..model.SetApplicationTypeLanduseType import *
from ..model.CaSpaParcelTbl import *
from ..model.SetValidation import *
from ..model.DatabaseHelper import *
from ..model.AuLevel3 import *
from ..model import SettingsConstants
from ..model import ConstantsPasture
from ..model.AuLevel1 import *
from ..model.AuLevel2 import *
from ..model.MaintenanceSearch import *
from ..model.ClPersonType import *
from ..model.EnumerationsPasture import ApplicationType, UserRight
from ..model.Enumerations import PersonType
from ..model.CtPersonGroup import *
from ..model.CtApplicationPUG import *
from ..model.CtApplicationPUGParcel import *
from ..model.CtApplicationParcelPasture import *
from ..model.CtGroupMember import *
from ..model.CtAppGroupBoundary import *
from ..model.SetApplicationTypeDocumentRole import *
from ..model.ClRightType import *
from ..model.ClParcelType import *
from ..model.SetApplicationTypeParcelType import *
from ..model.CtApplicationParcel import *
from .qt_classes.PastureApplicationDocumentDelegate import PastureApplicationDocumentDelegate
from .qt_classes.DocumentsTableWidget import DocumentsTableWidget
from .qt_classes.DragTableWidget import DragTableWidget
from .qt_classes.DragTreeWidget import DragTreeWidget
from .qt_classes.DoubleSpinBoxDelegate import DoubleSpinBoxDelegate
from .qt_classes.DropLabel import DropLabel
from .qt_classes.ComboBoxDelegate import *
from .qt_classes.IntegerSpinBoxDelegate import *
from ..view.Ui_ApplicationsSpaDialog import *
from ..model.PersonSearch import *
from ..model.BsPerson import *
from ..model.SdPosition import *
from ..model.SdUser import *
from ..model.SdAutoNumbers import *
from ..model.SdConfiguration import *
from ..model.SdFtpConnection import *
from ..model.SdFtpPermission import *
from ..model.SdEmployee import *
from ..model.SdDepartment import *
from ..model.CaPastureParcelTbl import *
from ..model.ClPersonGroupType import *
from ..model.ClSpaType import *
from ..model.ClSpaMood import *
from ..utils.SessionHandler import SessionHandler
from ..utils.PluginUtils import PluginUtils
from ..utils.DatabaseUtils import DatabaseUtils
from ..utils.PasturePath import *
from ..utils.LayerUtils import *

DOC_PROVIDED_COLUMN = 0
DOC_FILE_TYPE_COLUMN = 1
DOC_FILE_NAME_COLUMN = 2
DOC_OPEN_FILE_COLUMN = 3
DOC_DELETE_COLUMN = 4
DOC_VIEW_COLUMN = 5
DOC_VIEW_COLUMN = 5
MORTGAGE_SHARE = 0
MORTGAGE_PERSON_ID = 1
MORTGAGE_NAME = 2
MORTGAGE_SURNAME = 3
MORTGAGE_BEGIN = 4
MORTGAGE_END = 5
MORTGAGE_TYPE = 6
APPLICANT_MAIN = 0
APPLICANT_SHARE = 1
APPLICANT_PERSON_ID = 2
APPLICANT_SURNAME = 3
APPLICANT_FIRST_NAME = 4
LEGAL_REP_PERSON_ID = 0
LEGAL_REP_SURNAME = 1
LEGAL_REP_FIRST_NAME = 2
LEGAL_REP_AGE = 3
NEW_RIGHT_HOLDER_MAIN = 0
OLD_RIGHT_HOLDER_SHARE = 0
NEW_RIGHT_HOLDER_SHARE = 1
NEW_RIGHT_HOLDER_PERSON_ID = 2
NEW_RIGHT_HOLDER_SURNAME = 3
NEW_RIGHT_HOLDER_FIRST_NAME = 4
STATUS_STATE = 0
STATUS_DATE = 1
STATUS_OFFICER = 2
STATUS_NEXT_OFFICER = 3
CO_OWNERSHIP_MAIN = 0
CO_OWNERSHIP_PERSON_ID = 1
CO_OWNERSHIP_SURNAME = 2
CO_OWNERSHIP_FIRST_NAME = 3


class ApplicationsSpaDialog(QDialog, Ui_ApplicationsSpaDialog, DatabaseHelper):

    def __init__(self, plugin,application, navigator, attribute_update=False, parent=None):

        super(ApplicationsSpaDialog, self).__init__(parent)
        DatabaseHelper.__init__(self)
        self.plugin = plugin
        self.navigator = navigator
        self.attribute_update = attribute_update

        self.session = SessionHandler().session_instance()
        self.application = application

        self.timer = None
        self.last_row = None
        self.last_tab = -1
        self.updating = False

        self.person_name_model = None
        self.person_name_proxy_model = None
        self.person_name_completer = None

        self.person_register_model = None
        self.person_register_proxy_model = None
        self.person_register_completer = None

        self.applicant_twidget = None
        self.documents_twidget = None
        self.person = None
        self.is_tmp_parcel = False
        self.setupUi(self)
        self.close_button.clicked.connect(self.reject)

        self.__setup_validators()
        self.__setup_combo_boxes()
        self.__setup_ui()
        self.__setup_permissions()

    #public functions

    def __setup_validators(self):

        self.int_validator = QRegExpValidator(QRegExp("[0-9]+"), None)

    def __set_up_twidget(self, table_widget):

        table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = table_widget.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)

    def current_document_applicant(self):

        applicant = self.applicant_documents_cbox.itemData(self.applicant_documents_cbox.currentIndex())
        return applicant

    def current_application(self):

        return self.application

    def current_application_no(self):
        app_no = self.application_num_first_edit.text() + "-" + self.application_num_type_edit.text() + "-" \
                     + self.application_num_middle_edit.text() + "-" + self.application_num_last_edit.text()

        return app_no
    #end public functions

    def __setup_ui(self):

        self.share_spinbox = QDoubleSpinBox()
        self.share_spinbox.setDecimals(2)
        self.share_spinbox.setMaximum(1.0)
        self.share_spinbox.setValue(1.0)
        self.share_spinbox.setSingleStep(0.1)

        self.status_date_date.setDate(QDate().currentDate())

        self.drop_label = DropLabel("parcel", self.search_group_box)
        self.drop_label.itemDropped.connect(self.on_drop_label_itemDropped)

        if self.attribute_update:
            self.__setup_mapping()
        else:
            self.date_time_date.setDateTime(QDateTime.currentDateTime())

        try:
            self.__setup_status_widget()
            self.__setup_documents_twidget()
            self.__setup_applicant_twidget()
            self.__setup_parcel()

        except LM2Exception, e:
            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

    def __setup_mapping(self):

        try:
            status_count = self.session.query(CtApplicationStatus)\
                .filter(CtApplication.app_no == self.application.app_no)\
                .filter(CtApplicationStatus.status >= 5).count()
            if status_count > 0:
                self.requested_land_use_type_cbox.setEnabled(False)

        except SQLAlchemyError, e:
            self.rollback_to_savepoint()
            raise LM2Exception(self.tr("Database Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
        # details
        python_date = self.application.app_timestamp
        app_date = PluginUtils.convert_python_datetime_to_qt(python_date)
        self.date_time_date.setDateTime(app_date)

        self.application_type_cbox.setCurrentIndex(self.application_type_cbox.findData(self.application.app_type))
        self.application_type_cbox.setEnabled(False)
        self.approved_land_use_type_cbox.setCurrentIndex(self.approved_land_use_type_cbox.findData(self.application.approved_landuse))
        self.requested_land_use_type_cbox.setCurrentIndex(self.requested_land_use_type_cbox.findData(self.application.requested_landuse))

        rigth_types = self.session.query(ClRightType).all()
        for item in rigth_types:
            self.rigth_type_cbox.addItem(item.description, item.code)

        if self.application.requested_duration:
            self.requested_year_spin_box.setValue(self.application.requested_duration)

        if self.application.approved_duration:
            self.approved_year_spin_box.setValue(self.application.approved_duration)

        self.remarks_text_edit.setText(self.application.remarks)

        # App_no + Soum + Landuse
        app_no = self.application.app_no
        parts_app_no = app_no.split("-")

        self.application_num_first_edit.setText(parts_app_no[0])
        self.application_num_type_edit.setText(parts_app_no[1])
        self.application_num_middle_edit.setText(parts_app_no[2])
        self.application_num_last_edit.setText(parts_app_no[3])

    def __setup_parcel(self):

        app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())
        app_parcel_count = self.session.query(CtApplicationParcel).filter(CtApplicationParcel.app_id == self.application.app_id).count()
        if app_parcel_count == 1:
            app_parcel = self.session.query(CtApplicationParcel).filter(
                CtApplicationParcel.app_id == self.application.app_id).one()
            if app_parcel.parcel_type:
                current_parcel_type = app_parcel.parcel_type
                parcel_type = self.session.query(ClParcelType).filter(ClParcelType.code == current_parcel_type).one()
                parcel_table_name = str(parcel_type.table_name)
                if app_parcel.parcel_id:
                    parcel_id = app_parcel.parcel_id
                    sql = "select parcel_id, area_m2 from " + parcel_table_name + " where parcel_id = " + "'" + parcel_id + "'"
                    values = self.session.execute(sql).fetchall()
                    for row in values:
                        parcel_id = row[0]
                        area_m2 = str(row[1])
                        self.parcel_edit.setText(parcel_id)
                        self.parcel_area_edit.setText(area_m2)

                    count = self.session.query(CaSpaParcelTbl).filter(CaSpaParcelTbl.parcel_id == parcel_id).count()
                    if count == 1:
                        spa_parcel = self.session.query(CaSpaParcelTbl).filter(
                            CaSpaParcelTbl.parcel_id == parcel_id).one()
                        if spa_parcel.spa_type:
                            self.spa_type_cbox.setCurrentIndex(self.spa_type_cbox.findData(spa_parcel.spa_type))
                        if spa_parcel.spa_mood:
                            self.spa_mood_cbox.setCurrentIndex(self.spa_mood_cbox.findData(spa_parcel.spa_mood))

    def __setup_permissions(self):

        user_name = QSettings().value(SettingsConstants.USER)
        user_rights = DatabaseUtils.userright_by_name(user_name)

        if UserRight.application_update in user_rights:
            self.apply_button.setEnabled(True)
            self.applicant_twidget.setAcceptDrops(True)
            self.documents_twidget.setEnabled(True)
            self.apply_button.setEnabled(True)
            self.appliciants_remove_button.setEnabled(True)
        else:
            self.applicant_twidget.setAcceptDrops(False)
            self.documents_twidget.setEnabled(False)
            self.apply_button.setEnabled(False)
            self.appliciants_remove_button.setEnabled(False)

    def __setup_applicant_twidget(self):

        self.applicant_twidget = DragTableWidget("person", 20, 150, 720, 180, self.applicants_group_box)

        header = [self.tr("Main Applicant"),
                  self.tr("Share [0.0 - 1.0]"),
                  self.tr("Personal/Company ID"),
                  self.tr("Surname/Company"),
                  self.tr("First Name")]

        self.applicant_twidget.setup_header(header)
        delegate = DoubleSpinBoxDelegate(APPLICANT_SHARE, 0, 1, 1, 0.1, self.applicant_twidget)
        self.applicant_twidget.setItemDelegateForColumn(APPLICANT_SHARE, delegate)
        self.applicant_twidget.cellChanged.connect(self.on_application_twidget_cellChanged)

        # try:
        applicants = self.application.stakeholders.filter(
            CtApplicationPersonRole.role == Constants.APPLICANT_ROLE_CODE).all()

        # except SQLAlchemyError, e:
        #     raise LM2Exception(self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

        for applicant in applicants:
            self.__add_applicant_item(applicant)

    def __setup_status_widget(self):

        self.application_status_twidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.application_status_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.application_status_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.application_status_twidget.setSortingEnabled(True)

        for status in self.application.statuses:
            self.__add_application_status_item(status)

        self.application_status_twidget.sortItems(0, Qt.AscendingOrder)

    def __setup_documents_twidget(self):

        self.documents_twidget = DocumentsTableWidget(self.documents_group_box)
        delegate = PastureApplicationDocumentDelegate(self.documents_twidget, self)
        self.documents_twidget.setItemDelegate(delegate)

    def __setup_combo_boxes(self):

        l2_code = DatabaseUtils.working_l2_code()

        if l2_code == -1 or not l2_code:
            return

        database_name = QSettings().value(SettingsConstants.DATABASE_NAME)
        user_code = database_name.split('_')[1]
        user_start = 'user' + user_code

        try:
            rigth_types = self.session.query(ClRightType).all()

            application_types = self.session.query(ClApplicationType).\
                filter(or_(ClApplicationType.code == ApplicationType.spa_parcel, ClApplicationType.code == ApplicationType.state_parcel)).\
                order_by(ClApplicationType.code).all()
            statuses = self.session.query(ClApplicationStatus).order_by(ClApplicationStatus.code).all()
            # set_roles = self.session.query(SetRole). \
            #     filter(SetRole.user_name.startswith(user_start)).all()
            set_roles = self.session.query(SetRole). \
                filter(SetRole.is_active == True).all()
            landuse_types = self.session.query(ClLanduseType).all()

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

        for item in rigth_types:
            self.rigth_type_cbox.addItem(item.description, item.code)
        self.rigth_type_cbox.setCurrentIndex(self.rigth_type_cbox.findData(4))

        # for item in application_types:
        #     self.application_type_cbox.addItem(item.description, item.code)

        for status in statuses:
            self.status_cbox.addItem(status.description, status.code)

        soum_code = DatabaseUtils.working_l2_code()
        for setRole in set_roles:
            l2_code_list = setRole.restriction_au_level2.split(',')
            if soum_code in l2_code_list:
                sd_user = self.session.query(SdUser).filter(SdUser.gis_user_real == setRole.user_name_real).first()
                lastname = ''
                firstname = ''
                if sd_user:
                    lastname = sd_user.lastname
                    firstname = sd_user.firstname
                    self.next_officer_in_charge_cbox.addItem(lastname + ", " + firstname, sd_user.user_id)

        persontype_list = self.session.query(ClPersonType).all()

        for personType in persontype_list:
            self.person_type_cbox.addItem(personType.description, personType.code)
        self.person_type_cbox.setCurrentIndex(self.person_type_cbox.findData(40))
        # for item in landuse_types:
        #     self.approved_land_use_type_cbox.addItem(str(item.code) + ": " + item.description, item.code)

        spa_types = self.session.query(ClSpaType).all()
        spa_moods = self.session.query(ClSpaMood).all()

        for value in spa_types:
            self.spa_type_cbox.addItem(value.description, value.code)

        for value in spa_moods:
            self.spa_mood_cbox.addItem(value.description, value.code)

    def __validity_of_application(self):

        valid = True
        error_message = self.tr("The application can't be saved. The following errors have been found: ")

        if self.application_type_cbox.currentIndex() == -1:
            self.application_type_cbox.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            valid = False
            app_type_error = self.tr("Missing Application type.")
            error_message = error_message + "\n \n" + app_type_error

        if self.date_time_date.date() == "":
            self.date_time_date.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            date_time_error = self.tr("Missing timestamp for Application.")
            error_message = error_message + "\n \n" + date_time_error
            valid = False

        if self.applicant_twidget.rowCount() == 0:
            self.applicant_twidget.setStyleSheet(Constants.ERROR_TWIDGET_STYLESHEET)
            applicants_error = self.tr("Missing applicants. ")
            error_message = error_message + "\n \n" + applicants_error
            valid = False

        if not self.__check_main_capable_applicant() and self.application.app_type == 3:
            self.applicant_twidget.setStyleSheet(Constants.ERROR_TWIDGET_STYLESHEET)
            applicants_error = self.tr("In uncapable person should be main.")
            error_message = error_message + "\n \n" + applicants_error
            valid = False

        if not self.__check_main_applicant():
            self.applicant_twidget.setStyleSheet(Constants.ERROR_TWIDGET_STYLESHEET)
            applicants_error = self.tr("Exactly one main applicant has to be defined.")
            error_message = error_message + "\n \n" + applicants_error
            valid = False

        if not self.__check_share(self.applicant_twidget, APPLICANT_SHARE):

            self.applicant_twidget.setStyleSheet(Constants.ERROR_TWIDGET_STYLESHEET)
            self.applicant_twidget.setStyleSheet(Constants.ERROR_TWIDGET_STYLESHEET)
            error_convert_share = self.tr("The share value is not a valid numerial. "
                                          "\n The share should be between 0.0 and 1.0 with one precision.")
            error_message = error_message + "\n \n" + error_convert_share
            valid = False

        if not self.__check_share_sum(self.applicant_twidget, APPLICANT_SHARE):
            self.applicant_twidget.setStyleSheet(Constants.ERROR_TWIDGET_STYLESHEET)
            error_share = self.tr("The sum of the applicants share is larger than 1.0 .")
            error_message = error_message + "\n \n" + error_share
            valid = False

        return valid, error_message

    def __check_age_applicants(self, person_id):

        if self.person.type == 10 or self.person.type == 20:
            self.is_age_18 = None
            today = date.today()
            t_y = today.year
            t_m = today.month
            t_d = today.day
            person = self.session.query(BsPerson).filter(BsPerson.person_id == person_id).one()

            birthday = person.date_of_birth
            if not birthday:
                return True
            b_y = int(birthday.year)
            b_m = int(birthday.month)
            b_d = int(birthday.day)
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

    def __check_main_capable_applicant(self):

        count = 0
        for row in range(self.applicant_twidget.rowCount()):
            item_main = self.applicant_twidget.item(row, APPLICANT_MAIN)
            if item_main.checkState() == Qt.Checked:
                person_id = item_main.data(Qt.UserRole)
                person = self.session.query(BsPerson).filter(BsPerson.person_id == person_id).one()
                if person.type == 20:
                    return True
                else:
                    return False
                count += 1

        if count <> 1:
            return False
        else:
            return True

    def __check_main_age_applicant(self):

        count = 0
        for row in range(self.applicant_twidget.rowCount()):
            item_main = self.applicant_twidget.item(row, APPLICANT_MAIN)
            if item_main.checkState() == Qt.Checked:
                person_id = item_main.data(Qt.UserRole)
                person = self.session.query(BsPerson).filter(BsPerson.person_id == person_id).one()
                if not self.__check_age_applicants(person_id) and person.type == 20:
                    return False
                count += 1

        if count <> 1:
            return False
        else:
            return True

    def __check_share_age_applicants(self):

        sum_share = Decimal(0.0)

        for row in range(self.applicant_twidget.rowCount()):
            item_share = self.applicant_twidget.item(row, APPLICANT_SHARE)
            item_main = self.applicant_twidget.item(row, APPLICANT_MAIN)
            person_id = item_main.data(Qt.UserRole)
            person = self.session.query(BsPerson).filter(BsPerson.person_id == person_id).one()
            if not self.__check_age_applicants(person_id) and person.type == 20:
                sum_share = sum_share + Decimal(item_share.text())
                if sum_share != Decimal(0.0):
                    return False
        return True

    def __check_share_applicants(self):

        sum_share = Decimal(0.0)

        for row in range(self.applicant_twidget.rowCount()):
            item_share = self.applicant_twidget.item(row, APPLICANT_SHARE)
            sum_share = sum_share + Decimal(item_share.text())

        if sum_share != Decimal(1.0):
            return False

        return True

    def __check_main_applicant(self):

        count = 0
        for row in range(self.applicant_twidget.rowCount()):
            item_main = self.applicant_twidget.item(row, APPLICANT_MAIN)
            if item_main.checkState() == Qt.Checked:
                count += 1

        if count <> 1:
            return False
        else:
            return True

    def __check_share(self, twidget, share_column):

        for row in range(twidget.rowCount()):
            item_share = twidget.item(row, share_column)

            try:
                Decimal(item_share.text())
            except ValueError:
                return False

        return True

    def __check_share_sum(self, twidget, column):

        share_all = 0

        for row in range(twidget.rowCount()):
            item_share = twidget.item(row, column)
            try:
                share = Decimal(item_share.text())
            except ValueError:
                return False

            share_all = share_all + share

        if share_all > Decimal(1.0):
            return False
        else:
            return True

    def __remove_style_sheet(self):

        dialog_style = self.styleSheet()
        self.application_num_middle_edit.setStyleSheet(dialog_style)
        self.application_type_cbox.setStyleSheet(dialog_style)
        self.date_time_date.setStyleSheet(dialog_style)
        self.applicant_twidget.setStyleSheet(dialog_style)

    def __remove_document_items(self):

        if not self.documents_twidget:
            return

        while self.documents_twidget.rowCount() > 0:
            self.documents_twidget.removeRow(0)

    @pyqtSlot()
    def on_search_parcel_number_button_clicked(self):

        if self.search_parcel_num_edit.text() == "":
            return
        soum_code = DatabaseUtils.working_l2_code()
        parcel_id = self.search_parcel_num_edit.text()

        current_parcel_type = self.parcel_type_cbox.itemData(self.parcel_type_cbox.currentIndex())

        parcel_type = self.session.query(ClParcelType).filter(ClParcelType.code == current_parcel_type).one()

        parcel_table_name = str(parcel_type.table_name)

        sql = "select count(*) from " +  parcel_table_name + " parcel " \
              "join admin_units.au_level2 au2 on public.st_intersects(parcel.geometry, au2.geometry) " \
              "where parcel.parcel_id = " + "'" + parcel_id + "' and au2.code = " + "'" + soum_code + "'"

        values = self.session.execute(sql).fetchall()
        count = 0
        for row in values:
            count = row[0]

        if count == 0:
            PluginUtils.show_error(self, self.tr("No Parcel found"),
                            self.tr("The parcel number {0} could not be found within the current working soum.")
                            .format(parcel_id))
            return
        else:
            sql = "select parcel_id from " + parcel_table_name + " where parcel_id = " + "'" + parcel_id + "'"
            values = self.session.execute(sql).fetchall()
            for row in values:
                parcel_id = row[0]
                self.found_parcel_number_edit.setText(parcel_id)

    @pyqtSlot()
    def on_accept_parcel_number_button_clicked(self):

        app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())
        current_parcel_type = self.parcel_type_cbox.itemData(self.parcel_type_cbox.currentIndex())
        parcel_type = self.session.query(ClParcelType).filter(ClParcelType.code == current_parcel_type).one()
        parcel_table_name = str(parcel_type.table_name)

        parcel_id = self.found_parcel_number_edit.text()
        app_id = self.application.app_id

        if parcel_id == "":
            return

        count = self.session.query(CtApplicationParcel).filter(CtApplicationParcel.app_id == app_id).count()
        if count > 0:
            PluginUtils.show_error(self, u'Анхааруулга',
                                   u'Энэ өргөдөл нэгж талбартай холбогдсон байна!')
            return
        else:
            app_parcel = CtApplicationParcel()
            app_parcel.app_id = app_id
            app_parcel.parcel_id = parcel_id
            app_parcel.parcel_type = current_parcel_type
            self.session.add(app_parcel)
            self.session.flush()
            if app_type == ApplicationType.spa_parcel:
                spa_mood = self.spa_mood_cbox.itemData(self.spa_mood_cbox.currentIndex())
                spa_type = self.spa_mood_cbox.itemData(self.spa_type_cbox.currentIndex())
                count = self.session.query(CaSpaParcelTbl).filter(CaSpaParcelTbl.parcel_id == parcel_id).count()
                if count == 1:
                    spa_parcel = self.session.query(CaSpaParcelTbl).filter(CaSpaParcelTbl.parcel_id == parcel_id).one()
                    spa_parcel.spa_mood = spa_mood
                    spa_parcel.spa_type = spa_type

            sql = "select parcel_id, area_m2 from " + parcel_table_name + " where parcel_id = " + "'" + parcel_id + "'"
            values = self.session.execute(sql).fetchall()
            for row in values:
                parcel_id = row[0]
                area_m2 = str(row[1])
                self.parcel_edit.setText(parcel_id)
                self.parcel_area_edit.setText(area_m2)

    def __save_parcel(self):

        app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())
        parcel_id = self.parcel_edit.text()

        if parcel_id == "":
            return

        if app_type == ApplicationType.spa_parcel:
            spa_mood = self.spa_mood_cbox.itemData(self.spa_mood_cbox.currentIndex())
            spa_type = self.spa_mood_cbox.itemData(self.spa_type_cbox.currentIndex())
            count = self.session.query(CaSpaParcelTbl).filter(CaSpaParcelTbl.parcel_id == parcel_id).count()
            if count == 1:
                spa_parcel = self.session.query(CaSpaParcelTbl).filter(CaSpaParcelTbl.parcel_id == parcel_id).one()
                spa_parcel.spa_mood = spa_mood
                spa_parcel.spa_type = spa_type

    @pyqtSlot()
    def on_unassign_button_clicked(self):

        app_id = self.application.app_id
        self.session.query(CtApplicationParcel).filter(CtApplicationParcel.app_id == app_id).delete()

        self.parcel_edit.setText("")
        self.parcel_area_edit.setText("")
        self.accept_parcel_number_button.setEnabled(True)

    @pyqtSlot(int)
    def on_applicant_documents_cbox_currentIndexChanged(self, index):

        if not self.documents_twidget:
            return

        if self.updating:
            return

        # self.__update_documents_twidget()

    def __update_documents_twidget(self):

        self.__remove_document_items()

        current_app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())

        try:
            required_doc_types = self.session.query(SetApplicationTypeDocumentRole).filter_by(
                application_type=current_app_type)

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

        person_id = self.applicant_documents_cbox.itemData(self.applicant_documents_cbox.currentIndex())

        for docType in required_doc_types:
            item_provided = QTableWidgetItem()
            item_provided.setCheckState(Qt.Unchecked)

            item_doc_type = QTableWidgetItem(docType.document_role_ref.description)
            item_doc_type.setData(Qt.UserRole, docType.document_role_ref.code)
            item_doc_type.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            item_name = QTableWidgetItem("")
            item_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            item_open = QTableWidgetItem("")
            item_remove = QTableWidgetItem("")
            item_view = QTableWidgetItem("")
            row = self.documents_twidget.rowCount()

            self.documents_twidget.insertRow(row)
            self.documents_twidget.setItem(row, DOC_PROVIDED_COLUMN, item_provided)
            self.documents_twidget.setItem(row, DOC_FILE_TYPE_COLUMN, item_doc_type)
            self.documents_twidget.setItem(row, DOC_FILE_NAME_COLUMN, item_name)
            self.documents_twidget.setItem(row, DOC_OPEN_FILE_COLUMN, item_open)
            self.documents_twidget.setItem(row, DOC_DELETE_COLUMN, item_remove)
            self.documents_twidget.setItem(row, DOC_VIEW_COLUMN, item_view)

        app_docs = self.session.query(CtApplicationDocument.role, CtApplicationDocument.person, CtApplicationDocument.document)\
            .filter(CtApplicationDocument.application_ref == self.application).all()

        for app_document in app_docs:
            for i in range(self.documents_twidget.rowCount()):
                doc_type_item = self.documents_twidget.item(i, DOC_FILE_TYPE_COLUMN)
                if app_document.role == doc_type_item.data(Qt.UserRole) and app_document.person == person_id:
                    try:
                        item_name = self.documents_twidget.item(i, DOC_FILE_NAME_COLUMN)
                        document = self.session.query(CtDocument.name).filter(CtDocument.id == app_document.document).one()
                        item_name.setText(document.name)

                        item_provided = self.documents_twidget.item(i, DOC_PROVIDED_COLUMN)
                        item_provided.setCheckState(Qt.Checked)

                        item_open = self.documents_twidget.item(i, DOC_OPEN_FILE_COLUMN)

                        self.documents_twidget.setItem(i, 0, item_provided)
                        self.documents_twidget.setItem(i, 2, item_name)
                        self.documents_twidget.setItem(i, 3, item_open)

                    except SQLAlchemyError, e:
                        PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                        return

    def __update_documents_file_twidget(self):

        app_docs = self.session.query(CtApplicationDocument).filter(
            CtApplicationDocument.application_id == self.application.app_id).all()
        for app_doc in app_docs:
            document_count = self.session.query(CtDocument).filter(CtDocument.id == app_doc.document_id).count()
            if document_count == 1:
                document = self.session.query(CtDocument).filter(CtDocument.id == app_doc.document_id).one()
                for i in range(self.documents_twidget.rowCount()):
                    doc_type_item = self.documents_twidget.item(i, DOC_FILE_TYPE_COLUMN)
                    doc_type_code = doc_type_item.data(Qt.UserRole)
                    # if len(str(doc_type_item.data(Qt.UserRole))) == 1:
                    #     doc_type_code = '0' + str(doc_type_item.data(Qt.UserRole))

                    if app_doc.role == doc_type_code:
                        item_name = self.documents_twidget.item(i, DOC_FILE_NAME_COLUMN)
                        item_name.setText(document.name)

                        item_provided = self.documents_twidget.item(i, DOC_PROVIDED_COLUMN)
                        item_provided.setCheckState(Qt.Checked)

                        item_open = self.documents_twidget.item(i, DOC_OPEN_FILE_COLUMN)

                        self.documents_twidget.setItem(i, 0, item_provided)
                        self.documents_twidget.setItem(i, 2, item_name)
                        self.documents_twidget.setItem(i, 3, item_open)

        self.documents_twidget.resizeColumnsToContents()

    @pyqtSlot()
    def on_load_doc_button_clicked(self):

        ftp = DatabaseUtils.ftp_connect()
        if not ftp:
            return

        # self.documents_twidget.clear()
        self.__remove_document_items()
        current_app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())
        try:
            required_doc_types = self.session.query(SetApplicationTypeDocumentRole).filter_by(
                application_type=current_app_type)

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"),
                                   self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

        for docType in required_doc_types:
            item_provided = QTableWidgetItem()
            item_provided.setCheckState(Qt.Unchecked)

            item_doc_type = QTableWidgetItem(docType.document_role_ref.description)
            item_doc_type.setData(Qt.UserRole, docType.document_role_ref.code)
            item_doc_type.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            item_name = QTableWidgetItem("")
            item_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            if docType.document_role_ref.is_ubeg_required:
                item_doc_type.setBackground(Qt.yellow)
                item_doc_type.setBackground(Qt.yellow)
                item_name.setBackground(Qt.yellow)

            item_open = QTableWidgetItem("")
            item_remove = QTableWidgetItem("")
            item_view = QTableWidgetItem("")

            row = self.documents_twidget.rowCount()

            self.documents_twidget.insertRow(row)
            self.documents_twidget.setItem(row, DOC_PROVIDED_COLUMN, item_provided)
            self.documents_twidget.setItem(row, DOC_FILE_TYPE_COLUMN, item_doc_type)
            self.documents_twidget.setItem(row, DOC_FILE_NAME_COLUMN, item_name)
            self.documents_twidget.setItem(row, DOC_OPEN_FILE_COLUMN, item_open)
            self.documents_twidget.setItem(row, DOC_DELETE_COLUMN, item_remove)
            self.documents_twidget.setItem(row, DOC_VIEW_COLUMN, item_view)
        #
        self.__update_documents_file_twidget()

    @pyqtSlot(int, int)
    def on_application_twidget_cellChanged(self, row, column):

        if column == APPLICANT_MAIN:
            changed_item = self.applicant_twidget.item(row, column)
            if changed_item.checkState() == Qt.Checked:

                for cu_row in range(self.applicant_twidget.rowCount()):
                    item = self.applicant_twidget.item(cu_row, column)
                    if item.checkState() == Qt.Checked and row != cu_row:
                        item.setCheckState(Qt.Unchecked)

    @pyqtSlot()
    def on_drop_label_itemDropped(self):

        self.__copy_parcel_from_navigator()

    @pyqtSlot()
    def on_contract_drop_label_itemDropped(self):

        self.__copy_contract_from_navigator()

    @pyqtSlot()
    def on_appliciants_remove_button_clicked(self):

        app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())

        new_role = Constants.NEW_RIGHT_HOLDER_CODE
        old_role = Constants.OLD_RIGHT_HOLDER_CODE
        if app_type == 15 or app_type == 2:
            new_role = Constants.REMAINING_OWNER_CODE
            old_role = Constants.GIVING_UP_OWNER_CODE

        current_row = self.applicant_twidget.currentRow()
        person_item = self.applicant_twidget.item(current_row, 0)
        person_id = person_item.data(Qt.UserRole)

        try:
            applicant_roles = self.application.stakeholders.filter(CtApplicationPersonRole.person == person_id) \
                .filter(CtApplicationPersonRole.role == Constants.APPLICANT_ROLE_CODE).one()

            # in case of ApplicationType.giving_up_ownership
            # or in case of a Transfer (possession or ownership):
            # Remove the applicants also from the co-ownership widget

            app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())
            self.application.stakeholders.remove(applicant_roles)
            self.applicant_twidget.removeRow(current_row)

            if app_type == ApplicationType.giving_up_ownership:

                giving_count = self.application.stakeholders.filter(CtApplicationPersonRole.person == person_id) \
                    .filter(CtApplicationPersonRole.role == Constants.GIVING_UP_OWNER_CODE).count()
                remaining_count = self.application.stakeholders.filter(CtApplicationPersonRole.person == person_id) \
                    .filter(CtApplicationPersonRole.role == new_role).count()

                if giving_count > 0:
                    ownership_giving_roles = self.application.stakeholders \
                        .filter(CtApplicationPersonRole.person == person_id) \
                        .filter(CtApplicationPersonRole.role == Constants.GIVING_UP_OWNER_CODE) \
                        .one()

                    self.application.stakeholders.remove(ownership_giving_roles)
                    self.__remove_person_from_co_ownership_twidgets(person_id, Constants.GIVING_UP_OWNER_CODE)

                if remaining_count > 0:
                    ownership_remain_roles = self.application.stakeholders \
                        .filter(CtApplicationPersonRole.person == person_id) \
                        .filter(CtApplicationPersonRole.role == new_role) \
                        .one()

                    self.application.stakeholders.remove(ownership_remain_roles)
                    self.__remove_person_from_co_ownership_twidgets(person_id, new_role)

            elif app_type == ApplicationType.transfer_possession_right or app_type == ApplicationType.change_ownership \
                    or app_type == ApplicationType.possess_split or app_type == ApplicationType.encroachment \
                    or app_type == ApplicationType.possession_right_use_right:

                old_count = self.application.stakeholders.filter(CtApplicationPersonRole.person == person_id) \
                    .filter(CtApplicationPersonRole.role == old_role).count()

                if old_count > 0:
                    old_right_holders = self.application.stakeholders \
                        .filter(CtApplicationPersonRole.person == person_id) \
                        .filter(CtApplicationPersonRole.role == old_role) \
                        .all()

                    for applicant in old_right_holders:
                        self.application.stakeholders.remove(applicant)
                        self.__remove_old_right_holder(applicant.person)

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"),
                                   self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

        if self.application.stakeholders.count() > 0:
            self.application_type_cbox.setEnabled(False)
        elif not self.attribute_update:
            self.application_type_cbox.setEnabled(True)

    @pyqtSlot()
    def on_up_button_clicked(self):

        try:
            remaining_role = self.session.query(ClPersonRole).filter_by(code=Constants.REMAINING_OWNER_CODE).one()
        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

        for row in range(self.owners_giving_twidget.rowCount()):
            item = self.owners_giving_twidget.item(row, 0)

            if item is not None and item.isSelected():

                row_count = self.owners_remaining_twidget.rowCount()
                self.owners_remaining_twidget.insertRow(row_count)
                main_item = QTableWidgetItem(QIcon(), "")
                main_item.setCheckState(Qt.Unchecked)

                for column in range(self.owners_giving_twidget.columnCount()):
                    item1 = self.owners_giving_twidget.takeItem(row, column)
                    self.owners_remaining_twidget.setItem(row_count, column+1, item1)
                    self.owners_remaining_twidget.setItem(row_count, 0 , main_item)

                try:
                    applicant = self.session.query(CtApplicationPersonRole)\
                        .filter(CtApplicationPersonRole.person == item.data(Qt.UserRole))\
                        .filter(CtApplicationPersonRole.role == Constants.GIVING_UP_OWNER_CODE)\
                        .filter(CtApplicationPersonRole.application == self.application.app_id).one()

                    applicant.role = Constants.REMAINING_OWNER_CODE
                    applicant.role_ref = remaining_role
                except SQLAlchemyError, e:
                    PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                    return

                self.owners_giving_twidget.removeRow(row)

    @pyqtSlot()
    def on_down_button_clicked(self):

        try:
            giving_role = self.session.query(ClPersonRole).filter_by(code=Constants.GIVING_UP_OWNER_CODE).one()

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

        row_count = self.owners_remaining_twidget.rowCount()

        if row_count == 1:
            PluginUtils.show_message(self, self.tr("Change of co-ownership"),
                                     self.tr("At least one owner should remain."))
            return

        for row in range(self.owners_remaining_twidget.rowCount()):
            item = self.owners_remaining_twidget.item(row, 1)

            if item is not None and item.isSelected():
                row_count = self.owners_giving_twidget.rowCount()
                self.owners_giving_twidget.insertRow(row_count)

                item = self.owners_remaining_twidget.takeItem(row, 1)
                self.owners_giving_twidget.setItem(row_count, 0, item)

                item = self.owners_remaining_twidget.takeItem(row, 2)
                self.owners_giving_twidget.setItem(row_count, 1, item)

                item = self.owners_remaining_twidget.takeItem(row, 3)
                self.owners_giving_twidget.setItem(row_count, 2, item)
                # for column in range(self.owners_remaining_twidget.columnCount()):
                #     item = self.owners_remaining_twidget.takeItem(row, column)
                #     self.owners_giving_twidget.setItem(row_count, column-1, item)
                try:
                    applicant = self.application.stakeholders.filter_by(person=item.data(Qt.UserRole)).filter_by(
                        role=Constants.REMAINING_OWNER_CODE).one()
                    applicant.role = Constants.GIVING_UP_OWNER_CODE
                    applicant.role_ref = giving_role

                except SQLAlchemyError, e:
                    PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                    return

                self.owners_remaining_twidget.removeRow(row)

    @pyqtSlot(int)
    def on_application_tab_widget_currentChanged(self, current_index):

        self.last_tab = current_index

        if self.application_tab_widget.widget(current_index) == self.document_tab:
            self.__update_applicant_cbox()

    @pyqtSlot(int)
    def on_application_type_cbox_currentIndexChanged(self, index):

        app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())

        parcel_types = self.session.query(SetApplicationTypeParcelType). \
            filter(SetApplicationTypeParcelType.app_type == app_type).all()

        for value in parcel_types:
            parcel_type = value.parcel_type_ref
            self.parcel_type_cbox.addItem(parcel_type.description, parcel_type.code)

        if app_type == ApplicationType.spa_parcel:
            self.spa_gbox.show()
        else:
            self.spa_gbox.hide()

        self.__generate_application_number()

        self.__set_visible_tabs()

    @pyqtSlot()
    def on_application_status_twidget_itemSelectionChanged(self):

        current_row = self.application_status_twidget.currentRow()
        status_item = self.application_status_twidget.item(current_row, 0)

        if status_item is None:
            return

        date_item = self.application_status_twidget.item(current_row, 1)
        next_officer_item = self.application_status_twidget.item(current_row, 3)

        self.status_date_date.setDate(QDate.fromString(date_item.text(), Constants.DATE_FORMAT))
        self.status_cbox.setCurrentIndex(self.status_cbox.findData(status_item.data(Qt.UserRole)))
        self.next_officer_in_charge_cbox.setCurrentIndex(
            self.next_officer_in_charge_cbox.findData(next_officer_item.data(Qt.UserRole)))

        status = self.session.query(func.max(CtApplicationStatus.status)).\
            filter(CtApplicationStatus.application == self.application.app_id).one()
        mas_status = str(status).split(",")[0][1:]
        if mas_status == '7':
            self.add_button.setEnabled(False)
            self.update_button.setEnabled(False)
            self.delete_button.setEnabled(False)

    @pyqtSlot()
    def on_delete_button_clicked(self):

        selected_row = self.application_status_twidget.currentRow()
        status_item = self.application_status_twidget.item(selected_row, 0)

        self.create_savepoint()

        for app_status in self.application.statuses:
            if app_status.status_ref.code == status_item.data(Qt.UserRole):
                if app_status.status_ref.code == Constants.FIRST_STATUS_CODE:
                    PluginUtils.show_message(self, self.tr("Status error"), self.tr("First status can't be deleted."))
                    return
                try:
                    self.application.statuses.remove(app_status)

                except SQLAlchemyError, e:
                    self.rollback_to_savepoint()
                    PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                    return

                self.application_status_twidget.removeRow(selected_row)
                return

    @pyqtSlot()
    def on_update_button_clicked(self):

        selected_row = self.application_status_twidget.currentRow()
        if selected_row is None:
            return

        status_item = self.application_status_twidget.item(selected_row, 0)
        date_item = self.application_status_twidget.item(selected_row, 1)
        next_officer_item = self.application_status_twidget.item(selected_row, 3)
        status_code = self.status_cbox.itemData(self.status_cbox.currentIndex(), Qt.UserRole)

        if status_item is None:
            return

        for appStatus in self.application.statuses:

            if appStatus.status_ref.code == status_item.data(Qt.UserRole):

                if not self.__valid_status(status_code) \
                        and not appStatus.status_ref.code == status_code:
                    PluginUtils.show_message(self, self.tr("Status error"),
                                             self.tr("This status is already added to the application."))
                    return

                if appStatus.status_ref.code == 8:
                    PluginUtils.show_message(self, self.tr("Status error"),
                                             self.tr("This application refused by governor."))
                    return

                try:
                    self.create_savepoint()

                     #Status 1 can't be updated
                    if appStatus.status_ref.code != Constants.FIRST_STATUS_CODE:
                        status_id = self.status_cbox.itemData(self.status_cbox.currentIndex(), Qt.UserRole)
                        appStatus.status = status_id

                    index = self.next_officer_in_charge_cbox.currentIndex()
                    next_officer_user_name = self.next_officer_in_charge_cbox.itemData(index, Qt.UserRole)
                    appStatus.next_officer_in_charge = next_officer_user_name
                    python_date = PluginUtils.convert_qt_date_to_python(self.status_date_date.date())
                    appStatus.status_date = python_date
                    #self.commit()

                except SQLAlchemyError, e:
                    PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                    return

                status_item.setText(appStatus.status_ref.description)
                status_item.setData(Qt.UserRole, appStatus.status_ref.code)
                qt_date = PluginUtils.convert_python_date_to_qt(appStatus.status_date)
                date_item.setText(qt_date.toString(Constants.DATE_FORMAT))
                next_officer = appStatus.next_officer_in_charge_ref.lastname + ", " \
                               + appStatus.next_officer_in_charge_ref.firstname
                next_officer_item.setText(next_officer)
                next_officer_item.setData(Qt.UserRole, appStatus.next_officer_in_charge_ref.gis_user_real)

    def __current_sd_user(self):

        officer = self.session.query(SetRole) \
            .filter(SetRole.user_name == QSettings().value(SettingsConstants.USER)) \
            .filter(SetRole.is_active == True).one()

        sd_user = self.session.query(SdUser).filter(SdUser.gis_user_real == officer.user_name_real).first()
        return sd_user

    def __max_application_status(self):

        status = self.session.query(func.max(CtApplicationStatus.app_status_id)). \
            filter(CtApplicationStatus.application == self.application.app_id).one()
        max_status = str(status).split(",")[0][1:]
        return int(max_status)

    def __max_status_object(self):

        status = self.session.query(CtApplicationStatus).\
            filter(CtApplicationStatus.application == self.application.app_id).\
            filter(CtApplicationStatus.app_status_id == self.__max_application_status()).one()
        return status

    @pyqtSlot()
    def on_add_button_clicked(self):

        next_officer_username = self.next_officer_in_charge_cbox.itemData(
            self.next_officer_in_charge_cbox.currentIndex(), Qt.UserRole)
        status_id = self.status_cbox.itemData(self.status_cbox.currentIndex(), Qt.UserRole)

        if self.__max_status_object().next_officer_in_charge != self.__current_sd_user().user_id:
            PluginUtils.show_message(self, self.tr("Application Status"),
                                     self.tr("Permission Status!!"))
            return

        if status_id == 6:
            PluginUtils.show_message(self, self.tr("Application Status"),
                                     self.tr("First prepare draft decision for this application!!"))
            return
        if status_id == 7:
            PluginUtils.show_message(self, self.tr("Application Status"), self.tr("First register governor decision!!"))
            return

        contract_app_count = self.session.query(CtContractApplicationRole). \
            filter(CtContractApplicationRole.application == self.application.app_id).count()

        if status_id == 9:
            if contract_app_count == 0:
                PluginUtils.show_message(self, self.tr("Application Status"),
                                         self.tr("First create contract!!"))
                return

        for appStatus in self.application.statuses:
            if appStatus.status_ref.code == 8:
                PluginUtils.show_message(self, self.tr("Status error"),
                                         self.tr("This application refused by governor."))
                return

        new_status = CtApplicationStatus()

        # try:
        sd_next_officer = self.session.query(SdUser).filter(SdUser.user_id == next_officer_username).one()
        if status_id:
            status = self.session.query(ClApplicationStatus).filter_by(code=status_id).one()

        # except SQLAlchemyError, e:
        #     PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
        #     return


        check_count = self.application.statuses.filter(CtApplicationStatus.status == (status_id - 1)).count()
        status_7_count = self.application.statuses.filter(CtApplicationStatus.status == 7).count()
        if check_count == 0 and status_id != 8 and status_7_count == 0:
            PluginUtils.show_error(self, self.tr("Status error"),
                                   self.tr("Application status must be in order!."))
            return
        new_status.app_no = self.application.app_no
        new_status.officer_in_charge_ref = self.__current_sd_user()
        new_status.officer_in_charge = self.__current_sd_user().user_id
        new_status.next_officer_in_charge = sd_next_officer.user_id
        new_status.next_officer_in_charge_ref = sd_next_officer
        ui_date = self.status_date_date.date()
        # new_status.status_date = date(ui_date.year(), ui_date.month(), ui_date.day())
        new_status.status_date = self.status_date_date.dateTime().toString(Constants.DATABASE_DATETIME_FORMAT)
        new_status.status = status_id
        new_status.status_ref = status

        if not self.__valid_status(status_id):
            PluginUtils.show_error(self, self.tr("Status error"),
                                   self.tr("This status is already added to the application."))
            return

        try:
            self.application.statuses.append(new_status)

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"),
                                   self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return
        if new_status.status >= 5:
            self.requested_land_use_type_cbox.setEnabled(False)
        self.__add_application_status_item(new_status)

    @pyqtSlot(int)
    def on_rigth_type_cbox_currentIndexChanged(self, index):

        self.application_type_cbox.clear()
        rigth_code = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())

        application_types = self.session.query(ClApplicationType). \
            join(SetRightTypeApplicationType, ClApplicationType.code == SetRightTypeApplicationType.application_type). \
            filter(SetRightTypeApplicationType.right_type == rigth_code). \
            order_by(SetRightTypeApplicationType.application_type).all()

        for item in application_types:
            self.application_type_cbox.addItem(item.description, item.code)

    @pyqtSlot()
    def on_apply_button_clicked(self):

        app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())
        app_type = app_type

        # save application details
        validity_result = self.__validity_of_application()

        if not validity_result[0]:
            log_message = validity_result[1]

            PluginUtils.show_error(self, self.tr("Invalid application"), log_message)
            return

        self.__save_application()

        self.__start_fade_out_timer()

        self.attribute_update = True

    def __save_application(self):

        try:
            self.create_savepoint()

            self.__save_application_details()

            self.__save_applicants()

            self.__save_parcel()

            self.commit()

        except LM2Exception, e:
            self.rollback_to_savepoint()
            PluginUtils.show_error(self, e.title(), e.message())
            return

    def __save_application_details(self):

        self.create_savepoint()

        try:
            app_no = self.application_num_first_edit.text() + "-" + self.application_num_type_edit.text() + "-" \
                     + self.application_num_middle_edit.text() + "-" + self.application_num_last_edit.text()

            #check if the app_no is still valid, otherwise generate new one
            if not self.attribute_update:
                app_no_count = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).count()
                if app_no_count > 0:

                    self.__generate_application_number()

                    app_no = self.application_num_first_edit.text() + "-" + self.application_num_type_edit.text() + "-" \
                     + self.application_num_middle_edit.text() + "-" + self.application_num_last_edit.text()

                    PluginUtils.show_message(self, self.tr("Application Number"), self.tr("The application number was updated to the next available number."))

                soum_code = self.application_num_first_edit.text()
                app_type = self.application_num_type_edit.text()
                year = self.application_num_last_edit.text()
                # year_filter = "%-" + str(year)
                obj_type = 'application\Application'
                PluginUtils.generate_auto_app_no(year, app_type, soum_code, obj_type, self.session)

            self.application.app_no = app_no
            self.application.requested_landuse = self.requested_land_use_type_cbox.itemData(self.requested_land_use_type_cbox.currentIndex())
            #self.application.approved_landuse = self.requested_land_use_type_cbox.itemData(self.requested_land_use_type_cbox.currentIndex())
            self.application.app_timestamp = self.date_time_date.dateTime().toString(Constants.DATABASE_DATETIME_FORMAT)
            self.application.requested_duration = self.requested_year_spin_box.value()
            #self.application.approved_duration = self.approved_year_spin_box.value()
            self.application.remarks = self.remarks_text_edit.toPlainText()

            self.application.au2 = DatabaseUtils.current_working_soum_schema()
            self.application.au1 = DatabaseUtils.working_l1_code()

            rigth_type = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())
            self.application.right_type = rigth_type

            app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())
            self.application.app_type = app_type

            status = self.session.query(func.max(CtApplicationStatus.status)).\
                filter(CtApplicationStatus.application == self.application.app_id).one()
            max_status = str(status).split(",")[0][1:]


        except SQLAlchemyError, e:
            self.rollback_to_savepoint()
            raise LM2Exception(self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

    def __save_applicants(self):

        self.create_savepoint()

        for row in range(self.applicant_twidget.rowCount()):
            item = self.applicant_twidget.item(row, APPLICANT_MAIN)
            person_id = item.data(Qt.UserRole)
            main = True if item.checkState() == Qt.Checked else False

            try:
                person = self.session.query(BsPerson).filter(BsPerson.person_id == person_id).one()
                applicant_count = self.application.stakeholders.filter(
                    CtApplicationPersonRole.role == Constants.APPLICANT_ROLE_CODE) \
                    .filter(CtApplicationPersonRole.person == person_id).count()
                if applicant_count == 1:
                    applicant = self.application.stakeholders.filter(
                        CtApplicationPersonRole.role == Constants.APPLICANT_ROLE_CODE) \
                        .filter(CtApplicationPersonRole.person == person_id).one()

                    applicant.main_applicant = main
                    share_item = self.applicant_twidget.item(row, APPLICANT_SHARE)
                    if person.type == 20:
                        applicant.share = 0
                    else:
                        applicant.share = Decimal(share_item.text())
            except SQLAlchemyError, e:
                self.rollback_to_savepoint()
                raise LM2Exception(self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
        # self.__save_remaining_ownership()

    def __save_remaining_ownership(self):

        app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())
        new_role = Constants.NEW_RIGHT_HOLDER_CODE
        old_role = Constants.OLD_RIGHT_HOLDER_CODE
        if app_type == 15 or app_type == 2:
            new_role = Constants.REMAINING_OWNER_CODE
            old_role = Constants.GIVING_UP_OWNER_CODE

        self.create_savepoint()

        for row in range(self.owners_remaining_twidget.rowCount()):
            item = self.owners_remaining_twidget.item(row, 0)
            person_id = item.data(Qt.UserRole)
            if item.checkState() == Qt.Checked:
                main = True
                try:
                    count = self.application.stakeholders.filter(
                        CtApplicationPersonRole.role == new_role) \
                        .filter(CtApplicationPersonRole.person == person_id).count()
                    if count == 1:
                        applicant = self.application.stakeholders.filter(
                            CtApplicationPersonRole.role == new_role) \
                            .filter(CtApplicationPersonRole.person == person_id).one()

                        applicant.main_applicant = main
                        share_item = self.applicant_twidget.item(row, APPLICANT_SHARE)
                        if share_item:
                            applicant.share = Decimal(share_item.text())

                except SQLAlchemyError, e:
                    self.rollback_to_savepoint()
                    raise LM2Exception(self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            else:
                main = False
                # try:
                count = self.application.stakeholders.filter(
                    CtApplicationPersonRole.role == new_role) \
                    .filter(CtApplicationPersonRole.person == person_id).count()
                if count == 1:
                    applicant = self.application.stakeholders.filter(
                        CtApplicationPersonRole.role == new_role) \
                        .filter(CtApplicationPersonRole.person == person_id).one()

                    applicant.main_applicant = main
                    share_item = self.applicant_twidget.item(row, APPLICANT_SHARE)
                    if share_item:
                        applicant.share = Decimal(share_item.text())

                # except SQLAlchemyError, e:
                #     self.rollback_to_savepoint()
                #     raise LM2Exception(self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

    def __landuse_per_application_type(self, app_type):

        try:
            types = exists().where(ClLanduseType.code == SetApplicationTypeLanduseType.landuse_type)\
                            .where(SetApplicationTypeLanduseType.application_type == app_type)
            landuse_types = self.session.query(ClLanduseType).filter(types).order_by(ClLanduseType.code).all()
            landuse_count = self.session.query(ClLanduseType).filter(types).count()

            if landuse_count == 0:
                landuse_types = self.session.query(ClLanduseType).order_by(ClLanduseType.code).all()

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

        self.requested_land_use_type_cbox.clear()

        for item in landuse_types:
            self.requested_land_use_type_cbox.addItem(str(item.code) + ": " + item.description, item.code)
            self.approved_land_use_type_cbox.addItem(str(item.code) + ": " + item.description, item.code)

    def reject(self):

        self.rollback()

        if QDateTime.currentDateTime().toString("yyMMdd") in self.current_application_no():

            # when an auto-flush is executed the temp-Application is already committed
            # to the database and needs to be deleted again
            application_count = self.session.query(CtApplication.app_no).filter_by(app_id=self.application.app_id).count()
            if application_count > 0:
                self.session.query(CtApplication).filter_by(app_id=self.application.app_id).delete()

        QDialog.reject(self)

    @pyqtSlot()
    def on_contract_cancelled_accept_button_clicked(self):

        to_be_accepted_num = self.contract_cancelled_num_edit.text()
        self.contract_to_be_cancelled_edit.setText(to_be_accepted_num)

    @pyqtSlot()
    def on_reg_receipt_print_button_clicked(self):

        # current_file = os.path.dirname(__file__) + "/.." + "/pentaho/application_registration_reciept.prpt"
        # QDesktopServices.openUrl(QUrl.fromLocalFile(current_file))
        app_no = self.application_num_first_edit.text() + "-" + self.application_num_type_edit.text() + "-" \
                     + self.application_num_middle_edit.text() + "-" + self.application_num_last_edit.text()
        app_count = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).count()
        if app_count == 0:
            PluginUtils.show_error(self, self.tr("application error"), self.tr("not save"))
            return
        path = FileUtils.map_file_path()
        template = path + "app_reciept.qpt"

        templateDOM = QDomDocument()
        templateDOM.setContent(QFile(template), False)

        map_canvas = QgsMapCanvas()

        map_composition = QgsComposition(map_canvas.mapRenderer())
        map_composition.loadFromTemplate(templateDOM)

        map_composition.setPrintResolution(300)

        default_path = r'D:/TM_LM2/application_list'
        default_parent_path = r'D:/TM_LM2'
        if not os.path.exists(default_parent_path):
            os.makedirs('D:/TM_LM2')
            os.makedirs('D:/TM_LM2/application_response')
            os.makedirs('D:/TM_LM2/application_list')
            os.makedirs('D:/TM_LM2/approved_decision')
            os.makedirs('D:/TM_LM2/cad_maintenance')
            os.makedirs('D:/TM_LM2/cad_maps')
            os.makedirs('D:/TM_LM2/contracts')
            os.makedirs('D:/TM_LM2/decision_draft')
            os.makedirs('D:/TM_LM2/dumps')
            os.makedirs('D:/TM_LM2/q_data')
            os.makedirs('D:/TM_LM2/refused_decision')
            os.makedirs('D:/TM_LM2/reports')
            os.makedirs('D:/TM_LM2/training')
        if not os.path.exists(default_path):
            os.makedirs(default_path)

        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path+"/app_reciept.pdf")
        printer.setPaperSize(QSizeF(map_composition.paperWidth(), map_composition.paperHeight()), QPrinter.Millimeter)
        printer.setFullPage(True)
        printer.setColorMode(QPrinter.Color)
        printer.setResolution(map_composition.printResolution())

        pdfPainter = QPainter(printer)
        paperRectMM = printer.pageRect(QPrinter.Millimeter)
        paperRectPixel = printer.pageRect(QPrinter.DevicePixel)
        map_composition.render(pdfPainter, paperRectPixel, paperRectMM)
        pdfPainter.end()

        self.__add_aimag_name(map_composition)
        self.__add_soum_name(map_composition)
        self.__add_app_no(map_composition)
        self.__add_app_date(map_composition)
        self.__add_person_name(map_composition)
        self.__add_officer(map_composition)
        map_composition.exportAsPDF(path + "/app_reciept.pdf")
        map_composition.exportAsPDF(default_path + "/"+app_no+".pdf")
        QDesktopServices.openUrl(QUrl.fromLocalFile(default_path+"/"+app_no+".pdf"))

    @pyqtSlot()
    def on_app_return_button_clicked(self):

        app_no = self.application_num_first_edit.text() + "-" + self.application_num_type_edit.text() + "-" \
                     + self.application_num_middle_edit.text() + "-" + self.application_num_last_edit.text()
        app_count = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).count()
        if app_count == 0:
            PluginUtils.show_error(self, self.tr("application error"), self.tr("not save"))
            return
        app_status = self.session.query(CtApplicationStatus).filter(CtApplicationStatus.application == app_no).all()
        ok = 0
        for s in app_status:
            if s.status == 8:
                ok = 1

        if ok == 0:
            PluginUtils.show_error(self, self.tr("application error"), self.tr("there is no information in the remarks if application details. Application status must be 8."))
            return
        path = FileUtils.map_file_path()
        template = path + "app_return_reciept.qpt"

        templateDOM = QDomDocument()
        templateDOM.setContent(QFile(template), False)

        map_canvas = QgsMapCanvas()

        map_composition = QgsComposition(map_canvas.mapRenderer())
        map_composition.loadFromTemplate(templateDOM)

        map_composition.setPrintResolution(300)

        default_path = r'D:/TM_LM2/application_response'
        default_parent_path = r'D:/TM_LM2'
        if not os.path.exists(default_parent_path):
            os.makedirs('D:/TM_LM2')
            os.makedirs('D:/TM_LM2/application_response')
            os.makedirs('D:/TM_LM2/application_list')
            os.makedirs('D:/TM_LM2/approved_decision')
            os.makedirs('D:/TM_LM2/cad_maintenance')
            os.makedirs('D:/TM_LM2/cad_maps')
            os.makedirs('D:/TM_LM2/contracts')
            os.makedirs('D:/TM_LM2/decision_draft')
            os.makedirs('D:/TM_LM2/dumps')
            os.makedirs('D:/TM_LM2/q_data')
            os.makedirs('D:/TM_LM2/refused_decision')
            os.makedirs('D:/TM_LM2/reports')
            os.makedirs('D:/TM_LM2/training')
        if not os.path.exists(default_path):
            os.makedirs(default_path)


        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path+"app_response.pdf")
        printer.setPaperSize(QSizeF(map_composition.paperWidth(), map_composition.paperHeight()), QPrinter.Millimeter)
        printer.setFullPage(True)
        printer.setColorMode(QPrinter.Color)
        printer.setResolution(map_composition.printResolution())

        pdfPainter = QPainter(printer)
        paperRectMM = printer.pageRect(QPrinter.Millimeter)
        paperRectPixel = printer.pageRect(QPrinter.DevicePixel)
        map_composition.render(pdfPainter, paperRectPixel, paperRectMM)
        pdfPainter.end()

        self.__add_aimag_name(map_composition)
        self.__add_soum_name(map_composition)
        self.__add_app_no(map_composition)
        self.__add_app_status_date(map_composition)
        self.__add_person_name(map_composition)
        self.__add_officer_name(map_composition)
        self.__add_app_remarks(map_composition)

        map_composition.exportAsPDF(path + "app_response.pdf")
        map_composition.exportAsPDF(default_path + "/"+app_no+".pdf")
        QDesktopServices.openUrl(QUrl.fromLocalFile(default_path+"/"+app_no+".pdf"))

    def __add_aimag_name(self,map_composition):

        aimag_code = self.application_num_first_edit.text()[:3]
        try:
            aimag = self.session.query(AuLevel1).filter(AuLevel1.code == aimag_code).one()
        except SQLAlchemyError, e:
            raise LM2Exception(self.tr("Database Query Error"), self.tr("aCould not execute: {0}").format(e.message))
        item = map_composition.getComposerItemById("aimag_name")
        item.setText(aimag.name)
        item.adjustSizeToText()

    def __add_soum_name(self,map_composition):

        soum_code = self.application_num_first_edit.text()
        try:
            soum = self.session.query(AuLevel2).filter(AuLevel2.code == soum_code).one()
        except SQLAlchemyError, e:
            raise LM2Exception(self.tr("Database Query Error"), self.tr("aCould not execute: {0}").format(e.message))
        item = map_composition.getComposerItemById("soum_name")
        item.setText(soum.name)
        item.adjustSizeToText()

    def __add_app_no(self,map_composition):

        app_no = self.application_num_first_edit.text() + "-" + self.application_num_type_edit.text() + "-" \
                     + self.application_num_middle_edit.text() + "-" + self.application_num_last_edit.text()
        item = map_composition.getComposerItemById("app_no")
        item.setText(app_no)
        item.adjustSizeToText()

    def __wrap(self,text, width):
        """
        A word-wrap function that preserves existing line breaks
        and most spaces in the text. Expects that existing line
        breaks are posix newlines (\n).
        """
        return reduce(lambda line, word, width=width: '%s%s%s' %
                      (line,
                       ' \n'[(len(line)-line.rfind('\n')-1
                             + len(word.split('\n',1)[0]
                                  ) >= width)],
                       word),
                      text.split(' ')
                     )

    def __add_app_remarks(self,map_composition):

        app_no = self.application_num_first_edit.text() + "-" + self.application_num_type_edit.text() + "-" \
                     + self.application_num_middle_edit.text() + "-" + self.application_num_last_edit.text()

        try:
            app = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).one()
        except SQLAlchemyError, e:
            raise LM2Exception(self.tr("Database Query Error"), self.tr("aCould not execute: {0}").format(e.message))

        item = map_composition.getComposerItemById("app_remarks")

        item.setText(self.__wrap(app.remarks,140))
        # item.adjustSizeToText()

    def __add_app_date(self,map_composition):

        app_no = self.application_num_first_edit.text() + "-" + self.application_num_type_edit.text() + "-" \
                     + self.application_num_middle_edit.text() + "-" + self.application_num_last_edit.text()
        try:
            app = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).one()
        except SQLAlchemyError, e:
            raise LM2Exception(self.tr("Database Query Error"), self.tr("aCould not execute: {0}").format(e.message))

        item = map_composition.getComposerItemById("year")
        item.setText(str(app.app_timestamp)[:4])
        item.adjustSizeToText()

        item = map_composition.getComposerItemById("month")
        item.setText(str(app.app_timestamp)[5:-12])
        item.adjustSizeToText()

        item = map_composition.getComposerItemById("day")
        item.setText(str(app.app_timestamp)[8:-9])
        item.adjustSizeToText()

        item = map_composition.getComposerItemById("hour")
        item.setText(str(app.app_timestamp)[10:-6])
        item.adjustSizeToText()

        item = map_composition.getComposerItemById("minute")
        item.setText(str(app.app_timestamp)[14:-3])
        item.adjustSizeToText()

    def __add_app_status_date(self,map_composition):

        app_no = self.application_num_first_edit.text() + "-" + self.application_num_type_edit.text() + "-" \
                     + self.application_num_middle_edit.text() + "-" + self.application_num_last_edit.text()
        try:
            app_status = self.session.query(CtApplicationStatus).filter(CtApplicationStatus.application == app_no) \
                                                                .filter(CtApplicationStatus.status == 8).one()
        except SQLAlchemyError, e:
            raise LM2Exception(self.tr("Database Query Error"), self.tr("aCould not execute: {0}").format(e.message))

        item = map_composition.getComposerItemById("year")
        item.setText(str(app_status.status_date)[:4])
        item.adjustSizeToText()

        item = map_composition.getComposerItemById("month")
        item.setText(str(app_status.status_date)[5:-3])
        item.adjustSizeToText()

        item = map_composition.getComposerItemById("day")
        item.setText(str(app_status.status_date)[8:])
        item.adjustSizeToText()

    def __add_app_date_minut(self,map_composition):

        app_no = self.application_num_first_edit.text() + "-" + self.application_num_type_edit.text() + "-" \
                     + self.application_num_middle_edit.text() + "-" + self.application_num_last_edit.text()
        try:
            app = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).one()
        except SQLAlchemyError, e:
            raise LM2Exception(self.tr("Database Query Error"), self.tr("aCould not execute: {0}").format(e.message))
        item = map_composition.getComposerItemById("app_date_minut")
        item.setText(str(app.app_timestamp)[10:])
        item.adjustSizeToText()

    def __add_person_name(self,map_composition):

        app_no = self.application_num_first_edit.text() + "-" + self.application_num_type_edit.text() + "-" \
                     + self.application_num_middle_edit.text() + "-" + self.application_num_last_edit.text()

        # try:
        if self.application.app_type == 7 or self.application.app_type == 15:
            app_person = self.session.query(CtApplicationPersonRole).\
                filter(CtApplicationPersonRole.application == app_no).\
                filter(CtApplicationPersonRole.role == Constants.NEW_RIGHT_HOLDER_CODE).all()
        elif self.application.app_type == 2:
            app_person = self.session.query(CtApplicationPersonRole). \
                filter(CtApplicationPersonRole.application == app_no). \
                filter(CtApplicationPersonRole.role == Constants.REMAINING_OWNER_CODE).all()
        else:
            app_person = self.session.query(CtApplicationPersonRole). \
                filter(CtApplicationPersonRole.application == self.application.app_id).all()
        for p in app_person:
            if p.main_applicant == True:
                person = self.session.query(BsPerson).filter(BsPerson.person_id == p.person).one()
        # except SQLAlchemyError, e:
        #     raise LM2Exception(self.tr("Database Query Error"), self.tr("aCould not execute: {0}").format(e.message))
        item = map_composition.getComposerItemById("person_name")
        first_name = ''
        if person.first_name == None:
            first_name = u' '
        else:
            first_name = person.first_name
        name = person.name +u", "+ first_name
        item.setText(name)
        item.adjustSizeToText()

    def __wrap(self,text, width):
        """
        A word-wrap function that preserves existing line breaks
        and most spaces in the text. Expects that existing line
        breaks are posix newlines (\n).
        """
        return reduce(lambda line, word, width=width: '%s%s%s' %
                      (line,
                       ' \n'[(len(line)-line.rfind('\n')-1
                             + len(word.split('\n',1)[0]
                                  ) >= width)],
                       word),
                      text.split(' ')
                     )

    def __add_officer_name(self,map_composition):

        app_no = self.application_num_first_edit.text() + "-" + self.application_num_type_edit.text() + "-" \
                     + self.application_num_middle_edit.text() + "-" + self.application_num_last_edit.text()
        app_id = self.application.app_id
        try:
            app_status = self.session.query(CtApplicationStatus).\
                filter(CtApplicationStatus.application == app_id).\
                filter(CtApplicationStatus.status == 8).all()
            for p in app_status:
                sd_officer = self.session.query(SdUser).filter(SdUser.user_id == p.officer_in_charge).one()
                officer = sd_officer.gis_user_real_ref
        except SQLAlchemyError, e:
            raise LM2Exception(self.tr("Database Query Error"), self.tr("aCould not execute: {0}").format(e.message))
        position = 10
        if officer.position != None:
            position = officer.position
            position = self.session.query(SdPosition).filter(SdPosition.position_id == position).one()
        officer_full = '                          ' + position.name + u' албан тушаалтан '+ sd_officer.lastname + u' овогтой ' + sd_officer.firstname + ' ___________________ '+ u' хүлээн авав.'
        item = map_composition.getComposerItemById("officer_surname")
        item.setText(sd_officer.lastname)
        item.adjustSizeToText()

        item = map_composition.getComposerItemById("officer_name")
        item.setText(sd_officer.firstname)
        item.adjustSizeToText()

    def __add_officer(self,map_composition):

        app_no = self.application_num_first_edit.text() + "-" + self.application_num_type_edit.text() + "-" \
                     + self.application_num_middle_edit.text() + "-" + self.application_num_last_edit.text()
        app_id = self.application.app_id
        try:
            app_status = self.session.query(CtApplicationStatus).\
                filter(CtApplicationStatus.application == app_id).all()
            for p in app_status:
                sd_officer = self.session.query(SdUser).filter(SdUser.user_id == p.officer_in_charge).one()
                officer = sd_officer.gis_user_real_ref
        except SQLAlchemyError, e:
            raise LM2Exception(self.tr("Database Query Error"), self.tr("aCould not execute: {0}").format(e.message))
        position = 10
        if officer.position != None:
            position = officer.position
            position = self.session.query(SdPosition).filter(SdPosition.position_id == position).one()
            position = position.description

        officer_full = '                          ' + position + u' албан тушаалтан '+ officer.surname + u' овогтой ' + officer.first_name + ' ___________________ '+ u' хүлээн авав.'
        item = map_composition.getComposerItemById("officer_full")
        item.setText(self.__wrap(officer_full, 200))
        # item.adjustSizeToText()

    def __valid_status(self, status_code):

        count = self.application.statuses.filter(CtApplicationStatus.status == status_code).count()
        if count > 0:
            return False

        return True

    def __add_applicant_item(self, applicant):

        if applicant.person_ref:
            try:
                person = self.session.query(BsPerson).filter(BsPerson.person_id == (applicant.person_ref.person_id)).one()
                self.person = person
            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return
            main_item = QTableWidgetItem(QIcon(), "")
            main_item.setCheckState(Qt.Checked) if applicant.main_applicant \
                else main_item.setCheckState(Qt.Unchecked)

            main_item.setData(Qt.UserRole, applicant.person)

            if person.type == 20:
                share_item = QTableWidgetItem(str(0))
                share_item.setData(Qt.UserRole, applicant.person)
            else:
                share_item = QTableWidgetItem(str(applicant.share) if (applicant.share) else '0')
                share_item.setData(Qt.UserRole, applicant.person)

            person_id_item = QTableWidgetItem(applicant.person_ref.person_register)
            person_id_item.setData(Qt.UserRole, applicant.person)
            person_id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            surname_item = QTableWidgetItem(applicant.person_ref.name)
            surname_item.setData(Qt.UserRole, applicant.person)
            surname_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            first_name_item = QTableWidgetItem(applicant.person_ref.first_name)
            first_name_item.setData(Qt.UserRole, applicant.person)
            first_name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            inserted_row = self.applicant_twidget.rowCount()

            self.applicant_twidget.insertRow(inserted_row)
            self.applicant_twidget.setItem(inserted_row, APPLICANT_MAIN, main_item)
            self.applicant_twidget.setItem(inserted_row, APPLICANT_SHARE, share_item)
            self.applicant_twidget.setItem(inserted_row, APPLICANT_PERSON_ID, person_id_item)
            self.applicant_twidget.setItem(inserted_row, APPLICANT_SURNAME, surname_item)
            self.applicant_twidget.setItem(inserted_row, APPLICANT_FIRST_NAME, first_name_item)

    def __add_person_item(self, person):

        if person:
            main_item = QTableWidgetItem(QIcon(), "")
            main_item.setCheckState(Qt.Unchecked)

            main_item.setData(Qt.UserRole, person.person_id)

            share_item = QTableWidgetItem(str(0))
            share_item.setData(Qt.UserRole, person.person_id)

            person_id_item = QTableWidgetItem(person.person_register)
            person_id_item.setData(Qt.UserRole, person.person_id)
            person_id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            surname_item = QTableWidgetItem(person.name)
            surname_item.setData(Qt.UserRole, person.person_id)
            surname_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            first_name_item = QTableWidgetItem(person.first_name)
            first_name_item.setData(Qt.UserRole, person.person_id)
            first_name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            inserted_row = self.applicant_twidget.rowCount()

            self.applicant_twidget.insertRow(inserted_row)
            self.applicant_twidget.setItem(inserted_row, APPLICANT_MAIN, main_item)
            self.applicant_twidget.setItem(inserted_row, APPLICANT_SHARE, share_item)
            self.applicant_twidget.setItem(inserted_row, APPLICANT_PERSON_ID, person_id_item)
            self.applicant_twidget.setItem(inserted_row, APPLICANT_SURNAME, surname_item)
            self.applicant_twidget.setItem(inserted_row, APPLICANT_FIRST_NAME, first_name_item)

            role = Constants.APPLICANT_ROLE_CODE
            role_ref = self.session.query(ClPersonRole).filter_by(
                code=role).one()

            app_person_role = CtApplicationPersonRole()
            app_person_role.application = self.application.app_id
            app_person_role.share = Decimal(1.0)
            app_person_role.role = role
            app_person_role.role_ref = role_ref
            app_person_role.person = person.person_id
            app_person_role.person_ref = person
            app_person_role.main_applicant = False

            self.application.stakeholders.append(app_person_role)

    def __add_application_status_item(self, status):

        item_status = QTableWidgetItem(status.status_ref.description)
        item_status.setData(Qt.UserRole, status.status_ref.code)
        item_date = QTableWidgetItem(str(status.status_date))

        if status.next_officer_in_charge_ref:
            next_officer = status.next_officer_in_charge_ref.lastname + ", " + status.next_officer_in_charge_ref.firstname
            officer = status.officer_in_charge_ref.lastname + ", " + status.officer_in_charge_ref.firstname

            item_next_officer = QTableWidgetItem(next_officer)
            item_next_officer.setData(Qt.UserRole, status.next_officer_in_charge)

            item_officer = QTableWidgetItem(officer)
            item_officer.setData(Qt.UserRole, status.officer_in_charge)

            row = self.application_status_twidget.rowCount()
            self.application_status_twidget.insertRow(row)

            self.application_status_twidget.setItem(row, STATUS_STATE, item_status)
            self.application_status_twidget.setItem(row, STATUS_DATE, item_date)
            self.application_status_twidget.setItem(row, STATUS_OFFICER, item_officer)
            self.application_status_twidget.setItem(row, STATUS_NEXT_OFFICER, item_next_officer)

    def __generate_application_number(self):

        au_level2 = DatabaseUtils.current_working_soum_schema()
        application_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())

        if au_level2 is None or application_type is None:
            return

        if self.attribute_update:
            return

        self.application_num_first_edit.setText(au_level2)
        self.application_num_type_edit.setText(str(application_type).zfill(2))
        app_type_filter = "%-" + str(application_type).zfill(2) + "-%"
        soum_filter = str(au_level2) + "-%"
        year_filter = "%-" + str(QDate().currentDate().toString("yy"))

        try:

            count = self.session.query(CtApplication).filter(CtApplication.app_id != self.application.app_id) \
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
                    .filter(CtApplication.app_id != self.application.app_id) \
                    .filter(CtApplication.app_no.like("%-%"))\
                    .filter(CtApplication.app_no.like(app_type_filter)) \
                    .filter(CtApplication.app_no.like(soum_filter)) \
                    .filter(CtApplication.app_no.like(year_filter)) \
                    .order_by(func.substr(CtApplication.app_no, 10, 14).desc()).first()
            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return

            app_no_numbers = max_number_app.app_no.split("-")

            self.application_num_middle_edit.setText(str(int(app_no_numbers[2]) + 1).zfill(5))

        else:
            self.application_num_middle_edit.setText("00001")

        self.application_num_last_edit.setText(QDate().currentDate().toString("yy"))

    def __set_visible_tabs(self):

        app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())

        self.requested_year_spin_box.setVisible(False)
        self.approved_year_spin_box.setVisible(False)
        self.duration_approved_label.setVisible(False)
        self.duration_request_label.setVisible(False)

        self.__landuse_per_application_type(app_type)

        #type: 26 or 27

        self.requested_year_spin_box.setVisible(True)
        self.approved_year_spin_box.setVisible(True)
        self.duration_approved_label.setVisible(True)
        self.duration_request_label.setVisible(True)

        self.application_tab_widget.setCurrentIndex(0)

    def __is_contract_query(self, application_type):

        result = True if application_type in Constants.CONTRACT_TYPES else False
        return result

    def __update_applicant_cbox(self):

        self.applicant_documents_cbox.clear()
        self.updating = True
        for applicant in self.application.stakeholders:
            if applicant.role == Constants.APPLICANT_ROLE_CODE:
                person = self.session.query(BsPerson.person_id, BsPerson.name, BsPerson.first_name).filter_by(person_id=applicant.person).one()
                if person.first_name is None:
                    person_label = u"{0}".format(person.name)
                else:
                    person_label = u"{0}, {1}".format(person.name, person.first_name)
                self.applicant_documents_cbox.addItem(person_label, person.person_id)
        self.updating = False

    def __double_applicant(self, person_id):

        try:
            count = self.application.stakeholders.filter_by(person=person_id)\
                                    .filter_by(role=Constants.APPLICANT_ROLE_CODE).count()
        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return True

        if count > 0:
            return True

        return False

    def __valid_applicant_person(self, app_type_code, person_type_code):

        try:
            count = self.session.query(SetPersonTypeApplicationType).filter_by(application_type=app_type_code) \
                .filter_by(person_type=person_type_code).filter_by((SetPersonTypeApplicationType.person_type==10, SetPersonTypeApplicationType.person_type==20)).count()

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return False

        if count > 0:
            return True
        else:
            return False

    def __valid_applicant(self, app_type_code, person_type_code):

        try:
            count = self.session.query(SetPersonTypeApplicationType).filter_by(application_type=app_type_code) \
                .filter_by(person_type=person_type_code).count()

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return False

        if count > 0:
            return True
        else:
            return False

    def __fade_status_message(self):

        opacity = int(self.time_counter * 0.5)
        self.status_label.setStyleSheet("QLabel {color: rgba(255,0,0," + str(opacity) + ");}")
        self.status_label.setText(self.tr('Changes applied successfully.'))
        if self.time_counter == 0:
            self.timer.stop()
        self.time_counter -= 1

    def __start_fade_out_timer(self):

        self.timer = QTimer()
        self.timer.timeout.connect(self.__fade_status_message)
        self.time_counter = 500
        self.timer.start(10)

    @pyqtSlot()
    def on_help_button_clicked(self):

        app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())

        if app_type == 01:
            if self.application_tab_widget.currentIndex() == 0:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/application_details.htm")
            elif self.application_tab_widget.currentIndex() == 1:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/application_applicants.htm")
            elif self.application_tab_widget.currentIndex() == 2:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/application_documents.htm")
            elif self.application_tab_widget.currentIndex() == 3:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/application_parcel.htm")
            elif self.application_tab_widget.currentIndex() == 4:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/application_record_created.htm")
            elif self.application_tab_widget.currentIndex() == 5:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/application_print.htm")

    def __validate_entity_id(self, text):

        valid = self.int_validator.regExp().exactMatch(text)

        if not valid:
            self.error_label.setText(self.tr("Company id should be with numbers only."))
            return False
        if len(text) > 7:
            cut = text[:7]
            self.personal_id_edit.setText(cut)

        return True

    @pyqtSlot(int)
    def on_is_find_applicant_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            person_type = self.person_type_cbox.itemData(self.person_type_cbox.currentIndex())
            person_registers = []
            person_names = []
            # register_like = "%" + text+ "%"
            for value in self.session.query(BsPerson.person_register, BsPerson.name).distinct().filter(
                            BsPerson.type == person_type):
                if value[0]:
                    register_value = value[0] + ':' + value[1]
                    person_registers.append(register_value)

                if value[1]:
                    name_value = value[1] + ':' + value[0]
                    person_names.append(name_value)

            self.person_register_model = QStringListModel(person_registers)

            self.person_register_proxy_model = QSortFilterProxyModel()
            self.person_register_proxy_model.setSourceModel(self.person_register_model)

            self.person_register_completer = QCompleter(self.person_register_proxy_model, self,
                                                        activated=self.on_person_register_completer_activated)
            self.person_register_completer.setCompletionMode(QCompleter.PopupCompletion)

            self.personal_id_edit.setCompleter(self.person_register_completer)
            self.personal_id_edit.textEdited.connect(self.person_register_proxy_model.setFilterFixedString)
            ###
            self.person_name_model = QStringListModel(person_names)

            self.person_name_proxy_model = QSortFilterProxyModel()
            self.person_name_proxy_model.setSourceModel(self.person_name_model)

            self.person_name_completer = QCompleter(self.person_name_proxy_model, self,
                                                    activated=self.on_person_name_completer_activated)
            self.person_name_completer.setCompletionMode(QCompleter.PopupCompletion)

            self.personal_name_edit.setCompleter(self.person_name_completer)
            self.personal_name_edit.textEdited.connect(self.person_name_proxy_model.setFilterFixedString)

    @pyqtSlot(int)
    def on_person_type_cbox_currentIndexChanged(self, index):

        person_type = self.person_type_cbox.itemData(self.person_type_cbox.currentIndex())
        person_registers = []
        person_names = []
        # register_like = "%" + text+ "%"
        # for value in self.session.query(BsPerson.person_register, BsPerson.name).distinct().filter(
        #                 BsPerson.type == person_type):
        #     if value[0]:
        #         register_value = value[0] + ':' + value[1]
        #         person_registers.append(register_value)
        #
        #     if value[1]:
        #         name_value = value[1] + ':' + value[0]
        #         person_names.append(name_value)
        #
        # self.person_register_model = QStringListModel(person_registers)
        #
        # self.person_register_proxy_model = QSortFilterProxyModel()
        # self.person_register_proxy_model.setSourceModel(self.person_register_model)
        #
        # self.person_register_completer = QCompleter(self.person_register_proxy_model, self,
        #                                    activated=self.on_person_register_completer_activated)
        # self.person_register_completer.setCompletionMode(QCompleter.PopupCompletion)
        #
        # self.personal_id_edit.setCompleter(self.person_register_completer)
        # self.personal_id_edit.textEdited.connect(self.person_register_proxy_model.setFilterFixedString)
        # ###
        # self.person_name_model = QStringListModel(person_names)
        #
        # self.person_name_proxy_model = QSortFilterProxyModel()
        # self.person_name_proxy_model.setSourceModel(self.person_name_model)
        #
        # self.person_name_completer = QCompleter(self.person_name_proxy_model, self,
        #                                             activated=self.on_person_name_completer_activated)
        # self.person_name_completer.setCompletionMode(QCompleter.PopupCompletion)
        #
        # self.personal_name_edit.setCompleter(self.person_name_completer)
        # self.personal_name_edit.textEdited.connect(self.person_name_proxy_model.setFilterFixedString)

    @pyqtSlot(str)
    def on_person_register_completer_activated(self, text):

        if not text:
            return
        value = text.split(':')
        self.person_register_completer.activated[str].emit(value[0])
        self.personal_name_edit.setText(text)

    @pyqtSlot(str)
    def on_person_name_completer_activated(self, text):

        if not text:
            return

        self.person_name_completer.activated[str].emit(text)

    @pyqtSlot(str)
    def on_personal_name_edit_textChanged(self, text):

        if len(text.split(":")) > 1:
            register = text.split(":")[1]
            self.personal_id_edit.setText(register)

    @pyqtSlot(str)
    def on_personal_id_edit_textChanged(self, text):

        self.personal_id_edit.setStyleSheet(self.styleSheet())

        value = text.split(':')
        self.personal_id_edit.setText(value[0])

    @pyqtSlot()
    def on_search_person_button_clicked(self):

        if self.personal_id_edit.text() == "":
            return

        person_type = self.person_type_cbox.itemData(self.person_type_cbox.currentIndex())
        person_register = self.personal_id_edit.text()

        person_count = self.session.query(BsPerson).filter(BsPerson.person_register == person_register).count()
        if person_count == 1:
            person = self.session.query(BsPerson).filter(BsPerson.person_register == person_register).one()
            person_info = ''
            if person.first_name:
                person_info = person.person_register + ': ' + person.name + ' ' + person.first_name
            else:
                person_info = person.person_register + ': ' + person.name
            self.accept_person_edit.setText(person_info)

    @pyqtSlot()
    def on_accept_person_button_clicked(self):

        if self.personal_id_edit.text() == "":
            return

        person_register = self.personal_id_edit.text()

        person_count = self.session.query(BsPerson).filter(BsPerson.person_register == person_register).count()
        if person_count == 1:
            person = self.session.query(BsPerson).filter(BsPerson.person_register == person_register).one()

            self.__add_person_item(person)