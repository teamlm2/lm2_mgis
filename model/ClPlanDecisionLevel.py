__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Boolean, DateTime
from Base import *


class ClPlanDecisionLevel(Base):

    __tablename__ = 'cl_plan_decision_level'

    plan_decision_level_id = Column(Integer, primary_key=True)
    code = Column(String)
    description = Column(String)

    is_active = Column(Boolean)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)
