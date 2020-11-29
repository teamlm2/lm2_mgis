# -*- encoding: utf-8 -*-
import os.path

from trace import Trace
from controller.ConnectionToMainDatabaseDialog import *
from controller.OfficialDocumentsDialog import OfficialDocumentsDialog
from controller.LandOfficeAdministrativeSettingsDialog import *
from controller.UserRoleManagementDialog import *
from controller.NavigatorWidget import *
from controller.NavigatorMainWidget import *
from controller.PastureWidget import *
from controller.SpaParcelWidget import *
from controller.ParcelInfoDialog import *
from controller.ParcelMpaDialog import *
from controller.ParcelInfoFeeDialog import *
from controller.PlanNavigatorWidget import *
from controller.PlanSettingsDialog import *
from controller.CamaNavigatorWidget import *
from controller.AddressNavigatorWidget import *
from controller.ApplicationsDialog import *
from controller.ContractDialog import *
from controller.OwnRecordDialog import *
from controller.ImportDecisionDialog import *
from controller.LogOnDialog import *
from controller.CreateCaseDialog import CreateCaseDialog
from controller.SentToGovernorDialog import *
from controller.PrintCadastreExtractMapTool import *
from controller.PrintOtherParcelExtractMapTool import *
from controller.ParcelInfoExtractMapTool import *
from controller.ParcelMpaEditMapTool import *
from controller.PrintPointExtractMapTool import *
from controller.CamaInfoExtractMapTool import *
from controller.AboutDialog import *
from controller.ReportDialog import *
from utils.DatabaseUtils import *
from utils.PluginUtils import PluginUtils
from utils.SessionHandler import SessionHandler
from utils.LM2Logger import LM2Logger
from model import SettingsConstants
from model.SetRightTypeApplicationType import *
from model.DialogInspector import DialogInspector
from model.SetUserGroupRole import *
from controller.ManageParcelRecordsDialog import *
from controller.DatabaseDump import *
from controller.WebgisUtilityDialog import *
from controller.PdfInsertDialog import *
from view.resources_rc import *
import qgis.core
from qgis.core import QgsRasterLayer

