__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Boolean
from sqlalchemy.orm import relationship, backref
from SetWorkruleStatus import *

class PlProject(Base):

    __tablename__ = 'pl_project'

    project_id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)

    is_active = Column(Boolean)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)

    # foreign keys:
    plan_type_id = Column(Integer, ForeignKey('cl_plan_type.plan_type_id'))
    plan_type_ref = relationship("ClPlanType")

    workrule_status_id = Column(Integer, ForeignKey('set_workrule_status.workrule_status_id'))
    workrule_status_ref = relationship("SetWorkruleStatus")

    plan_decision_level_id = Column(Integer, ForeignKey('cl_plan_decision_level.plan_decision_level_id'))
    plan_decision_level_ref = relationship("ClPlanDecisionLevel")

    au1 = Column(String, ForeignKey('au_level1.code'))
    au1_ref = relationship("AuLevel1")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")
