# -*- encoding: utf-8 -*-
__author__ = 'B.Ankhbold'

from qgis.core import *
from geoalchemy2.elements import WKTElement
from sqlalchemy import func, or_, and_, desc
from ..view.Ui_CreateCaseDialog import *
from ..utils.LayerUtils import LayerUtils
from ..model.CaTmpParcel import *
from ..model.CaMaintenanceCase import *
from ..model.CaBuilding import *
from ..model.CaTmpBuilding import *
from ..model.CtApplicationStatus import *
from ..model.ClLanduseType import *
from ..model.DatabaseHelper import DatabaseHelper
from ..model import Constants
from ..model.CaParcelTbl import *
from ..model.SetOrgTypeSpaTypeLanduse import *
from ..model.CaSpaParcelTbl import *
from .qt_classes.ApplicationCmbBoxDelegate import *
from ..controller.ApplicationsDialog import *
from ..model.ApplicationSearch import *
from ..model.AuMpa import *
# from ..model.CaPlanParcel import *
from ..model.PlProjectParcel import *
from ..model.PlProject import *
from ..model.ClPlanType import *
from ..model.StStreet import *
from ..model.StRoad import *
from ..model.ClPlanDecisionLevel import *
from ..model.StStreetLineView import *
from ..model.AuLevel3 import *
from ..model.SetLanduseSafetyZone import *
from ..model.SetOverlapsLanduse import *
from ..model.CaTmpLanduseTypeTbl import *
from ..model.StWorkflow import *
from ..model.CaLanduseMaintenanceCase import *
from ..model.StWorkflow import *
from ..model.StWorkflowStatusLanduse import *
from ..model.ClLanduseMovementStatus import *
from ..model.StWorkflowStatus import *
from ..model.CaLanduseMaintenanceStatus import *
import urllib
import urllib2
import json

APPROVED = 'approved'
REFUSED = 'refused'

