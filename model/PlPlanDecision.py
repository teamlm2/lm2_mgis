__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Boolean
from sqlalchemy.orm import relationship, backref
from Base import *

class PlPlanDecision(Base):

    __tablename__ = 'pl_plan_decision'

    plan_decision_id = Column(Integer, primary_key=True)
    decision_no  = Column(String)
    decision_date = Column(Date)
    description = Column(String)
    created_by = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)
    plan_decision_draft_status_id = Column(Integer)

    # foreign keys:
    project_id = Column(Integer, ForeignKey('pl_project.project_id'))
    project_ref = relationship("PlProject")

    plan_decision_level_id = Column(Integer, ForeignKey('cl_plan_decision_level.plan_decision_level_id'))
    plan_decision_level_ref = relationship("ClPlanDecisionLevel")

