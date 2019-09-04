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
from ..controller.DraftDecisionPrintDialog import *
from ..view.Ui_SpaParcelWidget import Ui_SpaParcelWidget
from ..model.ClSpaType import *
from ..model.ClSpaMood import *
from ..model.SdDepartment import *
from ..controller.PastureMonitoringValueDialog import PastureMonitoringValueDialog
from ..controller.MemberGroupDialog import *
from PastureSettings import PastureSettings
from ApplicationsSpaDialog import ApplicationsSpaDialog
from SentToGovernorPastureDialog import SentToGovernorPastureDialog
from LandFeePaymentsDialog import *
from ContractPastureDialog import *
from ..model.DialogInspector import DialogInspector
from ..model.ApplicationPastureSearch import *
from ..model.PClPastureDaatsLevel import *
from ..model.PsPointDetail import *
from ..model.PsPointDaatsValue import *
from ..model.PsPointDetailPoints import *
from ..model.PsPastureBoundary import *
from ..model.PsAvgDaats import *
from ..model.AuReserveZone import *
from ..model.PsParcel import *
from ..model.BsPerson import *
from ..model.PClReserveDaatsLevel import *
from ..model.PsAvgReserveDaats import *
from ..utils.LayerUtils import LayerUtils
from ..utils.SessionHandler import SessionHandler
from ..model.Enumerations import ApplicationType
from ..model.EnumerationsPasture import ApplicationType
from ..model.PsRecoveryClass import *
from ..model.PsParcelDuration import *
from ..model.CtAppGroupBoundary import *
from datetime import timedelta
from xlsxwriter.utility import xl_rowcol_to_cell, xl_col_to_name
import xlsxwriter

LANDUSE_1 = u'Хөдөө аж ахуйн газар'
LANDUSE_2 = u'Хот, тосгон, бусад суурины газар'
LANDUSE_3 = u'Зам, шугам сүлжээний газар'
LANDUSE_4 = u'Ойн сан бүхий газар'
LANDUSE_5 = u'Усны сан бүхий газар'
LANDUSE_6 = u'Улсын тусгай хэрэгцээний газар'

DAATS_LEVEL_1 = 1
DAATS_LEVEL_2 = 2
DAATS_LEVEL_3 = 3
DAATS_LEVEL_4 = 4
DAATS_LEVEL_5 = 5
DAATS_LEVEL_6 = 6

RESERVE_DAATS_LEVEL_1 = 1
RESERVE_DAATS_LEVEL_2 = 2
RESERVE_DAATS_LEVEL_3 = 3

