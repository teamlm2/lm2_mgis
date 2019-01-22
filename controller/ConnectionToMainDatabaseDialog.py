# coding=utf8
__author__ = 'anna'

import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from qgis.core import *
from inspect import currentframe
from ..view.Ui_ConnectionToMainDatabaseDialog import *
from ..model import SettingsConstants
from ..model.SetRole import *
from ..model.SetUserGroupRole import *
from ..utils.SessionHandler import SessionHandler
from sqlalchemy.exc import DatabaseError, SQLAlchemyError
from ..utils.PluginUtils import PluginUtils
from ..model import Constants
from ..model.SdConfiguration import *
from datetime import timedelta, datetime
import win32netcon,win32wnet
import os
import os.path
import shutil
import sys
import win32wnet
import qgis.core

class ConnectionToMainDatabaseDialog(QDialog, Ui_ConnectionToMainDatabaseDialog):

    def __init__(self, iface, parent=None):

        super(ConnectionToMainDatabaseDialog,  self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.setWindowTitle(self.tr("Connection to main database dialog"))
        self.load_settings()
        self.__password = None
        self.__is_expired = False
        self.__setup_validators()
        # self.mac_addr = self.get_mac_address()

    def __setup_validators(self):

        reg_ex = QRegExp(u"[a-z]{4}[0-9]{6}")
        validator = QRegExpValidator(reg_ex, None)
        self.user_name_edit.setValidator(validator)

        reg_ex = QRegExp(u"[a-z0-9_]+")
        validator = QRegExpValidator(reg_ex, None)
        self.password_edit.setValidator(validator)

    def load_settings(self):

        database = QSettings().value(SettingsConstants.DATABASE_NAME)
        host = QSettings().value(SettingsConstants.HOST)
        port = QSettings().value(SettingsConstants.PORT, "5432")
        user = QSettings().value(SettingsConstants.USER)

        self.database_edit.setText(database)
        self.server_name_edit.setText(host)
        self.port_edit.setText(str(port))
        self.user_name_edit.setText(user)

    def get_password(self):
        return self.__password

    def get_expired(self):
        return self.__is_expired

    @pyqtSlot()
    def on_ok_button_clicked(self):

        QSettings().setValue(SettingsConstants.DATABASE_NAME, self.database_edit.text())
        QSettings().setValue(SettingsConstants.HOST, self.server_name_edit.text())
        QSettings().setValue(SettingsConstants.PORT, self.port_edit.text())
        QSettings().setValue(SettingsConstants.USER, self.user_name_edit.text())
        QSettings().setValue(SettingsConstants.PASSWORD, self.password_edit.text())

        host = self.server_name_edit.text().strip()
        port = self.port_edit.text().strip()

        database = self.database_edit.text().strip()
        user = self.user_name_edit.text().strip()
        password = self.password_edit.text().strip()

        self.__password = password
        if not self.password_edit.text():
            PluginUtils.show_message(self, self.tr("Password error"),
                                     self.tr("input password!!!"))
            return

        try:
            if not SessionHandler().create_session(user, password, host, port, database):
                return
        except (DatabaseError, SQLAlchemyError), e:
            PluginUtils.show_error(self, self.tr("Query Error"), self.tr("User name or password is not correct!!!"))
            return

        session = SessionHandler().session_instance()

        conf = session.query(SdConfiguration).filter(SdConfiguration.code == 'setup_version').one()

        if str(Constants.SETUP_VERSION) != conf.value:
            PluginUtils.show_message(self, u'Анхааруулга',
                                     u'Програмын шинэ хувилбарыг суулгана уу! ' + conf.description )
            return
        # self.__layers_permission(user, password, host, port, database)
        self.reject()

    def __replace_line_dump_name(self, file_name, line_num, text):

        lines = open(file_name, 'r').readlines()
        lines[line_num] = ''
        lines[line_num] = text+'\n'
        out = open(file_name, 'w')
        out.writelines(lines)
        out.close()

    def wnet_connect(self, host, username, password):

        if host == 'localhost':
            dest_dir = '\\archive'
        else:
            dest_dir = '\\documents'

        unc = ''.join(['\\\\', host])
        try:
            win32wnet.WNetAddConnection2(win32netcon.RESOURCETYPE_DISK, '',unc+dest_dir, None, username,password, 0)
            # PluginUtils.show_message(self, self.tr("success"), self.tr("Successfully"))
        except Exception, err:
            aa = 0
            # if isinstance(err, win32wnet.error):
                #
                # if err[0] == 1219:
                #     print unc + dest_dir
                #     win32wnet.WNetCancelConnection2(unc + dest_dir, 0, 0)
            # PluginUtils.show_error(self, self.tr("Out error"), self.tr("Not connect. Password incorrect"))

    def covert_unc(self, host, path):

        return ''.join(['\\\\', host, '\\', path.replace(':', '$')])

    def netcopy(self, host, source, dest_dir, username=None, password=None, move=False):

        self.wnet_connect(host, username, password)

        dest_dir = self.covert_unc(host, dest_dir)

        filename = 'test.pdf'
        shutil.copy2(source, dest_dir+'/'+filename)

    def get_mac_address(self):

        if sys.platform == 'win32':
            for line in os.popen("ipconfig /all"):
                if line.lstrip().startswith('Physical Address'):
                    mac = line.split(':')[1].strip().replace('-', ':')
                    if len(mac) == 17:
                        mac = line.split(':')[1].strip().replace('-', ':')
                    break
        else:
            for line in os.popen("/sbin/ifconfig"):
                if line.find('Ether') > -1:
                    mac = line.split()[4]
                    if len(mac) == 17:
                        mac = line.split(':')[1].strip().replace('-', ':')
                    break
        return mac

    @pyqtSlot()
    def on_cancel_button_clicked(self):
        self.reject()

    @pyqtSlot()
    def on_help_button_clicked(self):

        os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/Create_New_Postgis_Connection.htm")

    def __layers_permission(self, user, password, host, port, database):

        layers = self.iface.legendInterface().layers()
        ###################

        try:
            if not SessionHandler().create_session(user, password, host, port, database):
                return
        except (DatabaseError, SQLAlchemyError), e:
            PluginUtils.show_error(self, self.tr("Query Error"), self.tr("User name or password is not correct!!!"))
            return

        session = SessionHandler().session_instance()

        role_count = session.query(SetRole).\
            filter(SetRole.user_name == user).\
            filter(SetRole.is_active == True).count()
        if user.find("user") == -1:
            return
        if role_count  == 1:
            role = session.query(SetRole). \
                filter(SetRole.user_name == user). \
                filter(SetRole.is_active == True).one()
            user_name_real = role.user_name_real
            l2_code_list = role.restriction_au_level2.split(',')

            user_right_parcel_count = session.query(SetUserGroupRole). \
                filter(SetUserGroupRole.user_name_real == user_name_real). \
                filter(SetUserGroupRole.group_role == 6).count()

            user_right_temp_parcel_count = session.query(SetUserGroupRole). \
                filter(SetUserGroupRole.user_name_real == user_name_real). \
                filter(SetUserGroupRole.group_role == 7).count()

            vlayer = LayerUtils.layer_by_data_source("admin_units", "au_mpa_zone")
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