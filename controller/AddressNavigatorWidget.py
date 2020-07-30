# coding=utf8

__author__ = 'B.Ankhbold'

from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtXml import *
from PyQt4.QtCore import QDate
from geoalchemy2.elements import WKTElement
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import func, or_, and_, desc
from sqlalchemy.sql.expression import cast
from sqlalchemy import func, or_, extract
from ..view.Ui_AddressNavigatorWidget import Ui_AddressNavigatorWidget
from ..utils.LayerUtils import LayerUtils
from ..model.AuCadastreBlock import *
from ..model.AuLevel1 import *
from ..model.AuLevel2 import *
from ..model.PlProject import *
from ..model.ClPlanDecisionLevel import *
from ..model.ClPlanType import *
from ..model.CaParcel import *
from ..controller.PlanCaseDialog import *
from ..controller.ManageParcelRecordsDialog import *
from ..utils.DatabaseUtils import *
from ..utils.PluginUtils import *
from ..utils.LayerUtils import *
from ..model.DatabaseHelper import *
from ..model.StStreetPoint import *
from ..model.StMapStreetPoint import *
from ..model.StStreetLineView import *
from ..model.CaBuildingAddress import *
from ..model.CaParcelAddress import *
from ..controller.PlanDetailWidget import *
from ..controller.PlanLayerFilterDialog import *
# from ..LM2Plugin import *
from datetime import timedelta
from xlsxwriter.utility import xl_rowcol_to_cell, xl_col_to_name
import xlsxwriter
import time
import urllib
import urllib2
import json

LANDUSE_1 = u'Хөдөө аж ахуйн газар'
LANDUSE_2 = u'Хот, тосгон, бусад суурины газар'
LANDUSE_3 = u'Зам, шугам сүлжээний газар'
LANDUSE_4 = u'Ойн сан бүхий газар'
LANDUSE_5 = u'Усны сан бүхий газар'
LANDUSE_6 = u'Улсын тусгай хэрэгцээний газар'

SURFACE_ELEVATION = 'surface_elevation'
SURFACE_SLOPE = 'surface_slope'