class SpaParcelWidget(QDockWidget, Ui_SpaParcelWidget, DatabaseHelper):

    def __init__(self,  plugin, parent=None):

        super(SpaParcelWidget, self).__init__(parent)
        DatabaseHelper.__init__(self)

        self.setupUi(self)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.plugin = plugin

        self.session = SessionHandler().session_instance()

        self.userSettings = None

        self.app_date_edit.setDate(QDate.currentDate())
        self.__setup_twidgets()

        # self.__load_role_settings()

        self.__setup_combo_boxes()

        self.working_l1_cbox.currentIndexChanged.connect(self.__working_l1_changed)
        self.working_l2_cbox.currentIndexChanged.connect(self.__working_l2_changed)

    def __setup_twidgets(self):

        self.zoom_to_parcel_action = QAction(QIcon(":/plugins/lm2/parcel.png"), self.tr("Zoom to parcel"), self)
        self.copy_number_action = QAction(QIcon(":/plugins/lm2/copy.png"), self.tr("Copy number"), self)
        self.copy_number_action.triggered.connect(self.on_copy_number_action_clicked)
        self.zoom_to_parcel_action.triggered.connect(self.on_zoom_to_parcel_action_clicked)

        self.contract_context_menu = QMenu()
        self.contract_action = QAction(QIcon(":/plugins/lm2/landfeepayment.png"),
                                                self.tr("Create and View Contract"), self)
        self.contract_action.triggered.connect(self.__show_contract_dialog)
        self.contract_context_menu.addAction(self.contract_action)
        self.contract_context_menu.addAction(self.zoom_to_parcel_action)
        self.contract_context_menu.addSeparator()
        self.contract_context_menu.addAction(self.copy_number_action)

        self.parcel_results_twidget.setColumnCount(1)
        self.parcel_results_twidget.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.parcel_results_twidget.horizontalHeader().setVisible(False)
        self.parcel_results_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.parcel_results_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.parcel_results_twidget.setDragEnabled(True)
        self.parcel_results_twidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.parcel_results_twidget.customContextMenuRequested.connect(self.on_custom_context_menu_requested)

    @pyqtSlot(QTableWidgetItem)
    def on_zoom_to_parcel_action_clicked(self):

        app = self.__selected_application()
        app_type = app.app_type
        app_parcels = self.session.query(CtApplicationPUGParcel).\
            filter(CtApplicationPUGParcel.application == app.app_id).all()

        if app is None:
            return

        parcels = []

        for app_parcel in app_parcels:
            if app_parcel.parcel is not None:
                parcels.append(app_parcel.parcel)

        self.__zoom_to_parcel_ids(parcels, app_type)

    def __zoom_to_parcel_ids(self, parcel_ids, app_type, layer_name = None):

        LayerUtils.deselect_all()
        if layer_name is None:
            for parcel_id in parcel_ids:
                if len(parcel_id) == 10:
                    if app_type == 26:
                        layer_name = "ca_pasture_parcel"
                    else:
                        layer_name = "ca_person_group_parcel"

        layer = LayerUtils.layer_by_data_source("data_soums_union", layer_name)

        restrictions = DatabaseUtils.working_l2_code()
        if layer is None:
            layer = LayerUtils.load_layer_by_name(layer_name, "parcel_id", restrictions)

        exp_string = ""

        for parcel_id in parcel_ids:
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

    @pyqtSlot()
    def on_copy_number_action_clicked(self):

        if self.tabWidget.currentWidget() == self.pasture_tab:
            app = self.__selected_application()
            QApplication.clipboard().setText(app.app_no)

    @pyqtSlot()
    def on_pasture_contract_view_button_clicked(self):

        if DialogInspector().dialog_visible():
            return

        app_instance = self.__selected_application()
        app_contract_count = self.session.query(CtContractApplicationRole). \
            filter(CtContractApplicationRole.application == app_instance.app_id).count()

        if app_contract_count == 0:
            DatabaseUtils.set_working_schema()
            contract = PluginUtils.create_new_contract()
            self.current_dialog = ContractPastureDialog(self.plugin, contract, self, False, self.plugin.iface.mainWindow())
            self.current_dialog.rejected.connect(self.on_current_dialog_closed)
            DialogInspector().set_dialog_visible(True)
            self.current_dialog.setModal(False)
            self.current_dialog.show()
        elif app_contract_count == 1:
            app_contract = self.session.query(CtContractApplicationRole). \
                filter(CtContractApplicationRole.application == app_instance.app_id).one()
            contract = self.session.query(CtContract).filter_by(contract_id=app_contract.contract).one()

            self.current_dialog = ContractPastureDialog(self.plugin, contract, self, True, self.plugin.iface.mainWindow())
            self.current_dialog.rejected.connect(self.on_current_dialog_closed)
            DialogInspector().set_dialog_visible(True)
            self.current_dialog.setModal(False)
            self.current_dialog.show()

    def __show_contract_dialog(self):

        if DialogInspector().dialog_visible():
            return

        app_instance = self.__selected_application()
        app_contract_count = self.session.query(CtContractApplicationRole).\
            filter(CtContractApplicationRole.application == app_instance.app_id).count()

        if app_contract_count == 0:
            DatabaseUtils.set_working_schema()
            contract = PluginUtils.create_new_contract()

            self.current_dialog = ContractPastureDialog(self.plugin, contract, self, False, self.plugin.iface.mainWindow())
            self.current_dialog.rejected.connect(self.on_current_dialog_closed)
            DialogInspector().set_dialog_visible(True)
            self.current_dialog.setModal(False)
            self.current_dialog.show()
        elif app_contract_count == 1:
            app_contract = self.session.query(CtContractApplicationRole). \
                filter(CtContractApplicationRole.application == app_instance.app_id).one()
            contract = self.session.query(CtContract).filter_by(contract_id=app_contract.contract).one()

            self.current_dialog = ContractPastureDialog(self.plugin, contract, self, True, self.plugin.iface.mainWindow())
            self.current_dialog.rejected.connect(self.on_current_dialog_closed)
            DialogInspector().set_dialog_visible(True)
            self.current_dialog.setModal(False)
            self.current_dialog.show()

    @pyqtSlot(QPoint)
    def on_custom_context_menu_requested(self, point):

        if self.tabWidget.currentWidget() == self.pasture_tab:
            item = self.parcel_results_twidget.itemAt(point)
            if item is None: return
            self.contract_context_menu.exec_(self.parcel_results_twidget.mapToGlobal(point))

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

    def __load_role_settings(self):

        user_name = QSettings().value(SettingsConstants.USER)
        self.userSettings = DatabaseUtils.role_settings(user_name)

        self.__create_pasture_app_view()
        self.__create_pug_view()
        self.__create_parcel_duration_view()
        # self.__create_pasture_monitoring_point_view()

    def __create_parcel_duration_view(self):

        current_working_soum = "'" + str(DatabaseUtils.current_working_soum_schema()) + "'"

        sql = ""
        if not sql:
            sql = "Create or replace temp view ps_parcel_duration as" + "\n"
        else:
            sql = sql + "UNION" + "\n"

        select = "SELECT pasture_parcel.parcel, pasture_parcel.application, pasture_parcel.pasture, pasture_parcel.begin_month, " \
                 "pasture_parcel.end_month, pasture_parcel.days, pasture_parcel.app_no " \
                 "FROM data_soums_union.ct_application_parcel_pasture pasture_parcel " \
                 "left join data_soums_union.ct_application app on pasture_parcel.application = app.app_id " \
                 "where  app.au2 = {0}".format(current_working_soum) + "\n"
        sql = sql + select
        sql = "{0} order by parcel;".format(sql)

        # try:
        self.session.execute(sql)
        self.commit()
        # except SQLAlchemyError, e:
        #     PluginUtils.show_message(self, self.tr("LM2", "Sql Error"), e.message)
        #     return

    def __create_pug_view(self):

        current_working_soum = "'" + str(DatabaseUtils.current_working_soum_schema()) + "'"

        sql = ""

        if not sql:
            sql = "Create or replace temp view ps_pasture_boundary as" + "\n"
        else:
            sql = sql + "UNION" + "\n"

        select = "SELECT pasture_parcel.parcel_id, pasture_parcel.address_neighbourhood pasture_land_name, pasture_parcel.pasture_type, pasture_parcel.area_ga pasture_area, " \
                 "pug.code pug_code, pug.area_ga pug_area, pug.group_name pug_name, au2.code as au2_code, au3.code as au3_code, " \
                 "pasture_parcel.geometry parcel_geom, pug.geometry as pug_geom " \
                 "FROM data_soums_union.ca_pasture_parcel pasture_parcel " \
                 "left join data_soums_union.ca_pug_boundary pug on st_intersects(pasture_parcel.geometry, pug.geometry) " \
                 "left join admin_units.au_level2 au2 on st_intersects(pasture_parcel.geometry, au2.geometry) " \
                 "left join admin_units.au_level3 au3 on st_intersects(pasture_parcel.geometry, au3.geometry) " \
                 "where  au2.code = {0}".format(current_working_soum) + "\n"

        sql = sql + select
        sql = "{0} order by parcel_id;".format(sql)

        # try:
        self.session.execute(sql)
        self.commit()
        # except SQLAlchemyError, e:
        #     PluginUtils.show_message(self, self.tr("LM2", "Sql Error"), e.message)
        #     return

    def __create_pasture_app_view(self):

        current_working_soum = "'" + str(DatabaseUtils.current_working_soum_schema()) + "'"

        sql = ""

        if not sql:
            sql = "Create or replace temp view pasture_app_search as" + "\n"
        else:
            sql = sql + "UNION" + "\n"

        select = "SELECT application.app_no,application.app_id, group_member.group_no, parcel.pasture_type ,application.app_timestamp, application.app_type, status.status, status.status_date, status.officer_in_charge, status.next_officer_in_charge, decision.decision_no, " \
                 "contract.contract_no,contract.contract_id, person.person_id, person.person_register, person.name, person.first_name, person.middle_name, parcel.parcel_id, tmp_parcel.parcel_id tmp_parcel_id " \
                 "FROM data_soums_union.ct_application application " \
                 "left join data_soums_union.ct_application_status status on status.application = application.app_id " \
                 "left join data_soums_union.ct_decision_application dec_app on dec_app.application = application.app_id " \
                 "left join data_soums_union.ct_decision decision on decision.decision_id = dec_app.decision " \
                 "left join data_soums_union.ct_contract_application_role contract_app on application.app_id = contract_app.application " \
                 "left join data_soums_union.ct_contract contract on contract_app.contract = contract.contract_id " \
                 "left join data_soums_union.ct_application_person_role app_pers on app_pers.application = application.app_id " \
                 "left join data_soums_union.ct_group_member group_member on group_member.person = app_pers.person " \
                 "left join base.bs_person person on person.person_id = app_pers.person " \
                 "left join data_soums_union.ca_tmp_parcel tmp_parcel on application.tmp_parcel = tmp_parcel.parcel_id " \
                 "left join data_soums_union.ca_pasture_parcel parcel on parcel.parcel_id = application.parcel " \
                 "where (application.app_type = 26 or application.app_type = 27) and application.au2 = {0}".format(current_working_soum) + "\n"

        sql = sql + select

        sql = "{0} order by app_no;".format(sql)

        # try:
        self.session.execute(sql)
        self.commit()
        # except SQLAlchemyError, e:
        #     PluginUtils.show_message(self, self.tr("LM2", "Sql Error"), e.message)
        #     return

    def __create_pasture_monitoring_point_view(self):

        au_level2_string = self.userSettings.restriction_au_level2
        au_level2_list = au_level2_string.split(",")
        sql = ""

        for au_level2 in au_level2_list:

            au_level2 = au_level2.strip()
            if not sql:
                sql = "Create temp view ca_pasture_monitoring_search as" + "\n"
            else:
                sql = sql + "UNION" + "\n"

            select = "SELECT * " \
                     "FROM data_soums_union.ca_pasture_monitoring monitoring ".format(au_level2) + "\n"

            sql = sql + select

        try:
            self.session.execute(sql)
            self.commit()
        except SQLAlchemyError, e:
            PluginUtils.show_message(self, self.tr("LM2", "Sql Error"), e.message)
            return

    def __working_l2_changed(self, index):

        l2_code = self.working_l2_cbox.itemData(index)

        self.create_savepoint()

        try:
            role = DatabaseUtils.current_user()
            if not l2_code:
                role.working_au_level2 = None
            else:
                role.working_au_level2 = l2_code
            self.__change_workig_soum_list()
            self.commit()

            user = DatabaseUtils.current_user().user_name
            setRole = self.session.query(SetRole).filter(SetRole.user_name == user).filter(
                SetRole.is_active == True).one()
            auLevel2List = setRole.restriction_au_level2.split(",")
            schemaList = []

            for auLevel2 in auLevel2List:
                auLevel2 = auLevel2.strip()
                schemaList.append("s" + auLevel2)

            schema_string = ",".join(schemaList)

            self.session.execute(set_search_path)

            self.session.commit()
        except SQLAlchemyError, e:
            self.rollback_to_savepoint()
            PluginUtils.show_message(self,  self.tr("Sql Error"), e.message)
            return
        self.__zoom_to_soum(l2_code)
        self.__load_role_settings()

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

    def __change_workig_soum_list(self):

        role = DatabaseUtils.current_user()
        first_code = None
        l1_working_code = DatabaseUtils.working_l1_code()
        working_l2_code = DatabaseUtils.working_l2_code()
        # in case of districts - sort after l1 code
        if l1_working_code[:2] == "01":
            search_path_array = DatabaseUtils.l2_restriction_array()
        else:
            search_path_array = DatabaseUtils.l2_restriction_array()

        found_code = False
        schema_string = ''
        schema_list = []
        if not working_l2_code:
            return
        first_schema = working_l2_code
        schema_list.append(first_schema)
        for item in search_path_array:
            au_level2 = item.strip()

            if item != working_l2_code:
                schema_list.append(au_level2)
        schema_string = ",".join(schema_list)

        role.restriction_au_level2 = schema_string

    def __setup_combo_boxes(self):

        self.spa_type_cbox.clear()
        self.land_use_type_cbox.clear()
        self.department_cbox.clear()

        try:
            PluginUtils.populate_au_level1_cbox(self.working_l1_cbox, False)
            au2 = DatabaseUtils.working_l2_code()
            l1_code = self.working_l1_cbox.itemData(self.working_l1_cbox.currentIndex(), Qt.UserRole)
            PluginUtils.populate_au_level2_cbox(self.working_l2_cbox, l1_code, False)

            cl_landusetype = self.session.query(ClLanduseType).all()
            cl_spa_type = self.session.query(ClSpaType).all()
            cl_department = self.session.query(SdDepartment).all()

        except SQLAlchemyError, e:
            PluginUtils.show_message(self, self.tr("Sql Error"), e.message)
            return


        self.spa_type_cbox.addItem("*", -1)
        self.land_use_type_cbox.addItem("*", -1)
        self.department_cbox.addItem("*", -1)

        if cl_landusetype is not None:
            for value in cl_landusetype:
                self.land_use_type_cbox.addItem(str(value.code)+':'+value.description, value.code)

        if cl_spa_type is not None:
            for value in cl_spa_type:
                self.spa_type_cbox.addItem(str(value.code)+':'+value.description, value.code)

        if cl_department is not None:
            for value in cl_department:
                self.department_cbox.addItem(value.name, value.department_id)


    @pyqtSlot()
    def on_current_dialog_closed(self):

        DialogInspector().set_dialog_visible(False)

    @pyqtSlot()
    def on_pasture_app_add_button_clicked(self):

        if DialogInspector().dialog_visible():
            return

        DatabaseUtils.set_working_schema()
        application = PluginUtils.create_new_application()
        self.current_dialog = ApplicationsSpaDialog(self.plugin, application, self, False, self.plugin.iface.mainWindow())
        self.current_dialog.setModal(False)
        self.current_dialog.rejected.connect(self.on_current_dialog_closed)
        DialogInspector().set_dialog_visible(True)
        self.current_dialog.show()

    @pyqtSlot()
    def on_clear_button_clicked(self):

        self.__remove_items()
        self.__clear_find_values()

    def __remove_items(self):

        self.parcel_results_twidget.setRowCount(0)
        self.results_label.setText("")

    def __clear_find_values(self):

        self.parcel_id_edit.clear()
        self.personal_parcel_edit.clear()
        self.pasture_app_no_edit.clear()
        self.parcel_right_holder_name_edit.clear()
        self.parcel_contract_num_edit.clear()
        self.app_date_edit.setDate(QDate.currentDate())
        self.app_date_edit.setEnabled(False)
        self.app_date_cbox.setChecked(False)
        self.spa_type_cbox.setCurrentIndex(self.spa_type_cbox.findData(-1))
        self.land_use_type_cbox.setCurrentIndex(self.land_use_type_cbox.findData(-1))

    @pyqtSlot(int)
    def on_app_date_cbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.app_date_edit.setEnabled(True)
        else:
            self.app_date_edit.setEnabled(False)

    @pyqtSlot()
    def on_pasture_find_button_clicked(self):

        self.__pasture_applications()

    def __pasture_applications(self):

        # try:
        applications = self.session.query(ApplicationPastureSearch)
        filter_is_set = False

        applications = applications.filter(or_(ApplicationPastureSearch.app_type == ApplicationType.right_land,
                   ApplicationPastureSearch.app_type == ApplicationType.pasture_use))
        if self.spa_type_cbox.currentIndex() != -1:
            if not self.spa_type_cbox.itemData(self.spa_type_cbox.currentIndex()) == -1:
                filter_is_set = True
                group_no = self.spa_type_cbox.itemData(self.spa_type_cbox.currentIndex())

                applications = applications.filter(ApplicationPastureSearch.group_no == group_no)

        if self.pasture_app_no_edit.text():
            filter_is_set = True
            app_no = "%" + self.pasture_app_no_edit.text() + "%"
            applications = applications.filter(ApplicationPastureSearch.app_no.ilike(app_no))

        if self.parcel_right_holder_name_edit.text():
            filter_is_set = True
            right_holder = self.parcel_right_holder_name_edit.text()
            if "," in right_holder:
                right_holder_strings = right_holder.split(",")
                surname = "%" + right_holder_strings[0].strip() + "%"
                first_name = "%" + right_holder_strings[1].strip() + "%"
                applications = applications.filter(and_(func.lower(ApplicationPastureSearch.name).ilike(func.lower(surname)), func.lower(ApplicationPastureSearch.first_name).ilike(func.lower(first_name))))
            else:
                right_holder = "%" + self.parcel_right_holder_name_edit.text() + "%"
                applications = applications.filter(or_(func.lower(ApplicationPastureSearch.name).ilike(func.lower(right_holder)), func.lower(ApplicationPastureSearch.first_name).ilike(func.lower(right_holder)), func.lower(ApplicationPastureSearch.middle_name).ilike(func.lower(right_holder))))

        if self.parcel_id_edit.text():
            filter_is_set = True
            parcel_no = "%" + self.parcel_id_edit.text() + "%"

            applications = applications.filter(ApplicationPastureSearch.parcel_id.ilike(parcel_no))

        if self.personal_parcel_edit.text():
            filter_is_set = True
            register_no = "%" + self.personal_parcel_edit.text() + "%"
            applications = applications.filter(ApplicationPastureSearch.person_register.ilike(register_no))

        if self.parcel_contract_num_edit.text():
            filter_is_set = True
            contract_num = "%" + self.parcel_contract_num_edit.text() + "%"
            applications = applications.filter(or_(ApplicationPastureSearch.contract_no.ilike(contract_num), ApplicationPastureSearch.record_no.ilike(contract_num)))


        if self.app_date_cbox.isChecked():
            filter_is_set = True
            qt_date = self.app_date_edit.date().toString(Constants.DATABASE_DATE_FORMAT)
            python_date = datetime.strptime(str(qt_date), Constants.PYTHON_DATE_FORMAT)

            applications = applications.filter(ApplicationPastureSearch.app_timestamp >= python_date)

        count = 0

        self.__remove_pasture_items()

        # if applications.distinct(ApplicationPastureSearch.app_no).count() == 0:
        #     self.error_label.setText(self.tr("No applications found for this search filter."))
        #     return

        if filter_is_set is False:
            self.error_label.setText(self.tr("Please specify a search filter."))
            return

        for application in applications.distinct(ApplicationPastureSearch.app_no, ApplicationPastureSearch.app_id, ApplicationPastureSearch.status).all():

            app_type = "" if not application.app_type_ref else application.app_type_ref.description
            item = QTableWidgetItem(str(application.app_no) + " ( " + unicode(app_type) + " )")
            if application.status == 9:
                item.setBackground(QtGui.QColor(133, 193, 233 ))
            elif application.status == 7:
                item.setBackground(QtGui.QColor(88, 214, 141))
            elif application.status == 6:
                item.setBackground(QtGui.QColor(213, 219, 219))
            else:
                item.setBackground(QtGui.QColor(249, 231, 159))
            item.setIcon(QIcon(QPixmap(":/plugins/lm2/application.png")))
            item.setData(Qt.UserRole, application.app_no)
            item.setData(Qt.UserRole+1, application.app_id)
            self.parcel_results_twidget.insertRow(count)
            self.parcel_results_twidget.setItem(count, 0, item)
            count += 1

        self.error_label.setText("")
        self.results_label.setText(self.tr("Results: ") + str(count))

        # except SQLAlchemyError, e:
        #     PluginUtils.show_message(self, self.tr("LM2", "Sql Error"), e.message)
        #     return

    @pyqtSlot(QTableWidgetItem)
    def on_parcel_results_twidget_itemDoubleClicked(self, item):

        if DialogInspector().dialog_visible():
            return

        app_instance = self.__selected_application()

        if app_instance is not None:
            self.current_dialog = ApplicationsSpaDialog(self.plugin,app_instance, self, True, self.plugin.iface.mainWindow())
            DialogInspector().set_dialog_visible(True)
            self.current_dialog.rejected.connect(self.on_current_dialog_closed)
            self.current_dialog.setModal(False)
            self.current_dialog.show()

    def __selected_application(self):

        selected_items = self.parcel_results_twidget.selectedItems()

        if len(selected_items) != 1:
            self.error_label.setText(self.tr("Only single selection allowed."))
            return None

        selected_item = selected_items[0]
        app_no = selected_item.data(Qt.UserRole)

        app_no_soum = app_no.split("-")[0]

        DatabaseUtils.set_working_schema(app_no_soum)

        try:
            application_instance = self.session.query(CtApplication).filter_by(app_no=app_no).one()
        except SQLAlchemyError, e:
            PluginUtils.show_message(self, self.tr("LM2", "Sql Error"), e.message)
            return None

        return application_instance

    @pyqtSlot()
    def on_draft_decision_button_clicked(self):

        self.dlg = SentToGovernorPastureDialog(False, self.plugin.iface.mainWindow())
        self.dlg.show()

    @pyqtSlot()
    def on_pasture_app_view_button_clicked(self):

        if DialogInspector().dialog_visible():
            return

        app_instance = self.__selected_application()

        if app_instance is not None:
            self.current_dialog = ApplicationsSpaDialog(self.plugin, app_instance, self, True, self.plugin.iface.mainWindow())
            DialogInspector().set_dialog_visible(True)
            self.current_dialog.rejected.connect(self.on_current_dialog_closed)
            self.current_dialog.setModal(False)
            self.current_dialog.show()

    @pyqtSlot(QTableWidgetItem)
    def on_parcel_results_twidget_itemClicked(self, item):

        id = item.data(Qt.UserRole)
        soum_code = id.split("-")[0]
        aimag_code = soum_code[:3]
        self.working_l1_cbox.setCurrentIndex(self.working_l1_cbox.findData(aimag_code))
        self.working_l2_cbox.setCurrentIndex(self.working_l2_cbox.findData(soum_code))
        try:
            app_result = self.session.query(ApplicationPastureSearch).filter(ApplicationPastureSearch.app_no == id).one()
            self.pasture_app_no_edit.setText(app_result.app_no)
            self.parcel_right_holder_name_edit.setText(app_result.first_name)
            self.parcel_id_edit.setText(app_result.person_register)
            self.personal_parcel_edit.setText(app_result.person_register)
            if app_result.contract_no != None:
                self.parcel_contract_num_edit.setText(app_result.contract_no)
                self.parcel_contract_num_edit.setStyleSheet(self.styleSheet())
            else:
                self.parcel_contract_num_edit.setText(self.tr('No Contract'))
                self.parcel_contract_num_edit.setStyleSheet("color: rgb(189, 21, 38)")

            self.spa_type_cbox.setCurrentIndex(self.spa_type_cbox.findData(app_result.group_no))

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"),
                                   self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

    @pyqtSlot()
    def on_pasture_layer_view_button_clicked(self):

        root = QgsProject.instance().layerTreeRoot()

        self.__pug_group_layers(root)

        self.__tnc_group_layers(root)

    def __tnc_group_layers(self, root):

        mygroup = root.findGroup(u'Байгалын нөөц')
        if mygroup is None:
            mygroup = root.insertGroup(8, u'Байгалын нөөц')

        is_person_group_layer = False
        layers = self.plugin.iface.legendInterface().layers()
        vlayer_parcel = LayerUtils.load_union_layer_by_name("ca_person_group_parcel", "parcel_id")
        for layer in layers:
            if layer.name() == u"Байгалын нөөцийн хил" or layer.name() == "TNCParcel":
                is_person_group_layer = True
        if not is_person_group_layer:
            mygroup.addLayer(vlayer_parcel)

        vlayer_parcel.setLayerName(QApplication.translate("Plugin", "TNCParcel"))
        vlayer_parcel.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "template\style/tnc_boundary.qml")


    def __pug_group_layers(self, root):

        mygroup = root.findGroup("PUG")
        if mygroup is None:
            mygroup = root.insertGroup(7, "PUG")
        is_layer = False
        is_eco_layer = False
        is_pug_parcel = False
        is_pug_building = False
        is_monitoring_layer = False
        is_natural_zone_layer = False

        monitoring_layer = LayerUtils.load_layer_by_name_pasture_monitoring("ca_pasture_monitoring", "point_id")
        natural_zone_layaer = LayerUtils.load_layer_by_name_pasture_monitoring("au_natural_zone", "code")
        vlayer = LayerUtils.load_union_layer_by_name("ca_pug_boundary", "code")
        vlayer_eco = LayerUtils.load_union_layer_by_name("ca_pug_eco", "code")
        vlayer_parcel = LayerUtils.load_union_layer_by_name("ca_pasture_parcel", "parcel_id")
        vlayer_building = LayerUtils.load_union_layer_by_name("ca_pasture_building", "building_id")
        # vlayer_monitoring_point = LayerUtils.load_layer_by_name_report("ca_pasture_monitoring", "point_id", restrictions)

        layers = self.plugin.iface.legendInterface().layers()

        for layer in layers:
            if layer.name() == "PUGBuilding" or layer.name() == u"БАХ байшин":
                is_pug_building = True
        if not is_pug_building:
            mygroup.addLayer(vlayer_building)

        for layer in layers:
            if layer.name() == "PUGParcel" or layer.name() == u"БАХ нэгж талбар":
                is_pug_parcel = True
        if not is_pug_parcel:
            mygroup.addLayer(vlayer_parcel)

        for layer in layers:
            if layer.name() == "PUGBoundary" or layer.name() == u"БАХ-ийн хил":
                is_layer = True
        if not is_layer:
            mygroup.addLayer(vlayer)

        for layer in layers:
            if layer.name() == "PUGEcological" or layer.name() == u"БАХ экологийн чадавхи":
                is_eco_layer = True
        if not is_eco_layer:
            mygroup.addLayer(vlayer_eco)

        for layer in layers:
            if layer.name() == "PastureMonitoringPoint" or layer.name() == u"Мониторингийн Цэг":
                is_monitoring_layer = True

        if not is_monitoring_layer:
            mygroup.addLayer(monitoring_layer)

        for layer in layers:
            if layer.name() == "NaturalZone" or layer.name() == u"Байгалийн бүс, бүслүүр":
                is_natural_zone_layer = True
        if not is_natural_zone_layer:
            mygroup.addLayer(natural_zone_layaer)

        vlayer.setLayerName(QApplication.translate("Plugin", "PUGBoundary"))
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "template\style/pug_boundary.qml")
        vlayer_eco.setLayerName(QApplication.translate("Plugin", "PUGEcological"))
        vlayer_eco.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "template\style/pug_eco.qml")
        vlayer_parcel.setLayerName(QApplication.translate("Plugin", "PUGParcel"))
        vlayer_parcel.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "template\style/pug_parcel.qml")
        vlayer_building.setLayerName(QApplication.translate("Plugin", "PUGBuilding"))

        monitoring_layer.setLayerName(QApplication.translate("Plugin", "PastureMonitoringPoint"))
        monitoring_layer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "template\style/ca_monitoring_point.qml")

        natural_zone_layaer.setLayerName(QApplication.translate("Plugin", "NaturalZone"))
        natural_zone_layaer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))[:-10]) + "template\style/ca_nat_zone_marged.qml")

        # legend = self.plugin.iface.legendInterface()  # access the legend
        # legend.setLayerVisible(vlayer, False)
        # legend.setLayerVisible(vlayer_eco, False)

    def __calculate_capacity(self, area, biomass_present, duration):

        if duration > 0:
            d3 = int(float(area) * biomass_present / float(duration * 1.4))
        else:
            d3 = int(float(area) * biomass_present / float(1 * 1.4))
        return d3

    @pyqtSlot(int)
    def on_reserve_zone_cbox_currentIndexChanged(self, index):

        self.reserve_parcel_cbox.clear()
        otor_zone_id = self.reserve_zone_cbox.itemData(self.reserve_zone_cbox.currentIndex(), Qt.UserRole)
        if not otor_zone_id:
            return
        if otor_zone_id != -1:
            otor_zones = self.session.query(AuReserveZone).filter(AuReserveZone.code == otor_zone_id).one()
            otor_parcels = self.session.query(PsParcel).filter(
                PsParcel.geometry.ST_Intersects(otor_zones.geometry)).all()

            if otor_parcels is not None:
                for parcel in otor_parcels:
                    address_neighbourhood = ''
                    if parcel.address_neighbourhood:
                        address_neighbourhood = parcel.address_neighbourhood
                    self.reserve_parcel_cbox.addItem(parcel.parcel_id + ' | ' + address_neighbourhood, parcel.parcel_id)

    def __is_number(self, s):

        try:
            float(s)  # for int, long and float
        except ValueError:
            try:
                complex(s)  # for complex
            except ValueError:
                return False

        return True

    @pyqtSignature("")
    def on_delete_button_clicked(self):

        selected_items = self.parcel_results_twidget.selectedItems()

        if len(selected_items) != 1:
            self.error_label.setText(self.tr("Only single selection allowed."))
            return None

        selected_item = selected_items[0]
        app_no = selected_item.data(Qt.UserRole)
        app_id = selected_item.data(Qt.UserRole+1)

        message_box = QMessageBox()
        message_box.setText(self.tr("Do you want to delete the all information for application ?"))

        delete_button = message_box.addButton(self.tr("Delete"), QMessageBox.ActionRole)
        message_box.addButton(self.tr("Cancel"), QMessageBox.ActionRole)
        message_box.exec_()

        if not message_box.clickedButton() == delete_button:
            return

        app_pugs = self.session.query(CtApplicationPUG).\
            filter(CtApplicationPUG.application == app_id).all()

        for app_pug in app_pugs:
            self.session.query(CtApplicationPUG). \
                filter(CtApplicationPUG.group_no == app_pug.group_no).\
                filter(CtApplicationPUG.application == app_id).delete()

        app_pug_parcels = self.session.query(CtApplicationPUGParcel).\
            filter(CtApplicationPUGParcel.application == app_id).all()

        for app_pug_parcel in app_pug_parcels:
            self.session.query(CtApplicationPUGParcel). \
                filter(CtApplicationPUGParcel.parcel == app_pug_parcel.parcel).\
                filter(CtApplicationPUGParcel.application == app_id).delete()

        app_persons = self.session.query(CtApplicationPersonRole).\
            filter(CtApplicationPersonRole.application == app_id).all()

        for app_person in app_persons:
            self.session.query(CtApplicationPersonRole). \
                filter(CtApplicationPersonRole.person == app_person.person). \
                filter(CtApplicationPersonRole.role == 10). \
                filter(CtApplicationPersonRole.application == app_id).delete()

        app_parcels = self.session.query(CtApplicationParcelPasture).\
            filter(CtApplicationParcelPasture.application == app_id).all()

        for app_parcel in app_parcels:
            self.session.query(CtApplicationParcelPasture). \
                filter(CtApplicationParcelPasture.pasture == app_parcel.pasture). \
                filter(CtApplicationParcelPasture.parcel == app_parcel.parcel).\
                filter(CtApplicationParcelPasture.application == app_id).delete()

        app_statuses = self.session.query(CtApplicationStatus).\
            filter(CtApplicationStatus.application == app_id).all()

        for app_status in app_statuses:
            self.session.query(CtApplicationStatus). \
                filter(CtApplicationStatus.status == app_status.status).\
                filter(CtApplicationStatus.application == app_id).delete()

        app_group_boundaries = self.session.query(CtAppGroupBoundary).\
            filter(CtAppGroupBoundary.application == app_id).all()

        for app_group_boundary in app_group_boundaries:
            self.session.query(CtAppGroupBoundary). \
                filter(CtAppGroupBoundary.boundary_code == app_group_boundary.boundary_code). \
                filter(CtAppGroupBoundary.group_no == app_group_boundary.group_no).\
                filter(CtAppGroupBoundary.application == app_id).delete()

        self.session.query(CtApplication).filter(CtApplication.app_id == app_id).delete()

        selected_row = self.parcel_results_twidget.currentRow()
        self.parcel_results_twidget.removeRow(selected_row)

        self.session.commit()
