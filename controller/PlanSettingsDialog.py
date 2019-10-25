__author__ = 'B.Ankhbold'
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ..view.Ui_PlanSettingsDialog import *
from ..model import Constants
from ..utils.SessionHandler import SessionHandler
from ..model.SetPlanZonePlanType import *

class PlanSettingsDialog(QDialog, Ui_PlanSettingsDialog):

    def __init__(self, parent=None):

        super(PlanSettingsDialog,  self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr("Plan Admin Settings"))
        self.session = SessionHandler().session_instance()
        self.__process_type_mapping(1, False)

    def __process_type_mapping(self, plan_type, is_default):

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
            if plan_type != -1:
                if is_default:
                    sub_types = self.session.query(SetPlanZonePlanType).\
                        join(ClPlanZone, ClPlanZone.plan_zone_id == SetPlanZonePlanType.plan_zone_id). \
                        filter(SetPlanZonePlanType.plan_type_id == plan_type). \
                        filter(SetPlanZonePlanType.is_default == is_default). \
                        filter(ClPlanZone.code.ilike(parent_type_value))
                else:
                    sub_types = self.session.query(SetPlanZonePlanType). \
                        join(ClPlanZone, ClPlanZone.plan_zone_id == SetPlanZonePlanType.plan_zone_id). \
                        filter(SetPlanZonePlanType.plan_type_id == plan_type). \
                        filter(ClPlanZone.code.ilike(parent_type_value))
            else:
                sub_types = self.session.query(SetPlanZonePlanType). \
                    join(ClPlanZone, ClPlanZone.plan_zone_id == SetPlanZonePlanType.plan_zone_id). \
                    filter(ClPlanZone.code.ilike(parent_type_value))

            for value in sub_types.distinct(SetPlanZonePlanType.plan_zone_id).all():
                sub_type = value.plan_zone_ref
                # if sub_type.code[:1] == parent_type:
                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, str(sub_type.code) + ': ' + sub_type.name)
                child.setData(0, Qt.UserRole, sub_type.code)
                child.setToolTip(0, str(sub_type.code) + ': ' + sub_type.name)
                child.setFlags(child.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                if value.is_default == True:
                    child.setCheckState(0, Qt.Checked)
                else:
                    child.setCheckState(0, Qt.Unchecked)

        tree.show()