class CreateCaseDialog(QDialog, Ui_CreateCaseDialog, DatabaseHelper):

    def __init__(self, plugin, m_case, attribute_update=False, parent=None):

        super(CreateCaseDialog, self).__init__(parent)
        DatabaseHelper.__init__(self)

        self.setupUi(self)
        self.timer = None
        self.close_button.clicked.connect(self.reject)

        self.plugin = plugin
        self.ca_maintenance_case = m_case
        self.attribute_update = attribute_update

        self.session = SessionHandler().session_instance()
        self.is_file_import = False
        self.file_path = None
        self.landuse_code = None
        self.approved_item = None
        self.refused_item = None
        self.__setup_landuse_combobox()
        self.__result_twidget_setup()
        self.error_dic = {}
        self.buildings_item = None
        self.parcels_item = None
        self.filling = False
        self.exclude_list = []
        self.application_list = list()
        self.start_date.setDateTime(QDateTime().currentDateTime())
        self.working_soum = DatabaseUtils.working_l2_code()
        self.maintenance_parcels = []
        self.maintenance_buildings = []
        self.tabWidget.currentChanged.connect(self.onChangetab)
        self.tab_index = 0
        self.import_landuse_groupbox.setEnabled(True)

        self.__setup_street_table_widget()
        self.street_treewidget.itemClicked.connect(self.__onItemClickedStreetTreewidget)
        self.street_treewidget.itemDoubleClicked.connect(self.__onItemDoubleClickedStreetTreewidget)

        # self.__setup_twidgets()
        self.__setup_context_menu()
        self.is_shape_parcel = False

        try:

            if self.__check_requirements():
                if self.attribute_update:
                    self.__setup_mapping()
                else:
                    user = DatabaseUtils.current_user()
                    self.created_by_edit.setText(user.surname + "-" + user.first_name)

                    self.__parcel_touch_select()

        except LM2Exception, e:
            PluginUtils.show_error(self, e.title(), e.message())

    def onChangetab(self, i):

        self.tab_index = i

    def __setup_mapping(self):

        self.__set_up_twidget(self.applications_twidget)
        completion_date = PluginUtils.convert_python_date_to_qt(self.ca_maintenance_case.completion_date)
        if completion_date:
            converted_date = completion_date.toString(completion_date.toString(Constants.DATABASE_DATE_FORMAT))
            self.completion_date_edit.setText(converted_date)

        survey_date = PluginUtils.convert_python_date_to_qt(self.ca_maintenance_case.survey_date)
        if survey_date:
            self.survey_date_edit.setText(survey_date.toString(Constants.DATABASE_DATE_FORMAT))

        creation_date = PluginUtils.convert_python_date_to_qt(self.ca_maintenance_case.creation_date)
        if creation_date:
            self.start_date.setDate(creation_date)

        if self.ca_maintenance_case.created_by is not None:

            sd_user = self.session.query(SdUser).filter(SdUser.user_id == self.ca_maintenance_case.created_by).one()
            # created_by_role = self.session.query(SetRole)\
            #                         .filter(SetRole.user_name_real == self.ca_maintenance_case.created_by).one()
            self.created_by_edit.setText((sd_user.lastname + " " + sd_user.firstname))

        if self.ca_maintenance_case.surveyed_by_land_office is not None:
            sd_user_count = self.session.query(SdUser).filter(SdUser.user_id == self.ca_maintenance_case.surveyed_by_land_office).count()
            if sd_user_count == 1:
                sd_user = self.session.query(SdUser).filter(
                    SdUser.user_id == self.ca_maintenance_case.surveyed_by_land_office).one()
                # surveyed_land_office_role = self.session.query(SetRole)\
                #                                 .filter(SetRole.user_name_real == self.ca_maintenance_case.surveyed_by_land_office)\
                #                                 .one()
                self.surveyed_by_land_office_edit.setText((sd_user.lastname +" "+
                                                           sd_user.firstname))

        if self.ca_maintenance_case.surveyed_by_surveyor is not None:
            surveyed_by_surveyor_role = self.session.query(SetSurveyor)\
                                            .filter(SetSurveyor.id == self.ca_maintenance_case.surveyed_by_surveyor)\
                                            .one()
            self.surveyed_by_surveyor_edit.setText((surveyed_by_surveyor_role.first_name+" "+
                                                           surveyed_by_surveyor_role.surname))

        if self.ca_maintenance_case.completed_by:
            sd_user = self.session.query(SdUser).filter(
                SdUser.user_id == self.ca_maintenance_case.completed_by).one()
            # completed_by_role = self.session.query(SetRole)\
            #                                     .filter(SetRole.user_name_real == self.ca_maintenance_case.completed_by).one()
            self.completed_by_edit.setText((sd_user.lastname +" "+ sd_user.firstname))

        # applications = self.session.query(CtApplication.app_no)\
        #     .filter(CtApplication.parcel == None).all()

        # for app_result in applications:
        #
        #     item = QTableWidgetItem()
        #     item.setText(app_result[0])
        #
        #     row = self.applications_twidget.rowCount()
        #     self.applications_twidget.insertRow(row)
        #
        #     self.applications_twidget.setItem(row, 0, item)

        self.buildings_item = QTreeWidgetItem()
        self.buildings_item.setExpanded(True)
        self.buildings_item.setText(0, self.tr("Buildings"))

        self.parcels_item = QTreeWidgetItem()
        self.parcels_item.setExpanded(True)
        self.parcels_item.setText(0, self.tr("Parcels"))

        self.result_twidget.addTopLevelItem(self.parcels_item)
        self.result_twidget.addTopLevelItem(self.buildings_item)

        parcel_count = 0
        khashaa = ""
        street = ""

        for parcel in self.ca_maintenance_case.parcels:
            touch_item = QTreeWidgetItem()
            touch_item.setText(0, parcel.parcel_id)
            khashaa = parcel.address_khashaa
            street = parcel.address_streetname
            touch_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_grey.png")))
            touch_item.setData(0, Qt.UserRole, parcel.parcel_id)
            touch_item.setData(0, Qt.UserRole + 1, Constants.CASE_PARCEL_IDENTIFIER)
            self.parcels_item.addChild(touch_item)
            parcel_count += 1

        building_count = 0
        for building in self.ca_maintenance_case.buildings:
            building_item = QTreeWidgetItem()
            building_item.setText(0, building.building_id)
            building_item.setData(0, Qt.UserRole, building.building_id)
            building_item.setData(0, Qt.UserRole + 1, Constants.CASE_BUILDING_IDENTIFIER)
            building_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/building.gif")))
            self.buildings_item.addChild(building_item)
            building_count += 1

        self.parcel_count_label.setText(str(parcel_count))
        self.building_count_label.setText(str(building_count))
        self.street_label.setText(street)
        self.khashaa_label.setText(khashaa)

    @staticmethod
    def __check_requirements():

        #parcel layer and tmp parcel layer should be added
        #building layer and tmp building layer should be added
        root = QgsProject.instance().layerTreeRoot()

        LayerUtils.refresh_layer()
        restrictions = DatabaseUtils.working_l2_code()

        parcel_layer = LayerUtils.layer_by_data_source("data_soums_union", "ca_parcel")
        if parcel_layer is None:
            LayerUtils.load_tmp_layer_by_name("ca_parcel", "parcel_id", "data_soums_union")

        building_layer = LayerUtils.layer_by_data_source("data_soums_union", "ca_building")
        if building_layer is None:
            LayerUtils.load_tmp_layer_by_name("ca_building", "building_id", "data_soums_union")

        vlayer = LayerUtils.layer_by_data_source("data_soums_union", "ca_tmp_parcel_view")
        if vlayer is None:
            vlayer = LayerUtils.load_tmp_layer_by_name("ca_tmp_parcel_view", "parcel_id", "data_soums_union")
        LayerUtils.refresh_layer()
        mygroup = root.findGroup(u"Кадастр")
        if mygroup is None:
            group = root.insertGroup(3, u"Кадастр")
            group.setExpanded(False)
            mygroup = group.addGroup(u"Кадастрын өөрчлөлт")
        else:
            if root.findGroup(u"Кадастрын өөрчлөлт") is None:
                mygroup = mygroup.addGroup(u"Кадастрын өөрчлөлт")

        myalayer = root.findLayer(vlayer.id())
        vlayer.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"template\style/ca_tmp_parcel.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "Tmp_Parcel"))
        if myalayer is None:
            mygroup.addLayer(vlayer)

        #######    buildingf
        b_vlayer = LayerUtils.layer_by_data_source("data_soums_union", "ca_tmp_building_view")
        if b_vlayer is None:
            b_vlayer = LayerUtils.load_tmp_layer_by_name("ca_tmp_building_view", "building_id", "data_soums_union")
        mygroup = root.findGroup(u"Кадастрын өөрчлөлт")
        myalayer = root.findLayer(b_vlayer.id())
        b_vlayer.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"template\style/ca_tmp_building.qml")
        b_vlayer.setLayerName(QApplication.translate("Plugin", "Tmp_Building"))
        if myalayer is None:
            mygroup.addLayer(b_vlayer)

        return True

    def __setup_twidgets(self):

        self.__set_up_twidget(self.applications_twidget)

        self.result_twidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.result_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.result_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.result_twidget.setContextMenuPolicy(Qt.CustomContextMenu)

        parcel_layer = LayerUtils.layer_by_data_source("data_soums_union", "ca_parcel")
        selected_features = parcel_layer.selectedFeatures()
        selected_features_count = parcel_layer.selectedFeatureCount()
        parcel_id_index = parcel_layer.dataProvider().fieldNameIndex("parcel_id")
        applications = ''
        try:
            for feature in selected_features:
                parcel_id = feature.attributes()[parcel_id_index]
                app_contract_count = self.session.query(CtContractApplicationRole)\
                    .join(CtApplication, CtContractApplicationRole.application == CtApplication.app_no)\
                    .filter(CtContractApplicationRole.contract != None)\
                    .filter(CtApplication.parcel == parcel_id).count()
                app_record_count = self.session.query(CtRecordApplicationRole)\
                    .join(CtApplication, CtRecordApplicationRole.application == CtApplication.app_no)\
                    .filter(CtRecordApplicationRole.record != None)\
                    .filter(CtApplication.parcel == parcel_id).count()
                if app_contract_count > 0:
                    contracts = self.session.query(CtContract)\
                        .join(CtContractApplicationRole, CtContract.contract_no == CtContractApplicationRole.contract)\
                        .join(CtApplication, CtContractApplicationRole.application == CtApplication.app_no)\
                        .filter(CtContract.contract_no != None)\
                        .filter(CtApplication.parcel == parcel_id).all()
                    for contract in contracts:
                        if contract.status != 40:
                            PluginUtils.show_error(self, self.tr("Invalid Parcel"),
                                                self.tr("This parcel connected active possess contract!!!"))
                            self.apply_button.setEnabled(False)
                            return

                        contract_apps = contract.application_roles.all()
                        for contract_app in contract_apps:
                            app = self.session.query(CtApplication). \
                                filter(CtApplication.app_no == contract_app.application).one()
                            if app.app8ext:
                                app8ext = app.app8ext
                                if app8ext.mortgage_status == 10:
                                    PluginUtils.show_error(self, self.tr("Error"),
                                                           self.tr("The contract {0} is mortgagee!").format(contract.contract_no))
                                    return

                            if app.app29ext:
                                app29ext = app.app29ext
                                if app29ext.court_status == 10 or app29ext.court_status == 20:
                                    PluginUtils.show_error(self, self.tr("Error"),
                                                           self.tr("The contract {0} is court decision!").format(
                                                               contract.contract_no))
                                    return

                if app_record_count > 0:
                    records = self.session.query(CtOwnershipRecord)\
                        .join(CtRecordApplicationRole, CtOwnershipRecord.record_no == CtRecordApplicationRole.record)\
                        .join(CtApplication, CtRecordApplicationRole.application == CtApplication.app_no)\
                        .filter(CtOwnershipRecord.record_no != None)\
                        .filter(CtApplication.parcel == parcel_id).all()
                    for record in records:
                        if record.status != 30:
                            PluginUtils.show_error(self, self.tr("Invalid Parcel"),
                                                self.tr("This parcel connected active ownership record!!!"))
                            self.apply_button.setEnabled(False)
                            return
                        record_apps = record.application_roles.all()
                        for record_app in record_apps:
                            app = self.session.query(CtApplication). \
                                filter(CtApplication.app_no == record_app.application).one()
                            if app.app8ext:
                                app8ext = app.app8ext
                                if app8ext.mortgage_status == 10:
                                    PluginUtils.show_error(self, self.tr("Error"),
                                                           self.tr("The contract {0} is mortgagee!").format(record.record_no))
                                    return

                            if app.app29ext:
                                app29ext = app.app29ext
                                if app29ext.court_status == 10 or app29ext.court_status == 20:
                                    PluginUtils.show_error(self, self.tr("Error"),
                                                           self.tr("The contract {0} is court decision!").format(
                                                               record.record_no))
                                    return

                applications = self.session.query(CtApplication.app_no).join(CtApplicationStatus)\
                    .filter(CtApplication.parcel == parcel_id)\
                    .filter(CtApplicationStatus.status < Constants.APP_STATUS_SEND)\
                    .filter(CtApplication.maintenance_case.is_(None)).distinct(CtApplication.app_no).all()
                applications_count = self.session.query(CtApplication.app_no).join(CtApplicationStatus)\
                    .filter(CtApplication.parcel == parcel_id)\
                    .filter(CtApplicationStatus.status < Constants.APP_STATUS_SEND)\
                    .filter(CtApplication.maintenance_case.is_(None)).distinct(CtApplication.app_no).count()

                if applications_count != 0:
                    for app_result in applications:

                        item = QTableWidgetItem()
                        item.setText(app_result[0])
                        row = self.applications_twidget.rowCount()
                        self.applications_twidget.insertRow(row)

                        self.applications_twidget.setItem(row, 0, item)

            app_no_parcel = self.session.query(CtApplication.app_no).filter(CtApplication.parcel == None).all()
            app_no_parcel_count = self.session.query(CtApplication).filter(CtApplication.parcel == None).count()

            if selected_features_count == 0 and app_no_parcel_count != 0:

                for app_result in app_no_parcel:

                    item = QTableWidgetItem()
                    item.setText(app_result[0])
                    row = self.applications_twidget.rowCount()
                    self.applications_twidget.insertRow(row)

                    self.applications_twidget.setItem(row, 0, item)

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return


        self.application_list = list()
        del self.application_list[:]
        for app in applications:
            self.application_list.append(app.app_no)
        if applications != "" and applications_count != 0:
            delegate = ApplicationCmbBoxDelegate(0, self.application_list, self.applications_twidget)
            self.applications_twidget.setItemDelegateForColumn(0, delegate)
        else:
            for app in app_no_parcel:
                self.application_list.append(app.app_no)
            if selected_features_count == 0 and app_no_parcel_count > 0:
                delegate = ApplicationCmbBoxDelegate(0, self.application_list, self.applications_twidget)
                self.applications_twidget.setItemDelegateForColumn(0, delegate)

    def __set_up_twidget(self, table_widget):

        table_widget.setAlternatingRowColors(True)
        table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        table_widget.setSelectionMode(QTableWidget.SingleSelection)

    def __setup_context_menu(self):

        self.menu = QMenu()
        self.zoom_to_selected = QAction(QIcon("zoom.png"), "Zoom to item", self)
        self.menu.addAction(self.zoom_to_selected)
        self.zoom_to_selected.triggered.connect(self.zoom_to_selected_clicked)

        self.new_menu = QMenu()
        self.new_zoom_to_selected = QAction(QIcon("zoom.png"), "New Parcel Zoom to item", self)
        self.new_menu.addAction(self.new_zoom_to_selected)
        self.new_zoom_to_selected.triggered.connect(self.new_zoom_to_selected_clicked)

        self.landuse_case_menu = QMenu()
        self.landsue_case_zoom_to_selected = QAction(QIcon("zoom.png"), "New Parcel Zoom to item", self)
        self.landuse_case_menu.addAction(self.landsue_case_zoom_to_selected)
        self.landsue_case_zoom_to_selected.triggered.connect(self.landsue_case_zoom_to_selected_clicked)

    @pyqtSlot()
    def zoom_to_selected_clicked(self):

        selected_item = self.result_twidget.selectedItems()[0]

        if selected_item is None:
            return

        if selected_item.data(0, Qt.UserRole + 1) == Constants.CASE_PARCEL_IDENTIFIER:
            working_soum = DatabaseUtils.working_l2_code()
            parcel_layer = LayerUtils.layer_by_data_source("data_soums_union", "ca_parcel")
            selection_features = []

            for f in LayerUtils.where(parcel_layer, "parcel_id={0}".format(selected_item.data(0, Qt.UserRole))):
                selection_features.append(f.id())

            parcel_layer.setSelectedFeatures(selection_features)

            self.plugin.iface.mapCanvas().zoomToSelected(parcel_layer)
            self.plugin.iface.mapCanvas().zoomOut()

        elif selected_item.data(0, Qt.UserRole + 1) == Constants.CASE_BUILDING_IDENTIFIER:
            working_soum = DatabaseUtils.working_l2_code()
            building_layer = LayerUtils.layer_by_data_source("data_soums_union", "ca_building")
            selection_features = []

            for f in LayerUtils.where(building_layer, "building_id={0}".format(selected_item.data(0, Qt.UserRole))):
                selection_features.append(f.id())

            building_layer.setSelectedFeatures(selection_features)

            self.plugin.iface.mapCanvas().zoomToSelected(building_layer)
            self.plugin.iface.mapCanvas().zoomOut()
            self.plugin.iface.mapCanvas().zoomOut()


    def __setup_file_import(self):

        self.import_groupbox.setEnabled(True)
        self.parcels_item = QTreeWidgetItem()
        parcels_caption = self.tr("Parcels")
        self.parcels_item.setText(0, parcels_caption)

        self.buildings_item = QTreeWidgetItem()
        buildings_caption = self.tr("Buildings")
        self.buildings_item.setText(0, buildings_caption)

        self.result_twidget.addTopLevelItem(self.buildings_item)
        self.result_twidget.addTopLevelItem(self.parcels_item)

    def __parcel_touch_select(self):

        working_soum = DatabaseUtils.working_l2_code()
        parcel_layer = LayerUtils.layer_by_data_source("data_soums_union", "ca_parcel")
        self.maintenance_parcels = []
        self.maintenance_buildings = []

        if not parcel_layer:
            PluginUtils.show_error(self, self.tr("Error"),
                                   self.tr("Could not identify parcel layer. "
                                           "Please load the parcel layer for the working soum."))
            self.apply_button.setEnabled(False)
            return

        count = parcel_layer.selectedFeatureCount()
        if count == 0:
            #enable file import
            self.is_file_import = True
            self.__setup_file_import()
            return

        selected_features = parcel_layer.selectedFeatures()
        parcel_id_index = parcel_layer.dataProvider().fieldNameIndex("parcel_id")

        parcel_count = 0
        building_count = 0

        for feature in selected_features:
            parcel_count += 1
            parcel_id = feature.attributes()[parcel_id_index]

            #checks if the parcel is already in the tmp layer
            try:
                count1 = self.session.query(CaTmpParcel).filter(CaTmpParcel.parcel_id == parcel_id).count()

            except SQLAlchemyError, e:
                raise LM2Exception(self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

            if count1 > 0:
                PluginUtils.show_error(self, "Selection Error",
                                       self.tr("One of selected parcel is already in an active case. "
                                               "First finalize or revert from active case. Close dialog window"))
                self.apply_button.setEnabled(False)
                return

            if parcel_id in self.maintenance_parcels:
                continue

            self.maintenance_parcels.append(parcel_id)

            #Add main parcel to the tree
            main_parcel_item = QTreeWidgetItem()
            main_parcel_item.setText(0, parcel_id)
            main_parcel_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
            main_parcel_item.setData(0, Qt.UserRole, parcel_id)
            main_parcel_item.setData(0, Qt.UserRole + 1, Constants.CASE_PARCEL_IDENTIFIER)
            main_parcel_item.setData(0, Qt.UserRole + 1, Constants.CASE_PARCEL_IDENTIFIER)
            self.result_twidget.addTopLevelItem(main_parcel_item)

            try:
                parcel_geometry = self.session.query(CaParcel.geometry).filter(CaParcel.parcel_id == parcel_id).one()

                touching_parcels = self.session.query(CaParcel)\
                    .filter(CaParcel.geometry.ST_Intersects(parcel_geometry[0]))\
                    .filter(CaParcel.parcel_id != parcel_id).all()

            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return

            for touching_parcel in touching_parcels:

                try:
                    count = self.session.query(CaTmpParcel)\
                        .filter(CaTmpParcel.parcel_id == touching_parcel.parcel_id).count()
                except SQLAlchemyError, e:
                    PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                    return

                if count > 0:
                    PluginUtils.show_error(self, self.tr("Selection Error"),
                                           self.tr("One of selected parcel is already in active case. "
                                                   "First finalize or revert from active case. Close dialog window"))

                    self.apply_button.setEnabled(False)
                    self.reject()
                    return

                if touching_parcel.parcel_id in self.maintenance_parcels:
                    continue

                parcel_count += 1
                touch_item = QTreeWidgetItem()
                touch_item.setText(0, touching_parcel.parcel_id)
                touch_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_grey.png")))
                touch_item.setData(0, Qt.UserRole, touching_parcel.parcel_id)
                touch_item.setData(0, Qt.UserRole + 1, Constants.CASE_PARCEL_IDENTIFIER)
                self.result_twidget.addTopLevelItem(touch_item)

                self.maintenance_parcels.append(touching_parcel.parcel_id)

                #building features for touching parcels
                try:
                    buildings = self.session.query(CaBuilding.building_id)\
                                    .filter(CaBuilding.geometry.ST_Within(touching_parcel.geometry))\
                                    .filter(CaBuilding.building_id.ilike(touching_parcel.parcel_id + "%")).all()

                except SQLAlchemyError, e:
                    raise LM2Exception(self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                    return

                for building in buildings:

                    if building[0] in self.maintenance_buildings:
                        continue

                    building_count += 1
                    building_item = QTreeWidgetItem()
                    building_item.setText(0, building[0])
                    building_item.setData(0, Qt.UserRole, building[0])
                    building_item.setData(0, Qt.UserRole + 1, Constants.CASE_BUILDING_IDENTIFIER)
                    building_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/building.gif")))
                    touch_item.addChild(building_item)

                    self.maintenance_buildings.append(building[0])

            #gets the containing building features
            try:
                buildings = self.session.query(CaBuilding.building_id)\
                                .filter(CaBuilding.geometry.ST_Within(parcel_geometry[0]))\
                                .filter(CaBuilding.building_id.contains(parcel_id)).all()

                for building in buildings:

                    if building[0] in self.maintenance_buildings:
                        continue

                    building_count += 1
                    building_item = QTreeWidgetItem()
                    building_item.setText(0, building[0])
                    building_item.setData(0, Qt.UserRole, building[0])
                    building_item.setData(0, Qt.UserRole + 1, Constants.CASE_BUILDING_IDENTIFIER)
                    building_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/building.gif")))
                    main_parcel_item.addChild(building_item)

                    self.maintenance_buildings.append(building[0])

            except SQLAlchemyError, e:
                raise LM2Exception(self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return

        self.parcel_count_label.setText(str(parcel_count))
        self.building_count_label.setText(str(building_count))

    @pyqtSlot()
    def on_result_twidget_itemSelectionChanged(self):

        if self.is_file_import:
            return

        current_item = self.result_twidget.selectedItems()[0]
        object_type = current_item.data(0, Qt.UserRole + 1)
        object_id = current_item.data(0, Qt.UserRole)

        if object_type == Constants.CASE_PARCEL_IDENTIFIER:
            try:
                parcel = self.session.query(CaParcel.address_khashaa, CaParcel.address_streetname)\
                    .filter(CaParcel.parcel_id == object_id).one()

                self.khashaa_label.setText(parcel[0])
                self.street_label.setText(parcel[1])
            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return

        elif object_type == Constants.CASE_BUILDING_IDENTIFIER:
            try:
                building = self.session.query(CaBuilding.address_khashaa, CaBuilding.address_streetname)\
                    .filter(CaBuilding.building_id == object_id).one()

                self.khashaa_label.setText(building[0])
                self.street_label.setText(building[1])
            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return

    def __default_path(self):

        default_path = r'D:/TM_LM2/cad_maintenance'
        default_parent_path = r'D:/TM_LM2'
        if not os.path.exists(default_parent_path):
            os.makedirs('D:/TM_LM2')
            os.makedirs('D:/TM_LM2/application_response')
            os.makedirs('D:/TM_LM2/application_list')
            os.makedirs('D:/TM_LM2/approved_decision')
            os.makedirs('D:/TM_LM2/cad_maintenance')
            os.makedirs('D:/TM_LM2/cad_maps')
            os.makedirs('D:/TM_LM2/contracts')
            os.makedirs('D:/TM_LM2/decision_draft')
            os.makedirs('D:/TM_LM2/dumps')
            os.makedirs('D:/TM_LM2/q_data')
            os.makedirs('D:/TM_LM2/refused_decision')
            os.makedirs('D:/TM_LM2/reports')
            os.makedirs('D:/TM_LM2/training')
        if not os.path.exists(default_path):
            os.makedirs(default_path)

        return default_path

    @pyqtSlot()
    def on_open_parcel_file_button_clicked(self):

        default_path = self.__default_path()

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

    def __check_parcel_correct(self, geometry, error_message):

        organization = DatabaseUtils.current_user_organization()

        valid = True
        if not organization:
            return

        count = self.session.query(CaSpaParcelTbl).filter(geometry.ST_Intersects(CaSpaParcelTbl.geometry)).count()
        if count > 0:
            spa_parcel = self.session.query(CaSpaParcelTbl).filter(geometry.ST_Intersects(CaSpaParcelTbl.geometry)).first()
            check_count = self.session.query(SetOrgTypeSpaTypeLanduse). \
                filter(SetOrgTypeSpaTypeLanduse.org_type == organization). \
                filter(SetOrgTypeSpaTypeLanduse.landuse == spa_parcel.landuse). \
                filter(SetOrgTypeSpaTypeLanduse.spa_type == spa_parcel.spa_type).count()
            landuse = spa_parcel.landuse_ref
            if check_count == 0:
                valid = False
                parcel_error = '"' + landuse.description + '"' + u' -т бүртгэл хийх эрхгүй байна!'
                error_message = error_message + "\n \n" + parcel_error

        # if organization == 1:
        #     # Тусгай хамгаалалтай болон чөлөөт бүсд нэгж талбар оруулж болохгүй
        #     count = self.session.query(AuMpa.id) \
        #         .filter(geometry.ST_Intersects(AuMpa.geometry)).count()
        #     if count > 0:
        #         valid = False
        #         parcel_error = self.tr("Parcels mpa boundary overlap!!!")
        #         error_message = error_message + "\n \n" + parcel_error
        # elif organization == 3:
        #     # Тусгай хамгаалалтай газар нутгаас өөр газар нэгж талбар оруулж болохгүй
        #     count = self.session.query(AuMpa.id) \
        #         .filter(geometry.ST_Within(AuMpa.geometry)).count()
        #
        #     if count == 0:
        #         valid = False
        #         parcel_error = self.tr("Parcels out mpa boundary overlap!!!")
        #         error_message = error_message + "\n \n" + parcel_error
        # elif organization == 5:
        #     # Чөлөөт бүсээс өөр газар нэгж талбар оруулж болохгүй
        #     print ''

        return valid, error_message

    @pyqtSlot()
    def on_open_building_file_button_clicked(self):

        default_path = r'D:/TM_LM2/cad_maintenance'
        default_parent_path = r'D:/TM_LM2'
        if not os.path.exists(default_parent_path):
            os.makedirs('D:/TM_LM2')
            os.makedirs('D:/TM_LM2/application_response')
            os.makedirs('D:/TM_LM2/application_list')
            os.makedirs('D:/TM_LM2/approved_decision')
            os.makedirs('D:/TM_LM2/cad_maintenance')
            os.makedirs('D:/TM_LM2/cad_maps')
            os.makedirs('D:/TM_LM2/contracts')
            os.makedirs('D:/TM_LM2/decision_draft')
            os.makedirs('D:/TM_LM2/dumps')
            os.makedirs('D:/TM_LM2/q_data')
            os.makedirs('D:/TM_LM2/refused_decision')
            os.makedirs('D:/TM_LM2/reports')
            os.makedirs('D:/TM_LM2/training')
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
            self.building_shape_edit.setText(file_path)
            if not self.__import_new_buildings(file_path):
                self.apply_button.setEnabled(False)

            self.open_building_file_button.setEnabled(False)

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
        au1 = DatabaseUtils.working_l1_code()
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

            au2_parcel_count = self.session.query(AuLevel2).\
                filter(AuLevel2.code == working_soum_code). \
                filter(parcel_geometry.ST_Within(AuLevel2.geometry)).count()
            if au2_parcel_count == 0:
                is_out_parcel = True
                break

            wkt_geom = WKTElement(parcel.geometry().exportToWkt(), srid=4326)
            params = urllib.urlencode({'geom': wkt_geom})
            f = urllib.urlopen("http://192.168.15.222/api/geo/parcel/check/by/geom/wkt", params)
            data = json.load(f)
            status = data['status']
            result = data['result']
            if not status:
                PluginUtils.show_message(self, u'Амжилтгүй', u'Өгөгдөл буруу байна!!!')
                return
            else:
                if result:
                    PluginUtils.show_message(self, u'Амжилтгүй', u'Газар олгох боломжгүй байршил!!!')
                    return

            count += 1
            new_parcel = CaTmpParcel()
            new_parcel.parcel_id = QDateTime().currentDateTime().toString("MMddhhmmss") + str(count)
            new_parcel.initial_insert = None
            new_parcel.maintenance_case = self.ca_maintenance_case.id
            new_parcel.au2 = self.working_soum
            new_parcel.valid_from = PluginUtils.convert_qt_date_to_python(QDateTime().currentDateTime())
            new_parcel.geometry = WKTElement(parcel.geometry().exportToWkt(), srid=4326)
            new_parcel = self.__copy_parcel_attributes(parcel, new_parcel, parcel_shape_layer)

            parcel_overlap_c = self.session.query(CaParcel.parcel_id) \
                .filter(WKTElement(parcel.geometry().exportToWkt(), srid=4326).ST_Overlaps(CaParcel.geometry)) \
                .filter(CaParcel.valid_till == "infinity").count()

            tmp_parcel_overlap_c = self.session.query(CaTmpParcel.parcel_id) \
                .filter(
                WKTElement(parcel.geometry().exportToWkt(), srid=4326).ST_Overlaps(CaTmpParcel.geometry)) \
                .filter(CaTmpParcel.valid_till == "infinity").count()

            safety_zone_overlap_c = self.session.query(SetLanduseSafetyZone) \
                .filter(WKTElement(parcel.geometry().exportToWkt(), srid=4326).ST_Overlaps(SetLanduseSafetyZone.geometry)).count()
            # parcel_c = self.session.query(CaParcel.parcel_id) \
            #     .filter(WKTElement(parcel.geometry().exportToWkt(), srid=4326).ST_Within(CaParcel.geometry)).count()

            tmp_parcel_c = self.session.query(CaTmpParcel.parcel_id) \
                .filter(
                WKTElement(parcel.geometry().exportToWkt(), srid=4326).ST_Within(CaTmpParcel.geometry)).count()

            # parcel_plan_c = self.session.query(CaPlanParcel.parcel_id) \
            #     .filter(CaPlanParcel.geometry.ST_Within(WKTElement(parcel.geometry().exportToWkt(), srid=4326))).count()
            #
            # if parcel_plan_c == 0:
            #     PluginUtils.show_message(self, self.tr("Error"), self.tr("This parcel not in cadastre plan!!!"))
            #     return
            if au1 == '011':
                plan_type = self.session.query(ClPlanType).filter(ClPlanType.code == '05').one()
            else:
                plan_type = self.session.query(ClPlanType).filter(ClPlanType.code == '07').one()

            # parcel_plan_c = self.session.query(PlProjectParcel). \
            #     join(PlProject, PlProjectParcel.project_id == PlProject.project_id). \
            #     filter(PlProjectParcel.is_active == True). \
            #     filter(PlProjectParcel.au2 == working_soum_code). \
            #     filter(PlProject.plan_type_id == plan_type.plan_type_id).count()
            #
            # if parcel_plan_c == 0:
            #     PluginUtils.show_message(self, self.tr("Error"), self.tr("This parcel not in cadastre plan!!!"))
            #     return

            landuse_code =  self.__attribute_landuse(parcel, new_parcel, parcel_shape_layer)
            if safety_zone_overlap_c != 0:
                PluginUtils.show_message(self, self.tr("Error"), self.tr("Safety zone layer parcel overlap!!!"))
                return

            if parcel_overlap_c != 0:
                parcel_overlaps = self.session.query(CaParcel) \
                    .filter(WKTElement(parcel.geometry().exportToWkt(), srid=4326).ST_Overlaps(CaParcel.geometry)) \
                    .filter(CaParcel.valid_till == "infinity").all()
                for value in parcel_overlaps:
                    landuse_count = self.session.query(SetOverlapsLanduse). \
                        filter(SetOverlapsLanduse.in_landuse == landuse_code). \
                        filter(SetOverlapsLanduse.ch_landuse == value.landuse).count()
                    if landuse_count == 0:
                        PluginUtils.show_message(self, self.tr("Error"), self.tr("Ca_Parcel layer parcel overlap!!!"))
                        return

            if tmp_parcel_overlap_c != 0:
                PluginUtils.show_message(self, self.tr("Error"), self.tr("Ca_Tmp_Parcel layer parcel overlap!!!"))
                return

            if tmp_parcel_c != 0:
                PluginUtils.show_message(self, self.tr("Error"), self.tr("Ca_Tmp_Parcel layer parcel duplicate!!!"))
                return
            # if parcel_c != 0:
            #     PluginUtils.show_message(self, self.tr("Error"), self.tr("Ca_Parcel layer parcel duplicate!!!"))
            #     return

            self.session.add(new_parcel)

                #Add main parcel to the tree
            main_parcel_item = QTreeWidgetItem()
            main_parcel_item.setText(0, new_parcel.parcel_id)
            main_parcel_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
            main_parcel_item.setData(0, Qt.UserRole, new_parcel.parcel_id)
            main_parcel_item.setData(0, Qt.UserRole + 1, Constants.CASE_PARCEL_IDENTIFIER)
            self.parcels_item.addChild(main_parcel_item)
        if is_out_parcel:
            self.apply_button.setEnabled(False)
            PluginUtils.show_message(self, self.tr('Error Parcel'), self.tr(
                'This parcel out current soum boundary.'))
            return

        # except SQLAlchemyError, e:
        #     PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
        #     return

        self.is_shape_parcel = True

    def __attribute_landuse(self, parcel_feature, parcel_object, layer):

        column_name_old_parcel = "old_parcel"
        column_name_geo_id = "geo_id"
        column_name_landuse = "landuse"
        column_name_documented = "documented"
        column_name_khashaa = "address_kh"
        column_name_street = "address_st"
        column_name_neighbourhood = "address_ne"

        column_names = {column_name_old_parcel: "", column_name_geo_id: "", column_name_landuse: "",
                        column_name_documented: "", column_name_khashaa: "", column_name_street: "",
                        column_name_neighbourhood: ""}

        provider = layer.dataProvider()
        for key, item in column_names.iteritems():
            index = provider.fieldNameIndex(key)
            if index != -1:
                value = parcel_feature.attributes()[index]
                column_names[key] = value
        landuse_invalid = False
        try:
            count = self.session.query(ClLanduseType).filter(ClLanduseType.code == column_names[column_name_landuse]).count()
            if count == 0:
                PluginUtils.show_error(self, self.tr("Shapefile error"), self.tr("The landuse is not available in the database."))
                column_names[column_name_landuse] = ""
                landuse_invalid = True

        except SQLAlchemyError, e:
            landuse_invalid = True
            PluginUtils.show_error(self, self.tr("Shapefile error"), self.tr("The landuse is not available in the database."))

        return column_names[column_name_landuse]

    def __copy_parcel_attributes(self, parcel_feature, parcel_object, layer):

        column_name_old_parcel = "old_parcel"
        column_name_geo_id = "geo_id"
        column_name_landuse = "landuse"
        column_name_documented = "documented"
        column_name_khashaa = "address_kh"
        column_name_street = "address_st"
        column_name_neighbourhood = "address_ne"

        column_names = {column_name_old_parcel: "", column_name_geo_id: "", column_name_landuse: "",
                        column_name_documented: "", column_name_khashaa: "", column_name_street: "",
                        column_name_neighbourhood: ""}

        provider = layer.dataProvider()

        for key, item in column_names.iteritems():
            index = provider.fieldNameIndex(key)
            if index != -1:
                value = parcel_feature.attributes()[index]
                column_names[key] = value
        landuse_invalid = False
        try:
            count = self.session.query(ClLanduseType).filter(ClLanduseType.code == column_names[column_name_landuse]).count()
            if count == 0:
                PluginUtils.show_error(self, self.tr("Shapefile error"), self.tr("The landuse is not available in the database."))
                column_names[column_name_landuse] = ""
                landuse_invalid = True
            else:
                if not self.change_landuse_chbox.isChecked():
                    self.landuse_code = column_names[column_name_landuse]

        except SQLAlchemyError, e:
            landuse_invalid = True
            PluginUtils.show_error(self, self.tr("Shapefile error"), self.tr("The landuse is not available in the database."))

        if landuse_invalid:
            self.apply_button.setEnabled(False)
        else:
            self.apply_button.setEnabled(True)

        old_parcel_id = 0
        geo_id = 0
        documented_area_m2 = 0
        address_khashaa = 0
        address_streetname = ''
        address_neighbourhood = ''

        if column_names[column_name_old_parcel] != None:
            old_parcel_id = column_names[column_name_old_parcel]
        if column_names[column_name_geo_id] != None:
            geo_id = column_names[column_name_geo_id]
        if column_names[column_name_documented] != None:
            documented_area_m2 = column_names[column_name_documented]
        if column_names[column_name_khashaa] != None:
            address_khashaa = column_names[column_name_khashaa]
        if column_names[column_name_street] != None:
            address_streetname = column_names[column_name_street]
        if column_names[column_name_neighbourhood] != None:
            address_neighbourhood = column_names[column_name_neighbourhood]
        parcel_object.old_parcel_id = old_parcel_id
        if geo_id != 0:
            parcel_object.geo_id = geo_id
        parcel_object.landuse = column_names[column_name_landuse]
        parcel_object.documented_area_m2 = documented_area_m2
        parcel_object.address_khashaa = address_khashaa
        parcel_object.address_streetname = address_streetname
        parcel_object.address_neighbourhood = address_neighbourhood

        return parcel_object

    def __copy_building_attributes(self, building_feature, building_object, layer):

        column_name_building_no = "building_n"
        column_name_geo_id = "geo_id"
        column_name_khashaa = "address_kh"
        column_name_street = "address_st"
        column_name_neighbourhood = "address_ne"

        column_names = {column_name_building_no: "", column_name_geo_id: "", column_name_khashaa: "", column_name_street: "", column_name_neighbourhood: ""}

        provider = layer.dataProvider()

        for key, item in column_names.iteritems():
            index = provider.fieldNameIndex(key)
            if index != -1:
                value = building_feature.attributes()[index]
                column_names[key] = value

        geo_id = 0
        building_no = 0
        address_khashaa = ''
        address_streetname = ''
        address_neighbourhood = ''
        if column_names[column_name_geo_id] != None:
            geo_id = column_names[column_name_geo_id]
        if column_names[column_name_building_no] != None:
            building_no = column_names[column_name_building_no]
        if column_names[column_name_khashaa] != None:
            address_khashaa = column_names[column_name_khashaa]
        if column_names[column_name_street] != None:
            address_streetname = column_names[column_name_street]
        if column_names[column_name_neighbourhood] != None:
            address_streetname = column_names[column_name_neighbourhood]
        building_object.geo_id = geo_id
        building_object.building_no = building_no
        building_object.address_khashaa = address_khashaa
        building_object.address_streetname = address_streetname
        building_object.address_neighbourhood = address_neighbourhood

        return building_object

    def __import_new_buildings(self, file_path):

        building_shape_layer = QgsVectorLayer(file_path, "tmp_building_shape", "ogr")

        if not building_shape_layer.isValid():
            PluginUtils.show_error(self, self.tr("Error loading layer"), self.tr("The layer is invalid."))
            return False

        if building_shape_layer.crs().postgisSrid() != 4326:
            PluginUtils.show_error(self, self.tr("Error loading layer"), self.tr("The crs of the has to be 32648."))
            return False

        iterator = building_shape_layer.getFeatures()
        count = 0

        for building in iterator:
            count += 1

            # try:
            tmp_parcel_count = self.session.query(CaTmpParcel).filter(WKTElement(building.geometry().exportToWkt(), srid=4326).ST_Contains(CaTmpParcel.geometry)).count()

            parcel_count = self.session.query(CaParcel).filter(
                WKTElement(building.geometry().exportToWkt(), srid=4326).ST_Within(CaParcel.geometry)).count()

            if tmp_parcel_count == 0 and parcel_count == 0:
                PluginUtils.show_message(self, self.tr('No parcel'), self.tr('This building no parcel.'))
                return
            if self.is_shape_parcel:
                case_id  = self.ca_maintenance_case.id

            if tmp_parcel_count > 0:
                parcel = self.session.query(CaTmpParcel).filter(WKTElement(building.geometry().exportToWkt(), srid=4326).ST_Within(CaTmpParcel.geometry)).one()
                case_id = parcel.maintenance_case
                new_building = CaTmpBuilding()
                new_building.building_id = QDateTime().currentDateTime().toString("MMddhhmmss") + str(count)
                new_building.initial_insert = None
                new_building.valid_from = PluginUtils.convert_qt_date_to_python(QDateTime().currentDateTime())
                new_building.maintenance_case = case_id
                new_building.au2 = self.working_soum
                new_building.geometry = WKTElement(building.geometry().exportToWkt(), srid=4326)
                self.__copy_building_attributes(building, new_building, building_shape_layer)
                self.session.add(new_building)

                # Add main parcel to the tree
                main_building_item = QTreeWidgetItem()
                main_building_item.setText(0, new_building.building_id)
                main_building_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/building.gif")))
                main_building_item.setData(0, Qt.UserRole, new_building.building_id)
                main_building_item.setData(0, Qt.UserRole + 1, Constants.CASE_BUILDING_IDENTIFIER)

                self.buildings_item.addChild(main_building_item)

            elif parcel_count > 0:
                parcel = self.session.query(CaParcel).filter(
                    WKTElement(building.geometry().exportToWkt(), srid=4326).ST_Within(CaParcel.geometry)).one()
                new_building = CaBuilding()
                new_building.geometry = WKTElement(building.geometry().exportToWkt(), srid=4326)
                self.session.add(new_building)

                # Add main parcel to the tree
                main_building_item = QTreeWidgetItem()
                main_building_item.setText(0, new_building.building_id)
                main_building_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/building.gif")))
                main_building_item.setData(0, Qt.UserRole, new_building.building_id)
                main_building_item.setData(0, Qt.UserRole + 1, Constants.CASE_BUILDING_IDENTIFIER)

                self.buildings_item.addChild(main_building_item)

            # except SQLAlchemyError, e:
            #     PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            #     return

        return True

    def reject(self):

        self.rollback()
        QDialog.reject(self)

    @pyqtSlot()
    def on_apply_button_clicked(self):

        # try:
        # root = self.result_twidget.invisibleRootItem()
        # self.result_twidget.topLevelItemCount()
        # child_count = root.childCount()
        #
        # parent_item = root.child(0)
        # b_count = parent_item.childCount()
        #
        # parent_item = root.child(1)
        # p_count = parent_item.childCount()

        if self.tab_index == 0:
            # if b_count > 0 and p_count > 0:
            self.ca_maintenance_case.creation_date = PluginUtils.convert_qt_date_to_python(self.start_date.date())
            self.create_savepoint()

            if self.connect_app_checkbox.isChecked():
                count = self.applications_twidget.rowCount()
                if count == 0:
                    PluginUtils.show_error(self, self.tr("Maintenance case Error"), self.tr("Select an application to create an maintenance case"))
                    return

                for i in range(self.applications_twidget.rowCount()):

                    item = self.applications_twidget.item(i, 0)

                    if item is None:
                        continue
                    app_no = item.text()
                    application_count = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).count()
                    if application_count != 0:
                        application = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).one()
                        application.maintenance_case = self.ca_maintenance_case.id

            for parcel_id in self.maintenance_parcels:
                self.create_savepoint()

                p_count = self.session.query(CaParcel).filter(CaParcel.parcel_id == parcel_id).count()

                if p_count == 1:
                    parcel = self.session.query(CaParcel).filter(CaParcel.parcel_id == parcel_id).one()
                    if parcel in self.ca_maintenance_case.parcels:
                        continue

                    soum = DatabaseUtils.working_l2_code()
                    self.ca_maintenance_case.parcels.append(parcel)
                    temp_parcel = CaTmpParcel()
                    temp_parcel.parcel_id = parcel.parcel_id
                    temp_parcel.old_parcel_id = parcel.old_parcel_id
                    temp_parcel.geo_id = parcel.geo_id
                    temp_parcel.landuse = parcel.landuse
                    temp_parcel.address_khashaa = parcel.address_khashaa
                    temp_parcel.address_streetname = parcel.address_streetname
                    temp_parcel.address_neighbourhood = parcel.address_neighbourhood
                    temp_parcel.valid_from = parcel.valid_from
                    temp_parcel.valid_till = parcel.valid_till
                    temp_parcel.documented_area_m2 = parcel.documented_area_m2
                    temp_parcel.area_m2 = parcel.area_m2
                    temp_parcel.geometry = parcel.geometry
                    temp_parcel.maintenance_case = self.ca_maintenance_case.id
                    temp_parcel.initial_insert = True
                    temp_parcel.au2 = soum

                    self.session.add(temp_parcel)

            for building_id in self.maintenance_buildings:

                self.create_savepoint()

                building = self.session.query(CaBuilding).filter(CaBuilding.building_id == building_id).one()
                if building in self.ca_maintenance_case.buildings:
                    continue
                count = self.session.query(CaTmpBuilding).filter(
                    CaTmpBuilding.building_id == building.building_id).count()
                if count == 0:
                    python_date = PluginUtils.convert_qt_date_to_python(QDateTime().currentDateTime())
                    self.ca_maintenance_case.buildings.append(building)
                    temp_building = CaTmpBuilding()

                    temp_building.building_id = building.building_id
                    temp_building.geo_id = building.geo_id
                    temp_building.valid_from = building.valid_from
                    temp_building.valid_till = building.valid_till
                    temp_building.address_streetname = building.address_streetname
                    temp_building.address_neighbourhood = building.address_neighbourhood
                    temp_building.address_khashaa = building.address_khashaa
                    temp_building.area_m2 = building.area_m2
                    temp_building.geometry = building.geometry#.ST_SetSRID(32648)
                    temp_building.maintenance_case = self.ca_maintenance_case.id
                    temp_building.au2 = soum

                    self.session.add(temp_building)

            # self.commit()
            self.__set_visible_layers()

            self.__delete_template_parcel_features()
            self.__delete_template_building_features()

            self.__start_fade_out_timer()
            self.plugin.iface.mapCanvas().refresh()

            # except SQLAlchemyError, e:
            #     self.rollback()
            #     PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            #     return
            case_none = self.session.query(CaMaintenanceCase).all()

            # for case in case_none:
            #     case_count = self.session.query(CaParcel).\
            #         outerjoin(CaMaintenanceCase.parcels).\
            #         filter(CaMaintenanceCase.id == case.id).count()
            #
            #     if case_count == 0:
            #         self.session.query(CaMaintenanceCase).\
            #             filter(CaMaintenanceCase.id == case.id).delete()
        # else:
        self.commit()

    def __set_visible_layers(self):

        root = QgsProject.instance().layerTreeRoot()
        for key in QgsMapLayerRegistry.instance().mapLayers():
            layer = QgsMapLayerRegistry.instance().mapLayers()[key]
            if layer.type() == QgsMapLayer.VectorLayer:
                uri_string = layer.dataProvider().dataSourceUri()
                uri = QgsDataSourceURI(uri_string)

                if uri.table() == 'ca_tmp_parcel_view' or uri.table() == 'ca_tmp_building_view':
                    root.findLayer( layer.id() ).setVisible(2)

    def __delete_template_parcel_features(self):

        file_path = self.parcel_shape_edit.text()
        layer = QgsVectorLayer(file_path, "tmp_parcel_shape", "ogr")
        layer.startEditing()
        for feature in layer.getFeatures():
            layer.deleteFeature(feature.id())
        layer.commitChanges()

    def __delete_template_building_features(self):

        file_path = self.building_shape_edit.text()
        layer = QgsVectorLayer(file_path, "tmp_building_shape", "ogr")
        layer.startEditing()
        for feature in layer.getFeatures():
            layer.deleteFeature(feature.id())
        layer.commitChanges()

    @pyqtSlot(QPoint)
    def on_result_twidget_customContextMenuRequested(self, point):

        if self.is_file_import:
            return

        point = self.result_twidget.viewport().mapToGlobal(point)
        self.menu.exec_(point)

    def __collect_used_codes(self, application_twidget):

        used_codes = list()
        for row in range(application_twidget.rowCount()):
            application_no = application_twidget.item(row, 0).text()
            used_codes.append(application_no)
        return used_codes

    @pyqtSlot()
    def on_add_button_clicked(self):

        used_codes = self.__collect_used_codes(self.applications_twidget)
        unused_code = ''
        for code in self.application_list:
            if code not in used_codes:
                unused_code = code
                break

        row = self.applications_twidget.rowCount()
        self.applications_twidget.insertRow(row)
        self.__add_application_row(row, -1, unused_code)

    def __add_application_row(self, row, id, app_no):

        item = QTableWidgetItem(app_no)
        item.setData(Qt.UserRole, id)
        self.applications_twidget.setItem(row, 0, item)

    @pyqtSlot()
    def on_delete_button_clicked(self):

        self.applications_twidget.removeRow(self.applications_twidget.currentRow())

    def exclude_list(self):

        return self.exclude_list

    def add_to_exclude_list(self, item):

        self.exclude_list.append(item)

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
    def on_help_button_clicked(self):

        os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/create_maintenance_case.htm")

    @pyqtSlot(int)
    def on_connect_app_checkbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.applications_twidget.setEnabled(True)
            self.add_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            self.person_id_label.setEnabled(True)
            self.app_person_id.setEnabled(True)
            self.__setup_twidgets()
        else:
            self.applications_twidget.setEnabled(False)
            self.add_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.person_id_label.setEnabled(False)
            self.app_person_id.setEnabled(False)
            self.applications_twidget.setRowCount(0)

    @pyqtSlot(str)
    def on_app_person_id_textChanged(self, text):

        value = "%" + text + "%"
        self.applications_twidget.setRowCount(0)
        try:
            applications = self.session.query(ApplicationSearch).\
                filter(ApplicationSearch.status == 1).\
                filter(ApplicationSearch.person_register.ilike(value)).all()
            count = 0
            for application in applications:
                item = QTableWidgetItem(application.app_no)
                item.setCheckState(Qt.Unchecked)
                item.setData(Qt.UserRole, application.app_no)
                self.applications_twidget.insertRow(count)
                self.applications_twidget.setItem(count, 0, item)
                count +=1
        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("Database Query Error"), self.tr("Could not execute: {0}").format(e.message))
            return

    def __setup_street_table_widget(self):

        names = [u'Нэр', u'Дугаар', u'Шийдвэрийн түвшин', u'Шийдвэрийн дугаар', u'Шийдвэрийн огноо', u'Тайлбар']
        self.street_treewidget.setHeaderHidden(False)
        self.street_treewidget.setColumnCount(len(names))
        self.street_treewidget.setHeaderLabels(names)

        self.touches_road_twidget.setAlternatingRowColors(True)
        self.touches_road_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.touches_road_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.touches_road_twidget.setSelectionMode(QTableWidget.SingleSelection)

        self.joined_road_twidget.setAlternatingRowColors(True)
        self.joined_road_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.joined_road_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.joined_road_twidget.setSelectionMode(QTableWidget.SingleSelection)

        au2 = DatabaseUtils.working_l2_code()
        au3s = self.session.query(AuLevel3).filter(AuLevel3.au2_code == au2).all()
        self.find_au3_cbox.clear()
        self.find_au3_cbox.addItem("*", -1)
        for item in au3s:
            self.find_au3_cbox.addItem(item.name, item.code)


    @pyqtSlot(QTreeWidgetItem, int)
    def __onItemDoubleClickedStreetTreewidget(self, item, col):

        id = item.data(0, Qt.UserRole)
        layer = LayerUtils.layer_by_data_source("data_address", 'st_street_line_view')
        self.__select_feature(str(id), layer)

    @pyqtSlot(QTreeWidgetItem, int)
    def __onItemClickedStreetTreewidget(self, item, col):

        id = item.data(0, Qt.UserRole)
        # print(item, col, item.text(col))
        self.__load_touches_roads(id)
        self.__load_joined_roads(id)

    def __load_touches_roads(self, id):

        self.touches_road_twidget.setRowCount(0)
        street = self.session.query(StStreet).filter_by(id=id).one()
        count = self.session.query(StRoad).filter(StRoad.street_id == id).count()
        roads = None
        if count == 0:
            if street.geometry is not None:
                roads = self.session.query(StRoad). \
                    filter(street.geometry.ST_Intersects(StRoad.line_geom)).all()
        else:
            roads = self.session.query(StRoad).\
                filter(StRoad.line_geom.ST_Touches(StStreetLineView.geometry)).\
                filter(StStreetLineView.id == id).all()

        if roads is None:
            return
        for value in roads:
            count = self.touches_road_twidget.rowCount()
            self.touches_road_twidget.insertRow(count)
            name = u''
            if value.name:
                name = value.name
            item = QTableWidgetItem(unicode(name))
            item.setData(Qt.UserRole, value.id)
            self.touches_road_twidget.setItem(count, 0, item)

            length = ''
            if value.length:
                length = value.length
            item = QTableWidgetItem(str(length))
            item.setData(Qt.UserRole, value.length)
            self.touches_road_twidget.setItem(count, 1, item)

            if value.road_type_id_ref:
                road_type = value.road_type_id_ref
                item = QTableWidgetItem(unicode(road_type.description))
                item.setData(Qt.UserRole, road_type.code)
                self.touches_road_twidget.setItem(count, 2, item)

            item = QTableWidgetItem()
            item.setCheckState(True)
            if value.is_active == False:
                item.setCheckState(False)
            item.setData(Qt.UserRole, value.is_active)
            self.touches_road_twidget.setItem(count, 3, item)

    def __load_joined_roads(self, id):

        self.joined_road_twidget.setRowCount(0)
        roads = self.session.query(StRoad).filter(StRoad.street_id == id).all()
        for value in roads:
            count = self.joined_road_twidget.rowCount()
            self.joined_road_twidget.insertRow(count)
            name = u''
            if value.name:
                name = value.name
            item = QTableWidgetItem(unicode(name))
            item.setData(Qt.UserRole, value.id)
            self.joined_road_twidget.setItem(count, 0, item)

            length = ''
            if value.length:
                length = value.length
            item = QTableWidgetItem(str(length))
            item.setData(Qt.UserRole, value.length)
            self.joined_road_twidget.setItem(count, 1, item)

            if value.road_type_id_ref:
                road_type = value.road_type_id_ref
                item = QTableWidgetItem(unicode(road_type.description))
                item.setData(Qt.UserRole, road_type.code)
                self.joined_road_twidget.setItem(count, 2, item)

            item = QTableWidgetItem()
            item.setCheckState(True)
            if value.is_active == False:
                item.setCheckState(False)
            item.setData(Qt.UserRole, value.is_active)
            self.joined_road_twidget.setItem(count, 3, item)

    @pyqtSlot()
    def on_street_find_button_clicked(self):

        self.street_treewidget.clear()

        tree = self.street_treewidget

        au2 = DatabaseUtils.working_l2_code()
        # values = self.session.query(StStreet).\
        #     filter(AuLevel2.geometry.ST_Intersects(StStreet.geometry)).\
        #     filter(AuLevel2.code == au2).\
        #     filter(StStreet.parent_id == None).\
        #     order_by(StStreet.name, StStreet.code)

        values = self.session.query(StStreet). \
            filter(StStreet.au2 == au2). \
            filter(StStreet.parent_id == None). \
            order_by(StStreet.name, StStreet.code)

        filter_is_set = False
        if self.find_street_name_edit.text():
            filter_is_set = True
            find_value = "%" + self.find_street_name_edit.text() + "%"
            values = values.filter(StStreet.name.ilike(find_value))

        if not self.find_au3_cbox.itemData(self.find_au3_cbox.currentIndex()) == -1:
            filter_is_set = True
            au3 = self.find_au3_cbox.itemData(self.find_au3_cbox.currentIndex())
            values = values.filter(StStreet.au3 == au3)

        for value in values.all():
            parent = QTreeWidgetItem(tree)
            parent.setText(0, unicode(value.name))
            parent.setToolTip(0, unicode(value.name))
            parent.setData(0, Qt.UserRole, value.id)

            if value.decision_level_id_ref:
                d_level = value.decision_level_id_ref
                parent.setText(2, unicode(d_level.description))
                parent.setToolTip(2, unicode(d_level.description))
                parent.setData(2, Qt.UserRole, d_level.plan_decision_level_id)

            if value.decision_no:
                parent.setText(3, unicode(value.decision_no))
                parent.setToolTip(3, unicode(value.decision_no))
                parent.setData(3, Qt.UserRole, value.decision_no)

            if value.decision_date:
                parent.setText(4, unicode(value.decision_date))
                parent.setToolTip(4, unicode(value.decision_date))
                parent.setData(4, Qt.UserRole, value.decision_date)

            if value.decision_date:
                parent.setText(5, unicode(value.description))
                parent.setToolTip(5, unicode(value.description))
                parent.setData(5, Qt.UserRole, value.description)

            values_sub = self.session.query(StStreet).filter(StStreet.au2 == au2). \
                filter(StStreet.parent_id == value.id).\
                order_by(StStreet.code).all()
            for value_sub in values_sub:
                child = QTreeWidgetItem(parent)
                child.setText(0, unicode(value_sub.name))
                child.setToolTip(0, unicode(value_sub.name))
                child.setData(0, Qt.UserRole, value_sub.id)

                child.setText(1, unicode(value_sub.code))
                child.setToolTip(1, unicode(value_sub.code))
                child.setData(1, Qt.UserRole, value_sub.code)

                if value_sub.description:
                    child.setText(5, unicode(value_sub.description))
                    child.setToolTip(5, unicode(value_sub.description))
                    child.setData(5, Qt.UserRole, value_sub.description)

        tree.show()

        self.street_treewidget.resizeColumnToContents(0)
        self.street_treewidget.resizeColumnToContents(1)
        self.street_treewidget.resizeColumnToContents(2)
        self.street_treewidget.resizeColumnToContents(3)
        self.street_treewidget.resizeColumnToContents(4)
        self.street_treewidget.resizeColumnToContents(5)
        # self.street_treewidget.resizeColumnToContents(6)

    @pyqtSlot(QTableWidgetItem)
    def on_touches_road_twidget_itemDoubleClicked(self, item):

        selected_row = self.touches_road_twidget.currentRow()
        id = self.touches_road_twidget.item(selected_row, 0).data(Qt.UserRole)

        layer = LayerUtils.layer_by_data_source("data_address", 'st_road_line_view')
        self.__select_feature(str(id), layer)

    @pyqtSlot(QTableWidgetItem)
    def on_joined_road_twidget_itemDoubleClicked(self, item):

        selected_row = self.joined_road_twidget.currentRow()
        id = self.joined_road_twidget.item(selected_row, 0).data(Qt.UserRole)

        layer = LayerUtils.layer_by_data_source("data_address", 'st_road_line_view')
        self.__select_feature(str(id), layer)

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

    @pyqtSlot()
    def on_remove_road_button_clicked(self):

        current_item = self.street_treewidget.selectedItems()[0]
        street_id = current_item.data(0, Qt.UserRole)

        selected_row = self.joined_road_twidget.currentRow()
        id = self.joined_road_twidget.item(selected_row, 0).data(Qt.UserRole)

        value = self.session.query(StRoad).filter_by(id=id).one()
        value.street_id = None

        self.joined_road_twidget.removeRow(selected_row)

    @pyqtSlot()
    def on_join_road_button_clicked(self):

        selected_row = self.touches_road_twidget.currentRow()
        id = self.touches_road_twidget.item(selected_row, 0).data(Qt.UserRole)

        self.__add_road_to_street(id)

    def __add_road_to_street(self, road_id):

        if len(self.street_treewidget.selectedItems()) == 0:
            PluginUtils.show_message(self, u'Анхааруулга', u'Гудамж сонгоогүй байна.')
            return

        current_item = self.street_treewidget.selectedItems()[0]
        street_id = current_item.data(0, Qt.UserRole)

        id = road_id
        count = self.session.query(StRoad). \
            filter(StRoad.street_id == street_id). \
            filter(StRoad.id == id).count()
        if count > 0:
            PluginUtils.show_message(self, u'Анхааруулга', u'Энэ зам гудамжинд бүртгэгдсэн байна.')
            return

        count = self.session.query(StRoad). \
            filter(StRoad.street_id != street_id). \
            filter(StRoad.id == id).count()
        if count > 0:
            PluginUtils.show_message(self, u'Анхааруулга', u'Энэ зам өөр гудамжинд бүртгэгдсэн байна.')
            return

        value = self.session.query(StRoad).filter_by(id=id).one()
        count = self.joined_road_twidget.rowCount()
        self.joined_road_twidget.insertRow(count)
        name = u''
        if value.name:
            name = value.name
        item = QTableWidgetItem(unicode(name))
        item.setData(Qt.UserRole, value.id)
        self.joined_road_twidget.setItem(count, 0, item)

        length = ''
        if value.length:
            length = value.length
        item = QTableWidgetItem(str(length))
        item.setData(Qt.UserRole, value.length)
        self.joined_road_twidget.setItem(count, 1, item)

        if value.road_type_id_ref:
            road_type = value.road_type_id_ref
            item = QTableWidgetItem(unicode(road_type.description))
            item.setData(Qt.UserRole, road_type.code)
            self.joined_road_twidget.setItem(count, 2, item)

        item = QTableWidgetItem()
        item.setCheckState(True)
        if value.is_active == False:
            item.setCheckState(False)
        item.setData(Qt.UserRole, value.is_active)
        self.joined_road_twidget.setItem(count, 3, item)

        value.street_id = street_id

    @pyqtSlot()
    def on_select_road_button_clicked(self):

        parcelLayer = LayerUtils.layer_by_data_source("data_address", "st_road_line_view")
        select_feature = parcelLayer.selectedFeatures()

        for feature in select_feature:
            attr = feature.attributes()
            id = attr[0]

            self.__add_road_to_street(id)

    @pyqtSlot()
    def on_open_landuse_parcel_file_button_clicked(self):


        default_path = self.__default_path()

        file_dialog = QFileDialog()
        file_dialog.setModal(True)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setFilter(self.tr("Shapefiles (*.shp)"))
        file_dialog.setDirectory(default_path)

        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            file_path = QFileInfo(selected_file).filePath()
            self.file_path = file_path
            self.landuse_parcel_shape_edit.clear()
            self.landuse_parcel_shape_edit.setText(file_path)
            self.__import_landuse_parcels(file_path)
            self.open_landuse_parcel_file_button.setEnabled(False)

        self.change_shp_landuse_type_cbox.setCurrentIndex(self.change_shp_landuse_type_cbox.findData(self.landuse_code))

    def __import_landuse_parcels(self, file_path):

        self.result_landuse_twidget.clear()
        self.__result_twidget_setup()
        self.session.close()
        self.session = SessionHandler().session_instance()
        parcel_shape_layer = QgsVectorLayer(file_path, "tmp_landuse_parcel_shape", "ogr")

        if not parcel_shape_layer.isValid():
            PluginUtils.show_error(self,  self.tr("Error loading layer"), self.tr("The layer is invalid."))
            return

        if parcel_shape_layer.crs().postgisSrid() != 4326:
            PluginUtils.show_error(self, self.tr("Error loading layer"),
                                   self.tr("The crs of the layer has to be 4326."))
            return

        iterator = parcel_shape_layer.getFeatures()
        provider = parcel_shape_layer.dataProvider()
        feature_count = parcel_shape_layer.featureCount()
        self.main_load_pbar.setVisible(True)
        self.main_load_pbar.setMinimum(1)
        self.main_load_pbar.setValue(0)

        updateMap = {}
        count = 0
        approved_count = 0
        refused_count = 0

        self.main_load_pbar.setMaximum(feature_count)
        for parcel in iterator:
            feature_id = parcel.id()
            count += 1
            header = str(count)
            landuse = self.__get_attribute(parcel, parcel_shape_layer)[0]
            if self.change_landuse_chbox.isChecked():
                header =  header + ':' + self.change_shp_landuse_type_cbox.currentText()
                landuse_type_code = self.change_shp_landuse_type_cbox.itemData(
                    self.change_shp_landuse_type_cbox.currentIndex())
                self.landuse_code = landuse_type_code
                ###
                parcel_shape_layer.startEditing()
                fieldIdx = parcel.fields().indexFromName('landuse')
                updateMap[parcel.id()] = {fieldIdx: landuse_type_code}
                provider.changeAttributeValues(updateMap)
                parcel_shape_layer.commitChanges()
                self.plugin.iface.vectorLayerTools().stopEditing(parcel_shape_layer)
                self.plugin.iface.mapCanvas().refresh()
                ###
            if landuse:
                header = header + ':' + '(' + str(landuse.code) + ')' + unicode(landuse.description)

            parcel_geometry = WKTElement(parcel.geometry().exportToWkt(), srid=4326)

            validaty_result = self.__validaty_of_new_parcel(parcel, parcel_shape_layer, feature_id)

            if validaty_result[0]:
                landuse = self.__get_attribute(parcel, parcel_shape_layer)[0]
                # header = header + ':' + '(' + str(landuse.code) + ')' + unicode(landuse.description)

                new_parcel = CaTmpLanduseTypeTbl()
                new_parcel.is_insert_cadastre = False
                new_parcel.is_active = True
                new_parcel.geometry = parcel_geometry

                new_parcel.created_by = DatabaseUtils.current_sd_user().user_id
                new_parcel.updated_by = DatabaseUtils.current_sd_user().user_id
                new_parcel.created_at = date.today()
                new_parcel.updated_at = date.today()
                new_parcel = self.__copy_parcel_attributes(parcel, new_parcel, parcel_shape_layer)
                # if self.landuse_code:
                landuse_type = self.session.query(ClLanduseType).filter(ClLanduseType.code == self.landuse_code).one()
                landuse_code1 = landuse_type.code1
                landuse_code2 = landuse_type.code2
                new_parcel.landuse_level1 = landuse_code1
                new_parcel.landuse_level2 = landuse_code2

                self.__save_maintenance_case_parcel(self.landuse_code)

                case_id = self.landuse_maintenance_cbox.itemData(self.landuse_maintenance_cbox.currentIndex())
                new_parcel.case_id = case_id
                self.session.add(new_parcel)

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

            value_p = self.main_load_pbar.value() + 1
            self.main_load_pbar.setValue(value_p)

        self.approved_item.setText(0, self.tr("Approved") + ' (' + str(approved_count) + ')')
        self.refused_item.setText(0, self.tr("Refused") + ' (' + str(refused_count) + ')')

    def __result_twidget_setup(self):

        self.result_landuse_twidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.result_landuse_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.result_landuse_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.result_landuse_twidget.setContextMenuPolicy(Qt.CustomContextMenu)

        self.case_parcels_treewidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.case_parcels_treewidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.case_parcels_treewidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.case_parcels_treewidget.setContextMenuPolicy(Qt.CustomContextMenu)

        self.approved_item = QTreeWidgetItem()
        self.approved_item.setExpanded(True)
        self.approved_item.setText(0, u"Зөрчилгүй")

        self.refused_item = QTreeWidgetItem()
        self.refused_item.setExpanded(True)
        self.refused_item.setText(0, u"Зөрчилтэй")

        self.result_landuse_twidget.addTopLevelItem(self.approved_item)
        self.result_landuse_twidget.addTopLevelItem(self.refused_item)

        self.case_parcel_tabwidget.currentChanged.connect(self.__case_tab_widget_onChange)
        self.case_parcels_treewidget.itemChanged.connect(self.__itemCaseParcelsCheckChanged)
        self.case_parcels = []

        self.overlap_parcels_twidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.overlap_parcels_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.overlap_parcels_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.overlap_parcels_twidget.setSortingEnabled(True)

    def __itemCaseParcelsCheckChanged(self, item, column):

        self.main_load_pbar.setVisible(True)
        self.main_load_pbar.setMinimum(1)
        self.main_load_pbar.setValue(0)

        if item.checkState(column) == QtCore.Qt.Checked:
            code = item.data(0, Qt.UserRole)
            if code not in self.case_parcels:
                self.case_parcels.append(code)
                # if self.settings_tab_widget.currentIndex() == 0:
                #     self.__settings_add_save(code)
                # if self.settings_tab_widget.currentIndex() == 1:
                #     self.__zone_relation_save(code)
        elif item.checkState(column) == QtCore.Qt.Unchecked:
            code = item.data(0, Qt.UserRole)
            if code in self.case_parcels:
                self.case_parcels.remove(code)
                # if self.settings_tab_widget.currentIndex() == 0:
                #     self.__settings_remove_delete(code)
                # if self.settings_tab_widget.currentIndex() == 1:
                #     self.__zone_relation_delete(code)

    @pyqtSlot()
    def on_result_landuse_twidget_itemSelectionChanged(self):

        self.overlap_parcels_twidget.setVisible(False)
        self.message_txt_edit.setVisible(True)

        if len(self.result_landuse_twidget.selectedItems()) > 0:
            current_item = self.result_landuse_twidget.selectedItems()[0]
            object_type = current_item.data(0, Qt.UserRole + 1)
            object_id = current_item.data(0, Qt.UserRole)

            if object_type == REFUSED:
                # self.message_label.setStyleSheet("QLabel {color: rgb(255,0,0);}")
                # self.message_label.setText(self.error_dic[object_id])
                self.message_txt_edit.setPlainText(self.error_dic[object_id])
            else:
                # self.message_label.setStyleSheet("QLabel {color: rgb(0,71,31);}")
                # self.message_label.setText(current_item.text(0))
                self.message_txt_edit.setPlainText(current_item.text(0))

    def __setup_landuse_combobox(self):

        self.change_shp_landuse_type_cbox.clear()
        cl_landusetype = self.session.query(ClLanduseType).order_by(ClLanduseType.code.asc()).all()
        # self.change_shp_landuse_type_cbox.addItem("*", -1)
        if cl_landusetype is not None:
            for landuse in cl_landusetype:
                if len(str(landuse.code)) == 4:
                    self.change_shp_landuse_type_cbox.addItem(str(landuse.code) + ':' + landuse.description, landuse.code)

    def __validaty_of_new_parcel(self, parcel, parcel_shape_layer, id):

        valid = True
        error_message = u'Гарсан зөрчил'

        if not parcel.geometry():
            message =  u'Геометр алдаатай байна!!!'
            error_message = error_message + "\n" + message
            valid = False

        g = parcel.geometry()
        if not g.isGeosValid():
            message = u'Геометр алдаатай байна!!!'
            error_message = error_message + "\n" + message
            valid = False
        if g.isMultipart():
            message = u'Мулти Полигон төрөлтэй геометр утга оруулах боломжгүй!!!'
            error_message = error_message + "\n" + message
            valid = False

        parcel_geometry = WKTElement(parcel.geometry().exportToWkt(), srid=4326)
        temp_overlaps_count = self.session.query(CaTmpLanduseTypeTbl). \
            filter((parcel_geometry).ST_Overlaps(CaTmpLanduseTypeTbl.geometry)). \
            filter(or_(CaTmpLanduseTypeTbl.valid_till == None, CaTmpLanduseTypeTbl.valid_till == 'infinity')).count()

        temp_covers_count = self.session.query(CaTmpLanduseTypeTbl). \
            filter((parcel_geometry).ST_Covers(CaTmpLanduseTypeTbl.geometry)). \
            filter(or_(CaTmpLanduseTypeTbl.valid_till == None, CaTmpLanduseTypeTbl.valid_till == 'infinity')).count()

        if temp_overlaps_count > 0 or temp_covers_count > 0:
            message = u'ГНС-н ажлын давхаргад байгаа нэгж талбартай давхардаж байна. Та давхардлыг арилган дахин оруулна уу!!!'
            error_message = error_message + "\n" + message
            valid = False

        landuse = self.__get_attribute(parcel, parcel_shape_layer)[0]

        if landuse is None:
            message = u'ГНС-н ангилал буруу байна!!!'
            error_message = error_message + "\n" + message
            valid = False
        else:
            if not self.change_landuse_chbox.isChecked():
                self.landuse_code = landuse.code
            landuse_type_code = landuse.code
            case_landuse_count = self.session.query(StWorkflowStatusLanduse). \
                filter(StWorkflowStatusLanduse.next_landuse == landuse_type_code).count()
            if case_landuse_count == 0:
                message = (u'/{0}/ ГНС-н ангилалд шилжилт хөдөлгөөний тохиргоо хийгээгүй байна!').format(
                                           landuse_type_code)
                error_message = error_message + "\n" + message
                valid = False

        if not valid:
            self.error_dic[id] = error_message

        return valid, error_message

    @pyqtSlot(int)
    def on_change_landuse_chbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.change_shp_landuse_type_cbox.setEnabled(True)

    def __save_maintenance_case_parcel(self, landuse_type_code):

        # case_landuse_count = self.session.query(StWorkflowStatusLanduse). \
        #     filter(StWorkflowStatusLanduse.next_landuse == landuse_type_code).count()
        # if case_landuse_count == 0:
        #     PluginUtils.show_error(self, u'Анхааруулга',
        #                            (u'/{0}/ ГНС-н ангилалд шилжилт хөдөлгөөний тохиргоо хийгээгүй байна!').format(
        #                                landuse_type_code))
        # else:
        new_case_id = None
        is_draft_status = self.session.query(ClLanduseMovementStatus). \
            filter(ClLanduseMovementStatus.is_draft == True).first()

        case_count = self.session.query(CaLanduseMaintenanceCase). \
            join(StWorkflow, CaLanduseMaintenanceCase.workflow_id == StWorkflow.id). \
            filter(StWorkflowStatusLanduse.workflow_id == StWorkflow.id). \
            filter(StWorkflowStatusLanduse.next_landuse == landuse_type_code). \
            filter(CaLanduseMaintenanceCase.status_id < is_draft_status.code).count()

        if case_count == 0:
            message_box = QMessageBox()
            message_box.setWindowTitle(u'ГНС-н үндсэн ангилалын шилжилт хөдөлгөөн')
            message_box.setWindowFlags(message_box.windowFlags() | Qt.WindowTitleHint)
            message_box.setText(
                u'Өөрчлөлтйн бүртгэл үүсээгүй байна. Шинээр өөрчлөлтийн бүртгэл үүсгэх бол ТИЙМ товчийг дарна уу!')

            yes_button = message_box.addButton(self.tr('Yes'), QMessageBox.ActionRole)

            message_box.addButton(self.tr('No'), QMessageBox.ActionRole)
            message_box.exec_()

            if message_box.clickedButton() == yes_button:
                workflows = []
                values = self.session.query(StWorkflow).join(StWorkflowStatusLanduse,
                                                             StWorkflow.id == StWorkflowStatusLanduse.workflow_id). \
                    filter(StWorkflowStatusLanduse.next_landuse == landuse_type_code).all()
                for value in values:
                    desc = str(value.code) + ':-' + value.name
                    workflows.append(desc)

                item, ok = QInputDialog.getItem(self, "select input dialog",
                                                "list of plan zones", workflows, 0, False)

                if ok:
                    workflow_code, workflow_desc = item.split(':-')

                    workflow = self.session.query(StWorkflow).filter(StWorkflow.code == workflow_code).first()
                    status = self.session.query(ClLanduseMovementStatus).order_by(
                        ClLanduseMovementStatus.code.asc()).first()

                    new_case = CaLanduseMaintenanceCase()
                    new_case.workflow_id = workflow.id
                    new_case.landuse = landuse_type_code
                    new_case.au2 = self.working_soum
                    new_case.status_id = status.code
                    new_case.created_by = DatabaseUtils.current_sd_user().user_id
                    new_case.updated_by = DatabaseUtils.current_sd_user().user_id
                    new_case.creation_date = date.today()
                    new_case.created_at = date.today()
                    new_case.updated_at = date.today()
                    self.session.add(new_case)
                    self.session.flush()
                    new_case_id = new_case.id

                    status_id = 1
                    status = self.session.query(ClLanduseMovementStatus).filter(ClLanduseMovementStatus.code == status_id).one()
                    status_new = CaLanduseMaintenanceStatus()
                    status_new.case_id = new_case_id
                    status_new.status_date = self.status_date_date.dateTime().toString(
                        Constants.DATABASE_DATETIME_FORMAT)
                    status_new.officer_in_charge_ref = DatabaseUtils.current_sd_user()
                    status_new.officer_in_charge = DatabaseUtils.current_sd_user().user_id
                    status_new.next_officer_in_charge = DatabaseUtils.current_sd_user().user_id
                    status_new.next_officer_in_charge_ref = DatabaseUtils.current_sd_user()
                    status_new.status_id = status_id
                    status_new.status_ref = status
                    self.session.add(status_new)
                    self.session.flush()
                    self.__case_status(status_new)

            else:
                return

        cases = self.session.query(CaLanduseMaintenanceCase). \
            join(StWorkflow, CaLanduseMaintenanceCase.workflow_id == StWorkflow.id). \
            filter(StWorkflowStatusLanduse.workflow_id == StWorkflow.id). \
            filter(StWorkflowStatusLanduse.next_landuse == landuse_type_code). \
            filter(CaLanduseMaintenanceCase.status_id < is_draft_status.code).all()

        self.landuse_maintenance_cbox.clear()
        for case in cases:
            self.landuse_maintenance_cbox.addItem(str(case.landuse) + ':' + str(case.creation_date), case.id)
        if new_case_id:
            self.landuse_maintenance_cbox.setCurrentIndex(self.landuse_maintenance_cbox.findData(new_case_id))

    @pyqtSlot(int)
    def on_change_shp_landuse_type_cbox_currentIndexChanged(self, index):

        self.change_shp_landuse_type_cbox.setToolTip(self.change_shp_landuse_type_cbox.currentText())

        landuse_type_code = self.change_shp_landuse_type_cbox.itemData(self.change_shp_landuse_type_cbox.currentIndex())

        if self.change_landuse_chbox.isChecked():
            parcel_shape_layer = QgsVectorLayer(self.file_path, "tmp_landuse_parcel_shape", "ogr")
            if parcel_shape_layer.isValid():
                self.__import_landuse_parcels(self.file_path)
            # self.__save_maintenance_case_parcel(landuse_type_code)
            else:
                self.landuse_maintenance_cbox.clear()

                is_draft_status = self.session.query(ClLanduseMovementStatus). \
                    filter(ClLanduseMovementStatus.is_draft == True).first()

                cases = self.session.query(CaLanduseMaintenanceCase). \
                    join(StWorkflow, CaLanduseMaintenanceCase.workflow_id == StWorkflow.id). \
                    filter(StWorkflowStatusLanduse.workflow_id == StWorkflow.id). \
                    filter(StWorkflowStatusLanduse.next_landuse == landuse_type_code). \
                    filter(CaLanduseMaintenanceCase.status_id < is_draft_status.code).all()
                for case in cases:
                    self.landuse_maintenance_cbox.addItem(str(case.landuse) + ':' + str(case.creation_date), case.id)

    @pyqtSlot(int)
    def on_landuse_maintenance_cbox_currentIndexChanged(self, index):

        case_id = self.landuse_maintenance_cbox.itemData(self.landuse_maintenance_cbox.currentIndex())

        if self.session.query(CaLanduseMaintenanceCase).filter(CaLanduseMaintenanceCase.id == case_id).count() == 1:

            case = self.session.query(CaLanduseMaintenanceCase).filter(CaLanduseMaintenanceCase.id == case_id).one()
            workflow = self.session.query(StWorkflow).filter(StWorkflow.id == case.workflow_id).one()

            self.workflow_cbox.clear()
            self.workflow_cbox.addItem(workflow.name, workflow.id)
            self.__case_parcels_mapping(case_id)
            values = self.session.query(CaLanduseMaintenanceStatus).filter(
                CaLanduseMaintenanceStatus.case_id == case_id).all()
            print len(values)
            if len(values) == 0:
                status_id = 1
                status = self.session.query(ClLanduseMovementStatus).filter(
                    ClLanduseMovementStatus.code == status_id).one()
                status_new = CaLanduseMaintenanceStatus()
                status_new.case_id = case_id
                status_new.status_date = self.status_date_date.dateTime().toString(
                    Constants.DATABASE_DATETIME_FORMAT)
                status_new.officer_in_charge_ref = DatabaseUtils.current_sd_user()
                status_new.officer_in_charge = DatabaseUtils.current_sd_user().user_id
                status_new.next_officer_in_charge = DatabaseUtils.current_sd_user().user_id
                status_new.next_officer_in_charge_ref = DatabaseUtils.current_sd_user()
                status_new.status_id = status_id
                status_new.status_ref = status
                self.session.add(status_new)
                self.session.flush()
            self.movement_status_twidget.setRowCount(0)
            values = self.session.query(CaLanduseMaintenanceStatus).filter(
                CaLanduseMaintenanceStatus.case_id == case_id).all()
            for value in values:
                self.__case_status(value)

    def __get_attribute(self, parcel_feature, layer):

        column_name_landuse = "landuse"

        column_names = {column_name_landuse: ""}

        provider = layer.dataProvider()
        for key, item in column_names.iteritems():
            index = provider.fieldNameIndex(key)
            if index != -1:
                value = parcel_feature.attributes()[index]
                column_names[key] = value


        if not self.change_landuse_chbox.isChecked():
            self.landuse_code = column_names[column_name_landuse]

        landuse = None
        if self.landuse_code:
            count = self.session.query(ClLanduseType).filter(ClLanduseType.code == self.landuse_code).count()
            if count == 1:
                landuse = self.session.query(ClLanduseType).filter(ClLanduseType.code == self.landuse_code).one()

        return landuse,

    @pyqtSlot(QPoint)
    def on_result_landuse_twidget_customContextMenuRequested(self, point):

        # if self.is_file_import:
        #     return

        point = self.result_landuse_twidget.viewport().mapToGlobal(point)
        self.new_menu.exec_(point)

    @pyqtSlot(QPoint)
    def on_case_parcels_treewidget_customContextMenuRequested(self, point):

        # if self.is_file_import:
        #     return

        point = self.case_parcels_treewidget.viewport().mapToGlobal(point)
        self.landuse_case_menu.exec_(point)

    @pyqtSlot()
    def new_zoom_to_selected_clicked(self):

        selected_item = self.result_landuse_twidget.selectedItems()[0]

        file_path = self.landuse_parcel_shape_edit.text()

        if selected_item is None:
            return

        parcel_shape_layer = QgsVectorLayer(file_path, "tmp_parcel_shape", "ogr")

        feature_id = self.result_landuse_twidget.currentItem().data(0, Qt.UserRole + 2)

        parcel_shape_layer.select(feature_id)
        self.plugin.iface.mapCanvas().zoomToSelected(parcel_shape_layer)

    @pyqtSlot()
    def landsue_case_zoom_to_selected_clicked(self):

        selected_item = self.case_parcels_treewidget.selectedItems()[0]

        if selected_item is None:
            return

        layer = LayerUtils.layer_by_data_source("data_landuse", 'ca_tmp_landuse_type')

        if len(self.case_parcels_treewidget.selectedItems()) > 0:
            current_item = self.case_parcels_treewidget.selectedItems()[0]

            code = current_item.data(0, Qt.UserRole)

            self.__select_landuse_feature(str(code), layer)

    def __select_landuse_feature(self, parcel_id, layer):

        expression = " parcel_id = \'" + parcel_id + "\'"
        request = QgsFeatureRequest()
        request.setFilterExpression(expression)
        feature_ids = []
        if layer:
            iterator = layer.getFeatures(request)

            for feature in iterator:
                feature_ids.append(feature.id())
            # if len(feature_ids) == 0:
                # self.error_label.setText(self.tr("No parcel assigned"))

            layer.setSelectedFeatures(feature_ids)
            self.plugin.iface.mapCanvas().zoomToSelected(layer)

    def __case_tab_widget_onChange(self, index):

        is_change = False
        if index:
            if index == 1:
                case_id = self.landuse_maintenance_cbox.itemData(self.landuse_maintenance_cbox.currentIndex())
                self.__case_parcels_mapping(case_id)

    def __case_parcels_mapping(self, case_id):

        if not case_id:
            return
        self.case_parcels_treewidget.clear()
        tree = self.case_parcels_treewidget

        landuse_types = self.session.query(CaTmpLanduseTypeTbl.landuse).\
            filter(CaTmpLanduseTypeTbl.case_id == case_id).group_by(CaTmpLanduseTypeTbl.landuse).all()

        for parent_type in landuse_types:
            parent_type = parent_type[0]
            landuse = self.session.query(ClLanduseType).filter(ClLanduseType.code == parent_type).one()
            parent = QTreeWidgetItem(tree)
            parent.setText(0, str(landuse.code) + ': ' + unicode(landuse.description))
            parent.setToolTip(0, str(landuse.code) + ': ' + unicode(landuse.description))
            parent.setData(0, Qt.UserRole, parent_type)
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            landuse_parcels = self.session.query(CaTmpLanduseTypeTbl).\
                filter(CaTmpLanduseTypeTbl.case_id == case_id).\
                filter(CaTmpLanduseTypeTbl.landuse == parent_type).all()

            for sub_type in landuse_parcels:
                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, str(sub_type.parcel_id) + ': ' + str(landuse.code) + ': ' + unicode(landuse.description))
                child.setToolTip(0, str(sub_type.parcel_id) + ': ' + str(landuse.code) + ': ' + unicode(landuse.description))
                child.setData(0, Qt.UserRole, sub_type.parcel_id)
                child.setCheckState(0, Qt.Unchecked)

        self.case_parcels_treewidget.itemChanged.connect(self.__itemCaseParcelsCheckChanged)
        tree.show()

    @pyqtSlot()
    def on_case_parcels_treewidget_itemSelectionChanged(self):

        self.message_txt_edit.setVisible(False)
        self.overlap_parcels_twidget.setVisible(True)

        self.overlap_parcels_twidget.setRowCount(0)

        if len(self.case_parcels_treewidget.selectedItems()) > 0:
            current_item = self.case_parcels_treewidget.selectedItems()[0]

            code = current_item.data(0, Qt.UserRole)

            sql = "select * from base.landuse_temp_parcel_overlaps(" + str(code) + ");"

            result = self.session.execute(sql)
            for item_row in result:
                parcel_id = item_row[1]
                overlaps_area_m2 = item_row[2]
                landuse_code = item_row[3]

                landuse = self.session.query(ClLanduseType).filter(ClLanduseType.code == landuse_code).one()
                row = self.overlap_parcels_twidget.rowCount()
                self.overlap_parcels_twidget.insertRow(row)

                item = QTableWidgetItem()
                item.setText(str(parcel_id))
                item.setData(Qt.UserRole, parcel_id)
                self.overlap_parcels_twidget.setItem(row, 0, item)

                item = QTableWidgetItem()
                item.setText(str(overlaps_area_m2))
                item.setData(Qt.UserRole, overlaps_area_m2)
                self.overlap_parcels_twidget.setItem(row, 1, item)

                item = QTableWidgetItem()
                item.setText(str(landuse.code) + ':' + unicode(landuse.description))
                item.setToolTip(str(landuse.code) + ':' + unicode(landuse.description))
                item.setData(Qt.UserRole, landuse.code)
                self.overlap_parcels_twidget.setItem(row, 2, item)

            self.overlap_parcels_twidget.resizeColumnsToContents()

    @pyqtSlot(QTableWidgetItem)
    def on_overlap_parcels_twidget_itemDoubleClicked(self, item):

        soum = DatabaseUtils.working_l2_code()
        if not soum:
            PluginUtils.show_message(self, self.tr("Connection Error"), self.tr("Please connect to database!!!"))
            return
        layer = LayerUtils.layer_by_data_source("data_landuse", 'ca_landuse_type')

        selected_row = self.overlap_parcels_twidget.currentRow()
        parcel_id = self.overlap_parcels_twidget.item(selected_row, 0).data(Qt.UserRole)
        column_name = 'parcel_id'

        self.__select_feature_column(column_name, str(parcel_id), layer)

    def __select_feature_column(self, column_name, id, layer):

        expression = column_name +  "=\'" + id + "\'"
        request = QgsFeatureRequest()
        request.setFilterExpression(expression)
        feature_ids = []
        if layer:
            iterator = layer.getFeatures(request)

            for feature in iterator:
                feature_ids.append(feature.id())

            layer.setSelectedFeatures(feature_ids)
            self.plugin.iface.mapCanvas().zoomToSelected(layer)

    @pyqtSlot(int)
    def on_workflow_cbox_currentIndexChanged(self, index):

        workflow_id = self.workflow_cbox.itemData(self.workflow_cbox.currentIndex())
        statuses = self.session.query(ClLanduseMovementStatus).\
            join(StWorkflowStatus, ClLanduseMovementStatus.code == StWorkflowStatus.next_status_id).\
            filter(StWorkflowStatus.workflow_id == workflow_id).all()
        self.status_date_date.setDate(QDate().currentDate())
        self.status_cbox.clear()
        self.next_officer_in_charge_cbox.clear()

        for value in statuses:
            self.status_cbox.addItem(value.description, value.code)

        set_roles = self.session.query(SetRole). \
            filter(SetRole.working_au_level2 == self.working_soum). \
            filter(SetRole.is_active == True).all()

        for setRole in set_roles:
            l2_code_list = setRole.restriction_au_level2.split(',')
            if self.working_soum in l2_code_list:
                sd_user = self.session.query(SdUser).filter(SdUser.gis_user_real == setRole.user_name_real).first()
                if sd_user:
                    lastname = sd_user.lastname
                    firstname = sd_user.firstname
                    self.next_officer_in_charge_cbox.addItem(lastname + ", " + firstname, sd_user.user_id)

    def __case_status(self, value):

        # values = self.session.query(CaLanduseMaintenanceStatus).filter(CaLanduseMaintenanceStatus.case_id == case_id).all()
        # for value in values:
        status_count = self.session.query(ClLanduseMovementStatus).filter(ClLanduseMovementStatus.code == value.status_id).count()
        if status_count == 1:
            status = self.session.query(ClLanduseMovementStatus).filter(
                ClLanduseMovementStatus.code == value.status_id).one()

            row = self.movement_status_twidget.rowCount()
            self.movement_status_twidget.insertRow(row)

            item_status = QTableWidgetItem(unicode(status.description))
            item_status.setData(Qt.UserRole, status.code)
            item_status.setData(Qt.UserRole + 1, value.id)

            item_date = QTableWidgetItem(str(value.status_date))
            item_status.setData(Qt.UserRole, value.status_date)

            if value.next_officer_in_charge_ref:
                next_officer = value.next_officer_in_charge_ref.lastname + ", " + value.next_officer_in_charge_ref.firstname
                officer = value.officer_in_charge_ref.lastname + ", " + value.officer_in_charge_ref.firstname

                item_next_officer = QTableWidgetItem(next_officer)
                item_next_officer.setData(Qt.UserRole, value.next_officer_in_charge)
                # if value.status_ref.color:
                #     item_next_officer.setBackground(QtGui.QColor(value.status_ref.color))

                item_officer = QTableWidgetItem(officer)
                item_officer.setData(Qt.UserRole, value.officer_in_charge)
                # if value.status_ref.color:
                #     item_officer.setBackground(QtGui.QColor(value.status_ref.color))

                self.movement_status_twidget.setItem(row, 0, item_status)
                self.movement_status_twidget.setItem(row, 1, item_date)
                self.movement_status_twidget.setItem(row, 2, item_officer)
                self.movement_status_twidget.setItem(row, 3, item_next_officer)

    @pyqtSlot()
    def on_status_add_button_clicked(self):

        next_officer_username = self.next_officer_in_charge_cbox.itemData(
            self.next_officer_in_charge_cbox.currentIndex(), Qt.UserRole)
        sd_next_officer = self.session.query(SdUser).filter(SdUser.user_id == next_officer_username).one()

        case_id = self.landuse_maintenance_cbox.itemData(self.landuse_maintenance_cbox.currentIndex())
        status_id = self.status_cbox.itemData(self.status_cbox.currentIndex())
        status = self.session.query(ClLanduseMovementStatus).filter(ClLanduseMovementStatus.code == status_id).one()

        status_new = CaLanduseMaintenanceStatus()
        status_new.case_id = case_id

        status_new.officer_in_charge_ref = DatabaseUtils.current_sd_user()
        status_new.officer_in_charge = DatabaseUtils.current_sd_user().user_id
        status_new.next_officer_in_charge = sd_next_officer.user_id
        status_new.next_officer_in_charge_ref = sd_next_officer

        status_new.status_id = status_id
        status_new.status_ref = status

        self.session.add(status_new)
        self.session.flush()
        self.__case_status(status_new)
