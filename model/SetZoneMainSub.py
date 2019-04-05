__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClZoneActivity import *

class SetZoneMainSub(Base):

    __tablename__ = 'set_zone_main_sub'

    is_active = Column(Boolean)
    created_at = Column(DateTime)
    created_by = Column(Integer)

    # foreign keys:
    zone_sub_id = Column(Integer, ForeignKey('cl_zone_sub.zone_sub_id'), primary_key=True)
    zone_sub_ref = relationship("ClZoneSub")

    plan_zone_id = Column(Integer, ForeignKey('cl_plan_zone.plan_zone_id'), primary_key=True)
    zone_main_ref = relationship("ClPlanZone")

