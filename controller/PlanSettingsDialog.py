__author__ = 'B.Ankhbold'
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ..view.Ui_PlanSettingsDialog import *
from ..model import Constants
from ..utils.SessionHandler import SessionHandler
from ..model.SetPlanZonePlanType import *
from ..model.ClPlanZoneType import *
from ..model.SetPlanZoneRelation import *
from ..model.ClRightForm import *
from ..model.ClPlanType import *
from ..model.SetPlanZoneRightForm import *

class PlanSettingsDialog(QDialog, Ui_PlanSettingsDialog):

    def __init__(self, parent=None):

        super(PlanSettingsDialog,  self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr("Plan Admin Settings"))
        self.session = SessionHandler().session_instance()

        self.time_counter = None
        self.__setup_table_widget()
        self.__process_type_mapping(None)
        self.process_type_treewidget.itemChanged.connect(self.__itemProcessCheckChanged)
        self.process_list = []

    def __itemProcessCheckChanged(self, item, column):

        if item.checkState(column) == QtCore.Qt.Checked:
            code = item.data(0, Qt.UserRole)
            if code not in self.process_list:
                self.process_list.append(code)
                self.__settings_add_save(code)
        elif item.checkState(column) == QtCore.Qt.Unchecked:
            code = item.data(0, Qt.UserRole)
            if code in self.process_list:
                self.process_list.remove(code)
                self.__settings_remove_delete(code)

    def __setup_table_widget(self):

        self.settings_twidget.setAlternatingRowColors(True)
        self.settings_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.settings_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.settings_twidget.setSelectionMode(QTableWidget.SingleSelection)

        self.settings_twidget.setColumnWidth(0, 80)
        self.settings_twidget.setColumnWidth(1, 350)

    def __process_type_mapping(self, values):

        # plan_type = 1
        # is_default = False
        self.process_type_treewidget.clear()
        tree = self.process_type_treewidget
        parent_types = Constants.plan_process_type_parent
        for parent_type in parent_types:
            parent = QTreeWidgetItem(tree)
            parent.setText(0, str(parent_type) + ': ' + parent_types[parent_type])
            parent.setData(0, Qt.UserRole, parent_type)
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            parent_type_value = str(parent_type) + '%'


            # sub_types = self.session.query(ClPlanZone).\
            #     join(SetPlanZoneRelation, ClPlanZone.plan_zone_id == SetPlanZoneRelation.parent_plan_zone_id). \
            #     filter(ClPlanZone.code.ilike(parent_type_value)).all()
            sub_types = self.session.query(ClPlanZone). \
              filter(ClPlanZone.plan_zone_type_id == 2). \
              filter(ClPlanZone.code.ilike(parent_type_value)).all()
            for sub_type in sub_types:
                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, str(sub_type.code) + ': ' + sub_type.name)
                child.setData(0, Qt.UserRole, sub_type.plan_zone_id)
                child.setFlags(child.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

                parent_type_value = str(sub_type.code)[:3] + '%'

                child_types = self.session.query(ClPlanZone). \
                    filter(ClPlanZone.plan_zone_type_id == 3). \
                    filter(ClPlanZone.code.ilike(parent_type_value)).all()
                for child_type in child_types:
                    sub_child = QTreeWidgetItem(child)
                    sub_child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                    sub_child.setText(0, str(child_type.code) + ': ' + child_type.name)
                    sub_child.setData(0, Qt.UserRole, child_type.plan_zone_id)
                    sub_child.setFlags(sub_child.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

                    # process_types = self.session.query(ClPlanZone). \
                    #     join(SetPlanZoneRelation, ClPlanZone.plan_zone_id == SetPlanZoneRelation.child_plan_zone_id). \
                    #     filter(SetPlanZoneRelation.parent_plan_zone_id == sub_type.plan_zone_id).all()
                    parent_type_value = str(child_type.code)[:5] + '%'
                    process_types = self.session.query(ClPlanZone). \
                        filter(ClPlanZone.plan_zone_type_id == 4). \
                        filter(ClPlanZone.code.ilike(parent_type_value)).all()

                    for process_type in process_types:
                        process_child = QTreeWidgetItem(sub_child)
                        process_child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                        process_child.setText(0, str(process_type.code) + ': ' + process_type.name)
                        process_child.setData(0, Qt.UserRole, process_type.plan_zone_id)
                        process_child.setCheckState(0, Qt.Unchecked)
                        if values:
                            for value in values:
                                if value.plan_zone_id == process_type.plan_zone_id:
                                    process_child.setCheckState(0, Qt.Checked)

        self.process_type_treewidget.itemChanged.connect(self.__itemProcessCheckChanged)
        tree.show()

    @pyqtSlot(bool)
    def on_zone_type_rbutton_toggled(self, state):

        if not state:
            return

        self.settings_twidget.setRowCount(0)
        values = self.session.query(ClRightForm).all()

        for value in values:
            id = value.right_form_id
            desc = value.description
            self.__add_settings_twidget_row(id, desc)

    @pyqtSlot(bool)
    def on_plan_type_rbutton_toggled(self, state):

        if not state:
            return

        self.settings_twidget.setRowCount(0)
        values = self.session.query(ClPlanType).all()

        for value in values:
            id = value.plan_type_id
            desc = value.description
            self.__add_settings_twidget_row(id, desc)

    def __add_settings_twidget_row(self, id, desc):

        count = self.settings_twidget.rowCount()
        self.settings_twidget.insertRow(count)

        item = QTableWidgetItem(unicode(id))
        item.setCheckState(Qt.Unchecked)
        item.setData(Qt.UserRole, id)
        self.settings_twidget.setItem(count, 0, item)

        item = QTableWidgetItem(unicode(desc))
        item.setData(Qt.UserRole, id)
        self.settings_twidget.setItem(count, 1, item)

    @pyqtSlot(QTableWidgetItem)
    def on_settings_twidget_itemClicked(self, item):

        selected_row = self.settings_twidget.currentRow()
        id_item = self.settings_twidget.item(selected_row, 0)
        if id_item:
            for row in range(self.settings_twidget.rowCount()):
                item_dec = self.settings_twidget.item(row, 0)
                item_dec.setCheckState(Qt.Unchecked)
            id_item.setCheckState(Qt.Checked)
        if self.zone_type_rbutton.isChecked():
            id = self.settings_twidget.item(selected_row, 0).data(Qt.UserRole)
            values = self.session.query(ClPlanZone).\
                join(SetPlanZoneRightForm, ClPlanZone.plan_zone_id == SetPlanZoneRightForm.plan_zone_id). \
                filter(SetPlanZoneRightForm.right_form_id == id).all()

            self.__process_type_mapping(values)

    def __settings_add_save(self, plan_zone_id):

        row_count = range(self.settings_twidget.rowCount())
        if self.zone_type_rbutton.isChecked():
            for row in row_count:
                item = self.settings_twidget.item(row, 0)
                if item.checkState() == QtCore.Qt.Checked:
                    id = item.data(Qt.UserRole)

                    zone_count = self.session.query(ClPlanZone).filter(ClPlanZone.plan_zone_id == plan_zone_id).count()
                    if zone_count == 1:
                        count = self.session.query(SetPlanZoneRightForm). \
                            filter(SetPlanZoneRightForm.right_form_id == id). \
                            filter(SetPlanZoneRightForm.plan_zone_id == plan_zone_id).count()
                        if count == 0:
                            object = SetPlanZoneRightForm()
                            object.plan_zone_id = plan_zone_id
                            object.right_form_id = id

                            self.session.add(object)

        if self.plan_type_rbutton.isChecked():
            for row in row_count:
                item = self.settings_twidget.item(row, 0)
                if item.checkState() == QtCore.Qt.Checked:
                    id = item.data(Qt.UserRole)
                    zone_count = self.session.query(ClPlanZone).filter(ClPlanZone.plan_zone_id == plan_zone_id).count()
                    if zone_count == 1:
                        count = self.session.query(SetPlanZonePlanType). \
                            filter(SetPlanZonePlanType.plan_type_id == id). \
                            filter(SetPlanZonePlanType.plan_zone_id == plan_zone_id).count()
                        if count == 0:
                            object = SetPlanZonePlanType()
                            object.plan_zone_id = plan_zone_id
                            object.plan_type_id = id

                            self.session.add(object)

    def __settings_remove_delete(self, plan_zone_id):

        row_count = range(self.settings_twidget.rowCount())
        if self.zone_type_rbutton.isChecked():
            for row in row_count:
                item = self.settings_twidget.item(row, 0)
                if item.checkState() == QtCore.Qt.Checked:
                    id = item.data(Qt.UserRole)
                    count = self.session.query(SetPlanZoneRightForm). \
                        filter(SetPlanZoneRightForm.right_form_id == id). \
                        filter(SetPlanZoneRightForm.plan_zone_id == plan_zone_id).count()
                    if count == 1:
                        self.session.query(SetPlanZoneRightForm). \
                            filter(SetPlanZoneRightForm.right_form_id == id). \
                            filter(SetPlanZoneRightForm.plan_zone_id == plan_zone_id).delete()

        if self.plan_type_rbutton.isChecked():
            for row in row_count:
                item = self.settings_twidget.item(row, 0)
                if item.checkState() == QtCore.Qt.Checked:
                    id = item.data(Qt.UserRole)
                    count = self.session.query(SetPlanZonePlanType). \
                        filter(SetPlanZonePlanType.plan_type_id == id). \
                        filter(SetPlanZonePlanType.plan_zone_id == plan_zone_id).count()
                    if count == 1:
                        self.session.query(SetPlanZonePlanType). \
                            filter(SetPlanZonePlanType.plan_type_id == id). \
                            filter(SetPlanZonePlanType.plan_zone_id == plan_zone_id).delete()

    @pyqtSlot()
    def on_apply_button_clicked(self):

        self.session.commit()
        self.__start_fade_out_timer()

    def __start_fade_out_timer(self):

        # self.error_label.setVisible(False)
        self.status_label.setVisible(True)
        self.timer = QTimer()
        self.timer.timeout.connect(self.__fade_status_message)
        self.time_counter = 500
        self.timer.start(10)

    def __fade_status_message(self):

        opacity = int(self.time_counter * 0.5)
        self.status_label.setStyleSheet("QLabel {color: rgba(255,0,0," + str(opacity) + ");}")
        self.status_label.setText(self.tr('Changes applied successfully.'))
        if self.time_counter == 0:
            self.timer.stop()
        self.time_counter -= 1
