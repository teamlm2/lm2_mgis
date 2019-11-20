# coding=utf8

__author__ = 'B.Ankhbold'

from types import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from qgis.core import *
from qgis.gui import *
from sqlalchemy import func, or_, and_, desc,extract
from geoalchemy2.elements import WKTElement
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
from ..model.SetValidation import *
from ..model.DatabaseHelper import *
from ..model import SettingsConstants
from ..model import Constants
from ..model.AuLevel1 import *
from ..model.AuLevel2 import *
from ..model.SdUser import *
from ..model.Enumerations import ApplicationType, UserRight
from ..model.SdFtpConnection import *
from ..model.SdFtpPermission import *
from ..model.PlProjectParcel import *
from ..model.ClPlanZone import *
from ..model.Constants import *
from ..model.SetFilterPlanLayer import *
from ..model.ClAttributeZone import *
from ..model.ClAttributeGroup import *
from ..model.SetPlanZoneAttribute import *
from ..model.PlProjectParcelAttributeValue import *
from ..model.PlProjectParcelAttributeValue import *
from ..model.PlProjectParcelAttributeValue import *
from ..view.Ui_PlanAttributeEditDialog import Ui_PlanAttributeEditDialog
from .qt_classes.ApplicantDocumentDelegate import ApplicationDocumentDelegate
from .qt_classes.DocumentsTableWidget import DocumentsTableWidget
from .qt_classes.DragTableWidget import DragTableWidget
from .qt_classes.DoubleSpinBoxDelegate import DoubleSpinBoxDelegate
from .qt_classes.LineEditDelegate import LineEditDelegate
from .qt_classes.DateDelegate import DateDelegate
from .qt_classes.DropLabel import DropLabel
from ..view.Ui_ApplicationsDialog import *
from ..utils.SessionHandler import SessionHandler
from ..utils.PluginUtils import PluginUtils
from ..utils.DatabaseUtils import DatabaseUtils
from ..utils.FilePath import *
from ftplib import FTP, error_perm

ATTRIBUTE_NAME = 0
ATTRIBUTE_VALUE = 1

