# coding=utf8

__author__ = 'B.Ankhbold'

from types import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from qgis.core import *
from qgis.gui import *
from sqlalchemy import func, or_, and_, desc,extract
from geoalchemy2.elements import WKTElement
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
from sqlalchemy.sql import exists
from datetime import date, datetime, timedelta
from inspect import currentframe
import os
import types
import textwrap
import win32api
import win32net
import win32netcon,win32wnet
from ..utils.FileUtils import FileUtils
from ..model.LM2Exception import LM2Exception
from ..model.SetValidation import *
from ..model.DatabaseHelper import *
from ..model import SettingsConstants
from ..model import Constants
from ..model.AuLevel1 import *
from ..model.AuLevel2 import *
from ..model.SdUser import *
from ..model.Enumerations import ApplicationType, UserRight
from ..model.SdFtpConnection import *
from ..model.SdFtpPermission import *
from ..model.LdProjectParcel import *
from ..model.LdProjectMainZone import *
from ..model.LdProjectSubZone import *
from ..model.LdProcessPlan import *
from ..model.Constants import *
from ..model.SetFilterPlanLayer import *
from ..model.LdAttribute import *
from ..model.LdAttributeGroup import *
from ..model.LdAttributeProcess import *
from ..model.LdAttributeMainZoneValue import *
from ..model.LdAttributeParcelValue import *
from ..model.LdAttributeSubZoneValue import *
from ..view.Ui_PlanAttributeEditDialog import Ui_PlanAttributeEditDialog
from .qt_classes.ApplicantDocumentDelegate import ApplicationDocumentDelegate
from .qt_classes.DocumentsTableWidget import DocumentsTableWidget
from .qt_classes.DragTableWidget import DragTableWidget
from .qt_classes.DoubleSpinBoxDelegate import DoubleSpinBoxDelegate
from .qt_classes.DropLabel import DropLabel
from ..view.Ui_ApplicationsDialog import *
from ..utils.SessionHandler import SessionHandler
from ..utils.PluginUtils import PluginUtils
from ..utils.DatabaseUtils import DatabaseUtils
from ..utils.FilePath import *
from ftplib import FTP, error_perm

ATTRIBUTE_NAME = 0
ATTRIBUTE_VALUE = 1

class PlanAttributeEditDialog(QDialog, Ui_PlanAttributeEditDialog, DatabaseHelper):

    def __init__(self, plugin, navigator, parcel_list, process_type, attribute_update=False, parent=None):

        super(PlanAttributeEditDialog, self).__init__(parent)
        DatabaseHelper.__init__(self)

        self.setupUi(self)
        self.navigator = navigator
        self.attribute_update = attribute_update
        self.close_button.clicked.connect(self.reject)
        self.session = SessionHandler().session_instance()
        self.plugin = plugin
        self.parcel_list = parcel_list
        self.process_type = process_type
        self.au2 = DatabaseUtils.working_l2_code()
        self.au1 = DatabaseUtils.working_l1_code()

        self.user = DatabaseUtils.current_sd_user()
        self.user_id = self.user.user_id

        print self.parcel_list
        print self.process_type
        print type(self.process_type)

        self.attribute_twidget = None
        self.__setup_attribute_twidget()

    def __setup_attribute_twidget(self):

        self.attribute_twidget = DragTableWidget("Attribute", 10, 30, 381, 501, self.applicants_group_box)

        header = [self.tr("Attribute Name"),
                  self.tr("Attribute Value")]

        self.attribute_twidget.setup_header(header)
        delegate = DoubleSpinBoxDelegate(ATTRIBUTE_VALUE, 0, 1, 1, 0.1, self.attribute_twidget)
        self.attribute_twidget.setItemDelegateForColumn(ATTRIBUTE_VALUE, delegate)
        # self.attribute_twidget.itemDropped.connect(self.on_application_twidget_itemDropped)
        # self.attribute_twidget.cellChanged.connect(self.on_application_twidget_cellChanged)

