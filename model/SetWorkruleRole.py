__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClPlanZone import *

class SetWorkruleStatus(Base):

    __tablename__ = 'set_workrule_status'

    role_id = Column(Integer, primary_key=True)
    is_active = Column(Boolean)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)

    # foreign keys:
    transition_id = Column(Integer, ForeignKey('set_workrule_transition.workrule_transition_id'), primary_key=True)
    transition_ref = relationship("SetWorkflowTransition")


