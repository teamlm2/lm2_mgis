__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClZoneActivity import *

class SetZoneSubActivity(Base):

    __tablename__ = 'set_zone_sub_activity'

    is_active = Column(Boolean)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)

    # foreign keys:
    zone_sub_id = Column(Integer, ForeignKey('cl_zone_sub.zone_sub_id'), primary_key=True)
    zone_sub_ref = relationship("ClZoneSub")

    zone_activity_id = Column(Integer, ForeignKey('cl_zone_activity.zone_activity_id'), primary_key=True)
    zone_activity_ref = relationship("ClZoneActivity")

