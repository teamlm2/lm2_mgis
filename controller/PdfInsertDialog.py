# coding=utf8
__author__ = 'ankhbold'

import os
from os import walk
import shutil
import zlib
from PIL import Image
from geoalchemy2.elements import WKTElement
from sqlalchemy.exc import SQLAlchemyError
from qgis.core import *
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import func, or_, and_, desc
from sqlalchemy.sql.expression import cast
from sqlalchemy import func
from xlrd import *
from decimal import Decimal
from ..view.Ui_PdfInsertDialog import *
from ..utils.PluginUtils import *
from ..utils.DatabaseUtils import DatabaseUtils
from ..model.Enumerations import *
from ..model.ClDocumentRole import *
from ..model.CtContractApplicationRole import *
from ..model.CtContractDocument import *
from ..model.SetContractDocumentRole import *
from ..model.CtRecordApplicationRole import *
from ..model.CtRecordDocument import *
from ..model.BsPerson import *
from ..model.ClPersonRole import *
from ..utils.FilePath import *
from ..model.CtDecision import *
from ..model.CtContract import *
from ..model.CtOwnershipRecord import *
from ..model.CtDecisionDocument import *
from ..model.DatabaseHelper import *
from ..utils.FileUtils import FileUtils
import codecs

class PdfInsertDialog(QDialog, Ui_PdfInsertDialog):

    def __init__(self, parent=None):

        super(PdfInsertDialog,  self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle(self.tr("Pdf file insert Dialog"))
        self.close_button.clicked.connect(self.reject)
        self.session = SessionHandler().session_instance()
        self.progressBar.setMinimum(1)
        self.progressBar.setValue(0)

        self.application = None
        self.contract = None
        self.record = None
        self.right_type = None
        self.app_type = None
        self.app_no = None
        self.zovshdate = None
        self.import_parcel_ids = []

        self.__setup_validators()
        self.import_data_twidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.import_data_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.import_data_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.import_data_twidget.setSortingEnabled(True)

    def __setup_validators(self):

        self.capital_asci_letter_validator = QRegExpValidator(QRegExp("[A-Z]"), None)
        self.lower_case_asci_letter_validator = QRegExpValidator(QRegExp("[a-z]"), None)

        self.email_validator = QRegExpValidator(QRegExp("[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,4}"), None)

        self.www_validator = QRegExpValidator(QRegExp("www\\.[a-z0-9._%+-]+\\.[a-z]{2,4}"), None)
        self.numbers_validator = QRegExpValidator(QRegExp("[1-9][0-9]+( *,*[1-9][0-9]+)*"), None)
        self.int_validator = QRegExpValidator(QRegExp("[0-9]+"), None)

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

            # selected_file = file_dialog.selectedFiles()[0]
            #
            # file_path = QFileInfo(selected_file).path()
            self.dir_path_edit.setText(selected_directory)

            for root, dirs, files in os.walk(selected_directory):
                count = 0
                for file in files:
                    if file.endswith('.png'):
                        # print root
                        # print dirs
                        # print file
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
    def on_delete_data_button_clicked(self):

        for parcel_id in self.import_parcel_ids:
            self.session.query(CaParcel).filter(CaParcel.parcel_id == parcel_id).delete()


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
            # print landuse

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

            if self.__is_number(zovshdate)        :
                zovshdate = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(zovshdate) - 2)
                zovshdate = str(datetime.date(zovshdate))

            if self.__is_number(duusdate)        :
                duusdate = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(duusdate) - 2)
                duusdate = str(datetime.date(duusdate))

            is_valid = self.__validate_import_data(parcel_id, landuse, register, middlename, ovog, ner, heid, gaid, zovshbaig, shovshshiid, zovshdate, duusdate)[0]
            error_message = self.__validate_import_data(parcel_id, landuse, register, middlename, ovog, ner, heid, gaid, zovshbaig, shovshshiid, zovshdate, duusdate)[1]
            print is_valid
            print error_message

            item = QTableWidgetItem(str(parcel_id))
            item.setData(Qt.UserRole, parcel_id)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            if not is_valid:
                item.setBackground(Qt.yellow)
            self.import_data_twidget.setItem(count, 0, item)

            item = QTableWidgetItem(unicode(landuse))
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

            if is_valid:
                zovshdate = self.__convert_zovshdate_duusdate(zovshdate, duusdate)[0]

                self.zovshdate = PluginUtils.convert_python_date_to_qt(zovshdate)
                duusdate = self.__convert_zovshdate_duusdate(zovshdate, duusdate)[1]

                duration = 0
                if isinstance(zovshdate, datetime) and isinstance(duusdate, datetime):
                    duration = duusdate.year - zovshdate.year
                column_name = 'pid'
                layer = self.__get_shp_layer()
                geometry = self.__get_geometry_by_parcel_id(column_name, str(int(parcel_id)), layer)

                self.__add_import_data_database(geometry, landuse, register, middlename, ovog, ner, heid, gaid, zovshbaig,
                                                shovshshiid, zovshdate, duusdate, duration, gerchid)

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

        # file_path = self.load_shp_edit.text()
        # self.__read_shp_file(file_path)
        self.session.commit()

    def __add_import_data_database(self, geometry, landuse, register, middlename, ovog, ner, heid, gaid, zovshbaig, shovshshiid,
                               zovshdate, duusdate, duration, gerchid):
        heid = int(heid)
        gaid = int(gaid)
        landuse = int(landuse)
        zovshbaig = int(zovshbaig)
        # zovshdate = datetime.strptime(str(zovshdate), '%m.%d.%Y')
        # duusdate = datetime.strptime(str(duusdate), '%m.%d.%Y')

        self.__save_person(register, middlename, ovog, ner, heid)
        self.__save_parcel(geometry, landuse, gaid, zovshdate, duusdate, duration)
        self.__save_applicant(register)
        self.__save_status(zovshdate)
        self.__save_decision(zovshbaig, shovshshiid, zovshdate)
        self.__save_contract_owner(gaid, zovshdate, duusdate, gerchid)

        print self.import_parcel_ids
        print 'niit orson negj talbar: ' + str(len(self.import_parcel_ids))

    def __save_person(self, register, middlename, ovog, ner, heid):

        person_id = register

        if self.__is_number(person_id):
            person_id = str(int(person_id))
        person_id = unicode(person_id).upper()

        person_type = None
        if int(heid) == 1:
            person_type = 10
        elif int(heid) == 2:
            person_type = 30
        elif int(heid) == 3:
            person_type = 40
        elif int(heid) == 4:
            person_type = 50
        elif int(heid) == 5 or str(heid) == 5:
            person_type = 60
        # self.create_savepoint()
        # try:
        person_count = self.session.query(BsPerson).filter(BsPerson.person_register == person_id).count()
        if person_count > 0:
            bs_person = self.session.query(BsPerson).filter(BsPerson.person_register == person_id).first()
        else:
            if len(person_id) < 11:
                bs_person = BsPerson()
                bs_person.person_register = person_id
                bs_person.type = person_type
                if person_type == 10 or person_type == 20 or person_type == 50:
                    bs_person.name = ner
                    bs_person.first_name = ovog
                    bs_person.middle_name = middlename
                else:
                    bs_person.name = ner
                    bs_person.contact_surname = middlename
                    bs_person.contact_first_name = ovog

                # bs_person.date_of_birth = DatabaseUtils.convert_date(self.date_of_birth_date.date())

                if person_count == 0:
                    self.session.add(bs_person)
        # except SQLAlchemyError, e:
        #     self.rollback_to_savepoint()
        #     raise LM2Exception(self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
        # self.session.flush()

    def __save_parcel(self, geometry, landuse, gaid, decision_date, duusdate, duration):

        au_level1 = DatabaseUtils.working_l1_code()
        au_level2 = DatabaseUtils.working_l2_code()

        parcel = CaParcel()

        parcel.landuse = landuse
        parcel.geometry = geometry

        valid_from = PluginUtils.convert_qt_date_to_python(QDate.currentDate())
        parcel.valid_from = valid_from

        self.session.add(parcel)
        self.session.flush()
        self.import_parcel_ids.append(parcel.parcel_id)

        parcel_id = parcel.parcel_id
        app_time = decision_date
        status_date = decision_date

        right_type = self.__get_right_type(gaid)[0]
        self.right_type = right_type
        app_type = self.__get_right_type(gaid)[1]
        self.app_type = app_type
        app_no = self.__generate_application_number()
        self.app_no = app_no

        self.application = CtApplication()

        application_status = CtApplicationStatus()
        application_status.ct_application = self.application
        status = self.session.query(ClApplicationStatus).filter_by(code='1').one()
        application_status.status = 1
        application_status.status_ref = status
        application_status.status_date = status_date
        self.application.app_no = app_no
        self.application.app_type = app_type
        self.application.requested_landuse = landuse
        self.application.approved_landuse = landuse
        self.application.app_timestamp = app_time
        self.application.requested_duration = duration
        self.application.approved_duration = duration
        self.application.right_type = right_type
        self.application.created_by = DatabaseUtils.current_sd_user().user_id
        # self.application.created_at = app_time
        # self.application.updated_at = app_time
        self.application.au1 = au_level1
        self.application.au2 = au_level2
        self.application.remarks = ''

        # current_user = QSettings().value(SettingsConstants.USER)
        # officer = self.session.query(SetRole).filter_by(user_name=current_user).filter(SetRole.is_active == True).one()
        application_status.next_officer_in_charge = DatabaseUtils.current_sd_user().user_id
        application_status.next_officer_in_charge_ref = DatabaseUtils.current_sd_user()
        application_status.officer_in_charge_ref = DatabaseUtils.current_sd_user()
        application_status.officer_in_charge = DatabaseUtils.current_sd_user().user_id
        self.application.statuses.append(application_status)

        self.application.parcel = parcel_id
        self.session.add(self.application)

    def __save_applicant(self, person_id):

        if self.__is_number(person_id):
            person_id = str(int(person_id))
        person_id = unicode(person_id).upper()

        person = self.session.query(BsPerson).filter(BsPerson.person_register == person_id).\
            order_by(BsPerson.parent_id.asc()).first()
        role_ref = self.session.query(ClPersonRole).filter_by(
            code=Constants.APPLICANT_ROLE_CODE).one()

        # self.create_savepoint()
        # try:
        app_person_role = CtApplicationPersonRole()
        app_person_role.application = self.application.app_id
        app_person_role.share = Decimal(1.0)
        app_person_role.role = Constants.APPLICANT_ROLE_CODE
        app_person_role.role_ref = role_ref
        app_person_role.person = person.person_id
        app_person_role.person_ref = person
        app_person_role.main_applicant = True

        self.application.stakeholders.append(app_person_role)

    def __save_status(self, zovshdate):

        status_date = zovshdate

        statuses = self.session.query(ClApplicationStatus).\
            filter(ClApplicationStatus.code != 1). \
            filter(ClApplicationStatus.code != 8). \
            filter(ClApplicationStatus.code < 10).order_by(ClApplicationStatus.code.asc()).all()

        # self.create_savepoint()
        # try:
        for status in statuses:
            application_status = CtApplicationStatus()
            application_status.ct_application = self.application
            application_status.status = status.code
            application_status.status_ref = status
            application_status.status_date = status_date

            # current_user = QSettings().value(SettingsConstants.USER)
            # officer = self.session.query(SetRole).filter_by(user_name=current_user).filter(SetRole.is_active == True).one()
            application_status.next_officer_in_charge = DatabaseUtils.current_sd_user().user_id
            application_status.next_officer_in_charge_ref = DatabaseUtils.current_sd_user()
            application_status.officer_in_charge_ref = DatabaseUtils.current_sd_user()
            application_status.officer_in_charge = DatabaseUtils.current_sd_user().user_id
            self.application.statuses.append(application_status)
        # except SQLAlchemyError, e:
        #     self.rollback_to_savepoint()
        #     raise LM2Exception(self.tr("File Error"),
        #                        self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

    def __save_decision(self, zovshbaig, shovshshiid, zovshdate):

        decision_level = zovshbaig

        au_level2 = DatabaseUtils.current_working_soum_schema()
        year_filter = str(self.zovshdate.toString("yyyy"))
        if self.__is_number(shovshshiid):
            shovshshiid = str(int(shovshshiid))
        shovshshiid = codecs.encode(shovshshiid, 'utf-8')
        f = codecs.decode(shovshshiid, 'utf-8')
        shovshshiid = f.replace('A', '')
        decision_no = au_level2 + '-' + shovshshiid + '/' + year_filter

        decision_count = self.session.query(CtDecision).filter(CtDecision.decision_no == decision_no). \
            filter(CtDecision.decision_level == decision_level).count()
        # self.create_savepoint()
        # try:

        if decision_count == 1:
            self.decision = self.session.query(CtDecision).filter(CtDecision.decision_no == decision_no). \
                filter(CtDecision.decision_level == decision_level).one()

        else:
            self.decision = CtDecision()

            self.decision.decision_date = zovshdate
            self.decision.decision_no = decision_no
            self.decision.decision_level = decision_level
            self.decision.imported_by = DatabaseUtils.current_sd_user().user_id
            self.decision.au2 = DatabaseUtils.working_l2_code()
            self.session.add(self.decision)
            self.session.flush()

        decision_app = CtDecisionApplication()
        decision_app.decision = self.decision.decision_id
        decision_app.decision_result = 10
        decision_app.application = self.application.app_id
        self.decision.results.append(decision_app)
        # except SQLAlchemyError, e:
        #     self.rollback_to_savepoint()
        #     raise LM2Exception(self.tr("File Error"),
        #                        self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            # self.session.flush()

    def __save_contract_owner(self, gaid, zovshdate, duusdate, gerchid):

        cert_no = None
        if self.__is_number(gerchid):
            cert_no = int(gerchid)

        right_type = self.__get_right_type(gaid)[0]
        if right_type == 1 or right_type == 2:
            contract_no = self.__generate_contract_number()
            # self.create_savepoint()
            # try:

            self.contract = CtContract()
            self.contract.type = 1
            self.contract.contract_no = contract_no
            self.contract.contract_begin = zovshdate
            self.contract.contract_date = zovshdate
            self.contract.contract_end = duusdate
            self.contract.certificate_no = cert_no
            self.contract.status = Constants.CONTRACT_STATUS_ACTIVE
            self.contract.au2 = DatabaseUtils.working_l2_code()

            self.session.add(self.contract)

            app_type = None
            obj_type = 'contract\Contract'
            qt_date = self.zovshdate
            # contract_number_filter = "%-{0}/%".format(str(qt_date.toString("yyyy")))
            year = qt_date.toString("yyyy")
            PluginUtils.generate_auto_app_no(str(year), app_type, DatabaseUtils.working_l2_code(), obj_type, self.session)

            contract_app = CtContractApplicationRole()
            contract_app.application_ref = self.application
            contract_app.application = self.application.app_id
            contract_app.contract = self.contract.contract_id
            contract_app.contract_ref = self.contract

            contract_app.role = Constants.APPLICATION_ROLE_CREATES
            self.contract.application_roles.append(contract_app)
            # except SQLAlchemyError, e:
            #     self.rollback_to_savepoint()
            #     raise LM2Exception(self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
        else:
            record_no = self.__generate_record_number()
            # self.create_savepoint()
            # try:
            self.record = CtOwnershipRecord()
            self.record.record_no = record_no
            self.record.record_date = zovshdate
            self.record.record_begin = zovshdate
            self.record.certificate_no = cert_no
            self.record.status = Constants.RECORD_STATUS_ACTIVE
            self.record.au2 = DatabaseUtils.working_l2_code()

            self.session.add(self.record)

            app_type = None
            obj_type = 'record\OwnershipRecord'
            qt_date = self.zovshdate
            # contract_number_filter = "%-{0}/%".format(str(qt_date.toString("yyyy")))
            year = qt_date.toString("yyyy")
            PluginUtils.generate_auto_app_no(str(year), app_type, DatabaseUtils.working_l2_code(), obj_type, self.session)

            record_app = CtRecordApplicationRole()
            record_app.application_ref = self.application
            record_app.application = self.application.app_id
            record_app.record = self.record.record_id

            record_app.role = Constants.APPLICATION_ROLE_CREATES
            self.record.application_roles.append(record_app)
            # except SQLAlchemyError, e:
            #     self.rollback_to_savepoint()
            #     raise LM2Exception(self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

    def __generate_record_number(self):

        soum = DatabaseUtils.current_working_soum_schema()
        soum_filter = soum + "-%"
        qt_date = self.zovshdate
        # try:
        record_number_filter = "%-{0}/%".format(str(qt_date.toString("yyyy")))

        # return
        count = self.session.query(CtOwnershipRecord) \
                    .filter(CtOwnershipRecord.record_no.like("%-%")) \
                    .filter(CtOwnershipRecord.record_no.like(soum + "-%")) \
                    .filter(CtOwnershipRecord.record_no.like(record_number_filter))  \
                    .filter(CtOwnershipRecord.au2 == soum) \
                    .order_by(func.substr(CtOwnershipRecord.record_no, 10, 16).desc()).count()
        if count == 0:
            cu_max_number = "00001"

        else:
            sql = "select split_part(record_no, '/', 2)::int, record_no from data_soums_union.ct_ownership_record " \
                  "where record_no like " + "'" + soum_filter + "'" + " and record_no like " + "'" + record_number_filter + "'" + " " \
                                 "order by split_part(record_no, '/', 2)::int desc limit 1; "
            result = self.session.execute(sql)
            for item_row in result:
                cu_max_number = item_row[0]
            # cu_max_number = self.session.query(CtOwnershipRecord.record_no)\
            #                     .filter(CtOwnershipRecord.record_no.like("%-%")) \
            #                     .filter(CtOwnershipRecord.record_no.like(soum + "-%")) \
            #                     .filter(CtOwnershipRecord.record_no.like(record_number_filter)) \
            #                     .filter(CtOwnershipRecord.au2 == soum) \
            #     .order_by(func.substr(CtOwnershipRecord.record_no, 10, 16).desc()).first()
            #
            # cu_max_number = cu_max_number[0]
            # minus_split_number = cu_max_number.split("-")
            # slash_split_number = minus_split_number[1].split("/")
            # cu_max_number = int(slash_split_number[1]) + 1
                cu_max_number = int(cu_max_number) + 1

        year = qt_date.toString("yyyy")
        number = soum + "-" + year + "/" + str(cu_max_number).zfill(5)

        # except SQLAlchemyError, e:
        #     PluginUtils.show_error(self, self.tr("Database Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

        return number

    def __generate_contract_number(self):

        soum = DatabaseUtils.current_working_soum_schema()
        soum_filter = soum + "-%"
        qt_date = self.zovshdate
        # try:
        contract_number_filter = "%-{0}/%".format(str(qt_date.toString("yyyy")))

        count = self.session.query(CtContract) \
            .filter(CtContract.contract_no.like("%-%")) \
            .filter(CtContract.contract_no.like(soum+"-%")) \
            .filter(CtContract.contract_no.like(contract_number_filter)) \
            .filter(CtContract.au2 == soum) \
            .order_by(func.substr(CtContract.contract_no, 10, 16).desc()).count()
        if count == 0:
            cu_max_number = "00001"
        else:
            sql = "select split_part(contract_no, '/', 2)::int, contract_no from data_soums_union.ct_contract " \
                    "where contract_no like " + "'" + soum_filter + "'" + " and contract_no like " + "'" + contract_number_filter + "'" + " " \
                    "order by split_part(contract_no, '/', 2)::int desc limit 1; "
            result = self.session.execute(sql)
            for item_row in result:
                cu_max_number = item_row[0]
            # cu_max_number = self.session.query(CtContract.contract_no) \
            #     .filter(CtContract.contract_no.like("%-%")) \
            #     .filter(CtContract.contract_no.like(soum + "-%")) \
            #     .filter(CtContract.contract_no.like(contract_number_filter)) \
            #     .filter(CtContract.au2 == soum) \
            #     .order_by(func.substr(CtContract.contract_no, 10, 16).desc()).first()
            #     cu_max_number = cu_max_number

                # minus_split_number = cu_max_number.split("-")
                # slash_split_number = minus_split_number[1].split("/")
                # cu_max_number = int(slash_split_number[1]) + 1
                cu_max_number = int(cu_max_number) + 1
        soum = DatabaseUtils.current_working_soum_schema()
        year = qt_date.toString("yyyy")
        number = soum + "-" + year + "/" + str(cu_max_number).zfill(5)

        # except SQLAlchemyError, e:
        #     raise LM2Exception(self.tr("Database Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

        return number

    def __generate_application_number(self):

        au_level2 = DatabaseUtils.current_working_soum_schema()
        # right_type = self.rigth_type_cbox.itemData(self.rigth_type_cbox.currentIndex())

        # app_type = self.application_type_cbox.itemData(self.application_type_cbox.currentIndex())
        app_type = self.app_type
        # app_type = 1
        # if right_type == 1:
        #     app_type = 6
        # elif right_type == 2:
        #     app_type == 5
        # elif right_type == 3:
        #     app_type == 1

        app_no_part_0 = au_level2
        app_no_part_1 = (str(app_type).zfill(2))
        app_type_filter = "%-" + str(app_type).zfill(2) + "-%"
        soum_filter = str(au_level2) + "-%"
        # qt_date = self.decision_date.date()
        qt_date = self.zovshdate
        year_filter = "%-" + str(qt_date.toString("yy"))

        # try:

        count = self.session.query(CtApplication) \
                    .filter(CtApplication.app_no.like("%-%"))\
                    .filter(CtApplication.app_no.like(app_type_filter))  \
                    .filter(CtApplication.app_no.like(soum_filter)) \
                    .filter(CtApplication.app_no.like(year_filter)) \
                .order_by((func.substr(CtApplication.app_no, 10, 14)).desc()).count()

        # count = self.session.query(CtApplication) \
        #     .filter(CtApplication.app_no.like("%-%")) \
        #     .filter(CtApplication.app_no.like(app_type_filter)) \
        #     .filter(CtApplication.app_no.like(soum_filter)) \
        #     .filter(CtApplication.app_no.like(year_filter)) \
        #     .order_by((CtApplication.app_no).split('-')[2].desc()).first()

        # except SQLAlchemyError, e:
        #     PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
        #     return

        if count > 0:
            # try:
            # max_number_app = self.session.query(CtApplication) \
            #     .filter(CtApplication.app_no.like("%-%")) \
            #     .filter(CtApplication.app_no.like(app_type_filter)) \
            #     .filter(CtApplication.app_no.like(soum_filter)) \
            #     .filter(CtApplication.app_no.like(year_filter)) \
            #     .order_by((CtApplication.app_no).split  ('-')[2].desc()).first()

            sql = "select split_part(app_no, '-', 3)::int, app_no from data_soums_union.ct_application " \
                    "where app_no like " + "'" + soum_filter + "'" + " and app_no like "+ "'" + app_type_filter + "'" +" and app_no like "+ "'" + year_filter + "'" +" " \
                    "order by split_part(app_no, '-', 3)::int desc limit 1; "
            result = self.session.execute(sql)
            for item_row in result:
                max_number_app = item_row[0]
            # max_number_app = self.session.query(CtApplication)\
            #     .filter(CtApplication.app_no.like("%-%"))\
            #     .filter(CtApplication.app_no.like(app_type_filter)) \
            #     .filter(CtApplication.app_no.like(soum_filter)) \
            #     .filter(CtApplication.app_no.like(year_filter)) \
            #     .order_by(int(func.substr(CtApplication.app_no, 10, 14)).desc()).first()
            #     app_no_numbers = max_number_app.app_no.split("-")
                app_no_numbers = max_number_app

                # app_no_part_2 = str(int(app_no_numbers[2]) + 1).zfill(5)
                app_no_part_2 = str(int(app_no_numbers) + 1).zfill(5)
            # except SQLAlchemyError, e:
            #     PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            #     return
        else:
            app_no_part_2 = "00001"

        app_no_part_3 = (qt_date.toString("yy"))
        app_no = app_no_part_0 + '-' + app_no_part_1 + '-' + app_no_part_2 + '-' + app_no_part_3

        return app_no

    def __validate_import_data(self, parcel_id, landuse, register, middlename, ovog, ner, heid, gaid, zovshbaig,
                               shovshshiid, zovshdate, duusdate):

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
            count = self.session.query(ClLanduseType). \
                filter(ClLanduseType.code == landuse).count()
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
        if not self.__validate_zovshdate(zovshdate):
            is_valid = False
            message = u'Захирамжийн огноо алдаатай байна'
            error_message = error_message + "\n" + message

        right_type = self.__get_right_type(gaid)[0]
        if right_type != 3:
            if duusdate is not None:
                if not self.__validate_duusdate(duusdate):
                    is_valid = False
                    message = u'Гэрээний дуусах огноо алдаатай байна'
                    error_message = error_message + "\n" + message
        column_name = 'pid'
        layer = self.__get_shp_layer()
        if self.__is_number(parcel_id):
            parcel_id = int(parcel_id)
            geometry = self.__get_geometry_by_parcel_id(column_name, str(int(parcel_id)), layer)
            if geometry is None:
                is_valid = False
                message = u'Геометр утга олдсонгүй'
                error_message = error_message + "\n" + message
            if geometry is not None:
                ca_parcel_overlaps_count = self.session.query(CaParcelTbl). \
                    filter(or_(CaParcelTbl.valid_till == 'infinity', CaParcelTbl.valid_till == None)). \
                    filter(geometry.ST_Overlaps(CaParcelTbl.geometry)).count()
                if ca_parcel_overlaps_count > 0:
                    is_valid = False
                    message = u'Кадастрын нэгж талбар давхардаж байна'
                    error_message = error_message + "\n" + message

                ca_parcel_overlaps_count = self.session.query(CaParcelTbl). \
                    filter(or_(CaParcelTbl.valid_till == 'infinity', CaParcelTbl.valid_till == None)). \
                    filter(geometry.ST_Covers(CaParcelTbl.geometry)).count()
                if ca_parcel_overlaps_count > 0:
                    is_valid = False
                    message = u'Кадастрын нэгж талбар давхардаж байна'
                    error_message = error_message + "\n" + message
        else:
            is_valid = False
            message = u'Нэгж талбарын дугаар алдаатай'
            error_message = error_message + "\n" + message

        person_id = register

        if self.__is_number(person_id):
            person_id = str(int(person_id))
        person_id = unicode(person_id).upper()

        if len(person_id) > 10:
            is_valid = False
            message = u'Хуулийн этгээдийн регистрийн дугаар алдаатай байна'
            error_message = error_message + "\n" + message

        self.__validate_person(register, middlename, ovog, ner, heid)

        return is_valid, error_message

    def __validate_person(self, register, middlename, ovog, ner, heid):

        is_valid = True
        error_message = u''

        person_type = None

        heid = str(heid)
        if self.__is_number(heid):
            if int(heid) == 1:
                person_type = 10
            elif int(heid) == 2:
                person_type = 30
            elif int(heid) == 3:
                person_type = 40
            elif int(heid) == 4:
                person_type = 50
            elif int(heid) == 5 or str(heid) == 5:
                person_type = 60

        text = register
        if person_type:
            if person_type == PersonType.legally_capable_mongolian or person_type == PersonType.legally_uncapable_mongolian:
                if not self.__validate_private_person_id(text):
                    valid = False
                    street_error = self.tr("Person id error!.")
                    error_message = error_message + "\n \n" + street_error

            elif person_type == PersonType.mongolian_buisness or person_type == PersonType.mongolian_state_org:

                if not self.__validate_entity_id(str(text)):
                    valid = False
                    street_error = self.tr("Company id error!.")
                    error_message = error_message + "\n \n" + street_error

            text = middlename

            # type of Company/state organisation:
            if person_type == PersonType.mongolian_state_org \
                    or person_type == PersonType.mongolian_buisness \
                    or person_type == PersonType.legal_entity_foreign \
                    or person_type == PersonType.foreign_citizen:

                if not self.__validate_company_name(text):
                    valid = False
                    street_error = self.tr("Company contact Middle name error!.")
                    error_message = error_message + "\n \n" + street_error

            # type of private person
            else:
                if not self.__validate_person_name(text, person_type):
                    valid = False
                    street_error = self.tr("Person middle name error!.")
                    error_message = error_message + "\n \n" + street_error

            text = ner

            # type of Company/state organisation:
            if person_type == PersonType.mongolian_state_org \
                    or person_type == PersonType.mongolian_buisness \
                    or person_type == PersonType.legal_entity_foreign \
                    or person_type == PersonType.foreign_citizen:

                if not self.__validate_company_name(text):
                    valid = False
                    street_error = self.tr("Company name error!.")
                    error_message = error_message + "\n \n" + street_error

            # type of private person
            else:
                if not self.__validate_person_name(text, person_type):
                    valid = False
                    street_error = self.tr("Person name error!.")
                    error_message = error_message + "\n \n" + street_error
        else:
            is_valid = False
            message = u'Хуулийн этгээдийн төрөл буруу'
            error_message = error_message + "\n" + message

    def __is_number(self, s):

        try:
            float(s)  # for int, long and float
        except ValueError:
            try:
                complex(s)  # for complex
            except ValueError:
                return False

        return True

    def __validate_person_name(self, text, person_type):

        if person_type == 10 or person_type == 20 or person_type == 50:
            if not text:
                text = ''
            if len(text) <= 0:
                return False

            first_letter = text[0]
            rest = text[1:]
            result_capital = self.capital_asci_letter_validator.regExp().indexIn(rest)
            result_lower = self.lower_case_asci_letter_validator.regExp().indexIn(rest)

            if first_letter not in Constants.CAPITAL_MONGOLIAN:
                # self.error_label.setText(self.tr("The first letter and the letter after of a "
                #                                  "name and the letter after a \"-\"  should be a capital letters."))
                return False

            if len(rest) > 0:

                if result_capital != -1 or result_lower != -1:
                    # self.error_label.setText(self.tr("Only mongolian characters are allowed."))
                    return False

                for i in range(len(rest)):
                    if rest[i] not in Constants.LOWER_CASE_MONGOLIAN and rest[i] != "-":
                        if len(rest) - 1 == i:
                            return True

                        if rest[i - 1] != "-":
                            # self.error_label.setText(
                            #     self.tr("Capital letters are only allowed at the beginning of a name or after a \"-\". "))
                            return False

        return True

    def __validate_company_name(self, text):

        # no validation so far
        if text == "":
            return False

        return True

    def __validate_entity_id(self, text):

        valid = self.int_validator.regExp().exactMatch(text)

        if not valid:
            # self.error_label.setText(self.tr("Company id should be with numbers only."))
            return False
        if len(text) > 7:
            cut = text[:7]
            self.personal_id_edit.setText(cut)

        return True

    def __validate_private_person_id(self, text):

        original_text = text
        first_letters = text[:2]
        rest = text[2:]
        first_large_letters = first_letters.upper()

        reg = QRegExp("[0-9][0-9]+")
        is_valid = True

        if first_large_letters[0:1] not in Constants.CAPITAL_MONGOLIAN \
                and first_large_letters[1:2] not in Constants.CAPITAL_MONGOLIAN:
            # self.error_label.setText(
            #     self.tr("First letters of the person id should be capital letters and in mongolian."))
            is_valid = False

        if len(original_text) > 2:
            if not reg.exactMatch(rest):
                # self.error_label.setText(
                #     self.tr("After the first two capital letters, the person id should contain only numbers."))
                is_valid = False

        if len(original_text) > 10:
            # self.error_label.setText(self.tr("The person id shouldn't be longer than 10 characters."))
            is_valid = False

        return is_valid

    def __validate_zovshdate(self, zovshdate):

        is_zovshdate = True

        if self.__is_number(str(zovshdate)):
            zovshdate = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(zovshdate) - 2)

        try:
            zovshdate = datetime.strptime(str(zovshdate), '%Y.%m.%d')
        except:
            is_zovshdate = False
            # print "zovshdate after: ", 'aldaatai'

        if not is_zovshdate:
            try:
                zovshdate = datetime.strptime(str(zovshdate), '%Y-%m-%d')
                is_zovshdate = True
            except:
                is_zovshdate = False
                # print "zovshdate after: ", 'aldaatai'

        if not is_zovshdate:
            try:
                zovshdate = datetime.strptime(str(zovshdate), '%Y/%m/%d')
                is_zovshdate = True
            except:
                is_zovshdate = False
                # print "zovshdate after: ", 'aldaatai'

        if not is_zovshdate:
            try:
                zovshdate = datetime.strptime(str(zovshdate), '%m/%d/%y')
                is_zovshdate = True
            except:
                is_zovshdate = False
                # print "zovshdate after: ", 'aldaatai'

        return is_zovshdate

    def __validate_duusdate(self, duusdate):

        is_duusate = True

        if self.__is_number(str(duusdate)):
            duusdate = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(duusdate) - 2)

        try:
            duusdate = datetime.strptime(str(duusdate), '%Y.%m.%d')
        except:
            is_duusate = False
            # print "duusdate after: ", 'aldaatai'

        if not is_duusate:
            try:
                duusdate = datetime.strptime(str(duusdate), '%Y-%m-%d')
                is_duusate = True
            except:
                is_duusate = False
                # print "duusdate after: ", 'aldaatai'

        if not is_duusate:
            try:
                duusdate = datetime.strptime(str(duusdate), '%Y/%m/%d')
                is_duusate = True
            except:
                is_duusate = False
                # print "duusdate after: ", 'aldaatai'

        if not is_duusate:
            try:
                duusdate = datetime.strptime(str(duusdate), '%m/%d/%y')
                is_duusate = True
            except:
                is_duusate = False
                # print "duusdate after: ", 'aldaatai'

        return is_duusate

    def __convert_zovshdate_duusdate(self, zovshdate, duusdate):

        is_zovshdate = True

        if self.__is_number(str(zovshdate)):
            zovshdate = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(zovshdate) - 2)

        if zovshdate is not None:
            try:
                zovshdate = datetime.strptime(str(zovshdate), '%Y.%m.%d')
            except:
                is_zovshdate = False
                # print "zovshdate after: ", 'aldaatai'

            if not is_zovshdate:
                try:
                    zovshdate = datetime.strptime(str(zovshdate), '%Y-%m-%d')
                    is_zovshdate = True
                except:
                    is_zovshdate = False
                    # print "zovshdate after: ", 'aldaatai'

            if not is_zovshdate:
                try:
                    zovshdate = datetime.strptime(str(zovshdate), '%Y/%m/%d')
                    is_zovshdate = True
                except:
                    is_zovshdate = False
                    # print "zovshdate after: ", 'aldaatai'

            if not is_zovshdate:
                try:
                    zovshdate = datetime.strptime(str(zovshdate), '%m/%d/%y')
                    is_zovshdate = True
                except:
                    is_zovshdate = False
                    # print "zovshdate after: ", 'aldaatai'

        #############
        is_duusate = True
        if self.__is_number(str(duusdate)):
            duusdate = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(duusdate) - 2)
        if duusdate is not None:
            try:
                duusdate = datetime.strptime(str(duusdate), '%Y.%m.%d')
            except:
                is_duusate = False
                # print "duusdate after: ", 'aldaatai'

            if not is_duusate:
                try:
                    duusdate = datetime.strptime(str(duusdate), '%Y-%m-%d')
                    is_duusate = True
                except:
                    is_duusate = False
                    # print "duusdate after: ", 'aldaatai'

            if not is_duusate:
                try:
                    duusdate = datetime.strptime(str(duusdate), '%Y/%m/%d')
                    is_duusate = True
                except:
                    is_duusate = False
                    # print "duusdate after: ", 'aldaatai'

            if not is_duusate:
                try:
                    duusdate = datetime.strptime(str(duusdate), '%m/%d/%y')
                    is_duusate = True
                except:
                    is_duusate = False
                    # print "duusdate after: ", 'aldaatai'

        return zovshdate, duusdate

    def __get_right_type(self, gaid):

        right_type = 1
        app_type = 1

        type = str(gaid)
        if self.__is_number(type):
            if int(type) == 1:
                right_type = 3
                app_type = 1
            elif int(type) == 2:
                right_type = 2
                app_type = 5
            elif int(type) == 3:
                right_type = 1
                app_type = 6
        # right_type_subject = self.session.query(ClRightType).filter(ClRightType.code == right_type).one()
        return right_type, app_type

    def __get_shp_layer(self):

        file_path = self.load_shp_edit.text()

        parcel_shape_layer = QgsVectorLayer(file_path, "tmp_landuse_parcel_shape", "ogr")

        if not parcel_shape_layer.isValid():
            PluginUtils.show_error(self, self.tr("Error loading layer"), self.tr("The layer is invalid."))
            return

        if parcel_shape_layer.crs().postgisSrid() != 4326:
            PluginUtils.show_error(self, self.tr("Error loading layer"),
                                   self.tr("The crs of the layer has to be 4326."))
            return

        return parcel_shape_layer

    def __get_geometry_by_parcel_id(self, column_name, parcel_id, layer):

        parcel_geometry = None

        expression = column_name + " = \'" + str(parcel_id) + "\'"

        request = QgsFeatureRequest()
        request.setFilterExpression(expression)
        feature_ids = []
        iterator = layer.getFeatures(request)

        for feature in iterator:
            feature_ids.append(feature.id())
            parcel_geometry = WKTElement(feature.geometry().exportToWkt(), srid=4326)

        return parcel_geometry


