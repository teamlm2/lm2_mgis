__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from StWorkflow import *

class StWorkflowStatusLanduse(Base):

    __tablename__ = 'st_workflow_status_landuse'

    id = Column(Integer, primary_key=True)

    # foreign keys:
    workflow_id = Column(Integer, ForeignKey('st_workflow.id'))
    workflow_ref = relationship("StWorkflow")

    prev_landuse = Column(Integer, ForeignKey('cl_landuse_type.code'))
    # landuse_ref = relationship("ClLanduseType")
    next_landuse = Column(Integer, ForeignKey('cl_landuse_type.code'))


