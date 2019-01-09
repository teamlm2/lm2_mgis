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