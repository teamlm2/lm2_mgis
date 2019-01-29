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

APPROVED = 'approved'
REFUSED = 'refused'

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
        self.au2 = DatabaseUtils.working_l2_code()
        self.au1 = DatabaseUtils.working_l1_code()
        self.error_dic = {}
        self.polygon_rbutton.setChecked(True)
        self.zone_parcel_rbutton.setChecked(True)
        self.message_label.setWordWrap(True)
        # self.message_label.setStyleSheet("QLabel { background-color : red; color : blue; }");
        self.message_label.setStyleSheet("QLabel {color: rgb(255,0,0);}")
        self.__zones_rbutton_setup()
        self.__setup_data()
        self.__setup_twidget()
        self.__setup_context_menu()

    def __zones_rbutton_setup(self):

        if self.zone_parcel_rbutton.isChecked():
            self.point_rbutton.setChecked(False)
            self.point_rbutton.setEnabled(False)
            self.line_rbutton.setChecked(False)
            self.line_rbutton.setEnabled(False)
            self.polygon_rbutton.setChecked(True)
            self.polygon_rbutton.setEnabled(True)
        elif self.zone_sub_rbutton.isChecked():
            self.point_rbutton.setChecked(False)
            self.point_rbutton.setEnabled(False)
            self.line_rbutton.setChecked(False)
            self.line_rbutton.setEnabled(False)
            self.polygon_rbutton.setChecked(True)
            self.polygon_rbutton.setEnabled(True)
        elif self.zone_main_rbutton.isChecked():
            self.point_rbutton.setChecked(True)
            self.point_rbutton.setEnabled(True)
            self.line_rbutton.setChecked(True)
            self.line_rbutton.setEnabled(True)
            self.polygon_rbutton.setChecked(True)
            self.polygon_rbutton.setEnabled(True)

    @pyqtSlot(bool)
    def on_zone_parcel_rbutton_toggled(self, state):

        if state:
            self.point_rbutton.setChecked(False)
            self.point_rbutton.setEnabled(False)
            self.line_rbutton.setChecked(False)
            self.line_rbutton.setEnabled(False)
            self.polygon_rbutton.setChecked(True)
            self.polygon_rbutton.setEnabled(True)

    @pyqtSlot(bool)
    def on_zone_sub_rbutton_toggled(self, state):

        if state:
            self.point_rbutton.setChecked(False)
            self.point_rbutton.setEnabled(False)
            self.line_rbutton.setChecked(False)
            self.line_rbutton.setEnabled(False)
            self.polygon_rbutton.setChecked(True)
            self.polygon_rbutton.setEnabled(True)

    @pyqtSlot(bool)
    def on_zone_main_rbutton_toggled(self, state):

        if state:
            self.point_rbutton.setChecked(True)
            self.point_rbutton.setEnabled(True)
            self.line_rbutton.setChecked(True)
            self.line_rbutton.setEnabled(True)
            self.polygon_rbutton.setChecked(True)
            self.polygon_rbutton.setEnabled(True)

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
        approved_count = 0
        refused_count = 0
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
            id = QDateTime().currentDateTime().toString("MMddhhmmss") + str(count)
            is_approved = False
            if self.__approved_parcel_check(parcel, parcel_shape_layer, id):
                is_approved = True

            header = str(count)
            if self.__get_attribute(parcel, parcel_shape_layer)[0]:
                process_type = self.__get_attribute(parcel, parcel_shape_layer)[0]
                header = header + ':' + '(' + str(process_type.code) + ')' + unicode(process_type.description)
            if self.__get_attribute(parcel, parcel_shape_layer)[1]:
                landuse = self.__get_attribute(parcel, parcel_shape_layer)[1]
            if self.__get_attribute(parcel, parcel_shape_layer)[2]:
                landname = self.__get_attribute(parcel, parcel_shape_layer)[2]
                header = header + '/' + unicode(landname) + '/'

            if is_approved:
                if self.zone_parcel_rbutton.isChecked():
                    new_parcel = LdProjectParcel()
                elif self.zone_sub_rbutton.isChecked():
                    new_parcel = LdProjectSubZone()
                elif self.zone_main_rbutton.isChecked():
                    new_parcel = LdProjectMainZone()
                new_parcel.plan_draft_id = self.plan.plan_draft_id
                new_parcel.plan_draft_ref = self.plan
                new_parcel.parcel_id = id
                new_parcel.valid_from = PluginUtils.convert_qt_date_to_python(QDateTime().currentDateTime())
                new_parcel.au1 = self.au1
                new_parcel.au2 = self.au2
                if self.zone_parcel_rbutton.isChecked():
                    if self.polygon_rbutton.isChecked():
                        new_parcel.polygon_geom = WKTElement(parcel.geometry().exportToWkt(), srid=4326)
                elif self.zone_parcel_rbutton.isChecked():
                    if self.polygon_rbutton.isChecked():
                        new_parcel.polygon_geom = WKTElement(parcel.geometry().exportToWkt(), srid=4326)
                elif self.zone_main_rbutton.isChecked():
                    if self.point_rbutton.isChecked():
                        new_parcel.point_geom = WKTElement(parcel.geometry().exportToWkt(), srid=4326)
                    elif self.line_rbutton.isChecked():
                        new_parcel.line_geom = WKTElement(parcel.geometry().exportToWkt(), srid=4326)
                    elif self.polygon_rbutton.isChecked():
                        new_parcel.polygon_geom = WKTElement(parcel.geometry().exportToWkt(), srid=4326)

                new_parcel = self.__copy_parcel_attributes(parcel, new_parcel, parcel_shape_layer)

                self.session.add(new_parcel)

                main_parcel_item = QTreeWidgetItem()
                main_parcel_item.setText(0, header)
                main_parcel_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                main_parcel_item.setData(0, Qt.UserRole, id)
                main_parcel_item.setData(0, Qt.UserRole + 1, APPROVED)
                self.approved_item.addChild(main_parcel_item)
                approved_count += 1
            else:
                main_parcel_item = QTreeWidgetItem()
                main_parcel_item.setText(0, header)
                main_parcel_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                main_parcel_item.setData(0, Qt.UserRole, id)
                main_parcel_item.setData(0, Qt.UserRole + 1, REFUSED)
                self.refused_item.addChild(main_parcel_item)
                refused_count += 1

        self.approved_item.setText(0, self.tr("Approved") + ' (' + str(approved_count) + ')')
        self.refused_item.setText(0, self.tr("Refused") + ' (' + str(refused_count) + ')')

    def __get_attribute(self, parcel_feature, layer):

        column_name_parcel_id = "id"
        column_name_plan_code = "plan_code"
        column_name_landuse = "landuse"
        column_name_landname = "landname"
        column_name_khashaa = "address_kh"
        column_name_street = "address_st"
        column_name_comment = "comment"

        column_names = {column_name_parcel_id: "", column_name_plan_code: "", column_name_landuse: "",
                        column_name_landname: "", column_name_khashaa: "", column_name_street: "",
                        column_name_comment: ""}

        parcel_geometry = WKTElement(parcel_feature.geometry().exportToWkt(), srid=4326)

        provider = layer.dataProvider()
        for key, item in column_names.iteritems():
            index = provider.fieldNameIndex(key)
            if index != -1:
                value = parcel_feature.attributes()[index]
                column_names[key] = value

        plan_code = column_names[column_name_plan_code]
        landuse_code = column_names[column_name_landuse]

        process_type = None
        if plan_code:
            count = self.session.query(LdProcessPlan).filter(LdProcessPlan.code == plan_code).count()
            if count == 1:
                process_type = self.session.query(LdProcessPlan).filter(LdProcessPlan.code == plan_code).one()
        landuse = None
        if landuse_code:
            count = self.session.query(ClLanduseType).filter(ClLanduseType.code == landuse_code).count()
            if count == 1:
                landuse = self.session.query(ClLanduseType).filter(ClLanduseType.code == landuse_code).one()
        landname = None
        if column_names[column_name_landname] != None:
            landname = column_names[column_name_landname]

        return process_type, landuse, landname

    def __approved_parcel_check(self, parcel_feature, layer, id):

        working_soum_code = DatabaseUtils.working_l2_code()
        valid = True

        column_name_parcel_id = "id"
        column_name_plan_code = "plan_code"
        column_name_landuse = "landuse"
        column_name_landname = "landname"
        column_name_khashaa = "address_kh"
        column_name_street = "address_st"
        column_name_comment = "comment"

        column_names = {column_name_parcel_id: "", column_name_plan_code: "", column_name_landuse: "",
                        column_name_landname: "", column_name_khashaa: "", column_name_street: "",
                        column_name_comment: ""}

        parcel_geometry = WKTElement(parcel_feature.geometry().exportToWkt(), srid=4326)

        provider = layer.dataProvider()
        for key, item in column_names.iteritems():
            index = provider.fieldNameIndex(key)
            if index != -1:
                value = parcel_feature.attributes()[index]
                column_names[key] = value
        error_message = u''

        try:
            if column_names[column_name_landuse] != None:
                landuse = column_names[column_name_landuse]
                if len(str(landuse).strip()) == 4:
                    count = self.session.query(ClLanduseType).filter(ClLanduseType.code == landuse).count()
                    if count == 0:
                        valid = False
                        message = unicode(u'Газрын нэгдмэл сангийн ангиллын дугаар буруу байна.')
                        error_message = error_message + "\n" + message
                        self.message_label.setText(error_message)
                else:
                    valid = False
                    message = unicode(u'Газрын нэгдмэл сангийн ангиллын дугаар буруу байна.')
                    error_message = error_message + "\n" + message
                    self.message_label.setText(error_message)
        except SQLAlchemyError, e:
            valid = False
            message = unicode(u'Газрын нэгдмэл сангийн дугаар ангиллын буруу байна.')
            error_message = error_message + "\n" + message
            self.message_label.setText(error_message)

        try:
            count = self.session.query(LdProcessPlan).filter(LdProcessPlan.code == column_names[column_name_plan_code]).count()
            if count == 0:
                valid = False
                message = unicode(u'Үйл ажиллагааны ангиллын дугаар буруу байна.')
                error_message = error_message + "\n" + message
                self.message_label.setText(error_message)
        except SQLAlchemyError, e:
            valid = False
            message = unicode(u'Үйл ажиллагааны ангиллын дугаар буруу байна.')
            error_message = error_message + "\n" + message
            self.message_label.setText(error_message)

        is_out_parcel = False
        au2_parcel_count = self.session.query(AuLevel2). \
            filter(AuLevel2.code == working_soum_code). \
            filter(parcel_geometry.ST_Within(AuLevel2.geometry)).count()
        if au2_parcel_count == 0:
            is_out_parcel = True

        if is_out_parcel:
            valid = False
            message = unicode(u'Сумын хилийн гадна байна.')
            error_message = error_message + "\n" + message
            self.message_label.setText(error_message)

        if self.zone_parcel_rbutton.isChecked():
            parcel_overlaps_count = self.session.query(LdProjectParcel).\
                filter(LdProjectParcel.plan_draft_id == self.plan.plan_draft_id).\
                filter(parcel_geometry.ST_Intersects(LdProjectParcel.polygon_geom)).count()
            if parcel_overlaps_count > 0:
                valid = False
                message = unicode(u'Нэгж талбар давхардаж байна.')
                error_message = error_message + "\n" + message

        if not valid:
            self.error_dic[id] = error_message

        return valid

    def __copy_parcel_attributes(self, parcel_feature, parcel_object, layer):

        column_name_parcel_id = "id"
        column_name_plan_code = "plan_code"
        column_name_landuse = "landuse"
        column_name_landname = "landname"
        column_name_khashaa = "address_kh"
        column_name_street = "address_st"
        column_name_comment = "comment"

        column_names = {column_name_parcel_id: "", column_name_plan_code: "", column_name_landuse: "",
                        column_name_landname: "", column_name_khashaa: "", column_name_street: "",
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
        if column_names[column_name_landname] != None:
            landname = column_names[column_name_landname]
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

    @pyqtSlot()
    def on_result_twidget_itemSelectionChanged(self):

        current_item = self.result_twidget.selectedItems()[0]
        object_type = current_item.data(0, Qt.UserRole + 1)
        object_id = current_item.data(0, Qt.UserRole)

        if object_type == REFUSED:
            self.message_label.setStyleSheet("QLabel {color: rgb(255,0,0);}")
            self.message_label.setText(self.error_dic[object_id])
        else:
            self.message_label.setStyleSheet("QLabel {color: rgb(0,71,31);}")
            self.message_label.setText(current_item.text(0))
