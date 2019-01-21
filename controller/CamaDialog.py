# coding=utf8
__author__ = 'B.Ankhbold'

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from geoalchemy2.elements import WKTElement
from qgis.core import *
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, or_, and_, desc
from decimal import Decimal
from ..view.Ui_CamaDialog import *
from ..controller.ParcelInfoFeeDialog import *
from ..utils.PluginUtils import PluginUtils
from ..utils.LayerUtils import LayerUtils
from ..utils.DatabaseUtils import DatabaseUtils
from ..utils.SessionHandler import SessionHandler
from ..utils.FileUtils import FileUtils
from ..model.CaBuilding import *
from ..model.BsPerson import *
from ..model.CtApplication import *
from ..model.ClApplicationStatus import *
from ..model.ClPersonType import *
from ..model.ClDecisionLevel import *
from ..model.ClContractStatus import *
from ..model.ClPersonRole import *
from ..model.MpaGisEditSubject import *
from ..model.ClDocumentRole import *
from ..model.CtDecision import *
from ..model.CaParcelTbl import *
from ..model.CtContractApplicationRole import *
from ..model.AuLevel1 import *
from ..model.AuLevel2 import *
from ..model.AuLevel3 import *
from ..model import SettingsConstants
from ..model import Constants
from ..model.SetRightTypeApplicationType import *
from ..model.LM2Exception import LM2Exception
from ..model.ClPositionType import *
from ..model.ClUbEditStatus import *
from ..model.Enumerations import PersonType, UserRight
from ..model.DatabaseHelper import *
from ..utils.SessionHandler import SessionHandler
from ..utils.FilePath import *
from .qt_classes.UbDocumentViewDelegate import UbDocumentViewDelegate
import math
import locale
import os
import pyproj
import urllib2
import shutil
import sys
import datetime
from ftplib import FTP, error_perm
from contextlib import closing

class CamaDialog(QDockWidget, Ui_CamaDialog, DatabaseHelper):

    def __init__(self, plugin, parent=None):

        super(CamaDialog, self).__init__(parent)
        DatabaseHelper.__init__(self)

        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.plugin = plugin
        self.session = SessionHandler().session_instance()
        self.setupUi(self)
