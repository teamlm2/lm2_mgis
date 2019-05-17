__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClZoneActivity import *

class ClAttributeZone(Base):

    __tablename__ = 'cl_attribute_zone'

    attribute_id = Column(Integer, primary_key=True)
    attribute_name = Column(String)
    attribute_name_mn = Column(String)
    attribute_type = Column(String)
    description = Column(String)

    is_active = Column(Boolean)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)

    # foreign keys:
    attribute_group_id = Column(Integer, ForeignKey('cl_attribute_group.attribute_group_id'))
    attribute_group_ref = relationship("ClAttributeGroup")
