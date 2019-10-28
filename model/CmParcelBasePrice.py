
__author__ = 'B.Ankhbold'
from sqlalchemy import Column, String, Float, Date, ForeignKey, Integer, Table, DateTime, Boolean
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from ClLanduseType import *


class CmParcelBasePrice(Base):

    __tablename__ = 'cm_parcel_base_price'

    id = Column(Integer, primary_key=True)
    base_price = Column(Float)
    base_price_m2 = Column(Float)
    calculate_year = Column(Integer)
    in_active = Column(Boolean)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # foreign keys:
    parcel_id = Column(String, ForeignKey('ca_parcel_tbl.parcel_id'))
    parcel_ref = relationship("CaParcelTbl")

    #applications = relationship("CtApplication")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")