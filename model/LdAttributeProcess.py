__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from LdProcessPlan import *

class ClAttributeZoneProcess(Base):

    __tablename__ = 'ld_attribute_process'

    id = Column(Integer, primary_key=True)
    is_required = Column(Boolean)
    description = Column(String)

    # foreign keys:
    process_id = Column(Integer, ForeignKey('ld_process_plan.code'))
    process_ref = relationship("LdProcessPlan")

    attribute_id = Column(Integer, ForeignKey('ld_attribute.id'))
    attribute_ref = relationship("ClAttributeZone")