class AddressNavigatorWidget(QDockWidget, Ui_AddressNavigatorWidget, DatabaseHelper):

    def __init__(self,  plugin, parent=None):

        super(AddressNavigatorWidget,  self).__init__(parent)
        DatabaseHelper.__init__(self)

        self.setupUi(self)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.plugin = plugin
        self.session = SessionHandler().session_instance()
        self.au2 = DatabaseUtils.working_l2_code()
        self.au1 = DatabaseUtils.working_l1_code()
        self.current_dialog = None
        self.__boundaryPointsLayer = None
        self.__setup_table_widget()

    def __setup_table_widget(self):

        # self.str_nodes_twidget.setColumnCount(1)
        # self.str_nodes_twidget.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.str_nodes_twidget.setAlternatingRowColors(True)
        self.str_nodes_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.str_nodes_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.str_nodes_twidget.setSelectionMode(QTableWidget.SingleSelection)

        # self.str_nodes_twidget.resizeColumnToContents(4)
        self.str_nodes_twidget.setColumnWidth(0, 30)
        self.str_nodes_twidget.setColumnWidth(1, 130)
        self.str_nodes_twidget.setColumnWidth(2, 130)

    @pyqtSlot()
    def on_selected_str_load_button_clicked(self):

        self.str_nodes_twidget.setRowCount(0)
        parcelLayer = LayerUtils.layer_by_data_source("data_address", "st_street_line_view")
        select_feature = parcelLayer.selectedFeatures()

        str_id = None
        for feature in select_feature:
            attr = feature.attributes()
            str_id = attr[0]

        if str_id is None:
            return
        sql = "select * from base.st_street_line_view_start_end_nodes("+ str(str_id) +");"

        result = self.session.execute(sql)
        for item_row in result:
            id = item_row[0]
            street_id = item_row[1]
            x = item_row[2]
            y = item_row[3]

            geom_spot4 = QgsPoint(x, y)
            geometry = QgsGeometry.fromPoint(geom_spot4)

            geometry = WKTElement(geometry.exportToWkt(), srid=4326)

            object_count = 0
            map_point_count = self.session.query(StMapStreetPoint).filter(StMapStreetPoint.street_id == street_id).count()
            if map_point_count != 0:
                map_object = self.session.query(StMapStreetPoint).filter(StMapStreetPoint.street_id == street_id).first()
                object_count = self.session.query(StStreetPoint).\
                    filter(StStreetPoint.id == map_object.street_point_id).\
                    filter(StStreetPoint.geometry.ST_Equals(geometry)).count()
            count = self.str_nodes_twidget.rowCount()
            self.str_nodes_twidget.insertRow(count)

            item = QTableWidgetItem(str(id))
            item.setData(Qt.UserRole, id)
            item.setData(Qt.UserRole + 1, street_id)
            if object_count == 1:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.str_nodes_twidget.setItem(count, 0, item)

            item = QTableWidgetItem(str(x))
            item.setData(Qt.UserRole, x)
            self.str_nodes_twidget.setItem(count, 1, item)

            item = QTableWidgetItem(str(y))
            item.setData(Qt.UserRole, y)
            self.str_nodes_twidget.setItem(count, 2, item)

    @pyqtSlot(QTableWidgetItem)
    def on_str_nodes_twidget_itemClicked(self, item):

        selected_row = self.str_nodes_twidget.currentRow()
        id = self.str_nodes_twidget.item(selected_row, 0).data(Qt.UserRole)
        x = self.str_nodes_twidget.item(selected_row, 1).data(Qt.UserRole)
        y = self.str_nodes_twidget.item(selected_row, 2).data(Qt.UserRole)

        row = self.str_nodes_twidget.currentRow()
        id_item = self.str_nodes_twidget.item(row, 0)
        for row in range(self.str_nodes_twidget.rowCount()):
            item_dec = self.str_nodes_twidget.item(row, 0)
            item_dec.setCheckState(Qt.Unchecked)
        if id_item:
            id_item.setCheckState(Qt.Checked)

    @pyqtSlot(QTableWidgetItem)
    def on_str_nodes_twidget_itemDoubleClicked(self, item):

        layers = self.plugin.iface.legendInterface().layers()
        for layer in layers:
            if layer.name() == "boundary_points":
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

        selected_row = self.str_nodes_twidget.currentRow()
        id = self.str_nodes_twidget.item(selected_row, 0).data(Qt.UserRole)
        x = self.str_nodes_twidget.item(selected_row, 1).data(Qt.UserRole)
        y = self.str_nodes_twidget.item(selected_row, 2).data(Qt.UserRole)

        self.__add_layers()
        self.__draw_features(x, y, id)

        zoom_layer = None
        layers = self.plugin.iface.legendInterface().layers()
        for layer in layers:
            if layer.name() == "boundary_points":
                zoom_layer = layer

        self.__select_feature(str(id), zoom_layer)

    def __select_feature(self, id, layer):

        expression = " id = \'" + id + "\'"
        request = QgsFeatureRequest()
        request.setFilterExpression(expression)
        feature_ids = []
        if layer:
            iterator = layer.getFeatures(request)

            for feature in iterator:
                feature_ids.append(feature.id())
            # if len(feature_ids) == 0:
            #     self.status_label.setText(self.tr("No geometry assigned"))

            layer.setSelectedFeatures(feature_ids)
            self.plugin.iface.mapCanvas().zoomToSelected(layer)

    def __draw_features(self, x, y, point_id):

        self.__draw_boundary_points(x, y, point_id)

        self.plugin.iface.mapCanvas().refresh()

    def __add_layers(self):
        # those layers must be in WGS84 because it could be that the user didn't enable the on the fly transformaton
        self.__add_boundary_points_layer()

    def __add_boundary_points_layer(self):

        soum = DatabaseUtils.working_l2_code()
        layer = LayerUtils.layer_by_data_source("data_address", 'st_street_line_view')
        crs = layer.crs()

        boundary_points_layer = QgsVectorLayer("Point?crs=" + str(crs.authid()), "boundary_points", "memory")
        # add fields
        boundary_points_layer.startEditing()
        boundary_points_layer.addAttribute(QgsField("id", QVariant.Int))
        boundary_points_layer.commitChanges()
        boundary_points_layer.setReadOnly(True)

        renderer_v2 = boundary_points_layer.rendererV2()
        symbol = renderer_v2.symbol()
        symbol.setColor(QColor(Qt.red))
        symbol.setSize(3)

        boundary_points_layer.enableLabels(True)
        label = boundary_points_layer.label()
        label.setLabelField(QgsLabel.Text, 0)
        label_attributes = label.labelAttributes()
        label_attributes.setOffset(10, 10, 1)
        label_attributes.setSize(8, 1)

        self.__add_map_layer(boundary_points_layer)
        self.__boundaryPointsLayer = boundary_points_layer

    def __add_map_layer(self, map_layer):

        QgsMapLayerRegistry.instance().addMapLayer(map_layer,  False)

        root = QgsProject.instance().layerTreeRoot()
        mygroup = root.findGroup(u"Хаяг")
        mygroup.insertLayer(0, map_layer)

    def __draw_boundary_points(self, x, y, point_id):

        boundary_points_layer = self.__boundaryPointsLayer
        boundary_points_layer.startEditing()
        # add a feature
        feature = QgsFeature()
        # feature.setGeometry(geometry)
        feature.setGeometry(QgsGeometry.fromPoint(QgsPoint(x, y)))
        feature.initAttributes(1)
        feature.setAttribute(0, str(point_id))
        boundary_points_layer.dataProvider().addFeatures([feature])

        boundary_points_layer.commitChanges()

        self.plugin.iface.mapCanvas().refresh()

    def __is_active_boundary_points(self):

        layers = self.plugin.iface.legendInterface().layers()
        is_layer_active = False
        for layer in layers:
            if layer.name() == "boundary_points":
                is_layer_active = True
        return is_layer_active

    def __delete_features(self, vector_layer):

        if vector_layer is None:
            return

        vector_layer.startEditing()

        ids = list()
        vector_layer.selectAll()

        for feature in vector_layer.getFeatures():
            ids.append(feature.id())

        vector_layer.dataProvider().deleteFeatures(ids)
        vector_layer.commitChanges()

        self.plugin.iface.mapCanvas().refresh()

    @pyqtSlot()
    def on_apply_button_clicked(self):

        for row in range(self.str_nodes_twidget.rowCount()):
            item_main = self.str_nodes_twidget.item(row, 0)
            if item_main.checkState() == Qt.Checked:
                id = self.str_nodes_twidget.item(row, 0).data(Qt.UserRole)
                street_id = self.str_nodes_twidget.item(row, 0).data(Qt.UserRole + 1)
                x = self.str_nodes_twidget.item(row, 1).data(Qt.UserRole)
                y = self.str_nodes_twidget.item(row, 2).data(Qt.UserRole)

                geom_spot4 = QgsPoint(x, y)
                geometry = QgsGeometry.fromPoint(geom_spot4)

                geometry = WKTElement(geometry.exportToWkt(), srid=4326)

                self.session.query(StMapStreetPoint).filter(StMapStreetPoint.street_id == street_id).delete()

                count = self.session.query(StStreetPoint).\
                    filter(StStreetPoint.geometry.ST_Equals(geometry)).count()

                if count == 0:
                    object = StStreetPoint()
                    object.is_active = True
                    object.geometry = geometry
                    object.valid_from = DatabaseUtils.current_date_time()
                    object.created_at = DatabaseUtils.current_date_time()
                    object.updated_at = DatabaseUtils.current_date_time()
                    object.au1 = self.au1
                    object.au2 = self.au2
                    self.session.add(object)
                    self.session.flush()

                    map_object = StMapStreetPoint()
                    map_object.street_point_id = object.id
                    map_object.street_id = street_id
                    self.session.add(map_object)
                if count == 1:
                    object = self.session.query(StStreetPoint). \
                        filter(StStreetPoint.geometry.ST_Equals(geometry)).one()
                    map_object = StMapStreetPoint()
                    map_object.street_point_id = object.id
                    map_object.street_id = street_id
                    self.session.add(map_object)

            self.session.commit()

    @pyqtSlot()
    def on_selected_str_load_button_clicked(self):

        self.str_nodes_twidget.setRowCount(0)
        parcelLayer = LayerUtils.layer_by_data_source("data_address", "ca_parcel_address")
        select_feature = parcelLayer.selectedFeatures()

        id = None
        for feature in select_feature:
            attr = feature.attributes()
            id = attr[0]

        if id is None:
            return