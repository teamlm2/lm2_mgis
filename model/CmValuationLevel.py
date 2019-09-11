__author__ = 'B.Ankhbold'

from sqlalchemy import String,Date, Integer, Column, Numeric, ForeignKey, Boolean
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from ClZoneType import *
from SetBaseFee import *

class CmValuationLevel(Base):

    __tablename__ = 'cm_valuation_level'

    id = Column(Integer, primary_key=True)
    level_no = Column(Integer)
    area_m2 = Column(Numeric)
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326))
    valid_from = Column(Date)
    valid_till = Column(Date)
    name = Column(String)
    location = Column(String)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    in_active = Column(Boolean)

    base_price = Column(String)

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")

    status =  Column(Integer, ForeignKey('cm_valuation_level_status.code'))
    status_ref = relationship("CmValuationLevelStatus")
