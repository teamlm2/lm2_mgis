__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from Base import *
from ClAddressSource import *
from ClStreetType import *

class StSettlementPoint(Base):

    __tablename__ = 'au_settlement_zone_point'

    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean)
    valid_from = Column(Date)
    valid_till = Column(Date)
    geometry = Column(Geometry('MULTIPOLYGON', 4326))
    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    au1 = Column(String, ForeignKey('au_level1.code'))
    au1_ref = relationship("AuLevel1")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")

    au3 = Column(String, ForeignKey('au_level3.code'))
    au3_ref = relationship("AuLevel3")