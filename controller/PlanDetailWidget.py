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

    def __init__(self, plan, navigator, attribute_update=False, parent=None):

        super(PlanDetailWidget,  self).__init__(parent)
        DatabaseHelper.__init__(self)

        self.setupUi(self)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        # self.plugin = plugin
        self.navigator = navigator
        self.attribute_update = attribute_update
        self.plan = plan
        self.session = SessionHandler().session_instance()

        self.userSettings = None
        self.planNavigatorWidget = None

        self.__setup_data()
        self.__setup_tree_widget()

    def __setup_tree_widget(self):

        self.item_point_main = QTreeWidgetItem()
        self.item_point_main.setText(0, self.tr("Point"))
        self.item_point_main.setData(0, Qt.UserRole, Constants.GEOM_POINT)

        self.item_line_main = QTreeWidgetItem()
        self.item_line_main.setText(0, self.tr("Line"))
        self.item_line_main.setData(0, Qt.UserRole, Constants.GEOM_LINE)

        self.item_polygon_main = QTreeWidgetItem()
        self.item_polygon_main.setText(0, self.tr("Polygon"))
        self.item_polygon_main.setData(0, Qt.UserRole, GEOM_POlYGON)

        self.main_tree_widget.addTopLevelItem(self.item_point_main)
        self.main_tree_widget.addTopLevelItem(self.item_line_main)
        self.main_tree_widget.addTopLevelItem(self.item_polygon_main)

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

    @pyqtSlot()
    def on_main_zone_load_button_clicked(self):

        au2 = DatabaseUtils.working_l2_code()
        main_zone_points = self.session.query(LdProjectMainZone).\
            filter(LdProjectMainZone.plan_draft_id == self.plan.plan_draft_id).\
            filter(LdProjectMainZone.polygon_geom == None).\
            filter(LdProjectMainZone.line_geom == None).\
            filter(LdProjectMainZone.au2 == au2).all()

        for main_zone_point in main_zone_points:
            item = QTreeWidgetItem()
            item.setText(0, str(main_zone_point.parcel_id)+'('+main_zone_point.gazner+')')
            self.item_point_main.addChild(item)