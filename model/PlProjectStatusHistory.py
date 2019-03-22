__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from Base import *


class PlProjectStatusHistory(Base):

    __tablename__ = 'pl_project_status_history'

    project_id = Column(Integer, ForeignKey('pl_project.project_id'), primary_key=True)
    project_ref = relationship("PlProject")

    workrule_status_id = Column(String, ForeignKey('set_workrule_status.workrule_status_id'), primary_key=True)
    workrule_status_ref = relationship("SetWorkruleStatus")

    created_at = Column(DateTime)
    created_by = Column(Integer)