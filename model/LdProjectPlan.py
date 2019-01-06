__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship, backref
from CtApp1Ext import *

class LdProjectPlan(Base):

    __tablename__ = 'ld_project_plan'
    plan_draft_id = Column(Integer, primary_key=True)
    plan_draft_no = Column(String)
    begin_date = Column(Date)
    end_date = Column(Date)
    remarks = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    created_by = Column(Integer)
    updated_by = Column(Integer)

    # foreign keys:
    plan_type = Column(Integer, ForeignKey('cl_plan_type.code'))
    plan_type_ref = relationship("ClPlanType")

    last_status_type = Column(Integer, ForeignKey('cl_plan_status_type.code'))
    last_status_type_ref = relationship("ClPlanStatusType")

    plan_decision_level = Column(Integer, ForeignKey('cl_plan_decision_level.code'))
    plan_decision_level_ref = relationship("ClPlanDecisionLevel")

    au1 = Column(String, ForeignKey('au_level1.code'))
    au1_ref = relationship("AuLevel1")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")

    # maintenance_case = Column(Integer, ForeignKey('ca_maintenance_case.id'))
    #maintenance_case_ref = relationship("CaMaintenanceCase")

    # statuses = relationship("CtApplicationStatus", backref="application_ref",
    #                         lazy='dynamic', cascade="all, delete-orphan")