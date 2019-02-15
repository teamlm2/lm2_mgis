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
from sqlalchemy import func
from ..view.Ui_CamaNavigatorWidget import Ui_CamaNavigatorWidget
from ..utils.LayerUtils import LayerUtils
from ..model.AuCadastreBlock import *
from ..model.AuLevel1 import *
from ..model.AuLevel2 import *
from ..model.LdProjectPlan import *
from ..model.ClPlanDecisionLevel import *
from ..model.ClPlanStatusType import *
from ..model.ClPlanType import *
from ..model.LdProjectPlanStatus import *
from ..model.CaParcel import *
from ..controller.PlanCaseDialog import *
from ..utils.DatabaseUtils import *
from ..utils.PluginUtils import *
from ..utils.LayerUtils import *
from ..model.DatabaseHelper import *
from ..model.SetProcessTypeColor import *
from ..model.CmCamaLanduseType import *
from ..model.CmFactorsAuValue import *
from ..model.CmFactorsValue import *
from ..model.CmFactorGroup import *
from ..model.CmParcelTbl import *
from ..model.CmFactors import *

from ..controller.PlanDetailWidget import *
from ..controller.PlanLayerFilterDialog import *
# from ..LM2Plugin import *
from datetime import timedelta
from xlsxwriter.utility import xl_rowcol_to_cell, xl_col_to_name
import xlsxwriter
import time
import urllib
import urllib2

LANDUSE_1 = u'Хөдөө аж ахуйн газар'
LANDUSE_2 = u'Хот, тосгон, бусад суурины газар'
LANDUSE_3 = u'Зам, шугам сүлжээний газар'
LANDUSE_4 = u'Ойн сан бүхий газар'
LANDUSE_5 = u'Усны сан бүхий газар'
LANDUSE_6 = u'Улсын тусгай хэрэгцээний газар'

