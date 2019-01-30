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
from ..view.Ui_PlanLayerFilterDialog import *
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

class PlanLayerFilterDialog(QDialog, Ui_PlanLayerFilterDialog, DatabaseHelper):

    def __init__(self, plugin, navigator, type_list, attribute_update=False, parent=None):

        super(PlanLayerFilterDialog, self).__init__(parent)
        DatabaseHelper.__init__(self)

        self.setupUi(self)
        self.navigator = navigator
        self.attribute_update = attribute_update
        self.close_button.clicked.connect(self.reject)
        self.session = SessionHandler().session_instance()
        self.plugin = plugin
        self.type_list = type_list
        self.au2 = DatabaseUtils.working_l2_code()
        self.au1 = DatabaseUtils.working_l1_code()

        self.__admin_unit_mapping()
        self.__process_type_mapping()

        self.admin_unit_treewidget.itemChanged.connect(self.__itemAuCheckChanged)
        self.process_type_treewidget.itemChanged.connect(self.__itemProcessCheckChanged)
        self.au2_list = []
        self.process_list = []

    def __itemAuCheckChanged(self, item, column):

        if item.checkState(column) == QtCore.Qt.Checked:
            au2 = item.data(0, Qt.UserRole)
            self.au2_list.append(au2)
        elif item.checkState(column) == QtCore.Qt.Unchecked:
            au2 = item.data(0, Qt.UserRole)
            self.au2_list.remove(au2)

    def __itemProcessCheckChanged(self, item, column):

        if item.checkState(column) == QtCore.Qt.Checked:
            code = item.data(0, Qt.UserRole)
            self.process_list.append(code)
        elif item.checkState(column) == QtCore.Qt.Unchecked:
            code = item.data(0, Qt.UserRole)
            self.process_list.remove(code)

    def __admin_unit_mapping(self):

        tree = self.admin_unit_treewidget
        aimags = self.session.query(AuLevel1.code, AuLevel1.name).order_by(AuLevel1.code.asc()).all()
        for aimag in aimags:
            parent = QTreeWidgetItem(tree)
            parent.setText(0, aimag.code + ': ' + aimag.name)
            parent.setData(0, Qt.UserRole, aimag.code)
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            soums = self.session.query(AuLevel2.code, AuLevel2.name).filter(AuLevel2.au1_code == aimag.code).order_by(AuLevel2.code.asc()).all()
            for soum in soums:
                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, soum.code + ': ' + soum.name)
                child.setData(0, Qt.UserRole, soum.code)
                child.setCheckState(0, Qt.Unchecked)
        tree.show()

    def __process_type_mapping(self):

        tree = self.process_type_treewidget
        parent_types = Constants.plan_process_type_parent
        for parent_type in parent_types:
            parent = QTreeWidgetItem(tree)
            parent.setText(0, str(parent_type) + ': ' + parent_types[parent_type])
            parent.setData(0, Qt.UserRole, parent_type)
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            sub_types = self.session.query(LdProcessPlan).filter(LdProcessPlan.parent_code == str(parent_type)).order_by(LdProcessPlan.code.asc()).all()
            for sub_type in sub_types:
                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, str(sub_type.code) + ': ' + sub_type.description)
                child.setData(0, Qt.UserRole, sub_type.code)
                child.setFlags(child.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

                child_types = self.session.query(LdProcessPlan).filter(
                    LdProcessPlan.parent_code == str(sub_type.code)).order_by(LdProcessPlan.code.asc()).all()
                for child_type in child_types:
                    sub_child = QTreeWidgetItem(child)
                    sub_child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                    sub_child.setText(0, str(child_type.code) + ': ' + child_type.description)
                    sub_child.setData(0, Qt.UserRole, child_type.code)
                    sub_child.setFlags(sub_child.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

                    process_types = self.session.query(LdProcessPlan).filter(
                        LdProcessPlan.parent_code == str(child_type.code)).order_by(LdProcessPlan.code.asc()).all()
                    for process_type in process_types:
                        process_child = QTreeWidgetItem(sub_child)
                        process_child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                        process_child.setText(0, str(process_type.code) + ': ' + process_type.description)
                        process_child.setData(0, Qt.UserRole, process_type.code)
                        process_child.setCheckState(0, Qt.Unchecked)

        tree.show()

    @pyqtSlot()
    def on_ok_button_clicked(self):

        print self.au2_list
        print '----'
        print self.process_list

        aa = SetFilterPlanLayer()

        self.plugin.iface.mapCanvas().refresh()