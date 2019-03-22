__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClZoneActivity import *

class SetZoneSubOverlap(Base):

    __tablename__ = 'set_zone_sub_overlap'

    is_active = Column(Boolean)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)

    # foreign keys:
    zone_sub_id_src = Column(Integer, ForeignKey('cl_zone_sub.zone_sub_id'), primary_key=True)
    zone_sub_id_src_ref = relationship("ClZoneSub")

    zone_sub_id_trg = Column(Integer, ForeignKey('cl_zone_sub.zone_sub_id'), primary_key=True)
    zone_sub_id_trg_ref = relationship("ClZoneSub")

