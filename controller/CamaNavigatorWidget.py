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
        self.au2 = DatabaseUtils.working_l2_code()
