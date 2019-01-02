__author__ = 'B.Ankhbold'
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sqlalchemy.exc import SQLAlchemyError
from ...utils.FilePath import *
from ...utils.PluginUtils import *
from ...model.CtDocument import *
import shutil
import os
import subprocess

PROVIDED_COLUMN = 0
FILE_TYPE_COLUMN = 1
FILE_NAME_COLUMN = 2
OPEN_FILE_COLUMN = 3
DELETE_COLUMN = 4
VIEW_COLUMN = 5


class FtpConnection(QStyledItemDelegate):

    def __init__(self, widget, parent):

        super(FtpConnection, self).__init__(parent)
        self.widget = widget
        self.parent = parent
        self.session = SessionHandler().session_instance()
        self.button = QPushButton("", parent)
        self.button.hide()

    def chdir(self, ftp_path, ftp_conn):
        dirs = [d for d in ftp_path.split('/') if d != '']
        for p in dirs:
            self.check_dir(p, ftp_conn)

    def check_dir(self, dir, ftp_conn):
        filelist = []
        ftp_conn.retrlines('LIST', filelist.append)
        found = False

        for f in filelist:
            if f.split()[-1] == dir and f.lower().startswith('d'):
                found = True

        if not found:
            ftp_conn.mkd(dir)
        ftp_conn.cwd(dir)
