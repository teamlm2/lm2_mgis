# coding=utf8
__author__ = 'ankhbold'

import os
from os import walk
import shutil
import zlib
from PIL import Image
from sqlalchemy.exc import SQLAlchemyError
from qgis.core import *
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import func, or_, and_, desc
from sqlalchemy.sql.expression import cast
from sqlalchemy import func
from xlrd import open_workbook
from ..view.Ui_PdfInsertDialog import *
from ..utils.PluginUtils import *
from ..model.ClDocumentRole import *
from ..model.CtContractApplicationRole import *
from ..model.CtContractDocument import *
from ..model.SetContractDocumentRole import *
from ..model.CtRecordApplicationRole import *
from ..model.CtRecordDocument import *
from ..utils.FilePath import *
from ..model.CtDecisionDocument import *
from ..utils.FileUtils import FileUtils

class PdfInsertDialog(QDialog, Ui_PdfInsertDialog):

    def __init__(self, parent=None):

        super(PdfInsertDialog,  self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle(self.tr("Pdf file insert Dialog"))
        self.close_button.clicked.connect(self.reject)
        self.session = SessionHandler().session_instance()
        self.progressBar.setMinimum(1)
        self.progressBar.setValue(0)

        self.import_data_twidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.import_data_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.import_data_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.import_data_twidget.setSortingEnabled(True)

    @pyqtSlot()
    def on_select_file_button_clicked(self):

        file_dialog = QFileDialog()
        file_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
        file_dialog.setModal(True)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setFilter(self.tr("Decision Files (*.img *.png *.pdf)"))
        if file_dialog.exec_():

            selected_file = file_dialog.selectedFiles()[0]

            file_path = QFileInfo(selected_file).path()
            self.decision_file_edit.setText(file_path)

            self.tableWidget.setRowCount(0)
            count = 0
            parcel_count = 0
            f = ""
            for file in os.listdir(file_path):
                # if file.endswith(".pdf"):
                    name = file[:-8]
                    parcel_id = "0"+name[:-8]+"0"+name[2:]
                    if parcel_id != f:
                        parcel_count +=1
                    f = parcel_id
                    item_name = QTableWidgetItem(str(file))
                    item_name.setData(Qt.UserRole,file)

                    self.tableWidget.insertRow(count)
                    self.tableWidget.setItem(count,0,item_name)
                    count +=1
            self.count.setText(str(count))
            self.parcel_count_lbl.setText(str(parcel_count))

    @pyqtSlot()
    def on_import_button_clicked(self):

        session = SessionHandler().session_instance()

        count = int(self.count.text())
        self.progressBar.setMaximum(count)
        file_path = self.decision_file_edit.text()

        for file in os.listdir(file_path):

            con_doc = CtDocument()
            if file.endswith(".pdf"):
                 name = file[:-8]
                 parcel_id = "0"+name[:-8]+"0"+name[2:]

                 full_name = file[:-4]
                 path = str(self.decision_file_edit.text()+"/"+file)

                 data = DatabaseUtils.file_data(path)
                 document_type = full_name[12:]

                 application_count = session.query(CtApplication).filter(CtApplication.parcel == parcel_id).count()
                 if application_count == 1 and len(full_name) == 14:

                     application = session.query(CtApplication).filter(CtApplication.parcel == parcel_id).one()
                     parcel = session.query(CaParcel).filter(CaParcel.parcel_id == parcel_id).one()
                     admin2 = session.query(AuLevel2).filter(AuLevel2.geometry.ST_Contains(parcel.geometry)).one()
                     year_filter = str(QDate().currentDate().toString("yy"))
                     if len(str(application.app_type)) == 1:
                        document_name = str(admin2.code) +"-"+ "0"+str(application.app_type) +"-"+ name[5:]+"-"+year_filter+"-"+document_type+".pdf"
                     else:
                         document_name = str(admin2.code) +"-"+str(application.app_type) +"-"+ name[5:]+"-"+year_filter+"-"+document_type+".pdf"
                     value = self.progressBar.value() + 1
                     self.progressBar.setValue(value)
                     try:
                            doc_c = self.session.query(CtDocument).filter(CtDocument.name == document_name).count()
                            if doc_c == 0:
                                con_doc.name = document_name
                                con_doc.content = bytes(data)
                                value = self.progressBar.value() + 1
                                self.progressBar.setValue(value)
                                session.add(con_doc)
                                session.commit()
                                document_id = con_doc.id
                                application_person = session.query(CtApplicationPersonRole).filter(CtApplicationPersonRole.application == application.app_no).all()
                                application_contract_count = session.query(CtContractApplicationRole).filter(CtContractApplicationRole.application == application.app_no).count()

                                application_record_count = session.query(CtRecordApplicationRole).filter(CtRecordApplicationRole.application == application.app_no).count()

                                for app_person in application_person:
                                    if app_person.main_applicant == True:
                                        if int(document_type):
                                            doc_count = session.query(ClDocumentRole).filter(ClDocumentRole.code == int(document_type)).count()
                                            doc_contract_count = session.query(SetContractDocumentRole).filter(SetContractDocumentRole.role == int(document_type)).count()

                                            if doc_count == 1:
                                                app_doc = CtApplicationDocument()

                                                doc_role = session.query(ClDocumentRole).filter(ClDocumentRole.code == int(document_type)).one()
                                                document_role = doc_role.code
                                                count_doc = self.session.query(CtApplicationDocument).filter(CtApplicationDocument.application == application.app_no)\
                                                                                        .filter(CtApplicationDocument.document == document_id).count()
                                                if count_doc == 0:
                                                    app_doc.application = application.app_no
                                                    app_doc.document = document_id
                                                    app_doc.person = app_person.person
                                                    app_doc.role = document_role
                                                    session.add(app_doc)

                                            decision_app_count = session.query(CtDecisionApplication).filter(CtDecisionApplication.application == application.app_no).count()
                                            if int(document_type) == 17 and decision_app_count == 1:
                                                decision_app = session.query(CtDecisionApplication).filter(CtDecisionApplication.application == application.app_no).one()

                                                decision_doc = CtDecisionDocument()
                                                count_doc = self.session.query(CtDecisionDocument).filter(CtDecisionDocument.decision == decision_app.decision)\
                                                                                        .filter(CtDecisionDocument.document == document_id).count()
                                                if count_doc == 0:
                                                    decision_doc.decision = decision_app.decision
                                                    decision_doc.document = document_id
                                                    session.add(decision_doc)

                                            if application_contract_count == 1:
                                                application_contract =session.query(CtContractApplicationRole).filter(CtContractApplicationRole.application == application.app_no).one()
                                                if doc_contract_count == 1:
                                                    doc_contract_role = session.query(SetContractDocumentRole).filter(SetContractDocumentRole.role == int(document_type)).one()

                                                    document_contract_role = doc_contract_role.role
                                                    contact_doc = CtContractDocument()
                                                    count_doc = self.session.query(CtContractDocument).filter(CtContractDocument.contract == application_contract.contract)\
                                                                                        .filter(CtContractDocument.document == document_id).count()
                                                    if count_doc == 0:
                                                        contact_doc.contract = application_contract.contract
                                                        contact_doc.document = document_id
                                                        contact_doc.role = document_contract_role
                                                        session.add(contact_doc)
                                            elif application_record_count == 1:
                                                application_record =session.query(CtRecordApplicationRole).filter(CtRecordApplicationRole.application == application.app_no).one()
                                                if doc_contract_count == 1:

                                                    doc_contract_role = session.query(SetContractDocumentRole).filter(SetContractDocumentRole.role == int(document_type)).one()
                                                    document_contract_role = doc_contract_role.role
                                                    record_doc = CtRecordDocument()
                                                    count_doc = self.session.query(CtRecordDocument).filter(CtRecordDocument.record == application_record.record)\
                                                                                        .filter(CtRecordDocument.document == document_id).count()
                                                    if count_doc == 0:
                                                        record_doc.record = application_record.record
                                                        record_doc.document = document_id
                                                        record_doc.role = document_contract_role
                                                        session.add(record_doc)

                     except SQLAlchemyError, e:
                            session.rollback()
                            PluginUtils.show_error(self, self.tr("Database Error"), e.message)
                            return
        session.commit()
        PluginUtils.show_message(self,self.tr("Success"),self.tr("Successfully"))
        self.accept()

    @pyqtSlot()
    def on_rename_button_clicked(self):
        session = SessionHandler().session_instance()

        count = int(self.count.text())
        self.progressBar.setMaximum(count)
        file_path = self.decision_file_edit.text()

        archive_app_path = FilePath.app_file_path()
        if not os.path.exists(archive_app_path):
            os.makedirs(archive_app_path)

        for file in os.listdir(file_path):

            if file.endswith(".pdf"):
                 name = file[:-8]
                 parcel_id = "0"+name[:-8]+"0"+name[2:]

                 full_name = file[:-4]
                 document_type = full_name[12:]

                 application_count = session.query(CtApplication).filter(CtApplication.parcel == parcel_id).count()
                 if application_count == 1 and len(full_name) == 14:

                     application = session.query(CtApplication).filter(CtApplication.parcel == parcel_id).one()
                     app_year = application.app_no[-2:]
                     parcel = session.query(CaParcel).filter(CaParcel.parcel_id == parcel_id).one()
                     admin2 = session.query(AuLevel2).filter(AuLevel2.geometry.ST_Contains(parcel.geometry)).one()
                     year_filter = str(QDate().currentDate().toString("yy"))
                     app_no = None
                     if len(str(application.app_type)) == 1:
                        document_name = str(admin2.code) +"-"+ "0"+str(application.app_type) +"-"+ name[5:]+"-"+app_year+"-"+document_type+".pdf"
                        app_no = str(admin2.code) +"-"+ "0"+str(application.app_type) +"-"+ name[5:]+"-"+app_year
                     else:
                         document_name = str(admin2.code) +"-"+str(application.app_type) +"-"+ name[5:]+"-"+app_year+"-"+document_type+".pdf"
                         app_no = str(admin2.code) +"-"+ "0"+str(application.app_type) +"-"+ name[5:]+"-"+app_year
                     if app_no:
                         app_path_folder = archive_app_path + '/' + app_no
                         if not os.path.exists(app_path_folder):
                             os.makedirs(app_path_folder)
                         value = self.progressBar.value() + 1
                         self.progressBar.setValue(value)
                         file_with_dir = app_path_folder+'/'+document_name
                         if not os.path.isfile(file_with_dir):
                            shutil.copy2(file_path+'/'+file, app_path_folder+'/'+document_name)

    @pyqtSlot()
    def on_output_file_button_clicked(self):

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)

        if dialog.exec_():
            for directory in dialog.selectedFiles():
                self.output_file_edit.setText(directory)

    @pyqtSlot()
    def on_export_button_clicked(self):

        # if not self.output_file_edit.text():
        #     PluginUtils.show_message(self,self.tr("Director"),self.tr("Select output director!!!"))
        #     return
        archive_app_path = FilePath.app_file_path()
        if not os.path.exists(archive_app_path):
            os.makedirs(archive_app_path)

        documents = self.session.query(CtApplicationDocument).all()
        count = self.session.query(CtApplicationDocument).count()
        self.progressBar.setMaximum(count)
        for document in documents:

            app_no = document.application
            app_no_dir = archive_app_path + '/' + app_no
            if not os.path.exists(app_no_dir):
                os.makedirs(app_no_dir)
                app_docs = self.session.query(CtApplicationDocument).filter(CtApplicationDocument.application == app_no).all()
                #if python_array is None:
                #    PluginUtils.show_message(self, self.tr("Error"), self.tr("No digital documents available."))
                #    return False
                for document in app_docs:
                    python_array = document.document_ref.content
                    if python_array != None:
                        role = document.role
                        file_name = document.document_ref.name
                        qt_array = QByteArray(python_array)
                        current_bytes = QByteArray(qt_array)
                        item_file_path = FileUtils.temp_file_path() + "/" \
                                         + unicode(file_name)

                        new_file = QFile(item_file_path)
                        new_file.open(QIODevice.WriteOnly)
                        new_file.write(current_bytes.data())
                        file_info = QFileInfo(new_file)
                        new_file.close()
                        file_name = document.application + "-" + str(role) + "." + file_info.suffix()
                        shutil.copy2(item_file_path, app_no_dir+'/'+file_name)

                        value = self.progressBar.value() + 1
                        self.progressBar.setValue(value)

        PluginUtils.show_message(self,self.tr("Success"),self.tr("Successfully"))

    @pyqtSlot()
    def on_conver_version_button_clicked(self):

        archive_app_path = FilePath.app_file_path()
        for file in os.listdir(archive_app_path):
            if file.endswith(".pdf"):
                 app_no = file[:17]
                 if len(app_no)==17:
                     app_path = archive_app_path + '/' + app_no
                     if not os.path.exists(app_path):
                         os.makedirs(app_path)
                     shutil.copy2(archive_app_path + '/' + file, app_path + '/' + file)

    @pyqtSlot()
    def on_darkhan_button_clicked(self):

        session = SessionHandler().session_instance()

        count = int(self.count.text())
        self.progressBar.setMaximum(count)
        file_path = self.decision_file_edit.text()

        archive_app_path = FilePath.app_file_path()
        if not os.path.exists(archive_app_path):
            os.makedirs(archive_app_path)

        for file in os.listdir(file_path):

            if file.endswith(".pdf"):
                name = file[:-8]
                old_parcel_id_sub = name[5:]
                old_parcel_id_like = '%'+old_parcel_id_sub

                parcel_count = self.session.query(CaParcel).filter(CaParcel.old_parcel_id.ilike(old_parcel_id_like)).count()

                if parcel_count == 1:
                    parcel = self.session.query(CaParcel).filter(
                        CaParcel.old_parcel_id.like(old_parcel_id_like)).one()

                    parcel_id = parcel.parcel_id

                    full_name = file[:-4]
                    document_type = full_name[12:]

                    application_count = session.query(CtApplication).filter(CtApplication.parcel == parcel_id).count()
                    if application_count == 1 and len(full_name) == 14:
                        application = session.query(CtApplication).filter(CtApplication.parcel == parcel_id).one()
                        app_no = application.app_no
                        document_name = app_no + "-" + document_type + ".pdf"

                        if app_no:
                            app_path_folder = archive_app_path + '/' + app_no
                            if not os.path.exists(app_path_folder):
                                os.makedirs(app_path_folder)
                            value = self.progressBar.value() + 1
                            self.progressBar.setValue(value)
                            file_with_dir = app_path_folder + '/' + document_name
                            if not os.path.isfile(file_with_dir):
                                shutil.copy2(file_path + '/' + file, app_path_folder + '/' + document_name)

    @pyqtSlot()
    def on_select_dir_button_clicked(self):

        file_dialog = QFileDialog()
        # file_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
        # file_dialog.setModal(True)
        file_dialog.setFileMode(QFileDialog.Directory)

        if file_dialog.exec_():
            selected_directory = file_dialog.getExistingDirectory()
            print selected_directory
            # selected_file = file_dialog.selectedFiles()[0]
            #
            # file_path = QFileInfo(selected_file).path()
            self.dir_path_edit.setText(selected_directory)

            for root, dirs, files in os.walk(selected_directory):
                count = 0
                for file in files:
                    if file.endswith('.png'):
                        print root
                        print dirs
                        print file
                        self.files_twidget.insertRow(count)

                        item = QTableWidgetItem(str(root))
                        item.setData(Qt.UserRole, root)
                        self.files_twidget.setItem(count, 0, item)

                        item = QTableWidgetItem(str(file))
                        item.setData(Qt.UserRole, file)
                        self.files_twidget.setItem(count, 1, item)
                        count += 1

    @pyqtSlot()
    def on_compressor_button_clicked(self):

        selected_directory = self.dir_path_edit.text()
        #
        for root, dirs, files in os.walk(selected_directory):
            count = 0
            for file in files:
                if file.endswith('.png'):
                    print selected_directory
                    print root
                    print root.split(selected_directory)[1]

        # session = SessionHandler().session_instance()
        #
        # count = int(self.count.text())
        # self.progressBar.setMaximum(count)
        # file_path = self.decision_file_edit.text()
        #
        # for file in os.listdir(file_path):
        #
        #     if file.endswith(".png"):
        #         print file_path
        #         print file
        #
        #         file = file_path +'/'+ file
        #         archive_app_path = r'D:/'
        #
        #         if not os.path.isfile(archive_app_path):
        #             compImg = Image.open(file)
        #             # compress file at 50% of previous quality
        #             out_dir = 'D:/compressor/test_jpg.jpg'
        #             compImg.save(out_dir, "JPEG", quality=0)
        #             # shutil.copy2(file_path + '/' + file, app_path_folder + '/' + document_name)

    @pyqtSlot()
    def on_load_shp_button_clicked(self):

        # default_path = self.__default_path()
        file_dialog = QFileDialog()
        file_dialog.setModal(True)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setFilter(self.tr("Shapefiles (*.shp)"))
        # file_dialog.setDirectory(default_path)

        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            file_path = QFileInfo(selected_file).filePath()
            self.file_path = file_path
            self.load_shp_edit.setText(file_path)
            # self.__read_shp_file(file_path)
            self.load_shp_button.setEnabled(False)

    @pyqtSlot()
    def on_load_xls_button_clicked(self):

        # default_path = self.__default_path()
        file_dialog = QFileDialog()
        file_dialog.setModal(True)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        # file_dialog.setFilter(self.tr("Shapefiles (*.shp)"))
        # file_dialog.setDirectory(default_path)

        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            file_path = QFileInfo(selected_file).filePath()
            self.file_path = file_path
            self.load_xls_edit.setText(file_path)
            self.__read_xls_file(file_path)
            # self.load_xls_button.setEnabled(False)

    def __read_shp_file(self, file_path):

        parcel_shape_layer = QgsVectorLayer(file_path, "tmp_landuse_parcel_shape", "ogr")

        if not parcel_shape_layer.isValid():
            PluginUtils.show_error(self,  self.tr("Error loading layer"), self.tr("The layer is invalid."))
            return

        if parcel_shape_layer.crs().postgisSrid() != 4326:
            PluginUtils.show_error(self, self.tr("Error loading layer"),
                                   self.tr("The crs of the layer has to be 4326."))
            return

        iterator = parcel_shape_layer.getFeatures()
        provider = parcel_shape_layer.dataProvider()
        feature_count = parcel_shape_layer.featureCount()

        for parcel in iterator:
            feature_id = parcel.id()
            landuse = self.__get_attribute(parcel, parcel_shape_layer)
            print landuse


    def __read_xls_file(self, file_name):

        if file_name == "":
            PluginUtils.show_message(self, self.tr("File operation"), self.tr("Please select a file."))
            return

        if not QFileInfo(file_name).exists():
            PluginUtils.show_message(self, self.tr("File operation"), self.tr("Invalid file."))
            return

        workbook = open_workbook(file_name)
        worksheet = workbook.sheet_by_name('data')
        # num_rows = worksheet.nrows - 1
        # num_cells = worksheet.ncols - 1
        # curr_row = -1
        self.import_data_twidget.setRowCount(0)
        count = 0

        for curr_row in range(worksheet.nrows - 1):
            curr_row = curr_row + 1
            row = worksheet.row(curr_row)
            parcel_id = worksheet.cell_value(curr_row, 1)
            old_parcel_id = worksheet.cell_value(curr_row, 2)
            landuse = worksheet.cell_value(curr_row, 3)
            horoo = worksheet.cell_value(curr_row, 4)
            gudamj = worksheet.cell_value(curr_row, 5)
            hashaa = worksheet.cell_value(curr_row, 6)
            register = worksheet.cell_value(curr_row, 7)
            middlename = worksheet.cell_value(curr_row, 8)
            ovog = worksheet.cell_value(curr_row, 9)
            ner = worksheet.cell_value(curr_row, 10)
            utas1 = worksheet.cell_value(curr_row, 11)
            utas2 = worksheet.cell_value(curr_row, 12)
            heid = worksheet.cell_value(curr_row, 13)
            gaid = worksheet.cell_value(curr_row, 14)
            zovshbaig = worksheet.cell_value(curr_row, 15)
            shovshshiid = worksheet.cell_value(curr_row, 16)
            zovshdate = worksheet.cell_value(curr_row, 17)
            gerchid = worksheet.cell_value(curr_row, 18)
            duusdate = worksheet.cell_value(curr_row, 19)
            tailbar = worksheet.cell_value(curr_row, 20)
            gerid = worksheet.cell_value(curr_row, 21)
            gerdate = worksheet.cell_value(curr_row, 22)

            self.import_data_twidget.insertRow(count)


            is_valid = self.__validate_import_data(landuse, register, middlename, ovog, ner, heid, gaid, zovshbaig, shovshshiid, zovshdate)
            print is_valid
            item = QTableWidgetItem(str(parcel_id))
            item.setData(Qt.UserRole, parcel_id)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            if not is_valid:
                item.setBackground(Qt.yellow)
            self.import_data_twidget.setItem(count, 0, item)

            item = QTableWidgetItem(str(landuse))
            item.setData(Qt.UserRole, landuse)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            if not is_valid:
                item.setBackground(Qt.yellow)
            self.import_data_twidget.setItem(count, 1, item)

            item = QTableWidgetItem(unicode(register))
            item.setData(Qt.UserRole, register)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.import_data_twidget.setItem(count, 2, item)

            item = QTableWidgetItem(unicode(middlename))
            item.setData(Qt.UserRole, middlename)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.import_data_twidget.setItem(count, 3, item)

            item = QTableWidgetItem(unicode(ovog))
            item.setData(Qt.UserRole, ovog)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.import_data_twidget.setItem(count, 4, item)

            item = QTableWidgetItem(unicode(ner))
            item.setData(Qt.UserRole, ner)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.import_data_twidget.setItem(count, 5, item)

            item = QTableWidgetItem(unicode(heid))
            item.setData(Qt.UserRole, heid)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.import_data_twidget.setItem(count, 6, item)

            item = QTableWidgetItem(unicode(gaid))
            item.setData(Qt.UserRole, gaid)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.import_data_twidget.setItem(count, 7, item)

            item = QTableWidgetItem(unicode(zovshbaig))
            item.setData(Qt.UserRole, zovshbaig)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.import_data_twidget.setItem(count, 8, item)

            item = QTableWidgetItem(unicode(shovshshiid))
            item.setData(Qt.UserRole, shovshshiid)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.import_data_twidget.setItem(count, 9, item)

            item = QTableWidgetItem(unicode(zovshdate))
            item.setData(Qt.UserRole, zovshdate)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.import_data_twidget.setItem(count, 10, item)

            item = QTableWidgetItem(unicode(gerchid))
            item.setData(Qt.UserRole, gerchid)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.import_data_twidget.setItem(count, 11, item)

            item = QTableWidgetItem(unicode(duusdate))
            item.setData(Qt.UserRole, duusdate)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.import_data_twidget.setItem(count, 12, item)

            item = QTableWidgetItem(unicode(gerdate))
            item.setData(Qt.UserRole, gerdate)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.import_data_twidget.setItem(count, 13, item)

            count += 1

    def __get_attribute(self, parcel_feature, layer):

        column_name_landuse = "landuse"

        column_names = {column_name_landuse: ""}

        provider = layer.dataProvider()
        for key, item in column_names.iteritems():
            index = provider.fieldNameIndex(key)
            if index != -1:
                value = parcel_feature.attributes()[index]
                column_names[key] = value
        landuse = column_names[column_name_landuse]
        # landuse = None
        #
        # count = self.session.query(ClLanduseType).filter(ClLanduseType.code == column_names[column_name_landuse]).count()
        # if count == 1:
        #     landuse = self.session.query(ClLanduseType).filter(ClLanduseType.code == column_names[column_name_landuse]).one()
        #
        return landuse

    @pyqtSlot()
    def on_import_data_button_clicked(self):

        file_path = self.load_shp_edit.text()
        self.__read_shp_file(file_path)

    def __validate_import_data(self, landuse, register, middlename, ovog, ner, heid, gaid, zovshbaig, shovshshiid, zovshdate):

        is_valid = True
        error_message = u''

        if self.__is_number(heid):
            heid = int(heid)
            if heid not in [1, 2, 3, 4, 5]:
                is_valid = False
                message = u'Хуулийн этгээдийн төрөл буруу'
                error_message = error_message + "\n" + message
        else:
            is_valid = False
            message = u'Хуулийн этгээдийн төрөл буруу'
            error_message = error_message + "\n" + message

        if self.__is_number(gaid):
            gaid = int(gaid)
            if gaid not in [1, 2, 3]:
                is_valid = False
                message = u'Эрхийн төрөл буруу'
                error_message = error_message + "\n" + message
        else:
            is_valid = False
            message = u'Эрхийн төрөл буруу'
            error_message = error_message + "\n" + message

        if self.__is_number(landuse):
            landuse = int(landuse)
            count = self.session.query(ClLanduseType).\
                filter(ClLanduseType.code == landuse).\
                filter(ClLanduseType.parent_code == None).count()
            if count == 0:
                is_valid = False
                message = u'Зориулалт буруу байна'
                error_message = error_message + "\n" + message
        else:
            is_valid = False
            message = u'Зориулалт буруу байна'
            error_message = error_message + "\n" + message

        if self.__is_number(zovshbaig):
            zovshbaig = int(zovshbaig)
            count = self.session.query(ClDecisionLevel).filter(ClDecisionLevel.code == zovshbaig).count()
            if count == 0:
                is_valid = False
                message = u'Захирамжийн түвшин буруу байна'
                error_message = error_message + "\n" + message
        else:
            is_valid = False
            message = u'Захирамжийн түвшин буруу байна'
            error_message = error_message + "\n" + message

        if shovshshiid is None or shovshshiid == '':
            is_valid = False
            message = u'Захирамжийн дугаар оруулаагүй байна'
            error_message = error_message + "\n" + message

        if zovshdate is None or zovshdate == '':
            is_valid = False
            message = u'Захирамжийн огноо оруулаагүй байна'
            error_message = error_message + "\n" + message

        return is_valid

    def __is_number(self, s):

        try:
            float(s)  # for int, long and float
        except ValueError:
            try:
                complex(s)  # for complex
            except ValueError:
                return False

        return True

