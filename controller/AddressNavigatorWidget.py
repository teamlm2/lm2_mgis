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
from ..model.StRoad import *
from ..model.StStreet import *
from ..model.StStreetAu2 import *
from ..model.StStreetPoint import *
from ..model.StMapStreetPoint import *
from ..model.StStreetLineView import *
from ..model.CaBuildingAddress import *
from ..model.CaParcelAddress import *
from ..model.ClAddressStatus import *
from ..model.AuZipCodeArea import *
from ..model.StEntrance import *
from ..controller.PlanDetailWidget import *
from ..controller.PlanLayerFilterDialog import *
from ..model.ClParcelType import *
from ..model.StSettlementPoint import *
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
        self.side = None
        self.str_id = None
        self.parcel_address_no = None
        self.building_address_no = None
        self.__boundaryPointsLayer = None
        self.__setup_table_widget()
        self.__combobox_setup()
        self.__setup_combo_boxes()
        self.working_l1_cbox.currentIndexChanged.connect(self.__working_l1_changed)
        self.working_l2_cbox.currentIndexChanged.connect(self.__working_l2_changed)
        self.working_l3_cbox.currentIndexChanged.connect(self.__working_l3_changed)

    def __working_l1_changed(self, index):

        l1_code = self.working_l1_cbox.itemData(index)
        try:
            role = DatabaseUtils.current_user()
            if l1_code == -1 or not l1_code:
                return
            self.create_savepoint()
            role.working_au_level1 = l1_code
            self.commit()
            PluginUtils.populate_au_level2_cbox(self.working_l2_cbox, l1_code, False, True, False)
        except SQLAlchemyError, e:
            self.rollback_to_savepoint()
            PluginUtils.show_message(self,  self.tr("Sql Error"), e.message)
            return

    def __working_l2_changed(self, index):

        l2_code = self.working_l2_cbox.itemData(index)

        self.create_savepoint()

        try:
            role = DatabaseUtils.current_user()
            if role:
                if not l2_code:
                    role.working_au_level2 = None
                else:
                    role.working_au_level2 = l2_code

                DatabaseUtils.set_working_schema(l2_code)
                self.commit()
                PluginUtils.populate_au_level3_cbox(self.working_l3_cbox, l2_code, False)

        except SQLAlchemyError, e:
            self.rollback_to_savepoint()
            PluginUtils.show_message(self,  self.tr("Sql Error"), e.message)
            return
        self.__zoom_to_soum(l2_code)

    def __working_l3_changed(self, index):

        l3_code = self.working_l3_cbox.itemData(index)

        self.create_savepoint()

        try:
            role = DatabaseUtils.current_user()
            if role:
                if not l3_code:
                    role.working_au_level3 = None
                else:
                    role.working_au_level3 = l3_code

                # DatabaseUtils.set_working_schema(l3_code)
                self.commit()

        except SQLAlchemyError, e:
            self.rollback_to_savepoint()
            PluginUtils.show_message(self,  self.tr("Sql Error"), e.message)
            return
        self.__zoom_to_bag(l3_code)

    def __zoom_to_soum(self, soum_code):

        layer = LayerUtils.layer_by_data_source("admin_units", "au_level2")
        if layer is None:
            layer = LayerUtils.load_layer_by_name_admin_units("au_level2", "code", "admin_units")
        if soum_code:
            expression = " code = \'" + soum_code + "\'"
            request = QgsFeatureRequest()
            request.setFilterExpression(expression)
            feature_ids = []
            iterator = layer.getFeatures(request)

            for feature in iterator:
                feature_ids.append(feature.id())
            if len(feature_ids) == 0:
                self.error_label.setText(self.tr("No soum assigned"))

            layer.setSelectedFeatures(feature_ids)
            self.plugin.iface.mapCanvas().zoomToSelected(layer)

    def __zoom_to_bag(self, bag_code):

        layer = LayerUtils.layer_by_data_source("admin_units", "au_level3")
        if layer is None:
            layer = LayerUtils.load_layer_by_name_admin_units("au_level3", "code", "admin_units")
        if bag_code:
            expression = " code = \'" + bag_code + "\'"
            request = QgsFeatureRequest()
            request.setFilterExpression(expression)
            feature_ids = []
            iterator = layer.getFeatures(request)

            for feature in iterator:
                feature_ids.append(feature.id())
            if len(feature_ids) == 0:
                self.error_label.setText(self.tr("No soum assigned"))

            layer.setSelectedFeatures(feature_ids)
            self.plugin.iface.mapCanvas().zoomToSelected(layer)

    def __setup_combo_boxes(self):

        try:
            PluginUtils.populate_au_level1_cbox(self.working_l1_cbox, False)

            l1_code = self.working_l1_cbox.itemData(self.working_l1_cbox.currentIndex(), Qt.UserRole)
            PluginUtils.populate_au_level2_cbox(self.working_l2_cbox, l1_code, False)

            self.working_l1_cbox.setCurrentIndex(self.working_l1_cbox.findData(DatabaseUtils.working_l1_code()))

            if self.working_l2_cbox.currentIndex():
                l2_code = self.working_l2_cbox.itemData(self.working_l2_cbox.currentIndex(), Qt.UserRole)
                PluginUtils.populate_au_level3_cbox(self.working_l3_cbox, l2_code, False)
            self.working_l2_cbox.setCurrentIndex(self.working_l2_cbox.findData(DatabaseUtils.working_l2_code()))
            self.working_l3_cbox.setCurrentIndex(self.working_l3_cbox.findData(DatabaseUtils.working_l3_code()))

        except SQLAlchemyError, e:
            PluginUtils.show_message(self, self.tr("Sql Error"), e.message)
            return

    def __combobox_setup(self):

        #parcel
        layer_types = self.session.query(ClParcelType).filter(ClParcelType.layer_type == 1).\
            order_by(ClParcelType.code.asc()).all()

        self.layer_type_cbox.clear()
        self.layer_type_cbox.addItem('*', -1)

        for value in layer_types:
            self.layer_type_cbox.addItem(value.description, value.code)

        #building
        layer_types = self.session.query(ClParcelType).filter(ClParcelType.layer_type == 2). \
            order_by(ClParcelType.code.asc()).all()

        self.building_layer_type_cbox.clear()
        self.building_layer_type_cbox.addItem('*', -1)

        for value in layer_types:
            self.building_layer_type_cbox.addItem(value.description, value.code)

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

        self.address_parcel_twidget.setAlternatingRowColors(True)
        self.address_parcel_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.address_parcel_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.address_parcel_twidget.setSelectionMode(QTableWidget.SingleSelection)

        self.str_road_twidget.setAlternatingRowColors(True)
        self.str_road_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.str_road_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.str_road_twidget.setSelectionMode(QTableWidget.SingleSelection)

        self.address_building_twidget.setAlternatingRowColors(True)
        self.address_building_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.address_building_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.address_building_twidget.setSelectionMode(QTableWidget.SingleSelection)

    @pyqtSlot()
    def on_selected_str_load_button_clicked(self):

        self.str_nodes_twidget.setRowCount(0)
        parcelLayer = LayerUtils.layer_by_data_source("data_address", "st_street_line_view")
        select_feature = parcelLayer.selectedFeatures()

        str_id = None
        for feature in select_feature:
            attr = feature.attributes()
            str_id = attr[1]
            self.str_id = str_id

        if str_id is None:
            return

        street = self.session.query(StStreet).filter(StStreet.id == str_id).one()

        self.str_id_lbl.setText(str(str_id))
        self.str_code_lbl.setText(str(street.code))
        self.str_name_lbl.setText(street.name)

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

            object_count = self.session.query(StStreetPoint).\
                filter(StStreetPoint.street_id == street_id). \
                filter(StStreetPoint.geometry.ST_Equals(geometry)). \
                filter(StStreetPoint.point_type == 1).count()
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

            if object_count == 1:
                item = QTableWidgetItem(u'Эхлэл')
                item.setData(Qt.UserRole, 1)
                self.str_nodes_twidget.setItem(count, 3, item)
            else:
                item = QTableWidgetItem(u'Төгсгөл')
                item.setData(Qt.UserRole, 2)
                self.str_nodes_twidget.setItem(count, 3, item)

    # @pyqtSlot(int)
    # def on_is_selected_parcels_chbox_stateChanged(self, state):
    #
    #     if state == Qt.Checked:
    #         self.is_selected_bag_chbox.setCheckable(False)
    #
    # @pyqtSlot(int)
    # def on_is_selected_bag_chbox_stateChanged(self, state):
    #
    #     if state == Qt.Checked:
    #         self.is_selected_parcels_chbox.setCheckable(False)

    @pyqtSlot()
    def on_get_street_parcels_button_clicked(self):

        str_calc_count = 10
        str_select_count = 1
        self.parcel_progressBar.setValue(0)

        if self.is_selected_parcels_chbox.isChecked():
            layer_name = "ca_parcel_address_view"
            schema_name = "data_address"
            parcelLayer = LayerUtils.layer_by_data_source(schema_name, layer_name)
            select_feature = parcelLayer.selectedFeatures()
            id = None
            self.parcel_progressBar.setMaximum(len(select_feature))
            for feature in select_feature:
                attr = feature.attributes()

                if len(attr) > 0:
                    id = attr[0]

                    sql = "select base.st_auto_street_select("+ str(str_calc_count) +", "+ str(str_select_count) +", "+ str(id) +"::bigint)"
                    result = self.session.execute(sql)
                    street_id = None
                    for row in result:
                        street_id = row[0]
                    if street_id is not None and id is not None:
                        parcel = self.session.query(CaParcelAddress).filter(CaParcelAddress.id == id).one()
                        sql_side = "select base.st_street_line_parcel_side2(" + str(street_id) + ", " + str(id) + "::bigint)"
                        result_side = self.session.execute(sql_side)
                        str_side = None
                        for row in result_side:
                            str_side = row[0]
                        parcel.street_id = street_id
                        if str_side:
                            parcel.street_side = str_side
                value_p = self.parcel_progressBar.value() + 1
                self.parcel_progressBar.setValue(value_p)
        if self.is_selected_bag_chbox.isChecked():
            l3_code = self.working_l3_cbox.itemData(self.working_l3_cbox.currentIndex())
            parcels = self.session.query(CaParcelAddress).filter(CaParcelAddress.au3 == l3_code).all()
            id = None
            self.parcel_progressBar.setMaximum(len(parcels))
            for parcel in parcels:
                id = parcel.id
                sql = "select * from base.st_auto_street_select("+ str(str_calc_count) + ", " + str(str_select_count) + ", " + str(id) + "::bigint)"

                result = self.session.execute(sql)
                street_id = None
                for row in result:
                    street_id = row[0]
                if street_id is not None and id is not None:
                    parcel = self.session.query(CaParcelAddress).filter(CaParcelAddress.id == id).one()
                    sql_side = "select * from base.st_street_line_parcel_side2(" + str(street_id) + ", " + str(id) + "::bigint)"
                    result_side = self.session.execute(sql_side)
                    str_side = None
                    for row in result_side:
                        str_side = row[0]
                    parcel.street_id = street_id
                    if str_side:
                        parcel.street_side = str_side
                value_p = self.parcel_progressBar.value() + 1
                self.parcel_progressBar.setValue(value_p)

    @pyqtSlot()
    def on_load_street_parcels_button_clicked(self):

        if self.str_id:
            sql = "(select row_number() over() as gid, id, parcel_id, street_id, geometry from data_address.ca_parcel_address where street_id = "+ str(self.str_id) +")"

            root = QgsProject.instance().layerTreeRoot()
            mygroup = root.findGroup(U"Хаяг")
            layer_list = []
            layers = QgsMapLayerRegistry.instance().mapLayers()
            layer_name = "ParcelByStreet"

            for id, layer in layers.iteritems():
                if layer.type() == QgsMapLayer.VectorLayer:
                    if layer.name() == layer_name:
                        layer_list.append(id)

            vlayer_parcel = LayerUtils.layer_by_data_source("", sql)
            if vlayer_parcel:
                QgsMapLayerRegistry.instance().removeMapLayers(layer_list)
            vlayer_parcel = LayerUtils.load_temp_table(sql, layer_name)

            myalayer = root.findLayer(vlayer_parcel.id())
            # if myalayer is None:
            mygroup.addLayer(vlayer_parcel)

            symbol = QgsSymbolV2.defaultSymbol(vlayer_parcel.geometryType())

            symbol.setColor(QColor.fromRgb(255, 0, 0))
            vlayer_parcel.triggerRepaint()

    @pyqtSlot()
    def on_load_parcel_street_button_clicked(self):

        selected_row = self.address_parcel_twidget.currentRow()
        id = self.address_parcel_twidget.item(selected_row, 0).data(Qt.UserRole + 1)

        sql = "(select row_number() over() as gid, str_type, line_geom as geometry from ( " \
                "select 1 as str_type, ss.line_geom from data_address.st_street ss  " \
                "where ss.id in  " \
                "(select street_id from data_address.ca_parcel_address cpa  " \
                "where cpa.id = " + str(id) + ") " \
                "union all " \
                "select 2 as str_type, ss.line_geom from data_address.st_road ss  " \
                "where ss.belong_street_id in  " \
                "(select street_id from data_address.ca_parcel_address cpa  " \
                "where cpa.id = " + str(id) + "))xxx)"

        root = QgsProject.instance().layerTreeRoot()
        mygroup = root.findGroup(U"Хаяг")
        layer_list = []
        layers = QgsMapLayerRegistry.instance().mapLayers()
        layer_name = "StreetByParcel"
        column_name = "str_type"
        for id, layer in layers.iteritems():
            if layer.type() == QgsMapLayer.VectorLayer:
                if layer.name() == layer_name:
                    layer_list.append(id)

        vlayer_parcel = LayerUtils.layer_by_data_source("", sql)
        if vlayer_parcel:
            QgsMapLayerRegistry.instance().removeMapLayers(layer_list)
        vlayer_parcel = LayerUtils.load_temp_table(sql, layer_name)

        myalayer = root.findLayer(vlayer_parcel.id())
        # if myalayer is None:
        mygroup.addLayer(vlayer_parcel)
        self.__load_layer_style_parcel(vlayer_parcel, column_name, sql)

    def __load_layer_style(self, vlayer_parcel, column_name, sql):

        sql = "select str_type from (" + sql + " )xxx group by str_type order by str_type"

        categories = []
        parcels = self.session.execute(sql).fetchall()
        for row in parcels:
            str_type = row[0]

            fill_color = "#009732"
            boundary_color = "#009732"
            opacity = 0.5
            description = u"Үндсэн гудамж"
            if str_type == 2:
                fill_color = "#ff0730"
                boundary_color = "#ff0730"
                description = u"Дэд гудамж"

            self.__categorized_style(categories, vlayer_parcel, fill_color, boundary_color, opacity, str_type,
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

    def __rgb_to_hex(self, red, green, blue):
        """Return color as #rrggbb for the given color values."""
        return '#%02x%02x%02x' % (red, green, blue)

    @pyqtSlot()
    def on_get_entry_parcels_button_clicked(self):

        self.parcel_progressBar.setValue(0)
        a_count = 0
        if self.is_selected_parcels_chbox.isChecked():
            parcelLayer = LayerUtils.layer_by_data_source("data_address", "ca_parcel_address_view")
            select_feature = parcelLayer.selectedFeatures()
            str_count = str(len(select_feature))
            self.parcel_progressBar.setMaximum(len(select_feature))
            str_count_lbl = str_count + '/' + str(a_count)
            self.parcel_count_lbl.setText(str_count_lbl)

            # self.session.execute("alter table data_address.st_entrance disable trigger a_create_address_entry_id;")
            for feature in select_feature:
                attr = feature.attributes()
                id = attr[0]

                sql = "select * from base.st_generate_parcel_entry_auto(" + str(id) + ");"

                geometry = None
                result = self.session.execute(sql)
                for item_row in result:
                    entry_type = item_row[0]
                    x = item_row[1]
                    y = item_row[2]

                    geom_spot4 = QgsPoint(x, y)
                    geometry = QgsGeometry.fromPoint(geom_spot4)

                    geometry = WKTElement(geometry.exportToWkt(), srid=4326)
                if geometry is not None:
                    count = self.session.query(StEntrance).filter(StEntrance.parcel_id == id).count()
                    if count == 0:

                        object = StEntrance()
                        object.type = entry_type
                        object.parcel_id = id
                        object.is_active = True
                        # object.au2 = self.au2
                        object.geometry = geometry
                        self.session.add(object)
                        self.session.flush()

                a_count = a_count + 1
                str_count_lbl = str_count + '/' + str(a_count)
                self.parcel_count_lbl.setText(str_count_lbl)
                value_p = self.parcel_progressBar.value() + 1
                self.parcel_progressBar.setValue(value_p)
            # self.session.execute("alter table data_address.st_entrance enable trigger a_create_address_entry_id;")
        else:
            print 'ffgg'

    @pyqtSlot()
    def on_get_str_start_button_clicked(self):

        self.progressBar.setValue(0)
        a_count = 0
        if self.is_selected_str_chbox.isChecked():
            parcelLayer = LayerUtils.layer_by_data_source("data_address", "st_street_line_view")
            select_feature = parcelLayer.selectedFeatures()
            str_count = str(len(select_feature))
            self.progressBar.setMaximum(len(select_feature))
            str_count_lbl = str_count + '/' + str(a_count)
            self.str_count_lbl.setText(str_count_lbl)

            for feature in select_feature:
                attr = feature.attributes()
                street_id = attr[1]

                sql = "select * from base.st_street_line_view_start_end_nodes_auto(" + str(street_id) + ");"

                geometry = None
                self.session.query(StStreetPoint).filter(StStreetPoint.street_id == street_id).delete()
                result = self.session.execute(sql)
                for item_row in result:
                    p_type = item_row[0]
                    street_id = item_row[1]

                    x = item_row[2]
                    y = item_row[3]

                    geom_spot4 = QgsPoint(x, y)
                    geometry = QgsGeometry.fromPoint(geom_spot4)

                    geometry = WKTElement(geometry.exportToWkt(), srid=4326)
                    if geometry is not None:

                        count = self.session.query(StStreetPoint). \
                            filter(StStreetPoint.geometry.ST_Equals(geometry)). \
                            filter(StStreetPoint.street_id == street_id).count()

                        if count == 0:
                            print geometry
                            print p_type
                            print count
                            object = StStreetPoint()
                            object.is_active = True
                            object.geometry = geometry
                            if p_type == 1:
                                object.point_type = 1
                            else:
                                object.point_type = 2
                            object.street_id = street_id
                            object.valid_from = DatabaseUtils.current_date_time()
                            object.created_at = DatabaseUtils.current_date_time()
                            object.updated_at = DatabaseUtils.current_date_time()
                            object.au1 = self.au1
                            object.au2 = self.au2
                            self.session.add(object)
                            self.session.commit()

                        # if count == 1:
                        #     object = self.session.query(StStreetPoint). \
                        #         filter(StStreetPoint.geometry.ST_Equals(geometry)).one()

                a_count = a_count + 1
                str_count_lbl = str_count + '/' + str(a_count)
                self.str_count_lbl.setText(str_count_lbl)
                value_p = self.progressBar.value() + 1
                self.progressBar.setValue(value_p)
        else:
            strs = self.session.query(StStreetLineView).all()
            self.progressBar.setMaximum(len(strs))
            str_count = str(len(strs))

            str_count_lbl = str_count + '/' +  str(a_count)
            self.str_count_lbl.setText(str_count_lbl)
            for value in strs:
                street_id = value.street_id

                sql = "select * from base.st_street_line_view_start_end_nodes_auto(" + str(street_id) + ");"
                self.session.query(StStreetPoint).filter(StStreetPoint.street_id == street_id).delete()
                geometry = None
                result = self.session.execute(sql)
                for item_row in result:
                    p_type = item_row[0]
                    street_id = item_row[1]
                    x = item_row[2]
                    y = item_row[3]

                    geom_spot4 = QgsPoint(x, y)
                    geometry = QgsGeometry.fromPoint(geom_spot4)
                    geometry = WKTElement(geometry.exportToWkt(), srid=4326)
                    if geometry is not None:
                        count = self.session.query(StStreetPoint). \
                            filter(StStreetPoint.geometry.ST_Equals(geometry)). \
                            filter(StStreetPoint.street_id == street_id).count()

                        if count == 0:
                            object = StStreetPoint()
                            object.is_active = True
                            object.geometry = geometry
                            # object.point_type = 1
                            object.street_id = street_id
                            if p_type == 1:
                                object.point_type = 1
                            else:
                                object.point_type = 2
                            object.valid_from = DatabaseUtils.current_date_time()
                            object.created_at = DatabaseUtils.current_date_time()
                            object.updated_at = DatabaseUtils.current_date_time()
                            object.au1 = self.au1
                            object.au2 = self.au2
                            self.session.add(object)
                            self.session.commit()

                        if count == 1:
                            object = self.session.query(StStreetPoint). \
                                filter(StStreetPoint.geometry.ST_Equals(geometry)).one()

                a_count = a_count + 1
                str_count_lbl = str_count + '/' + str(a_count)
                self.str_count_lbl.setText(str_count_lbl)
                value_p = self.progressBar.value() + 1
                self.progressBar.setValue(value_p)


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

    def __save_street_point(self):

        self.session.query(StStreetPoint).filter(StStreetPoint.street_id == self.str_id).delete()
        for row in range(self.str_nodes_twidget.rowCount()):
            item_main = self.str_nodes_twidget.item(row, 0)

            id = self.str_nodes_twidget.item(row, 0).data(Qt.UserRole)
            street_id = self.str_nodes_twidget.item(row, 0).data(Qt.UserRole + 1)
            x = self.str_nodes_twidget.item(row, 1).data(Qt.UserRole)
            y = self.str_nodes_twidget.item(row, 2).data(Qt.UserRole)

            geom_spot4 = QgsPoint(x, y)
            geometry = QgsGeometry.fromPoint(geom_spot4)

            geometry = WKTElement(geometry.exportToWkt(), srid=4326)

            count = self.session.query(StStreetPoint).\
                filter(StStreetPoint.geometry.ST_Equals(geometry)). \
                filter(StStreetPoint.street_id == street_id).count()

            if count == 0:
                object = StStreetPoint()
                object.is_active = True
                object.geometry = geometry
                object.valid_from = DatabaseUtils.current_date_time()
                object.created_at = DatabaseUtils.current_date_time()
                object.updated_at = DatabaseUtils.current_date_time()
                object.au1 = self.au1
                object.au2 = self.au2
                object.street_id = street_id
                if item_main.checkState() == Qt.Checked:
                    object.point_type = 1
                else:
                    object.point_type = 2
                self.session.add(object)
                self.session.flush()

            if count == 1:
                object = self.session.query(StStreetPoint). \
                    filter(StStreetPoint.geometry.ST_Equals(geometry)). \
                    filter(StStreetPoint.street_id == street_id).one()
                if item_main.checkState() == Qt.Checked:
                    object.point_type = 1
                else:
                    object.point_type = 2

    @pyqtSlot()
    def on_selected_parcel_load_button_clicked(self):

        layer_type_id = self.layer_type_cbox.itemData(self.layer_type_cbox.currentIndex())

        layer_type = self.session.query(ClParcelType).filter_by(code = layer_type_id).one()

        layer_name = None
        schema_name = None
        if layer_type.table_name == 'data_soums_union.ca_parcel_tbl':
            layer_name = "ca_parcel"
            schema_name = "data_soums_union"
        elif layer_type.table_name == 'data_soums_union.ca_tmp_parcel':
            layer_name = "ca_tmp_parcel_view"
            schema_name = "data_soums_union"
        elif layer_type.table_name == 'data_soums_union.ca_building_tbl':
            layer_name = "ca_building"
            schema_name = "data_soums_union"
        elif layer_type.table_name == 'data_soums_union.ca_tmp_building':
            layer_name = "ca_tmp_building_view"
            schema_name = "data_soums_union"
        elif layer_type.table_name == 'data_address.ca_parcel_address_view':
            layer_name = "ca_parcel_address_view"
            schema_name = "data_address"
        elif layer_type.table_name == 'data_address.ca_building_address_view':
            layer_name = "ca_building_address_view"
            schema_name = "data_address"

        if not layer_name:
            return
        parcelLayer = LayerUtils.layer_by_data_source(schema_name, layer_name)
        select_feature = parcelLayer.selectedFeatures()

        id = None
        for feature in select_feature:
            attr = feature.attributes()

            if len(attr) > 0:
                id = attr[0]
                geometry = WKTElement(feature.geometry().exportToWkt(), srid=4326)

        if id is None:
            return
        if layer_name == "ca_parcel_address_view":
            addrs_parcel = self.session.query(CaParcelAddress).filter_by(id=id).one()
            address_status = self.session.query(ClAddressStatus).filter_by(code=addrs_parcel.status).one()
            if not self.__is_add_addrs_parcel(addrs_parcel.id):
                count = self.address_parcel_twidget.rowCount()
                self.address_parcel_twidget.insertRow(count)

                item = QTableWidgetItem(str(addrs_parcel.parcel_id))
                item.setData(Qt.UserRole, addrs_parcel.parcel_id)
                item.setData(Qt.UserRole + 1, addrs_parcel.id)
                self.address_parcel_twidget.setItem(count, 0, item)

                item = QTableWidgetItem(unicode(layer_type.description))
                item.setData(Qt.UserRole, layer_type.code)
                item.setData(Qt.UserRole + 1, layer_type.layer_type)
                self.address_parcel_twidget.setItem(count, 1, item)

                item = QTableWidgetItem(unicode(address_status.description))
                item.setData(Qt.UserRole, address_status.code)
                self.address_parcel_twidget.setItem(count, 2, item)
        else:
            addrs_parcel_count = self.session.query(CaParcelAddress).\
                filter(CaParcelAddress.parcel_type == layer_type.code).\
                filter(CaParcelAddress.parcel_id == id).count()
            if addrs_parcel_count == 1:
                addrs_parcel = self.session.query(CaParcelAddress). \
                    filter(CaParcelAddress.parcel_type == layer_type.code). \
                    filter(CaParcelAddress.parcel_id == id).one()
                # PluginUtils.show_message(self, u'Анхааруулга', u'Энэ нэгж талбар хаягын мэдээллийн санд бүртгэлтэй байна.')
                # return

                message_box = QMessageBox()
                message_box.setText(u'Энэ нэгж талбар хаягын мэдээллийн санд бүртгэлтэй байна. Жагсаалтад нэмэх үү?')

                yes_button = message_box.addButton(u'Тийм', QMessageBox.ActionRole)
                message_box.addButton(u'Үгүй', QMessageBox.ActionRole)
                message_box.exec_()
                address_status = self.session.query(ClAddressStatus).filter_by(code=addrs_parcel.status).one()
                if message_box.clickedButton() == yes_button:
                    if not self.__is_add_addrs_parcel(addrs_parcel.id):
                        count = self.address_parcel_twidget.rowCount()
                        self.address_parcel_twidget.insertRow(count)

                        item = QTableWidgetItem(str(addrs_parcel.parcel_id))
                        item.setData(Qt.UserRole, addrs_parcel.parcel_id)
                        item.setData(Qt.UserRole + 1, addrs_parcel.id)
                        self.address_parcel_twidget.setItem(count, 0, item)

                        item = QTableWidgetItem(unicode(layer_type.description))
                        item.setData(Qt.UserRole, layer_type.code)
                        item.setData(Qt.UserRole + 1, layer_type.layer_type)
                        self.address_parcel_twidget.setItem(count, 1, item)

                        item = QTableWidgetItem(unicode(address_status.description))
                        item.setData(Qt.UserRole, address_status.code)
                        self.address_parcel_twidget.setItem(count, 2, item)

            if addrs_parcel_count == 0:
                addrs_parcel_overlaps_count = self.session.query(CaParcelAddress).\
                    filter(geometry.ST_Overlaps(CaParcelAddress.geometry)).\
                    filter(CaParcelAddress.is_active == True).count()

                if addrs_parcel_overlaps_count == 0:

                    address_status = self.session.query(ClAddressStatus).filter_by(code = 1).one()

                    addrs_parcel = CaParcelAddress()
                    addrs_parcel.parcel_id = id
                    addrs_parcel.is_active = True
                    addrs_parcel.geometry = geometry
                    addrs_parcel.parcel_type = layer_type.code
                    addrs_parcel.status = 1

                    self.session.add(addrs_parcel)
                    self.session.flush()

                    count = self.address_parcel_twidget.rowCount()
                    self.address_parcel_twidget.insertRow(count)

                    item = QTableWidgetItem(str(id))
                    item.setData(Qt.UserRole, id)
                    item.setData(Qt.UserRole + 1, addrs_parcel.id)
                    self.address_parcel_twidget.setItem(count, 0, item)

                    item = QTableWidgetItem(unicode(layer_type.description))
                    item.setData(Qt.UserRole, layer_type.code)
                    item.setData(Qt.UserRole + 1, layer_type.layer_type)
                    self.address_parcel_twidget.setItem(count, 1, item)

                    item = QTableWidgetItem(unicode(address_status.description))
                    item.setData(Qt.UserRole, address_status.code)
                    self.address_parcel_twidget.setItem(count, 2, item)

    #building add
    @pyqtSlot()
    def on_selected_building_load_button_clicked(self):

        layer_type_id = self.building_layer_type_cbox.itemData(self.building_layer_type_cbox.currentIndex())

        layer_type = self.session.query(ClParcelType).filter_by(code=layer_type_id).one()

        layer_name = None
        schema_name = None
        if layer_type.table_name == 'data_soums_union.ca_parcel_tbl':
            layer_name = "ca_parcel"
            schema_name = "data_soums_union"
        elif layer_type.table_name == 'data_soums_union.ca_tmp_parcel':
            layer_name = "ca_tmp_parcel_view"
            schema_name = "data_soums_union"
        elif layer_type.table_name == 'data_soums_union.ca_building_tbl':
            layer_name = "ca_building"
            schema_name = "data_soums_union"
        elif layer_type.table_name == 'data_soums_union.ca_tmp_building':
            layer_name = "ca_tmp_building_view"
            schema_name = "data_soums_union"
        elif layer_type.table_name == 'data_address.ca_parcel_address_view':
            layer_name = "ca_parcel_address_view"
            schema_name = "data_address"
        elif layer_type.table_name == 'data_address.ca_building_address_view':
            layer_name = "ca_building_address_view"
            schema_name = "data_address"

        if not layer_name:
            return
        parcelLayer = LayerUtils.layer_by_data_source(schema_name, layer_name)
        select_feature = parcelLayer.selectedFeatures()

        id = None
        for feature in select_feature:
            attr = feature.attributes()

            if len(attr) > 0:
                id = attr[0]
                geometry = WKTElement(feature.geometry().exportToWkt(), srid=4326)

        if id is None:
            return
        if layer_name == "ca_building_address_view":
            addrs_building = self.session.query(CaBuildingAddress).filter_by(id=id).one()
            address_status = self.session.query(ClAddressStatus).filter_by(code=addrs_building.status).one()
            if not self.__is_add_addrs_building(addrs_building.id):
                count = self.address_building_twidget.rowCount()
                self.address_building_twidget.insertRow(count)

                item = QTableWidgetItem(str(addrs_building.building_id))
                item.setData(Qt.UserRole, addrs_building.building_id)
                item.setData(Qt.UserRole + 1, addrs_building.id)
                self.address_building_twidget.setItem(count, 0, item)

                item = QTableWidgetItem(unicode(layer_type.description))
                item.setData(Qt.UserRole, layer_type.code)
                item.setData(Qt.UserRole + 1, layer_type.layer_type)
                self.address_building_twidget.setItem(count, 1, item)

                item = QTableWidgetItem(unicode(address_status.description))
                item.setData(Qt.UserRole, address_status.code)
                self.address_building_twidget.setItem(count, 2, item)
        else:
            addrs_building_count = self.session.query(CaBuildingAddress). \
                filter(CaBuildingAddress.parcel_type == layer_type.code). \
                filter(CaBuildingAddress.building_id == id).count()
            if addrs_building_count == 1:
                addrs_building = self.session.query(CaBuildingAddress). \
                    filter(CaBuildingAddress.parcel_type == layer_type.code). \
                    filter(CaBuildingAddress.building_id == id).one()
                # PluginUtils.show_message(self, u'Анхааруулга', u'Энэ нэгж талбар хаягын мэдээллийн санд бүртгэлтэй байна.')
                # return

                message_box = QMessageBox()
                message_box.setText(u'Энэ нэгж талбар хаягын мэдээллийн санд бүртгэлтэй байна. Жагсаалтад нэмэх үү?')

                yes_button = message_box.addButton(u'Тийм', QMessageBox.ActionRole)
                message_box.addButton(u'Үгүй', QMessageBox.ActionRole)
                message_box.exec_()
                address_status = self.session.query(ClAddressStatus).filter_by(code=addrs_building.status).one()
                if message_box.clickedButton() == yes_button:
                    if not self.__is_add_addrs_building(addrs_building.id):
                        count = self.address_building_twidget.rowCount()
                        self.address_building_twidget.insertRow(count)

                        item = QTableWidgetItem(str(addrs_building.building_id))
                        item.setData(Qt.UserRole, addrs_building.building_id)
                        item.setData(Qt.UserRole + 1, addrs_building.id)
                        self.address_building_twidget.setItem(count, 0, item)

                        item = QTableWidgetItem(unicode(layer_type.description))
                        item.setData(Qt.UserRole, layer_type.code)
                        item.setData(Qt.UserRole + 1, layer_type.layer_type)
                        self.address_building_twidget.setItem(count, 1, item)

                        item = QTableWidgetItem(unicode(address_status.description))
                        item.setData(Qt.UserRole, address_status.code)
                        self.address_building_twidget.setItem(count, 2, item)

            if addrs_building_count == 0:
                addrs_building_overlaps_count = self.session.query(CaBuildingAddress). \
                    filter(geometry.ST_Overlaps(CaBuildingAddress.geometry)). \
                    filter(CaBuildingAddress.is_active == True).count()

                if addrs_building_overlaps_count == 0:
                    address_status = self.session.query(ClAddressStatus).filter_by(code=1).one()

                    addrs_building = CaBuildingAddress()
                    addrs_building.building_id = id
                    addrs_building.is_active = True
                    addrs_building.geometry = geometry
                    addrs_building.parcel_type = layer_type.code
                    addrs_building.status = 1

                    self.session.add(addrs_building)
                    self.session.flush()

                    count = self.address_building_twidget.rowCount()
                    self.address_building_twidget.insertRow(count)

                    item = QTableWidgetItem(str(id))
                    item.setData(Qt.UserRole, id)
                    item.setData(Qt.UserRole + 1, addrs_parcel.id)
                    self.address_building_twidget.setItem(count, 0, item)

                    item = QTableWidgetItem(unicode(layer_type.description))
                    item.setData(Qt.UserRole, layer_type.code)
                    item.setData(Qt.UserRole + 1, layer_type.layer_type)
                    self.address_building_twidget.setItem(count, 1, item)

                    item = QTableWidgetItem(unicode(address_status.description))
                    item.setData(Qt.UserRole, address_status.code)
                    self.address_building_twidget.setItem(count, 2, item)

    @pyqtSlot()
    def on_selected_building_remove_button_clicked(self):

        selected_row = self.address_building_twidget.currentRow()
        id = self.address_building_twidget.item(selected_row, 0).data(Qt.UserRole + 1)
        #
        # self.session.query(StEntrance).filter(StEntrance.parcel_id == id).delete()
        # self.session.query(CaBuildingAddress).filter(CaBuildingAddress.id == id).delete()

        self.address_building_twidget.removeRow(selected_row)

    @pyqtSlot()
    def on_selected_parcel_remove_button_clicked(self):

        selected_row = self.address_parcel_twidget.currentRow()
        if self.address_parcel_twidget.item(selected_row, 0):
            id = self.address_parcel_twidget.item(selected_row, 0).data(Qt.UserRole + 1)
        #
        # self.session.query(StEntrance).filter(StEntrance.parcel_id == id).delete()
        # self.session.query(CaParcelAddress).filter(CaParcelAddress.id == id).delete()

        self.address_parcel_twidget.removeRow(selected_row)

    def __is_add_addrs_parcel(self, id):

        is_true = False
        for row in range(self.address_parcel_twidget.rowCount()):
            item_id = self.address_parcel_twidget.item(row, 0)
            addrs_id = item_id.data(Qt.UserRole + 1)

            if addrs_id == id:
                is_true = True

        return is_true

    def __is_add_addrs_building(self, id):

        is_true = False
        for row in range(self.address_building_twidget.rowCount()):
            item_id = self.address_building_twidget.item(row, 0)
            addrs_id = item_id.data(Qt.UserRole + 1)

            if addrs_id == id:
                is_true = True

        return is_true

    @pyqtSlot()
    def on_get_address_button_clicked(self):

        if self.tabWidget.currentIndex() == 0:
            self.__get_parcel_address()
        if self.tabWidget.currentIndex() == 1:
            self.__get_building_address()

    def __get_parcel_address(self):

        selected_row = self.address_parcel_twidget.currentRow()
        if selected_row == -1:
            return
        id = self.address_parcel_twidget.item(selected_row, 0).data(Qt.UserRole + 1)

        addrs_parcel_count = self.session.query(CaParcelAddress).filter_by(id=id).count()
        if addrs_parcel_count == 0:
            PluginUtils.show_message(self, u'Анхааруулга', u'Энэ нэгж талбар хаяг мэдээллийн санд ороогүй байна.')
            return

        addrs_parcel = self.session.query(CaParcelAddress).filter_by(id=id).one()

        status_code = 1
        if addrs_parcel.status_ref:
            status = addrs_parcel.status_ref
            status_code = status.code

        if status_code == 3:
            PluginUtils.show_message(self, u'Анхааруулга', u'Энэ нэгж талбарын хаяг баталгаажсан байна.')
            return

        entry_count = self.session.query(StEntrance).filter(StEntrance.parcel_id == addrs_parcel.id).count()

        if entry_count == 0:
            PluginUtils.show_message(self, u'Анхааруулга', u'Энэ нэгж талбарын орц, гарцыг тодорхойлоогүй байна.')
            return
        str_id = self.streets_cbox.itemData(self.streets_cbox.currentIndex())

        if not str_id:
            return
        self.str_id = str_id
        street = self.session.query(StStreet).filter_by(id=str_id).one()
        str_shape = street.street_shape_id_ref

        if street.start_number is None:
            PluginUtils.show_message(self, u'Анхааруулга', u'Гудамжны бүртгэлд нэгж талбарт олгох хаягын эхлэх дугаарыг оруулаагүй байна.')
            return

        if self.side == '-1':
            sql = "select unnest(string_to_array(base.st_generate_address_khashaa_no_sondgoi(" + str(
                str_id) + ", " + str(id) + ")::text, ','));"
            result = self.session.execute(sql)
            for row in result:
                self.parcel_address_no = row[0]
        if self.side == '1':
            sql = "select unnest(string_to_array(base.st_generate_address_khashaa_no_tegsh(" + str(
                str_id) + ", " + str(id) + ")::text, ','));"
            result = self.session.execute(sql)
            for row in result:
                self.parcel_address_no = row[0]
        if not self.parcel_address_no:
            return

        str_addrs_count = self.session.query(StStreet).\
            join(CaParcelAddress, StStreet.id == CaParcelAddress.street_id).\
            filter(StStreet.id == str_id).\
            filter(CaParcelAddress.address_parcel_no == self.parcel_address_no). \
            filter(CaParcelAddress.id != addrs_parcel.id).count()
        if str_addrs_count > 0:
            PluginUtils.show_message(self, u'Анхааруулга',
                                     u'Гудамжинд нэгж талбарын ' + unicode(self.parcel_address_no) + u'q хаяг давхардаж байна.')
            return


        zipcode = self.session.query(AuZipCodeArea). \
            filter(func.ST_Centroid(addrs_parcel.geometry).ST_Within(AuZipCodeArea.geometry)).first()
        zip_addrs_count = self.session.query(AuZipCodeArea).\
            join(CaParcelAddress, AuZipCodeArea.id == CaParcelAddress.zipcode_id). \
            filter(CaParcelAddress.address_parcel_no == self.parcel_address_no).\
            filter(AuZipCodeArea.id == zipcode.id). \
            filter(CaParcelAddress.id != addrs_parcel.id).count()
        # if zip_addrs_count > 0:
        #     PluginUtils.show_message(self, u'Анхааруулга',
        #                              u'Шуудангийн бүсчлэлд нэгж талбарын ' + unicode(self.parcel_address_no) + u' хаяг давхардаж байна.')
        #     return

        if self.khashaa_no_edit.text() != self.parcel_address_no:
            self.khashaa_no_edit.setText(self.parcel_address_no)

        # addrs_parcel.street_id = str_id
        # addrs_parcel.address_parcel_no = self.parcel_address_no

    #building
    def __get_building_address(self):

        selected_row = self.address_building_twidget.currentRow()
        if selected_row == -1:
            return
        id = self.address_building_twidget.item(selected_row, 0).data(Qt.UserRole + 1)

        addrs_parcel_count = self.session.query(CaBuildingAddress).filter_by(id=id).count()
        if addrs_parcel_count == 0:
            PluginUtils.show_message(self, u'Анхааруулга', u'Энэ барилга хаягын мэдээллийн санд ороогүй байна.')
            return

        addrs_parcel = self.session.query(CaBuildingAddress).filter_by(id=id).one()

        status_code = 1
        if addrs_parcel.status_ref:
            status = addrs_parcel.status_ref
            status_code = status.code

        if status_code == 3:
            PluginUtils.show_message(self, u'Анхааруулга', u'Энэ барилгын хаяг баталгаажсан байна.')
            return

        entry_count = self.session.query(StEntrance).filter(StEntrance.building_id == addrs_parcel.id).count()

        if entry_count == 0:
            PluginUtils.show_message(self, u'Анхааруулга', u'Энэ барилгын орц, гарцыг тодорхойлоогүй байна.')
            return
        str_id = self.building_streets_cbox.itemData(self.building_streets_cbox.currentIndex())

        if not str_id:
            return
        self.str_id = str_id
        street = self.session.query(StStreet).filter_by(id=str_id).one()
        str_shape = street.street_shape_id_ref
        if street.building_start_number is None:
            PluginUtils.show_message(self, u'Анхааруулга', u'Гудамжны бүртгэлд барилгад олгох хаягын эхлэх дугаарыг оруулаагүй байна.')
            return


        sql = "select unnest(string_to_array(base.st_generate_address_building_without_parcel(" + str(
            str_id) + ", " + str(id) + ")::text, ','));"
        result = self.session.execute(sql)

        for row in result:
            self.building_address_no = row[0]
        # if self.side == '-1':
        #     sql = "select unnest(string_to_array(base.st_generate_address_khashaa_no_sondgoi(" + str(
        #         str_id) + ", " + str(id) + ")::text, ','));"
        #     result = self.session.execute(sql)
        #     for row in result:
        #         parcel_address_no = row[0]
        # if self.side == '1':
        #     sql = "select unnest(string_to_array(base.st_generate_address_khashaa_no_tegsh(" + str(
        #         str_id) + ", " + str(id) + ")::text, ','));"
        #     result = self.session.execute(sql)
        #     for row in result:
        #         parcel_address_no = row[0]
        if self.building_address_no is None:
            return
        str_addrs_count = self.session.query(StStreet).\
            join(CaBuildingAddress, StStreet.id == CaBuildingAddress.street_id). \
            filter(StStreet.id == str_id).\
            filter(CaBuildingAddress.address_building_no == self.building_address_no).\
            filter(CaBuildingAddress.id != addrs_parcel.id).count()
        if str_addrs_count > 0:
            PluginUtils.show_message(self, u'Анхааруулга',
                                     u'Гудамжинд барилгын ' + unicode(self.building_address_no) + u' хаяг давхардаж байна.')
            return

        zipcode = self.session.query(AuZipCodeArea). \
            filter(func.ST_Centroid(addrs_parcel.geometry).ST_Within(AuZipCodeArea.geometry)).first()

        zip_addrs_count = self.session.query(AuZipCodeArea).\
            join(CaBuildingAddress, AuZipCodeArea.id == CaBuildingAddress.zipcode_id). \
            filter(CaBuildingAddress.address_building_no == self.building_address_no). \
            filter(AuZipCodeArea.id == zipcode.id). \
            filter(CaBuildingAddress.id != addrs_parcel.id).count()

        if zip_addrs_count > 0:
            PluginUtils.show_message(self, u'Анхааруулга',
                                     u'Шуудангийн бүсчлэлд барилгын ' + unicode(self.building_address_no) + u' хаяг давхардаж байна.')
            return

        if self.building_no_edit.text() != self.building_address_no:
            self.building_no_edit.setText(self.building_address_no)

        # addrs_parcel.street_id = str_id
        # addrs_parcel.address_building_no = self.building_address_no

    def __save_parcel_address(self):

        selected_row = self.address_parcel_twidget.currentRow()
        if selected_row == -1:
            return

        id = self.address_parcel_twidget.item(selected_row, 0).data(Qt.UserRole + 1)

        addrs_parcel_count = self.session.query(CaParcelAddress).filter_by(id=id).count()
        if addrs_parcel_count == 0:
            PluginUtils.show_message(self, u'Анхааруулга', u'Энэ нэгж талбар хаяг мэдээллийн санд ороогүй байна.')
            return

        addrs_parcel = self.session.query(CaParcelAddress).filter_by(id=id).one()

        addrs_parcel.street_id = self.str_id
        addrs_parcel.address_parcel_no = self.parcel_address_no

    def __save_building_address(self):

        selected_row = self.address_building_twidget.currentRow()
        if selected_row == -1:
            return

        id = self.address_building_twidget.item(selected_row, 0).data(Qt.UserRole + 1)

        addrs_parcel_count = self.session.query(CaBuildingAddress).filter_by(id=id).count()
        if addrs_parcel_count == 0:
            PluginUtils.show_message(self, u'Анхааруулга', u'Энэ нэгж талбар хаяг мэдээллийн санд ороогүй байна.')
            return

        addrs_parcel = self.session.query(CaBuildingAddress).filter_by(id=id).one()

        addrs_parcel.street_id = self.str_id
        addrs_parcel.address_building_no = self.building_address_no

    @pyqtSlot()
    def on_apply_address_button_clicked(self):

        if self.tabWidget.currentIndex() == 0:
            self.__save_parcel_address()
            self.session.commit()
        if self.tabWidget.currentIndex() == 1:
            self.__save_building_address()
            self.session.commit()
        if self.tabWidget.currentIndex() == 2:
            self.__save_street_point()
        if self.tabWidget.currentIndex() == 3:
            self.session.commit()

    @pyqtSlot(QTableWidgetItem)
    def on_address_parcel_twidget_itemClicked(self, item):

        selected_row = self.address_parcel_twidget.currentRow()
        id = self.address_parcel_twidget.item(selected_row, 0).data(Qt.UserRole + 1)

        str_count = self.str_count_sbox.value()
        sql = "select s.id, s.code, s.name from data_address.st_all_street_line_view s, data_address.ca_parcel_address p " \
            "where p.id = " + str(id) + " group by s.name, s.id, s.code " \
            "order by min(st_distance(s.geometry, p.geometry)) asc limit " + str(str_count) + ";"

        result = self.session.execute(sql)

        self.streets_cbox.clear()
        for row in result:
            str_id = row[0]
            str_code = row[1]
            str_name = row[2]

            street_name = str_name
            if str_code:
                street_name = str_name + " - " + str_code
            self.streets_cbox.addItem(street_name, str_id)

        # layer = LayerUtils.layer_by_data_source("data_address", 'st_road_line_view')
        # self.__select_feature(str(id), layer)

    #building
    @pyqtSlot(QTableWidgetItem)
    def on_address_building_twidget_itemClicked(self, item):

        selected_row = self.address_building_twidget.currentRow()
        id = self.address_building_twidget.item(selected_row, 0).data(Qt.UserRole + 1)

        str_count = self.building_str_count_sbox.value()
        sql = "select s.id, s.code, s.name from data_address.st_all_street_line_view s, data_address.ca_building_address p " \
              "where p.id = " + str(id) + " group by s.name, s.id, s.code " \
                                          "order by min(st_distance(s.geometry, p.geometry)) asc limit " + str(
            str_count) + ";"

        result = self.session.execute(sql)

        self.building_streets_cbox.clear()
        for row in result:
            str_id = row[0]
            str_code = row[1]
            str_name = row[2]

            street_name = str_name
            if str_code:
                street_name = str_name + " - " + str_code
            self.building_streets_cbox.addItem(street_name, str_id)

    @pyqtSlot(int)
    def on_str_count_sbox_valueChanged(self, str_count):

        selected_row = self.address_parcel_twidget.currentRow()
        id = self.address_parcel_twidget.item(selected_row, 0).data(Qt.UserRole + 1)

        str_count = self.str_count_sbox.value()
        sql = "select s.id, s.code, s.name from data_address.st_all_street_line_view s, data_address.ca_parcel_address p " \
              "where p.id = " + str(id) + " group by s.name, s.id, s.code " \
                                          "order by min(st_distance(s.geometry, p.geometry)) asc limit " + str(str_count) + ";"

        result = self.session.execute(sql)

        self.streets_cbox.clear()
        for row in result:
            str_id = row[0]
            str_code = row[1]
            str_name = row[2]

            street_name = str_name
            if str_code:
                street_name = str_name + " - " + str_code
            self.streets_cbox.addItem(street_name, str_id)

    #building
    @pyqtSlot(int)
    def on_building_str_count_sbox_valueChanged(self, str_count):

        selected_row = self.address_building_twidget.currentRow()
        id = self.address_building_twidget.item(selected_row, 0).data(Qt.UserRole + 1)

        str_count = self.building_str_count_sbox.value()
        sql = "select s.id, s.code, s.name from data_address.st_all_street_line_view s, data_address.ca_building_address p " \
              "where p.id = " + str(id) + " group by s.name, s.id, s.code " \
                                          "order by min(st_distance(s.geometry, p.geometry)) asc limit " + str(
            str_count) + ";"

        result = self.session.execute(sql)

        self.building_streets_cbox.clear()
        for row in result:
            str_id = row[0]
            str_code = row[1]
            str_name = row[2]

            street_name = str_name
            if str_code:
                street_name = str_name + " - " + str_code
            self.building_streets_cbox.addItem(street_name, str_id)

    @pyqtSlot(int)
    def on_streets_cbox_currentIndexChanged(self, index):

        str_id = self.streets_cbox.itemData(self.streets_cbox.currentIndex())

        if not str_id:
            return
        street = self.session.query(StStreet).filter_by(id=str_id).one()
        str_shape = street.street_shape_id_ref

        selected_row = self.address_parcel_twidget.currentRow()
        id = self.address_parcel_twidget.item(selected_row, 0).data(Qt.UserRole + 1)

        entry_count = self.session.query(StEntrance).\
            filter(StEntrance.parcel_id == id).count()
        if entry_count == 0:
            self.str_type_lbl.setText(u'Энэ нэгж талбарын орц, гарцыг тодорхойлоогүй байна.')
            return

        str_start_point_count = self.session.query(StStreetPoint).\
            filter(StStreetPoint.street_id == str_id).\
            filter(StStreetPoint.point_type == 1).count()
        if str_start_point_count == 0:
            self.str_type_lbl.setText(u'Гудамжны эхлэлийг тодорхойлоогүй байна. Гудамжны бүртгэлрүү орж засна уу!')
            return
        # sql = "select unnest(string_to_array(base.st_street_parcel_side_with_str_start_point(" + str(str_id) + ", " + str(id) + ")::text, ','));"
        sql = "select unnest(string_to_array(base.st_street_line_parcel_side2(" + str(
            str_id) + ", " + str(id) + ")::text, ','));"
        result = self.session.execute(sql)

        for row in result:
            self.side = row[0]

        if not str_shape:
            self.str_type_lbl.setText(u'Гудамжны хэлбэрийг тодорхойлоогүй байна. Гудамжны бүртгэлрүү орж засна уу!')
        else:
            self.str_type_lbl.setText(unicode(str_shape.description))

        if self.side == '-1':
            self.str_txt_lbl.setText(u'Гудамжны зүүн гар талд байрлаж байгаа тул СОНДГОЙ дугаар авна')

        if self.side == '1':
            self.str_txt_lbl.setText(u'Гудамжны баруун гар талд байрлаж байгаа тул ТЭГШ дугаар авна')

        layer = LayerUtils.layer_by_data_source("data_address", 'st_street_line_view')
        self.__select_feature(str(str_id), layer)

    #building
    @pyqtSlot(int)
    def on_building_streets_cbox_currentIndexChanged(self, index):

        str_id = self.building_streets_cbox.itemData(self.building_streets_cbox.currentIndex())

        if not str_id:
            return
        street = self.session.query(StStreet).filter_by(id=str_id).one()
        str_shape = street.street_shape_id_ref

        selected_row = self.address_building_twidget.currentRow()
        id = self.address_building_twidget.item(selected_row, 0).data(Qt.UserRole + 1)

        sql = "select unnest(string_to_array(base.st_street_building_side_with_str_start_point(" + str(
            str_id) + ", " + str(id) + ")::text, ','));"
        result = self.session.execute(sql)

        for row in result:
            self.side = row[0]

        if not str_shape:
            self.building_str_type_lbl.setText(u'Гудамжны хэлбэрийг тодорхойлоогүй байна. Гудамжны бүртгэлрүү орж засна уу!')
        else:
            self.building_str_type_lbl.setText(unicode(str_shape.description))

        if self.side == '-1':
            self.building_str_txt_lbl.setText(u'Гудамжны зүүн гар талд байрлаж байгаа тул СОНДГОЙ дугаар авна')

        if self.side == '1':
            self.building_str_txt_lbl.setText(u'Гудамжны баруун гар талд байрлаж байгаа тул ТЭГШ дугаар авна')

        layer = LayerUtils.layer_by_data_source("data_address", 'st_street_line_view')
        self.__select_feature(str(str_id), layer)

    @pyqtSlot()
    def on_address_raster_layer_button_clicked(self):

        root = QgsProject.instance().layerTreeRoot()

        mygroup = root.findGroup(U"Хаяг")
        myNewGroup = root.findGroup(U"Хаяг засварлалт")
        if mygroup is None:
            group = root.insertGroup(8, u"Хаяг")
            group.setExpanded(False)
            if myNewGroup is None:
                myNewGroup = group.addGroup(u"Хаяг засварлалт")

        urlWithParams = 'url=http://nsdi.gov.mn:8080/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=BaseMap&bbox=-181.8000030517578%2C-90.86817169189453%2C181.80001831054688%2C90.00000000000006&width=768&height=382&srs=EPSG%3A4326&styles=&format=application/openlayers'
        rlayer = QgsRasterLayer(urlWithParams, 'Base Layer', 'wms')
        rlayer.isValid()
        vlayer = QgsMapLayerRegistry.instance().addMapLayer(rlayer)
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            myNewGroup.addLayer(vlayer)

    @pyqtSlot()
    def on_address_layer_button_clicked(self):

        root = QgsProject.instance().layerTreeRoot()

        mygroup = root.findGroup(U"Хаяг")
        myNewGroup = root.findGroup(U"Хаяг засварлалт")
        if mygroup is None:
            group = root.insertGroup(8, u"Хаяг")
            group.setExpanded(False)
            if myNewGroup is None:
                myNewGroup = group.addGroup(u"Хаяг засварлалт")

        vlayer = LayerUtils.layer_by_data_source("data_address", "ca_parcel_address_no_entry_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("ca_parcel_address_no_entry_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "template\style/geocad_building_view.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "No Entry Parcel"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            myNewGroup.addLayer(vlayer)

        vlayer = LayerUtils.layer_by_data_source("data_address", "geocad_building_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("geocad_building_view", "gid", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "template\style/geocad_building_view.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "GeoCad Building"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            myNewGroup.addLayer(vlayer)
        # root.findLayer(vlayer.id()).setVisible(0)

        vlayer = LayerUtils.layer_by_data_source("data_address", "geocad_parcel_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("geocad_parcel_view", "gid", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "template\style/geocad_parcel_view.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "GeoCad Parcel"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            myNewGroup.addLayer(vlayer)

        vlayer = LayerUtils.layer_by_data_source("data_address", "geocad_street_view")
        if vlayer is None:
            vlayer = LayerUtils.load_line_layer_base_layer("geocad_street_view", "gid", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "template\style/geocad_street_view.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "GeoCad Street"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            myNewGroup.addLayer(vlayer)

        vlayer = LayerUtils.layer_by_data_source("data_address", "geocad_street_point_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("geocad_street_point_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "template\style/geocad_street_point_view.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "GeoCad Street Point"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            myNewGroup.addLayer(vlayer)

        addrs_group = root.findGroup(u"Хаяг")
        addrs_parcel_group = root.findGroup(u"Хаягийн нэгж талбар")
        addrs_building_group = root.findGroup(u"Хаягийн барилга")

        vlayer = LayerUtils.layer_by_data_source("data_address", "ca_parcel_address_bairzui_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("ca_parcel_address_bairzui_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/ca_parcel_address_bairzui_view.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", " Address BairZui Parcel"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_parcel_group.addLayer(vlayer)

        vlayer = LayerUtils.layer_by_data_source("data_address", "ca_parcel_address_cadastre_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("ca_parcel_address_cadastre_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/ca_parcel_address_cadastre_view.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", " Address Cadastre Parcel"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_parcel_group.addLayer(vlayer)

        vlayer = LayerUtils.layer_by_data_source("data_address", "ca_parcel_address_temp_cadastre_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("ca_parcel_address_temp_cadastre_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(
                os.path.realpath(__file__))[:-10]) + "/template\style/ca_parcel_address_temp_cadastre_view.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", " Address Temp Cadastre Parcel"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_parcel_group.addLayer(vlayer)

        vlayer = LayerUtils.layer_by_data_source("data_address", "ca_parcel_address_plan_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("ca_parcel_address_plan_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/ca_parcel_address_plan_view.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", " Address Plan Parcel"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_parcel_group.addLayer(vlayer)

        vlayer = LayerUtils.layer_by_data_source("data_address", "ca_parcel_address_is_new_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("ca_parcel_address_is_new_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/ca_parcel_address_is_new_view.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", " Is New Address Parcel"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_parcel_group.addLayer(vlayer)

        vlayer = LayerUtils.layer_by_data_source("data_address", "au_settlement_zone_point")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("au_settlement_zone_point", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[
                :-10]) + "/template\style/au_settlement_zone_point.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", " Settlement Center"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_group.addLayer(vlayer)

        ###building
        vlayer = LayerUtils.layer_by_data_source("data_address", "ca_building_address_bairzui_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("ca_building_address_bairzui_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[
                :-10]) + "/template\style/ca_building_address_bairzui_view.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", " Address BairZui Building"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_building_group.addLayer(vlayer)

        vlayer = LayerUtils.layer_by_data_source("data_address", "ca_building_address_cadastre_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("ca_building_address_cadastre_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[
                :-10]) + "/template\style/ca_building_address_cadastre_view.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", " Address Cadastre Building"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_building_group.addLayer(vlayer)

        vlayer = LayerUtils.layer_by_data_source("data_address", "ca_building_address_is_new_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("ca_building_address_is_new_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[
                :-10]) + "/template\style/ca_building_address_is_new_view.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", " Is New Address Building"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_building_group.addLayer(vlayer)

        vlayer = LayerUtils.layer_by_data_source("data_address", "ca_building_address_temp_cadastre_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("ca_building_address_temp_cadastre_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[
                :-10]) + "/template\style/ca_building_address_temp_cadastre_view.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", " Address Temp Cadastre Building"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_building_group.addLayer(vlayer)

    @pyqtSlot()
    def on_selected_road_load_button_clicked(self):

        self.str_road_twidget.setRowCount(0)
        parcelLayer = LayerUtils.layer_by_data_source("data_address", "st_road_line_view")
        select_feature = parcelLayer.selectedFeatures()

        id = None
        for feature in select_feature:
            attr = feature.attributes()
            id = attr[0]
            code = attr[1]
            name = attr[2]
            road_len = None

            road = self.session.query(StRoad).filter(StRoad.id == id).one()
            if not road.street_id:
                sql = "select sr.id, st_length(st_transform(sr.line_geom, base.find_utm_srid(st_centroid(sr.line_geom)))) as road_len from data_address.st_road sr where id = (" + str(id) + ");"

                result = self.session.execute(sql)

                for item_row in result:
                    id = item_row[0]
                    road_len = item_row[1]

                count = self.str_road_twidget.rowCount()
                self.str_road_twidget.insertRow(count)

                item = QTableWidgetItem(str(id))
                item.setData(Qt.UserRole, id)
                self.str_road_twidget.setItem(count, 0, item)

                item = QTableWidgetItem(str(road_len))
                item.setData(Qt.UserRole, road_len)
                self.str_road_twidget.setItem(count, 1, item)

        if self.str_road_twidget.rowCount() == 1:
            self.create_single_str_button.setDisabled(False)
        if self.str_road_twidget.rowCount() > 1:
            self.create_single_str_button.setDisabled(False)
            self.create_single_name_str_button.setDisabled(False)
            self.create_multi_str_button.setDisabled(False)

    @pyqtSlot()
    def on_selected_road_remove_button_clicked(self):

        if self.str_road_twidget.rowCount() == 1:
            self.create_single_str_button.setDisabled(False)
        if self.str_road_twidget.rowCount() > 1:
            self.create_single_str_button.setDisabled(False)
            self.create_single_name_str_button.setDisabled(False)
            self.create_multi_str_button.setDisabled(False)

    @pyqtSlot()
    def on_selected_road_remove_button_clicked(self):

        selected_row = self.str_road_twidget.currentRow()
        id = self.str_road_twidget.item(selected_row, 0).data(Qt.UserRole)

        self.str_road_twidget.removeRow(selected_row)

    @pyqtSlot(QTableWidgetItem)
    def on_str_road_twidget_itemClicked(self, item):

        selected_row = self.str_road_twidget.currentRow()
        id = self.str_road_twidget.item(selected_row, 0).data(Qt.UserRole)

        zoom_layer = LayerUtils.layer_by_data_source("data_address", "st_road_line_view")
        self.__select_feature(str(id), zoom_layer)

    @pyqtSlot()
    def on_create_single_str_button_clicked(self):

        if self.str_road_twidget.rowCount() == 0:
            PluginUtils.show_message(self, u'Анхааруулга', u'Гудамж үүсгэх зам сонгоогүй байна.')
            return
        message_box = QMessageBox()
        message_box.setText(u'Гудамж үүсгэхдээ итгэлтэй байна уу?')

        yes_button = message_box.addButton(u'Тийм', QMessageBox.ActionRole)
        message_box.addButton(u'Үгүй', QMessageBox.ActionRole)
        message_box.exec_()
        if message_box.clickedButton() == yes_button:
            ids = []
            for row in range(self.str_road_twidget.rowCount()):
                item_id = self.str_road_twidget.item(row, 0)
                id = item_id.data(Qt.UserRole)
                id = str(id)
                ids.append(id)

            ids = str(ids).strip('[]')
            count = self.session.query(StStreet).\
                filter(StStreet.street_status == 10).\
                filter(StStreet.au2 == self.au2).count()
            result = None
            if count == 0:
                sql = "select row_number() over() as street_code, sr.au2 || lpad((row_number() over(partition by sr.au2))::text, 5, '0') as street_name, " \
                       "st_union(line_geom) from data_address.st_road sr  where id in (" + str(ids) + ") group by sr.au2; "
                result = self.session.execute(sql)
            else:
                sql = "select row_number() over() as street_code, " + "'" + str(self.au2) + "'" + " || (select lpad((max((substring(name, 6, 5))::int) + row_number() over())::text, 5, '0') from data_address.st_street ss " \
                      "where ss.au2 = " + "'" + str(self.au2) + "'" + " and ss.street_status = 10) as street_name, st_union(line_geom) from data_address.st_road sr " \
                      "where id in (" + str(ids) + ") "\
                      "group by sr.au2; "

                result = self.session.execute(sql)

            if result:
                for item_row in result:
                    str_code = item_row[0]
                    str_name = item_row[1]

                    street = StStreet()
                    street.code = str_code
                    street.name = str_name
                    street.is_active = True
                    street.status = 1
                    street.street_status = 10
                    street.created_at = DatabaseUtils.current_date_time()
                    street.valid_from = DatabaseUtils.current_date_time()
                    street.updated_at = DatabaseUtils.current_date_time()
                    street.au1 = self.au1
                    street.au2 = self.au2

                    self.session.add(street)
                    self.session.flush()

                    str_id = street.id

                    street_au2 = StStreetAu2()
                    street_au2.street_id = str_id
                    street_au2.au2 = self.au2
                    street_au2.created_at = DatabaseUtils.current_date_time()
                    self.session.add(street_au2)

                    for row in range(self.str_road_twidget.rowCount()):
                        item_id = self.str_road_twidget.item(row, 0)
                        id = item_id.data(Qt.UserRole)

                        road = self.session.query(StRoad).filter(StRoad.id == id).one()
                        road.street_id = str_id

            self.session.commit()

    @pyqtSlot()
    def on_create_single_name_str_button_clicked(self):

        if self.str_road_twidget.rowCount() == 0:
            PluginUtils.show_message(self, u'Анхааруулга', u'Гудамж үүсгэх зам сонгоогүй байна.')
            return
        message_box = QMessageBox()
        message_box.setText(u'Гудамж үүсгэхдээ итгэлтэй байна уу?')

        yes_button = message_box.addButton(u'Тийм', QMessageBox.ActionRole)
        message_box.addButton(u'Үгүй', QMessageBox.ActionRole)
        message_box.exec_()
        if message_box.clickedButton() == yes_button:
            ids = []
            for row in range(self.str_road_twidget.rowCount()):
                item_id = self.str_road_twidget.item(row, 0)
                id = item_id.data(Qt.UserRole)
                ids.append(id)

            ids = str(ids).strip('[]')
            count = self.session.query(StStreet). \
                filter(StStreet.street_status == 10). \
                filter(StStreet.au2 == self.au2).count()
            result = None
            if count == 0:
                sql = "select row_number() over() as street_code, sr.au2 || '00001' as street_name, " \
                       "line_geom, sr.id from data_address.st_road sr  where id in (" + str(ids) + ") group by sr.au2, sr.line_geom, sr.id; "
                result = self.session.execute(sql)
            else:
                sql = "select row_number() over() as street_code, " \
                      "sr.au2 || (select lpad((max((substring(name, 6, 5))::int) + row_number() over())::text, 5, '0') from data_address.st_street ss " \
                      "where ss.au2 = " + "'" + str(self.au2) + "'" + " and ss.street_status = 10) as street_name, line_geom, sr.id from data_address.st_road sr " \
                      "where id in (" + str(ids) + ") "\
                      "group by sr.au2, sr.line_geom, sr.id; "

                result = self.session.execute(sql)

            if result:
                for item_row in result:
                    str_code = item_row[0]
                    str_name = item_row[1]
                    road_id = item_row[3]

                    street = StStreet()
                    street.code = str_code
                    street.name = str_name
                    street.is_active = True
                    street.status = 1
                    street.street_status = 10
                    street.created_at = DatabaseUtils.current_date_time()
                    street.valid_from = DatabaseUtils.current_date_time()
                    street.updated_at = DatabaseUtils.current_date_time()
                    street.au1 = self.au1
                    street.au2 = self.au2

                    self.session.add(street)
                    self.session.flush()

                    str_id = street.id

                    street_au2 = StStreetAu2()
                    street_au2.street_id = str_id
                    street_au2.au2 = self.au2
                    street_au2.created_at = DatabaseUtils.current_date_time()
                    self.session.add(street_au2)

                    road = self.session.query(StRoad).filter(StRoad.id == road_id).one()
                    road.street_id = str_id

                self.session.commit()

    @pyqtSlot()
    def on_create_multi_str_button_clicked(self):

        if self.str_road_twidget.rowCount() == 0:
            PluginUtils.show_message(self, u'Анхааруулга', u'Гудамж үүсгэх зам сонгоогүй байна.')
            return
        message_box = QMessageBox()
        message_box.setText(u'Гудамж үүсгэхдээ итгэлтэй байна уу?')

        yes_button = message_box.addButton(u'Тийм', QMessageBox.ActionRole)
        message_box.addButton(u'Үгүй', QMessageBox.ActionRole)
        message_box.exec_()
        if message_box.clickedButton() == yes_button:
            ids = []
            for row in range(self.str_road_twidget.rowCount()):
                item_id = self.str_road_twidget.item(row, 0)
                id = item_id.data(Qt.UserRole)
                ids.append(id)

            ids = str(ids).strip('[]')
            count = self.session.query(StStreet). \
                filter(StStreet.street_status == 10). \
                filter(StStreet.au2 == self.au2).count()
            result = None
            if count == 0:
                sql = "select row_number() over() as street_code, sr.au2 || lpad((row_number() over(partition by sr.au2))::text, 5, '0') as street_name, " \
                      "line_geom, sr.id from data_address.st_road sr  where id in (" + str(ids) + ") group by sr.au2, sr.line_geom, sr.id; "
                result = self.session.execute(sql)
            else:
                sql = "select row_number() over() as street_code, " \
                      "sr.au2 || lpad(((select (max((substring(name, 6, 5))::int))::text from data_address.st_street ss " \
                      "where ss.au2 = '01104' and ss.street_status = 10)::int + row_number() over())::text, 5, '0') as street_name, line_geom, sr.id from data_address.st_road sr " \
                                      "where id in (" + str(ids) + ") " \
                                                                   "group by sr.au2, sr.line_geom, sr.id; "

                result = self.session.execute(sql)

            if result:
                for item_row in result:
                    str_code = item_row[0]
                    str_name = item_row[1]
                    road_id = item_row[3]

                    street = StStreet()
                    street.code = str_code
                    street.name = str_name
                    street.is_active = True
                    street.status = 1
                    street.street_status = 10
                    street.created_at = DatabaseUtils.current_date_time()
                    street.valid_from = DatabaseUtils.current_date_time()
                    street.updated_at = DatabaseUtils.current_date_time()
                    street.au1 = self.au1
                    street.au2 = self.au2

                    self.session.add(street)
                    self.session.flush()

                    str_id = street.id

                    street_au2 = StStreetAu2()
                    street_au2.street_id = str_id
                    street_au2.au2 = self.au2
                    street_au2.created_at = DatabaseUtils.current_date_time()
                    self.session.add(street_au2)

                    road = self.session.query(StRoad).filter(StRoad.id == road_id).one()
                    road.street_id = str_id

                self.session.commit()

    @pyqtSlot()
    def on_delete_selected_str_button_clicked(self):

        print ''
