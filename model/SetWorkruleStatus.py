__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClObject import *

class SetWorkruleStatus(Base):

    __tablename__ = 'set_workrule_status'

    workrule_status_id = Column(Integer, primary_key=True)
    description = Column(String)
    is_active = Column(Boolean)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)

    # foreign keys:
    object_id = Column(Integer, ForeignKey('cl_object.object_id'), primary_key=True)
    object_ref = relationship("ClObject")


