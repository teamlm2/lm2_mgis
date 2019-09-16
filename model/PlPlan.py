__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Boolean
from sqlalchemy.orm import relationship, backref
from Base import *

class PlPlan(Base):

    __tablename__ = 'pl_plan'

    plan_id = Column(Integer, primary_key=True)
    approved_date = Column(Date)
    is_active = Column(Boolean)
    created_by = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)

    # foreign keys:
    project_id = Column(Integer, ForeignKey('pl_project.project_id'))
    project_ref = relationship("PlProject")

    plan_decision_id = Column(Integer, ForeignKey('pl_plan_decision.plan_decision_id'))
    plan_decision_ref = relationship("PlPlanDecision")

