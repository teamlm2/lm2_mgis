__author__ = 'B.Ankhbold'
import os
import shutil
from sqlalchemy.exc import SQLAlchemyError
from ...utils.FtpConnection import *
from ...utils.PasturePath import *
from ...utils.PluginUtils import *
from ...model.CtDocument import *
from ...model.SdConfiguration import *
import urllib
import urllib2

PROVIDED_COLUMN = 0
FILE_TYPE_COLUMN = 1
FILE_NAME_COLUMN = 2
OPEN_FILE_COLUMN = 3
DELETE_COLUMN = 4
VIEW_COLUMN = 5


class PastureApplicationDocumentDelegate(QStyledItemDelegate):

    def __init__(self, widget, parent):

        super(PastureApplicationDocumentDelegate, self).__init__(parent)
        self.widget = widget
        self.parent = parent
        self.session = SessionHandler().session_instance()
        self.button = QPushButton("", parent)
        self.button.hide()

        self.remove = QIcon(":/plugins/lm2/remove.png")
        self.openIcon = QIcon(":/plugins/lm2/open.png")
        self.viewIcon = QIcon(":/plugins/lm2/file.png")

    def paint(self, painter, option, index):

        if index.column() == OPEN_FILE_COLUMN:
            self.button.setIcon(self.openIcon)
        elif index.column() == DELETE_COLUMN:
            self.button.setIcon(self.remove)
        elif index.column() == VIEW_COLUMN:
            self.button.setIcon(self.viewIcon)
        else:
            super(PastureApplicationDocumentDelegate, self).paint(painter, option, index)
            return

        self.button.setGeometry(option.rect)
        button_picture = QPixmap.grabWidget(self.button)
        painter.drawPixmap(option.rect.x(), option.rect.y(), button_picture)

    def editorEvent(self, event, model, option, index):

        if not index is None:

            if index.isValid() and event.type() == QEvent.MouseButtonRelease:
                app_id = self.parent.current_application().app_id
                role = self.widget.item(index.row(), FILE_TYPE_COLUMN).data(Qt.UserRole)

                archive_ftp_path = PasturePath.app_ftp_parent_path('document') + '/' + str(self.parent.current_application_no())
                if event.button() == Qt.RightButton:
                    return False

                if index.column() == OPEN_FILE_COLUMN:
                    file_dialog = QFileDialog()
                    file_dialog.setFilter('PDF (*.pdf)')
                    file_dialog.setModal(True)
                    file_dialog.setFileMode(QFileDialog.ExistingFile)
                    if file_dialog.exec_():
                        selected_file = file_dialog.selectedFiles()[0]
                        file_info = QFileInfo(selected_file)
                        if QFileInfo(file_info).size() / (1024 * 1024) > 5:
                            PluginUtils.show_error(self.parent, self.tr("File size exceeds limit!"),
                                                   self.tr("The maximum size of documents to be attached is 5 MB."))
                            return False
                        file_name = str(self.parent.current_application_no()) + "-" + str(role).zfill(
                            2) + "." + file_info.suffix()
                        if DatabaseUtils.ftp_connect():
                            ftp = DatabaseUtils.ftp_connect()

                            FtpConnection.chdir(archive_ftp_path, ftp[0])
                            FtpConnection.upload_app_ftp_file(selected_file, file_name, ftp[0])

                            file_url_name = archive_ftp_path + '/' + file_name
                            app_doc_count = self.session.query(CtApplicationDocument).filter(
                                CtApplicationDocument.application_id == app_id). \
                                filter(CtApplicationDocument.role == role).count()
                            if app_doc_count == 0:
                                doc = CtDocument()
                                doc.name = file_name
                                doc.created_by = DatabaseUtils.current_sd_user().user_id
                                doc.created_at = DatabaseUtils.current_date_time()
                                doc.updated_at = DatabaseUtils.current_date_time()
                                doc.file_url = file_url_name
                                doc.ftp_id = ftp[1].ftp_id
                                self.session.add(doc)
                                self.session.flush()

                                app_doc = CtApplicationDocument()
                                app_doc.application_id = app_id
                                app_doc.document_id = doc.id
                                app_doc.role = role
                                self.session.add(app_doc)
                                self.session.flush()
                                self.session.commit()

                            elif app_doc_count == 1:
                                app_doc = self.session.query(CtApplicationDocument).filter(
                                    CtApplicationDocument.application_id == app_id). \
                                    filter(CtApplicationDocument.role == role).one()

                                doc_count = self.session.query(CtDocument).filter(CtDocument.id == app_doc.document_id).count()
                                if doc_count == 1:
                                    doc = self.session.query(CtDocument).filter(
                                        CtDocument.id == app_doc.document_id).one()

                                    doc.updated_at = DatabaseUtils.current_date_time()
                                    doc.file_url = file_url_name
                                    doc.ftp_id = ftp[1].ftp_id

                            # try:

                            self.widget.item(index.row(), FILE_NAME_COLUMN).setText(file_name)

                            check_item = self.widget.item(index.row(), PROVIDED_COLUMN)
                            check_item.setCheckState(True)
                            #
                            # except SQLAlchemyError, e:
                            #     PluginUtils.show_error(self, self.tr("File Error"), self.tr("Could not execute: {0}").format(e.message))
                            #     return True

                elif index.column() == VIEW_COLUMN:
                    if DatabaseUtils.ftp_connect():
                        ftp = DatabaseUtils.ftp_connect()
                        app_doc_count = self.session.query(CtApplicationDocument).filter(
                            CtApplicationDocument.application_id == app_id). \
                            filter(CtApplicationDocument.role == role).count()
                        if app_doc_count == 1:
                            app_doc = self.session.query(CtApplicationDocument).filter(
                                CtApplicationDocument.application_id == app_id). \
                                filter(CtApplicationDocument.role == role).one()
                            doc = self.session.query(CtDocument).filter(CtDocument.id == app_doc.document_id).one()

                            archive_app_path = r'D:/TM_LM2/view.pdf'
                            view_pdf = open(archive_app_path, 'wb')
                            file_url = ''

                            url_splits = doc.file_url.split('/')
                            for url_split in url_splits:
                                if not url_split.endswith('.pdf'):
                                    if file_url == '':
                                        file_url = url_split
                                    else:
                                        file_url = file_url + '/' + url_split
                            # # for each word in the line:
                            try:
                                ftp[0].cwd(file_url)
                                ftp[0].retrbinary('RETR ' + doc.name, view_pdf.write)
                            except Exception, e:
                                errorcode_string = str(e).split(None, 1)[0]
                                if errorcode_string == '550':
                                    QMessageBox.information(None, QApplication.translate("LM2", "Warning"),
                                                            QApplication.translate("LM2",
                                                                                   "Not found directory or file, Please reupload"))
                                else:
                                    QMessageBox.information(None, QApplication.translate("LM2", "Warning"),
                                                            QApplication.translate("LM2",
                                                                                   "Not found directory or file, Please reupload"))
                                return True

                            try:
                                QDesktopServices.openUrl(QUrl.fromLocalFile(archive_app_path))
                            except IOError, e:
                                QMessageBox.information(None, QApplication.translate("LM2", "No parcel"),
                                                        QApplication.translate("LM2",
                                                                               "This file is already opened. Please close re-run"))
                                return True

                elif index.column() == DELETE_COLUMN:

                    message_box = QMessageBox()
                    message_box.setText(self.tr("Do you want to delete the selected document?"))

                    delete_button = message_box.addButton(self.tr("Delete"), QMessageBox.ActionRole)
                    message_box.addButton(self.tr("Cancel"), QMessageBox.ActionRole)
                    message_box.exec_()

                    if message_box.clickedButton() == delete_button:
                        try:
                            check_item = self.widget.item(index.row(), PROVIDED_COLUMN)
                            check_item.setCheckState(False)
                            self.widget.item(index.row(), FILE_NAME_COLUMN).setText("")
                        except SQLAlchemyError, e:
                            PluginUtils.show_error(self, self.tr("File Error"),
                                                   self.tr("Could not execute: {0}").format(e.message))
                            return True

                elif index.column() == PROVIDED_COLUMN:
                    if index.data(Qt.CheckStateRole) == Qt.Unchecked:
                        item = self.widget.item(index.row(), PROVIDED_COLUMN)
                        item.setCheckState(Qt.Checked)
                    else:
                        item = self.widget.item(index.row(), PROVIDED_COLUMN)
                        item.setCheckState(Qt.Unchecked)

                elif index.column() == FILE_TYPE_COLUMN or index.column() == FILE_NAME_COLUMN:
                    return False

                else:
                    index.model().setData(index, 0, Qt.EditRole)
        return False
