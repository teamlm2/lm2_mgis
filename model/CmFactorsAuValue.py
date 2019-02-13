
__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, Integer, Table, Boolean, Numeric
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from ClLanduseType import *


class CmFactorsAuValue(Base):

    __tablename__ = 'cm_factors_au_value'

    id = Column(String, primary_key=True)
    is_interval = Column(Boolean)
    first_value = Column(Numeric)
    last_value = Column(Numeric)
    remarks = Column(String)

    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # foreign keys:
    factor_id = Column(Integer, ForeignKey('cm_factors.code'), primary_key=True)
    factor_ref = relationship("CmFactors")

    factor_value_id = Column(Integer, ForeignKey('cm_factors_value.code'), primary_key=True)
    factor_value_ref = relationship("CmFactorsValue")

    au2 = Column(String, ForeignKey('au_level2.code'), primary_key=True)
    au2_ref = relationship("AuLevel2")