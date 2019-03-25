__author__ = 'B.Ankhbold'

from sqlalchemy import String,Date, Integer, Column, Numeric, ForeignKey, DateTime, Boolean
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from ClZoneType import *
from SetBaseFee import *

class PaValuationLevel(Base):

    __tablename__ = 'pa_valuation_level'

    id = Column(Integer, primary_key=True)
    level_no = Column(Integer)
    area_m2 = Column(Numeric)
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326))
    valid_from = Column(Date)
    valid_till = Column(Date)
    level_type = Column(Integer)

    au1 = Column(String, ForeignKey('au_level1.code'))
    au1_ref = relationship("AuLevel1")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")

    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    location = Column(String)
    name = Column(String)

    in_active = Column(Boolean)
