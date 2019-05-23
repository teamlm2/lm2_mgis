
__author__ = 'B.Ankhbold'
from sqlalchemy import Column, String, Float, Date, ForeignKey, Integer, Table, DateTime, Boolean, Numeric
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from ClLanduseType import *

class CmParcelFactorValue(Base):

    __tablename__ = 'cm_parcel_factor_value'

    id = Column(Integer, primary_key=True)
    factor_value = Column(Numeric)
    in_active = Column(Boolean)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # foreign keys:
    parcel_id = Column(String, ForeignKey('ca_parcel_tbl.parcel_id'))
    parcel_ref = relationship("CaParcelTbl")

    factor_id = Column(String, ForeignKey('cm_factor.id'))
    factor_ref = relationship("CaParcelTbl")
