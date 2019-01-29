# coding=utf8

__author__ = 'B.Ankhbold'

from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtXml import *
from PyQt4.QtCore import QDate
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import func, or_, and_, desc
from sqlalchemy.sql.expression import cast
from sqlalchemy import func
from ..view.Ui_PlanDetailWidget import Ui_PlanDetailWidget
from ..utils.LayerUtils import LayerUtils
from ..model.AuCadastreBlock import *
from ..model.AuLevel1 import *
from ..model.AuLevel2 import *
from ..model.LdProjectPlan import *
from ..model.ClPlanDecisionLevel import *
from ..model.ClPlanStatusType import *
from ..model.ClPlanType import *
from ..model.LdProjectPlanStatus import *
from ..model.LdProjectMainZone import *
# from ..model.LdProjectSubZone import *
from ..model.LdProjectParcel import *
from ..model.LdProcessPlan import *
from ..utils.DatabaseUtils import *
from ..utils.PluginUtils import *
from ..model.DatabaseHelper import *
from ..controller.PlanNavigatorWidget import *
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

class PlanDetailWidget(QDockWidget, Ui_PlanDetailWidget, DatabaseHelper):

    def __init__(self, plugin, plan, navigator, attribute_update=False, parent=None):

        super(PlanDetailWidget,  self).__init__(parent)
        DatabaseHelper.__init__(self)

        self.setupUi(self)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.plugin = plugin
        self.navigator = navigator
        self.attribute_update = attribute_update
        self.plan = plan
        self.session = SessionHandler().session_instance()

        self.userSettings = None
        self.planNavigatorWidget = None
        self.load_pbar.setVisible(False)
        self.__setup_data()
        self.__setup_cbox()
        self.__setup_main_tree_widget()
        self.__setup_context_menu()

    def __setup_cbox(self):

        self.process_type_cbox.clear()
        values = self.session.query(LdProjectMainZone.plan_draft_id, LdProcessPlan.code, LdProcessPlan.description).\
            join(LdProcessPlan, LdProjectMainZone.badedturl == LdProcessPlan.code).\
            filter(LdProjectMainZone.plan_draft_id == self.plan.plan_draft_id).\
            group_by(LdProjectMainZone.plan_draft_id, LdProcessPlan.code, LdProcessPlan.description). \
            order_by(LdProcessPlan.code)
        self.process_type_cbox.addItem("*", -1)
        for value in values:
            self.process_type_cbox.addItem(str(value.code)+':'+value.description, value.code)

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
        self.item_polygon_main.setData(0, Qt.UserRole, GEOM_POlYGON)

        self.main_tree_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.main_tree_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.main_tree_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.main_tree_widget.addTopLevelItem(self.item_point_main)
        self.main_tree_widget.addTopLevelItem(self.item_line_main)
        self.main_tree_widget.addTopLevelItem(self.item_polygon_main)
        self.main_tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)

    def __setup_context_menu(self):

        self.menu = QMenu()
        self.zoom_to_selected = QAction(QIcon("zoom.png"), "Zoom to item", self)
        self.menu.addAction(self.zoom_to_selected)
        self.zoom_to_selected.triggered.connect(self.zoom_to_selected_clicked)

    def __setup_data(self):

        self.plan_num_edit.setText(self.plan.plan_draft_no)
        self.date_edit.setText(str(self.plan.begin_date))
        self.type_edit.setText(self.plan.plan_type_ref.description)
        self.decision_level_edit.setText(self.plan.plan_decision_level_ref.description)
        self.status_edit.setText(self.plan.last_status_type_ref.description)

    @pyqtSlot()
    def on_home_button_clicked(self):

        self.navigator.show()
        self.hide()

    @pyqtSlot(QPoint)
    def on_main_tree_widget_customContextMenuRequested(self, point):

        point = self.main_tree_widget.viewport().mapToGlobal(point)
        self.menu.exec_(point)

    def __load_main_zone(self, au2):

        self.load_pbar.setValue(1)

        values = self.session.query(LdProjectMainZone). \
            filter(LdProjectMainZone.plan_draft_id == self.plan.plan_draft_id). \
            filter(LdProjectMainZone.au2 == au2)

        self.load_pbar.setMaximum(values.count())

        main_zone_points = self.session.query(LdProjectMainZone). \
            filter(LdProjectMainZone.plan_draft_id == self.plan.plan_draft_id). \
            filter(LdProjectMainZone.polygon_geom == None). \
            filter(LdProjectMainZone.line_geom == None). \
            filter(LdProjectMainZone.au2 == au2).order_by(LdProjectMainZone.badedturl)

        main_zone_lines = self.session.query(LdProjectMainZone). \
            filter(LdProjectMainZone.plan_draft_id == self.plan.plan_draft_id). \
            filter(LdProjectMainZone.polygon_geom == None). \
            filter(LdProjectMainZone.point_geom == None). \
            filter(LdProjectMainZone.au2 == au2).order_by(LdProjectMainZone.badedturl)

        main_zone_polygons = self.session.query(LdProjectMainZone). \
            filter(LdProjectMainZone.plan_draft_id == self.plan.plan_draft_id). \
            filter(LdProjectMainZone.line_geom == None). \
            filter(LdProjectMainZone.point_geom == None). \
            filter(LdProjectMainZone.au2 == au2).order_by(LdProjectMainZone.badedturl)

        if self.process_type_cbox.currentIndex() != -1:
            if not self.process_type_cbox.itemData(self.process_type_cbox.currentIndex()) == -1:
                process_type = self.process_type_cbox.itemData(self.process_type_cbox.currentIndex())

                main_zone_points = main_zone_points.filter(LdProjectMainZone.badedturl == process_type)
                main_zone_lines = main_zone_lines.filter(LdProjectMainZone.badedturl == process_type)
                main_zone_polygons = main_zone_polygons.filter(LdProjectMainZone.badedturl == process_type)

        if self.process_edit.text():
            process_text = "%" + self.process_edit.text() + "%"
            main_zone_points = main_zone_points.\
                join(LdProcessPlan, LdProjectMainZone.badedturl == LdProcessPlan.code).\
                filter(LdProcessPlan.description.ilike(process_text))

            main_zone_lines = main_zone_lines. \
                join(LdProcessPlan, LdProjectMainZone.badedturl == LdProcessPlan.code). \
                filter(LdProcessPlan.description.ilike(process_text))

            main_zone_polygons = main_zone_polygons. \
                join(LdProcessPlan, LdProjectMainZone.badedturl == LdProcessPlan.code). \
                filter(LdProcessPlan.description.ilike(process_text))


        for main_zone in main_zone_points:
            name = ''
            if main_zone.gazner:
                name = '(' + main_zone.gazner + ')'
            desc = ''
            if main_zone.process_ref:
                if main_zone.process_ref.description:
                    desc = main_zone.process_ref.description
                    item = QTreeWidgetItem()
                    item.setText(0, str(main_zone.process_ref.code) + name + desc)
                    item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                    item.setData(0, Qt.UserRole, main_zone.parcel_id)
                    item.setData(0, Qt.UserRole + 1, "point")
                    self.item_point_main.addChild(item)

                    value_p = self.load_pbar.value() + 1
                    self.load_pbar.setValue(value_p)

        for main_zone in main_zone_lines:
            name = ''
            if main_zone.gazner:
                name = '(' + main_zone.gazner + ')'
            desc = ''
            if main_zone.process_ref:
                if main_zone.process_ref.description:
                    desc = main_zone.process_ref.description
                    item = QTreeWidgetItem()
                    item.setText(0, str(main_zone.process_ref.code) + name + desc)
                    item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                    item.setData(0, Qt.UserRole, main_zone.parcel_id)
                    item.setData(0, Qt.UserRole + 1, "line")
                    self.item_line_main.addChild(item)
                    value_p = self.load_pbar.value() + 1
                    self.load_pbar.setValue(value_p)

        for main_zone in main_zone_polygons:
            name = ''
            if main_zone.gazner:
                name = '(' + main_zone.gazner + ')'
            desc = ''
            if main_zone.process_ref:
                if main_zone.process_ref.description:
                    desc = main_zone.process_ref.description
                    item = QTreeWidgetItem()
                    item.setText(0, str(main_zone.process_ref.code) + name + desc)
                    item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                    item.setData(0, Qt.UserRole, main_zone.parcel_id)
                    item.setData(0, Qt.UserRole + 1, "polygon")
                    self.item_polygon_main.addChild(item)
                    value_p = self.load_pbar.value() + 1
                    self.load_pbar.setValue(value_p)

        self.main_tree_widget.expandAll()
        self.load_pbar.setVisible(False)

    @pyqtSlot()
    def on_main_zone_load_button_clicked(self):

        self.load_pbar.setVisible(True)
        self.load_pbar.setMinimum(1)
        self.load_pbar.setValue(0)

        au2 = DatabaseUtils.working_l2_code()
        if self.tabWidget.currentIndex() == 0:
            self.__setup_main_tree_widget()
            self.__load_main_zone(au2)

    @pyqtSlot()
    def zoom_to_selected_clicked(self):

        selected_item = self.main_tree_widget.selectedItems()[0]

        parcel_id = selected_item.data(0, Qt.UserRole)
        type = selected_item.data(0, Qt.UserRole+1)
        if selected_item is None:
            return

        LayerUtils.deselect_all()

        if type == 'line':
            layer = LayerUtils.layer_by_data_source("data_plan", "ld_view_project_main_zone_line")

            if parcel_id:
                expression = " parcel_id = \'" + str(parcel_id) + "\'"
                request = QgsFeatureRequest()
                request.setFilterExpression(expression)
                feature_ids = []
                iterator = layer.getFeatures(request)

                for feature in iterator:
                    feature_ids.append(feature.id())
                if len(feature_ids) == 0:
                    self.error_label.setText(self.tr("No parcel assigned"))

                layer.setSelectedFeatures(feature_ids)
                self.plugin.iface.mapCanvas().zoomToSelected(layer)
        if type == 'point':
            layer = LayerUtils.layer_by_data_source("data_plan", "ld_view_project_main_zone_point")

            if parcel_id:
                expression = " parcel_id = \'" + str(parcel_id) + "\'"
                request = QgsFeatureRequest()
                request.setFilterExpression(expression)
                feature_ids = []
                iterator = layer.getFeatures(request)

                for feature in iterator:
                    feature_ids.append(feature.id())
                if len(feature_ids) == 0:
                    self.error_label.setText(self.tr("No parcel assigned"))

                layer.setSelectedFeatures(feature_ids)
                self.plugin.iface.mapCanvas().zoomToSelected(layer)
        if type == 'polygon':
            layer = LayerUtils.layer_by_data_source("data_plan", "ld_view_project_main_zone_polygon")

            if parcel_id:
                expression = " parcel_id = \'" + str(parcel_id) + "\'"
                request = QgsFeatureRequest()
                request.setFilterExpression(expression)
                feature_ids = []
                iterator = layer.getFeatures(request)

                for feature in iterator:
                    feature_ids.append(feature.id())
                if len(feature_ids) == 0:
                    self.error_label.setText(self.tr("No parcel assigned"))

                layer.setSelectedFeatures(feature_ids)
                self.plugin.iface.mapCanvas().zoomToSelected(layer)