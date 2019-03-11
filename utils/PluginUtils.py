__author__ = 'anna'
#!/usr/bin/python
# -*- coding: utf-8
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import QgsTolerance
from datetime import date, datetime
from ..model.CtApplication import CtApplication
from ..model.CtApplicationStatus import CtApplicationStatus
from ..model.ClApplicationStatus import ClApplicationStatus
from ..model.CtOwnershipRecord import CtOwnershipRecord
from ..model.LM2Exception import LM2Exception
from ..model.SdUser import SdUser
from ..model.CtContract import CtContract
from ..model.SetRole import SetRole
from ..model.CaMaintenanceCase import CaMaintenanceCase
from ..model.AuLevel1 import AuLevel1
from ..model.AuLevel2 import AuLevel2
from ..model.AuLevel3 import AuLevel3
from ..model.CaParcelTbl import CaParcelTbl
from ..model import SettingsConstants
from ..model import Constants
from ..model.SdUser import *
from ..model.SdAutoNumbers import *
from ..utils.LM2Logger import LM2Logger
from geoalchemy2 import func
from sqlalchemy import func, or_, and_, desc
from sqlalchemy.exc import SQLAlchemyError
from ..utils.DatabaseUtils import DatabaseUtils
from SessionHandler import SessionHandler
import os
import hashlib

