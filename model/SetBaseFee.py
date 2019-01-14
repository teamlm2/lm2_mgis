__author__ = 'Anna'

from sqlalchemy import Column, Numeric, Integer, Sequence, ForeignKey, String, Float, Boolean, Date, DateTime
from Base import *
from sqlalchemy.orm import relationship


class SetBaseFee(Base):

    __tablename__ = 'set_base_fee'

    id = Column(Integer, Sequence('set_base_fee_id_seq'), primary_key=True)
    base_fee_per_m2 = Column(Integer)
    subsidized_area = Column(Integer)
    subsidized_fee_rate = Column(Numeric)
    confidence_percent = Column(Float)
    in_active = Column(Boolean)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    # foreign keys:
    landuse = Column(Integer, ForeignKey('cl_landuse_type.code'))
    landuse_ref = relationship("ClLanduseType")

    fee_zone = Column(String, ForeignKey('set_fee_zone.zone_id'))
    fee_zone_ref = relationship("SetFeeZone")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")
