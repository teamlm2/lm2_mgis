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

        self.au2 = DatabaseUtils.working_l2_code()
        self.__setup_combo_boxes()
        self.working_l1_cbox.currentIndexChanged.connect(self.__working_l1_changed)
        self.working_l2_cbox.currentIndexChanged.connect(self.__working_l2_changed)

        self.water_quality_list = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V'}
        self.is_yes_list = {1: u'Тйим', 0: u'Үгүй'}

        self.__setup_cbox()
        self.cadastre_rbutton.isCheckable()

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

            self.__get_base_price(parcel.parcel_id)

    def __get_base_price(self, parcel_id):

        sql = "select vl.id, vl.name, lt.description, vl.level_no, vlp.base_price, vlp.base_price_m2 " \
                "from data_soums_union.ca_parcel_tbl pl " \
                "inner join data_estimate.pa_valuation_level vl on st_within(st_centroid(pl.geometry), vl.geometry) " \
                "inner join data_estimate.cl_valuation_level_type lt on vl.level_type = lt.parent_code " \
                "inner join data_estimate.set_level_type_landuse tl on lt.code = tl.level_type_id and tl.landuse_type = pl.landuse " \
                "left join data_estimate.pa_valuation_level_price vlp on vlp.level_id = vl.id " \
                "where parcel_id = :parcel_id "

        result = self.session.execute(sql, {'parcel_id': parcel_id})

        base_price_m2 = 0
        base_price_ha = 0
        for item_row in result:
            base_price_ha = item_row[4]
            base_price_m2 = item_row[5]

        self.parcel_base_price.setText(str(base_price_m2))

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

        self.__setup_change_combo_boxes()

    @pyqtSlot()
    def on_distinct_calc_button_clicked(self):

        print ''

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

    def __all_clear(self):

        # parcel info
        self.parcel_id_edit.clear()
        self.parcel_area_edit.clear()
        self.parcel_base_price.clear()
        self.parcel_market_price.clear()
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