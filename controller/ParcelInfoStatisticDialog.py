# -*- encoding: utf-8 -*-
__author__ = 'B.Ankhbold'

from PyQt4.QtXml import *
from geoalchemy2.elements import WKTElement
from PyQt4.QtXml import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.core import *
from qgis.gui import *
from sqlalchemy import exc, or_
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, or_, extract
from datetime import date, datetime, timedelta
from ..view.Ui_ParcelInfoStatisticDialog import *
from inspect import currentframe
from ..utils.FileUtils import FileUtils
from ..utils.LayerUtils import LayerUtils
from ..model.SetRole import *
from ..model.UbGisSubject import *
from ..model.DatabaseHelper import *
from ..model import Constants
from .qt_classes.DoubleSpinBoxDelegate import *
import os
import locale
from collections import defaultdict
import collections
from xlsxwriter.utility import xl_rowcol_to_cell, xl_col_to_name
import xlsxwriter


class ParcelInfoStatisticDialog(QDialog, Ui_ParcelInfoStatisticDialog, DatabaseHelper):
    def __init__(self, plugin, parent=None):

        super(ParcelInfoStatisticDialog, self).__init__(parent)
        DatabaseHelper.__init__(self)

        self.setupUi(self)
        self.time_counter = None
        self.setWindowTitle(self.tr("Parcel info statistic"))
        self.close_button.clicked.connect(self.reject)
        self.session = SessionHandler().session_instance()
        self.plugin = plugin

        self.finish_date.setDate(QDate.currentDate())
        self.__setup_table_widget()
        self.__setup_cbox()

    def __setup_cbox(self):

        set_roles = self.session.query(SetRole).filter(SetRole.restriction_au_level1 == '011').\
            filter(SetRole.is_active == True).order_by(SetRole.user_name.asc()).all()

        self.user_name_cbox.addItem("*", -1)
        for value in set_roles:
            self.user_name_cbox.addItem(value.user_name + '/' + value.first_name + ' ' + value.surname, value.user_name)

    def __setup_table_widget(self):

        self.result_twidget.setAlternatingRowColors(True)
        self.result_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_twidget.setSelectionMode(QTableWidget.SingleSelection)
        self.result_twidget.setSortingEnabled(True)

        self.result_user_twidget.setAlternatingRowColors(True)
        self.result_user_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_user_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_user_twidget.setSelectionMode(QTableWidget.SingleSelection)
        self.result_user_twidget.setSortingEnabled(True)

    @pyqtSlot(int)
    def on_finish_date_checkbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.finish_date.setEnabled(True)
        else:
            self.finish_date.setEnabled(False)

    @pyqtSlot()
    def on_find_button_clicked(self):

        if self.tabWidget.currentWidget() == self.ubgis_stat_tab:
            self.__ubgis_static()
        elif self.tabWidget.currentWidget() == self.ubgis_finish_tab:
            self.__ubgis_finish_static()
        else:
            return

    def __ubgis_finish_static(self):

        self.result_user_twidget.setRowCount(0)

        finish_parcels = self.session.query(func.count(UbGisSubject.finish_user).label("count"), UbGisSubject.finish_user). \
            filter(UbGisSubject.is_finish == True). \
            filter(UbGisSubject.finish_user != None). \
            group_by(UbGisSubject.finish_user)
        filter_is_set = False
        if self.user_name_cbox.currentIndex() != -1:
            if not self.user_name_cbox.itemData(self.user_name_cbox.currentIndex()) == -1:
                filter_is_set = True
                user_name = self.user_name_cbox.itemData(self.user_name_cbox.currentIndex())

                finish_parcels = finish_parcels.filter(UbGisSubject.finish_user == user_name)

        if self.finish_date_checkbox.isChecked():
            filter_is_set = True
            qt_date = self.finish_date.date().toString(Constants.DATABASE_DATE_FORMAT)
            python_date = datetime.strptime(str(qt_date), Constants.PYTHON_DATE_FORMAT)

            finish_parcels = finish_parcels.filter(UbGisSubject.finish_date >= python_date)

        row = 0
        for value in finish_parcels:
            set_role_count = self.session.query(SetRole). \
                filter(SetRole.user_name == value.finish_user). \
                filter(SetRole.is_active == True).count()

            self.result_user_twidget.insertRow(row)

            item = QTableWidgetItem()
            item.setText(value.finish_user)
            item.setData(Qt.UserRole, value.finish_user)
            self.result_user_twidget.setItem(row, 0, item)

            if set_role_count > 0:
                set_role = self.session.query(SetRole). \
                    filter(SetRole.user_name == value.finish_user). \
                    filter(SetRole.is_active == True).first()
                item = QTableWidgetItem()
                item.setText(set_role.surname)
                item.setData(Qt.UserRole, set_role.surname)
                self.result_user_twidget.setItem(row, 1, item)

                item = QTableWidgetItem()
                item.setText(set_role.first_name)
                item.setData(Qt.UserRole, set_role.first_name)
                self.result_user_twidget.setItem(row, 2, item)

            item = QTableWidgetItem()
            item.setText(str(value.count))
            item.setData(Qt.UserRole, value.count)
            self.result_user_twidget.setItem(row, 3, item)

            row = + 1

        self.result_user_twidget.resizeColumnsToContents()

    def __ubgis_static(self):

        self.result_twidget.setRowCount(0)
        sql = "select * from data_ub.view_ub_statistic_all  "

        result = self.session.execute(sql)
        row = 0
        for item_row in result:
            self.result_twidget.insertRow(row)

            item = QTableWidgetItem()
            item.setText(unicode(item_row[1]))
            item.setData(Qt.UserRole, item_row[1])
            self.result_twidget.setItem(row, 0, item)

            item = QTableWidgetItem()
            item.setText(unicode(item_row[3]))
            item.setData(Qt.UserRole, item_row[3])
            self.result_twidget.setItem(row, 1, item)

            item = QTableWidgetItem()
            item.setText(str(item_row[4]) if item_row[4] else '0')
            item.setData(Qt.UserRole, item_row[4])
            self.result_twidget.setItem(row, 2, item)

            item = QTableWidgetItem()
            item.setText(str(item_row[8]) if item_row[8] else '0')
            item.setData(Qt.UserRole, item_row[8])
            self.result_twidget.setItem(row, 3, item)

            item = QTableWidgetItem()
            item.setText(str(item_row[6]) if item_row[6] else '0')
            item.setData(Qt.UserRole, item_row[6])
            self.result_twidget.setItem(row, 4, item)

            item = QTableWidgetItem()
            item.setText(str(item_row[5]) if item_row[5] else '0')
            item.setData(Qt.UserRole, item_row[5])
            self.result_twidget.setItem(row, 5, item)

            item = QTableWidgetItem()
            item.setText(str(item_row[7]) if item_row[7] else '0')
            item.setData(Qt.UserRole, item_row[7])
            self.result_twidget.setItem(row, 6, item)

            row = + 1

        self.result_twidget.resizeColumnsToContents()

    @pyqtSlot()
    def on_print_button_clicked(self):

        if self.tabWidget.currentWidget() == self.ubgis_stat_tab:
            self.__ubgis_static_print()
        elif self.tabWidget.currentWidget() == self.ubgis_finish_tab:
            self.__ubgis_finish_static_print()
        else:
            return

    def __ubgis_finish_static_print(self):

        default_path = r'D:/TM_LM2/reports'

        # path = os.path.join(os.path.dirname(__file__), "../view/map/report_temp/")
        workbook = xlsxwriter.Workbook(default_path + "/" + "finish_parcel_info_statistic.xlsx")
        worksheet = workbook.add_worksheet()

        worksheet.set_row(3, 20)
        # worksheet.set_landscape()
        # worksheet.set_paper(9)
        worksheet.set_margins(left=0.3, right=0.3)

        format_header = workbook.add_format()
        # format_header.set_text_wrap()
        format_header.set_align('center')
        format_header.set_align('vcenter')
        format_header.set_font_name('Times New Roman')
        format_header.set_font_size(14)
        format_header.set_bold()

        format_normal = workbook.add_format()
        # format_normal.set_text_wrap()
        # format_normal.set_border(1)
        format_normal.set_font_name('Times New Roman')
        format_normal.set_font_size(12)
        # format_normal.set_bold()

        worksheet.merge_range('B2:L2', u'Хэрэглэгчийн Нэгж талбарыг баталгаажуулж үндсэн мэдээллийн санд оруулж буй тайлан', format_header)

        worksheet.write(3, 0, u'№', format_normal)
        worksheet.write(3, 1, u'Хэрэглэгчийн нэр', format_normal)
        worksheet.write(3, 2, u'Овог', format_normal)
        worksheet.write(3, 3, u'Нэг', format_normal)
        worksheet.write(3, 4, u'Тоо', format_normal)

        row_count = range(self.result_user_twidget.rowCount())

        x_row = 4
        for row in row_count:
            worksheet.write(x_row, 0, row + 1, format_normal)
            worksheet.write(x_row, 1, self.result_user_twidget.item(row, 0).text(), format_normal)
            worksheet.write(x_row, 2, self.result_user_twidget.item(row, 1).text(), format_normal)
            worksheet.write(x_row, 3, self.result_user_twidget.item(row, 2).text(), format_normal)
            worksheet.write(x_row, 4, self.result_user_twidget.item(row, 3).text(), format_normal)

            x_row += 1

        # try:
        workbook.close()
        QDesktopServices.openUrl(QUrl.fromLocalFile(default_path + "/" + "finish_parcel_info_statistic.xlsx"))
        # except IOError, e:
        #     PluginUtils.show_error(self, self.tr("Out error"), self.tr("This file is already opened. Please close re-run"))

    def __ubgis_static_print(self):

        default_path = r'D:/TM_LM2/reports'

        # path = os.path.join(os.path.dirname(__file__), "../view/map/report_temp/")
        workbook = xlsxwriter.Workbook(default_path + "/" + "parcel_info_statistic.xlsx")
        worksheet = workbook.add_worksheet()

        worksheet.set_row(3, 20)
        # worksheet.set_landscape()
        # worksheet.set_paper(9)
        worksheet.set_margins(left=0.3, right=0.3)

        format_header = workbook.add_format()
        format_header.set_text_wrap()
        format_header.set_align('center')
        format_header.set_align('vcenter')
        format_header.set_font_name('Times New Roman')
        format_header.set_font_size(14)
        format_header.set_bold()

        format_normal = workbook.add_format()
        format_normal.set_text_wrap()
        format_normal.set_border(1)
        format_normal.set_font_name('Times New Roman')
        format_normal.set_font_size(12)
        # format_normal.set_bold()

        worksheet.merge_range('D2:L2', u'Мэдээллийн сангийн өгөгдөл засварлаж буй тайлан', format_header)

        row_count = range(self.result_twidget.rowCount())

        x_row = 5
        for row in row_count:
            worksheet.write(x_row, 0, row + 1, format_normal)
            worksheet.write(x_row, 1, self.result_twidget.item(row, 0).text(), format_normal)
            worksheet.write(x_row, 2, self.result_twidget.item(row, 1).text(), format_normal)
            worksheet.write(x_row, 3, self.result_twidget.item(row, 2).text(), format_normal)
            worksheet.write(x_row, 4, self.result_twidget.item(row, 3).text(), format_normal)
            worksheet.write(x_row, 5, self.result_twidget.item(row, 4).text(), format_normal)
            worksheet.write(x_row, 6, self.result_twidget.item(row, 5).text(), format_normal)
            worksheet.write(x_row, 7, self.result_twidget.item(row, 6).text(), format_normal)

            x_row += 1

        # try:
        workbook.close()
        QDesktopServices.openUrl(QUrl.fromLocalFile(default_path + "/" + "parcel_info_statistic.xlsx"))
        # except IOError, e:
        #     PluginUtils.show_error(self, self.tr("Out error"), self.tr("This file is already opened. Please close re-run"))
