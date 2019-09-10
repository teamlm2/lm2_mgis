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
from ..model.PlProjectParcel import *
from ..model.ClPlanZoneType import *
from ..model.ClPlanZone import *
from ..model.PlProject import *
from ..model.SetZoneColor import *
from ..model.ClRightForm import *
from ..model.ClRightType import *
from ..model.PlSetRightFormRightType import *
from ..model.PlProjectParcelRefParcel import *
from ..model.ParcelSearch import *
from ..model.CaParcelTbl import *
from ..model.PlProjectParcelAttributeValue import *
from ..model.ClAttributeZone import *
from ..model.SetPlanZoneRelation import *
from ..model.PlBaseConditionParcel import *
from ..model.ClBaseConditionType import *
from ..model.SetPlanZoneBaseConditionType import *
from ..model.SetPlanZonePlanType import *
from ..model.PlProjectPlanZone import *
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
from ..utils.LayerUtils import LayerUtils
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
        self.file_path = None
        self.au2 = DatabaseUtils.working_l2_code()
        self.au1 = DatabaseUtils.working_l1_code()
        self.error_dic = {}
        self.polygon_rbutton.setChecked(True)

        self.message_label.setWordWrap(True)
        # self.message_label.setStyleSheet("QLabel { background-color : red; color : blue; }");
        self.message_label.setStyleSheet("QLabel {color: rgb(255,0,0);}")
        self.__setup_data()
        self.__setup_current_tree_widget()
        self.__setup_twidget()
        self.__result_twidget_setup()
        self.__setup_context_menu()
        self.__setup_cbox()
        self.main_parcels = []
        self.main_tree_widget.itemChanged.connect(self.__itemMainParcelCheckChanged)

    def reject(self):

        self.rollback()
        QDialog.reject(self)

    def __setup_data(self):

        self.plan_num_edit.setText(self.plan.code)
        self.date_edit.setText(str(self.plan.start_date))
        self.type_edit.setText(self.plan.plan_type_ref.description)
        self.status_edit.setText(self.plan.workrule_status_ref.description)

    def __setup_twidget(self):

        self.cadastre_twidget.setColumnCount(1)
        self.cadastre_twidget.setDragEnabled(True)
        self.cadastre_twidget.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.cadastre_twidget.horizontalHeader().setVisible(False)
        self.cadastre_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.cadastre_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.cadastre_twidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.cadastre_twidget.customContextMenuRequested.connect(self.on_custom_context_menu_requested)

        # self.cadastre_current_twidget.setColumnCount(1)
        self.cadastre_current_twidget.setDragEnabled(True)
        self.cadastre_current_twidget.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        # self.cadastre_current_twidget.horizontalHeader().setVisible(False)
        self.cadastre_current_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.cadastre_current_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.cadastre_current_twidget.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.cadastre_current_twidget.customContextMenuRequested.connect(self.on_custom_context_menu_requested)

    def __result_twidget_setup(self):

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

    @pyqtSlot(QPoint)
    def on_custom_context_menu_requested(self, point):

        item = self.cadastre_twidget.itemAt(point)
        if item is None: return
        self.context_menu.exec_(self.cadastre_twidget.mapToGlobal(point))

    def __itemMainParcelCheckChanged(self, item, column):

        parcel_id = item.data(0, Qt.UserRole)
        if item.checkState(column) == QtCore.Qt.Checked:
            if parcel_id not in self.main_parcels:
                self.main_parcels.append(parcel_id)
        elif item.checkState(column) == QtCore.Qt.Unchecked:
            if parcel_id in self.main_parcels:
                self.main_parcels.remove(parcel_id)

    def __setup_context_menu(self):

        self.new_menu = QMenu()
        self.new_zoom_to_selected = QAction(QIcon("zoom.png"), "New Parcel Zoom to item", self)
        self.new_menu.addAction(self.new_zoom_to_selected)
        self.new_zoom_to_selected.triggered.connect(self.new_zoom_to_selected_clicked)

        self.main_menu = QMenu()
        self.main_zoom_to_selected = QAction(QIcon("zoom.png"), "Main Parcel Zoom to item", self)
        self.main_menu.addAction(self.main_zoom_to_selected)
        self.main_zoom_to_selected.triggered.connect(self.main_zoom_to_selected_clicked)

        self.current_menu = QMenu()
        self.current_zoom_to_selected = QAction(QIcon("zoom.png"), "Current Parcel Zoom to item", self)
        self.current_menu.addAction(self.current_zoom_to_selected)
        self.current_zoom_to_selected.triggered.connect(self.current_menu_zoom_to_selected_clicked)

        self.context_menu = QMenu()
        self.zoom_to_parcel_action = QAction(QIcon(":/plugins/lm2/parcel.png"), self.tr("Zoom to parcel"), self)
        self.copy_number_action = QAction(QIcon(":/plugins/lm2/copy.png"), self.tr("Copy number"), self)
        self.context_menu.addAction(self.zoom_to_parcel_action)
        self.context_menu.addSeparator()
        self.context_menu.addAction(self.copy_number_action)
        self.zoom_to_parcel_action.triggered.connect(self.on_zoom_to_parcel_action_clicked)
        self.copy_number_action.triggered.connect(self.on_copy_number_action_clicked)

    @pyqtSlot()
    def on_copy_number_action_clicked(self):

        parcel_id = self.__selected_parcel_id()
        QApplication.clipboard().setText(parcel_id)

    @pyqtSlot(QTableWidgetItem)
    def on_zoom_to_parcel_action_clicked(self):

        parcel_id = self.__selected_parcel_id()
        self.__zoom_to_parcel_ids(parcel_id)

    def __selected_parcel_id(self):

        parcels = []
        selected_items = self.cadastre_twidget.selectedItems()

        for item in selected_items:
            parcel_no = item.data(Qt.UserRole)
            parcels.append(parcel_no)

        # if len(selected_items) != 1:
        #     self.error_label.setText(self.tr("Only single selection allowed."))
        #     return None

        # selected_item = selected_items[0]
        # parcel_no = selected_item.data(Qt.UserRole)
        return parcels

    def __zoom_to_parcel_ids(self, parcel_ids, layer_name = None):

        LayerUtils.deselect_all()
        is_temp = False
        if layer_name is None:
            for parcel_id in parcel_ids:
                if parcel_id:
                    if len(parcel_id) == 10:
                        layer_name = "ca_parcel"
                    else:
                        layer_name = "ca_tmp_parcel_view"
                        is_temp = True
                else:
                    layer_name = "ca_parcel"

        root = QgsProject.instance().layerTreeRoot()
        vlayer = LayerUtils.layer_by_data_source("data_soums_union", layer_name)

        restrictions = DatabaseUtils.working_l2_code()
        if not restrictions:
            PluginUtils.show_message(self, self.tr("Connection Error"), self.tr("Please connect to database!!!"))
            return

        if is_temp:
            if vlayer is None:
                vlayer = LayerUtils.load_tmp_layer_by_name(layer_name, "parcel_id", "data_soums_union")
            mygroup = root.findGroup(u"Кадастрын өөрчлөлт")
            myalayer = root.findLayer(vlayer.id())
            vlayer.loadNamedStyle(
                str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "template\style/ca_tmp_parcel.qml")
            vlayer.setLayerName(QApplication.translate("Plugin", "Tmp_Parcel"))
            if myalayer is None:
                mygroup.addLayer(vlayer)

            b_vlayer = LayerUtils.layer_by_data_source("data_soums_union", "ca_tmp_building_view")
            if b_vlayer is None:
                b_vlayer = LayerUtils.load_tmp_layer_by_name("ca_tmp_building_view", "building_id", "data_soums_union")
            mygroup = root.findGroup(u"Кадастрын өөрчлөлт")
            myalayer = root.findLayer(b_vlayer.id())
            b_vlayer.loadNamedStyle(
                str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "template\style/ca_tmp_building.qml")
            b_vlayer.setLayerName(QApplication.translate("Plugin", "Tmp_Building"))
            if myalayer is None:
                mygroup.addLayer(b_vlayer)

        exp_string = ""

        for parcel_id in parcel_ids:

            if exp_string == "":
                exp_string = "parcel_id = \'" + parcel_id  + "\'"
            else:
                exp_string += " or parcel_id = \'" + parcel_id  + "\'"

        request = QgsFeatureRequest()
        request.setFilterExpression(exp_string)

        feature_ids = []
        if vlayer:
            iterator = vlayer.getFeatures(request)

            for feature in iterator:
                feature_ids.append(feature.id())

            if len(feature_ids) == 0:
                self.error_label.setText(self.tr("No parcel assigned"))

            vlayer.setSelectedFeatures(feature_ids)
            self.plugin.iface.mapCanvas().zoomToSelected(vlayer)

    @pyqtSlot(QPoint)
    def on_main_tree_widget_customContextMenuRequested(self, point):

        point = self.main_tree_widget.viewport().mapToGlobal(point)
        self.main_menu.exec_(point)

    @pyqtSlot(QPoint)
    def on_current_tree_widget_customContextMenuRequested(self, point):

        point = self.current_tree_widget.viewport().mapToGlobal(point)
        self.current_menu.exec_(point)

    @pyqtSlot(QPoint)
    def on_result_twidget_customContextMenuRequested(self, point):

        if self.is_file_import:
            return

        point = self.result_twidget.viewport().mapToGlobal(point)
        self.new_menu.exec_(point)

    def __search_parent_type(self, key):

        parent_types = Constants.plan_process_type_parent
        for parent_type in parent_types:
            if key == str(parent_type):
                name = parent_types[parent_type]
                return name

    def __create_layer_group(self, root_group, group_name):

        if root_group.findGroup(group_name):
            return group_name
        else:
            return root_group.insertGroup(1, group_name)

    def __load_layer_style(self, vlayer_parcel, project_id, column_name, sql):

        sql = "select zone_code from (" + sql + " )xxx group by zone_code order by zone_code"

        categories = []
        parcels = self.session.execute(sql).fetchall()
        for row in parcels:
            badedturl = row[0]

            count = self.session.query(SetZoneColor).filter(
                SetZoneColor.code == badedturl).count()

            if count == 1:
                style = self.session.query(SetZoneColor).filter(
                    SetZoneColor.code == badedturl).one()
                fill_color = style.fill_color
                boundary_color = style.boundary_color
                opacity = 0.5
                code = str(int(style.code))
                description = str(int(style.code)) + ': ' + style.description

                self.__categorized_style(categories, vlayer_parcel, fill_color, boundary_color, opacity, code,
                                         description)

        expression = column_name  # field name
        renderer = QgsCategorizedSymbolRendererV2(expression, categories)
        vlayer_parcel.setRendererV2(renderer)

    def __categorized_style(self, categories, layer, fill_color, boundary_color, opacity, code, description):

        symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
        if symbol:
            if fill_color:
                fill_color = self.__hex_to_rgb(fill_color)
                symbol.setColor(QColor(fill_color[0], fill_color[1], fill_color[2]))
            if boundary_color:
                boundary_color = self.__hex_to_rgb(boundary_color)
                symbol.symbolLayer(0).setOutlineColor(QColor(boundary_color[0], boundary_color[1], boundary_color[2]))
            symbol.setAlpha(opacity)

            category = QgsRendererCategoryV2(code, symbol, description)
            categories.append(category)

    def __hex_to_rgb(self, value):
        """Return (red, green, blue) for the color given as #rrggbb."""
        value = value.lstrip('#')
        lv = len(value)
        return list(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    def __load_temp_layer(self, project_id, layer_name, mygroup, root, base_code):

        sql_polygon = "(select parcel_id as gid, zone.code as zone_code, zone.name, proj.code as project_code, parcel.gazner, parcel.txt, polygon_geom as geometry from data_plan.pl_project_parcel parcel " \
                      "join data_plan.pl_project proj on parcel.project_id = proj.project_id  " \
                      "join data_plan.cl_plan_zone zone on parcel.plan_zone_id = zone.plan_zone_id  " \
                      "where substring(zone.code, 1, 1) = " + base_code + " and proj.project_id = " + str(project_id) + " and polygon_geom is not null  " \
                                                                     " order by zone.code)"

        sql_point = "(select parcel_id as gid, zone.code as zone_code, zone.name, proj.code as project_code, parcel.gazner, parcel.txt, point_geom as geometry from data_plan.pl_project_parcel parcel " \
                    "join data_plan.pl_project proj on parcel.project_id = proj.project_id  " \
                    "join data_plan.cl_plan_zone zone on parcel.plan_zone_id = zone.plan_zone_id  " \
                    "where substring(zone.code, 1, 1) = " + base_code + " and proj.project_id = " + str(project_id) + " and point_geom is not null  " \
                                                                     " order by zone.code)"

        sql_line = "(select parcel_id as gid, zone.code as zone_code, zone.name, proj.code as project_code, parcel.gazner, parcel.txt, line_geom as geometry from data_plan.pl_project_parcel parcel " \
                      "join data_plan.pl_project proj on parcel.project_id = proj.project_id  " \
                      "join data_plan.cl_plan_zone zone on parcel.plan_zone_id = zone.plan_zone_id  " \
                      "where substring(zone.code, 1, 1) = " + base_code + " and proj.project_id = " + str(project_id) + " and line_geom is not null  " \
                                                                     " order by zone.code)"

        column_name = 'zone_code'
        layer_list = []
        layers = QgsMapLayerRegistry.instance().mapLayers()

        for id, layer in layers.iteritems():
            if layer.type() == QgsMapLayer.VectorLayer:
                if layer.name() == layer_name:
                    layer_list.append(id)

        if layer_name == "Polygon":
            vlayer_parcel = LayerUtils.layer_by_data_source("", sql_polygon)
            if vlayer_parcel:
                QgsMapLayerRegistry.instance().removeMapLayers(layer_list)
            vlayer_parcel = LayerUtils.load_temp_table(sql_polygon, layer_name)

            myalayer = root.findLayer(vlayer_parcel.id())
            if myalayer is None:
                mygroup.addLayer(vlayer_parcel)
                self.__load_layer_style(vlayer_parcel, project_id, column_name, sql_polygon)
        elif layer_name == "Point":
            vlayer_parcel = LayerUtils.layer_by_data_source("", sql_point)
            if vlayer_parcel:
                QgsMapLayerRegistry.instance().removeMapLayers(layer_list)
            vlayer_parcel = LayerUtils.load_temp_table(sql_point, layer_name)
            myalayer = root.findLayer(vlayer_parcel.id())
            if myalayer is None:
                mygroup.addLayer(vlayer_parcel)
                self.__load_layer_style(vlayer_parcel, project_id, column_name, sql_point)
        else:
            vlayer_parcel = LayerUtils.layer_by_data_source("", sql_line)
            if vlayer_parcel:
                QgsMapLayerRegistry.instance().removeMapLayers(layer_list)
            vlayer_parcel = LayerUtils.load_temp_table(sql_line, layer_name)
            myalayer = root.findLayer(vlayer_parcel.id())
            if myalayer is None:
                mygroup.addLayer(vlayer_parcel)
                self.__load_layer_style(vlayer_parcel, project_id, column_name, sql_line)

    @pyqtSlot()
    def main_zoom_to_selected_clicked(self):

        selected_item = self.main_tree_widget.selectedItems()[0]

        parcel_id = selected_item.data(0, Qt.UserRole)
        type = selected_item.data(0, Qt.UserRole + 1)
        plan_zone_id = selected_item.data(0, Qt.UserRole + 2)
        zone_code = selected_item.data(0, Qt.UserRole + 3)

        parent_id = str(zone_code)[:1]
        parent_name = self.__search_parent_type(parent_id)

        if selected_item is None:
            return

        project_id = self.plan_cbox.itemData(self.plan_cbox.currentIndex())
        plan = self.session.query(PlProject).filter(PlProject.project_id == project_id).one()
        group_name = plan.plan_type_ref.short_name + '/' + plan.code + '/'

        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup(group_name)

        if not group:
            LayerUtils.refresh_layer_plan()
            root_group = root.findGroup(u"Бусад ГЗБТ")
            parent_group = self.__create_layer_group(root_group, group_name)
            parent_group.setExpanded(False)

            sql = "select base_code from ( " \
                  "select substring(zone.code, 1, 1) base_code from data_plan.pl_project_parcel parcel " \
                  "join data_plan.cl_plan_zone zone on parcel.plan_zone_id = zone.plan_zone_id " \
                  "where project_id = " + str(
                project_id) + " group by zone.code order by zone.code )xxx group by base_code order by base_code "

            values = self.session.execute(sql).fetchall()
            parent_types = Constants.plan_process_type_parent
            for parent_type in parent_types:
                for row in values:
                    base_code = str(row[0])
                    if base_code == str(parent_type):
                        name = parent_types[parent_type]
                        mygroup = self.__create_layer_group(parent_group, unicode(name))
                        mygroup.setExpanded(False)
                        code = "'" + base_code + "'"
                        self.__load_temp_layer(project_id, "Point", mygroup, root, code)
                        self.__load_temp_layer(project_id, "Line", mygroup, root, code)
                        self.__load_temp_layer(project_id, "Polygon", mygroup, root, code)

        group = root.findGroup(group_name)
        for child in group.children():
            parent_group_name = child.name()
            for child in child.children():
                if isinstance(child, QgsLayerTreeLayer):
                    layer = child.layer()

                    if layer.name() == 'Polygon' and type == 'polygon':
                        if parent_group_name == parent_name:
                            column_name = 'gid'
                            self.__selected_feature(column_name, parcel_id, layer)
                    elif layer.name() == 'Point' and type == 'point':
                        if parent_group_name == parent_name:
                            column_name = 'gid'
                            self.__selected_feature(column_name, parcel_id, layer)
                    else:
                        if parent_group_name == parent_name:
                            column_name = 'gid'
                            self.__selected_feature(column_name, parcel_id, layer)


    @pyqtSlot()
    def current_menu_zoom_to_selected_clicked(self):

        selected_item = self.current_tree_widget.selectedItems()[0]

        parcel_id = selected_item.data(0, Qt.UserRole + 4)
        type = selected_item.data(0, Qt.UserRole + 1)
        if selected_item is None:
            return

        LayerUtils.deselect_all()

        schema_name = "data_plan"
        table_name = "pl_view_project_parcel"
        column_name = 'parcel_id'
        layers = QgsMapLayerRegistry.instance().mapLayers()

        for id, layer in layers.iteritems():
            if layer.type() == QgsMapLayer.VectorLayer:
                uri_string = layer.dataProvider().dataSourceUri()
                uri = QgsDataSourceURI(uri_string)
                if uri.table() == table_name:
                    if uri.schema() == schema_name:
                        self.__selected_feature(column_name, parcel_id, layer)

    def __selected_feature(self, column_name ,parcel_id, layer):

        expression = column_name + " = \'" + str(parcel_id) + "\'"

        request = QgsFeatureRequest()
        request.setFilterExpression(expression)
        feature_ids = []
        iterator = layer.getFeatures(request)

        for feature in iterator:
            feature_ids.append(feature.id())
        if len(feature_ids) == 0:
            self.status_label.setText(self.tr("No parcel assigned"))

        layer.setSelectedFeatures(feature_ids)
        self.plugin.iface.mapCanvas().zoomToSelected(layer)

    def __setup_cbox(self):

        values = self.session.query(PlProject)
        l1_code = DatabaseUtils.working_l1_code()
        l2_code = DatabaseUtils.working_l2_code()

        values = values.filter(or_(PlProject.au2 == l2_code, PlProject.au2 == None)). \
            filter(or_(PlProject.au1 == l1_code, PlProject.au1 == None)). \
            filter(PlProject.project_id != self.plan.project_id)

        for value in values.order_by(PlProject.code).all():

            description = ''
            plan_type = "" if not value.plan_type_ref else value.plan_type_ref.short_name
            au_type = ''

            if value.plan_type_ref.admin_unit_type == 2:
                if value.au1_ref:
                    au_type = ' /' + unicode(value.au1_ref.name) + '/'
            elif value.plan_type_ref.admin_unit_type == 3:
                if value.au2_ref:
                    au_type = ' /' + unicode(value.au2_ref.name) + '/'
            else:
                au_type = ''
            description = str(value.code) + au_type + " (" + unicode(plan_type) + ")"

            self.plan_cbox.addItem(description, value.project_id)

        self.zone_type_cbox.clear()
        values = self.session.query(ClPlanZoneType).order_by(ClPlanZoneType.sort_order.asc()).all()

        self.zone_type_cbox.addItem("*", -1)
        for value in values:
            self.zone_type_cbox.addItem(str(value.code) + ':' + value.name, value.plan_zone_type_id)

        self.form_type_cbox.addItem("*", -1)
        values = self.session.query(ClRightForm).all()
        for value in values:
            self.form_type_cbox.addItem(str(value.code) + ':' + value.description, value.right_form_id)
            self.form_type_change_cbox.addItem(str(value.code) + ':' + value.description, value.right_form_id)
            self.cadastre_form_type_change_cbox.addItem(str(value.code) + ':' + value.description, value.right_form_id)

        #
        self.land_use_type_cbox.clear()

        cl_landusetype = self.session.query(ClLanduseType).order_by(ClLanduseType.code).all()
        self.land_use_type_cbox.addItem("*", -1)
        if cl_landusetype is not None:
            for landuse in cl_landusetype:
                if len(str(landuse.code)) == 4:
                    self.land_use_type_cbox.addItem(str(landuse.code) + ':' + landuse.description, landuse.code)

        self.cadastre_right_type_cbox.clear()
        rigth_types = self.session.query(ClRightType).all()
        for item in rigth_types:
            self.cadastre_right_type_cbox.addItem(item.description, item.code)

        self.cad_process_type_cbox.clear()
        self.cad_process_type_cbox.addItem("*", -1)
        values = self.session.query(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
            join(PlProjectPlanZone, ClPlanZone.plan_zone_id == PlProjectPlanZone.plan_zone_id). \
            filter(PlProjectPlanZone.project_id == self.plan.project_id). \
            group_by(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
            order_by(ClPlanZone.code)
        for value in values:
            self.cad_process_type_cbox.addItem(str(value.code) + ':' + value.name, value.plan_zone_id)

    @pyqtSlot(int)
    def on_plan_cbox_currentIndexChanged(self, index):

        project_id = self.plan_cbox.itemData(self.plan_cbox.currentIndex())
        zone_type_id = self.zone_type_cbox.itemData(self.zone_type_cbox.currentIndex())

        self.main_process_type_cbox.clear()
        self.main_process_type_cbox.addItem("*", -1)

        if zone_type_id != -1:
            values = self.session.query(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                join(PlProjectParcel, ClPlanZone.plan_zone_id == PlProjectParcel.plan_zone_id). \
                filter(PlProjectParcel.project_id == project_id). \
                filter(ClPlanZone.plan_zone_type_id == zone_type_id). \
                group_by(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                order_by(ClPlanZone.code)
            for value in values:
                self.main_process_type_cbox.addItem(str(value.code) + ':' + value.name, value.plan_zone_id)
        elif zone_type_id == -1:
            values = self.session.query(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                join(PlProjectParcel, ClPlanZone.plan_zone_id == PlProjectParcel.plan_zone_id). \
                filter(PlProjectParcel.project_id == project_id). \
                group_by(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                order_by(ClPlanZone.code)
            for value in values:
                self.main_process_type_cbox.addItem(str(value.code) + ':' + value.name, value.plan_zone_id)

    @pyqtSlot(int)
    def on_zone_type_cbox_currentIndexChanged(self, index):

        project_id = self.plan_cbox.itemData(self.plan_cbox.currentIndex())
        zone_type_id = self.zone_type_cbox.itemData(index)

        self.main_process_type_cbox.clear()
        self.main_process_type_cbox.addItem("*", -1)

        if zone_type_id != -1:
            values = self.session.query(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                join(PlProjectParcel, ClPlanZone.plan_zone_id == PlProjectParcel.plan_zone_id). \
                filter(PlProjectParcel.project_id == project_id). \
                filter(ClPlanZone.plan_zone_type_id == zone_type_id). \
                group_by(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                order_by(ClPlanZone.code)
            for value in values:
                self.main_process_type_cbox.addItem(str(value.code) + ':' + value.name, value.plan_zone_id)
        elif zone_type_id == -1:
            values = self.session.query(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                join(PlProjectParcel, ClPlanZone.plan_zone_id == PlProjectParcel.plan_zone_id). \
                filter(PlProjectParcel.project_id == project_id). \
                group_by(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                order_by(ClPlanZone.code)
            for value in values:
                self.main_process_type_cbox.addItem(str(value.code) + ':' + value.name, value.plan_zone_id)

    @pyqtSlot()
    def on_find_button_clicked(self):

        self.main_load_pbar.setVisible(True)
        self.main_load_pbar.setMinimum(1)
        self.main_load_pbar.setValue(0)

        au2 = DatabaseUtils.working_l2_code()
        self.__setup_main_tree_widget()
        self.__setup_current_tree_widget()
        self.__load_main_zone(au2)
        self.__load_current_zone(au2)

    def __load_current_zone(self, au2):

        self.__load_current_polygon()
        self.__load_current_point()
        self.__load_current_line()

    def __load_current_line(self):

        lines = self.session.query(PlProjectParcel). \
            filter(PlProjectParcel.project_id == self.plan.project_id). \
            filter(PlProjectParcelRefParcel.is_cadastre == False). \
            filter(PlProjectParcel.polygon_geom == None). \
            filter(PlProjectParcel.point_geom == None).order_by(PlProjectParcel.badedturl)

        for value in lines:
            plan = value.project_ref
            plan_type = "" if not plan.plan_type_ref else plan.plan_type_ref.short_name
            au_type = ''

            if plan.plan_type_ref.admin_unit_type == 2:
                if plan.au1_ref:
                    au_type = ' /' + unicode(plan.au1_ref.name) + '/'
            elif plan.plan_type_ref.admin_unit_type == 3:
                if plan.au2_ref:
                    au_type = ' /' + unicode(plan.au2_ref.name) + '/'
            else:
                au_type = ''
            description = str(plan.code) + au_type + " (" + unicode(plan_type) + ")"
            form_type_desc = "" if not value.right_form_ref else value.right_form_ref.description
            form_type_id = None if not value.right_form_ref else value.right_form_ref.right_form_id

            name = ''
            if value.gazner:
                name = '(' + value.gazner + ')'
            if value.plan_zone_ref:
                if value.plan_zone_ref.name:
                    desc = value.plan_zone_ref.name
                    item = QTreeWidgetItem()
                    item.setText(0, '/' + str(value.parcel_id) + '/' + str(value.plan_zone_ref.code) + ': ' + name + desc)
                    item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                    item.setData(0, Qt.UserRole + 4, value.parcel_id)
                    item.setData(0, Qt.UserRole + 1, "polygon")
                    item.setData(0, Qt.UserRole + 2, value.plan_zone_id)
                    item.setData(0, Qt.UserRole + 3, value.plan_zone_ref.code)

                    item.setText(1, form_type_desc)
                    item.setData(1, Qt.UserRole, form_type_id)

                    item.setText(2, description)
                    item.setData(2, Qt.UserRole, plan.project_id)

                    item.setCheckState(0, Qt.Checked)
                    item.setCheckState(0, Qt.Unchecked)
                    self.item_line_current.addChild(item)

    def __load_current_point(self):

        points = self.session.query(PlProjectParcel). \
            join(PlProjectParcelRefParcel, PlProjectParcel.parcel_id == PlProjectParcelRefParcel.parcel_id). \
            filter(PlProjectParcel.project_id == self.plan.project_id). \
            filter(PlProjectParcelRefParcel.is_cadastre == False). \
            filter(PlProjectParcel.polygon_geom == None). \
            filter(PlProjectParcel.line_geom == None).order_by(PlProjectParcel.badedturl)

        for value in points:
            plan = value.project_ref
            plan_type = "" if not plan.plan_type_ref else plan.plan_type_ref.short_name
            au_type = ''

            if plan.plan_type_ref.admin_unit_type == 2:
                if plan.au1_ref:
                    au_type = ' /' + unicode(plan.au1_ref.name) + '/'
            elif plan.plan_type_ref.admin_unit_type == 3:
                if plan.au2_ref:
                    au_type = ' /' + unicode(plan.au2_ref.name) + '/'
            else:
                au_type = ''
            description = str(plan.code) + au_type + " (" + unicode(plan_type) + ")"
            form_type_desc = "" if not value.right_form_ref else value.right_form_ref.description
            form_type_id = None if not value.right_form_ref else value.right_form_ref.right_form_id

            name = ''
            if value.gazner:
                name = '(' + value.gazner + ')'
            if value.plan_zone_ref:
                if value.plan_zone_ref.name:
                    desc = value.plan_zone_ref.name
                    item = QTreeWidgetItem()
                    item.setText(0, '/' + str(value.parcel_id) + '/' + str(value.plan_zone_ref.code) + ': ' + name + desc)
                    item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                    item.setData(0, Qt.UserRole + 4, value.parcel_id)
                    item.setData(0, Qt.UserRole + 1, "polygon")
                    item.setData(0, Qt.UserRole + 2, value.plan_zone_id)
                    item.setData(0, Qt.UserRole + 3, value.plan_zone_ref.code)

                    item.setText(1, form_type_desc)
                    item.setData(1, Qt.UserRole, form_type_id)

                    item.setText(2, description)
                    item.setData(2, Qt.UserRole, plan.project_id)

                    item.setCheckState(0, Qt.Checked)
                    item.setCheckState(0, Qt.Unchecked)
                    self.item_point_current.addChild(item)

    def __load_current_polygon(self):

        polygons = self.session.query(PlProjectParcel). \
            join(PlProjectParcelRefParcel, PlProjectParcel.parcel_id == PlProjectParcelRefParcel.parcel_id). \
            filter(PlProjectParcel.project_id == self.plan.project_id). \
            filter(PlProjectParcelRefParcel.is_cadastre == False). \
            filter(PlProjectParcel.line_geom == None). \
            filter(PlProjectParcel.point_geom == None).order_by(PlProjectParcel.badedturl)

        for value in polygons:
            plan = value.project_ref
            plan_type = "" if not plan.plan_type_ref else plan.plan_type_ref.short_name
            au_type = ''

            if plan.plan_type_ref.admin_unit_type == 2:
                if plan.au1_ref:
                    au_type = ' /' + unicode(plan.au1_ref.name) + '/'
            elif plan.plan_type_ref.admin_unit_type == 3:
                if plan.au2_ref:
                    au_type = ' /' + unicode(plan.au2_ref.name) + '/'
            else:
                au_type = ''
            description = str(plan.code) + au_type + " (" + unicode(plan_type) + ")"
            form_type_desc = "" if not value.right_form_ref else value.right_form_ref.description
            form_type_id = None if not value.right_form_ref else value.right_form_ref.right_form_id

            name = ''
            if value.gazner:
                name = '(' + value.gazner + ')'
            if value.plan_zone_ref:
                if value.plan_zone_ref.name:
                    desc = value.plan_zone_ref.name
                    item = QTreeWidgetItem()
                    item.setText(0, '/' + str(value.parcel_id) + '/' + str(value.plan_zone_ref.code) + ': ' + name + desc)
                    item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                    item.setData(0, Qt.UserRole + 4, value.parcel_id)
                    item.setData(0, Qt.UserRole + 1, "polygon")
                    item.setData(0, Qt.UserRole + 2, value.plan_zone_id)
                    item.setData(0, Qt.UserRole + 3, value.plan_zone_ref.code)

                    item.setText(1, form_type_desc)
                    item.setData(1, Qt.UserRole, form_type_id)

                    item.setText(2, description)
                    item.setData(2, Qt.UserRole, plan.project_id)

                    item.setCheckState(0, Qt.Checked)
                    item.setCheckState(0, Qt.Unchecked)
                    self.item_polygon_current.addChild(item)

    def __load_main_zone(self, au2):

        project_id = self.plan_cbox.itemData(self.plan_cbox.currentIndex())
        self.main_load_pbar.setValue(1)

        values = self.session.query(PlProjectParcel). \
            filter(PlProjectParcel.project_id == project_id)

        self.main_load_pbar.setMaximum(values.count())

        points = self.session.query(PlProjectParcel). \
            filter(PlProjectParcel.project_id == project_id). \
            filter(PlProjectParcel.polygon_geom == None). \
            filter(PlProjectParcel.line_geom == None).order_by(PlProjectParcel.badedturl)

        lines = self.session.query(PlProjectParcel). \
            filter(PlProjectParcel.project_id == project_id). \
            filter(PlProjectParcel.polygon_geom == None). \
            filter(PlProjectParcel.point_geom == None).order_by(PlProjectParcel.badedturl)

        polygons = self.session.query(PlProjectParcel). \
            filter(PlProjectParcel.project_id == project_id). \
            filter(PlProjectParcel.line_geom == None). \
            filter(PlProjectParcel.point_geom == None).order_by(PlProjectParcel.badedturl)

        if self.main_process_type_cbox.currentIndex() != -1:
            if not self.main_process_type_cbox.itemData(self.main_process_type_cbox.currentIndex()) == -1:
                process_type = self.main_process_type_cbox.itemData(self.main_process_type_cbox.currentIndex())

                points = points.filter(PlProjectParcel.plan_zone_id == process_type)
                lines = lines.filter(PlProjectParcel.plan_zone_id == process_type)
                polygons = polygons.filter(PlProjectParcel.plan_zone_id == process_type)

        tree = self.main_tree_widget
        for value in polygons:
            name = ''
            if value.gazner:
                name = '(' + value.gazner + ')'
            desc = ''
            if value.plan_zone_ref:
                if value.plan_zone_ref.name:
                    desc = value.plan_zone_ref.name
                    item = QTreeWidgetItem()
                    item.setText(0, '/' + str(value.parcel_id) + '/' + str(value.plan_zone_ref.code)+ ': ' + name + desc)
                    item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                    item.setData(0, Qt.UserRole, value.parcel_id)
                    item.setData(0, Qt.UserRole + 1, "polygon")
                    item.setData(0, Qt.UserRole + 2, value.plan_zone_id)
                    item.setData(0, Qt.UserRole + 3, value.plan_zone_ref.code)
                    item.setCheckState(0, Qt.Unchecked)
                    self.item_polygon_main.addChild(item)
                    value_p = self.main_load_pbar.value() + 1
                    self.main_load_pbar.setValue(value_p)

        for value in points:
            name = ''
            if value.gazner:
                name = '(' + value.gazner + ')'
            desc = ''
            if value.plan_zone_ref:
                if value.plan_zone_ref.name:
                    desc = value.plan_zone_ref.name
                    item = QTreeWidgetItem()
                    item.setText(0, '/' + str(value.parcel_id) + '/' + str(value.plan_zone_ref.code)+ ': ' + name + desc)
                    item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                    item.setData(0, Qt.UserRole, value.parcel_id)
                    item.setData(0, Qt.UserRole + 1, "point")
                    item.setData(0, Qt.UserRole + 2, value.plan_zone_id)
                    item.setData(0, Qt.UserRole + 3, value.plan_zone_ref.code)
                    item.setCheckState(0, Qt.Unchecked)
                    self.item_point_main.addChild(item)
                    value_p = self.main_load_pbar.value() + 1
                    self.main_load_pbar.setValue(value_p)

        for value in lines:
            name = ''
            if value.gazner:
                name = '(' + value.gazner + ')'
            desc = ''
            if value.plan_zone_ref:
                if value.plan_zone_ref.name:
                    desc = value.plan_zone_ref.name
                    item = QTreeWidgetItem()
                    item.setText(0, '/' + str(value.parcel_id) + '/' + str(value.plan_zone_ref.code)+ ': ' + name + desc)
                    item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                    item.setData(0, Qt.UserRole, value.parcel_id)
                    item.setData(0, Qt.UserRole + 1, "line")
                    item.setData(0, Qt.UserRole + 2, value.plan_zone_id)
                    item.setData(0, Qt.UserRole + 3, value.plan_zone_ref.code)
                    item.setCheckState(0, Qt.Unchecked)
                    self.item_line_main.addChild(item)
                    value_p = self.main_load_pbar.value() + 1
                    self.main_load_pbar.setValue(value_p)

        self.main_tree_widget.expandAll()
        self.main_load_pbar.setVisible(False)

    def __setup_current_tree_widget(self):

        self.current_tree_widget.clear()

        self.item_point_current = QTreeWidgetItem()
        self.item_point_current.setText(0, self.tr("Point"))
        self.item_point_current.setData(0, Qt.UserRole, Constants.GEOM_POINT)

        self.item_line_current = QTreeWidgetItem()
        self.item_line_current.setText(0, self.tr("Line"))
        self.item_line_current.setData(0, Qt.UserRole, Constants.GEOM_LINE)

        self.item_polygon_current = QTreeWidgetItem()
        self.item_polygon_current.setText(0, self.tr("Polygon"))
        self.item_polygon_current.setData(0, Qt.UserRole, Constants.GEOM_POlYGON)

        self.current_tree_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.current_tree_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.current_tree_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.current_tree_widget.addTopLevelItem(self.item_point_current)
        self.current_tree_widget.addTopLevelItem(self.item_line_current)
        self.current_tree_widget.addTopLevelItem(self.item_polygon_current)
        self.current_tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)

    def __setup_main_tree_widget(self):

        self.main_tree_widget.clear()

        self.item_point_main = QTreeWidgetItem()
        self.item_point_main.setText(0, self.tr("Point"))
        self.item_point_main.setData(0, Qt.UserRole, Constants.GEOM_POINT)

        self.item_line_main = QTreeWidgetItem()
        self.item_line_main.setText(0, self.tr("Line"))
        self.item_line_main.setData(0, Qt.UserRole, Constants.GEOM_LINE)

        self.item_polygon_main = QTreeWidgetItem()
        self.item_polygon_main.setText(0, self.tr("Polygon"))
        self.item_polygon_main.setData(0, Qt.UserRole, Constants.GEOM_POlYGON)

        self.main_tree_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.main_tree_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.main_tree_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.main_tree_widget.addTopLevelItem(self.item_point_main)
        self.main_tree_widget.addTopLevelItem(self.item_line_main)
        self.main_tree_widget.addTopLevelItem(self.item_polygon_main)
        self.main_tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)

    def __validaty_of_new_parcel(self, parcel, parcel_shape_layer, id):

        valid = True
        plan_zone_message = unicode(u'* (ЗӨВШӨӨРӨГДӨХГҮЙ БҮС/АРГА ХЭМЖЭЭ/) ')
        base_condition_message = unicode(u'* (ЗӨВШӨӨРӨГДӨХГҮЙ ХАМГААЛЛАЛТЫН БҮС/ЗУРВАС/) ')
        error_message = u''

        check_value = self.__approved_parcel_check(parcel, parcel_shape_layer, id, error_message)
        if not check_value[0]:
            valid = False
            error_message = error_message + "\n" + check_value[1]
        plan_zone_id = None
        if self.if_single_type_chbox.isChecked():
            code = self.shp_process_type_cbox.itemData(self.shp_process_type_cbox.currentIndex())
            plan_zone_count = self.session.query(ClPlanZone).filter(ClPlanZone.code == code).count()
            if plan_zone_count == 1:
                plan_zone = self.session.query(ClPlanZone).filter(ClPlanZone.code == code).one()
                plan_zone_id = plan_zone.plan_zone_id
        else:
            process_type = self.__get_attribute(parcel, parcel_shape_layer)[0]
            if process_type:
                plan_zone_id = process_type.plan_zone_id

        if not parcel.geometry():
            valid = False
        else:
            g = parcel.geometry()
            if not g.isGeosValid():
                valid = False
            else:
                parcel_geometry = WKTElement(parcel.geometry().exportToWkt(), srid=4326)
                # if parcel_geometry.IsValid() == True:
                #     valid = False
                #     print parcel_geometry.IsValid()
                # parcel overlap not approved plan zone

                polygon_values = self.session.query(PlProjectParcel). \
                    filter(func.ST_Centroid(parcel_geometry).ST_Overlaps(PlProjectParcel.polygon_geom)).\
                    filter(PlProjectParcel.valid_till == None).all()
                for value in polygon_values:
                    plan_zone = value.plan_zone_ref
                    project = value.project_ref
                    if project:
                        plan_type = project.plan_type_ref
                        plan_zone_relation_count = self.session.query(SetPlanZoneRelation). \
                            filter(SetPlanZoneRelation.parent_plan_zone_id == plan_zone.plan_zone_id).\
                            filter(SetPlanZoneRelation.child_plan_zone_id == plan_zone_id).count()
                        if plan_zone_relation_count == 0:
                            message = plan_zone_message + value.project_ref.code + unicode(u' дугаартай ') + plan_type.short_name + \
                                    unicode(u'-ний ') + \
                                    '/'+plan_zone.code+'/' + unicode(plan_zone.name) + unicode(u' арга хэмжээтэй давхцаж байна.')
                            error_message = error_message + "\n" + message
                            valid = False

                point_values = self.session.query(PlProjectParcel). \
                    filter(func.ST_Centroid(parcel_geometry).ST_Overlaps(PlProjectParcel.point_geom)). \
                    filter(PlProjectParcel.valid_till == None).all()
                for value in point_values:
                    plan_zone = value.plan_zone_ref
                    project = value.project_ref
                    plan_type = project.plan_type_ref
                    plan_zone_relation_count = self.session.query(SetPlanZoneRelation). \
                        filter(SetPlanZoneRelation.parent_plan_zone_id == plan_zone.plan_zone_id). \
                        filter(SetPlanZoneRelation.child_plan_zone_id == plan_zone_id).count()
                    if plan_zone_relation_count == 0:
                        message = plan_zone_message + value.project_ref.code + unicode(u' дугаартай ') + plan_type.short_name + \
                                  unicode(u'-ний ') + \
                                  '/' + plan_zone.code + '/' + unicode(plan_zone.name) + unicode(u' арга хэмжээтэй давхцаж байна.')
                        error_message = error_message + "\n" + message
                        valid = False

                line_values = self.session.query(PlProjectParcel). \
                    filter(func.ST_Centroid(parcel_geometry).ST_Overlaps(PlProjectParcel.line_geom)). \
                    filter(PlProjectParcel.valid_till == None).all()
                for value in line_values:
                    plan_zone = value.plan_zone_ref
                    project = value.project_ref
                    plan_type = project.plan_type_ref
                    plan_zone_relation_count = self.session.query(SetPlanZoneRelation). \
                        filter(SetPlanZoneRelation.parent_plan_zone_id == plan_zone.plan_zone_id). \
                        filter(SetPlanZoneRelation.child_plan_zone_id == plan_zone_id).count()
                    if plan_zone_relation_count == 0:
                        message = plan_zone_message + value.project_ref.code + unicode(u' дугаартай ') + plan_type.short_name + \
                                  unicode(u'-ний ') + \
                                  '/' + plan_zone.code + '/' + unicode(plan_zone.name) + unicode(u' арга хэмжээтэй давхцаж байна.')
                        error_message = error_message + "\n" + message
                        valid = False

                # base condition overlaps
                values = self.session.query(PlBaseConditionParcel).\
                    filter(func.ST_Centroid(parcel_geometry).ST_Overlaps(PlBaseConditionParcel.geometry)).all()

                for value in values:
                    type = value.base_condition_type_ref
                    count = self.session.query(SetPlanZoneBaseConditionType).\
                        filter(SetPlanZoneBaseConditionType.plan_zone_id == plan_zone_id). \
                        filter(SetPlanZoneBaseConditionType.base_condition_type_id == type.base_condition_type_id).count()
                    if count == 1:
                        message = base_condition_message + type.short_name + unicode(u' -тэй давхцаж байна. ')
                        error_message = error_message + "\n" + message
                        valid = False

        if not valid:
            self.error_dic[id] = error_message

        return valid, error_message

    def __add_new_parcel(self, parcel, parcel_shape_layer):

        new_parcel = PlProjectParcel()

        new_parcel.project_id = self.plan.project_id
        new_parcel.project_ref = self.plan
        new_parcel.valid_from = PluginUtils.convert_qt_date_to_python(QDateTime().currentDateTime())
        new_parcel.au1 = self.au1
        new_parcel.au2 = self.au2
        new_parcel.created_at = DatabaseUtils.current_date_time()
        new_parcel.created_by = DatabaseUtils.current_sd_user().user_id
        if self.point_rbutton.isChecked():
            new_parcel.point_geom = WKTElement(parcel.geometry().exportToWkt(), srid=4326)
        elif self.line_rbutton.isChecked():
            new_parcel.line_geom = WKTElement(parcel.geometry().exportToWkt(), srid=4326)
        elif self.polygon_rbutton.isChecked():
            new_parcel.polygon_geom = WKTElement(parcel.geometry().exportToWkt(), srid=4326)

        self.__copy_parcel_attributes(parcel, new_parcel, parcel_shape_layer)

        self.session.add(new_parcel)
        self.session.flush()
        return new_parcel

    def __add_new_parcel_attributes(self, parcel, new_parcel, provider):

        fields = provider.fields()
        for field in fields:

            key = field.name()
            index = provider.fieldNameIndex(key)
            attribute_value = parcel.attributes()[index]
            if attribute_value:
                attribute_count = self.session.query(ClAttributeZone).filter(ClAttributeZone.attribute_name == str(key)).count()
                if attribute_count > 0:
                    attribute = self.session.query(ClAttributeZone).filter(ClAttributeZone.attribute_name == key).first()
                    attribute_id = attribute.attribute_id
                    count = self.session.query(PlProjectParcelAttributeValue).\
                        filter(PlProjectParcelAttributeValue.parcel_id == new_parcel.parcel_id).\
                        filter(PlProjectParcelAttributeValue.attribute_id == attribute_id).count()
                    if count == 0:
                        parcel_attribute_value = PlProjectParcelAttributeValue()
                        parcel_attribute_value.attribute_id = attribute_id
                        parcel_attribute_value.parcel_id = new_parcel.parcel_id
                        parcel_attribute_value.attribute_value = attribute_value
                        parcel_attribute_value.created_at = DatabaseUtils.current_date_time()
                        parcel_attribute_value.created_by = DatabaseUtils.current_sd_user().user_id
                        self.session.add(parcel_attribute_value)
                    else:
                        parcel_attribute_value = self.session.query(PlProjectParcelAttributeValue). \
                            filter(PlProjectParcelAttributeValue.parcel_id == new_parcel.parcel_id). \
                            filter(PlProjectParcelAttributeValue.attribute_id == attribute_id).first()

                        parcel_attribute_value.attribute_value = attribute_value
                        parcel_attribute_value.updated_at = DatabaseUtils.current_date_time()
                        parcel_attribute_value.updated_by = DatabaseUtils.current_sd_user().user_id

    def __import_template_data(self, file_path):

        self.result_twidget.clear()
        self.__result_twidget_setup()
        # SessionHandler().destroy_session()
        self.session = SessionHandler().session_instance()
        parcel_shape_layer = QgsVectorLayer(file_path, "tmp_parcel_shape", "ogr")

        if not parcel_shape_layer.isValid():
            # PluginUtils.show_error(self, self.tr("Error loading layer"), self.tr("The layer is invalid."))
            return

        if parcel_shape_layer.crs().postgisSrid() != 4326:
            PluginUtils.show_error(self, self.tr("Error loading layer"),
                                   self.tr("The crs of the layer has to be 4326."))
            return

        iterator = parcel_shape_layer.getFeatures()
        provider = parcel_shape_layer.dataProvider()

        # if self.if_single_type_chbox.isChecked():
        #     self.__shp_edit_attribute(parcel_shape_layer)

        fieldNames = []
        fields = provider.fields()
        for field in fields:
            fieldNames.append(field.name())

        count = 0
        approved_count = 0
        refused_count = 0

        for parcel in iterator:
            feature_id = parcel.id()
            count += 1
            id = QDateTime().currentDateTime().toString("MMddhhmmss") + str(count)
            header = str(count)
            if self.if_single_type_chbox.isChecked():
                header = self.shp_process_type_cbox.currentText()
            else:
                if self.__get_attribute(parcel, parcel_shape_layer)[0]:
                    process_type = self.__get_attribute(parcel, parcel_shape_layer)[0]
                    header = header + ':' + '(' + str(process_type.code) + ')' + unicode(process_type.name)
                if self.__get_attribute(parcel, parcel_shape_layer)[2]:
                    landname = self.__get_attribute(parcel, parcel_shape_layer)[2]
                    header = header + '/' + unicode(landname) + '/'

            validaty_result = self.__validaty_of_new_parcel(parcel, parcel_shape_layer, feature_id)
            if validaty_result[0]:
                # new_parcel = self.__add_new_parcel(parcel, parcel_shape_layer)
                # self.__add_new_parcel_attributes(parcel, new_parcel, provider)

                main_parcel_item = QTreeWidgetItem()
                main_parcel_item.setText(0, header)
                main_parcel_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                main_parcel_item.setData(0, Qt.UserRole, feature_id)
                main_parcel_item.setData(0, Qt.UserRole + 1, APPROVED)
                main_parcel_item.setData(0, Qt.UserRole + 2, feature_id)
                main_parcel_item.setToolTip(0, header)
                self.approved_item.addChild(main_parcel_item)
                approved_count += 1
            else:
                main_parcel_item = QTreeWidgetItem()
                main_parcel_item.setText(0, header)
                main_parcel_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                main_parcel_item.setData(0, Qt.UserRole, feature_id)
                main_parcel_item.setData(0, Qt.UserRole + 1, REFUSED)
                main_parcel_item.setData(0, Qt.UserRole + 2, feature_id)
                main_parcel_item.setToolTip(0, header)
                self.refused_item.addChild(main_parcel_item)
                refused_count += 1

        self.approved_item.setText(0, self.tr("Approved") + ' (' + str(approved_count) + ')')
        self.refused_item.setText(0, self.tr("Refused") + ' (' + str(refused_count) + ')')

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
            self.file_path = file_path
            # self.__import_new_parcels(file_path)

            self.__import_template_data(file_path)
            # self.open_parcel_file_button.setEnabled(False)

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

            count += 1
            id = QDateTime().currentDateTime().toString("MMddhhmmss") + str(count)

            header = str(count)
            if self.__get_attribute(parcel, parcel_shape_layer)[0]:
                process_type = self.__get_attribute(parcel, parcel_shape_layer)[0]
                header = header + ':' + '(' + str(process_type.code) + ')' + unicode(process_type.name)
            if self.__get_attribute(parcel, parcel_shape_layer)[1]:
                landuse = self.__get_attribute(parcel, parcel_shape_layer)[1]
            if self.__get_attribute(parcel, parcel_shape_layer)[2]:
                landname = self.__get_attribute(parcel, parcel_shape_layer)[2]
                header = header + '/' + unicode(landname) + '/'
            if self.__approved_parcel_check(parcel, parcel_shape_layer, id, ''):

                new_parcel = PlProjectParcel()

                new_parcel.project_id = self.plan.project_id
                new_parcel.project_ref = self.plan
                # new_parcel.parcel_id = id
                new_parcel.valid_from = PluginUtils.convert_qt_date_to_python(QDateTime().currentDateTime())
                new_parcel.au1 = self.au1
                new_parcel.au2 = self.au2

                if self.point_rbutton.isChecked():
                    new_parcel.point_geom = WKTElement(parcel.geometry().exportToWkt(), srid=4326)
                elif self.line_rbutton.isChecked():
                    new_parcel.line_geom = WKTElement(parcel.geometry().exportToWkt(), srid=4326)
                elif self.polygon_rbutton.isChecked():
                    new_parcel.polygon_geom = WKTElement(parcel.geometry().exportToWkt(), srid=4326)

                self.__copy_parcel_attributes(parcel, new_parcel, parcel_shape_layer)

                self.session.add(new_parcel)
                self.session.flush()

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
        column_name_plan_code = "badedturl"
        column_name_landuse = "landuse"
        column_name_landname = "gaz_add"
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

        plan_code = column_names[column_name_plan_code]
        landuse_code = column_names[column_name_landuse]

        process_type = None
        if plan_code:
            count = self.session.query(ClPlanZone).filter(ClPlanZone.code == plan_code).count()
            if count == 1:
                process_type = self.session.query(ClPlanZone).filter(ClPlanZone.code == plan_code).one()
        landuse = None
        if landuse_code:
            count = self.session.query(ClLanduseType).filter(ClLanduseType.code == landuse_code).count()
            if count == 1:
                landuse = self.session.query(ClLanduseType).filter(ClLanduseType.code == landuse_code).one()
        landname = None
        if column_names[column_name_landname] != None:
            landname = column_names[column_name_landname]

        return process_type, landuse, landname

    def __approved_parcel_check(self, parcel_feature, layer, id, error_message):

        working_soum_code = DatabaseUtils.working_l2_code()
        valid = True

        column_name_parcel_id = "id"
        column_name_plan_code = "badedturl"
        column_name_landuse = "landuse"
        column_name_landname = "gaz_add"
        column_name_khashaa = "address_kh"
        column_name_street = "address_st"
        column_name_comment = "comment"

        column_names = {column_name_parcel_id: "", column_name_plan_code: "", column_name_landuse: "",
                        column_name_landname: "", column_name_khashaa: "", column_name_street: "",
                        column_name_comment: ""}

        # geom = parcel_feature.GetGeometryRef()
        # if not geom.IsValid():
        #     parcel_feature.SetGeometry(geom.Buffer(0))  # <====== SetGeometry
        #     layer.SetFeature(parcel_feature)  # <====== SetFeature
        #     assert parcel_feature.GetGeometryRef().IsValid()  # Doesn't fail
        if not parcel_feature.geometry():
            valid = False
            message = '*' + unicode(u' Геометр алдаатай.')
            error_message = error_message + "\n" + message
            self.message_label.setText(error_message)
        else:
            g = parcel_feature.geometry()
            if not g.isGeosValid():
                valid = False
                message = '*' + unicode(u' Геометр алдаатай.')
                error_message = error_message + "\n" + message
                self.message_label.setText(error_message)
            else:
                parcel_geometry = WKTElement(parcel_feature.geometry().exportToWkt(), srid=4326)

                provider = layer.dataProvider()
                for key, item in column_names.iteritems():
                    index = provider.fieldNameIndex(key)
                    if index != -1:
                        value = parcel_feature.attributes()[index]
                        column_names[key] = value

                # try:
                # if column_names[column_name_landuse] != None:
                #     landuse = column_names[column_name_landuse]
                #     if len(str(landuse).strip()) == 4:
                #         count = self.session.query(ClLanduseType).filter(ClLanduseType.code == landuse).count()
                #         if count == 0:
                #             valid = False
                #             message = unicode(u'Газрын нэгдмэл сангийн ангиллын дугаар буруу байна.')
                #             error_message = error_message + "\n" + message
                #             self.message_label.setText(error_message)
                #     else:
                #         valid = False
                #         message = unicode(u'Газрын нэгдмэл сангийн ангиллын дугаар буруу байна.')
                #         error_message = error_message + "\n" + message
                #         self.message_label.setText(error_message)
                # except SQLAlchemyError, e:
                #     valid = False
                #     message = unicode(u'Газрын нэгдмэл сангийн дугаар ангиллын буруу байна.')
                #     error_message = error_message + "\n" + message
                #     self.message_label.setText(error_message)

                # try:
                if not self.if_single_type_chbox.isChecked():
                    if column_names[column_name_plan_code]:
                        count = self.session.query(ClPlanZone).filter(ClPlanZone.code == column_names[column_name_plan_code]).count()
                        if count == 0:
                            valid = False
                            message = '*' + unicode(u' Үйл ажиллагааны ангиллын дугаар буруу байна.')
                            error_message = error_message + "\n" + message
                            self.message_label.setText(error_message)
                    else:
                        valid = False
                        message = '*' + unicode(u' Үйл ажиллагааны ангиллын дугаар буруу байна.')
                        error_message = error_message + "\n" + message
                        self.message_label.setText(error_message)
                # except SQLAlchemyError, e:
                #     valid = False
                #     message = unicode(u'Үйл ажиллагааны ангиллын дугаар буруу байна.')
                #     error_message = error_message + "\n" + message
                #     self.message_label.setText(error_message)

                is_out_parcel = False
                au2_parcel_count = self.session.query(AuLevel2). \
                    filter(AuLevel2.code == working_soum_code). \
                    filter(func.ST_Centroid(parcel_geometry).ST_Within(AuLevel2.geometry)).count()
                if au2_parcel_count == 0:
                    is_out_parcel = True

                if is_out_parcel:
                    valid = False
                    message = '*' + unicode(u' Сумын хилийн гадна байна.')
                    error_message = error_message + "\n" + message
                    self.message_label.setText(error_message)

                parcel_overlaps_count = self.session.query(PlProjectParcel).\
                    join(PlProject, PlProjectParcel.project_id == PlProject.project_id). \
                    filter(PlProjectParcel.project_id == self.plan.project_id).\
                    filter(func.ST_Centroid(parcel_geometry).ST_Covers(PlProjectParcel.polygon_geom)).count()
                if parcel_overlaps_count > 0:
                    valid = False
                    message = '*' + unicode(u' Нэгж талбар давхардаж байна.')

                    error_message = error_message + "\n" + message

                # if not valid:
                #     self.error_dic[id] = error_message

        return valid, error_message

    def __copy_parcel_attributes(self, parcel, new_parcel, parcel_shape_layer):

        column_name_parcel_id = "id"
        column_name_plan_code = "badedturl"
        column_name_landuse = "landuse"
        column_name_landname = "gaz_add"
        column_name_khashaa = "address_kh"
        column_name_street = "address_st"
        column_name_comment = "comment"

        column_names = {column_name_parcel_id: "", column_name_plan_code: "", column_name_landuse: "",
                        column_name_landname: "", column_name_khashaa: "", column_name_street: "",
                        column_name_comment: ""}

        provider = parcel_shape_layer.dataProvider()
        for key, item in column_names.iteritems():
            index = provider.fieldNameIndex(key)
            if index != -1:
                value = parcel.attributes()[index]
                column_names[key] = value

        id = 0
        plan_code = ''
        landuse = None
        landname = ''
        address_khashaa = 0
        address_streetname = ''
        comment = ''
        plan_zone_id = None

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

        if self.if_single_type_chbox.isChecked():
            code = self.shp_process_type_cbox.itemData(self.shp_process_type_cbox.currentIndex())
            plan_zone_count = self.session.query(ClPlanZone).filter(ClPlanZone.code == code).count()
            if plan_zone_count == 1:
                plan_zone = self.session.query(ClPlanZone).filter(ClPlanZone.code == code).one()
                plan_zone_id = plan_zone.plan_zone_id
        else:
            zone_type_count = self.session.query(ClPlanZone).filter(ClPlanZone.code == plan_code).count()
            if zone_type_count == 0:
                PluginUtils.show_error(self, self.tr("Error loading layer"), self.tr("The layer is invalid."))
                return
            if zone_type_count == 1:
                zone_type = self.session.query(ClPlanZone).filter(ClPlanZone.code == plan_code).one()
                plan_zone_id = zone_type.plan_zone_id
        if plan_zone_id:
            new_parcel.plan_zone_id = plan_zone_id
            new_parcel.badedturl = plan_code

            # new_parcel.landuse = landuse
            new_parcel.gazner = landname

        return new_parcel

    @pyqtSlot()
    def new_zoom_to_selected_clicked(self):

        selected_item = self.result_twidget.selectedItems()[0]

        file_path = self.parcel_shape_edit.text()

        if selected_item is None:
            return

        parcel_shape_layer = QgsVectorLayer(file_path, "tmp_parcel_shape", "ogr")

        feature_id = self.result_twidget.currentItem().data(0, Qt.UserRole + 2)

        parcel_shape_layer.select(feature_id)
        self.plugin.iface.mapCanvas().zoomToSelected(parcel_shape_layer)

    def __save_new_parcel(self):

        file_path = self.file_path
        parcel_shape_layer = QgsVectorLayer(file_path, "tmp_parcel_shape", "ogr")
        iterator = parcel_shape_layer.getFeatures()
        provider = parcel_shape_layer.dataProvider()

        for parcel in iterator:
            feature_id = parcel.id()
            validaty_result = self.__validaty_of_new_parcel(parcel, parcel_shape_layer, feature_id)
            if validaty_result[0]:
                new_parcel = self.__add_new_parcel(parcel, parcel_shape_layer)
                self.__add_new_parcel_attributes(parcel, new_parcel, provider)

    @pyqtSlot()
    def on_apply_button_clicked(self):

        self.create_savepoint()

        self.__save_new_parcel()

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

        print self.result_twidget.selectedItems()
        current_item = self.result_twidget.selectedItems()[0]
        object_type = current_item.data(0, Qt.UserRole + 1)
        object_id = current_item.data(0, Qt.UserRole)

        if object_type == REFUSED:
            self.message_label.setStyleSheet("QLabel {color: rgb(255,0,0);}")
            self.message_label.setText(self.error_dic[object_id])
        else:
            self.message_label.setStyleSheet("QLabel {color: rgb(0,71,31);}")
            self.message_label.setText(current_item.text(0))

    @pyqtSlot()
    def on_add_button_clicked(self):

        if not self.main_parcels:
            PluginUtils.show_message(self, u'Анхааруулга', u'Нэгж талбар сонгоогүй байна.')
            return

        for parcel_id in self.main_parcels:
            value = self.session.query(PlProjectParcel).filter(PlProjectParcel.parcel_id == parcel_id).one()

            plan = value.project_ref
            description = ''
            plan_type = "" if not plan.plan_type_ref else plan.plan_type_ref.short_name
            au_type = ''

            if plan.plan_type_ref.admin_unit_type == 2:
                if plan.au1_ref:
                    au_type = ' /' + unicode(plan.au1_ref.name) + '/'
            elif plan.plan_type_ref.admin_unit_type == 3:
                if plan.au2_ref:
                    au_type = ' /' + unicode(plan.au2_ref.name) + '/'
            else:
                au_type = ''
            description = str(plan.code) + au_type + " (" + unicode(plan_type) + ")"

            form_type_desc = "" if not value.right_form_ref else value.right_form_ref.description
            form_type_id = None if not value.right_form_ref else value.right_form_ref.right_form_id

            name = ''
            if value.gazner:
                name = '(' + value.gazner + ')'
            desc = ''
            if value.plan_zone_ref:
                if value.plan_zone_ref.name:

                    desc = value.plan_zone_ref.name
                    item = QTreeWidgetItem()

                    item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                    item.setData(0, Qt.UserRole, value.parcel_id)
                    item.setData(0, Qt.UserRole + 1, "polygon")
                    item.setData(0, Qt.UserRole + 2, value.plan_zone_id)
                    item.setData(0, Qt.UserRole + 3, value.plan_zone_ref.code)

                    item.setText(1, form_type_desc)
                    item.setData(1, Qt.UserRole, form_type_id)

                    item.setText(2, description)
                    item.setData(2, Qt.UserRole, plan.project_id)

                    item.setCheckState(0, Qt.Checked)

                    if value.polygon_geom is not None:
                        if self.__parcel_duplicate_check('polygon', value.polygon_geom):
                            new_parcel = self.__add_parcel_ref('polygon', value)
                            item.setText(0, '/' + str(new_parcel.parcel_id) + '/' + str(value.plan_zone_ref.code) + ': ' + name + desc)
                            item.setData(0, Qt.UserRole + 4, new_parcel.parcel_id)
                            self.item_polygon_current.addChild(item)
                    elif value.line_geom is not None:
                        if self.__parcel_duplicate_check('line', value.line_geom):
                            new_parcel = self.__add_parcel_ref('line', value)
                            item.setText(0, '/' + str(new_parcel.parcel_id) + '/' + str(
                                value.plan_zone_ref.code) + ': ' + name + desc)
                            item.setData(0, Qt.UserRole + 4, new_parcel.parcel_id)
                            self.item_line_current.addChild(item)
                    else:
                        if self.__parcel_duplicate_check('point', value.point_geom):
                            new_parcel = self.__add_parcel_ref('point', value)
                            item.setText(0, '/' + str(new_parcel.parcel_id) + '/' + str(
                                value.plan_zone_ref.code) + ': ' + name + desc)
                            item.setData(0, Qt.UserRole + 4, new_parcel.parcel_id)
                            self.item_point_current.addChild(item)

    def __add_parcel_ref(self, geom_type, value):

        # if not value.polygon_geom and not value.line_geom and not value.point_geom:
        #     return

        new_parcel = PlProjectParcel()

        new_parcel.project_id = self.plan.project_id
        new_parcel.project_ref = self.plan
        new_parcel.landuse = value.landuse
        new_parcel.gazner = value.gazner
        new_parcel.plan_zone_id = value.plan_zone_id
        new_parcel.badedturl = value.badedturl
        new_parcel.right_form_id = value.right_form_id
        new_parcel.right_form_ref = value.right_form_ref
        new_parcel.valid_from = PluginUtils.convert_qt_date_to_python(QDateTime().currentDateTime())
        new_parcel.au1 = self.au1
        new_parcel.au2 = self.au2

        if geom_type == 'polygon':
            new_parcel.polygon_geom = value.polygon_geom
        elif geom_type == 'line':
            new_parcel.line_geom = value.line_geom
        else:
            new_parcel.point_geom = value.point_geom

        self.session.add(new_parcel)
        self.session.flush()

        parcel_ref = PlProjectParcelRefParcel()
        parcel_ref.parcel_id = new_parcel.parcel_id
        parcel_ref.ref_parcel_id = value.parcel_id
        parcel_ref.cad_parcel_id = None
        parcel_ref.is_cadastre = False
        self.session.add(parcel_ref)

        return new_parcel

    def __parcel_duplicate_check(self, geom_type, geometry):

        is_true = True
        if geom_type == 'polygon':
            count = self.session.query(PlProjectParcel).\
                filter(PlProjectParcel.project_id == self.plan.project_id).\
                filter(PlProjectParcel.polygon_geom.ST_Equals(geometry)).count()
            if count > 0:
                is_true = False
        elif geom_type == 'line':
            count = self.session.query(PlProjectParcel). \
                filter(PlProjectParcel.project_id == self.plan.project_id). \
                filter(PlProjectParcel.line_geom.ST_Equals(geometry)).count()
            if count > 0:
                is_true = False
        else:
            count = self.session.query(PlProjectParcel). \
                filter(PlProjectParcel.project_id == self.plan.project_id). \
                filter(PlProjectParcel.point_geom.ST_Equals(geometry)).count()
            if count > 0:
                is_true = False
        return is_true

    @pyqtSlot()
    def on_remove_button_clicked(self):

        root = self.current_tree_widget.invisibleRootItem()
        item = self.current_tree_widget.currentItem()
        if item:
            parcel_id = item.data(0, Qt.UserRole + 4)

            ref_count = self.session.query(PlProjectParcelRefParcel). \
                filter(PlProjectParcelRefParcel.parcel_id == parcel_id).count()

            if ref_count > 0:
                self.session.query(PlProjectParcelRefParcel). \
                    filter(PlProjectParcelRefParcel.parcel_id == parcel_id).delete()

            count = self.session.query(PlProjectParcel). \
                filter(PlProjectParcel.parcel_id == parcel_id).count()
            if count == 1:
                self.session.query(PlProjectParcel). \
                    filter(PlProjectParcel.parcel_id == parcel_id).delete()
            (item.parent() or root).removeChild(item)

    @pyqtSlot(int)
    def on_change_form_check_box_stateChanged(self, state):

        if state == Qt.Checked:
            self.form_type_change_cbox.setEnabled(True)
            self.right_type_change_cbox.setEnabled(True)
            self.form_change_button.setEnabled(True)
        else:
            self.form_type_change_cbox.setEnabled(False)
            self.right_type_change_cbox.setEnabled(False)
            self.form_change_button.setEnabled(False)
            # self.form_type_change_cbox.clear()

    @pyqtSlot(int)
    def on_cadastre_change_form_check_box_stateChanged(self, state):

        if state == Qt.Checked:
            self.cadastre_form_type_change_cbox.setEnabled(True)
            self.cadastre_right_type_change_cbox.setEnabled(True)
            self.cadastre_form_change_button.setEnabled(True)
        else:
            self.cadastre_form_type_change_cbox.setEnabled(False)
            self.cadastre_right_type_change_cbox.setEnabled(False)
            self.cadastre_form_change_button.setEnabled(False)
            # self.cadastre_form_type_change_cbox.clear()

    @pyqtSlot(int)
    def on_if_single_type_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.shp_process_type_cbox.setEnabled(True)
            plan_type = self.plan.plan_type_ref
            values = self.session.query(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                join(SetPlanZonePlanType, ClPlanZone.plan_zone_id == SetPlanZonePlanType.plan_zone_id). \
                filter(SetPlanZonePlanType.plan_type_id == plan_type.plan_type_id). \
                group_by(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                order_by(ClPlanZone.code)

            for value in values:
                self.shp_process_type_cbox.addItem(str(value.code) + ':' + value.name, value.code)

            for index in range(self.shp_process_type_cbox.count()):
                self.shp_process_type_cbox.setItemData(index, self.shp_process_type_cbox.itemText(index), Qt.ToolTipRole)

        else:
            self.shp_process_type_cbox.clear()
            self.shp_process_type_cbox.setEnabled(False)

    @pyqtSlot(int)
    def on_default_plan_zone_chbox_stateChanged(self, state):

        self.shp_process_type_cbox.clear()
        if state == Qt.Checked:
            is_default = True
            plan_type = self.plan.plan_type_ref
            values = self.session.query(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                join(SetPlanZonePlanType, ClPlanZone.plan_zone_id == SetPlanZonePlanType.plan_zone_id). \
                filter(SetPlanZonePlanType.plan_type_id == plan_type.plan_type_id). \
                filter(SetPlanZonePlanType.is_default == is_default). \
                group_by(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                order_by(ClPlanZone.code)

            for value in values:
                self.shp_process_type_cbox.addItem(str(value.code) + ':' + value.name, value.code)

            for index in range(self.shp_process_type_cbox.count()):
                self.shp_process_type_cbox.setItemData(index, self.shp_process_type_cbox.itemText(index),
                                                       Qt.ToolTipRole)
        else:
            plan_type = self.plan.plan_type_ref
            values = self.session.query(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                join(SetPlanZonePlanType, ClPlanZone.plan_zone_id == SetPlanZonePlanType.plan_zone_id). \
                filter(SetPlanZonePlanType.plan_type_id == plan_type.plan_type_id). \
                group_by(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                order_by(ClPlanZone.code)

            for value in values:
                self.shp_process_type_cbox.addItem(str(value.code) + ':' + value.name, value.code)

            for index in range(self.shp_process_type_cbox.count()):
                self.shp_process_type_cbox.setItemData(index, self.shp_process_type_cbox.itemText(index),
                                                       Qt.ToolTipRole)

    @pyqtSlot(int)
    def on_shp_process_type_cbox_currentIndexChanged(self, index):

        self.shp_process_type_cbox.setToolTip(self.shp_process_type_cbox.currentText())

        # feature_id = self.result_twidget.currentItem().data(0, Qt.UserRole + 2)
        #
        # self.approved_item

        self.__import_template_data(self.file_path)


    def __shp_edit_attribute(self, parcel_shape_layer):

        code = self.shp_process_type_cbox.itemData(self.shp_process_type_cbox.currentIndex())
        layer = parcel_shape_layer

        # features = layer.getFeatures()

        provider = layer.dataProvider()
        features = provider.getFeatures()
        # p = features.next()
        # p.attributes()

        updateMap = {}

        layer.startEditing()
        for feature in features:
            fieldIdx = feature.fields().indexFromName('badedturl')
            updateMap[feature.id()] = {fieldIdx: code}

        provider.changeAttributeValues(updateMap)
        layer.commitChanges()
        self.plugin.iface.vectorLayerTools().stopEditing(layer)
        self.plugin.iface.mapCanvas().refresh()

    @pyqtSlot()
    def on_form_change_button_clicked(self):

        form_type_txt = self.form_type_change_cbox.currentText()
        form_type_code = self.form_type_change_cbox.itemData(self.form_type_change_cbox.currentIndex())
        root = self.current_tree_widget.invisibleRootItem()

        self.current_tree_widget.topLevelItemCount()
        child_count = root.childCount()
        for i in range(child_count):
            parent_item = root.child(i)
            for i in range(parent_item.childCount()):
                child_item = parent_item.child(i)
                if child_item.checkState(0) == QtCore.Qt.Checked:
                    parcel_id = child_item.data(0, Qt.UserRole + 4)

                    child_item.setText(1, form_type_txt)
                    child_item.setData(1, Qt.UserRole, form_type_code)

                    count = self.session.query(PlProjectParcel). \
                        filter(PlProjectParcel.parcel_id == parcel_id).count()
                    if count == 1:
                        parcel = self.session.query(PlProjectParcel). \
                            filter(PlProjectParcel.parcel_id == parcel_id).one()

                        form_type_code = self.form_type_change_cbox.itemData(self.form_type_change_cbox.currentIndex())
                        right_type_code = self.right_type_change_cbox.itemData(self.right_type_change_cbox.currentIndex())
                        if form_type_code:
                            parcel.right_form_id = form_type_code
                        if right_type_code:
                            parcel.right_type_code = right_type_code

    @pyqtSlot(int)
    def on_form_type_change_cbox_currentIndexChanged(self, index):

        self.right_type_change_cbox.clear()
        form_type = self.form_type_change_cbox.itemData(self.form_type_change_cbox.currentIndex())

        form_right_types = self.session.query(PlSetRightFormRightType).filter(PlSetRightFormRightType.right_form_id == form_type)

        if form_right_types.count() > 0:
            self.right_type_change_cbox.setEnabled(True)
        else:
            self.right_type_change_cbox.setEnabled(False)

        for value in form_right_types.all():
            right_type = self.session.query(ClRightType).filter(ClRightType.code == value.right_type_code).one()
            self.right_type_change_cbox.addItem(right_type.description, right_type.code)

    @pyqtSlot(int)
    def on_cadastre_form_type_change_cbox_currentIndexChanged(self, index):

        self.cadastre_right_type_change_cbox.clear()
        form_type = self.cadastre_form_type_change_cbox.itemData(self.cadastre_form_type_change_cbox.currentIndex())

        form_right_types = self.session.query(PlSetRightFormRightType).filter(
            PlSetRightFormRightType.right_form_id == form_type)

        if form_right_types.count() > 0:
            self.cadastre_right_type_change_cbox.setEnabled(True)
        else:
            self.cadastre_right_type_change_cbox.setEnabled(False)

        for value in form_right_types.all():
            right_type = self.session.query(ClRightType).filter(ClRightType.code == value.right_type_code).one()
            self.cadastre_right_type_change_cbox.addItem(right_type.description, right_type.code)

    @pyqtSlot()
    def on_cadastre_find_button_clicked(self):

        self.__cadastre_find()
        self.__plan_cadastre_find()

    def __plan_cadastre_find(self):

        parcels = self.session.query(ParcelSearch, PlProjectParcelRefParcel, PlProjectParcel). \
            join(PlProjectParcelRefParcel, ParcelSearch.parcel_id == PlProjectParcelRefParcel.cad_parcel_id). \
            join(PlProjectParcel, PlProjectParcel.parcel_id == PlProjectParcelRefParcel.parcel_id). \
            filter(PlProjectParcel.project_id == self.plan.project_id). \
            filter(PlProjectParcelRefParcel.is_cadastre == True)

        count = 0
        self.cadastre_current_twidget.setRowCount(0)
        for parcel, parcel_ref, project_parcel in parcels.distinct(ParcelSearch.parcel_id).all():
            plan_zone = project_parcel.plan_zone_ref
            form_type = project_parcel.right_form_ref
            right_type = project_parcel.right_type_ref
            # geo_id = self.tr("n.a.") if not parcel.geo_id else parcel.geo_id
            self.cadastre_current_twidget.insertRow(count)
            address_khashaa = ''
            address_streetname = ''
            if parcel.address_khashaa:
                address_khashaa = parcel.address_khashaa
            if parcel.address_streetname:
                address_streetname = parcel.address_streetname
            item = QTableWidgetItem(parcel.parcel_id + " (" + address_khashaa + ", " + address_streetname + ")")
            item.setCheckState(Qt.Unchecked)
            item.setIcon(QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
            item.setData(Qt.UserRole, parcel.parcel_id)
            item.setData(Qt.UserRole + 1, parcel_ref.parcel_id)
            self.cadastre_current_twidget.setItem(count, 0, item)
            if plan_zone:
                item = QTableWidgetItem(plan_zone.code + ':' + plan_zone.name)
                item.setData(Qt.UserRole, plan_zone.plan_zone_id)
                self.cadastre_current_twidget.setItem(count, 1, item)
            if form_type:
                item = QTableWidgetItem(form_type.code + ':' + form_type.description)
                item.setData(Qt.UserRole, form_type.right_form_id)
                self.cadastre_current_twidget.setItem(count, 2, item)
            if right_type:
                item = QTableWidgetItem(right_type.description)
                item.setData(Qt.UserRole, right_type.code)
                self.cadastre_current_twidget.setItem(count, 3, item)
            count += 1
        self.error_label.setText("")

    def __cadastre_find(self):

        parcels = self.session.query(ParcelSearch.parcel_id, ParcelSearch.geo_id, ParcelSearch.landuse_ref, \
                                     ParcelSearch.address_khashaa, ParcelSearch.address_streetname)

        filter_is_set = False

        if self.parcel_num_edit.text():
            if len(self.parcel_num_edit.text()) < 5:
                self.error_label.setText(self.tr("parcel find search character should be at least 4"))
                return
            filter_is_set = True
            parcel_no = "%" + self.parcel_num_edit.text() + "%"
            parcels = parcels.filter(ParcelSearch.parcel_id.ilike(parcel_no))

        if not self.cadastre_right_type_cbox.itemData(self.cadastre_right_type_cbox.currentIndex()) == -1:
            filter_is_set = True
            value = self.cadastre_right_type_cbox.itemData(self.cadastre_right_type_cbox.currentIndex())
            parcels = parcels.filter(ParcelSearch.right_type_code == value)

        if not self.land_use_type_cbox.itemData(self.land_use_type_cbox.currentIndex()) == -1:
            filter_is_set = True
            value = self.land_use_type_cbox.itemData(self.land_use_type_cbox.currentIndex())
            parcels = parcels.filter(ParcelSearch.landuse == value)

        if self.parcel_right_holder_name_edit.text():
            if len(self.personal_parcel_edit.text()) < 2:
                self.error_label.setText(self.tr("find search character should be at least 2"))
                return
            filter_is_set = True
            right_holder = "%" + self.parcel_right_holder_name_edit.text() + "%"
            parcels = parcels.filter(or_(func.lower(ParcelSearch.name).ilike(func.lower(right_holder)),
                                         func.lower(ParcelSearch.first_name).ilike(func.lower(right_holder)),
                                         func.lower(ParcelSearch.middle_name).ilike(func.lower(right_holder))))

        if self.personal_parcel_edit.text():
            if len(self.personal_parcel_edit.text()) < 5:
                self.error_label.setText(self.tr("find search character should be at least 4"))
                return
            filter_is_set = True
            value = "%" + self.personal_parcel_edit.text() + "%"
            parcels = parcels.filter(ParcelSearch.person_register.ilike(value))

        if self.parcel_streetname_edit.text():
            filter_is_set = True
            value = "%" + self.parcel_streetname_edit.text() + "%"
            parcels = parcels.filter(ParcelSearch.address_streetname.ilike(value))

        if self.parcel_khashaa_edit.text():
            filter_is_set = True
            value = "%" + self.parcel_khashaa_edit.text() + "%"
            parcels = parcels.filter(ParcelSearch.address_khashaa.ilike(value))

        count = 0

        self.cadastre_twidget.setRowCount(0)

        if parcels.distinct(ParcelSearch.parcel_id).count() == 0:
            self.error_label.setText(self.tr("No parcels found for this search filter."))
            return

        elif filter_is_set is False:
            self.error_label.setText(self.tr("Please specify a search filter."))
            return

        for parcel in parcels.distinct(ParcelSearch.parcel_id).all():
            # geo_id = self.tr("n.a.") if not parcel.geo_id else parcel.geo_id
            address_khashaa = ''
            address_streetname = ''
            if parcel.address_khashaa:
                address_khashaa = parcel.address_khashaa
            if parcel.address_streetname:
                address_streetname = parcel.address_streetname
            item = QTableWidgetItem(parcel.parcel_id + " (" + address_khashaa + ", " + address_streetname + ")")
            item.setIcon(QIcon(QPixmap(":/plugins/lm2/parcel.png")))
            item.setData(Qt.UserRole, parcel.parcel_id)
            self.cadastre_twidget.insertRow(count)
            self.cadastre_twidget.setItem(count, 0, item)
            count += 1

        self.error_label.setText("")
        # self.parcel_results_label.setText(self.tr("Results: ") + str(count))

    @pyqtSlot()
    def on_cad_add_button_clicked(self):

        if not len(self.cadastre_twidget.selectedItems()):
            return

        # if self.__set_cad_parcel_values()[1]:
        # plan_zone = self.__set_cad_parcel_values()[0]

        values = self.session.query(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
            join(PlProjectPlanZone, ClPlanZone.plan_zone_id == PlProjectPlanZone.plan_zone_id). \
            filter(PlProjectPlanZone.project_id == self.plan.project_id). \
            group_by(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
            order_by(ClPlanZone.code)

        plan_zones = []
        for value in values:
            desc = str(value.code) + ':-' + value.name
            plan_zones.append(desc)

        item, ok = QInputDialog.getItem(self, "select input dialog",
                                        "list of languages", plan_zones, 0, False)

        zone_code, zone_desc = item.split(':-')

        plan_zone = self.session.query(ClPlanZone).filter(ClPlanZone.code == zone_code).one()

        if ok:
            items = self.cadastre_twidget.selectedItems()

            for item in items:
                parcel_id = item.data(Qt.UserRole)
                parcel_text = item.text()

                parcel = self.session.query(CaParcelTbl).filter(CaParcelTbl.parcel_id == parcel_id).one()
                if self.__cad_parcel_duplicate_check(parcel):
                    new_parcel = self.__add_cad_parcel_ref(parcel, plan_zone)

                    row_count = self.cadastre_current_twidget.rowCount()
                    self.cadastre_current_twidget.insertRow(row_count)

                    item = QTableWidgetItem(parcel_text)
                    item.setCheckState(Qt.Checked)
                    item.setIcon(QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                    item.setData(Qt.UserRole, parcel_id)
                    item.setData(Qt.UserRole + 1, new_parcel.parcel_id)
                    self.cadastre_current_twidget.setItem(row_count, 0, item)

                    item = QTableWidgetItem(plan_zone.code + ':' + plan_zone.name)
                    item.setData(Qt.UserRole, plan_zone.plan_zone_id)
                    self.cadastre_current_twidget.setItem(row_count, 1, item)

    @pyqtSlot()
    def on_cad_remove_button_clicked(self):

        if not len(self.cadastre_current_twidget.selectedItems()):
            return

        items = self.cadastre_current_twidget.selectedItems()
        for item in items:
            if item.checkState() == Qt.Checked:
                parcel_id = item.data(Qt.UserRole+1)
                self.session.query(PlProjectParcelRefParcel).filter(PlProjectParcelRefParcel.parcel_id == parcel_id).delete()
                self.session.query(PlProjectParcel).filter(PlProjectParcel.parcel_id == parcel_id).delete()

        self.__plan_cadastre_find()

    def __add_cad_parcel_ref(self, parcel, plan_zone):

        new_parcel = PlProjectParcel()

        new_parcel.project_id = self.plan.project_id
        new_parcel.project_ref = self.plan
        new_parcel.plan_zone_id = plan_zone.plan_zone_id
        new_parcel.badedturl = plan_zone.code
        new_parcel.plan_zone_ref = plan_zone
        new_parcel.landuse = parcel.landuse
        new_parcel.gazner = parcel.address_neighbourhood
        new_parcel.valid_from = PluginUtils.convert_qt_date_to_python(QDateTime().currentDateTime())
        new_parcel.au1 = self.au1
        new_parcel.au2 = self.au2
        new_parcel.polygon_geom = parcel.geometry

        self.session.add(new_parcel)
        self.session.flush()

        parcel_ref = PlProjectParcelRefParcel()
        parcel_ref.parcel_id = new_parcel.parcel_id
        parcel_ref.ref_parcel_id = None
        parcel_ref.cad_parcel_id = parcel.parcel_id
        parcel_ref.is_cadastre = True
        self.session.add(parcel_ref)

        return new_parcel

    def __cad_parcel_duplicate_check(self, parcel):

        is_true = True
        count = self.session.query(PlProjectParcelRefParcel). \
            join(PlProjectParcel, PlProjectParcelRefParcel.parcel_id == PlProjectParcel.parcel_id). \
            filter(PlProjectParcel.project_id == self.plan.project_id). \
            filter(PlProjectParcelRefParcel.cad_parcel_id == parcel.parcel_id).count()

        if count > 0:
            is_true = False
            self.error_label.setText(u"{0} нэгж талбар бүртгэгдсэн байна.".format(parcel.parcel_id))

        return is_true

    def __set_cad_parcel_values(self):

        values = self.session.query(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
            join(PlProjectPlanZone, ClPlanZone.plan_zone_id == PlProjectPlanZone.plan_zone_id). \
            filter(PlProjectPlanZone.project_id == self.plan.project_id). \
            group_by(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
            order_by(ClPlanZone.code)

        plan_zones = []
        for value in values:
            desc = str(value.code) + ':-' + value.name
            plan_zones.append(desc)

        item, ok = QInputDialog.getItem(self, "select input dialog",
                                        "list of languages", plan_zones, 0, False)

        zone_code, zone_desc = item.split(':-')

        plan_zone = self.session.query(ClPlanZone).filter(ClPlanZone.code == zone_code).one()

        return plan_zone, ok

    @pyqtSlot()
    def on_cadastre_form_change_button_clicked(self):

        plan_zone_id = self.cad_process_type_cbox.itemData(self.cad_process_type_cbox.currentIndex())
        form_type_code = self.cadastre_form_type_change_cbox.itemData(self.cadastre_form_type_change_cbox.currentIndex())
        form_type_text = self.cadastre_form_type_change_cbox.currentText()
        right_type_code = self.cadastre_right_type_change_cbox.itemData(self.cadastre_right_type_change_cbox.currentIndex())
        right_type_text = self.cadastre_right_type_change_cbox.currentText()

        row_count = self.cadastre_current_twidget.rowCount()

        for row in range(row_count):
            item = self.cadastre_current_twidget.item(row, 0)
            parcel_id = item.data(Qt.UserRole + 1)
            if item.checkState() == Qt.Checked:
                item = self.cadastre_current_twidget.item(row, 2)
                if item:
                    item.setText(form_type_text)
                    item.setData(Qt.UserRole, form_type_code)
                else:
                    item = QTableWidgetItem(form_type_text)
                    item.setData(Qt.UserRole, form_type_code)
                    self.cadastre_current_twidget.setItem(row, 2, item)
                item = self.cadastre_current_twidget.item(row, 3)
                if item:
                    item.setText(right_type_text)
                    item.setData(Qt.UserRole, right_type_code)
                else:
                    item = QTableWidgetItem(right_type_text)
                    item.setData(Qt.UserRole, right_type_code)
                    self.cadastre_current_twidget.setItem(row, 3, item)

                count = self.session.query(PlProjectParcel). \
                    filter(PlProjectParcel.parcel_id == parcel_id).count()
                if count == 1:
                    parcel = self.session.query(PlProjectParcel). \
                        filter(PlProjectParcel.parcel_id == parcel_id).one()

                    if form_type_code:
                        parcel.right_form_id = form_type_code
                    if right_type_code:
                        parcel.right_type_code = right_type_code
