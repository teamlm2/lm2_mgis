__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClPlanZone import *

class SetPlanZonePlanType(Base):

    __tablename__ = 'set_plan_zone_plan_type'

    # foreign keys:
    plan_type_id = Column(Integer, ForeignKey('cl_plan_type.plan_type_id'), primary_key=True)
    plan_type_ref = relationship("ClPlanType")

    plan_zone_id = Column(Integer, ForeignKey('cl_plan_zone.plan_zone_id'), primary_key=True)
    plan_zone_ref = relationship("ClPlanZone")

    is_default = Column(Boolean)

