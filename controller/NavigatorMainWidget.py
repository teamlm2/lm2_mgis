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
from ..controller.NavigatorWidget import *
from ..controller.PastureWidget import *
from ..controller.ParcelInfoDialog import *
from ..controller.ParcelMpaDialog import *
from ..view.Ui_NavigatorMainWidget import Ui_NavigatorMainWidget
from ..utils.LayerUtils import LayerUtils
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

class NavigatorMainWidget(QDockWidget, Ui_NavigatorMainWidget, DatabaseHelper):

    def __init__(self,  plugin, parent=None):

        super(NavigatorMainWidget,  self).__init__(parent)
        DatabaseHelper.__init__(self)

        self.setupUi(self)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.plugin = plugin
        self.selectedWidget = None
        self.session = SessionHandler().session_instance()

    @pyqtSlot()
    def on_cadastre_button_clicked(self):

        # if self.selectedWidget:
        #     self.plugin.iface.removeDockWidget(self.selectedWidget)
        #     del self.selectedWidget

        self.selectedWidget = NavigatorWidget(self)
        self.plugin.iface.addDockWidget(Qt.RightDockWidgetArea, self.selectedWidget)
        # QObject.connect(self.navigatorWidget, SIGNAL("visibilityChanged(bool)"), self.__navigatorVisibilityChanged)
        self.selectedWidget.show()

        self.hide()

    @pyqtSlot()
    def on_pasture_button_clicked(self):

        # if self.selectedWidget:
        #     self.plugin.iface.removeDockWidget(self.selectedWidget)
        #     del self.selectedWidget

        self.selectedWidget = PastureWidget(self)
        self.plugin.iface.addDockWidget(Qt.RightDockWidgetArea, self.selectedWidget)
        # QObject.connect(self.navigatorWidget, SIGNAL("visibilityChanged(bool)"), self.__navigatorVisibilityChanged)
        self.selectedWidget.show()

        self.get_test(self.selectedWidget)
        self.hide()

    @pyqtSlot()
    def on_ub_button_clicked(self):

        # if self.selectedWidget:
        #     self.plugin.iface.removeDockWidget(self.selectedWidget)
        #     del self.selectedWidget

        self.selectedWidget = ParcelInfoDialog(self)
        self.plugin.iface.addDockWidget(Qt.RightDockWidgetArea, self.selectedWidget)
        # QObject.connect(self.navigatorWidget, SIGNAL("visibilityChanged(bool)"), self.__navigatorVisibilityChanged)
        self.selectedWidget.show()

        self.hide()

    @pyqtSlot()
    def on_mpa_button_clicked(self):

        if self.selectedWidget:
            self.plugin.iface.removeDockWidget(self.selectedWidget)
            del self.selectedWidget

        self.selectedWidget = ParcelMpaDialog(self)
        self.plugin.iface.addDockWidget(Qt.RightDockWidgetArea, self.selectedWidget)
        # QObject.connect(self.navigatorWidget, SIGNAL("visibilityChanged(bool)"), self.__navigatorVisibilityChanged)
        self.selectedWidget.show()

        self.hide()

    def get_test(self, aa):
        return aa