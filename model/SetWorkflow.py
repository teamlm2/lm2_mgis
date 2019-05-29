__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClPlanZone import *

class SetWorkflow(Base):

    __tablename__ = 'set_workflow'

    workflow_id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)
    description = Column(String)
    is_active = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # foreign keys:
    object_id = Column(Integer, ForeignKey('cl_object.object_id'), primary_key=True)
    object_ref = relationship("ClObject")


