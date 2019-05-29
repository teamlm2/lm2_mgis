__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClPlanZone import *

class SetAttributeSubZone(Base):

    __tablename__ = 'set_attribute_sub_zone'

    is_required = Column(Boolean)
    description = Column(String)

    is_active = Column(Boolean)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)

    # foreign keys:
    zone_sub_id = Column(Integer, ForeignKey('cl_zone_sub.zone_sub_id'), primary_key=True)
    zone_sub_ref = relationship("ClZoneSub")

    attribute_id = Column(Integer, ForeignKey('cl_attribute_zone.attribute_id'), primary_key=True)
    attribute_ref = relationship("ClAttributeZone")