class LM2Plugin:

    def __init__(self, iface):

        # Save reference to the QGIS interface
        self.iface = iface
        self.activeAction = None
        self.activeParcelAction = None
        self.parcel_no = None
        self.result_feature = None
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        self.navigatorWidget = None
        override_locale = QSettings().value("locale/overrideFlag", False, type=bool)
        if not override_locale:
            locale = QLocale.system().name()
        else:
            locale = QSettings().value("locale/userLocale", "", type=str)

        self.translator = QTranslator()
        if self.translator.load("LM2Plugin_" + locale, self.plugin_dir):
            QApplication.installTranslator(self.translator)

        self.__add_repository()
        self.is_expired = True
        self.__layers_permission()

    def __add_repository(self):

        repository = QSettings().value(SettingsConstants.REPOSITORY_URL, None)
        if repository is None:
            QSettings().setValue(SettingsConstants.REPOSITORY_URL, Constants.REPOSITORY_URL)
            QSettings().setValue(SettingsConstants.REPOSITORY_ENABLED, True)

    def __create_db_session(self, password):

        user = QSettings().value(SettingsConstants.USER)
        db = QSettings().value(SettingsConstants.DATABASE_NAME)
        host = QSettings().value(SettingsConstants.HOST)
        port = QSettings().value(SettingsConstants.PORT, "5432")

        SessionHandler().create_session(user, password, host, port, db)

    def __destroy_db_session(self):

        SessionHandler().destroy_session()

    def initGui(self):

        self.toolButton = QToolButton()
        self.toolButton.setMenu(QMenu())
        self.toolButton.setPopupMode(QToolButton.MenuButtonPopup)
        # self.iface.addToolBarWidget(self.toolButton)

        # Create action that will start plugin configuration
        self.set_db_connection = QAction(QIcon(":/plugins/lm2/connection_to_main.png"), QApplication.translate("Plugin", "Set Connection To Main Database"), self.iface.mainWindow())
        self.user_role_management_action = QAction(QIcon(":/plugins/lm2/user_role_management.png"), QApplication.translate("Plugin", "User Role Management"), self.iface.mainWindow())
        self.admin_settings_action = QAction(QIcon(":/plugins/lm2/land_office_admin.png"), QApplication.translate("Plugin", "Administrative Settings"), self.iface.mainWindow())
        self.help_action = QAction(QIcon(":/plugins/lm2/help_button.png"), QApplication.translate("Plugin", "Help"), self.iface.mainWindow())
        self.create_case_action = QAction(QIcon(":/plugins/lm2/case.png"), QApplication.translate("Plugin", "Create Maintenance Case"), self.iface.mainWindow())
        self.import_data_action = QAction(QIcon(":/plugins/lm2/case.png"),
                                          QApplication.translate("Plugin", "Convert Data"),
                                          self.iface.mainWindow())
        self.person_action = QAction(QIcon(":/plugins/lm2/person.png"), QApplication.translate("Plugin", "Add Person"), self.iface.mainWindow())

        self.applications_action = QAction(QIcon(":/plugins/lm2/application.png"), QApplication.translate("Plugin", "Add Application"), self.iface.mainWindow())
        self.contract_action = QAction(QIcon(":/plugins/lm2/contract.png"), QApplication.translate("Plugin", "Add Contract"), self.iface.mainWindow())
        self.ownership_action = QAction(QIcon(":/plugins/lm2/land_ownership.png"), QApplication.translate("Plugin", "Add Ownership Record"), self.iface.mainWindow())
        self.import_decision_action = QAction(QIcon(":/plugins/lm2/import_decision.png"), QApplication.translate("Plugin", "Import Decision"), self.iface.mainWindow())
        self.mark_apps_action = QAction(QIcon(":/plugins/lm2/send_to_governor.png"), QApplication.translate("Plugin", "Mark Apps As Sent To Governor"), self.iface.mainWindow())
        self.print_cadastre_map_action = QAction(QIcon(":/plugins/lm2/extract.png"), QApplication.translate("Plugin", "Print cadastre map"), self.iface.mainWindow())
        self.print_point_map_action = QAction(QIcon(":/plugins/lm2_pasture/point.png"),
                                                 QApplication.translate("Plugin", "Show pasture monitroing point information"),
                                                 self.iface.mainWindow())
        # self.print_cadastre_map_action.setCheckable(True)


        self.about_action = QAction(QIcon(":/plugins/lm2/about.png"), QApplication.translate("Plugin", "About"), self.iface.mainWindow())
        self.document_action = QAction(QIcon(":/plugins/lm2/documents.png"), QApplication.translate("Plugin", "Official documents"), self.iface.mainWindow())
        # self.manage_parcel_records_action = QAction(QIcon(":/plugins/lm2/landfeepayment.png"), QApplication.translate("Plugin", "Manage Parcel Record"), self.iface.mainWindow())
        self.cama_navigator_action = QAction(QIcon(":/plugins/lm2/landfeepayment.png"),
                                         QApplication.translate("Plugin", "Parcel Mpa Info"),
                                         self.iface.mainWindow())
        self.cama_navigator_action.setCheckable(True)
        self.database_dump_action = QAction(QIcon(":/plugins/lm2/landfeepayment.png"), QApplication.translate("Plugin", "Database Dump"), self.iface.mainWindow())

        self.webgis_utility_action = QAction(QIcon(":/plugins/lm2/webgis.png"), QApplication.translate("Plugin", "WebGIS Utility"), self.iface.mainWindow())
        # self.reports_action = QAction(QIcon(":/plugins/lm2/landfeepayment.png"), QApplication.translate("Plugin", "GTs Reports"), self.iface.mainWindow())

        ###
        self.navigator_action = QAction(QIcon(":/plugins/lm2/navigator.png"),
                                        QApplication.translate("Plugin", "Show/Hide Navigator"),
                                        self.iface.mainWindow())
        self.navigator_action.setCheckable(True)

        ###
        self.address_action = QAction(QIcon(":/plugins/lm2/address_1.png"),
                                        QApplication.translate("Plugin", "Show/Hide Address Controller"),
                                        self.iface.mainWindow())
        self.address_action.setCheckable(True)
        ###
        self.pasture_use_action = QAction(QIcon(":/plugins/lm2_pasture/crops.png"),
                                        QApplication.translate("Plugin", "PUA / ER"),
                                        self.iface.mainWindow())
        self.pasture_use_action.setCheckable(True)
        ###
        self.nature_reserve_action = QAction(QIcon(":/plugins/lm2/nature_reserve.png"),
                                             QApplication.translate("Plugin",
                                                                    "Nature reserve"),
                                             self.iface.mainWindow())
        self.nature_reserve_action.setCheckable(True)
        ###
        self.parcel_map_action = QAction(QIcon(":/plugins/lm2/parcel_grey.png"),
                                         QApplication.translate("Plugin", "Parcel Info"),
                                         self.iface.mainWindow())
        self.parcel_map_action.setCheckable(True)
        ###
        self.parcel_mpa_action = QAction(QIcon(":/plugins/lm2/mpa_logo.png"),
                                         QApplication.translate("Plugin", "Parcel Mpa Info"),
                                         self.iface.mainWindow())
        self.parcel_mpa_action.setCheckable(True)

        ###
        self.parcel_spa_action = QAction(QIcon(":/plugins/lm2/spa_logo.png"),
                                         QApplication.translate("Plugin", "SPA Parcel Info"),
                                         self.iface.mainWindow())
        self.parcel_spa_action.setCheckable(True)

        ### GZBT navigator
        self.land_plan_settings_action = QAction(QIcon(":/plugins/lm2/land_office_admin.png"),
                                                  QApplication.translate("Plugin", "Land plan settings"),
                                                  self.iface.mainWindow())

        self.land_plan_navigator_action = QAction(QIcon(":/plugins/lm2/land_plan.png"),
                                         QApplication.translate("Plugin", "Land plan info"),
                                         self.iface.mainWindow())
        self.land_plan_navigator_action.setCheckable(True)

        m = self.toolButton.menu()
        m.addAction(self.land_plan_navigator_action)
        m.addAction(self.land_plan_settings_action)
        self.toolButton.setDefaultAction(self.land_plan_navigator_action)

        # connect the action to the run method
        self.set_db_connection.triggered.connect(self.__show_connection_to_main_database_dialog)
        self.admin_settings_action.triggered.connect(self.__show_land_office_admin_settings_dialog)
        self.user_role_management_action.triggered.connect(self.__show_user_role_management_dialog)
        self.help_action.triggered.connect(self.__show_help)
        self.person_action.triggered.connect(self.__show_person_dialog)
        self.navigator_action.triggered.connect(self.__show_navigator_widget)
        self.applications_action.triggered.connect(self.__show_applications_dialog)
        self.contract_action.triggered.connect(self.__show_contract_dialog)
        self.ownership_action.triggered.connect(self.__show_ownership_dialog)
        self.mark_apps_action.triggered.connect(self.__mark_apps_as_send_to_govenor)
        self.create_case_action.triggered.connect(self.__show_create_case_dialog)
        self.import_data_action.triggered.connect(self.__show_import_data_dialog)

        self.import_decision_action.triggered.connect(self.__show_import_decision_dialog)
        self.document_action.triggered.connect(self.__show_documents_dialog)
        self.about_action.triggered.connect(self.__show_about_dialog)
        self.print_cadastre_map_action.triggered.connect(self.__start_print_cadastre_map)
        self.print_cadastre_map_action.setCheckable(True)

        self.print_point_map_action.triggered.connect(self.__start_print_point_map)
        self.print_point_map_action.setCheckable(True)

        # self.manage_parcel_records_action.triggered.connect(self.__show_manage_parcel_records_dialog)
        self.cama_navigator_action.triggered.connect(self.__show_cama_navigator_widget)
        self.address_action.triggered.connect(self.__show_address_navigator_widget)
        self.database_dump_action.triggered.connect(self.__show_database_dump_dialog)
        self.webgis_utility_action.triggered.connect(self.__show_webgis_utility_action)
        self.pasture_use_action.triggered.connect(self.__show_pasture_navigator_widget)
        self.nature_reserve_action.triggered.connect(self.__show_natural_reserve_navigator_widget)
        self.parcel_map_action.triggered.connect(self.__show_parcel_navigator_widget)
        self.parcel_mpa_action.triggered.connect(self.__show_parcel_mpa_navigator_widget)
        self.parcel_spa_action.triggered.connect(self.__show_parcel_spa_navigator_widget)
        # self.reports_action.triggered.connect(self.__show_reports_dialog)
        self.land_plan_navigator_action.triggered.connect(self.__show_plan_navigator_widget)
        self.land_plan_settings_action.triggered.connect(self.__show_plan_settings_dialog)

        # Add toolbar button and menu item
        self.lm_toolbar = self.iface.addToolBar(QApplication.translate("Plugin", "LandManager 2"))

        self.lm_toolbar.addSeparator()
        self.lm_toolbar.addAction(self.address_action)
        self.lm_toolbar.addAction(self.parcel_map_action)
        self.lm_toolbar.addAction(self.parcel_mpa_action)
        self.lm_toolbar.addAction(self.parcel_spa_action)
        self.lm_toolbar.addSeparator()
        self.lm_toolbar.addSeparator()
        # self.lm_toolbar.addAction(self.manage_parcel_records_action)
        self.lm_toolbar.addAction(self.cama_navigator_action)
        self.lm_toolbar.addSeparator()
        self.lm_toolbar.addSeparator()
        self.lm_toolbar.addAction(self.pasture_use_action)
        self.lm_toolbar.addAction(self.print_point_map_action)
        self.lm_toolbar.addAction(self.nature_reserve_action)
        self.lm_toolbar.addSeparator()
        self.lm_toolbar.addSeparator()
        # self.lm_toolbar.addAction(self.land_plan_navigator_action)
        self.lm_toolbar.addWidget(self.toolButton)
        self.lm_toolbar.addSeparator()
        self.lm_toolbar.addSeparator()
        self.lm_toolbar.addAction(self.navigator_action)
        self.lm_toolbar.addAction(self.create_case_action)
        self.lm_toolbar.addAction(self.print_cadastre_map_action)
        # self.lm_toolbar.addSeparator()
        self.lm_toolbar.addAction(self.mark_apps_action)
        self.lm_toolbar.addAction(self.import_decision_action)

        self.lm_toolbar.addSeparator()

        self.lm_toolbar.addAction(self.webgis_utility_action)
        self.lm_toolbar.addAction(self.document_action)
        self.lm_toolbar.addSeparator()
        self.lm_toolbar.addSeparator()
        self.lm_toolbar.addAction(self.admin_settings_action)
        self.lm_toolbar.addAction(self.user_role_management_action)
        self.lm_toolbar.addAction(self.set_db_connection)
        self.lm_toolbar.addSeparator()

        # Retrieve main menu bar
        menu_bar = self.iface.mainWindow().menuBar()
        actions = menu_bar.actions()

        # Create menus
        self.lm_menu = QMenu()
        self.lm_menu.setTitle(QApplication.translate("Plugin", "&LM2_MGIS"))
        menu_bar.addMenu(self.lm_menu)

        # Cadastre menu
        self.cadastre_menu = QMenu()
        self.cadastre_menu.setTitle(QApplication.translate("Plugin", "Cadastre"))
        self.cadastre_menu.addAction(self.print_cadastre_map_action)
        self.cadastre_menu.addAction(self.create_case_action)
        self.cadastre_menu.addSeparator()
        self.cadastre_menu.addAction(self.import_data_action)

        # self.toolButton = QToolButton()
        #
        # self.toolButton.setMenu( self.cadastre_menu )
        # self.toolButton.setDefaultAction( self.create_case_action )
        # self.toolButton.setPopupMode( QToolButton.InstantPopup )
        # self.iface.addToolBarWidget( self.toolButton )

        #Applications/Decisions menu
        self.application_menu = QMenu()
        self.application_menu.setTitle(QApplication.translate("Plugin", "Applications/Decisions"))
        self.application_menu.addAction(self.person_action)
        self.application_menu.addAction(self.applications_action)
        self.application_menu.addSeparator()
        self.application_menu.addAction(self.mark_apps_action)
        self.application_menu.addAction(self.import_decision_action)

        #Contract/Ownership menu
        self.contract_menu = QMenu()
        self.contract_menu.setTitle(QApplication.translate("Plugin", "Contract/Ownership"))
        self.contract_menu.addAction(self.contract_action)
        self.contract_menu.addAction(self.ownership_action)

        # Add actions and menus to LM2 menu
        self.lm_menu.addAction(self.document_action)
        self.lm_menu.addAction(self.set_db_connection)
        self.lm_menu.addAction(self.admin_settings_action)
        self.lm_menu.addAction(self.user_role_management_action)
        self.lm_menu.addSeparator()
        self.lm_menu.addMenu(self.cadastre_menu)
        self.lm_menu.addMenu(self.application_menu)
        self.lm_menu.addSeparator()
        self.lm_menu.addMenu(self.contract_menu)
        self.lm_menu.addSeparator()
        self.lm_menu.addAction(self.navigator_action)
        # self.lm_menu.addAction(self.manage_parcel_records_action)
        self.lm_menu.addAction(self.database_dump_action)
        self.lm_menu.addAction(self.webgis_utility_action)
        self.lm_menu.addSeparator()
        self.lm_menu.addAction(self.pasture_use_action)
        self.lm_menu.addAction(self.nature_reserve_action)
        self.lm_menu.addAction(self.parcel_spa_action)
        # self.lm_menu.addAction(self.print_point_map_action)
        self.lm_menu.addSeparator()
        self.lm_menu.addAction(self.help_action)
        self.lm_menu.addAction(self.about_action)

        self.navigatorWidget = None
        self.parcelInfoWidget = None
        self.pastureWidget = None
        self.naturalReserveWidget = None
        self.spaParcelWidget = None
        self.parcelMpaInfoWidget = None
        self.planWidget = None
        self.planDetailWidget = None
        self.camaWidget = None
        self.addressWidget = None
        self.removeLayers()
        self.__set_menu_visibility()
        self.__setup_slots()

    def unload(self):

        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.create_case_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.import_decision_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.applications_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.person_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.contract_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.ownership_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.navigator_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.admin_settings_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.set_db_connection)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.user_role_management_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.help_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.print_cadastre_map_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.parcel_map_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.document_action)
        # self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.manage_parcel_records_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.cama_navigator_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.address_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.database_dump_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.webgis_utility_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.pasture_use_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.nature_reserve_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.parcel_spa_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.print_point_map_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.land_plan_navigator_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.land_plan_settings_action)


        del self.lm_toolbar

        if self.navigatorWidget:
            self.iface.removeDockWidget(self.navigatorWidget)
            del self.navigatorWidget

        if self.pastureWidget:
            self.iface.removeDockWidget(self.pastureWidget)
            del self.pastureWidget

        if self.naturalReserveWidget:
            self.iface.removeDockWidget(self.naturalReserveWidget)
            del self.naturalReserveWidget

        if self.spaParcelWidget:
            self.iface.removeDockWidget(self.spaParcelWidget)
            del self.spaParcelWidget

        if self.parcelInfoWidget:
            self.iface.removeDockWidget(self.parcelInfoWidget)
            del self.parcelInfoWidget

        if self.parcelMpaInfoWidget:
            self.iface.removeDockWidget(self.parcelMpaInfoWidget)
            del self.parcelMpaInfoWidget

        if self.planWidget:
            self.iface.removeDockWidget(self.planWidget)
            del self.planWidget

        self.removeLayers()

    def __setup_slots(self):

        QObject.connect(QgsMapLayerRegistry.instance(), SIGNAL("layerWasAdded(QgsMapLayer*)"), self.__update_database_connection)

    def __show_connection_to_main_database_dialog(self):

        if DialogInspector().dialog_visible():
            return

        dlg = ConnectionToMainDatabaseDialog(self.iface, self.iface.mainWindow())

        DialogInspector().set_dialog_visible(True)
        dlg.rejected.connect(self.on_current_dialog_rejected)
        if not dlg.exec_():
            if dlg.get_is_version():
                self.__disable_menu()
                return
            if self.navigatorWidget != None:
                if self.navigatorWidget.isVisible():
                    self.navigatorWidget.hide()

            if self.parcelInfoWidget != None:
                if self.parcelInfoWidget.isVisible():
                    self.parcelInfoWidget.hide()

            if self.pastureWidget != None:
                if self.pastureWidget.isVisible():
                    self.pastureWidget.hide()

            if self.naturalReserveWidget != None:
                if self.naturalReserveWidget.isVisible():
                    self.naturalReserveWidget.hide()

            if self.spaParcelWidget != None:
                if self.spaParcelWidget.isVisible():
                    self.spaParcelWidget.hide()

            if self.parcelMpaInfoWidget != None:
                if self.parcelMpaInfoWidget.isVisible():
                    self.parcelMpaInfoWidget.hide()

            if self.planWidget != None:
                if self.planWidget.isVisible():
                    self.planWidget.hide()

            SessionHandler().destroy_session()
            self.is_expired = dlg.get_expired()

            self.__update_database_connection(dlg.get_password(), self.is_expired)
        else:
            self.__disable_menu()
            SessionHandler().destroy_session()

    def __show_reports_dialog(self):

        dlg = ReportDialog()
        dlg.exec_()

    def __show_manage_parcel_records_dialog(self):

        dlg = ManageParcelRecordsDialog()
        dlg.exec_()

    def __show_database_dump_dialog(self):

        dlg = DatabaseDump()
        dlg.exec_()

    def __show_webgis_utility_action(self):

        dlg = WebgisUtilityDialog()
        dlg.exec_()

    def __show_import_data_dialog(self):

        dlg = PdfInsertDialog()
        dlg.exec_()


    def __show_create_case_dialog(self):

        if DialogInspector().dialog_visible():
            return

        DatabaseUtils.set_working_schema()
        m_case = PluginUtils.create_new_m_case()

        message_box = QMessageBox()
        message_box.setWindowTitle(QApplication.translate("LM2", "Create cadastre update case"))
        message_box.setWindowFlags(message_box.windowFlags() | Qt.WindowTitleHint)
        message_box.setText(QApplication.translate("LM2", "If you going to add new parcel, Please choose the New Parcel or " \
                                                          "If you going to chagne base parcel, Please choose the Base Parcel"))

        new_parcel_button = message_box.addButton(QApplication.translate("LM2", "New Parcel"), QMessageBox.ActionRole)
        new_parcel_button.setDisabled(false)

        user_name = QSettings().value(SettingsConstants.USER)
        user_right = DatabaseUtils.userright_by_name(user_name)
        if user_right:
            if UserRight.db_creation in user_right:
                new_parcel_button.setDisabled(True)
        message_box.addButton(QApplication.translate("LM2", "Base Parcel"), QMessageBox.ActionRole)
        message_box.exec_()
        restrictions = DatabaseUtils.working_l2_code()
        parcelLayer = LayerUtils.layer_by_data_source("data_soums_union", "ca_parcel")
        if message_box.clickedButton() == new_parcel_button:
            parcelLayer.removeSelection()
            self.iface.mapCanvas().refresh()
            self.create_case_dialog = CreateCaseDialog(self, m_case, False, self.iface.mainWindow())

            self.create_case_dialog.setModal(False)
            self.create_case_dialog.show()
        else:
            count = parcelLayer.selectedFeatureCount()
            if count != 1:
                QMessageBox.information(None, QApplication.translate("LM2", "No parcel"),
                                        QApplication.translate("LM2", "No select parcel"))
                return
            self.create_case_dialog = CreateCaseDialog(self, m_case, False, self.iface.mainWindow())
            self.create_case_dialog.setModal(False)
            self.create_case_dialog.show()

    def __show_land_office_admin_settings_dialog(self):

        user = QSettings().value(SettingsConstants.USER)

        if user == '':
            QMessageBox.information(None, QApplication.translate("LM2", "Role Error"),
                                        QApplication.translate("LM2", "No User Connection To Main Database"))
            return
        if DialogInspector().dialog_visible():
            return

        dlg = LogOnDialog(Constants.LAND_ADMIN_SETTINGS_DLG)
        if not dlg.exec_():
            if self.navigatorWidget != None:
                if self.navigatorWidget.isVisible():
                    self.navigatorWidget.hide()
                else:
                    self.navigatorWidget.show()
                self.__disable_menu()
                QMessageBox.information(None, QApplication.translate("LM2", "Database disconnect"),
                                        QApplication.translate("LM2",
                                                               "Please connect to database!!!"))
                if DialogInspector().dialog_visible():
                    return

                dlg = ConnectionToMainDatabaseDialog(self.iface, self.iface.mainWindow())

                DialogInspector().set_dialog_visible(True)
                dlg.rejected.connect(self.on_current_dialog_rejected)
                dlg.exec_()

                SessionHandler().destroy_session()
                self.is_expired = dlg.get_expired()
                self.__update_database_connection(dlg.get_password(), self.is_expired)
        else:
            if self.navigatorWidget != None:
                if self.navigatorWidget.isVisible():
                    self.navigatorWidget.hide()
                else:
                    self.navigatorWidget.show()
                self.__disable_menu()
                QMessageBox.information(None, QApplication.translate("LM2", "Database disconnect"),
                                        QApplication.translate("LM2",
                                                               "Please connect to database!!!"))
                if DialogInspector().dialog_visible():
                    return

                dlg = ConnectionToMainDatabaseDialog(self.iface, self.iface.mainWindow())

                DialogInspector().set_dialog_visible(True)
                dlg.rejected.connect(self.on_current_dialog_rejected)
                dlg.exec_()

                SessionHandler().destroy_session()
                self.is_expired = dlg.get_expired()
                self.__update_database_connection(dlg.get_password(), self.is_expired)

    def __show_user_role_management_dialog(self):

        if DialogInspector().dialog_visible():
            return

        dlg = LogOnDialog(Constants.ROLE_MANAGEMENT_DLG)
        if not dlg.exec_():
            if self.navigatorWidget != None:
                if self.navigatorWidget.isVisible():
                    self.navigatorWidget.hide()
                else:
                    self.navigatorWidget.show()
                self.__disable_menu()
                QMessageBox.information(None, QApplication.translate("LM2", "Database disconnect"),
                                        QApplication.translate("LM2",
                                                               "Please connect to database!!!"))
                if DialogInspector().dialog_visible():
                    return

                dlg = ConnectionToMainDatabaseDialog(self.iface, self.iface.mainWindow())

                DialogInspector().set_dialog_visible(True)
                dlg.rejected.connect(self.on_current_dialog_rejected)
                dlg.exec_()

                SessionHandler().destroy_session()
                self.is_expired = dlg.get_expired()
                self.__update_database_connection(dlg.get_password(), self.is_expired)
        else:
            if self.navigatorWidget != None:
                if self.navigatorWidget.isVisible():
                    self.navigatorWidget.hide()
                else:
                    self.navigatorWidget.show()
                self.__disable_menu()
                QMessageBox.information(None, QApplication.translate("LM2", "Database disconnect"),
                                        QApplication.translate("LM2",
                                                               "Please connect to database!!!"))
                if DialogInspector().dialog_visible():
                    return

                dlg = ConnectionToMainDatabaseDialog(self.iface, self.iface.mainWindow())

                DialogInspector().set_dialog_visible(True)
                dlg.rejected.connect(self.on_current_dialog_rejected)
                dlg.exec_()

                SessionHandler().destroy_session()
                self.is_expired = dlg.get_expired()
                self.__update_database_connection(dlg.get_password(), self.is_expired)

    def __show_person_dialog(self):

        if DialogInspector().dialog_visible():
            return

        person = BsPerson()
        dialog = PersonDialog(person)
        DialogInspector().set_dialog_visible(True)
        dialog.rejected.connect(self.on_current_dialog_rejected)
        dialog.exec_()

    def __show_navigator_widget(self):

        if self.navigatorWidget.isVisible():
            if self.navigatorWidget:
                self.navigatorWidget.hide()
        else:
            if self.navigatorWidget:
                self.navigatorWidget.show()
            if self.pastureWidget:
                self.pastureWidget.hide()
            if self.naturalReserveWidget:
                self.naturalReserveWidget.hide()
            if self.spaParcelWidget:
                self.spaParcelWidget.hide()
            if self.parcelInfoWidget:
                self.parcelInfoWidget.hide()
            if self.parcelMpaInfoWidget:
                self.parcelMpaInfoWidget.hide()
            if self.planWidget:
                self.planWidget.hide()
            if self.camaWidget:
                self.camaWidget.hide()
            if self.addressWidget:
                self.addressWidget.hide()

    def __show_pasture_navigator_widget(self):

        self.pastureWidget = None
        if self.pastureWidget:
            self.iface.removeDockWidget(self.pastureWidget)
            del self.pastureWidget

        if self.pastureWidget:
            if self.pastureWidget.isVisible():
                if self.pastureWidget:
                    self.pastureWidget.hide()
                if self.naturalReserveWidget:
                    self.naturalReserveWidget.hide()
                if self.parcelMpaInfoWidget:
                    self.parcelMpaInfoWidget.hide()
                if self.parcelInfoWidget:
                    self.parcelInfoWidget.hide()
                if self.planWidget:
                    self.planWidget.hide()
                if self.camaWidget:
                    self.camaWidget.hide()
                if self.addressWidget:
                    self.addressWidget.hide()
                if self.spaParcelWidget:
                    self.spaParcelWidget.hide()
                if self.navigatorWidget:
                    self.navigatorWidget.show()
            else:
                if self.pastureWidget:
                    self.pastureWidget.show()
                if self.navigatorWidget:
                    self.navigatorWidget.hide()
                if self.parcelMpaInfoWidget:
                    self.parcelMpaInfoWidget.hide()
                if self.parcelInfoWidget:
                    self.parcelInfoWidget.hide()
                if self.planWidget:
                    self.planWidget.hide()
                if self.camaWidget:
                    self.camaWidget.hide()
                if self.addressWidget:
                    self.addressWidget.hide()
                if self.spaParcelWidget:
                    self.spaParcelWidget.hide()
                if self.naturalReserveWidget:
                    self.naturalReserveWidget.hide()
        else:
            self.__create_pasture()

    def __show_natural_reserve_navigator_widget(self):

        self.naturalReserveWidget = None
        if self.naturalReserveWidget:
            self.iface.removeDockWidget(self.naturalReserveWidget)
            del self.naturalReserveWidget

        if self.naturalReserveWidget:
            if self.naturalReserveWidget.isVisible():
                if self.pastureWidget:
                    self.pastureWidget.hide()
                if self.naturalReserveWidget:
                    self.naturalReserveWidget.hide()
                if self.parcelMpaInfoWidget:
                    self.parcelMpaInfoWidget.hide()
                if self.parcelInfoWidget:
                    self.parcelInfoWidget.hide()
                if self.planWidget:
                    self.planWidget.hide()
                if self.camaWidget:
                    self.camaWidget.hide()
                if self.addressWidget:
                    self.addressWidget.hide()
                if self.spaParcelWidget:
                    self.spaParcelWidget.hide()
                if self.navigatorWidget:
                    self.navigatorWidget.show()
            else:
                if self.naturalReserveWidget:
                    self.naturalReserveWidget.show()
                if self.navigatorWidget:
                    self.navigatorWidget.hide()
                if self.parcelMpaInfoWidget:
                    self.parcelMpaInfoWidget.hide()
                if self.parcelInfoWidget:
                    self.parcelInfoWidget.hide()
                if self.planWidget:
                    self.planWidget.hide()
                if self.camaWidget:
                    self.camaWidget.hide()
                if self.addressWidget:
                    self.addressWidget.hide()
                if self.spaParcelWidget:
                    self.spaParcelWidget.hide()
                if self.pastureWidget:
                    self.pastureWidget.hide()
        else:
            self.__create_nature_reserve()

    def __show_parcel_spa_navigator_widget(self):

        self.spaParcelWidget = None
        if self.spaParcelWidget:
            self.iface.removeDockWidget(self.spaParcelWidget)
            del self.spaParcelWidget

        if self.spaParcelWidget:
            if self.spaParcelWidget.isVisible():
                if self.spaParcelWidget:
                    self.spaParcelWidget.hide()
                if self.parcelMpaInfoWidget:
                    self.parcelMpaInfoWidget.hide()
                if self.parcelInfoWidget:
                    self.parcelInfoWidget.hide()
                if self.planWidget:
                    self.planWidget.hide()
                if self.camaWidget:
                    self.camaWidget.hide()
                if self.addressWidget:
                    self.addressWidget.hide()
                if self.pastureWidget:
                    self.pastureWidget.hide()
                if self.naturalReserveWidget:
                    self.naturalReserveWidget.hide()
                if self.navigatorWidget:
                    self.navigatorWidget.show()
            else:
                if self.spaParcelWidget:
                    self.spaParcelWidget.show()
                if self.navigatorWidget:
                    self.navigatorWidget.hide()
                if self.parcelMpaInfoWidget:
                    self.parcelMpaInfoWidget.hide()
                if self.parcelInfoWidget:
                    self.parcelInfoWidget.hide()
                if self.planWidget:
                    self.planWidget.hide()
                if self.camaWidget:
                    self.camaWidget.hide()
                if self.addressWidget:
                    self.addressWidget.hide()
                if self.pastureWidget:
                    self.pastureWidget.hide()
                if self.naturalReserveWidget:
                    self.naturalReserveWidget.hide()
        else:
            self.__create_spa_parcel()

    def __show_parcel_navigator_widget(self):

        # self.__create_parcel_info()
        self.parcelInfoWidget = None
        if self.parcelInfoWidget:
            self.iface.removeDockWidget(self.parcelInfoWidget)
            del self.parcelInfoWidget

        if self.parcelInfoWidget:
            if self.parcelInfoWidget.isVisible():
                if self.parcelInfoWidget:
                    self.parcelInfoWidget.hide()
                if self.parcelMpaInfoWidget:
                    self.parcelMpaInfoWidget.hide()
                if self.pastureWidget:
                    self.pastureWidget.hide()
                if self.planWidget:
                    self.planWidget.hide()
                if self.camaWidget:
                    self.camaWidget.hide()
                if self.addressWidget:
                    self.addressWidget.hide()
                if self.spaParcelWidget:
                    self.spaParcelWidget.hide()
                if self.naturalReserveWidget:
                    self.naturalReserveWidget.hide()
                if self.navigatorWidget:
                    self.navigatorWidget.show()
            else:
                if self.parcelInfoWidget:
                    self.parcelInfoWidget.show()
                if self.navigatorWidget:
                    self.navigatorWidget.hide()
                if self.parcelMpaInfoWidget:
                    self.parcelMpaInfoWidget.hide()
                if self.pastureWidget:
                    self.pastureWidget.hide()
                if self.spaParcelWidget:
                    self.spaParcelWidget.hide()
                if self.naturalReserveWidget:
                    self.naturalReserveWidget.hide()
                if self.planWidget:
                    self.planWidget.hide()
                if self.camaWidget:
                    self.camaWidget.hide()
                if self.addressWidget:
                    self.addressWidget.hide()
        else:
            self.__create_parcel_info()
        self.__start_parcel_info_map()

    def __show_parcel_mpa_navigator_widget(self):

        # self.__create_parcel_info()
        self.parcelMpaInfoWidget = None
        if self.parcelMpaInfoWidget:
            self.iface.removeDockWidget(self.parcelMpaInfoWidget)
            del self.parcelMpaInfoWidget

        if self.parcelMpaInfoWidget:
            if self.parcelMpaInfoWidget.isVisible():
                if self.parcelMpaInfoWidget:
                    self.parcelMpaInfoWidget.hide()
                if self.navigatorWidget:
                    self.navigatorWidget.hide()
                if self.pastureWidget:
                    self.pastureWidget.hide()
                if self.spaParcelWidget:
                    self.spaParcelWidget.hide()
                if self.naturalReserveWidget:
                    self.naturalReserveWidget.hide()
                if self.parcelInfoWidget:
                    self.parcelInfoWidget.hide()
                if self.planWidget:
                    self.planWidget.hide()
                if self.camaWidget:
                    self.camaWidget.hide()
                if self.addressWidget:
                    self.addressWidget.hide()
                if self.navigatorWidget:
                    self.navigatorWidget.show()
            else:
                if self.parcelMpaInfoWidget:
                    self.parcelMpaInfoWidget.show()
                if self.navigatorWidget:
                    self.navigatorWidget.hide()
                if self.pastureWidget:
                    self.pastureWidget.hide()
                if self.spaParcelWidget:
                    self.spaParcelWidget.hide()
                if self.naturalReserveWidget:
                    self.naturalReserveWidget.hide()
                if self.parcelInfoWidget:
                    self.parcelInfoWidget.hide()
                if self.planWidget:
                    self.planWidget.hide()
                if self.camaWidget:
                    self.camaWidget.hide()
                if self.addressWidget:
                    self.addressWidget.hide()
        else:
            self.__create_mpa()
        self.__start_parcel_mpa_map()

    def __show_address_navigator_widget(self):

        self.addressWidget = None
        if self.addressWidget:
            self.iface.removeDockWidget(self.addressWidget)
            del self.addressWidget

        if self.addressWidget:
            if self.addressWidget.isVisible():
                if self.addressWidget:
                    self.addressWidget.hide()
                if self.planWidget:
                    self.planWidget.hide()
                if self.pastureWidget:
                    self.pastureWidget.hide()
                if self.spaParcelWidget:
                    self.spaParcelWidget.hide()
                if self.parcelMpaInfoWidget:
                    self.parcelMpaInfoWidget.hide()
                if self.parcelInfoWidget:
                    self.parcelInfoWidget.hide()
                if self.naturalReserveWidget:
                    self.naturalReserveWidget.hide()
                if self.camaWidget:
                    self.camaWidget.hide()
                if self.navigatorWidget:
                    self.navigatorWidget.show()
            else:
                if self.addressWidget:
                    self.addressWidget.show()
                if self.planWidget:
                    self.planWidget.hide()
                if self.pastureWidget:
                    self.pastureWidget.hide()
                if self.spaParcelWidget:
                    self.spaParcelWidget.hide()
                if self.navigatorWidget:
                    self.navigatorWidget.hide()
                if self.parcelMpaInfoWidget:
                    self.parcelMpaInfoWidget.hide()
                if self.parcelInfoWidget:
                    self.parcelInfoWidget.hide()
                if self.naturalReserveWidget:
                    self.naturalReserveWidget.hide()
                if self.camaWidget:
                    self.camaWidget.hide()
        else:
            self.__create_address_navigator()
        # self.__start_cama_info_map()

    def __show_cama_navigator_widget(self):

        self.camaWidget = None
        if self.camaWidget:
            self.iface.removeDockWidget(self.camaWidget)
            del self.camaWidget

        if self.camaWidget:
            if self.camaWidget.isVisible():
                if self.camaWidget:
                    self.camaWidget.hide()
                if self.planWidget:
                    self.planWidget.hide()
                if self.pastureWidget:
                    self.pastureWidget.hide()
                if self.spaParcelWidget:
                    self.spaParcelWidget.hide()
                if self.parcelMpaInfoWidget:
                    self.parcelMpaInfoWidget.hide()
                if self.parcelInfoWidget:
                    self.parcelInfoWidget.hide()
                if self.naturalReserveWidget:
                    self.naturalReserveWidget.hide()
                if self.navigatorWidget:
                    self.navigatorWidget.show()
                if self.addressWidget:
                    self.addressWidget.hide()
            else:
                if self.camaWidget:
                    self.camaWidget.show()
                if self.planWidget:
                    self.planWidget.hide()
                if self.pastureWidget:
                    self.pastureWidget.hide()
                if self.spaParcelWidget:
                    self.spaParcelWidget.hide()
                if self.navigatorWidget:
                    self.navigatorWidget.hide()
                if self.parcelMpaInfoWidget:
                    self.parcelMpaInfoWidget.hide()
                if self.parcelInfoWidget:
                    self.parcelInfoWidget.hide()
                if self.naturalReserveWidget:
                    self.naturalReserveWidget.hide()
                if self.addressWidget:
                    self.addressWidget.hide()
        else:
            self.__create_cama_navigator()
        self.__start_cama_info_map()

    def __show_plan_settings_dialog(self):

        dlg = PlanSettingsDialog()
        dlg.exec_()

    def __show_plan_navigator_widget(self):

        self.planWidget = None
        if self.planWidget:
            self.iface.removeDockWidget(self.planWidget)
            del self.planWidget

        if self.planWidget:
            if self.planWidget.isVisible():
                if self.planWidget:
                    self.planWidget.hide()
                if self.pastureWidget:
                    self.pastureWidget.hide()
                if self.spaParcelWidget:
                    self.spaParcelWidget.hide()
                if self.parcelMpaInfoWidget:
                    self.parcelMpaInfoWidget.hide()
                if self.parcelInfoWidget:
                    self.parcelInfoWidget.hide()
                if self.camaWidget:
                    self.camaWidget.hide()
                if self.addressWidget:
                    self.addressWidget.hide()
                if self.naturalReserveWidget:
                    self.naturalReserveWidget.hide()
                if self.navigatorWidget:
                    self.navigatorWidget.show()
            else:
                if self.planWidget:
                    self.planWidget.show()
                if self.pastureWidget:
                    self.pastureWidget.hide()
                if self.spaParcelWidget:
                    self.spaParcelWidget.hide()
                if self.naturalReserveWidget:
                    self.naturalReserveWidget.hide()
                if self.navigatorWidget:
                    self.navigatorWidget.hide()
                if self.parcelMpaInfoWidget:
                    self.parcelMpaInfoWidget.hide()
                if self.parcelInfoWidget:
                    self.parcelInfoWidget.hide()
                if self.camaWidget:
                    self.camaWidget.hide()
                if self.addressWidget:
                    self.addressWidget.hide()
        else:
            self.__create_plan_navigator()

    def __navigatorVisibilityChanged(self):

        if self.navigatorWidget.isVisible():
            self.navigator_action.setChecked(True)
        else:
            self.navigator_action.setChecked(False)

    def __pastureVisibilityChanged(self):

        if self.pastureWidget.isVisible():
            self.pasture_use_action.setChecked(True)
        else:
            self.pasture_use_action.setChecked(False)

    def __naturalReserveVisibilityChanged(self):

        if self.naturalReserveWidget.isVisible():
            self.nature_reserve_action.setChecked(True)
        else:
            self.nature_reserve_action.setChecked(False)

    def __spaParcelVisibilityChanged(self):

        if self.spaParcelWidget.isVisible():
            self.parcel_spa_action.setChecked(True)
        else:
            self.parcel_spa_action.setChecked(False)

    def __camaVisibilityChanged(self):

        if self.camaWidget.isVisible():
            self.cama_navigator_action.setChecked(True)
        else:
            self.cama_navigator_action.setChecked(False)

    def __addressVisibilityChanged(self):

        if self.address_action.isVisible():
            self.address_action.setChecked(True)
        else:
            self.address_action.setChecked(False)

    def __planVisibilityChanged(self):

        if self.planWidget.isVisible():
            self.land_plan_navigator_action.setChecked(True)
        else:
            self.land_plan_navigator_action.setChecked(False)

    def __mpaVisibilityChanged(self):

        if self.parcelMpaInfoWidget.isVisible():
            self.parcel_mpa_action.setChecked(True)
        else:
            self.parcel_mpa_action.setChecked(False)

    def __parcelVisibilityChanged(self):

        if self.parcelInfoWidget.isVisible():
            self.parcel_map_action.setChecked(True)
        else:
            self.parcel_map_action.setChecked(False)

    def __show_applications_dialog(self):

        if DialogInspector().dialog_visible():
            return

        DatabaseUtils.set_working_schema()
        application = PluginUtils.create_new_application()

        self.dlg = ApplicationsDialog(application, self.navigatorWidget, False, self.iface.mainWindow())
        DialogInspector().set_dialog_visible(True)
        self.dlg.rejected.connect(self.on_current_dialog_rejected)
        self.dlg.setModal(False)
        self.dlg.show()

    def __mark_apps_as_send_to_govenor(self):

        self.dlg = SentToGovernorDialog()
        self.dlg.show()

        # soum = DatabaseUtils.current_working_soum_schema()
        # DatabaseUtils.set_working_schema()
        #
        # msg_box = QMessageBox()
        # app_count = ""
        # try:
        #     session = SessionHandler().session_instance()
        #     app_count = session.query(CtApplicationStatus.application, func.max(CtApplicationStatus.status_date))\
        #         .group_by(CtApplicationStatus.application)\
        #         .having(func.max(CtApplicationStatus.status) == Constants.APP_STATUS_WAITING).distinct().count()
        #
        # except SQLAlchemyError, e:
        #     PluginUtils.show_error(self.iface.mainWindow(), QApplication.translate("Plugin", "Error executing"), e.message)
        #
        # msg_box.setText(QApplication.translate("Plugin", "Do you want to update {0} applications in working soum {1} to "
        #                                                  "the status \"send to the governor\"?").format(app_count, soum))
        # msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        #
        # result = msg_box.exec_()
        # if result == QMessageBox.Ok:
        #     DatabaseUtils.update_application_status()

    def __show_contract_dialog(self):

        if DialogInspector().dialog_visible():
            return

        DatabaseUtils.set_working_schema()
        contract = PluginUtils.create_new_contract()

        self.dlg = ContractDialog(contract, self.navigatorWidget, False, self.iface.mainWindow())
        DialogInspector().set_dialog_visible(True)
        self.dlg.rejected.connect(self.on_current_dialog_rejected)
        self.dlg.setModal(False)
        self.dlg.show()

    def __show_ownership_dialog(self):

        if DialogInspector().dialog_visible():
            return

        DatabaseUtils.set_working_schema()
        record = PluginUtils.create_new_record()

        self.dlg = OwnRecordDialog(record, self, False, self.iface.mainWindow())

        DialogInspector().set_dialog_visible(True)
        self.dlg.rejected.connect(self.on_current_dialog_rejected)
        self.dlg.setModal(False)
        self.dlg.show()

    def __show_documents_dialog(self):

        dialog = OfficialDocumentsDialog()
        dialog.exec_()

    def __show_import_decision_dialog(self):

        if DialogInspector().dialog_visible():
            return

        dlg = ImportDecisionDialog(False)
        DialogInspector().set_dialog_visible(True)
        dlg.rejected.connect(self.on_current_dialog_rejected)

        dlg.exec_()

    def __show_about_dialog(self):

        if DialogInspector().dialog_visible():
            return

        dlg = AboutDialog()
        DialogInspector().set_dialog_visible(True)
        dlg.rejected.connect(self.on_current_dialog_rejected)
        dlg.exec_()

    def __start_parcel_info_map(self):

        # self.removeLayers()
        # if DialogInspector().dialog_visible():
        #     return

        soum = DatabaseUtils.working_l2_code()
        layer = LayerUtils.layer_by_data_source("data_ub", 'ca_ub_parcel')

        if layer is None:
            QMessageBox.warning(self.iface.mainWindow(), QApplication.translate( "Plugin", "No <ub_parcel> layer"),
                                QApplication.translate( "Plugin", "Layer <ub_parcel> must be added "
                                                                  "to the table of contents first!"))
            self.parcel_map_action.setChecked(False)
            return

        map_units = self.iface.mapCanvas().mapUnits()
        if map_units != 0: # 0 = Meters
            self.parcel_map_action.setChecked(False)
            QMessageBox.warning(self.iface.mainWindow(),
                                QApplication.translate( "Plugin", "Layer / map units not set to 'Meters'"),
                                QApplication.translate( "Plugin", "Printing requires the layer units set to 'Meters'."
                                                          " \n(Settings->Project Properties->General->Layer units)"))
            return

        self.iface.mapCanvas().unsetMapTool(self.iface.mapCanvas().mapTool())

        mapTool = ParcelInfoExtractMapTool(self)

        self.iface.mapCanvas().setMapTool(mapTool)
        self.iface.mapCanvas().setCursor(QCursor(Qt.ArrowCursor))

        self.iface.mapCanvas().setFocus(Qt.OtherFocusReason)

    def __start_cama_info_map(self):

        layer = LayerUtils.layer_by_data_source("data_soums_union", 'ca_parcel')

        if layer is None:
            QMessageBox.warning(self.iface.mainWindow(), QApplication.translate( "Plugin", "No <parcel> layer"),
                                QApplication.translate( "Plugin", "Layer <parcel> must be added "
                                                                  "to the table of contents first!"))
            self.parcel_map_action.setChecked(False)
            return

        map_units = self.iface.mapCanvas().mapUnits()
        if map_units != 0: # 0 = Meters
            self.parcel_map_action.setChecked(False)
            QMessageBox.warning(self.iface.mainWindow(),
                                QApplication.translate( "Plugin", "Layer / map units not set to 'Meters'"),
                                QApplication.translate( "Plugin", "Printing requires the layer units set to 'Meters'."
                                                          " \n(Settings->Project Properties->General->Layer units)"))
            return

        self.iface.mapCanvas().unsetMapTool(self.iface.mapCanvas().mapTool())

        mapTool = CamaInfoExtractMapTool(self)

        self.iface.mapCanvas().setMapTool(mapTool)
        self.iface.mapCanvas().setCursor(QCursor(Qt.ArrowCursor))

        self.iface.mapCanvas().setFocus(Qt.OtherFocusReason)

    def __start_parcel_mpa_map(self):

        soum = DatabaseUtils.working_l2_code()
        layer = LayerUtils.layer_by_data_source("data_ub", 'ca_mpa_parcel_edit_view')

        if layer is None:
            QMessageBox.warning(self.iface.mainWindow(), QApplication.translate( "Plugin", "No <ub_parcel> layer"),
                                QApplication.translate( "Plugin", "Layer <ub_parcel> must be added "
                                                                  "to the table of contents first!"))
            self.parcel_mpa_action.setChecked(False)
            return

        map_units = self.iface.mapCanvas().mapUnits()
        if map_units != 0: # 0 = Meters
            self.parcel_mpa_action.setChecked(False)
            QMessageBox.warning(self.iface.mainWindow(),
                                QApplication.translate( "Plugin", "Layer / map units not set to 'Meters'"),
                                QApplication.translate( "Plugin", "Printing requires the layer units set to 'Meters'."
                                                          " \n(Settings->Project Properties->General->Layer units)"))
            return

        self.iface.mapCanvas().unsetMapTool(self.iface.mapCanvas().mapTool())

        mapTool = ParcelMpaEditMapTool(self)

        self.iface.mapCanvas().setMapTool(mapTool)
        self.iface.mapCanvas().setCursor(QCursor(Qt.ArrowCursor))

        self.iface.mapCanvas().setFocus(Qt.OtherFocusReason)

    def __start_print_cadastre_map(self):

        selectedLayers = self.iface.legendInterface().selectedLayers()

        if len(selectedLayers) == 0:
            QMessageBox.warning(self.iface.mainWindow(), QApplication.translate("Plugin", "Warning"),
                                QApplication.translate("Plugin", "No layer has been selected. " "Please select only one printing parcel layer!"))
            return

        if len(selectedLayers) > 1:
            QMessageBox.warning(self.iface.mainWindow(), QApplication.translate("Plugin", "Warning"),
                                QApplication.translate("Plugin", "You might have chosen more than one layer. ""Please select only one printing parcel layer!"))
            return

        layer_name = None
        for layer in selectedLayers:
            layer_name = layer.name()

        if self.print_cadastre_map_action.isCheckable():
            self.print_cadastre_map_action.setCheckable(False)
        else:
            self.print_cadastre_map_action.setCheckable(True)
            self.activeAction = None

        self.removeLayers()
        if DialogInspector().dialog_visible():
            return

        if self.activeAction == self.print_cadastre_map_action:
            self.print_cadastre_map_action.setChecked(True)
            return

        layer = None
        if layer_name == u'Нэгж талбар' or layer_name == 'Parcel':
            layer = LayerUtils.layer_by_data_source("data_soums_union", 'ca_parcel')
        elif layer_name == u'БН-н Нэгж талбар' or layer_name == 'Reserve Parcel':
            layer = LayerUtils.layer_by_data_source("data_soums_union", 'ca_person_group_parcel')
        elif layer_name == u'БАХ нэгж талбар' or layer_name == 'PUGParcel':
            layer = LayerUtils.layer_by_data_source("data_soums_union", 'ca_pasture_parcel')
        else:
            layer = LayerUtils.layer_by_data_source("data_soums_union", 'ca_parcel')

        if layer is None:
            QMessageBox.warning(self.iface.mainWindow(), QApplication.translate( "Plugin", "No <parcel> layer"),
                                QApplication.translate( "Plugin", "Layer <parcel> must be added "
                                                                  "to the table of contents first!"))
            self.print_cadastre_map_action.setChecked(False)
            return

        map_units = self.iface.mapCanvas().mapUnits()
        if map_units != 0: # 0 = Meters
            self.print_cadastre_map_action.setChecked(False)
            QMessageBox.warning(self.iface.mainWindow(),
                                QApplication.translate( "Plugin", "Layer / map units not set to 'Meters'"),
                                QApplication.translate( "Plugin", "Printing requires the layer units set to 'Meters'."
                                                          " \n(Settings->Project Properties->General->Layer units)"))
            return

        self.iface.mapCanvas().unsetMapTool(self.iface.mapCanvas().mapTool())

        mapTool = None
        if layer_name == u'Нэгж талбар' or layer_name == 'Parcel':
            table_name = 'ca_parcel'
            mapTool = PrintCadastreExtractMapTool(self, table_name, False)
        elif layer_name == u'БН-н Нэгж талбар' or layer_name == 'Reserve Parcel':
            table_name = 'ca_person_group_parcel'
            mapTool = PrintCadastreExtractMapTool(self, table_name, True)
        elif layer_name == u'БАХ нэгж талбар' or layer_name == 'PUGParcel':
            table_name = 'ca_pasture_parcel'
            mapTool = PrintCadastreExtractMapTool(self, table_name, True)
        elif layer_name == u'ТХ нэгж талбар' or layer_name == 'SPA Parcel':
            table_name = 'ca_spa_parcel'
            mapTool = PrintCadastreExtractMapTool(self, table_name, True)
        elif layer_name == u'ТХ нэгж талбар' or layer_name == 'State Parcel':
            table_name = 'ca_state_parcel'
            mapTool = PrintCadastreExtractMapTool(self, table_name, True)
        else:
            mapTool = PrintCadastreExtractMapTool(self)

        self.iface.mapCanvas().setMapTool(mapTool)
        self.iface.mapCanvas().setCursor(QCursor(Qt.ArrowCursor))

        self.activeAction = self.print_cadastre_map_action
        self.iface.mapCanvas().setFocus(Qt.OtherFocusReason)

    def __start_print_point_map(self):

        if self.print_point_map_action.isCheckable():
            self.print_point_map_action.setCheckable(False)
        else:
            self.print_point_map_action.setCheckable(True)
            self.activeAction = None

        self.removeLayers()
        if DialogInspector().dialog_visible():
            return

        if self.activeAction == self.print_point_map_action:
            self.print_point_map_action.setChecked(True)
            return

        soum = DatabaseUtils.working_l2_code()
        layer = LayerUtils.layer_by_data_source("pasture", 'ca_pasture_monitoring')

        if layer is None:
            QMessageBox.warning(self.iface.mainWindow(), QApplication.translate( "Plugin", "No <monitoring> layer"),
                                QApplication.translate( "Plugin", "Layer <monitoring> must be added "
                                                                  "to the table of contents first!"))
            self.print_point_map_action.setChecked(False)
            return

        map_units = self.iface.mapCanvas().mapUnits()
        if map_units != 0: # 0 = Meters
            self.print_point_map_action.setChecked(False)
            QMessageBox.warning(self.iface.mainWindow(),
                                QApplication.translate( "Plugin", "Layer / map units not set to 'Meters'"),
                                QApplication.translate( "Plugin", "Printing requires the layer units set to 'Meters'."
                                                          " \n(Settings->Project Properties->General->Layer units)"))
            return

        self.iface.mapCanvas().unsetMapTool(self.iface.mapCanvas().mapTool())

        mapTool = PrintPointExtractMapTool(self)

        self.iface.mapCanvas().setMapTool(mapTool)
        self.iface.mapCanvas().setCursor(QCursor(Qt.ArrowCursor))

        self.activeAction = self.print_point_map_action
        self.iface.mapCanvas().setFocus(Qt.OtherFocusReason)

    def __show_help(self):

        #session = SessionHandler().session_instance()
        #test = session.query(SetRightTypeApplicationType).count()
        #LM2Logger().log_message("testing further with the help button")
        #LM2Logger().log_message("second test with the help button")
        # PluginUtils.show_message(self.iface.mainWindow(), "help", "help ")
        os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))) +"\help\output\help_lm2.chm::/html/Introduction.htm")


    @pyqtSlot()
    def __update_database_connection(self, p_password, is_expired=True):

        if not SessionHandler().session_instance():

            database_name = QSettings().value(SettingsConstants.DATABASE_NAME)
            port = QSettings().value(SettingsConstants.PORT, "5432")
            user_name = QSettings().value(SettingsConstants.USER)
            server = QSettings().value(SettingsConstants.HOST)

            for key in QgsMapLayerRegistry.instance().mapLayers():
                layer = QgsMapLayerRegistry.instance().mapLayers()[key]
                if layer.type() == QgsMapLayer.VectorLayer and layer.dataProvider().name() == "postgres":
                    uri = QgsDataSourceURI(layer.source())
                    if uri.database() == database_name and user_name == uri.username() \
                            and server == uri.host() and port == uri.port() and p_password == uri.password()\
                            and not is_expired:
                        self.__create_db_session(uri.password())
                        self.__set_menu_visibility()
                        self.__refresh_layer()
                        break
                    else:
                        self.__disable_menu()

    def __set_menu_visibility(self):

        user_name = QSettings().value(SettingsConstants.USER)

        if not user_name:
            self.__disable_menu()
            return

        if not SessionHandler().session_instance():
            self.__disable_menu()
            return

        user_right = DatabaseUtils.userright_by_name(user_name)
        if user_right:
            self.__enable_menu(user_right)

    def __refresh_layer(self):

        root = QgsProject.instance().layerTreeRoot()
        LayerUtils.refresh_layer()

        ###
        saf_group = root.findGroup(u"Мэдээний хяналт")
        layers = self.iface.legendInterface().layers()

        vlayer = LayerUtils.layer_by_data_source("data_landuse", "set_landuse_safety_zone")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("set_landuse_safety_zone", "id", "data_landuse")
        vlayer.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))) + "/template\style/set_landuse_safety_zone.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "Safety Zone"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            saf_group.addLayer(vlayer)
            vlayer.setReadOnly(True)
        root.findLayer(vlayer.id()).setVisible(0)
        ###

        mygroup = root.findGroup(u"Кадастр")
        layers = self.iface.legendInterface().layers()

        vlayer = LayerUtils.layer_by_data_source("data_soums_union", "ca_parcel")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("ca_parcel", "parcel_id", "data_soums_union")
        vlayer.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))) + "/template\style/ca_parcel.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "Parcel"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            mygroup.addLayer(vlayer)
            vlayer.setReadOnly(True)

        vlayer = LayerUtils.layer_by_data_source("data_soums_union", "ca_building")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("ca_building", "building_id", "data_soums_union")
        vlayer.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))) + "/template\style/ca_building.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "Building"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            mygroup.addLayer(vlayer)
            vlayer.setReadOnly(True)

        ####
        vlayer = LayerUtils.layer_by_data_source("data_soums_union", "ca_sub_parcel")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("ca_sub_parcel", "sub_parcel_id", "data_soums_union")
        vlayer.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))) + "/template\style/ca_sub_parcel_tbl.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "Sub Parcel"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            mygroup.addLayer(vlayer)

        ####
        vlayer = LayerUtils.layer_by_data_source("data_soums_union", "ca_parcel_line")
        if vlayer is None:
            vlayer = LayerUtils.load_line_layer_base_layer("ca_parcel_line", "parcel_id", "data_soums_union")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))) + "/template\style/ca_parcel_line.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "Parcel Line"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            mygroup.addLayer(vlayer)

        ####
        vlayer = LayerUtils.layer_by_data_source("data_soums_union", "ca_temporary_parcel")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("ca_temporary_parcel", "parcel_id", "data_soums_union")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))) + "/template\style/ca_temporary_parcel.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "Temporary Parcel"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            mygroup.addLayer(vlayer)

        ######
        addrs_group = root.findGroup(u"Хаяг")

        vlayer = LayerUtils.layer_by_data_source("data_address", "st_street_start_point_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("st_street_start_point_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))) + "/template\style/st_street_start_point_view.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "Street Start Point"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_group.addLayer(vlayer)
        # root.findLayer(vlayer.id()).setVisible(0)
            # vlayer.setReadOnly(True)

        vlayer = LayerUtils.layer_by_data_source("data_address", "st_entrance_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("st_entrance_view", "entrance_id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))) + "/template\style/st_entrance.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "Address Entrance"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_group.addLayer(vlayer)
        # root.findLayer(vlayer.id()).setVisible(0)
            # vlayer.setReadOnly(True)

        addrs_parcel_group = root.findGroup(u"Хаягийн барилга")
        vlayer = LayerUtils.layer_by_data_source("data_address", "ca_building_address_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("ca_building_address_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))) + "/template\style/ca_building_address.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "Address Building"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_parcel_group.addLayer(vlayer)
        # root.findLayer(vlayer.id()).setVisible(0)
            # vlayer.setReadOnly(True)

        addrs_parcel_group = root.findGroup(u"Хаягийн нэгж талбар")
        vlayer = LayerUtils.layer_by_data_source("data_address", "ca_parcel_address_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("ca_parcel_address_view", "id", "data_address")
        vlayer.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))) + "/template\style/ca_parcel_address.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", " Address Parcel"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_parcel_group.addLayer(vlayer)
        # root.findLayer(vlayer.id()).setVisible(0)
            # vlayer.setReadOnly(True)



        vlayer = LayerUtils.layer_by_data_source("data_address", "st_road_line_view")
        if vlayer is None:
            vlayer = LayerUtils.load_line_layer_base_layer("st_road_line_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))) + "/template\style/st_road_line.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "Road Line"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_group.addLayer(vlayer)
        # root.findLayer(vlayer.id()).setVisible(0)

        vlayer = LayerUtils.layer_by_data_source("data_address", "st_street_line_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("st_street_line_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))) + "/template\style/st_street_line.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "Street Line"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_group.addLayer(vlayer)
        # root.findLayer(vlayer.id()).setVisible(0)

        vlayer = LayerUtils.layer_by_data_source("data_address", "st_street_sub_polygon_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("st_street_sub_polygon_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))) + "/template\style/st_street_sub.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "Address Sub Street"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_group.addLayer(vlayer)
        root.findLayer(vlayer.id()).setVisible(0)

        ######
        vlayer = LayerUtils.layer_by_data_source("data_address", "st_street_polygon_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("st_street_polygon_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))) + "/template\style/st_street.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "Address Street"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_group.addLayer(vlayer)
        root.findLayer(vlayer.id()).setVisible(0)

        self.iface.mapCanvas().refresh()

        vlayer = LayerUtils.layer_by_data_source("data_address", "au_zipcode_area")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("au_zipcode_area", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))) + "/template\style/au_zipcode_area.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "Address Post Zone"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            addrs_group.addLayer(vlayer)
        root.findLayer(vlayer.id()).setVisible(0)

        au_group = root.findGroup(U"Хилийн цэс, бүсчлэл")
        vlayer = LayerUtils.layer_by_data_source("data_address", "au2_settlement_zone_view")
        if vlayer is None:
            vlayer = LayerUtils.load_layer_base_layer("au2_settlement_zone_view", "id", "data_address")
        vlayer.loadNamedStyle(
            str(os.path.dirname(os.path.realpath(__file__))) + "/template\style/au2_settlement_zone_view.qml")
        vlayer.setLayerName(QApplication.translate("Plugin", "Settlement Zone"))
        myalayer = root.findLayer(vlayer.id())
        if myalayer is None:
            au_group.addLayer(vlayer)
        root.findLayer(vlayer.id()).setVisible(0)

        self.iface.mapCanvas().refresh()

    def __create_navigator(self):

        self.removeLayers()
        # create widget
        if self.navigatorWidget:
            self.iface.removeDockWidget(self.navigatorWidget)
            del self.navigatorWidget

        self.navigatorWidget = NavigatorWidget(self)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.navigatorWidget)
        QObject.connect(self.navigatorWidget, SIGNAL("visibilityChanged(bool)"), self.__navigatorVisibilityChanged)
        self.navigatorWidget.show()

    def __create_pasture(self):

        self.removeLayers()
        # create widget
        if self.pastureWidget:
            self.iface.removeDockWidget(self.pastureWidget)
            del self.pastureWidget

        self.pastureWidget = PastureWidget(self,zone_rigth_type = 1)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.pastureWidget)

        QObject.connect(self.pastureWidget, SIGNAL("visibilityChanged(bool)"), self.__pastureVisibilityChanged)
        self.pastureWidget.show()
        if self.navigatorWidget:
            self.navigatorWidget.hide()
        if self.parcelInfoWidget:
            self.parcelInfoWidget.hide()
        if self.parcelMpaInfoWidget:
            self.parcelMpaInfoWidget.hide()
        if self.planWidget:
            self.planWidget.hide()
        if self.spaParcelWidget:
            self.spaParcelWidget.hide()
        if self.naturalReserveWidget:
            self.naturalReserveWidget.hide()

    def __create_nature_reserve(self):

        self.removeLayers()
        # create widget
        if self.naturalReserveWidget:
            self.iface.removeDockWidget(self.naturalReserveWidget)
            del self.naturalReserveWidget

        self.naturalReserveWidget = PastureWidget(self, zone_rigth_type = 2)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.naturalReserveWidget)

        QObject.connect(self.naturalReserveWidget, SIGNAL("visibilityChanged(bool)"), self.__naturalReserveVisibilityChanged)
        self.naturalReserveWidget.show()
        if self.navigatorWidget:
            self.navigatorWidget.hide()
        if self.parcelInfoWidget:
            self.parcelInfoWidget.hide()
        if self.parcelMpaInfoWidget:
            self.parcelMpaInfoWidget.hide()
        if self.planWidget:
            self.planWidget.hide()
        if self.spaParcelWidget:
            self.spaParcelWidget.hide()
        if self.pastureWidget:
            self.pastureWidget.hide()

    def __create_spa_parcel(self):

        self.removeLayers()
        # create widget
        if self.spaParcelWidget:
            self.iface.removeDockWidget(self.spaParcelWidget)
            del self.spaParcelWidget

        self.spaParcelWidget = SpaParcelWidget(self)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.spaParcelWidget)

        QObject.connect(self.spaParcelWidget, SIGNAL("visibilityChanged(bool)"), self.__spaParcelVisibilityChanged)
        self.spaParcelWidget.show()
        if self.navigatorWidget:
            self.navigatorWidget.hide()
        if self.parcelInfoWidget:
            self.parcelInfoWidget.hide()
        if self.parcelMpaInfoWidget:
            self.parcelMpaInfoWidget.hide()
        if self.planWidget:
            self.planWidget.hide()
        if self.pastureWidget:
            self.pastureWidget.hide()

    def __create_mpa(self):

        self.removeLayers()
        # create widget
        if self.parcelMpaInfoWidget:
            self.iface.removeDockWidget(self.parcelMpaInfoWidget)
            del self.parcelMpaInfoWidget

        self.parcelMpaInfoWidget = ParcelMpaDialog(self)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.parcelMpaInfoWidget)
        QObject.connect(self.parcelMpaInfoWidget, SIGNAL("visibilityChanged(bool)"), self.__mpaVisibilityChanged)
        self.parcelMpaInfoWidget.show()
        if self.navigatorWidget:
            self.navigatorWidget.hide()
        if self.parcelInfoWidget:
            self.parcelInfoWidget.hide()
        if self.pastureWidget:
            self.pastureWidget.hide()
        if self.spaParcelWidget:
            self.spaParcelWidget.hide()
        if self.planWidget:
            self.planWidget.hide()

    def __create_parcel_info(self):

        self.removeLayers()
        # create widget
        if self.parcelInfoWidget:
            self.iface.removeDockWidget(self.parcelInfoWidget)
            del self.parcelInfoWidget

        self.parcelInfoWidget = ParcelInfoDialog(self)
        # self.parcelInfoWidget.set_parcel_data(self.parcel_no, self.result_feature)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.parcelInfoWidget)
        QObject.connect(self.parcelInfoWidget, SIGNAL("visibilityChanged(bool)"), self.__parcelVisibilityChanged)
        self.parcelInfoWidget.show()
        if self.navigatorWidget:
            self.navigatorWidget.hide()
        if self.parcelMpaInfoWidget:
            self.parcelMpaInfoWidget.hide()
        if self.pastureWidget:
            self.pastureWidget.hide()
        if self.spaParcelWidget:
            self.spaParcelWidget.hide()
        if self.planWidget:
            self.planWidget.hide()

    def __create_address_navigator(self):

        self.removeLayers()
        # create widget
        if self.addressWidget:
            self.iface.removeDockWidget(self.addressWidget)
            del self.addressWidget

        self.addressWidget = AddressNavigatorWidget(self)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.addressWidget)

        QObject.connect(self.addressWidget, SIGNAL("visibilityChanged(bool)"), self.__addressVisibilityChanged)
        self.addressWidget.show()
        if self.navigatorWidget:
            self.navigatorWidget.hide()
        if self.parcelInfoWidget:
            self.parcelInfoWidget.hide()
        if self.parcelMpaInfoWidget:
            self.parcelMpaInfoWidget.hide()
        if self.pastureWidget:
            self.pastureWidget.hide()
        if self.spaParcelWidget:
            self.spaParcelWidget.hide()
        if self.planWidget:
            self.planWidget.hide()
        if self.camaWidget:
            self.camaWidget.hide()

    def __create_cama_navigator(self):

        self.removeLayers()
        # create widget
        if self.camaWidget:
            self.iface.removeDockWidget(self.camaWidget)
            del self.camaWidget

        self.camaWidget = CamaNavigatorWidget(self)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.camaWidget)

        QObject.connect(self.camaWidget, SIGNAL("visibilityChanged(bool)"), self.__camaVisibilityChanged)
        self.camaWidget.show()
        if self.navigatorWidget:
            self.navigatorWidget.hide()
        if self.parcelInfoWidget:
            self.parcelInfoWidget.hide()
        if self.parcelMpaInfoWidget:
            self.parcelMpaInfoWidget.hide()
        if self.pastureWidget:
            self.pastureWidget.hide()
        if self.spaParcelWidget:
            self.spaParcelWidget.hide()
        if self.planWidget:
            self.planWidget.hide()

    def __create_plan_navigator(self):

        self.removeLayers()
        # create widget
        if self.planWidget:
            self.iface.removeDockWidget(self.planWidget)
            del self.planWidget

        self.planWidget = PlanNavigatorWidget(self)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.planWidget)

        QObject.connect(self.planWidget, SIGNAL("visibilityChanged(bool)"), self.__planVisibilityChanged)
        self.planWidget.show()
        if self.navigatorWidget:
            self.navigatorWidget.hide()
        if self.parcelInfoWidget:
            self.parcelInfoWidget.hide()
        if self.parcelMpaInfoWidget:
            self.parcelMpaInfoWidget.hide()
        if self.pastureWidget:
            self.pastureWidget.hide()
        if self.spaParcelWidget:
            self.spaParcelWidget.hide()

    def __enable_menu(self, user_rights):

        self.navigator_action.setEnabled(True)
        self.pasture_use_action.setEnabled(True)
        self.nature_reserve_action.setEnabled(True)
        self.parcel_spa_action.setEnabled(True)
        self.parcel_map_action.setEnabled(True)
        self.land_plan_navigator_action.setEnabled(True)
        self.cama_navigator_action.setEnabled(True)
        self.address_action.setEnabled(True)
        self.about_action.setEnabled(True)

        self.__create_navigator()

        # self.__create_pasture()

        # self.__create_mpa()

        # self.__create_parcel_info()
        if UserRight.land_office_admin in user_rights:
            self.land_plan_settings_action.setEnabled(True)
            self.admin_settings_action.setEnabled(True)

        if UserRight.cadastre_view in user_rights or UserRight.cadastre_update in user_rights:
            self.create_case_action.setEnabled(True)
            self.mark_apps_action.setEnabled(True)
        else:
            self.create_case_action.setEnabled(False)
            self.mark_apps_action.setEnabled(False)

        if UserRight.contracting_view in user_rights or UserRight.contracting_update in user_rights:
            self.contract_action.setEnabled(True)
            self.ownership_action.setEnabled(True)
            self.import_decision_action.setEnabled(True)
            self.applications_action.setEnabled(True)
            self.mark_apps_action.setEnabled(True)
            self.person_action.setEnabled(True)
            self.print_cadastre_map_action.setEnabled(True)
            self.document_action.setEnabled(True)
            # self.manage_parcel_records_action.setEnabled(True)
            self.database_dump_action.setEnabled(False)
            self.webgis_utility_action.setEnabled(True)
        else:
            self.contract_action.setEnabled(False)
            self.ownership_action.setEnabled(False)
            self.import_decision_action.setEnabled(False)
            self.applications_action.setEnabled(False)
            self.person_action.setEnabled(False)
            self.mark_apps_action.setEnabled(False)
            self.document_action.setEnabled(False)
            # self.manage_parcel_records_action.setEnabled(False)
            self.database_dump_action.setEnabled(True)
            self.webgis_utility_action.setEnabled(False)

    def __disable_menu(self):

        self.create_case_action.setEnabled(False)
        self.about_action.setEnabled(False)
        self.import_decision_action.setEnabled(False)
        self.applications_action.setEnabled(False)
        self.person_action.setEnabled(False)
        self.contract_action.setEnabled(False)
        self.ownership_action.setEnabled(False)
        self.navigator_action.setEnabled(False)
        self.mark_apps_action.setEnabled(False)
        self.parcel_map_action.setEnabled(False)
        self.document_action.setEnabled(False)
        # self.manage_parcel_records_action.setEnabled(False)
        self.cama_navigator_action.setEnabled(False)
        self.address_action.setEnabled(False)
        self.database_dump_action.setEnabled(True)
        self.webgis_utility_action.setEnabled(False)
        self.pasture_use_action.setEnabled(False)
        self.nature_reserve_action.setEnabled(False)
        self.parcel_spa_action.setEnabled(False)
        self.land_plan_navigator_action.setEnabled(False)
        self.land_plan_settings_action.setEnabled(False)
        self.admin_settings_action.setEnabled(False)

    def transformPoint(self, point, layer_postgis_srid):

        # If On-the-Fly transformation is enabled in the QGIS project settings
        # transform from map coordinates (destinationSrs()) to layer coordinates
        renderer = self.iface.mapCanvas().mapRenderer()
        if renderer.hasCrsTransformEnabled() and renderer.destinationCrs().postgisSrid() != layer_postgis_srid:
            transformation = QgsCoordinateTransform(renderer.destinationCrs(), QgsCoordinateReferenceSystem(layer_postgis_srid))
            point = transformation.transform(point)

        return point

    def on_current_dialog_rejected(self):

        DialogInspector().set_dialog_visible(False)

    def getLayerById(self, layerId):

        layermap = QgsMapLayerRegistry.instance().mapLayers()
        for id, layer in layermap.iteritems():
            if layer.name() == layerId:
                return layer
        return None

    def removeLayers(self):

        project = QgsProject.instance()
        isDirty = project.isDirty()

        layer = self.getLayerById("boundary_points")
        if layer != None:
            QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

        layer = self.getLayerById("boundary_lines")
        if layer != None:
            QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

        layer = self.getLayerById("boundary_polygon")
        if layer != None:
            QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

        layer = self.getLayerById("boundary_outline")
        if layer != None:
            QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

        layer = self.getLayerById("building_points")
        if layer != None:
            QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

        layer = self.getLayerById("building_polygon")
        if layer != None:
            QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

        layer = self.getLayerById("building_lines")
        if layer != None:
            QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

        if not isDirty:
            project.dirty(False)

    def __layers_permission(self):

        user_name = None
        password = None
        port = None
        server = None
        database_name = None
        user_name_real = None

        for key in QgsMapLayerRegistry.instance().mapLayers():
            layer = QgsMapLayerRegistry.instance().mapLayers()[key]
            if layer.type() == QgsMapLayer.VectorLayer and layer.dataProvider().name() == "postgres":
                uri = QgsDataSourceURI(layer.source())
                user_name = uri.username()
                password = uri.password()
                port = uri.port()
                server = uri.host()
                database_name = uri.database()

        layers = self.iface.legendInterface().layers()
        ###################

        if not port:
            return

        self.engine = create_engine("postgresql://{0}:{1}@{2}:{3}/{4}".format(user_name, password, server, port, database_name))

        Session = sessionmaker(bind=self.engine)
        session = Session()
        session.autocommit = False
        session.execute(set_search_path)

        role_count = session.query(SetRole).\
            filter(SetRole.user_name == user_name).\
            filter(SetRole.is_active == True).count()
        if user_name.find("user") == -1:
            return
        if role_count  == 1:
            role = session.query(SetRole). \
                filter(SetRole.user_name == user_name). \
                filter(SetRole.is_active == True).one()
            user_name_real = role.user_name_real
            l2_code_list = role.restriction_au_level2.split(',')

            user_right_parcel_count = session.query(SetUserGroupRole). \
                filter(SetUserGroupRole.user_name_real == user_name_real). \
                filter(SetUserGroupRole.group_role == 6).count()

            user_right_temp_parcel_count = session.query(SetUserGroupRole). \
                filter(SetUserGroupRole.user_name_real == user_name_real). \
                filter(SetUserGroupRole.group_role == 7).count()

            for layer in layers:
                for soum in l2_code_list:
                    if user_right_parcel_count == 1:
                        user_right_parcel = session.query(SetUserGroupRole). \
                            filter(SetUserGroupRole.user_name_real == user_name_real). \
                            filter(SetUserGroupRole.group_role == 6).one()
                        if layer.name() == "Parcel" + "_" + soum or layer.name() == u"Нэгж талбар" +"_"+soum:
                            if user_right_parcel.r_update:
                                layer.setReadOnly(False)
                            else:
                                layer.setReadOnly(True)
                        if layer.name() == "Building" + "_" + soum or layer.name() == u"Барилга" +"_"+soum:
                            if user_right_parcel.r_update:
                                layer.setReadOnly(False)
                            else:
                                layer.setReadOnly(True)
                    if user_right_temp_parcel_count == 1:
                        user_right_temp_parcel = session.query(SetUserGroupRole). \
                            filter(SetUserGroupRole.user_name_real == user_name_real). \
                            filter(SetUserGroupRole.group_role == 7).one()
                        if layer.name() == "Tmp_Parcel" + "_" + soum or layer.name() == u"Ажлын Нэгж талбар" +"_"+soum:
                            if user_right_temp_parcel.r_update:
                                layer.setReadOnly(False)
                            else:
                                layer.setReadOnly(True)
                        if layer.name() == "Tmp_Building" + "_" + soum or layer.name() == u"Ажлын Барилга" +"_"+soum:
                            if user_right_temp_parcel.r_update:
                                layer.setReadOnly(False)
                            else:
                                layer.setReadOnly(True)