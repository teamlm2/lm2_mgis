__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClZoneActivity import *

class SetZoneMainOverlap(Base):

    __tablename__ = 'set_zone_main_overlap'

    is_active = Column(Boolean)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)

    # foreign keys:
    zone_main_id_src = Column(Integer, ForeignKey('cl_zone_main.zone_main_id'), primary_key=True)
    zone_main_id_src_ref = relationship("ClZoneMain")

    zone_main_id_trg = Column(Integer, ForeignKey('cl_zone_main.zone_main_id'), primary_key=True)
    zone_main_id_trg_ref = relationship("ClZoneMain")

