__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClPlanZone import *

class SetPlanZoneAttribute(Base):

    __tablename__ = 'set_plan_zone_attribute'

    is_required = Column(Boolean)

    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)

    # foreign keys:
    plan_zone_id = Column(Integer, ForeignKey('cl_plan_zone.plan_zone_id'), primary_key=True)
    plan_zone_ref = relationship("ClPlanZone")

    attribute_id = Column(Integer, ForeignKey('cl_attribute_zone.attribute_id'), primary_key=True)
    attribute_ref = relationship("ClAttributeZone")

    plan_type_id = Column(Integer, ForeignKey('cl_plan_type.plan_type_id'), primary_key=True)
    plan_type_ref = relationship("ClPlanType")

