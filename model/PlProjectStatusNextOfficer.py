__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from Base import *


class PlProjectStatusNextOfficer(Base):

    __tablename__ = 'pl_project_status_next_officer'

    comment = Column(String)

    project_id = Column(Integer, ForeignKey('pl_project.project_id'), primary_key=True)
    project_ref = relationship("PlProject")

    workrule_status_id = Column(String, ForeignKey('set_workrule_status.workrule_status_id'), primary_key=True)
    workrule_status_ref = relationship("SetWorkruleStatus")

    next_officer_id = Column(Integer, ForeignKey('sd_user.user_id'))
    next_officer_ref = relationship("SdUser", foreign_keys=[next_officer_id], cascade="save-update")

    created_at = Column(DateTime)
    created_by = Column(Integer)