class PlanAttributeEditDialog(QDialog, Ui_PlanAttributeEditDialog, DatabaseHelper):

    def __init__(self, plugin, navigator, parcel_list, process_type, plan, attribute_update=False, parent=None):

        super(PlanAttributeEditDialog, self).__init__(parent)
        DatabaseHelper.__init__(self)

        self.setupUi(self)
        self.navigator = navigator
        self.attribute_update = attribute_update
        self.close_button.clicked.connect(self.reject)
        self.session = SessionHandler().session_instance()
        self.plugin = plugin
        self.parcel_list = parcel_list
        self.process_type = process_type
        self.plan = plan
        self.au2 = DatabaseUtils.working_l2_code()
        self.au1 = DatabaseUtils.working_l1_code()

        self.user = DatabaseUtils.current_sd_user()
        self.user_id = self.user.user_id
        self.attribute_row = 0
        self.attribute_twidget = None
        self.__setup_attribute_twidget()

    def __setup_attribute_twidget(self):

        self.default_attribute_twidget = DragTableWidget("Attribute", 10, 20, 431, 210, self.attribute_group_box)
        self.attribute_twidget = DragTableWidget("Attribute", 10, 231, 431, 300, self.attribute_group_box)
        #
        header = [self.tr("Attribute Name"),
                  self.tr("Attribute Value")]
        self.default_attribute_twidget.setup_header(header)
        self.attribute_twidget.setup_header(header)
        # self.attribute_twidget.itemDropped.connect(self.on_application_twidget_itemDropped)
        # self.attribute_twidget.cellChanged.connect(self.on_application_twidget_cellChanged)

        default_attribute_row = self.default_attribute_twidget.rowCount()
        name_item = QTableWidgetItem('')
        name_item.setData(Qt.UserRole, '')
        name_item.setData(Qt.UserRole + 1, 0)
        name_item.setData(Qt.UserRole + 2, 1)

        value_item = QTableWidgetItem('')
        value_item.setData(Qt.UserRole, '')
        value_item.setData(Qt.UserRole + 1, 0)
        value_item.setData(Qt.UserRole + 2, 1)

        self.default_attribute_twidget.insertRow(default_attribute_row)
        self.default_attribute_twidget.setItem(default_attribute_row, ATTRIBUTE_NAME, name_item)
        self.default_attribute_twidget.setItem(default_attribute_row, ATTRIBUTE_VALUE, value_item)

        attributes = self.session.query(ClAttributeZone, SetPlanZoneAttribute).\
            join(SetPlanZoneAttribute, ClAttributeZone.attribute_id == SetPlanZoneAttribute.attribute_id).\
            filter(SetPlanZoneAttribute.plan_type_id == self.plan.plan_type_id).\
            filter(SetPlanZoneAttribute.plan_zone_id == self.process_type).order_by(ClAttributeZone.attribute_id.desc()).all()

        for value in attributes:
            attribute_row = self.attribute_twidget.rowCount()
            attribute = value.ClAttributeZone
            attribute_type = value.ClAttributeZone.attribute_type

            attribute_process = value.SetPlanZoneAttribute

            name_item = QTableWidgetItem(unicode(attribute.attribute_name_mn))
            name_item.setData(Qt.UserRole, attribute.attribute_id)
            name_item.setData(Qt.UserRole + 1, attribute_type)
            name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            attribute_value = ''
            attribute_process_id = attribute_process.attribute_id
            for parcel_id in self.parcel_list:
                value_count = self.session.query(PlProjectParcelAttributeValue).\
                    filter(PlProjectParcelAttributeValue.parcel_id == parcel_id).\
                    filter(PlProjectParcelAttributeValue.attribute_id == attribute_process_id).count()
                if value_count > 0:
                    values = self.session.query(PlProjectParcelAttributeValue). \
                        filter(PlProjectParcelAttributeValue.parcel_id == parcel_id). \
                        filter(PlProjectParcelAttributeValue.attribute_id == attribute_process_id).all()
                    for value in values:
                        if value.attribute_value:
                            attribute_value = value.attribute_value

            value_item = QTableWidgetItem(attribute_value)
            value_item.setData(Qt.UserRole, attribute_value)
            value_item.setData(Qt.UserRole + 1, attribute_process_id)
            value_item.setData(Qt.UserRole + 2, 1)

            self.attribute_twidget.insertRow(attribute_row)
            self.attribute_twidget.setItem(attribute_row, ATTRIBUTE_NAME, name_item)
            self.attribute_twidget.setItem(attribute_row, ATTRIBUTE_VALUE, value_item)

            if attribute_type == 'number':
                delegate = QDoubleSpinBox()
                if attribute_value != '':
                    delegate.setValue(float(Decimal(attribute_value)))
                else:
                    delegate.setValue(0)
                self.attribute_twidget.setCellWidget(attribute_row, ATTRIBUTE_VALUE, delegate)
            elif attribute_type == 'text':
                delegate = QLineEdit()
                delegate.setText(attribute_value)
                self.attribute_twidget.setCellWidget(attribute_row, ATTRIBUTE_VALUE, delegate)
            elif attribute_type == 'date':
                delegate = QDateEdit()
                if attribute_value != '':
                    delegate.setDate(QDate.fromString(attribute_value, Constants.DATE_FORMAT))
                else:
                    q_date = QDate.currentDate()
                    delegate.setDate(q_date)
                self.attribute_twidget.setCellWidget(attribute_row, ATTRIBUTE_VALUE, delegate)

        # self.attribute_twidget.resizeColumnsToContents()

    def __save_attribute(self):

        rows = self.attribute_twidget.rowCount()
        for parcel_id in self.parcel_list:
            for row in range(rows):
                name_item = self.attribute_twidget.item(row, ATTRIBUTE_NAME)
                value_item = self.attribute_twidget.item(row, ATTRIBUTE_VALUE)

                attribute_id = name_item.data(Qt.UserRole)
                attribute_type = name_item.data(Qt.UserRole + 1)
                attribute_process_id = value_item.data(Qt.UserRole+1)
                if attribute_type == 'number':
                    attribute_value = str(self.attribute_twidget.cellWidget(row, ATTRIBUTE_VALUE).value())
                elif attribute_type == 'date':
                    qt_date = self.attribute_twidget.cellWidget(row, ATTRIBUTE_VALUE).date()
                    date_string = qt_date.toString(Constants.DATE_FORMAT)
                    attribute_value = date_string
                elif attribute_type == 'text':
                    attribute_value = unicode(self.attribute_twidget.cellWidget(row, ATTRIBUTE_VALUE).text())

                count = self.session.query(PlProjectParcelAttributeValue). \
                    filter(PlProjectParcelAttributeValue.parcel_id == parcel_id). \
                    filter(PlProjectParcelAttributeValue.attribute_id == attribute_process_id).count()

                if count == 1:
                    value = self.session.query(PlProjectParcelAttributeValue). \
                        filter(PlProjectParcelAttributeValue.parcel_id == parcel_id). \
                        filter(PlProjectParcelAttributeValue.attribute_id == attribute_process_id).one()
                    value.attribute_value = attribute_value
                elif count == 0:
                    new_value = PlProjectParcelAttributeValue()
                    new_value.attribute_id = attribute_process_id
                    new_value.parcel_id = parcel_id
                    new_value.attribute_value = attribute_value

                    self.session.add(new_value)

    @pyqtSlot()
    def on_apply_button_clicked(self):

        self.create_savepoint()
        self.__save_attribute()
        self.commit()

        self.__start_fade_out_timer()

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