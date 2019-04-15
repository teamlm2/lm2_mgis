__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from Base import *
from SetRole import *


class LdProjectPlanStatus(Base):

    __tablename__ = 'ld_project_plan_status'
    id = Column(Integer,  primary_key=True)
    status_date = Column(DateTime)
    description = Column(String)
    plan_draft_id = Column(Integer, ForeignKey('ld_project_plan.plan_draft_id'))

    status = Column(Integer, ForeignKey('cl_plan_status_type.code'))
    status_ref = relationship("ClPlanStatusType")

    officer_in_charge = Column(Integer, ForeignKey('sd_user.user_id'))
    officer_in_charge_ref = relationship("SdUser", foreign_keys=[officer_in_charge], cascade="save-update")

    next_officer_in_charge = Column(Integer, ForeignKey('sd_user.user_id'))
    next_officer_in_charge_ref = relationship("SdUser", foreign_keys=[next_officer_in_charge], cascade="save-update")
