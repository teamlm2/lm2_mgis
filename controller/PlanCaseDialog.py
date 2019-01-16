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
from ..model.LdProjectParcel import *
from ..model.LdProjectMainZone import *
from ..model.LdProjectSubZone import *
from ..model.LdProcessPlan import *
from ..view.Ui_PlanCaseDialog import *
from .qt_classes.ApplicantDocumentDelegate import ApplicationDocumentDelegate
from .qt_classes.DocumentsTableWidget import DocumentsTableWidget
from .qt_classes.DragTableWidget import DragTableWidget
from .qt_classes.DoubleSpinBoxDelegate import DoubleSpinBoxDelegate
from .qt_classes.DropLabel import DropLabel
from ..view.Ui_ApplicationsDialog import *
from ..utils.SessionHandler import SessionHandler
from ..utils.PluginUtils import PluginUtils
from ..utils.DatabaseUtils import DatabaseUtils
from ..utils.FilePath import *
from ftplib import FTP, error_perm

class PlanCaseDialog(QDialog, Ui_PlanCaseDialog, DatabaseHelper):

    def __init__(self, plugin, plan, navigator, attribute_update=False, parent=None):

        super(PlanCaseDialog, self).__init__(parent)
        DatabaseHelper.__init__(self)

        self.setupUi(self)
        self.navigator = navigator
        self.attribute_update = attribute_update
        self.plugin = plugin
        self.close_button.clicked.connect(self.reject)
        self.session = SessionHandler().session_instance()
        self.plan = plan
        self.is_file_import = False
        self.approved_item = None
        self.refused_item = None

        self.polygon_rbutton.setChecked(True)
        self.zone_parcel_rbutton.setChecked(True)
        # self.message_label.setStyleSheet("QLabel { background-color : red; color : blue; }");
        self.message_label.setStyleSheet("QLabel {color: rgb(255,0,0);}")
        self.__setup_data()
        self.__setup_twidget()
        self.__setup_context_menu()

    def __setup_data(self):

        self.plan_num_edit.setText(self.plan.plan_draft_no)
        self.date_edit.setText(str(self.plan.begin_date))
        self.type_edit.setText(self.plan.plan_type_ref.description)
        self.status_edit.setText(self.plan.last_status_type_ref.description)

    def __setup_twidget(self):

        self.result_twidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.result_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.result_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.result_twidget.setContextMenuPolicy(Qt.CustomContextMenu)

        self.approved_item = QTreeWidgetItem()
        self.approved_item.setExpanded(True)
        self.approved_item.setText(0, self.tr("Approved"))

        self.refused_item = QTreeWidgetItem()
        self.refused_item.setExpanded(True)
        self.refused_item.setText(0, self.tr("Refused"))

        self.result_twidget.addTopLevelItem(self.approved_item)
        self.result_twidget.addTopLevelItem(self.refused_item)

    @pyqtSlot()
    def on_open_parcel_file_button_clicked(self):

        default_path = r'D:/TM_LM2/plan_maintenance'
        if not os.path.exists(default_path):
            os.makedirs(default_path)

        file_dialog = QFileDialog()
        file_dialog.setModal(True)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setFilter(self.tr("Shapefiles (*.shp)"))
        file_dialog.setDirectory(default_path)

        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            file_path = QFileInfo(selected_file).filePath()
            self.parcel_shape_edit.setText(file_path)
            self.__import_new_parcels(file_path)
            self.open_parcel_file_button.setEnabled(False)

    def __import_new_parcels(self, file_path):

        parcel_shape_layer = QgsVectorLayer(file_path, "tmp_parcel_shape", "ogr")

        if not parcel_shape_layer.isValid():
            PluginUtils.show_error(self,  self.tr("Error loading layer"), self.tr("The layer is invalid."))
            return

        if parcel_shape_layer.crs().postgisSrid() != 4326:
            PluginUtils.show_error(self, self.tr("Error loading layer"),
                                   self.tr("The crs of the layer has to be 4326."))
            return

        working_soum_code = DatabaseUtils.working_l2_code()
        iterator = parcel_shape_layer.getFeatures()
        count = 0
        # try:
        is_out_parcel = False
        error_message = ''

        for parcel in iterator:
            parcel_geometry = WKTElement(parcel.geometry().exportToWkt(), srid=4326)

            validaty_result = self.__check_parcel_correct(parcel_geometry, error_message)

            if not validaty_result[0]:
                log_measage = validaty_result[1]

                PluginUtils.show_error(self, self.tr("Invalid parcel info"), log_measage)
                return
            count += 1

            is_approved = False
            if self.__approved_parcel_check(parcel, parcel_shape_layer):
                is_approved = True

            if is_approved:
                new_parcel = LdProjectParcel()
                new_parcel.plan_draft_id = self.plan.plan_draft_id
                new_parcel.plan_draft_ref = self.plan
                new_parcel.parcel_id = QDateTime().currentDateTime().toString("MMddhhmmss") + str(count)
                new_parcel.valid_from = PluginUtils.convert_qt_date_to_python(QDateTime().currentDateTime())
                new_parcel.polygon_geom = WKTElement(parcel.geometry().exportToWkt(), srid=4326)
                new_parcel = self.__copy_parcel_attributes(parcel, new_parcel, parcel_shape_layer)

                self.session.add(new_parcel)

                # self.__copy_parcel_attributes(parcel, new_parcel, parcel_shape_layer)

                main_parcel_item = QTreeWidgetItem()
                # main_parcel_item.setText(0, new_parcel.parcel_id)
                main_parcel_item.setText(0, str(count))
                main_parcel_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                # main_parcel_item.setData(0, Qt.UserRole, new_parcel.parcel_id)
                # main_parcel_item.setData(0, Qt.UserRole + 1, Constants.CASE_PARCEL_IDENTIFIER)
                self.approved_item.addChild(main_parcel_item)

            else:
                main_parcel_item = QTreeWidgetItem()
                # main_parcel_item.setText(0, new_parcel.parcel_id)
                main_parcel_item.setText(0, str(count))
                main_parcel_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                # main_parcel_item.setData(0, Qt.UserRole, new_parcel.parcel_id)
                # main_parcel_item.setData(0, Qt.UserRole + 1, Constants.CASE_PARCEL_IDENTIFIER)
                self.refused_item.addChild(main_parcel_item)

    def __approved_parcel_check(self, parcel_feature, layer):

        valid = True

        column_name_parcel_id = "id"
        column_name_plan_code = "plan_code"
        column_name_landuse = "landuse"
        column_landname = "landname"
        column_name_khashaa = "address_kh"
        column_name_street = "address_st"
        column_name_comment = "comment"

        column_names = {column_name_parcel_id: "", column_name_plan_code: "", column_name_landuse: "",
                        column_landname: "", column_name_khashaa: "", column_name_street: "",
                        column_name_comment: ""}

        provider = layer.dataProvider()
        for key, item in column_names.iteritems():
            index = provider.fieldNameIndex(key)
            if index != -1:
                value = parcel_feature.attributes()[index]
                column_names[key] = value

        try:
            count = self.session.query(LdProcessPlan).filter(LdProcessPlan.code == column_names[column_name_plan_code]).count()
            if count == 0:
                valid = False
                self.message_label.setText(self.tr('The process code is not available in the database.'))
        except SQLAlchemyError, e:
            valid = False
            self.message_label.setText(self.tr('The process code is not available in the database.'))

        return valid

    def __copy_parcel_attributes(self, parcel_feature, parcel_object, layer):

        column_name_parcel_id = "id"
        column_name_plan_code = "plan_code"
        column_name_landuse = "landuse"
        column_landname = "landname"
        column_name_khashaa = "address_kh"
        column_name_street = "address_st"
        column_name_comment = "comment"

        column_names = {column_name_parcel_id: "", column_name_plan_code: "", column_name_landuse: "",
                        column_landname: "", column_name_khashaa: "", column_name_street: "",
                        column_name_comment: ""}

        provider = layer.dataProvider()
        for key, item in column_names.iteritems():
            index = provider.fieldNameIndex(key)
            if index != -1:
                value = parcel_feature.attributes()[index]
                column_names[key] = value

        id = 0
        plan_code = 0
        landuse = 0
        landname = ''
        address_khashaa = 0
        address_streetname = ''
        comment = ''

        if column_names[column_name_parcel_id] != None:
            id = column_names[column_name_parcel_id]
        if column_names[column_name_plan_code] != None:
            plan_code = column_names[column_name_plan_code]
        if column_names[column_name_landuse] != None:
            landuse = column_names[column_name_landuse]
        if column_names[column_landname] != None:
            landname = column_names[column_landname]
        if column_names[column_name_khashaa] != None:
            address_khashaa = column_names[column_name_khashaa]
        if column_names[column_name_street] != None:
            address_streetname = column_names[column_name_street]
        if column_names[column_name_comment] != None:
            comment = column_names[column_name_comment]

        parcel_object.landuse = landuse
        parcel_object.gazner = landname

        return parcel_object

    def __check_parcel_correct(self, geometry, error_message):

        organization = DatabaseUtils.current_user_organization()
        if not organization:
            return

        valid = True

        return valid, error_message

    @pyqtSlot(QPoint)
    def on_result_twidget_customContextMenuRequested(self, point):

        if self.is_file_import:
            return

        point = self.result_twidget.viewport().mapToGlobal(point)
        self.menu.exec_(point)

    def __setup_context_menu(self):

        self.menu = QMenu()
        self.zoom_to_selected = QAction(QIcon("zoom.png"), "Zoom to item", self)
        self.menu.addAction(self.zoom_to_selected)
        self.zoom_to_selected.triggered.connect(self.zoom_to_selected_clicked)

    @pyqtSlot()
    def zoom_to_selected_clicked(self):

        selected_item = self.result_twidget.selectedItems()[0]

        if selected_item is None:
            return

    @pyqtSlot()
    def on_apply_button_clicked(self):

        self.create_savepoint()

        self.commit()

        self.__start_fade_out_timer()
        self.plugin.iface.mapCanvas().refresh()

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