class CamaNavigatorWidget(QDockWidget, Ui_CamaNavigatorWidget, DatabaseHelper):

    def __init__(self,  plugin, parent=None):

        super(CamaNavigatorWidget,  self).__init__(parent)
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

        self.__setup_validators()
        self.au2 = DatabaseUtils.working_l2_code()
        self.__setup_combo_boxes()
        self.working_l1_cbox.currentIndexChanged.connect(self.__working_l1_changed)
        self.working_l2_cbox.currentIndexChanged.connect(self.__working_l2_changed)

        self.water_quality_list = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V'}
        self.is_yes_list = {1: u'Тйим', 0: u'Үгүй'}

        self.__setup_cbox()
        self.cadastre_rbutton.isCheckable()

    def __setup_validators(self):

        self.numbers_validator = QRegExpValidator(QRegExp("[1-9][0-9]+\\.[0-9]{3}"), None)
        self.int_validator = QRegExpValidator(QRegExp("[0-9][0-9]"), None)

        self.elevation_edit.setValidator(self.numbers_validator)
        self.slopy_edit.setValidator(self.numbers_validator)
        self.rain_replicate_edit.setValidator(self.numbers_validator)
        self.earthquake_edit.setValidator(self.numbers_validator)
        self.soil_quality_edit.setValidator(self.numbers_validator)
        self.air_quality_edit.setValidator(self.numbers_validator)

    def set_parcel_data(self, parcel_no, feature, layer_type):

        if feature:
            self.layer_type = layer_type
            self.parcel_id = parcel_no
            self.__geometry = QgsGeometry(feature.geometry())
            self.__feature = feature
            self.__update_ui()

    def __update_ui(self):

        self.__all_clear()
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
        # self.parcel_base_price_value = float(base_price_m2)*parcel.area_m2/1000000

    def __setup_cbox(self):

        self.permafrost_cbox.addItem('*', -1)
        self.water_quality_cbox.addItem('*', -1)

        for key in self.water_quality_list:
            self.water_quality_cbox.addItem(self.water_quality_list[key], key)

        for key in self.is_yes_list:
            self.permafrost_cbox.addItem(self.is_yes_list[key], key)

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
    def on_price_calc_button_clicked(self):

        p_price = float(self.parcel_all_base_price.text())
        self.parcel_calc_price_value = p_price

        if self.elevation_value_edit.text() and self.parcel_calc_price_value:
            value = float(self.elevation_value_edit.text())
            self.parcel_calc_price_value = self.parcel_calc_price_value * value

        if self.slopy_value_edit.text() and self.parcel_calc_price_value:
            value = float(self.slopy_value_edit.text())
            self.parcel_calc_price_value = self.parcel_calc_price_value * value

        if self.rain_replicate_value_edit.text() and self.parcel_calc_price_value:
            value = float(self.rain_replicate_value_edit.text())
            self.parcel_calc_price_value = self.parcel_calc_price_value * value

        if self.earthquake_value_edit.text() and self.parcel_calc_price_value:
            value = float(self.earthquake_value_edit.text())
            self.parcel_calc_price_value = self.parcel_calc_price_value * value

        if self.soil_quality_value_edit.text() and self.parcel_calc_price_value:
            value = float(self.soil_quality_value_edit.text())
            self.parcel_calc_price_value = self.parcel_calc_price_value * value

        if self.air_quality_value_edit.text() and self.parcel_calc_price_value:
            value = float(self.air_quality_value_edit.text())
            self.parcel_calc_price_value = self.parcel_calc_price_value * value

        if self.permafrost_value_edit.text() and self.parcel_calc_price_value:
            value = float(self.permafrost_value_edit.text())
            self.parcel_calc_price_value = self.parcel_calc_price_value * value

        if self.water_quality_value_edit.text() and self.parcel_calc_price_value:
            value = float(self.water_quality_value_edit.text())
            self.parcel_calc_price_value = self.parcel_calc_price_value * value

        #
        if self.shcool_value_edit.text() and self.parcel_calc_price_value:
            value = float(self.shcool_value_edit.text())
            self.parcel_calc_price_value = self.parcel_calc_price_value * value

        self.parcel_calc_base_price.setText(str(self.parcel_calc_price_value))

    @pyqtSlot(str)
    def on_elevation_edit_textChanged(self, text):

        factor_id = 1
        is_interval = True
        if text == "":
            self.elevation_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            return
        else:
            self.elevation_edit.setStyleSheet(self.styleSheet())

        if self.__get_factor_change_value(text, factor_id, is_interval):
            value = self.__get_factor_change_value(text, factor_id, is_interval)
            self.elevation_value_edit.setText(str(value))

    @pyqtSlot(str)
    def on_slopy_edit_textChanged(self, text):

        factor_id = 2
        is_interval = True
        if text == "":
            self.slopy_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            return
        else:
            self.slopy_edit.setStyleSheet(self.styleSheet())

        if self.__get_factor_change_value(text, factor_id, is_interval):
            value = self.__get_factor_change_value(text, factor_id, is_interval)
            self.slopy_value_edit.setText(str(value))

    @pyqtSlot(str)
    def on_earthquake_edit_textChanged(self, text):

        factor_id = 3
        is_interval = True
        if text == "":
            self.earthquake_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            return
        else:
            self.earthquake_edit.setStyleSheet(self.styleSheet())

        if self.__get_factor_change_value(text, factor_id, is_interval):
            value = self.__get_factor_change_value(text, factor_id, is_interval)
            self.earthquake_value_edit.setText(str(value))

    @pyqtSlot(str)
    def on_soil_quality_edit_textChanged(self, text):

        factor_id = 8
        is_interval = True
        if text == "":
            self.soil_quality_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            return
        else:
            self.soil_quality_edit.setStyleSheet(self.styleSheet())

        if self.__get_factor_change_value(text, factor_id, is_interval):
            value = self.__get_factor_change_value(text, factor_id, is_interval)
            self.soil_quality_value_edit.setText(str(value))

    @pyqtSlot(str)
    def on_air_quality_edit_textChanged(self, text):

        factor_id = 6
        is_interval = True
        if text == "":
            self.air_quality_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            return
        else:
            self.air_quality_edit.setStyleSheet(self.styleSheet())

        if self.__get_factor_change_value(text, factor_id, is_interval):
            value = self.__get_factor_change_value(text, factor_id, is_interval)
            self.air_quality_value_edit.setText(str(value))

    @pyqtSlot(str)
    def on_rain_replicate_edit_textChanged(self, text):

        factor_id = 4
        is_interval = False
        if text == "":
            self.rain_replicate_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            return
        else:
            self.rain_replicate_edit.setStyleSheet(self.styleSheet())

        if self.__get_factor_change_value(text, factor_id, is_interval):
            value = self.__get_factor_change_value(text, factor_id, is_interval)
            self.rain_replicate_value_edit.setText(str(value))

    @pyqtSlot(int)
    def on_permafrost_cbox_currentIndexChanged(self, index):

        factor_id = 5
        is_interval = False
        id = self.permafrost_cbox.itemData(index)
        if id == -1:
            self.permafrost_value_edit.clear()
        else:
            if self.__get_factor_change_value(id, factor_id, is_interval):
                value = self.__get_factor_change_value(id, factor_id, is_interval)
                self.permafrost_value_edit.setText(str(value))

    @pyqtSlot(int)
    def on_water_quality_cbox_currentIndexChanged(self, index):

        factor_id = 7
        is_interval = False
        id = self.water_quality_cbox.itemData(index)
        if id == -1:
            self.water_quality_value_edit.clear()
        else:
            if self.__get_factor_change_value(id, factor_id, is_interval):
                value = self.__get_factor_change_value(id, factor_id, is_interval)
                self.water_quality_value_edit.setText(str(value))

    def __get_factor_change_value(self, text, factor_id, is_interval):

        ch_value = float(text)

        values = self.session.query(CmFactorsAuValue). \
            filter(CmFactorsAuValue.au2 == self.au2). \
            filter(CmFactorsAuValue.factor_id == factor_id). \
            filter(CmFactorsAuValue.is_interval == is_interval).all()

        is_ok = False
        conf_value = 1

        for value in values:
            if not is_ok:
                if is_interval:
                    if value.first_value <= ch_value and value.last_value >= ch_value:
                        is_ok = True
                        factor_value = self.session.query(CmFactorsValue).filter(
                            CmFactorsValue.code == value.factor_value_id).one()
                        conf_value = factor_value.value
                else:
                    if value.first_value == ch_value:
                        is_ok = True
                        factor_value = self.session.query(CmFactorsValue).filter(
                            CmFactorsValue.code == value.factor_value_id).one()
                        conf_value = factor_value.value

        if is_ok:
            return conf_value
        else:
            return None

    @pyqtSlot()
    def on_layer_button_clicked(self):

        root = QgsProject.instance().layerTreeRoot()
        mygroup = root.findGroup(u"CAMA")
        vlayer = LayerUtils.layer_by_data_source("data_cama", "cm_parcel_tbl")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("cm_parcel_tbl", "parcel_id", "data_cama")
        # vlayer.loadNamedStyle(
        #     str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/pa_valuation_level.qml")

        vlayer.setLayerName(self.tr("Cama Base Parcel"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            mygroup.addLayer(vlayer)

    @pyqtSlot()
    def on_distinct_calc_button_clicked(self):

        parcel_id = self.parcel_id_edit.text()
        cama_landuse = 210401
        if self.__calculate_parcel_distance(parcel_id, cama_landuse):
            distance_value = self.__calculate_parcel_distance(parcel_id, cama_landuse)
            self.shcool_edit.setText(str(distance_value))

    def __calculate_parcel_distance(self, parcel_id, cama_landuse):

        sql = "select parcel.parcel_id, " \
              "min(ST_Distance(ST_Transform(parcel.geometry, base.find_utm_srid(St_Centroid(parcel.geometry))), ST_Transform(cm_parcel.geometry, base.find_utm_srid(St_Centroid(cm_parcel.geometry))))) " \
              "from data_soums_union.ca_parcel_tbl parcel, data_cama.cm_parcel_tbl cm_parcel " \
              "where parcel.parcel_id = :parcel_id and cm_parcel.cama_landuse = :cama_landuse group by parcel.parcel_id"

        result = self.session.execute(sql, {'parcel_id': parcel_id, 'cama_landuse': cama_landuse})

        distance_value = None
        for item_row in result:
            print type(item_row[1])
            distance_value = item_row[1]/1000

        return distance_value

    @pyqtSlot(str)
    def on_shcool_edit_textChanged(self, text):

        factor_id = 15
        is_interval = True
        if text == "":
            self.shcool_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            return
        else:
            self.shcool_edit.setStyleSheet(self.styleSheet())
        if self.__get_factor_change_value(text, factor_id, is_interval):
            value = self.__get_factor_change_value(text, factor_id, is_interval)
            self.shcool_value_edit.setText(str(value))

    def __all_clear(self):

        # parcel info
        self.parcel_id_edit.clear()
        self.parcel_area_edit.clear()
        self.parcel_area_ha_edit.clear()
        self.parcel_base_price.clear()
        self.parcel_all_base_price.clear()
        self.parcel_calc_base_price.clear()
        self.parcel_market_price.clear()
        self.parcel_all_market_price.clear()
        self.parcel_calc_market_price.clear()
        self.parcel_address_edit.clear()

        # factor
        self.elevation_edit.clear()
        self.elevation_value_edit.clear()
        self.slopy_edit.clear()
        self.slopy_value_edit.clear()
        self.rain_replicate_edit.clear()
        self.rain_replicate_value_edit.clear()
        self.permafrost_value_edit.clear()
        self.water_quality_value_edit.clear()
        self.earthquake_edit.clear()
        self.earthquake_value_edit.clear()
        self.soil_quality_edit.clear()
        self.soil_quality_value_edit.clear()
        self.air_quality_edit.clear()
        self.air_quality_value_edit.clear()

        # enginering
        self.heat_line_edit.clear()
        self.heat_line_value_edit.clear()
        self.water_line_edit.clear()
        self.water_line_value_edit.clear()
        self.disinfect_line_edit.clear()
        self.disinfect_line_value_edit.clear()
        self.power_line_edit.clear()
        self.power_line_value_edit.clear()
        self.route_edit.clear()
        self.route_value_edit.clear()
        self.parking_edit.clear()
        self.parking_value_edit.clear()

        # infrastructure
        self.shcool_edit.clear()
        self.shcool_value_edit.clear()
        self.kindergarten_edit.clear()
        self.kindergarten_value_edit.clear()
        self.medical_edit.clear()
        self.medical_value_edit.clear()
        self.admin_edit.clear()
        self.admin_value_edit.clear()
        self.house_service_edit.clear()
        self.house_service_value_edit.clear()

        # service
        self.shop_center_edit.clear()
        self.shop_center_value_edit.clear()
        self.service_center_edit.clear()
        self.service_center_value_edit.clear()