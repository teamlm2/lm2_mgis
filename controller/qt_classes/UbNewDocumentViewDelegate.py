# coding=utf8
__author__ = 'B.Ankhbold'
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sqlalchemy.exc import SQLAlchemyError
from ...model import SettingsConstants
from ...model.SetOfficialDocument import SetOfficialDocument
from ...utils.FileUtils import FileUtils
from ...utils.PluginUtils import PluginUtils
from ...utils.SessionHandler import SessionHandler
from ...utils.DatabaseUtils import *
from ...utils.FilePath import *
from ftplib import *
import shutil
import codecs
NAME_COLUMN = 0
DESCRIPTION_COLUMN = 1
VIEW_COLUMN = 2
FILE_PDF = 'pdf'
FILE_IMAGE = 'png'

class UbNewDocumentViewDelegate(QStyledItemDelegate):

    def __init__(self, widget, parent):

        super(UbNewDocumentViewDelegate, self).__init__(parent)
        self.widget = widget
        self.parent = parent
        self.session = SessionHandler().session_instance()
        self.button = QPushButton("", parent)
        self.button.hide()

        self.viewIcon = QIcon(":/plugins/lm2/file.png")

    def paint(self, painter, option, index):

        if index.column() == VIEW_COLUMN:
            self.button.setIcon(self.viewIcon)
        else:
            super(UbNewDocumentViewDelegate, self).paint(painter, option, index)
            return

        self.button.setGeometry(option.rect)
        button_picture = QPixmap.grabWidget(self.button)
        painter.drawPixmap(option.rect.x(), option.rect.y(), button_picture)

    def editorEvent(self, event, model, option, index):

        if index is not None:

            if index.isValid() and event.type() == QEvent.MouseButtonRelease:

                if event.button() == Qt.RightButton:
                    return False

                if index.column() == VIEW_COLUMN:

                    ftp = self.widget.item(index.row(), NAME_COLUMN).data(Qt.UserRole)
                    file_name = self.widget.item(index.row(), NAME_COLUMN).data(Qt.UserRole + 1)
                    file_type = self.widget.item(index.row(), NAME_COLUMN).data(Qt.UserRole + 2)

                    # print file_name
                    # print file_type
                    # print ftp.pwd()
                    # print ftp.nlst()

                    view_pdf = open(FilePath.view_file_path(), 'wb')
                    view_png = open(FilePath.view_file_png_path(), 'wb')

                    if file_type == FILE_IMAGE:
                        ftp.retrbinary('RETR ' + file_name, view_png.write)
                    else:
                        ftp.retrbinary('RETR ' + file_name, view_pdf.write)
                    try:
                        if file_type == FILE_IMAGE:
                            QDesktopServices.openUrl(QUrl.fromLocalFile(FilePath.view_file_png_path()))
                        else:
                            QDesktopServices.openUrl(QUrl.fromLocalFile(FilePath.view_file_path()))
                    except SQLAlchemyError, e:
                            PluginUtils.show_error(self.parent, self.tr("File Error"), self.tr("Could not execute: {0}").format(e.message))
                            return True

                elif index.column() == DESCRIPTION_COLUMN or index.column() == NAME_COLUMN:
                    return True

                else:
                    index.model().setData(index, 0, Qt.EditRole)
        return False
