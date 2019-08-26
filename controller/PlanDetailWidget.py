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
from ..model.PlProject import *
from ..model.ClPlanDecisionLevel import *
from ..model.SetWorkruleStatus import *
from ..model.ClPlanType import *
from ..model.PlProjectStatusHistory import *
from ..model.PlProjectParcel import *
from ..model.ClPlanZone import *
from ..model.ClZoneSub import *
from ..model.ClPlanZone import *
from ..model.ClPlanZoneType import *
from ..utils.DatabaseUtils import *
from ..utils.PluginUtils import *
from ..model.DatabaseHelper import *
from ..model.Constants import *
from ..controller.PlanNavigatorWidget import *
from ..controller.PlanAttributeEditDialog import *
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
        self.main_load_pbar.setVisible(False)
        self.__setup_data()
        self.__setup_cbox()
        self.__setup_main_tree_widget()
        self.__setup_context_menu()
        self.parcels = []
        self.process_types = []
        self.main_tree_widget.itemChanged.connect(self.__itemMainParcelsCheckChanged)

    def __setup_cbox(self):

        self.zone_type_cbox.clear()
        values = self.session.query(ClPlanZoneType).order_by(ClPlanZoneType.sort_order.asc()).all()

        self.zone_type_cbox.addItem("*", -1)
        for value in values:
            self.zone_type_cbox.addItem(str(value.code) + ':' + value.name, value.plan_zone_type_id)

    @pyqtSlot(int)
    def on_zone_type_cbox_currentIndexChanged(self, index):

        zone_type_id = self.zone_type_cbox.itemData(index)

        self.main_process_type_cbox.clear()
        self.main_process_type_cbox.addItem("*", -1)
        if zone_type_id != -1:
            values = self.session.query(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                join(PlProjectParcel, ClPlanZone.plan_zone_id == PlProjectParcel.plan_zone_id). \
                filter(PlProjectParcel.project_id == self.plan.project_id). \
                filter(ClPlanZone.plan_zone_type_id == zone_type_id). \
                group_by(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                order_by(ClPlanZone.code)
            for value in values:
                self.main_process_type_cbox.addItem(str(value.code) + ':' + value.name, value.plan_zone_id)
        elif zone_type_id == -1:
            values = self.session.query(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                join(PlProjectParcel, ClPlanZone.plan_zone_id == PlProjectParcel.plan_zone_id). \
                filter(PlProjectParcel.project_id == self.plan.project_id). \
                group_by(ClPlanZone.plan_zone_id, ClPlanZone.code, ClPlanZone.name). \
                order_by(ClPlanZone.code)
            for value in values:
                self.main_process_type_cbox.addItem(str(value.code) + ':' + value.name, value.plan_zone_id)

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

        self.plan_num_edit.setText(self.plan.code)
        self.date_edit.setText(str(self.plan.start_date))
        self.type_edit.setText(self.plan.plan_type_ref.description)
        self.decision_level_edit.setText(self.plan.plan_decision_level_ref.description)
        self.status_edit.setText(self.plan.workrule_status_ref.description)

    @pyqtSlot()
    def on_home_button_clicked(self):

        self.navigator.show()
        self.hide()

    @pyqtSlot(QPoint)
    def on_main_tree_widget_customContextMenuRequested(self, point):

        point = self.main_tree_widget.viewport().mapToGlobal(point)
        self.menu.exec_(point)

    def __load_main_zone(self, au2):

        self.main_load_pbar.setValue(1)

        values = self.session.query(PlProjectParcel). \
            filter(PlProjectParcel.project_id == self.plan.project_id)

        all_count = values.count()
        self.main_load_pbar.setMaximum(all_count)

        points = self.session.query(PlProjectParcel). \
            filter(PlProjectParcel.project_id == self.plan.project_id). \
            filter(PlProjectParcel.polygon_geom == None). \
            filter(PlProjectParcel.line_geom == None).order_by(PlProjectParcel.badedturl)

        lines = self.session.query(PlProjectParcel). \
            filter(PlProjectParcel.project_id == self.plan.project_id). \
            filter(PlProjectParcel.polygon_geom == None). \
            filter(PlProjectParcel.point_geom == None).order_by(PlProjectParcel.badedturl)

        polygons = self.session.query(PlProjectParcel). \
            filter(PlProjectParcel.project_id == self.plan.project_id). \
            filter(PlProjectParcel.line_geom == None). \
            filter(PlProjectParcel.point_geom == None).order_by(PlProjectParcel.badedturl)

        if self.main_process_type_cbox.currentIndex() != -1:
            if not self.main_process_type_cbox.itemData(self.main_process_type_cbox.currentIndex()) == -1:
                process_type = self.main_process_type_cbox.itemData(self.main_process_type_cbox.currentIndex())

                points = points.filter(PlProjectParcel.plan_zone_id == process_type)
                lines = lines.filter(PlProjectParcel.plan_zone_id == process_type)
                polygons = polygons.filter(PlProjectParcel.plan_zone_id == process_type)

        if self.main_process_edit.text():
            process_text = "%" + self.main_process_edit.text() + "%"
            points = points.\
                join(ClZoneSub, PlProjectParcel.plan_zone_id == ClZoneSub.plan_zone_id).\
                filter(ClZoneSub.description.ilike(process_text))

            lines = lines. \
                join(ClZoneSub, PlProjectParcel.plan_zone_id == ClZoneSub.plan_zone_id). \
                filter(ClZoneSub.description.ilike(process_text))

            polygons = polygons. \
                join(ClZoneSub, PlProjectParcel.plan_zone_id == ClZoneSub.plan_zone_id). \
                filter(ClZoneSub.description.ilike(process_text))

        count = 0
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
                    item.setText(0, str(value.plan_zone_ref.code)+ ': ' + name + desc)
                    item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                    item.setData(0, Qt.UserRole, value.parcel_id)
                    item.setData(0, Qt.UserRole + 1, "polygon")
                    item.setData(0, Qt.UserRole + 2, value.plan_zone_id)
                    item.setCheckState(0, Qt.Unchecked)
                    self.item_polygon_main.addChild(item)
                    value_p = self.main_load_pbar.value() + 1
                    self.main_load_pbar.setValue(value_p)

                    count += 1
                    self.parcel_results_label.setText(self.tr("Results: ") + str(all_count) + '/' + str(count))

        for value in points:
            name = ''
            if value.gazner:
                name = '(' + value.gazner + ')'
            desc = ''
            if value.plan_zone_ref:
                if value.plan_zone_ref.name:
                    desc = value.plan_zone_ref.name
                    item = QTreeWidgetItem()
                    item.setText(0, str(value.plan_zone_ref.code)+ ': ' + name + desc)
                    item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                    item.setData(0, Qt.UserRole, value.parcel_id)
                    item.setData(0, Qt.UserRole + 1, "point")
                    item.setData(0, Qt.UserRole + 2, value.plan_zone_id)
                    item.setCheckState(0, Qt.Unchecked)
                    self.item_point_main.addChild(item)
                    value_p = self.main_load_pbar.value() + 1
                    self.main_load_pbar.setValue(value_p)

                    count += 1
                    self.parcel_results_label.setText(self.tr("Results: ") + str(all_count) + '/' + str(count))

        for value in lines:
            name = ''
            if value.gazner:
                name = '(' + value.gazner + ')'
            desc = ''
            if value.plan_zone_ref:
                if value.plan_zone_ref.name:
                    desc = value.plan_zone_ref.name
                    item = QTreeWidgetItem()
                    item.setText(0, str(value.plan_zone_ref.code)+ ': ' + name + desc)
                    item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                    item.setData(0, Qt.UserRole, value.parcel_id)
                    item.setData(0, Qt.UserRole + 1, "line")
                    item.setData(0, Qt.UserRole + 2, value.plan_zone_id)
                    item.setCheckState(0, Qt.Unchecked)
                    self.item_line_main.addChild(item)
                    value_p = self.main_load_pbar.value() + 1
                    self.main_load_pbar.setValue(value_p)

                    count += 1
                    self.parcel_results_label.setText(self.tr("Results: ") + str(all_count) + '/' + str(count))

        self.main_tree_widget.expandAll()
        self.main_load_pbar.setVisible(False)

    @pyqtSlot()
    def on_main_zone_load_button_clicked(self):

        self.main_load_pbar.setVisible(True)
        self.main_load_pbar.setMinimum(1)
        self.main_load_pbar.setValue(0)

        au2 = DatabaseUtils.working_l2_code()
        # if self.tabWidget.currentIndex() == 0:
        self.__setup_main_tree_widget()
        self.__load_main_zone(au2)

    def __selected_feature(self, parcel_id, layer):

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

    @pyqtSlot()
    def zoom_to_selected_clicked(self):

        selected_item = self.main_tree_widget.selectedItems()[0]

        parcel_id = selected_item.data(0, Qt.UserRole)
        type = selected_item.data(0, Qt.UserRole+1)
        if selected_item is None:
            return

        LayerUtils.deselect_all()

        schema_name = "data_plan"
        table_name = "pl_view_project_parcel"
        layers = QgsMapLayerRegistry.instance().mapLayers()

        for id, layer in layers.iteritems():
            if layer.type() == QgsMapLayer.VectorLayer:
                uri_string = layer.dataProvider().dataSourceUri()
                uri = QgsDataSourceURI(uri_string)
                if uri.table() == table_name:
                    if uri.schema() == schema_name:
                        self.__selected_feature(parcel_id, layer)

    @pyqtSlot()
    def on_main_edit_attribute_button_clicked(self):

        parcel_list = self.parcels

        if DialogInspector().dialog_visible():
            return

        if not parcel_list:
            PluginUtils.show_message(self, u'Анхааруулга',
                                     u'Жагсаалтаас сонгоно уу!')
            return

        #if not self.__parcels_process_type_check():
        #    PluginUtils.show_message(self, u'Анхааруулга',
        #                             u'Сонгосон нэгж талбаруудын үйл ажиллагааны төрөл зөвшөөрөгдөхгүй байна.')
        #   return
        b = set(self.process_types)

        process_type = list(b)[0]
        self.current_dialog = PlanAttributeEditDialog(self.plugin, self, parcel_list, process_type, self.plan,True,
                                                    self.plugin.iface.mainWindow())
        self.current_dialog.show()

        DatabaseUtils.set_working_schema()

    def __parcels_process_type_check(self):

        is_approved = False
        if self.process_types:
            b = set(self.process_types)
            if len(list(b)) == 1:
                is_approved = True
            else:
                is_approved = False

        return is_approved

    def __itemMainParcelsCheckChanged(self, item, column):

        if item.checkState(column) == QtCore.Qt.Checked:
            code = item.data(0, Qt.UserRole)
            process_type = item.data(0, Qt.UserRole+2)
            if code not in self.parcels:
                self.parcels.append(code)
            if process_type not in self.process_types:
                self.process_types.append(process_type)
        elif item.checkState(column) == QtCore.Qt.Unchecked:
            code = item.data(0, Qt.UserRole)
            process_type = item.data(0, Qt.UserRole + 2)
            if code in self.parcels:
                self.parcels.remove(code)
            if process_type in self.process_types:
                self.process_types.remove(process_type)

    def __itemSubParcelsCheckChanged(self, item, column):

        if item.checkState(column) == QtCore.Qt.Checked:
            code = item.data(0, Qt.UserRole)
            process_type = item.data(0, Qt.UserRole+2)
            if code not in self.parcels:
                self.parcels.append(code)
            if process_type not in self.process_types:
                self.process_types.append(process_type)
        elif item.checkState(column) == QtCore.Qt.Unchecked:
            code = item.data(0, Qt.UserRole)
            process_type = item.data(0, Qt.UserRole + 2)
            if code in self.parcels:
                self.parcels.remove(code)
            if process_type in self.process_types:
                self.process_types.remove(process_type)

    def __itemPlanParcelsCheckChanged(self, item, column):

        if item.checkState(column) == QtCore.Qt.Checked:
            code = item.data(0, Qt.UserRole)
            process_type = item.data(0, Qt.UserRole+2)
            if code not in self.parcels:
                self.parcels.append(code)
            if process_type not in self.process_types:
                self.process_types.append(process_type)
        elif item.checkState(column) == QtCore.Qt.Unchecked:
            code = item.data(0, Qt.UserRole)
            process_type = item.data(0, Qt.UserRole + 2)
            if code in self.parcels:
                self.parcels.remove(code)
            if process_type in self.process_types:
                self.process_types.remove(process_type)

    def __remove_parcel_items(self):

        self.__setup_main_tree_widget()
        self.parcel_results_label.setText("")

    @pyqtSlot()
    def on_parcel_clear_button_clicked(self):

        self.__remove_parcel_items()
        # self.__clear_parcel()

    @pyqtSlot()
    def on_get_data_layer_button_clicked(self):

        print '---'
        print self.item_polygon_main.childCount()
        print self.item_line_main.childCount()
        print self.item_point_main.childCount()


