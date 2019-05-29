__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClPlanZone import *

class SetWorkflowTransition(Base):

    __tablename__ = 'set_workflow_transition'

    transition_id = Column(Integer, primary_key=True)
    duration = Column(Integer)
    is_active = Column(Boolean)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)

    # foreign keys:
    prev_status_id = Column(Integer, ForeignKey('set_workflow_status.status_id'), primary_key=True)
    prev_status_ref = relationship("SetWorkflowStatus")

    next_status_id = Column(Integer, ForeignKey('set_workflow_status.status_id'), primary_key=True)
    next_status_ref = relationship("SetWorkflowStatus")

    workflow_id = Column(Integer, ForeignKey('set_workflow.workflow_id'), primary_key=True)
    workflow_ref = relationship("SetWorkflow")


