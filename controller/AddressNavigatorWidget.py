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
from ..model.SetWorkruleStatus import *
from ..model.ClPlanType import *
from ..model.PlProjectStatusHistory import *
from ..model.CaParcel import *
from ..model.CmParcelBasePrice import *
from ..model.CmParcelMassPrice import *
from ..model.CmValuationLevelStatus import *
from ..model.CmValuationLevel import *
from ..controller.PlanCaseDialog import *
from ..controller.ManageParcelRecordsDialog import *
from ..utils.DatabaseUtils import *
from ..utils.PluginUtils import *
from ..utils.LayerUtils import *
from ..model.DatabaseHelper import *
from ..model.SetZoneColor import *
from ..model.CmCamaLanduseType import *
from ..model.CmFactorAuValue import *
from ..model.CmFactorValue import *
from ..model.CmFactorGroup import *
from ..model.CmParcelTbl import *
from ..model.CmFactor import *
from ..model.CmParcelFactorValue import *
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

        self.userSettings = None
        self.current_dialog = None
        self.is_au_level2 = False
        self.parcel_id = None
        self.__geometry = None
        self.__feature = None
        self.layer_type = None
        self.parcel_base_price_value = None
        self.parcel_calc_price_value = None

        self.au2 = DatabaseUtils.working_l2_code()
        self.__setup_combo_boxes()
        self.working_l1_cbox.currentIndexChanged.connect(self.__working_l1_changed)
        self.working_l2_cbox.currentIndexChanged.connect(self.__working_l2_changed)

        self.water_quality_list = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V'}
        self.is_yes_list = {1: u'Тйим', 0: u'Үгүй'}

        self.__setup_analyze_cbox()
        self.cadastre_rbutton.isCheckable()
        self.__setup_twidget()
        self.__setup_context_menu()
        self.print_pbar.setVisible(False)
        self.print_pbar.setMinimum(1)
        self.print_pbar.setValue(0)

    def __setup_context_menu(self):

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
        parcel_ids = []
        parcel_id = self.__selected_parcel_id()
        parcel_ids.append(parcel_id)
        self.__zoom_to_parcel_ids(parcel_ids)

    @pyqtSlot(QPoint)
    def on_cadastre_current_twidget_customContextMenuRequested(self, point):

        point = self.cadastre_current_twidget.viewport().mapToGlobal(point)
        self.context_menu.exec_(point)

    def __selected_parcel_id(self):

        # parcels = []
        current_row = self.cadastre_current_twidget.currentRow()
        item = self.cadastre_current_twidget.item(current_row, 0)
        parcel_no = item.data(Qt.UserRole)
        # parcels.append(parcel_no)
        # selected_items = self.cadastre_current_twidget.currentItem()

        # for item in selected_items:
        #     parcel_no = item.data(Qt.UserRole)
        #     parcels.append(parcel_no)

        # if len(selected_items) != 1:
        #     self.error_label.setText(self.tr("Only single selection allowed."))
        #     return None

        # selected_item = selected_items[0]
        # parcel_no = selected_item.data(Qt.UserRole)
        return parcel_no

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

    def __setup_twidget(self):

        # self.cadastre_current_twidget.setColumnCount(1)
        # self.cadastre_current_twidget.setDragEnabled(True)
        # self.cadastre_current_twidget.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        # self.cadastre_current_twidget.horizontalHeader().setVisible(False)
        # self.cadastre_current_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.cadastre_current_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.cadastre_current_twidget.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.cadastre_current_twidget.customContextMenuRequested.connect(self.on_custom_context_menu_requested)

        self.cadastre_current_twidget.setAlternatingRowColors(True)
        self.cadastre_current_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.cadastre_current_twidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.cadastre_current_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.cadastre_current_twidget.setContextMenuPolicy(Qt.CustomContextMenu)

        self.cadastre_current_twidget.horizontalHeader().resizeSection(0, 250)
        self.cadastre_current_twidget.horizontalHeader().resizeSection(1, 70)
        self.cadastre_current_twidget.horizontalHeader().resizeSection(2, 70)

    def set_parcel_data(self, parcel_no, feature, layer_type):

        if feature:
            self.layer_type = layer_type
            self.parcel_id = parcel_no
            self.__geometry = QgsGeometry(feature.geometry())
            self.__feature = feature
            self.__update_ui()

    def __update_ui(self):

        self.setWindowTitle(self.tr('Parcel ID: <{0}>. Select the decision.'.format(self.parcel_id)))

        count = self.session.query(CaParcel).filter(CaParcel.parcel_id == self.parcel_id).count()
        if count == 1:
            parcel = self.session.query(CaParcel).filter(CaParcel.parcel_id == self.parcel_id).one()

            self.parcel_id_edit.setText(self.parcel_id)
            self.parcel_area_edit.setText(str(parcel.area_m2))
            self.parcel_area_ha_edit.setText(str(parcel.area_m2/10000))

            self.__get_base_price(parcel)

    def __get_base_price(self, parcel):

        sql = "select vl.id, vl.name, lt.description, vl.level_no, vlp.base_price, vlp.base_price_m2 " \
                "from data_soums_union.ca_parcel_tbl pl " \
                "inner join data_estimate.pa_valuation_level vl on st_within(st_centroid(pl.geometry), vl.geometry) " \
                "inner join data_estimate.cl_valuation_level_type lt on vl.level_type = lt.parent_code " \
                "inner join data_estimate.set_level_type_landuse tl on lt.code = tl.level_type_id and tl.landuse_type = pl.landuse " \
                "left join data_estimate.pa_valuation_level_price vlp on vlp.level_id = vl.id " \
                "where parcel_id = :parcel_id "

        result = self.session.execute(sql, {'parcel_id': parcel.parcel_id})

        base_price_m2 = 0
        base_price_ha = 0
        for item_row in result:
            base_price_ha = item_row[4]
            base_price_m2 = item_row[5]

        self.parcel_base_price.setText(str(base_price_m2))

        self.parcel_all_base_price.setText(str(float(base_price_m2)*parcel.area_m2/1000000))
        # self.parcel_base_price_value = float(base_price_m2)*parcel.area_m2/100000)

    def __setup_combo_boxes(self):

        try:
            PluginUtils.populate_au_level1_cbox(self.working_l1_cbox, False)

            l1_code = self.working_l1_cbox.itemData(self.working_l1_cbox.currentIndex(), Qt.UserRole)
            PluginUtils.populate_au_level2_cbox(self.working_l2_cbox, l1_code, False)

            self.working_l1_cbox.setCurrentIndex(self.working_l1_cbox.findData(DatabaseUtils.working_l1_code()))
            self.working_l2_cbox.setCurrentIndex(self.working_l2_cbox.findData(DatabaseUtils.working_l2_code()))

        except SQLAlchemyError, e:
            PluginUtils.show_message(self, self.tr("Sql Error"), e.message)
            return

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

        except SQLAlchemyError, e:
            self.rollback_to_savepoint()
            PluginUtils.show_message(self,  self.tr("Sql Error"), e.message)
            return
        self.__zoom_to_soum(l2_code)
        self.__setup_analyze_cbox()

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

    @pyqtSlot(int)
    def on_base_price_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.market_price_chbox.setChecked(False)
            self.parcel_market_price.setEnabled(False)
            self.parcel_base_price.setEnabled(True)
        else:
            self.market_price_chbox.setChecked(True)
            self.parcel_market_price.setEnabled(True)
            self.parcel_base_price.setEnabled(False)

    @pyqtSlot(int)
    def on_market_price_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.base_price_chbox.setChecked(False)
            self.parcel_base_price.setEnabled(False)
            self.parcel_market_price.setEnabled(True)
        else:
            self.base_price_chbox.setChecked(True)
            self.parcel_base_price.setEnabled(True)
            self.parcel_market_price.setEnabled(False)

    @pyqtSlot()
    def on_layer_button_clicked(self):

        root = QgsProject.instance().layerTreeRoot()
        mygroup = root.findGroup(u"CAMA")
        if not mygroup:
            mygroup = root.insertGroup(1, u"CAMA")
        vlayer = LayerUtils.layer_by_data_source("data_cama", "cm_parcel_tbl")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("cm_parcel_tbl", "parcel_id", "data_cama")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/cm_parcel_tbl.qml")

        vlayer.setLayerName(self.tr("CAMA Parcel Polygon"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            mygroup.addLayer(vlayer)

        vlayer_line = LayerUtils.layer_by_data_source("data_cama",
                                                      "cm_parcel_tbl")
        if vlayer_line is None:
            vlayer_line = LayerUtils.load_line_layer_base_layer(
                "cm_parcel_tbl", "id",
                "data_cama")
            vlayer_line.setLayerName(self.tr("CAMA Parcel Line"))
        myalayer = root.findLayer(vlayer_line.id())
        if myalayer is None:
            mygroup.addLayer(vlayer_line)

        vlayer = LayerUtils.layer_by_data_source("data_cama", "cm_valuation_level")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("cm_valuation_level", "id", "data_cama")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/cm_valuation_level.qml")

        vlayer.setLayerName(self.tr("CAMA Valuation Level"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            mygroup.addLayer(vlayer)

    @pyqtSlot()
    def on_load_button_clicked(self):

        au2 = DatabaseUtils.working_l2_code()

        parcel_base_price = self.session.query(CmParcelMassPrice).\
            join(CaParcelTbl, CmParcelMassPrice.parcel_id == CaParcelTbl.parcel_id).\
            filter(CaParcelTbl.au2 == au2)
        count = parcel_base_price.count()

        self.parcel_count_edit.setText(str(count))

        min_price = self.session.query(func.min(CmParcelMassPrice.mass_price_m2)).\
            join(CaParcelTbl, CmParcelMassPrice.parcel_id == CaParcelTbl.parcel_id).\
            filter(CaParcelTbl.au2 == au2).one()
        max_price = self.session.query(func.max(CmParcelMassPrice.mass_price_m2)).\
            join(CaParcelTbl, CmParcelMassPrice.parcel_id == CaParcelTbl.parcel_id).\
            filter(CaParcelTbl.au2 == au2).one()
        min_value = 0
        max_value = 0
        if min_price[0]:
            if min_price[0] > 0:
                min_value = min_price[0]
            self.min_price_edit.setText(str(min_value))
        if max_price[0]:
            if max_price[0] > 0:
                max_value = max_price[0]
            self.max_price_edit.setText(str(max_value))

    @pyqtSlot()
    def on_calculate_button_clicked(self):

        min_price = 0
        max_price = 0
        next_interval = 0
        begin_interval = 0
        end_interval = 0
        level_no = 1

        if self.min_price_edit.text():
            min_price = float(self.min_price_edit.text())
        if self.max_price_edit.text():
            max_price = float(self.max_price_edit.text())


        self.price_interval_twidget.setRowCount(0)
        level_count = self.level_count_sbox.value()
        if max_price == 0 or level_count == 0:
            return

        interval_sub = (max_price - min_price)/level_count
        for row in range(level_count):
            if row == 0:
                next_interval = next_interval + min_price
            else:
                next_interval = next_interval + interval_sub

            begin_interval = next_interval
            end_interval = next_interval + interval_sub
            delegate_integer = QSpinBox()
            delegate_integer.setValue(level_no)
            delegate_double_min = QDoubleSpinBox()
            delegate_double_min.setMaximum(999999999999999)
            delegate_double_min.setValue(begin_interval)
            delegate_double_max = QDoubleSpinBox()
            delegate_double_max.setMaximum(999999999999999)
            delegate_double_max.setValue(end_interval)
            delegate_double_avg = QDoubleSpinBox()
            delegate_double_avg.setMaximum(999999999999999)
            delegate_double_avg.setValue((end_interval+begin_interval)/2)
            count = self.price_interval_twidget.rowCount()
            self.price_interval_twidget.insertRow(count)

            item = QTableWidgetItem()
            item.setCheckState(Qt.Unchecked)

            self.price_interval_twidget.setItem(count, 0, item)
            self.price_interval_twidget.setCellWidget(count, 1, delegate_integer)
            self.price_interval_twidget.setCellWidget(count, 2, delegate_double_min)
            self.price_interval_twidget.setCellWidget(count, 3, delegate_double_max)
            self.price_interval_twidget.setCellWidget(count, 4, delegate_double_avg)

            level_no = level_no + 1


    @pyqtSlot()
    def on_view_layer_button_clicked(self):

        status = self.valuation_level_status_cbox.itemData(self.valuation_level_status_cbox.currentIndex())
        sql = ""
        sql_zone = ""

        au2 = DatabaseUtils.working_l2_code()

        au2_valuation_level_count = self.session.query(CmValuationLevel).filter(CmValuationLevel.au2 == au2).count()

        if au2_valuation_level_count > 0:
            message_box = QMessageBox()
            message_box.setText(u'Энэ сум/дүүрэгт үнэлгээний бүсчлэлийг тооцоолсан байна. Устгаад дахин тооцоолох уу?')
            delete_button = message_box.addButton(self.tr("Yes"), QMessageBox.ActionRole)
            message_box.addButton(self.tr("No"), QMessageBox.ActionRole)
            message_box.exec_()

            if not message_box.clickedButton() == delete_button:
                return
            else:
                print ""
                self.session.query(CmValuationLevel).\
                    filter(CmValuationLevel.status == status). \
                    filter(CmValuationLevel.au2 == au2).delete()

        rows = self.price_interval_twidget.rowCount()
        for row in range(rows):
            zone_no = str(self.price_interval_twidget.cellWidget(row, 1).value())
            begin_value = str(self.price_interval_twidget.cellWidget(row, 2).value())
            end_value = str(self.price_interval_twidget.cellWidget(row, 3).value())
            avg_value = str(self.price_interval_twidget.cellWidget(row, 4).value())
            if (row + 1) == rows:
                end_value = " <= " + end_value
            else:
                end_value = " < " + end_value
            if sql:
                sql = sql + "UNION" + "\n"
            select = "select parcel.parcel_id as gid, " + zone_no + " as zone_no, " + avg_value + " as avg_base_price, parcel_price.mass_price_m2, parcel.geometry from data_cama.cm_parcel_mass_price parcel_price " \
                     "join data_soums_union.ca_parcel_tbl parcel on parcel_price.parcel_id = parcel.parcel_id " \
                     "where parcel.au2 = " + "'" + au2 + "'" + " and (parcel_price.mass_price_m2 >= " + begin_value + " and parcel_price.mass_price_m2  "+ end_value +")"

            if sql_zone:
                sql_zone = sql_zone + "UNION" + "\n"
            select_zone = "select " + zone_no + " as zone_no, " + avg_value + " as avg_base_price, st_buffer(st_buffer((st_dump(st_union(st_buffer(parcel.geometry, 0.001)))).geom, -0.001), 0.0002) as geometry from data_cama.cm_parcel_mass_price parcel_price " \
                  "join data_soums_union.ca_parcel_tbl parcel on parcel_price.parcel_id = parcel.parcel_id where parcel.au2 = " + "'" + au2 + "'" + " and (parcel_price.mass_price_m2 >= " + begin_value + " and parcel_price.mass_price_m2   "+ end_value +") "

            sql = sql + select
            sql_zone = sql_zone + select_zone



        aimag_name = self.working_l1_cbox.currentText()
        soum_name = self.working_l2_cbox.currentText()

        full_name = aimag_name + ', ' + soum_name

        sql_zone = "select zone_no, avg_base_price, st_union(geometry) from (" + sql_zone + ")" + " as xxx group by zone_no, avg_base_price"

        result = self.session.execute(sql_zone)
        for item_row in result:
            zone_no = item_row[0]
            avg_base_price = item_row[1]
            geometry = item_row[2]
            geom = 'ST_Multi(' +  "'" + geometry +  "'" + ')'
            values = str(zone_no) + ", " + geom + ", " + "true" + ", " + "'" + au2 + "'" + ", " + str(status) + ", " + str(avg_base_price) + ", " + "'" + full_name + "'" + ", " + "'" + full_name + "'"
            sql = "insert into data_cama.cm_valuation_level (level_no, geometry, in_active, au2, status, base_price, name, location) values ("+ values +")"

            self.session.execute(sql)

        self.session.commit()
        # sql = "(" + sql + ")"
        #
        # root = QgsProject.instance().layerTreeRoot()
        # mygroup = root.findGroup(u"CAMA")
        # layer_name = 'Parcel Zone Classify'
        # layer_list = []
        # layers = QgsMapLayerRegistry.instance().mapLayers()
        #
        # for id, layer in layers.iteritems():
        #     if layer.type() == QgsMapLayer.VectorLayer:
        #         if layer.name() == layer_name:
        #             layer_list.append(id)
        #
        # vlayer_parcel = LayerUtils.layer_by_data_source("", sql)
        # if vlayer_parcel:
        #     QgsMapLayerRegistry.instance().removeMapLayers(layer_list)
        # vlayer_parcel = LayerUtils.load_temp_table(sql, layer_name)
        #
        # myalayer = root.findLayer(vlayer_parcel.id())
        # if myalayer is None:
        #     mygroup.addLayer(vlayer_parcel)
        #
        # layer_name = 'Test Zone Classify'
        # for id, layer in layers.iteritems():
        #     if layer.type() == QgsMapLayer.VectorLayer:
        #         if layer.name() == layer_name:
        #             layer_list.append(id)
        #
        # sql_zone = "select row_number() over() as gid, * from ( " + sql_zone + " )xxx"
        # sql_zone = "(" + sql_zone + ")"
        #
        # vlayer_parcel = LayerUtils.layer_by_data_source("", sql_zone)
        # if vlayer_parcel:
        #     QgsMapLayerRegistry.instance().removeMapLayers(layer_list)
        # vlayer_parcel = LayerUtils.load_temp_table(sql_zone, layer_name)
        #
        # myalayer = root.findLayer(vlayer_parcel.id())
        # if myalayer is None:
        #     mygroup.addLayer(vlayer_parcel)

    @pyqtSlot()
    def on_valuation_button_clicked(self):

        parcel_id = self.parcel_id_edit.text()
        self.current_dialog = ManageParcelRecordsDialog(self.plugin, parcel_id, self.plugin.iface.mainWindow())

        self.current_dialog.show()

    def __setup_analyze_cbox(self):

        self.land_use_type_cbox.clear()

        l2_code = DatabaseUtils.working_l2_code()

        if not l2_code:
            return
        else:
            try:
                PluginUtils.populate_au_level3_cbox(self.bag_cbox, l2_code)
            except SQLAlchemyError, e:
                PluginUtils.show_message(self, self.tr("Sql Error"), e.message)

        cl_landusetype = self.session.query(ClLanduseType).order_by(ClLanduseType.code.asc()).all()
        self.land_use_type_cbox.addItem("*", -1)
        if cl_landusetype is not None:
            for landuse in cl_landusetype:
                if len(str(landuse.code)) == 4:
                    self.land_use_type_cbox.addItem(str(landuse.code) + ':' + landuse.description, landuse.code)

        valuation_status = self.session.query(CmValuationLevelStatus).order_by(CmValuationLevelStatus.code).all()
        if valuation_status is not None:
            for value in valuation_status:
                if len(str(landuse.code)) == 4:
                    self.valuation_level_status_cbox.addItem(str(value.code) + ':' + value.description, value.code)

    @pyqtSlot()
    def on_parcel_find_button_clicked(self):

        self.__search_parcels()

    def __search_parcels(self):

        factor_elevation = self.session.query(CmFactor).filter(CmFactor.code == SURFACE_ELEVATION).one()
        factor_slope = self.session.query(CmFactor).filter(CmFactor.code == SURFACE_SLOPE).one()

        parcels = self.session.query(CaParcel)
        all_count = parcels.count()
        # return
        filter_is_set = False
        if self.parcel_num_edit.text():
            # if len(self.parcel_num_edit.text()) < 5:
            #     self.error_label.setText(self.tr("parcel find search character should be at least 4"))
            #     return
            filter_is_set = True
            parcel_no = "%" + self.parcel_num_edit.text() + "%"
            parcels = parcels.filter(CaParcel.parcel_id.ilike(parcel_no))

        if not self.land_use_type_cbox.itemData(self.land_use_type_cbox.currentIndex()) == -1:
            filter_is_set = True
            value = self.land_use_type_cbox.itemData(self.land_use_type_cbox.currentIndex())
            parcels = parcels.filter(CaParcel.landuse == value)

        if not self.bag_cbox.itemData(self.bag_cbox.currentIndex()) == -1:
            filter_is_set = True
            value = self.bag_cbox.itemData(self.bag_cbox.currentIndex())
            parcels = parcels.filter(func.ST_Centroid(CaParcel.geometry).ST_Within((AuLevel3.geometry))). \
                filter(AuLevel3.code == value)

        if self.parcel_streetname_edit.text():
            filter_is_set = True
            value = "%" + self.parcel_streetname_edit.text() + "%"
            parcels = parcels.filter(CaParcel.address_streetname.ilike(value))

        if self.parcel_khashaa_edit.text():
            filter_is_set = True
            value = "%" + self.parcel_khashaa_edit.text() + "%"
            parcels = parcels.filter(CaParcel.address_khashaa.ilike(value))

        if self.is_no_calculate_chbox.isChecked():
            parcels = parcels.outerjoin(CmParcelFactorValue, CaParcel.parcel_id == CmParcelFactorValue.parcel_id). \
                filter(CmParcelFactorValue.factor_id == None). \
                filter(CmParcelFactorValue.factor_id == None)
        count = 0
        self.cadastre_current_twidget.setRowCount(0)

        if parcels.distinct(CaParcel.parcel_id).count() == 0:
            self.error_label.setText(self.tr("No parcels found for this search filter."))
            return

        elif filter_is_set is False:
            self.error_label.setText(self.tr("Please specify a search filter."))
            return

        for parcel in parcels.all():
            self.cadastre_current_twidget.insertRow(count)
            address_khashaa = ''
            address_streetname = ''
            # coord_x = func.ST_X(func.ST_Centroid(parcel.geometry))
            # coord_y = func.ST_Y(func.ST_Centroid(parcel.geometry))
            c_p = self.session.query(func.ST_X(func.ST_Centroid(CaParcel.geometry)), func.ST_Y(func.ST_Centroid(CaParcel.geometry))).filter(CaParcel.parcel_id == parcel.parcel_id).one()

            if parcel.address_khashaa:
                address_khashaa = parcel.address_khashaa
            if parcel.address_streetname:
                address_streetname = parcel.address_streetname
            item = QTableWidgetItem(parcel.parcel_id + " (" + address_khashaa + ", " + address_streetname + ")")
            item.setCheckState(Qt.Unchecked)
            item.setIcon(QIcon(QPixmap(":/plugins/lm2/parcel.png")))
            item.setData(Qt.UserRole, parcel.parcel_id)
            item.setData(Qt.UserRole + 1, parcel.area_m2)
            item.setData(Qt.UserRole + 2, c_p)
            self.cadastre_current_twidget.setItem(count, 0, item)

            factor_elevation_count = self.session.query(CmParcelFactorValue).\
                filter(CmParcelFactorValue.parcel_id == parcel.parcel_id).\
                filter(CmParcelFactorValue.factor_id == factor_elevation.id). \
                filter(CmParcelFactorValue.in_active == True).count()

            factor_slope_count = self.session.query(CmParcelFactorValue). \
                filter(CmParcelFactorValue.parcel_id == parcel.parcel_id). \
                filter(CmParcelFactorValue.factor_id == factor_slope.id). \
                filter(CmParcelFactorValue.in_active == True).count()

            if factor_elevation_count == 1:
                factor_elevation_value = self.session.query(CmParcelFactorValue). \
                    filter(CmParcelFactorValue.parcel_id == parcel.parcel_id). \
                    filter(CmParcelFactorValue.factor_id == factor_elevation.id). \
                    filter(CmParcelFactorValue.in_active == True).one()
                item = QTableWidgetItem(str(factor_elevation_value.factor_value))
                item.setData(Qt.UserRole, factor_elevation_value.id)
                item.setData(Qt.UserRole + 1, factor_elevation.id)
                item.setData(Qt.UserRole + 2, factor_elevation_value.factor_value)
                self.cadastre_current_twidget.setItem(count, 1, item)

            if factor_slope_count == 1:
                factor_slope_value = self.session.query(CmParcelFactorValue). \
                    filter(CmParcelFactorValue.parcel_id == parcel.parcel_id). \
                    filter(CmParcelFactorValue.factor_id == factor_slope.id). \
                    filter(CmParcelFactorValue.in_active == True).one()
                item = QTableWidgetItem(str(factor_slope_value.factor_value))
                item.setData(Qt.UserRole, factor_slope.id)
                item.setData(Qt.UserRole + 1, factor_slope_value.id)
                item.setData(Qt.UserRole + 2, factor_slope_value.factor_value)
                self.cadastre_current_twidget.setItem(count, 2, item)

            count += 1
            self.parcel_results_label.setText(self.tr("Results: ") + str(all_count) + '/' + str(count))
        self.error_label.setText("")

    @pyqtSlot()
    def on_slope_calculate_button_clicked(self):

        row_count = self.cadastre_current_twidget.rowCount()

        for row in range(row_count):
            item = self.cadastre_current_twidget.item(row, 0)
            parcel_id = item.data(Qt.UserRole)
            if item.checkState() == Qt.Checked:
                sql = "select val, row_number() over(partition by xxx.parcel_id, 2, True) as rank from ( " \
                        "select parcel.au2, parcel.parcel_id, (ST_DumpAsPolygons(rast)).geom::geometry, (ST_DumpAsPolygons(rast)).val from ( " \
                        "select au2, parcel_id, geometry FROM data_soums_union.ca_parcel_tbl parcel " \
                        "where parcel.parcel_id = " + "'" + parcel_id + "'" + " " \
                        ")parcel, data_raster.mongolia_dem rast " \
                        "where st_intersects(parcel.geometry, rast) " \
                        ")xxx, (select au2, parcel_id, (geometry) as geometry FROM data_soums_union.ca_parcel_tbl parcel " \
                        "where parcel.parcel_id = " + "'" + parcel_id + "'" + ") parcel " \
                        "where parcel.parcel_id = xxx.parcel_id and st_intersects(xxx.geom, st_makevalid(parcel.geometry)) "

                result = self.session.execute(sql)
                elevation_value = None
                for item_row in result:
                    value = item_row[0]
                    elevation_value = int(value)

                factor_elevation = self.session.query(CmFactor).filter(CmFactor.code == SURFACE_ELEVATION).one()
                if elevation_value:
                    item = self.cadastre_current_twidget.item(row, 1)
                    if item:
                        item.setText(str(elevation_value))
                        item.setData(Qt.UserRole, factor_elevation.id)
                        item.setData(Qt.UserRole + 2, elevation_value)
                    else:
                        item = QTableWidgetItem(str(elevation_value))
                        item.setData(Qt.UserRole, factor_elevation.id)
                        item.setData(Qt.UserRole + 2, elevation_value)
                        self.cadastre_current_twidget.setItem(row, 1, item)
                # slope
                sql = "select val, row_number() over(partition by xxx.parcel_id, 2, True) as rank from ( " \
                      "select parcel.au2, parcel.parcel_id, (ST_DumpAsPolygons(rast)).geom::geometry, (ST_DumpAsPolygons(rast)).val from ( " \
                      "select au2, parcel_id, geometry FROM data_soums_union.ca_parcel_tbl parcel " \
                      "where parcel.parcel_id = " + "'" + parcel_id + "'" + " " \
                      ")parcel, data_raster.mongolia_slope rast " \
                      "where st_intersects(parcel.geometry, rast) " \
                      ")xxx, (select au2, parcel_id, (geometry) as geometry FROM data_soums_union.ca_parcel_tbl parcel " \
                      "where parcel.parcel_id = " + "'" + parcel_id + "'" + ") parcel " \
                      "where parcel.parcel_id = xxx.parcel_id and st_intersects(xxx.geom, st_makevalid(parcel.geometry)) "

                result = self.session.execute(sql)
                slope_value = None
                for item_row in result:
                    value = item_row[0]
                    slope_value = round(value, 2)

                factor_slope = self.session.query(CmFactor).filter(CmFactor.code == SURFACE_SLOPE).one()
                if slope_value:
                    item = self.cadastre_current_twidget.item(row, 2)
                    if item:
                        item.setText(str(slope_value))
                        item.setData(Qt.UserRole, factor_slope.id)
                        item.setData(Qt.UserRole + 2, slope_value)
                    else:
                        item = QTableWidgetItem(str(slope_value))
                        item.setData(Qt.UserRole, factor_slope.id)
                        item.setData(Qt.UserRole + 2, slope_value)
                        self.cadastre_current_twidget.setItem(row, 2, item)

    @pyqtSlot()
    def on_slope_apply_button_clicked(self):

        row_count = self.cadastre_current_twidget.rowCount()
        date_time_string = QDateTime.currentDateTime().toString(Constants.DATABASE_DATETIME_FORMAT)
        date_now = datetime.strptime(date_time_string, Constants.PYTHON_DATETIME_FORMAT)
        for row in range(row_count):
            item = self.cadastre_current_twidget.item(row, 0)
            parcel_id = item.data(Qt.UserRole)
            if item.checkState() == Qt.Checked:
                factor_slope = self.session.query(CmFactor).filter(CmFactor.code == SURFACE_SLOPE).one()
                factor_elevation = self.session.query(CmFactor).filter(CmFactor.code == SURFACE_ELEVATION).one()

                elevation_value_count = self.session.query(CmParcelFactorValue). \
                    filter(CmParcelFactorValue.parcel_id == parcel_id). \
                    filter(CmParcelFactorValue.factor_id == factor_elevation.id). \
                    filter(CmParcelFactorValue.in_active == True).count()
                item = self.cadastre_current_twidget.item(row, 1)
                if item:
                    value = item.data(Qt.UserRole + 2)
                    if elevation_value_count == 1:
                        parcel_factor_value = self.session.query(CmParcelFactorValue). \
                            filter(CmParcelFactorValue.parcel_id == parcel_id). \
                            filter(CmParcelFactorValue.factor_id == factor_elevation.id). \
                            filter(CmParcelFactorValue.in_active == True).one()

                        parcel_factor_value.factor_value = value
                    elif elevation_value_count == 0:
                        parcel_factor_value = CmParcelFactorValue()

                        parcel_factor_value.parcel_id = parcel_id
                        parcel_factor_value.factor_id = factor_elevation.id
                        parcel_factor_value.factor_value = value
                        parcel_factor_value.in_active = True
                        parcel_factor_value.created_at = date_now
                        self.session.add(parcel_factor_value)

                slope_value_count = self.session.query(CmParcelFactorValue). \
                    filter(CmParcelFactorValue.parcel_id == parcel_id). \
                    filter(CmParcelFactorValue.factor_id == factor_slope.id). \
                    filter(CmParcelFactorValue.in_active == True).count()
                item = self.cadastre_current_twidget.item(row, 2)
                if item:
                    value = item.data(Qt.UserRole + 2)
                    if slope_value_count == 1:
                        parcel_factor_value = self.session.query(CmParcelFactorValue). \
                            filter(CmParcelFactorValue.parcel_id == parcel_id). \
                            filter(CmParcelFactorValue.factor_id == factor_slope.id). \
                            filter(CmParcelFactorValue.in_active == True).one()

                        parcel_factor_value.factor_value = value
                    elif slope_value_count == 0:
                        parcel_factor_value = CmParcelFactorValue()

                        parcel_factor_value.parcel_id = parcel_id
                        parcel_factor_value.factor_id = factor_slope.id
                        parcel_factor_value.factor_value = value
                        parcel_factor_value.in_active = True
                        parcel_factor_value.created_at = date_now
                        self.session.add(parcel_factor_value)
        self.session.commit()

        PluginUtils.show_message(self, u'Мэдээлэл', u'Амжилттай хадгаллаа.')

    @pyqtSlot()
    def on_parcel_clear_button_clicked(self):

        self.__remove_parcel_items()
        self.__clear_parcel()

    def __remove_parcel_items(self):

        self.cadastre_current_twidget.setRowCount(0)
        self.parcel_results_label.setText("")

    def __clear_parcel(self):

        self.parcel_num_edit.clear()
        self.land_use_type_cbox.setCurrentIndex(self.land_use_type_cbox.findData(-1))
        self.bag_cbox.setCurrentIndex(self.bag_cbox.findData(-1))
        self.parcel_streetname_edit.clear()
        self.parcel_khashaa_edit.clear()
        self.is_no_calculate_chbox.setCheckState(Qt.Unchecked)

    @pyqtSlot()
    def on_print_button_clicked(self):

        self.print_pbar.setVisible(True)

        default_path = r'D:/TM_LM2/cama/reports'
        if not os.path.exists(default_path):
            os.makedirs(default_path)

        workbook = xlsxwriter.Workbook(default_path + "/" + "cama_calc_payment.xlsx")
        worksheet = workbook.add_worksheet()

        format = workbook.add_format()
        format.set_text_wrap()
        format.set_align('center')
        format.set_align('vcenter')
        format.set_font_name('Times New Roman')
        format.set_font_size(8)

        format_header = workbook.add_format()
        format_header.set_text_wrap()
        format_header.set_align('vcenter')
        format_header.set_font_name('Times New Roman')
        format_header.set_font_size(10)
        format_header.set_bold()

        head_text = self.working_l1_cbox.currentText() + u' аймаг/хот-н ' + self.working_l2_cbox.currentText() + u' сум/дүүрэг-н нэгж талбарын үнэлэгдсэн үнийн тайлан'
        worksheet.write(1, 0, u'Нэгж талбарын дугаар', format)
        worksheet.merge_range('A2:M2', head_text, format_header)

        r_row = 3

        worksheet.write(r_row, 0, u'Нэгж талбарын дугаар', format)
        worksheet.write(r_row, 1, u'Талбайн хэмжээ', format)
        worksheet.write(r_row, 2, u'Өндөршил', format)
        worksheet.write(r_row, 3, u'Налуужилт', format)
        worksheet.write(r_row, 4, u'Сургууль', format)
        worksheet.write(r_row, 5, u'Цэцэрлэг', format)
        worksheet.write(r_row, 6, u'Эмнэлэг', format)
        worksheet.write(r_row, 7, u'Хөрсний бохирдол', format)
        worksheet.write(r_row, 8, u'Үер усны эрсдэл', format)
        worksheet.write(r_row, 9, u'Хотын төв хүртэлх зай', format)
        worksheet.write(r_row, 10, u'Тооцоологдсон үнэ/₮/', format)

        rows = self.cadastre_current_twidget.rowCount()

        factors = self.session.query(CmFactor).\
            filter(or_(CmFactor.id == 2, CmFactor.id == 3, CmFactor.id == 16, CmFactor.id == 17, CmFactor.id == 18, CmFactor.id == 37, CmFactor.id == 5, CmFactor.id == 9)).all()
        print len(range(rows))
        pbar_count = len(range(rows))
        self.print_pbar.setValue(0)
        self.print_pbar.setMaximum(pbar_count)
        for row in range(rows):

            dis_shl = 0
            dis_hos = 0
            dis_kid = 0
            valuation = 0
            dis_center = 1000
            slope = 0
            risk_flood = 2
            risk_soil = 3

            item = self.cadastre_current_twidget.item(row, 0)
            parcel_id = item.data(Qt.UserRole)
            area = (item.data(Qt.UserRole + 1))
            coords = item.data(Qt.UserRole + 2)
            coord_x = (coords[0])
            coord_y = (coords[1])
            for factor in factors:
                count = self.session.query(CmParcelFactorValue).\
                    filter(CmParcelFactorValue.parcel_id == parcel_id). \
                    filter(CmParcelFactorValue.factor_id == factor.id). \
                    filter(CmParcelFactorValue.in_active == True).count()

                if count == 1:
                    value = self.session.query(CmParcelFactorValue). \
                        filter(CmParcelFactorValue.parcel_id == parcel_id). \
                        filter(CmParcelFactorValue.factor_id == factor.id). \
                        filter(CmParcelFactorValue.in_active == True).one()

                    if factor.id == 2:
                        valuation = int(value.factor_value)
                    if factor.id == 3:
                        slope = int(value.factor_value)
                    if factor.id == 5:
                        risk_flood = int(value.factor_value)
                    if factor.id == 9:
                        risk_soil = int(value.factor_value)
                    if factor.id == 16:
                        dis_shl = int(value.factor_value)
                    if factor.id == 17:
                        dis_kid = int(value.factor_value)
                    if factor.id == 18:
                        dis_hos = int(value.factor_value)
                    if factor.id == 37:
                        dis_center = int(value.factor_value)

                print factor.id

            params = 'area=' + str(area) + '&coord_x=' + str(coord_x) + '&coord_y=' + str(coord_y) + '&surface_elevation=' + str(valuation) + \
                     '&surface_slope=' + str(slope) + '&blood_frequence=' + str(risk_flood) + '&soil_pollution_level=' + str(risk_soil) + '&distanes_to_school=' + str(dis_shl) + \
                     '&distanes_to_kindergarten=' + str(dis_kid) + '&distanes_to_hospital=' + str(dis_hos) + '&distance_to_center=' + str(dis_center)

            url = 'http://192.168.15.202:5000/cama/api/pkl/getprices?' + params
            print url
            respons = urllib.request.urlopen(url)
            # print respons
            data = json.loads(respons.read().decode(respons.info().get_param('charset') or 'utf-8'))
            calc_value = data['value']
            # print parcel_id + '-' + unicode(data['value'])

            r_row = r_row + 1
            worksheet.write(r_row, 0, parcel_id, format)
            worksheet.write(r_row, 1, area, format)
            worksheet.write(r_row, 2, valuation, format)
            worksheet.write(r_row, 3, slope, format)
            worksheet.write(r_row, 4, dis_shl, format)
            worksheet.write(r_row, 5, dis_kid, format)
            worksheet.write(r_row, 6, dis_hos, format)
            worksheet.write(r_row, 7, risk_soil, format)
            worksheet.write(r_row, 8, risk_flood, format)
            worksheet.write(r_row, 9, dis_center, format)
            worksheet.write(r_row, 10, calc_value, format)

            value_p = self.print_pbar.value() + 1
            self.print_pbar.setValue(value_p)

        try:
            workbook.close()
            QDesktopServices.openUrl(
                QUrl.fromLocalFile(default_path + "/" + "cama_calc_payment.xlsx"))
        except IOError, e:
            PluginUtils.show_error(self, self.tr("Out error"),
                                   self.tr("This file is already opened. Please close re-run"))