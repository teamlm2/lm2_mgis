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
from ..view.Ui_PlanNavigatorWidget import Ui_PlanNavigatorWidget
from ..utils.LayerUtils import LayerUtils
from ..model.AuCadastreBlock import *
from ..model.AuLevel1 import *
from ..model.AuLevel2 import *
from ..model.LdProjectPlan import *
from ..model.ClPlanDecisionLevel import *
from ..model.ClPlanStatusType import *
from ..model.ClPlanType import *
from ..model.LdProjectPlanStatus import *
from ..utils.DatabaseUtils import *
from ..utils.PluginUtils import *
from ..model.DatabaseHelper import *
from ..controller.PlanDetailWidget import *
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

class PlanNavigatorWidget(QDockWidget, Ui_PlanNavigatorWidget, DatabaseHelper):

    def __init__(self,  plugin, parent=None):

        super(PlanNavigatorWidget,  self).__init__(parent)
        DatabaseHelper.__init__(self)

        self.setupUi(self)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.plugin = plugin
        self.session = SessionHandler().session_instance()

        self.userSettings = None
        self.planDetailWidget = None
        self.current_dialog = None
        self.is_au_level2 = False
        self.__setup_combo_boxes()
        self.__setup_change_combo_boxes()
        self.working_l1_cbox.currentIndexChanged.connect(self.__working_l1_changed)
        self.working_l2_cbox.currentIndexChanged.connect(self.__working_l2_changed)
        self.__setup_twidgets()
        self.__load_role_settings()
        # self.__report_setup()
        self.tabWidget.setCurrentIndex(0)

    def __load_role_settings(self):

        user_name = QSettings().value(SettingsConstants.USER)
        self.userSettings = DatabaseUtils.role_settings(user_name)

        if self.userSettings.pa_till.year == 9999:
            self.infinity_check_box.setChecked(True)
            self.till_date_edit.setEnabled(False)
        else:
            self.till_date_edit.setDate(self.userSettings.pa_till)

        self.from_date_edit.setDate(self.userSettings.pa_from)
        self.extent_rbutton.setChecked(True)

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

    def __setup_change_combo_boxes(self):

        self.office_in_charge_cbox.clear()
        self.next_officer_in_charge_cbox.clear()
        self.plan_type_cbox.clear()
        self.status_cbox.clear()
        self.decision_level_cbox.clear()

        self.office_in_charge_cbox.addItem("*", -1)
        self.next_officer_in_charge_cbox.addItem("*", -1)

        set_roles = self.session.query(SetRole).order_by(SetRole.user_name)
        soum_code = DatabaseUtils.working_l2_code()
        if set_roles is not None:
            for setRole in set_roles:
                l2_code_list = setRole.restriction_au_level2.split(',')
                if soum_code in l2_code_list:
                    sd_user = self.session.query(SdUser).filter(SdUser.gis_user_real == setRole.user_name_real).first()
                    lastname = ''
                    firstname = ''
                    if sd_user:
                        lastname = sd_user.lastname
                        firstname = sd_user.firstname
                    self.office_in_charge_cbox.addItem(lastname + ", " + firstname, sd_user.user_id)
                    self.next_officer_in_charge_cbox.addItem(lastname + ", " + firstname, sd_user.user_id)

        statuses = self.session.query(ClPlanStatusType).all()
        types = self.session.query(ClPlanType).all()
        decision_levels = self.session.query(ClPlanDecisionLevel).all()

        self.plan_type_cbox.addItem("*", -1)
        self.status_cbox.addItem("*", -1)
        self.decision_level_cbox.addItem("*", -1)

        for value in statuses:
            self.status_cbox.addItem(value.description, value.code)
        for value in types:
            self.plan_type_cbox.addItem(value.description, value.code)
        for value in decision_levels:
            self.decision_level_cbox.addItem(value.description, value.code)

    def __setup_twidgets(self):

        self.context_menu = QMenu()
        self.zoom_to_parcel_action = QAction(QIcon(":/plugins/lm2/parcel.png"), self.tr("Zoom to parcel"), self)
        self.copy_number_action = QAction(QIcon(":/plugins/lm2/copy.png"), self.tr("Copy number"), self)
        self.context_menu.addAction(self.zoom_to_parcel_action)
        self.context_menu.addSeparator()
        self.context_menu.addAction(self.copy_number_action)
        self.zoom_to_parcel_action.triggered.connect(self.on_zoom_to_parcel_action_clicked)
        self.copy_number_action.triggered.connect(self.on_copy_number_action_clicked)

        self.plan_context_menu = QMenu()

        self.plan_context_menu.addAction(self.zoom_to_parcel_action)
        self.plan_context_menu.addSeparator()
        self.plan_context_menu.addAction(self.copy_number_action)
        self.plan_context_menu.addSeparator()

        self.plan_results_twidget.setColumnCount(1)
        self.plan_results_twidget.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.plan_results_twidget.horizontalHeader().setVisible(False)
        self.plan_results_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.plan_results_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.plan_results_twidget.setDragEnabled(True)
        self.plan_results_twidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.plan_results_twidget.customContextMenuRequested.connect(self.on_custom_context_menu_requested)

        self.case_results_twidget.setColumnCount(1)
        self.case_results_twidget.setDragEnabled(False)
        self.case_results_twidget.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.case_results_twidget.horizontalHeader().setVisible(False)
        self.case_results_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.case_results_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.case_results_twidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.case_results_twidget.customContextMenuRequested.connect(self.on_custom_context_menu_requested)

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

    @pyqtSlot(str)
    def on_street_completer_activated(self, text):

        if not text:
            return

        self.street_completer.activated[str].emit(text)

    @pyqtSlot(str)
    def on_khashaa_completer_activated(self, text):

        if not text:
            return
        self.khashaa_completer.activated[str].emit(text)

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
    def on_infinity_check_box_stateChanged(self, state):

        if state == Qt.Checked:
            self.till_date_edit.setEnabled(False)
        else:
            self.till_date_edit.setEnabled(True)

    @pyqtSlot()
    def on_get_extent_button_clicked(self):

        rect = self.plugin.iface.mapCanvas().extent()
        self.extent_east_spinbox.setValue(rect.xMaximum())
        self.extent_west_spinbox.setValue(rect.xMinimum())
        self.extent_north_spinbox.setValue(rect.yMaximum())
        self.extent_south_spinbox.setValue(rect.yMinimum())

    @pyqtSlot()
    def on_clear_b_box_button_clicked(self):

        # self.session.execute("refresh materialized view webgis.view_contract")
        self.extent_west_spinbox.setValue(0)
        self.extent_east_spinbox.setValue(0)
        self.extent_south_spinbox.setValue(0)
        self.extent_north_spinbox.setValue(0)

    @pyqtSlot()
    def on_remove_button_clicked(self):

        database = QSettings().value(SettingsConstants.DATABASE_NAME, '', type=str)
        host = QSettings().value(SettingsConstants.HOST, '', type=str)
        port = QSettings().value(SettingsConstants.PORT, '5432', type=str)
        user = QSettings().value(SettingsConstants.USER, '', type=str)

        layermap = QgsMapLayerRegistry.instance().mapLayers()
        for layer_id, layer in layermap.iteritems():

            if layer.type() != QgsMapLayer.VectorLayer or layer.dataProvider().name() != "postgres":
                continue
            uri = QgsDataSourceURI(layer.source())
            if uri.database() != database or uri.host() != host or uri.port() != port or uri.username() != user:
                continue

            geometry_column = uri.geometryColumn().upper()
            subset_string = layer.subsetString()

            if subset_string.upper().find('ST_WITHIN') != -1 \
                    or subset_string.upper().find(geometry_column + ' &&') != -1 \
                    or subset_string.upper().find('ST_TRANSFORM') != -1:
                idx = subset_string.upper().find(' AND ')
                if idx == -1:
                    subset_string = ''
                else:
                    subset_string = subset_string[idx+5]

            layer.setSubsetString(subset_string)

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.plugin.iface.mapCanvas().refresh()
        QApplication.restoreOverrideCursor()
        project = QgsProject.instance()
        project.setDirty(True)

    @pyqtSlot()
    def on_apply_button_clicked(self):

        database = QSettings().value(SettingsConstants.DATABASE_NAME, '', type=str)
        host = QSettings().value(SettingsConstants.HOST, '', type=str)
        port = QSettings().value(SettingsConstants.PORT, '5432', type=str)
        user = QSettings().value(SettingsConstants.USER, '', type=str)

        core_subset_string = None
        layermap = QgsMapLayerRegistry.instance().mapLayers()
        for layer_id, layer in layermap.iteritems():

            if layer.type() != QgsMapLayer.VectorLayer or layer.dataProvider().name() != "postgres":
                continue
            uri = QgsDataSourceURI(layer.source())
            if uri.database() != database or uri.host() != host or uri.port() != port or uri.username() != user:
                continue

            subset_string = layer.subsetString()
            geometry_column = uri.geometryColumn().upper()

            if subset_string.upper().find('ST_WITHIN') != -1 \
                    or subset_string.upper().find(geometry_column + ' &&') != -1 \
                    or subset_string.upper().find('ST_TRANSFORM') != -1:

                idx = subset_string.upper().find(' AND ')
                if idx == -1:
                    subset_string = ''
                else:
                    subset_string = subset_string[idx:]
            else:
                if len(subset_string) > 0:
                    subset_string = ' AND ' + subset_string


            if core_subset_string is None:
                core_subset_string = self.__getBBoxSubsetString(layer)

            subset_string = core_subset_string + subset_string
            layer.setSubsetString(subset_string)

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.plugin.iface.mapCanvas().refresh()
        QApplication.restoreOverrideCursor()
        project = QgsProject.instance()
        project.setDirty(True)

    def __getBBoxSubsetString(self, layer):

        x_min = self.extent_west_spinbox.value()
        x_max = self.extent_east_spinbox.value()
        y_min = self.extent_south_spinbox.value()
        y_max = self.extent_north_spinbox.value()

        srs_id = layer.crs().postgisSrid()

        point1 = QgsPoint(x_min, y_min)
        point2 = QgsPoint(x_max, y_max)

        point1 = self.plugin.transformPoint(point1, srs_id)
        point2 = self.plugin.transformPoint(point2, srs_id)

        uri = QgsDataSourceURI(layer.source())
        geometry_column = uri.geometryColumn()

        return "ST_Within({0}, ST_SetSRID(ST_MakeBox2D(ST_Point({1}), ST_Point({2})), {3}))".format(geometry_column, point1.toString(), point2.toString(), srs_id)

    @pyqtSlot()
    def on_temp_filter_apply_button_clicked(self):

        self.create_savepoint()
        user_name = QSettings().value(SettingsConstants.USER)
        self.userSettings = DatabaseUtils.role_settings(user_name)

        try:
            if self.userSettings:
                if self.infinity_check_box.isChecked():
                    self.userSettings.pa_till = date(9999, 12, 31)
                else:
                    self.userSettings.pa_till = DatabaseUtils.convert_date(self.till_date_edit.date())

                self.userSettings.pa_from = DatabaseUtils.convert_date(self.from_date_edit.date())

                self.commit()

        except SQLAlchemyError, e:
            self.rollback_to_savepoint()
            PluginUtils.show_message(self,  self.tr("Sql Error"), e.message)
            return

        self.plugin.iface.mapCanvas().refresh()



    def __selected_application(self):

        selected_items = self.plan_results_twidget.selectedItems()

        if len(selected_items) != 1:
            self.error_label.setText(self.tr("Only single selection allowed."))
            return None

        selected_item = selected_items[0]
        app_id = selected_item.data(Qt.UserRole)

        try:
            application_instance = self.session.query(CtApplication).filter_by(app_id=app_id).one()
        except SQLAlchemyError, e:
            PluginUtils.show_message(self, self.tr("LM2", "Sql Error"), e.message)
            return None

        return application_instance

    def __selected_maintenance_case(self):

        selected_items = self.case_results_twidget.selectedItems()
        case_instance = None

        if len(selected_items) != 1:
            self.error_label.setText(self.tr("Only single selection allowed."))
            return None

        selected_case_item = selected_items[0]
        item_id = selected_case_item.data(Qt.UserRole)
        soum = selected_case_item.data(Qt.UserRole + 1)

        DatabaseUtils.set_working_schema(soum)

        try:
            case_instance = self.session.query(CaMaintenanceCase).filter_by(id=item_id).one()
        except SQLAlchemyError, e:
            PluginUtils.show_message(self, self.tr("LM2", "Sql Error"), e.message)
            return None

        return case_instance


    @pyqtSlot(int)
    def on_plan_date_checkbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.plan_datetime_edit.setEnabled(True)
        else:
            self.plan_datetime_edit.setEnabled(False)

    @pyqtSlot()
    def on_plan_find_button_clicked(self):

        self.__search_plans()

    def __search_plans(self):

        # try:
        values = self.session.query(LdProjectPlan)

        filter_is_set = False

        if self.plan_num_edit.text():
            filter_is_set = True
            plan_no = "%" + self.plan_num_edit.text() + "%"
            values = values.filter(LdProjectPlan.plan_draft_no.ilike(plan_no))


        if self.status_cbox.currentIndex() != -1:
            if not self.status_cbox.itemData(self.status_cbox.currentIndex()) == -1:
                filter_is_set = True
                status = self.status_cbox.itemData(self.status_cbox.currentIndex())

                values = values.filter(LdProjectPlan.last_status_type == status)
        if self.plan_type_cbox.currentIndex() != -1:
            if not self.plan_type_cbox.itemData(self.plan_type_cbox.currentIndex()) == -1:
                filter_is_set = True
                values = values.filter(LdProjectPlan.plan_type == self.plan_type_cbox.itemData(self.plan_type_cbox.currentIndex()))

        if self.decision_level_cbox.currentIndex() != -1:
            if not self.decision_level_cbox.itemData(self.decision_level_cbox.currentIndex()) == -1:
                filter_is_set = True
                values = values.filter(LdProjectPlan.plan_decision_level == self.decision_level_cbox.itemData(self.decision_level_cbox.currentIndex()))

        if self.office_in_charge_cbox.currentIndex() != -1:
            if not self.office_in_charge_cbox.itemData(self.office_in_charge_cbox.currentIndex()) == -1:
                filter_is_set = True
                officer = self.office_in_charge_cbox.itemData(self.office_in_charge_cbox.currentIndex())

                values = values.join(LdProjectPlanStatus, LdProjectPlan.plan_draft_id == LdProjectPlanStatus.plan_draft_id). \
                    filter(LdProjectPlanStatus.status == LdProjectPlan.last_status_type). \
                    filter(LdProjectPlanStatus.officer_in_charge == officer)

        if self.next_officer_in_charge_cbox.currentIndex() != -1:
            if not self.next_officer_in_charge_cbox.itemData(self.next_officer_in_charge_cbox.currentIndex()) == -1:
                filter_is_set = True
                officer = self.next_officer_in_charge_cbox.itemData(self.next_officer_in_charge_cbox.currentIndex())

                values = values.join(LdProjectPlanStatus, LdProjectPlan.plan_draft_id == LdProjectPlanStatus.plan_draft_id). \
                    filter(LdProjectPlanStatus.status == LdProjectPlan.last_status_type). \
                    filter(LdProjectPlanStatus.next_officer_in_charge == officer)

        if self.plan_date_checkbox.isChecked():
            filter_is_set = True
            qt_date = self.plan_datetime_edit.date().toString(Constants.DATABASE_DATE_FORMAT)
            python_date = datetime.strptime(str(qt_date), Constants.PYTHON_DATE_FORMAT)

            values = values.filter(LdProjectPlan.created_at >= python_date)

        count = 0

        self.__remove_plan_items()

        if values.distinct(LdProjectPlan.plan_draft_no).count() == 0:
            self.error_label.setText(self.tr("No land plan found for this search filter."))
            return

        elif filter_is_set is False:
            self.error_label.setText(self.tr("Please specify a search filter."))
            return

        for value in values.all():
            plan_type = "" if not value.plan_type_ref else value.plan_type_ref.description

            item = QTableWidgetItem(str(value.plan_draft_no) + " ( " + unicode(plan_type) + " )")
            item.setIcon(QIcon(QPixmap(":/plugins/lm2/land_plan.png")))
            item.setData(Qt.UserRole, value.plan_draft_id)
            item.setData(Qt.UserRole+1, value.plan_draft_no)
            self.plan_results_twidget.insertRow(count)
            self.plan_results_twidget.setItem(count, 0, item)
            count += 1

        self.error_label.setText("")
        self.plan_results_label.setText(self.tr("Results: ") + str(count))

        # except SQLAlchemyError, e:
        #     PluginUtils.show_message(self, self.tr("LM2", "Sql Error"), e.message)
        #     return

    @pyqtSlot()
    def on_case_find_button_clicked(self):

        self.__search_cases()

    def __search_cases(self):

        filter_is_set = False
        current_working_soum = DatabaseUtils.current_working_soum_schema()

        # try:
        # maintenance_search = self.session.query(MaintenanceSearch)
        maintenance_search = self.session.query(MaintenanceSearch)
        filter_is_set = False

        if self.case_app_no_edit.text():
            filter_is_set = True
            app_no = "%" + self.case_app_no_edit.text() + "%"
            maintenance_search = maintenance_search.filter(MaintenanceSearch.app_no.ilike(app_no))

        if self.case_completion_date_checkbox.isChecked():
            filter_is_set = True
            qt_date = self.case_completion_date_edit.date().toString(Constants.DATABASE_DATE_FORMAT)
            python_date = datetime.strptime(str(qt_date), Constants.PYTHON_DATE_FORMAT)
            maintenance_search = maintenance_search.filter(MaintenanceSearch.completion_date >= python_date)

        if self.case_no_edit.text():
            filter_is_set = True
            case_no = "%" + self.case_no_edit.text() + "%"
            maintenance_search = maintenance_search.\
                filter(or_(MaintenanceSearch.case_id.ilike(case_no), cast(MaintenanceSearch.id, String).ilike(case_no)))

        if self.case_parcel_no_edit.text():
            filter_is_set = True
            parcel = "%" + self.case_parcel_no_edit.text() + "%"
            maintenance_search = maintenance_search.filter(MaintenanceSearch.parcel.ilike(parcel))

        if self.surveyed_by_land_officer_cbox.itemData(self.surveyed_by_land_officer_cbox.currentIndex()) != -1:
            filter_is_set = True
            surveyed_by = self.surveyed_by_land_officer_cbox.itemData(self.surveyed_by_land_officer_cbox.currentIndex())
            maintenance_search = maintenance_search.filter(MaintenanceSearch.surveyed_by_land_office == surveyed_by)

        if self.finalized_by_cbox.itemData(self.finalized_by_cbox.currentIndex()) != -1:
            filter_is_set = True
            finalized_by = self.finalized_by_cbox.itemData(self.finalized_by_cbox.currentIndex())
            maintenance_search = maintenance_search.filter(MaintenanceSearch.completed_by == finalized_by)

        if self.surveyed_by_company_cbox.itemData(self.surveyed_by_company_cbox.currentIndex()) != -1:
            filter_is_set = True
            surveyor = self.surveyed_by_company_cbox.itemData(self.surveyed_by_company_cbox.currentIndex())

            maintenance_search = maintenance_search.filter(MaintenanceSearch.surveyed_by_surveyor == surveyor)

        if self.case_status_cbox.itemData(self.case_status_cbox.currentIndex()) != -1:
            filter_is_set = True
            status = self.case_status_cbox.itemData(self.case_status_cbox.currentIndex())
            if status == Constants.CASE_STATUS_IN_PROGRESS:
                maintenance_search = maintenance_search.filter(MaintenanceSearch.completion_date == None)
            else:
                maintenance_search = maintenance_search.filter(MaintenanceSearch.completion_date != None)
        if self.case_right_holder_name_edit.text():
            filter_is_set = True
            right_holder = self.case_right_holder_name_edit.text()
            if "," in right_holder:
                right_holder_strings = right_holder.split(",")
                surname = "%" + right_holder_strings[0].strip() + "%"
                first_name = "%" + right_holder_strings[1].strip() + "%"
                maintenance_search = maintenance_search.filter(
                    and_(func.lower(MaintenanceSearch.name).ilike(func.lower(surname)),
                         func.lower(MaintenanceSearch.first_name).ilike(func.lower(first_name))))
            else:
                right_holder = "%" + self.application_right_holder_name_edit.text() + "%"
                maintenance_search = maintenance_search.filter(
                    or_(func.lower(MaintenanceSearch.name).ilike(func.lower(right_holder)),
                        func.lower(MaintenanceSearch.first_name).ilike(func.lower(right_holder))))
        if self.personal_case_edit.text():
            filter_is_set = True
            person_id = "%" + self.personal_case_edit.text() + "%"
            maintenance_search = maintenance_search.filter(MaintenanceSearch.person_id.ilike(person_id))

        count = 0

        self.__remove_maintenance_case_items()

        if maintenance_search.distinct(MaintenanceSearch.id).count() == 0:
            self.error_label.setText(self.tr("No maintenance cases found for this search filter."))
            return

        elif filter_is_set is False:
            self.error_label.setText(self.tr("Please specify a search filter."))
            return

        for case in maintenance_search.distinct(MaintenanceSearch.id).all():
            item = QTableWidgetItem(str(case.id) + self.tr(" (Soum: {0})".format(case.soum)))
            item.setIcon(QIcon(QPixmap(":/plugins/lm2/case.png")))
            item.setData(Qt.UserRole, case.id)
            item.setData(Qt.UserRole + 1, str(case.soum))
            self.case_results_twidget.insertRow(count)
            self.case_results_twidget.setItem(count, 0, item)
            count += 1

        self.error_label.setText("")
        self.case_results_label.setText(self.tr("Results: ") + str(count))

        # except SQLAlchemyError, e:
        #     PluginUtils.show_message(self, self.tr("LM2", "Sql Error"), e.message)
        #     return

    def __clear_plan(self):

        self.plan_num_edit.clear()

        self.plan_type_cbox.setCurrentIndex(self.plan_type_cbox.findData(-1))
        self.status_cbox.setCurrentIndex(self.status_cbox.findData(-1))
        self.decision_level_cbox.setCurrentIndex(self.decision_level_cbox.findData(-1))
        self.office_in_charge_cbox.setCurrentIndex(self.office_in_charge_cbox.findData(-1))
        self.next_officer_in_charge_cbox.setCurrentIndex(self.next_officer_in_charge_cbox.findData(-1))

    def __clear_maintenance(self):

        self.case_no_edit.clear()
        self.case_completion_date_edit.clear()
        self.case_completion_date_edit.setDate(QDate.currentDate())
        self.case_parcel_no_edit.clear()
        self.case_app_no_edit.clear()
        self.case_right_holder_name_edit.clear()
        self.personal_case_edit.clear()

        self.surveyed_by_company_cbox.setCurrentIndex(self.surveyed_by_company_cbox.findData(-1))
        self.surveyed_by_land_officer_cbox.setCurrentIndex(self.surveyed_by_land_officer_cbox.findData(-1))
        self.finalized_by_cbox.setCurrentIndex(self.finalized_by_cbox.findData(-1))

    def __remove_plan_items(self):

        self.plan_results_twidget.setRowCount(0)
        self.plan_results_label.setText("")

    def __remove_maintenance_case_items(self):

        self.case_results_twidget.setRowCount(0)
        self.case_results_label.setText("")

    @pyqtSlot()
    def on_plan_clear_button_clicked(self):

        self.__remove_plan_items()
        self.__clear_plan()

    @pyqtSlot()
    def on_case_clear_button_clicked(self):

        self.__remove_maintenance_case_items()
        self.__clear_maintenance()

    @pyqtSlot(QPoint)
    def on_custom_context_menu_requested(self, point):

        if self.tabWidget.currentWidget() == self.plan_tab:
            item = self.plan_results_twidget.itemAt(point)
            if item is None: return
            self.plan_context_menu.exec_(self.plan_results_twidget.mapToGlobal(point))

        elif self.tabWidget.currentWidget() == self.maintenance_tab:
            item = self.case_results_twidget.itemAt(point)
            if item is None: return
            self.context_menu.exec_(self.case_results_twidget.mapToGlobal(point))

    @pyqtSlot()
    def on_current_dialog_closed(self):

        DialogInspector().set_dialog_visible(False)

    @pyqtSlot()
    def on_case_revert_button_clicked(self):

        if not len(self.case_results_twidget.selectedItems()):
            return

        items = self.case_results_twidget.selectedItems()
        message_box = QMessageBox()

        if len(items) > 1:
            message_box.setText(self.tr("Do you want to delete {0} selected maintenance cases and roll back the edits?").format(len(items)))
        elif len(items) == 1:
            message_box.setText(self.tr("Do you want to delete the maintenance case {0}").format(str(items[0].data(Qt.UserRole))))

        delete_button = message_box.addButton(self.tr("Delete"), QMessageBox.ActionRole)
        message_box.addButton(self.tr("Cancel"), QMessageBox.ActionRole)

        message_box.exec_()

        if not message_box.clickedButton() == delete_button:
            return

        for item in items:

            self.create_savepoint()

            case_no = item.data(Qt.UserRole)
            case_soum = item.data(Qt.UserRole + 1)
            case_soum = case_soum.strip()

            DatabaseUtils.set_working_schema(case_soum)
            m_case = self.session.query(CaMaintenanceCase).filter(CaMaintenanceCase.id == case_no).one()

            if m_case.completion_date is not None:
                if len(m_case.parcels) != 0:
                    self.error_label.setText(self.tr("The maintenance case {0} is finalized and has parcels assigned.".format(str(case_no))))
                    return
                else:
                    self.session.query(CaTmpBuilding).filter(CaTmpBuilding.maintenance_case == case_no).delete()
                    self.session.query(CaMaintenanceCase).filter(CaMaintenanceCase.id == case_no).delete()
                    self.commit()
                    self.__search_cases()
                    return

            self.session.query(CaTmpParcel).filter(CaTmpParcel.maintenance_case == case_no).delete()
            self.session.query(CaTmpBuilding).filter(CaTmpBuilding.maintenance_case == case_no).delete()

            self.session.query(CaMaintenanceCase).filter(CaMaintenanceCase.id == case_no).delete()

            self.commit()

        self.__search_cases()
        DatabaseUtils.set_working_schema()

    @pyqtSlot()
    def on_case_finalize_button_clicked(self):

        if DialogInspector().dialog_visible():
            return

        case_instance = self.__selected_maintenance_case()

        if case_instance is not None:

            if case_instance.completion_date is None:
                selected_item = self.case_results_twidget.selectedItems()[0]
                soum = selected_item.data(Qt.UserRole + 1)

                self.current_dialog = FinalizeCaseDialog(case_instance, soum, self.plugin, self.plugin.iface.mainWindow())
                DialogInspector().set_dialog_visible(True)
                self.current_dialog.rejected.connect(self.on_current_dialog_closed)
                self.current_dialog.setModal(False)
                self.current_dialog.show()

            else:
                PluginUtils.show_message(self, self.tr("Maintenance Case"), self.tr("The maintenance case is already finalized."))
                return

        self.__search_cases()

        self.plugin.iface.mapCanvas().refresh()

    @pyqtSlot()
    def on_case_create_button_clicked(self):

        if DialogInspector().dialog_visible():
            return
        session = SessionHandler().session_instance()
        ca_maintenance_case = CaMaintenanceCase()
        user = DatabaseUtils.current_user()
        officers = self.session.query(SetRole) \
            .filter(SetRole.user_name == user.user_name) \
            .filter(SetRole.is_active == True).one()

        ca_maintenance_case.created_by = officers.user_name_real
        session.add(ca_maintenance_case)

        DatabaseUtils.set_working_schema()
        create_new_m_case = PluginUtils.create_new_m_case()
        self.current_dialog = CreateCaseDialog(self.plugin, create_new_m_case, False, self.plugin.iface.mainWindow())
        self.current_dialog.rejected.connect(self.on_current_dialog_closed)
        DialogInspector().set_dialog_visible(True)
        self.current_dialog.setModal(False)
        self.current_dialog.show()

    @pyqtSlot(QTableWidgetItem)
    def on_plan_results_twidget_itemDoubleClicked(self, item):

        if DialogInspector().dialog_visible():
            return

        app_instance = self.__selected_application()

        if app_instance is not None:
            self.current_dialog = ApplicationsDialog(app_instance, self, True, self.plugin.iface.mainWindow())
            DialogInspector().set_dialog_visible(True)
            self.current_dialog.rejected.connect(self.on_current_dialog_closed)
            self.current_dialog.setModal(False)
            self.current_dialog.show()

    @pyqtSlot(QTableWidgetItem)
    def on_zoom_to_parcel_action_clicked(self):

        soum_with_parcels = {}

        if self.tabWidget.currentWidget() == self.person_tab:
            person = self.__selected_person()
            # try:
            person_search_results = self.session.query(PersonSearch.app_no).distinct(PersonSearch.app_no).filter(PersonSearch.person_id == person.person_id).all()
            for person_result in person_search_results:

                if person_result.app_no is not None:

                    app_no_soum = person_result.app_no.split("-")[0]

                    if app_no_soum not in soum_with_parcels.keys():
                        soum_with_parcels[app_no_soum] = []

                    DatabaseUtils.set_working_schema(app_no_soum)

                    count = self.session.query(CtApplication.parcel).filter(CtApplication.app_no == person_result.app_no).count()
                    if count <> 1:
                        continue

                    application = self.session.query(CtApplication.parcel).filter(CtApplication.app_no == person_result.app_no).one()

                    if application[0] is not None:
                        soum_with_parcels[app_no_soum].append(application[0])

            # except SQLAlchemyError, e:
            #     PluginUtils.show_message(self, self.tr("Sql Error"), e.message)
            #     DatabaseUtils.set_working_schema()
            #     return

            self.__zoom_to_parcel_several_soums(soum_with_parcels)

        elif self.tabWidget.currentWidget() == self.application_tab:

            application = self.__selected_application()
            if application.parcel is not None:
                #check refused parcels
                count = self.session.query(CaParcel).filter(CaParcel.parcel_id == application.parcel).count()
                if count == 0:
                    layer_name = "ca_refused_parcel"
                else:
                    layer_name = "ca_parcel"

                self.__zoom_to_parcel_ids([application.parcel], layer_name)
            else:
                self.error_label.setText(self.tr("No parcel assigned."))

        elif self.tabWidget.currentWidget() == self.maintenance_tab:

            m_case = self.__selected_maintenance_case()
            if len(m_case.parcels) > 0:
                self.__zoom_to_parcels(m_case.parcels)
            else:
                #its an m_case in progress
                #take care that the working schema in __selected_maintenance_case did not change
                self.__zoom_to_tmp_parcels(m_case.id)

        elif self.tabWidget.currentWidget() == self.contract_tab:

            contract = self.__selected_contract()
            if contract is None:
                return

            parcels = []

            for app_roles in contract.application_roles:
                application = app_roles.application_ref
                if application.parcel is not None:
                    parcels.append(application.parcel)

            self.__zoom_to_parcel_ids(parcels)

        elif self.tabWidget.currentWidget() == self.record_tab:

            record = self.__selected_record()
            if record is None:
                return

            parcels = []

            for app_roles in record.application_roles:
                application = app_roles.application_ref
                if application.parcel is not None:
                    parcels.append(application.parcel)

            self.__zoom_to_parcel_ids(parcels)

        elif self.tabWidget.currentWidget() == self.maintenance_tab:

            m_case = self.__selected_maintenance_case()
            self.__zoom_to_parcels(m_case.parcels)

        elif self.tabWidget.currentWidget() == self.parcel_tab:

            parcel_id = self.__selected_parcel_id()
            self.__zoom_to_parcel_ids([parcel_id])

        elif self.tabWidget.currentWidget() == self.decision_tab:

            decision = self.__selected_decision()
            if decision is None:
                return

            parcels = []

            for result in decision.results:
                application = result.application_ref
                if application.parcel is not None:
                    parcels.append(application.parcel)

            self.__zoom_to_parcel_ids(parcels)

        DatabaseUtils.set_working_schema()

    def __zoom_to_parcel_several_soums(self, soums):

        LayerUtils.deselect_all()

        for soum, parcel_array in soums.iteritems():

            layer = LayerUtils.layer_by_data_source("data_soums_union", "ca_parcel")

            if layer is None:
                layer = LayerUtils.load_layer_by_name_admin_units("ca_parcel", "parcel_id", "data_soums_union")

            exp_string = ""

            for parcel_id in parcel_array:
                if exp_string == "":
                    exp_string = "parcel_id = \'" + parcel_id  + "\'"
                else:
                    exp_string += " or parcel_id = \'" + parcel_id  + "\'"

            request = QgsFeatureRequest()
            request.setFilterExpression(exp_string)

            feature_ids = []
            iterator = layer.getFeatures(request)

            for feature in iterator:
                feature_ids.append(feature.id())

            if len(feature_ids) == 0:
                self.error_label.setText(self.tr("No parcel assigned"))

            layer.setSelectedFeatures(feature_ids)
            self.plugin.iface.mapCanvas().zoomToSelected(layer)

    def __zoom_to_parcel_ids(self, parcel_ids, layer_name = None):

        LayerUtils.deselect_all()
        is_temp = False
        if layer_name is None:
            for parcel_id in parcel_ids:
                if len(parcel_id) == 12:
                    layer_name = "ca_parcel"
                else:
                    layer_name = "ca_tmp_parcel_view"
                    is_temp = True

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

    def __zoom_to_parcels(self, parcels):

        LayerUtils.deselect_all()

        layer = LayerUtils.layer_by_data_source("data_soums_union", "ca_parcel")

        restrictions = DatabaseUtils.working_l2_code()
        if not restrictions:
            PluginUtils.show_message(self, self.tr("Connection Error"), self.tr("Please connect to database!!!"))
            return
        if layer is None:
            layer = LayerUtils.load_layer_by_name("ca_parcel", "parcel_id", restrictions)

        request = QgsFeatureRequest()
        exp_string = ""

        for parcel in parcels:
            if exp_string == "":
                exp_string = "parcel_id = \'" + parcel.parcel_id  + "\'"
            else:
                exp_string += " or parcel_id = \'" + parcel.parcel_id  + "\'"

        request.setFilterExpression(exp_string)
        feature_ids = []
        iterator = layer.getFeatures(request)

        for feature in iterator:
            feature_ids.append(feature.id())

        if len(feature_ids) == 0:
            self.error_label.setText(self.tr("No parcel assigned"))

        layer.setSelectedFeatures(feature_ids)
        self.plugin.iface.mapCanvas().zoomToSelected(layer)

    def __zoom_to_tmp_parcels(self, m_case_no):

        LayerUtils.deselect_all()

        root = QgsProject.instance().layerTreeRoot()

        vlayer = LayerUtils.layer_by_data_source("data_soums_union", "ca_tmp_parcel_view")

        if vlayer is None:
            vlayer = LayerUtils.load_tmp_layer_by_name("ca_tmp_parcel_view", "parcel_id", "data_soums_union")
        mygroup = root.findGroup(u"Кадастрын өөрчлөлт")
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

        request = QgsFeatureRequest()
        exp_string = "maintenance_case = {0}".format(m_case_no)
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

    @pyqtSlot()
    def on_copy_number_action_clicked(self):

        if self.tabWidget.currentWidget() == self.person_tab:
            person = self.__selected_person()
            QApplication.clipboard().setText(person.person_id)
        elif self.tabWidget.currentWidget() == self.parcel_tab:
            parcel_id = self.__selected_parcel_id()
            QApplication.clipboard().setText(parcel_id)
        elif self.tabWidget.currentWidget() == self.application_tab:
            app = self.__selected_application()
            QApplication.clipboard().setText(app.app_no)
        elif self.tabWidget.currentWidget() == self.contract_tab:
            contract = self.__selected_contract()
            QApplication.clipboard().setText(contract.contract_no)
        elif self.tabWidget.currentWidget() == self.record_tab:
            record = self.__selected_record()
            QApplication.clipboard().setText(record.record_no)
        elif self.tabWidget.currentWidget() == self.maintenance_tab:
            m_case = self.__selected_maintenance_case()
            QApplication.clipboard().setText(m_case.id)
        elif self.tabWidget.currentWidget() == self.decision_tab:
            decision = self.__selected_decision()
            QApplication.clipboard().setText(decision.decision_no)


    @pyqtSlot(QTableWidgetItem)
    def on_case_results_twidget_itemDoubleClicked(self, item):

        if DialogInspector().dialog_visible():
            return

        case_instance = self.__selected_maintenance_case()

        selected_case_item = self.case_results_twidget.selectedItems()[0]
        soum = selected_case_item.data(Qt.UserRole + 1)

        DatabaseUtils.set_working_schema(soum)

        if case_instance is not None:
            self.current_dialog = CreateCaseDialog(self.plugin, case_instance, True, self.plugin.iface.mainWindow())
            self.current_dialog.rejected.connect(self.on_current_dialog_closed)
            DialogInspector().set_dialog_visible(True)
            self.current_dialog.setModal(False)
            self.current_dialog.show()


    @pyqtSlot(int)
    def on_tabWidget_currentChanged(self):

        self.error_label.setText("")

    def keyPressEvent(self, event):

        key = event.key()

        if key in (Qt.Key_Enter, Qt.Key_Return):

            if self.tabWidget.currentWidget() == self.person_tab:
                self.__search_persons()
            elif self.tabWidget.currentWidget() == self.parcel_tab:
                self.__search_parcels()
            elif self.tabWidget.currentWidget() == self.application_tab:
                self.__search_plans()
            elif self.tabWidget.currentWidget() == self.contract_tab:
                self.__search_contracts()
            elif self.tabWidget.currentWidget() == self.record_tab:
                self.__search_records()
            elif self.tabWidget.currentWidget() == self.maintenance_tab:
                self.__search_cases()
            elif self.tabWidget.currentWidget() == self.decision_tab:
                self.__search_decisions()

    @pyqtSlot(QTableWidgetItem)
    def on_plan_results_twidget_itemClicked(self, item):

        id = item.data(Qt.UserRole)

        try:
            result = self.session.query(LdProjectPlan).filter(LdProjectPlan.plan_draft_id == id).one()

            self.plan_num_edit.setText(result.plan_draft_no)

            self.plan_type_cbox.setCurrentIndex(self.plan_type_cbox.findData(result.plan_type))
            self.status_cbox.setCurrentIndex(self.status_cbox.findData(result.last_status_type))
            self.decision_level_cbox.setCurrentIndex(self.decision_level_cbox.findData(result.last_status_type))
            # self.office_in_charge_cbox.setCurrentIndex(self.office_in_charge_cbox.findData(result.plan_decision_level))
            # self.next_officer_in_charge_cbox.setCurrentIndex(self.next_officer_in_charge_cbox.findData(result.next_officer_in_charge))
            self.__change_current_plan()
        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

    def __change_current_plan(self):

        try:
            role = DatabaseUtils.current_user()
            if role:
                role.working_plan_id = self.__selected_plan().plan_draft_id
                self.commit()

        except SQLAlchemyError, e:
            self.rollback_to_savepoint()
            PluginUtils.show_message(self,  self.tr("Sql Error"), e.message)
            return

    @pyqtSlot(QTableWidgetItem)
    def on_case_results_twidget_itemClicked(self, item):

        id = item.data(Qt.UserRole)
        # try:
        maintenance_results = self.session.query(MaintenanceSearch).filter(MaintenanceSearch.id == id).all()
        for maintenance_result in maintenance_results:

            self.case_no_edit.setText(str(maintenance_result.id))
            if maintenance_result.completion_date != None:
                self.case_completion_date_edit.setDate(maintenance_result.completion_date)
                self.case_parcel_no_edit.setText(maintenance_result.parcel)
            if maintenance_result.app_no != None:
                self.case_app_no_edit.setText(maintenance_result.app_no)

            if maintenance_result.surveyed_by_surveyor != None:
                self.surveyed_by_company_cbox.setCurrentIndex(
                    self.surveyed_by_company_cbox.findData(maintenance_result.surveyed_by_surveyor))
            if maintenance_result.surveyed_by_land_office != None:
                self.surveyed_by_land_officer_cbox.setCurrentIndex(
                    self.surveyed_by_land_officer_cbox.findData(maintenance_result.surveyed_by_land_office))
            if maintenance_result.completed_by != None:
                self.finalized_by_cbox.setCurrentIndex(self.finalized_by_cbox.findData(maintenance_result.completed_by))

        # except SQLAlchemyError, e:
        #     PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
        #     return

    #Gt's Reports
    @pyqtSlot(int)
    def on_begin_year_sbox_valueChanged(self, sbox_value):

        self.end_date = (str(sbox_value + 1) + '-01-01')
        self.end_date = datetime.strptime(self.end_date, "%Y-%m-%d").date()

        self.before_date = (str(sbox_value) + '-01-01')
        self.before_date = datetime.strptime(self.before_date, "%Y-%m-%d").date()

    @pyqtSlot()
    def on_au_level1_button_clicked(self):

        root = QgsProject.instance().layerTreeRoot()
        mygroup = root.findGroup(u"Хил")
        vlayer = LayerUtils.layer_by_data_source("admin_units", "au_level1")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("au_level1", "code","admin_units")
        vlayer.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "template\style/au_level1.qml")
        vlayer.setLayerName(self.tr("Admin Unit Level1"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            mygroup.addLayer(vlayer)

    @pyqtSlot()
    def on_au_level2_button_clicked(self):

        root = QgsProject.instance().layerTreeRoot()
        mygroup = root.findGroup(u"Хил")
        vlayer = LayerUtils.layer_by_data_source("admin_units", "au_level2")
        if vlayer is None:
        # if not self.is_au_level2:
            vlayer = LayerUtils.load_layer_base_layer("au_level2", "code", "admin_units")
        vlayer.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/au_level2.qml")
        vlayer.setLayerName(self.tr("Admin Unit Level2"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            mygroup.addLayer(vlayer)
        self.is_au_level2 = True

    @pyqtSlot()
    def on_au_level3_button_clicked(self):

        root = QgsProject.instance().layerTreeRoot()
        mygroup = root.findGroup(u"Хил")
        vlayer = LayerUtils.layer_by_data_source("admin_units", "au_level3")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("au_level3", "code", "admin_units")
        vlayer.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/au_level3.qml")
        vlayer.setLayerName(self.tr("Admin Unit Level3"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            mygroup.addLayer(vlayer)

    @pyqtSlot()
    def on_fee_tax_zone_button_clicked(self):

        root = QgsProject.instance().layerTreeRoot()
        mygroup = root.findGroup(u"Үнэлгээ, төлбөрийн бүс")
        vlayer = LayerUtils.layer_by_data_source("settings", "set_view_fee_zone")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("set_view_fee_zone", "zone_id", "settings")
        vlayer.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"/template\style/set_fee_zone.qml")
        vlayer.setLayerName(self.tr("Fee Zone"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            mygroup.addLayer(vlayer)

        vlayer = LayerUtils.layer_by_data_source("settings", "set_view_tax_zone")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("set_view_tax_zone", "zone_id", "settings")
        vlayer.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"/template\style/set_tax_and_price_zone.qml")
        vlayer.setLayerName(self.tr("Tax Zone"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            mygroup.addLayer(vlayer)

    @pyqtSlot()
    def on_sec_zone_button_clicked(self):

        root = QgsProject.instance().layerTreeRoot()
        mygroup = root.findGroup(u"Мэдээний хяналт")
        vlayer = LayerUtils.layer_by_data_source("data_landuse", "ca_sec_parcel")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("ca_sec_parcel", "parcel_id", "data_landuse")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/ca_sec_parcel.qml")
        vlayer.setLayerName(self.tr("Parcel Sec"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            mygroup.addLayer(vlayer)

    @pyqtSlot()
    def on_mpa_zone_button_clicked(self):

        root = QgsProject.instance().layerTreeRoot()
        mygroup = root.findGroup(u"Тусгай хамгаалалттай газар")
        vlayer = LayerUtils.layer_by_data_source("admin_units", "au_mpa")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("au_mpa", "id", "admin_units")
        vlayer.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/au_mpa.qml")
        vlayer.setLayerName(self.tr("Admin Unit MPA"))
        mygroup.addLayer(vlayer)

        vlayer = LayerUtils.layer_by_data_source("admin_units", "au_mpa_zone")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("au_mpa_zone", "id", "admin_units")
        vlayer.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/au_mpa_zone.qml")
        vlayer.setLayerName(self.tr("Admin Unit MPA Zone"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            mygroup.addLayer(vlayer)

    @pyqtSlot()
    def on_valuation_zone_button_clicked(self):

        root = QgsProject.instance().layerTreeRoot()
        mygroup = root.findGroup(u"Үнэлгээ, төлбөрийн бүс")
        vlayer = LayerUtils.layer_by_data_source("data_estimate", "pa_valuation_level_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("pa_valuation_level_view", "id", "data_estimate")
        vlayer.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/pa_valuation_level.qml")
        vlayer.setLayerName(self.tr("Valuation level"))
        mygroup.addLayer(vlayer)

        root = QgsProject.instance().layerTreeRoot()
        mygroup = root.findGroup(u"Үнэлгээ, төлбөрийн бүс")
        vlayer = LayerUtils.layer_by_data_source("data_estimate", "pa_valuation_level_agriculture_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("pa_valuation_level_agriculture_view", "id", "data_estimate")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/pa_valuation_agriculture_level.qml")
        vlayer.setLayerName(self.tr("Valuation Agrivulture level"))
        mygroup.addLayer(vlayer)

    @pyqtSlot()
    def on_plan_edit_button_clicked(self):

        if DialogInspector().dialog_visible():
            return

        plan_instance = self.__selected_plan()
        if plan_instance is not None:
            self.current_dialog = PlanDetailWidget(plan_instance, self, True, self.plugin.iface.mainWindow())
            self.plugin.iface.addDockWidget(Qt.RightDockWidgetArea, self.current_dialog)
            self.current_dialog.show()
            self.hide()
        # DatabaseUtils.set_working_schema()

    def __selected_plan(self):

        selected_items = self.plan_results_twidget.selectedItems()

        if len(selected_items) != 1:
            self.error_label.setText(self.tr("Only single selection allowed."))
            return None

        selected_item = selected_items[0]
        plan_id = selected_item.data(Qt.UserRole)

        try:
            plan_instance = self.session.query(LdProjectPlan).filter_by(plan_draft_id=plan_id).one()
        except SQLAlchemyError, e:
            PluginUtils.show_message(self, self.tr("LM2", "Sql Error"), e.message)
            return None

        return plan_instance

    @pyqtSlot()
    def on_current_view_button_clicked(self):

        root = QgsProject.instance().layerTreeRoot()
        mygroup = root.findGroup(u"Main")

        vlayer_polygon = LayerUtils.layer_by_data_source("data_plan", "ld_view_project_main_zone_polygon")
        if vlayer_polygon is None:
            vlayer_polygon = LayerUtils.load_polygon_layer_base_layer("ld_view_project_main_zone_polygon", "parcel_id", "data_plan")
        vlayer_polygon.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/plan_polygon_style.qml")
        vlayer_polygon.setLayerName(self.tr("Current Main Polygon"))
        myalayer = root.findLayer(vlayer_polygon.id())
        if myalayer is None:
            mygroup.addLayer(vlayer_polygon)

        vlayer_line = LayerUtils.layer_by_data_source("data_plan", "ld_view_project_main_zone_line")
        if vlayer_line is None:
            vlayer_line = LayerUtils.load_line_layer_base_layer("ld_view_project_main_zone_line", "parcel_id", "data_plan")
        vlayer_line.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/plan_line_style.qml")
        vlayer_line.setLayerName(self.tr("Current Main Line"))
        myalayer = root.findLayer(vlayer_line.id())
        if myalayer is None:
            mygroup.addLayer(vlayer_line)

        vlayer_point = LayerUtils.layer_by_data_source("data_plan", "ld_view_project_main_zone_point")
        if vlayer_point is None:
            vlayer_point = LayerUtils.load_point_layer_base_layer("ld_view_project_main_zone_point", "parcel_id", "data_plan")
        vlayer_point.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "/template\style/plan_point_style.qml")
        vlayer_point.setLayerName(self.tr("Current Main Point"))
        myalayer = root.findLayer(vlayer_point.id())
        if myalayer is None:
            mygroup.addLayer(vlayer_point)