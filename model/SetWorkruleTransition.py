__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClPlanZone import *

class SetWorkruleTransition(Base):

    __tablename__ = 'set_workrule_transition'

    workrule_transition_id = Column(Integer, primary_key=True)
    duration = Column(Integer)
    is_active = Column(Boolean)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)

    # foreign keys:
    prev_workrule_status_id = Column(Integer, ForeignKey('set_workrule_status.workrule_status_id'), primary_key=True)
    prev_workrule_status_ref = relationship("SetWorkruleStatus")

    next_workrule_status_id = Column(Integer, ForeignKey('set_workrule_status.workrule_status_id'), primary_key=True)
    next_workrule_status_ref = relationship("SetWorkruleStatus")

    workflow_id = Column(Integer, ForeignKey('set_workrule.workrule_id'), primary_key=True)
    workflow_ref = relationship("SetWorkflow")


