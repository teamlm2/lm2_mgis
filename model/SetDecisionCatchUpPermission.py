__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Base import *

class SetDecisionCatchUpPermission(Base):

    __tablename__ = 'set_decision_catch_up_permission'

    position_id = Column(String, ForeignKey('hr_position.position_id'), primary_key=True)
    position_ref = relationship("SdPosition")

    department_id = Column(Integer, ForeignKey('hr_department.department_id'), primary_key=True)
    department_ref = relationship("SdDepartment")