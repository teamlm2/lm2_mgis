__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from StWorkflow import *

class StWorkflowStatus(Base):

    __tablename__ = 'st_workflow_status'

    id = Column(Integer, primary_key=True)
    is_first = Column(Boolean)

    # foreign keys:
    workflow_id = Column(Integer, ForeignKey('st_workflow.id'))
    workflow_ref = relationship("StWorkflow")

    prev_status_id = Column(Integer, ForeignKey('cl_landuse_movement_status.id'))
    # landuse_ref = relationship("ClLanduseType")
    next_status_id = Column(Integer, ForeignKey('cl_landuse_movement_status.id'))