class PluginUtils(object):

    @staticmethod
    def create_new_application(app_no=None):

        session = SessionHandler().session_instance()
        current_user = QSettings().value(SettingsConstants.USER)
        application = CtApplication()

        if app_no is None:
            application.app_no = "00" + QDateTime.currentDateTime().toString("yyMMddhhmmss")
        else:
            application.app_no = app_no

        application_status = CtApplicationStatus()
        application_status.ct_application = application
        status = session.query(ClApplicationStatus).filter_by(code='1').one()
        application_status.status = 1
        application_status.status_ref = status
        application_status.status_date = date.today()
        date_time_string = QDateTime.currentDateTime().toString(Constants.DATABASE_DATETIME_FORMAT)
        application.app_timestamp = datetime.strptime(date_time_string, Constants.PYTHON_DATETIME_FORMAT)
        application.created_at = datetime.strptime(date_time_string, Constants.PYTHON_DATETIME_FORMAT)
        application.updated_at = datetime.strptime(date_time_string, Constants.PYTHON_DATETIME_FORMAT)
        application.app_type = 1
        application.au2 = DatabaseUtils.current_working_soum_schema()
        application.au1 = DatabaseUtils.working_l1_code()
        # application.right_type = 1

        application.created_by = DatabaseUtils.current_sd_user().user_id

        application_status.next_officer_in_charge = DatabaseUtils.current_sd_user().user_id
        application_status.next_officer_in_charge_ref = DatabaseUtils.current_sd_user()
        application_status.officer_in_charge_ref = DatabaseUtils.current_sd_user()
        application_status.officer_in_charge = DatabaseUtils.current_sd_user().user_id
        application.statuses.append(application_status)
        session.add(application)

        return application

    @staticmethod
    def create_new_contract():

        session = SessionHandler().session_instance()

        contract = CtContract()
        contract.contract_no = QDateTime.currentDateTime().toString("yyMMddhhmmss")
        contract.au2 = DatabaseUtils.working_l2_code()

        session.add(contract)

        return contract

    @staticmethod
    def create_new_m_case():

        session = SessionHandler().session_instance()
        ca_maintenance_case = CaMaintenanceCase()

        user_name = DatabaseUtils.current_user().user_name
        user = session.query(SetRole).filter(SetRole.user_name == user_name).filter(SetRole.is_active == True).one()
        sd_user = session.query(SdUser).filter(SdUser.gis_user_real == user.user_name_real).first()
        ca_maintenance_case.created_by = sd_user.user_id
        ca_maintenance_case.au2 = DatabaseUtils.working_l2_code()
        session.add(ca_maintenance_case)
        return ca_maintenance_case

    @staticmethod
    def create_new_record(record_no=None):

        session = SessionHandler().session_instance()
        record = CtOwnershipRecord()

        if not record_no:
            record.record_no = QDateTime.currentDateTime().toString("yyMMddhhmmss")
        else:
            record.record_no = record_no

        record.au2 = DatabaseUtils.working_l2_code()
        session.add(record)
        return record

    @staticmethod
    def populate_au_level1_cbox(cbox, with_star_entry=True, with_restriction=True, select_working_entry=True):

        cbox.clear()
        session = SessionHandler().session_instance()
        # cbox.addItem("UB", 01)
        if with_star_entry:
            cbox.addItem("*", -1)

        if with_restriction:
            l1_restrictions = DatabaseUtils.l1_restriction_array()
            for code, name in session.query(AuLevel1.code, AuLevel1.name).filter(
                    AuLevel1.code.in_(l1_restrictions)).\
                    filter(AuLevel1.code != '013').filter(AuLevel1.code != '012').order_by(AuLevel1.name):
                cbox.addItem(name, code)
        else:
            for code, name in session.query(AuLevel1.code, AuLevel1.name).\
                    filter(AuLevel1.code != '013').filter(AuLevel1.code != '012').order_by(AuLevel1.name):
                cbox.addItem(name, code)

        if select_working_entry:
            working_l1_code = DatabaseUtils.working_l1_code()
            idx = cbox.findData(working_l1_code, Qt.UserRole)
            if idx != -1:
                cbox.setCurrentIndex(idx)

    @staticmethod
    def populate_au_level2_cbox(cbox, l1_code, with_star_entry=True, with_restriction=True, select_working_entry=True):

        cbox.clear()
        session = SessionHandler().session_instance()

        if l1_code != -1:
            if l1_code != None:
                if with_star_entry:
                    cbox.addItem("*", -1)
                if with_restriction:
                    l2_restrictions = DatabaseUtils.l2_restriction_array()
                    for code, name in session.query(AuLevel2.code, AuLevel2.name).filter(
                            AuLevel2.code.in_(l2_restrictions)).filter(
                            AuLevel2.code.startswith(l1_code)).order_by(AuLevel2.name):
                        # if code.startswith('1') or code.startswith('01'):
                        #     continue
                        cbox.addItem(name, code)
                else:
                    for code, name in session.query(AuLevel2.code, AuLevel2.name).filter(
                            AuLevel2.code.startswith(l1_code)).order_by(AuLevel2.name):
                        cbox.addItem(name+'_'+code, code)
                if select_working_entry:
                    working_l2_code = DatabaseUtils.working_l2_code()
                    idx = cbox.findData(working_l2_code, Qt.UserRole)
                    if idx != -1:
                        cbox.setCurrentIndex(idx)

    @staticmethod
    def populate_au_level3_cbox(cbox, l1_or_l2_code, with_star_entry=True):

        cbox.clear()
        session = SessionHandler().session_instance()
        if with_star_entry:
            cbox.addItem("*", -1)

        for code, name in session.query(AuLevel3.code, AuLevel3.name).filter(
                AuLevel3.code.startswith(l1_or_l2_code)).order_by(AuLevel3.name):
            cbox.addItem(name, code)

    @staticmethod
    def show_message(parent, title, message):

        if PluginUtils.is_logging_enabled():
            LM2Logger().log_message(message)

        message_box = QMessageBox(QMessageBox.Information, title, message, QMessageBox.Ok,
                                  parent, Qt.WindowStaysOnTopHint)
        message_box.exec_()

    @staticmethod
    def show_error(parent, title, message):

        if PluginUtils.is_logging_enabled():
            LM2Logger().log_message(message)
        message_box = QMessageBox()
        message_box = QMessageBox(QMessageBox.Warning, title, message, QMessageBox.Ok,
                                  parent, Qt.WindowStaysOnTopHint)
        message_box.exec_()

    @staticmethod
    def convert_qt_date_to_python(qt_date):
        if not qt_date:
            return None
        date_string = qt_date.toString(Constants.DATE_FORMAT)
        python_date = datetime.strptime(str(date_string), Constants.PYTHON_DATE_FORMAT)
        return python_date

    @staticmethod
    def convert_python_date_to_qt(python_date):

        if not python_date:
            return None
        converted_date = QDate.fromString(python_date.strftime(Constants.PYTHON_DATE_FORMAT),
                                          Constants.DATABASE_DATE_FORMAT)
        return converted_date

    @staticmethod
    def convert_python_datetime_to_qt(python_datetime):

        if not python_datetime:
            return None
        converted_datetime = QDateTime.fromString(python_datetime.strftime(Constants.PYTHON_DATETIME_FORMAT),
                                                  Constants.DATABASE_DATETIME_FORMAT)
        return converted_datetime

    @staticmethod
    def soum_from_parcel(parcel_id):

        # try:
        session = SessionHandler().session_instance()
        parcel_count = session.query(CaParcelTbl).filter(CaParcelTbl.parcel_id == parcel_id).count()
        if parcel_count == 0:
            return None
        else:
            parcel = session.query(CaParcelTbl).filter(CaParcelTbl.parcel_id == parcel_id).first()
            soum = session.query(AuLevel2.code).filter(func.ST_Covers(AuLevel2.geometry, parcel.geometry)).one()
            return soum[0]
        # except SQLAlchemyError, e:
        #     raise LM2Exception(QApplication.translate("LM2", "Database Query Error"),
        #                        QApplication.translate("LM2", "Could not execute: {0}").format(e.message))



    @staticmethod
    def layer_tolerance(map_canvas, layer):
        """Functions finds out default tolerance from qgis settings.

        Required value (of qgis settings) is returned by QgsTolerance.defaultTolerance(...) calling.
        If returned value equals 0.0, we ignore it and calculate our own tolerance from current extent width.

        @return default tolerance
        """

        qgis_tolerance = QgsTolerance.defaultTolerance(layer, map_canvas.mapRenderer())

        if qgis_tolerance == 0.0:
            extent = map_canvas.extent()
            w = extent.xMaximum() - extent.xMinimum()
            return w/220

        return qgis_tolerance

    @staticmethod
    def get_map_path():

        mapPath = os.path.join(os.path.dirname(__file__), "view/map")
        return str(mapPath)

    @staticmethod
    def utm_srid_from_point(point):

        zoneNumber = ((point.x() + 180)/6) + 1
        zoneNumber = str(zoneNumber).split(".")[0]

        #south
        if point.y() < 0:
            return "327" + str(zoneNumber)
        #north
        else:
            return "326" + str(zoneNumber)

    @staticmethod
    def utm_proj4def_from_point(point):

        proj4Def = ""
        zoneNumber = ((point.x() + 180)/6) + 1
        zoneNumber = str(zoneNumber).split(".")[0]

        if point.y() < 0:
            proj4Def = "+proj=utm +zone={0} +south +datum=WGS84 +units=m +no_defs".format(zoneNumber)
        else:
            proj4Def = "+proj=utm +zone={0} +datum=WGS84 +units=m +no_defs".format(zoneNumber)

        return proj4Def

    @staticmethod
    def is_logging_enabled():

        session = SessionHandler().session_instance()
        if session is None:
            return True

        result = session.execute("SELECT log_enabled from settings.set_logging;")
        for row in result:
            return row[0]

    @staticmethod
    def generate_auto_app_no(year, app_type, soum_code, object_type):

        session = SessionHandler().session_instance()

        soum_filter = str(soum_code) + "-%"

        if object_type == 'application\Application':
            format_text = soum_code + '-' + app_type + '-' + '?' + '-' + year
            generate_name = 'a:3:{s:7:"classes";s:23:"application\Application";s:6:"format";s:13:"' + format_text + '";s:6:"length";i:5;}'
            generate_name_md5 = hashlib.md5(generate_name).hexdigest()
            app_type_filter = "%-" + str(app_type).zfill(2) + "-%"
            year_filter = "%-" + str(year)

            count = session.query(SdAutoNumbers). \
                filter(SdAutoNumbers.format.like("%-%")). \
                filter(SdAutoNumbers.format.like(app_type_filter)). \
                filter(SdAutoNumbers.format.like(soum_filter)). \
                filter(SdAutoNumbers.format.like(year_filter)). \
                filter(SdAutoNumbers.classes == object_type).count()
            if count > 1:
                count = session.query(SdAutoNumbers).filter(SdAutoNumbers.name == generate_name_md5).count()
                if count == 1:
                    auto_number = session.query(SdAutoNumbers).filter(SdAutoNumbers.name == generate_name_md5).one()
                    auto_number.number = auto_number.number + 1
            elif count == 1:
                auto_number = session.query(SdAutoNumbers). \
                    filter(SdAutoNumbers.format.like("%-%")). \
                    filter(SdAutoNumbers.format.like(app_type_filter)). \
                    filter(SdAutoNumbers.format.like(soum_filter)). \
                    filter(SdAutoNumbers.format.like(year_filter)). \
                    filter(SdAutoNumbers.classes == object_type).one()
                auto_number.number = auto_number.number + 1
            elif count == 0:
                auto_number = SdAutoNumbers()
                auto_number.name = generate_name_md5
                auto_number.number = 1
                auto_number.classes = object_type
                auto_number.format = format_text
                auto_number.length = 5

                session.add(auto_number)
        elif object_type == 'contract\Contract':
            format_text = soum_code + '-' + year + '/' + '?'
            generate_name = 'a:3:{s:7:"classes";s:17:"contract\Contract";s:6:"format";s:12:"' + format_text + '";s:6:"length";i:5;}'
            generate_name_md5 = hashlib.md5(generate_name).hexdigest()
            year_filter = "%-" + str(year) + '/%'
            count = session.query(SdAutoNumbers). \
                filter(SdAutoNumbers.format.like("%-%")). \
                filter(SdAutoNumbers.format.like(soum_filter)). \
                filter(SdAutoNumbers.format.like(year_filter)). \
                filter(SdAutoNumbers.classes == object_type).count()
            if count > 1:
                count = session.query(SdAutoNumbers).filter(SdAutoNumbers.name == generate_name_md5).count()
                if count == 1:
                    auto_number = session.query(SdAutoNumbers).filter(SdAutoNumbers.name == generate_name_md5).one()
                    auto_number.number = auto_number.number + 1
            elif count == 1:
                auto_number = session.query(SdAutoNumbers). \
                    filter(SdAutoNumbers.format.like("%-%")). \
                    filter(SdAutoNumbers.format.like(soum_filter)). \
                    filter(SdAutoNumbers.format.like(year_filter)). \
                    filter(SdAutoNumbers.classes == object_type).one()
                auto_number.number = auto_number.number + 1
            elif count == 0:
                auto_number = SdAutoNumbers()
                auto_number.name = generate_name_md5
                auto_number.number = 1
                auto_number.classes = object_type
                auto_number.format = format_text
                auto_number.length = 5

                session.add(auto_number)
        elif object_type == 'record\OwnershipRecord':
            year_filter = "%-" + str(year) + '/%'
            format_text = soum_code + '-' + year + '/' + '?'
            # 'a:3:{s:7:"classes";s:22:"record\OwnershipRecord";s:6:"format";s:12:"08110-2019/?";s:6:"length";i:5;}'
            generate_name = 'a:3:{s:7:"classes";s:22:"record\OwnershipRecord";s:6:"format";s:12:"' + format_text + '";s:6:"length";i:5;}'
            generate_name_md5 = hashlib.md5(generate_name).hexdigest()
            count = session.query(SdAutoNumbers). \
                filter(SdAutoNumbers.format.like("%-%")). \
                filter(SdAutoNumbers.format.like(soum_filter)). \
                filter(SdAutoNumbers.format.like(year_filter)). \
                filter(SdAutoNumbers.classes == object_type).count()

            if count > 1:
                count = session.query(SdAutoNumbers).filter(SdAutoNumbers.name == generate_name_md5).count()
                if count == 1:
                    auto_number = session.query(SdAutoNumbers).filter(SdAutoNumbers.name == generate_name_md5).one()
                    auto_number.number = auto_number.number + 1
            elif count == 1:
                auto_number = session.query(SdAutoNumbers). \
                    filter(SdAutoNumbers.format.like("%-%")). \
                    filter(SdAutoNumbers.format.like(soum_filter)). \
                    filter(SdAutoNumbers.format.like(year_filter)). \
                    filter(SdAutoNumbers.classes == object_type).one()
                auto_number.number = auto_number.number + 1
            elif count == 0:
                auto_number = SdAutoNumbers()
                auto_number.name = generate_name_md5
                auto_number.number = 1
                auto_number.classes = object_type
                auto_number.format = format_text
                auto_number.length = 5

                session.add(auto_number)
        # session.flush()
        session.commit()