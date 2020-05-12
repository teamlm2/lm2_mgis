__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Numeric, Table
from sqlalchemy.orm import relationship, backref
from Base import *

class SetNzPastureType(Base):

    __tablename__ = 'set_nz_pasture_type'

    pasture_type = Column(Integer, ForeignKey('cl_pasture_type.code'), primary_key=True)
    pasture_type_ref = relationship("ClPastureType")

    natural_zone = Column(Integer, ForeignKey('au_natural_zone.code'), primary_key=True)
    natural_zone_ref = relationship("AuNaturalZone")

    current_value = Column(Numeric)
    percent_value = Column(Numeric)
    duration_begin = Column(Date)
    duration_end = Column(Date)
    duration_days = Column(Integer)
    sheep_unit = Column(Numeric)
