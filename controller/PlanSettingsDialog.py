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
from ..model.ClRightType import *
from ..model.SetPlanZoneBaseConditionType import *
from ..model.ClBaseConditionType import *
from ..model.SetPlanZoneRigthType import *
from sqlalchemy import *

class PlanSettingsDialog(QDialog, Ui_PlanSettingsDialog):

    def __init__(self, parent=None):

        super(PlanSettingsDialog,  self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr("Plan Admin Settings"))
        self.session = SessionHandler().session_instance()

        self.time_counter = None
        self.settings_tab_widget.currentChanged.connect(self.__tab_widget_onChange)  # changed!
        self.__setup_table_widget()
        self.__process_type_mapping(None, None)

        self.process_type_treewidget.itemChanged.connect(self.__itemProcessCheckChanged)
        self.plan_zone_treewidget.itemChanged.connect(self.__itemPlanZoneCheckChanged)
        self.process_list = []
        self.zone_type_list = []
        self.zone_values = None

    def __tab_widget_onChange(self, index):

        is_change = False
        if index:
            if index == 1:
                self.__plan_zone_type_mapping(None)

    def __itemProcessCheckChanged(self, item, column):

        self.main_load_pbar.setVisible(True)
        self.main_load_pbar.setMinimum(1)
        self.main_load_pbar.setValue(0)

        if item.checkState(column) == QtCore.Qt.Checked:
            code = item.data(0, Qt.UserRole)
            if code not in self.process_list:
                self.process_list.append(code)
                if self.settings_tab_widget.currentIndex() == 0:
                    self.__settings_add_save(code)
                if self.settings_tab_widget.currentIndex() == 1:
                    self.__zone_relation_save(code)
        elif item.checkState(column) == QtCore.Qt.Unchecked:
            code = item.data(0, Qt.UserRole)
            if code in self.process_list:
                self.process_list.remove(code)
                if self.settings_tab_widget.currentIndex() == 0:
                    self.__settings_remove_delete(code)
                if self.settings_tab_widget.currentIndex() == 1:
                    self.__zone_relation_delete(code)

    def __itemPlanZoneCheckChanged(self, item, column):

        self.main_load_pbar.setVisible(True)
        self.main_load_pbar.setMinimum(1)
        self.main_load_pbar.setValue(0)

        if item.checkState(column) == QtCore.Qt.Checked:
            code = item.data(0, Qt.UserRole)
            if code not in self.zone_type_list:
                self.zone_type_list.append(code)
                # self.__plan_zone_relation(code)
        elif item.checkState(column) == QtCore.Qt.Unchecked:
            code = item.data(0, Qt.UserRole)
            if code in self.zone_type_list:
                self.zone_type_list.remove(code)

    @pyqtSlot()
    def on_plan_zone_treewidget_itemSelectionChanged(self):

        if len(self.plan_zone_treewidget.selectedItems()) > 0:
            current_item = self.plan_zone_treewidget.selectedItems()[0]

            code = current_item.data(0, Qt.UserRole)

            self.__plan_zone_relation(code)

    def __zone_relation_save(self, plan_zone_id):

        self.main_load_pbar.setMaximum(len(self.zone_type_list))
        for id in self.zone_type_list:
            zone_count = self.session.query(ClPlanZone).filter(ClPlanZone.plan_zone_id == id).count()
            if zone_count == 0:
                return

            child_count = self.session.query(ClPlanZone).filter(ClPlanZone.plan_zone_id == plan_zone_id).count()
            if child_count == 0:
                return

            count = self.session.query(SetPlanZoneRelation). \
                filter(SetPlanZoneRelation.parent_plan_zone_id == id). \
                filter(SetPlanZoneRelation.child_plan_zone_id == plan_zone_id).count()
            if count == 0:
                object = SetPlanZoneRelation()
                object.child_plan_zone_id = plan_zone_id
                object.parent_plan_zone_id = id

                self.session.add(object)

            value_p = self.main_load_pbar.value() + 1
            self.main_load_pbar.setValue(value_p)

    def __zone_relation_delete(self, plan_zone_id):

        self.main_load_pbar.setMaximum(len(self.zone_type_list))
        for id in self.zone_type_list:
            # count = self.session.query(SetPlanZoneRelation). \
            #     filter(SetPlanZoneRelation.parent_plan_zone_id == id). \
            #     filter(SetPlanZoneRelation.child_plan_zone_id == plan_zone_id).count()
            # if count == 1:
            self.session.query(SetPlanZoneRelation). \
                filter(SetPlanZoneRelation.parent_plan_zone_id == id). \
                filter(SetPlanZoneRelation.child_plan_zone_id == plan_zone_id).delete()

            self.session.query(SetPlanZoneRelation). \
                filter(SetPlanZoneRelation.child_plan_zone_id == id). \
                filter(SetPlanZoneRelation.parent_plan_zone_id == plan_zone_id).delete()

            value_p = self.main_load_pbar.value() + 1
            self.main_load_pbar.setValue(value_p)

    def __plan_zone_relation(self, plan_zone_id):

        zone_id_list = []
        values1 = self.session.query(SetPlanZoneRelation.child_plan_zone_id.label("plan_zone_id")). \
            filter(SetPlanZoneRelation.parent_plan_zone_id == plan_zone_id).\
            group_by(SetPlanZoneRelation.child_plan_zone_id).all()

        for value in values1:
            zone_id_list.append(value.plan_zone_id)

        values2 = self.session.query(SetPlanZoneRelation.parent_plan_zone_id.label("plan_zone_id")). \
            filter(SetPlanZoneRelation.child_plan_zone_id == plan_zone_id). \
            group_by(SetPlanZoneRelation.parent_plan_zone_id).all()

        for value in values2:
            zone_id_list.append(value.plan_zone_id)


        self.zone_values = zone_id_list

        self.__process_type_mapping(zone_id_list, None)
        # self.__process_type_item_change(values)

    def __process_type_item_change(self, values):

        # self.process_type_treewidget.items()
        root = self.process_type_treewidget.invisibleRootItem()
        child_count = root.childCount()
        self.main_load_pbar.setMaximum(child_count)
        for i in range(child_count):
            parent_item = root.child(i)
            parent_item.setCheckState(0, Qt.Unchecked)
            for i in range(parent_item.childCount()):
                child_item = parent_item.child(i)
                zone_code = child_item.data(0, Qt.UserRole)
                for i in range(child_item.childCount()):
                    t_item = child_item.child(i)
                    zone_code = t_item.data(0, Qt.UserRole)

                    if values:
                        for value in values:
                            if value.plan_zone_id == zone_code:
                                t_item.setCheckState(0, Qt.Checked)
            value_p = self.main_load_pbar.value() + 1
            self.main_load_pbar.setValue(value_p)


    def __setup_table_widget(self):

        self.settings_twidget.setAlternatingRowColors(True)
        self.settings_twidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.settings_twidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.settings_twidget.setSelectionMode(QTableWidget.SingleSelection)

        self.settings_twidget.setColumnWidth(0, 80)
        self.settings_twidget.setColumnWidth(1, 350)

    def __process_type_mapping(self, values, find_value):

        # plan_type = 1
        # is_default = False
        self.process_type_treewidget.clear()
        tree = self.process_type_treewidget
        parent_types = Constants.plan_process_type_parent
        for parent_type in parent_types:
            parent = QTreeWidgetItem(tree)
            parent.setText(0, str(parent_type) + ': ' + parent_types[parent_type])
            parent.setToolTip(0, str(parent_type) + ': ' + parent_types[parent_type])
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
                child.setToolTip(0, str(sub_type.code) + ': ' + sub_type.name)
                child.setData(0, Qt.UserRole, sub_type.plan_zone_id)
                child.setFlags(child.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

                parent_type_value = str(sub_type.code)[:3] + '%'

                child_types = self.session.query(ClPlanZone). \
                    filter(ClPlanZone.plan_zone_type_id == 3). \
                    filter(ClPlanZone.code.ilike(parent_type_value)).all()

                if values:
                    for plan_zone_id in values:
                        if plan_zone_id == sub_type.plan_zone_id:
                            child.setCheckState(0, Qt.Checked)

                for child_type in child_types:
                    sub_child = QTreeWidgetItem(child)
                    sub_child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                    sub_child.setText(0, str(child_type.code) + ': ' + child_type.name)
                    sub_child.setToolTip(0, str(child_type.code) + ': ' + child_type.name)
                    sub_child.setData(0, Qt.UserRole, child_type.plan_zone_id)
                    sub_child.setFlags(sub_child.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

                    # process_types = self.session.query(ClPlanZone). \
                    #     join(SetPlanZoneRelation, ClPlanZone.plan_zone_id == SetPlanZoneRelation.child_plan_zone_id). \
                    #     filter(SetPlanZoneRelation.parent_plan_zone_id == sub_type.plan_zone_id).all()
                    parent_type_value = str(child_type.code)[:5] + '%'
                    process_types = self.session.query(ClPlanZone). \
                        filter(ClPlanZone.plan_zone_type_id == 4). \
                        filter(ClPlanZone.code.ilike(parent_type_value)).all()

                    if values:
                        for plan_zone_id in values:
                            if plan_zone_id == child_type.plan_zone_id:
                                sub_child.setCheckState(0, Qt.Checked)

                    for process_type in process_types:
                        process_child = QTreeWidgetItem(sub_child)
                        process_child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                        process_child.setText(0, str(process_type.code) + ': ' + process_type.name)
                        process_child.setToolTip(0, str(process_type.code) + ': ' + process_type.name)
                        process_child.setData(0, Qt.UserRole, process_type.plan_zone_id)
                        process_child.setCheckState(0, Qt.Unchecked)
                        if values:
                            for plan_zone_id in values:
                                if plan_zone_id == process_type.plan_zone_id:
                                    process_child.setCheckState(0, Qt.Checked)

                        str_value = process_type.name
                        if find_value:
                            if str_value.find(find_value) != -1:
                                process_child.setCheckState(0, Qt.Checked)
        self.process_type_treewidget.itemChanged.connect(self.__itemProcessCheckChanged)
        tree.show()

    @pyqtSlot(bool)
    def on_zone_type_rbutton_toggled(self, state):

        self.zone_values = None
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

        self.zone_values = None
        if not state:
            return

        self.settings_twidget.setRowCount(0)
        values = self.session.query(ClPlanType).order_by(ClPlanType.code).all()

        for value in values:
            id = value.plan_type_id
            desc = value.description
            self.__add_settings_twidget_row(id, desc)

    @pyqtSlot(bool)
    def on_right_type_rbutton_toggled(self, state):

        self.zone_values = None
        if not state:
            return

        self.settings_twidget.setRowCount(0)
        values = self.session.query(ClRightType).order_by(ClRightType.code).all()

        for value in values:
            id = value.code
            desc = value.description
            self.__add_settings_twidget_row(id, desc)

    @pyqtSlot(bool)
    def on_sec_zone_rbutton_toggled(self, state):

        self.zone_values = None
        if not state:
            return

        self.settings_twidget.setRowCount(0)
        values = self.session.query(ClBaseConditionType).order_by(ClBaseConditionType.code).all()

        for value in values:
            id = value.base_condition_type_id
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

            zone_id_list = []
            for value in values:
                zone_id_list.append(value.plan_zone_id)

            self.zone_values = zone_id_list
            self.__process_type_mapping(zone_id_list, None)

        if self.plan_type_rbutton.isChecked():
            id = self.settings_twidget.item(selected_row, 0).data(Qt.UserRole)
            values = self.session.query(ClPlanZone).\
                join(SetPlanZonePlanType, ClPlanZone.plan_zone_id == SetPlanZonePlanType.plan_zone_id). \
                filter(SetPlanZonePlanType.plan_type_id == id).all()

            zone_id_list = []
            for value in values:
                zone_id_list.append(value.plan_zone_id)
            self.zone_values = zone_id_list
            self.__process_type_mapping(zone_id_list, None)

        if self.right_type_rbutton.isChecked():
            id = self.settings_twidget.item(selected_row, 0).data(Qt.UserRole)
            values = self.session.query(ClPlanZone).\
                join(SetPlanZoneRigthType, ClPlanZone.plan_zone_id == SetPlanZoneRigthType.plan_zone_id). \
                filter(SetPlanZoneRigthType.right_type_code == id).all()

            zone_id_list = []
            for value in values:
                zone_id_list.append(value.plan_zone_id)
            self.zone_values = zone_id_list
            self.__process_type_mapping(zone_id_list, None)

        if self.sec_zone_rbutton.isChecked():
            id = self.settings_twidget.item(selected_row, 0).data(Qt.UserRole)
            values = self.session.query(ClPlanZone).\
                join(SetPlanZoneBaseConditionType, ClPlanZone.plan_zone_id == SetPlanZoneBaseConditionType.plan_zone_id). \
                filter(SetPlanZoneBaseConditionType.base_condition_type_id == id).all()

            zone_id_list = []
            for value in values:
                zone_id_list.append(value.plan_zone_id)
            self.zone_values = zone_id_list
            self.__process_type_mapping(zone_id_list, None)

    def __settings_add_save(self, plan_zone_id):

        row_count = range(self.settings_twidget.rowCount())
        self.main_load_pbar.setMaximum(self.settings_twidget.rowCount())
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

                value_p = self.main_load_pbar.value() + 1
                self.main_load_pbar.setValue(value_p)

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

                value_p = self.main_load_pbar.value() + 1
                self.main_load_pbar.setValue(value_p)

        if self.right_type_rbutton.isChecked():
            for row in row_count:
                item = self.settings_twidget.item(row, 0)
                if item.checkState() == QtCore.Qt.Checked:
                    id = item.data(Qt.UserRole)
                    zone_count = self.session.query(ClPlanZone).filter(ClPlanZone.plan_zone_id == plan_zone_id).count()
                    if zone_count == 1:
                        count = self.session.query(SetPlanZoneRigthType). \
                            filter(SetPlanZoneRigthType.right_type_code == id). \
                            filter(SetPlanZoneRigthType.plan_zone_id == plan_zone_id).count()
                        if count == 0:
                            object = SetPlanZoneRigthType()
                            object.plan_zone_id = plan_zone_id
                            object.right_type_code = id

                            self.session.add(object)

                value_p = self.main_load_pbar.value() + 1
                self.main_load_pbar.setValue(value_p)

        if self.sec_zone_rbutton.isChecked():
            for row in row_count:
                item = self.settings_twidget.item(row, 0)
                if item.checkState() == QtCore.Qt.Checked:
                    id = item.data(Qt.UserRole)
                    zone_count = self.session.query(ClPlanZone).filter(ClPlanZone.plan_zone_id == plan_zone_id).count()
                    if zone_count == 1:
                        count = self.session.query(SetPlanZoneBaseConditionType). \
                            filter(SetPlanZoneBaseConditionType.base_condition_type_id == id). \
                            filter(SetPlanZoneBaseConditionType.plan_zone_id == plan_zone_id).count()
                        if count == 0:
                            object = SetPlanZoneBaseConditionType()
                            object.plan_zone_id = plan_zone_id
                            object.base_condition_type_id = id

                            self.session.add(object)

                value_p = self.main_load_pbar.value() + 1
                self.main_load_pbar.setValue(value_p)

    def __settings_remove_delete(self, plan_zone_id):

        row_count = range(self.settings_twidget.rowCount())
        self.main_load_pbar.setMaximum(self.settings_twidget.rowCount())
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

                value_p = self.main_load_pbar.value() + 1
                self.main_load_pbar.setValue(value_p)

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

                value_p = self.main_load_pbar.value() + 1
                self.main_load_pbar.setValue(value_p)

        if self.sec_zone_rbutton.isChecked():
            for row in row_count:
                item = self.settings_twidget.item(row, 0)
                if item.checkState() == QtCore.Qt.Checked:
                    id = item.data(Qt.UserRole)
                    count = self.session.query(SetPlanZoneBaseConditionType). \
                        filter(SetPlanZoneBaseConditionType.base_condition_type_id == id). \
                        filter(SetPlanZoneBaseConditionType.plan_zone_id == plan_zone_id).count()
                    if count == 1:
                        self.session.query(SetPlanZoneBaseConditionType). \
                            filter(SetPlanZoneBaseConditionType.base_condition_type_id == id). \
                            filter(SetPlanZoneBaseConditionType.plan_zone_id == plan_zone_id).delete()

                value_p = self.main_load_pbar.value() + 1
                self.main_load_pbar.setValue(value_p)

        if self.right_type_rbutton.isChecked():
            for row in row_count:
                item = self.settings_twidget.item(row, 0)
                if item.checkState() == QtCore.Qt.Checked:
                    id = item.data(Qt.UserRole)
                    count = self.session.query(SetPlanZoneRigthType). \
                        filter(SetPlanZoneRigthType.right_type_code == id). \
                        filter(SetPlanZoneRigthType.plan_zone_id == plan_zone_id).count()
                    if count == 1:
                        self.session.query(SetPlanZoneRigthType). \
                            filter(SetPlanZoneRigthType.right_type_code == id). \
                            filter(SetPlanZoneRigthType.plan_zone_id == plan_zone_id).delete()

                value_p = self.main_load_pbar.value() + 1
                self.main_load_pbar.setValue(value_p)

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

    def __plan_zone_type_mapping(self, value):

        # plan_type = 1
        # is_default = False
        self.plan_zone_treewidget.clear()
        tree = self.plan_zone_treewidget
        parent_types = Constants.plan_process_type_parent
        for parent_type in parent_types:
            parent = QTreeWidgetItem(tree)
            parent.setText(0, str(parent_type) + ': ' + parent_types[parent_type])
            parent.setToolTip(0, str(parent_type) + ': ' + parent_types[parent_type])
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
                child.setToolTip(0, str(sub_type.code) + ': ' + sub_type.name)
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
                    sub_child.setToolTip(0, str(child_type.code) + ': ' + child_type.name)
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
                        process_child.setToolTip(0, str(process_type.code) + ': ' + process_type.name)
                        process_child.setData(0, Qt.UserRole, process_type.plan_zone_id)
                        process_child.setCheckState(0, Qt.Unchecked)
                        str_value = process_type.name

                        if value:
                            if str_value.find(value) != -1:
                                process_child.setCheckState(0, Qt.Checked)

        self.plan_zone_treewidget.itemChanged.connect(self.__itemProcessCheckChanged)
        tree.show()

    @pyqtSlot()
    def on_zone_find_button_clicked(self):

        value = None
        if self.zone_find_edit.text():
            # value = '%'+self.zone_find_edit.text()+'%'
            value = self.zone_find_edit.text()
        self.__plan_zone_type_mapping(value)

    @pyqtSlot()
    def on_process_find_button_clicked(self):

        value = None
        if self.process_find_edit.text():
            # value = '%'+self.zone_find_edit.text()+'%'
            value = self.process_find_edit.text()
        self.__process_type_mapping(self.zone_values, value)

